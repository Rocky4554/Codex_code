# Plan: Split Codex backend onto Render, keep code execution on EC2

## Context

Today the entire Codex stack runs on a single EC2 box (`3.109.238.141`, ap-south-1 Mumbai, **911 MB RAM**). The Spring Boot backend (`codex-app`) mounts `/var/run/docker.sock` and creates ephemeral containers per submission from the optimized executor images (`codex-cpp`, `codex-java`, `codex-python`, `codex-javascript`). This worked, but we keep hitting walls:

- **RAM is exhausted**: 786 MB used at idle on a 911 MB box. The C++ executor build OOM-killed the instance and required AWS-console reboot. Every code run competes with the JVM for memory.
- **Manual ops**: deploys mean SSH → `docker compose pull` → restart. No HTTPS at the app layer (we worked around mixed-content via a Vercel proxy). No preview environments. No autoscaling.
- **No horizontal scaling**: backend and executor are bolted together — can't add a second backend instance without doubling the Docker daemon, and can't grow execution capacity without dragging the JVM along.

The fix is to move the backend to **Render** (managed PaaS — auto HTTPS, git-push deploys, scalable) and keep Docker + the executor images on EC2 behind a small **Executor Agent service** that the Render backend calls over HTTPS. The agent reuses the existing `DockerExecutor.java` verbatim, so we are not rewriting our hardened execution code — we're just relocating the orchestration boundary.

The intended outcome:
- Backend on Render: auto-deploy from git, HTTPS by default, easy to scale to N instances
- EC2: dedicated to running user code; no JVM competing for RAM
- Same observable behavior for the user; no data migration (Postgres + Redis are already cloud-managed)
- Incremental, zero-downtime cutover

---

## Architecture: before → after

**Before** (everything on one EC2):
```
[Vercel Frontend] → [/api/proxy on Vercel] → [Spring Boot on EC2] → [Docker socket on same EC2]
                                                       ↓
                                            [Neon Postgres] [Upstash Redis]
```

**After** (split):
```
[Vercel Frontend] → [Spring Boot on Render] ──HTTPS──→ [Executor Agent on EC2] → [Docker socket on EC2]
                            ↓                                      ↓
                  [Neon Postgres] [Upstash Redis]            [codex-* images]
```

The Vercel `/api/proxy` route stays — it still solves mixed-content for any HTTP fallbacks and lets the frontend hit `/api/proxy/*` regardless of where the backend lives. We just point it at Render's HTTPS URL instead of EC2's IP.

---

## Why an Executor Agent (and not "expose Docker daemon over TCP")

A typical submission triggers ~10 Docker API calls (create, start, exec compile, exec test1..N, remove, log fetches). Singapore-Mumbai RTT is ~60 ms.

| Approach | Network latency / submission | Source-code transfer | Security |
|---|---|---|---|
| Expose `dockerd` over TCP+TLS | ~10 × 60 ms = **600+ ms** | Bind mount breaks (host paths don't exist on Render); needs `docker cp` rewrite | Cert leak = root on EC2 |
| **Executor Agent (HTTPS)** | **1 × 120 ms** total | Source code embedded in JSON request body | Narrow API surface, bearer token + SG IP allowlist |

The bind-mount problem is the killer for the TCP approach: `DockerExecutor.prepareTempDirectory()` writes source code to the host FS and then bind-mounts it as `/workspace`. If Spring Boot runs on Render, "host" is Render's container — not EC2 — so the mount fails. Fixing that means writing into the container after creation via `docker cp`, at which point we've half-built an agent in the wrong place. The agent approach reuses `DockerExecutor.java` unchanged.

---

## Implementation phases

### Phase 0 — Stabilize EC2 (do this first, takes 5 min)

Adds permanent swap so the upcoming agent + ongoing builds don't OOM the box again:

```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Optional (recommended) in parallel: upgrade EC2 to **t3.small (2 GB RAM)** via AWS Console → Instance type. ~$15/month. Eliminates the constant memory pressure for both the agent and the executor containers.

### Phase 1 — Build the Executor Agent module (no behavior change)

Add a new Maven module `executor-agent` to `Codex_backend/`. It is a minimal Spring Boot app that:
- Reuses `DockerExecutor.java` and `DockerConfig.java` **verbatim** (move them or share via a common module)
- Reuses the existing language enum / command logic
- Exposes one HTTPS endpoint: `POST /v1/execute`
- Authenticates incoming requests with a bearer token from env var `EXECUTOR_AGENT_TOKEN`

**API contract:**

```
POST /v1/execute
Authorization: Bearer <EXECUTOR_AGENT_TOKEN>
Content-Type: application/json

Request:
{
  "submissionId": "uuid",
  "language": "C++" | "Java" | "Python" | "JavaScript",
  "dockerImage": "codex-cpp:latest",
  "compileCommand": "g++ -std=c++11 -o solution solution.cpp" | null,
  "executeCommand": "./solution",
  "fileExtension": ".cpp",
  "sourceCode": "<UTF-8, max 256 KB>",
  "compileTimeoutMs": 10000,
  "runTimeoutMs": 5000,
  "memoryLimitMb": 256,
  "testCases": [
    { "id": "tc1", "stdin": "...", "expectedStdout": "...", "comparison": "EXACT" }
  ]
}

Response 200:
{
  "submissionId": "uuid",
  "status": "ACCEPTED" | "WRONG_ANSWER" | "COMPILATION_ERROR" | "RUNTIME_ERROR" | "TIME_LIMIT_EXCEEDED" | "MEMORY_LIMIT_EXCEEDED",
  "compileOutput": "...",
  "compileTimeMs": 412,
  "totalExecTimeMs": 230,
  "results": [
    {
      "testCaseId": "tc1",
      "status": "PASSED" | "FAILED" | "TIME_LIMIT_EXCEEDED" | "RUNTIME_ERROR",
      "stdout": "...",
      "stderr": "...",
      "execTimeMs": 87,
      "memoryKb": 12480,
      "exitCode": 0
    }
  ]
}
```

Supporting endpoints:
- `GET /v1/healthz` → liveness, Docker daemon ping, free disk in `/tmp/codex`
- `GET /v1/version` → agent build version, executor image digests

**Idempotency**: in-memory `Map<submissionId, ExecuteResponse>` with 5 min TTL. Re-POSTing the same `submissionId` returns the cached result instead of re-running. Cheap insurance against Render-side retries.

**Concurrency**: `Semaphore` in the controller, `EXECUTOR_AGENT_MAX_CONCURRENT=1` env var (raise to 2-3 after EC2 upgrade). Keeps the 911 MB box from melting if Render fires several submissions at once.

**Disk hygiene**: `@Scheduled` task that nukes `/tmp/codex/exec-*` directories older than 1 hour as a backstop in case `cleanup()` is interrupted.

**Critical files (new):**
- `executor-agent/pom.xml` — minimal Spring Boot Web + docker-java
- `executor-agent/src/main/java/com/codex/agent/AgentApplication.java`
- `executor-agent/src/main/java/com/codex/agent/controller/ExecuteController.java`
- `executor-agent/src/main/java/com/codex/agent/dto/ExecuteRequest.java`
- `executor-agent/src/main/java/com/codex/agent/dto/ExecuteResponse.java`
- `executor-agent/src/main/java/com/codex/agent/security/BearerTokenFilter.java`
- `executor-agent/src/main/java/com/codex/agent/scheduled/TempDirJanitor.java`
- `executor-agent/Dockerfile` — same multi-stage pattern as the main backend
- `executor-agent/src/main/resources/application.yml`

**Critical files (reused unchanged via shared module or copy):**
- `Codex_backend/src/main/java/com/codex/platform/execution/service/DockerExecutor.java`
- `Codex_backend/src/main/java/com/codex/platform/config/DockerConfig.java`
- Language entity / enum

### Phase 2 — Add `ExecutorAgentClient` to backend, behind a feature flag

Add a new HTTP client in the existing backend that talks to the agent. **Default `execution.mode=local` so behavior is unchanged when deployed.**

**Critical files (new):**
- `Codex_backend/src/main/java/com/codex/platform/execution/client/ExecutorAgentClient.java` — Spring `RestClient` wrapper:
  - Base URL from `executor.agent.base-url`
  - Bearer token from `executor.agent.token`
  - Connect timeout 5s, read timeout 90s
  - Retry once on connection failure / 502 / 503
  - Resilience4j circuit breaker so a dead EC2 doesn't queue-bomb Render
- `Codex_backend/src/main/java/com/codex/platform/execution/client/dto/*` — request/response DTOs mirroring the agent's API

**Critical files (modified):**
- `Codex_backend/src/main/java/com/codex/platform/execution/service/ExecutionService.java` — branch on `execution.mode`:
  - `local` → existing path: `dockerExecutor.prepareTempDirectory()` → compile → run loop → cleanup (unchanged)
  - `remote` → build `ExecuteRequest` from submission + test cases, call `executorAgentClient.execute()`, map response to existing `Submission` / `SubmissionResult` entities, persist via existing repositories
- `Codex_backend/src/main/resources/application.properties` — add:
  ```
  execution.mode=${EXECUTION_MODE:local}
  executor.agent.base-url=${EXECUTOR_AGENT_BASE_URL:}
  executor.agent.token=${EXECUTOR_AGENT_TOKEN:}
  executor.agent.timeout-ms=${EXECUTOR_AGENT_TIMEOUT_MS:90000}
  ```
- `Codex_backend/pom.xml` — add Resilience4j Spring Boot Starter

**What stays unchanged (this is most of the codebase):**
- `SubmissionService.java`, `SubmissionController.java`, `SseService.java`
- All entities, repositories, DTOs
- Redis queue (`SubmissionWorker`, `QueueService`)
- Authentication, rate limiting, the new `GET /api/submissions?problemId=` endpoint
- Frontend — zero changes

### Phase 3 — Deploy the agent on EC2 alongside the existing backend

Ship the agent to EC2 using the existing `docker-compose.prod.yml` pattern:

```yaml
# Add to ~/Codex_code/docker-compose.prod.yml
  codex-executor-agent:
    image: ghcr.io/rocky4554/codex_executor_agent:latest
    container_name: codex-executor-agent
    restart: always
    ports:
      - "127.0.0.1:8081:8081"        # bind to localhost only for now
    environment:
      EXECUTOR_AGENT_TOKEN: ${EXECUTOR_AGENT_TOKEN}
      EXECUTOR_AGENT_MAX_CONCURRENT: 1
      EXECUTION_DOCKER_HOST: unix:///var/run/docker.sock
      EXECUTION_TEMP_DIR: /tmp/codex/submissions
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp/codex:/tmp/codex
```

Generate a strong token, store in `.env.production` on EC2.

**Smoke test from EC2 itself**:
```bash
curl -X POST http://127.0.0.1:8081/v1/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @sample-cpp-request.json
```
Validate one submission per language (cpp / java / python / javascript). Verify status, output, and that `/tmp/codex/exec-*` is cleaned up.

### Phase 4 — Expose the agent over HTTPS to the public internet

Put **Caddy** (auto Let's Encrypt) in front of the agent on EC2. Subdomain `executor.<your-domain>` pointing at the EC2 elastic IP.

```Caddyfile
executor.yourdomain.com {
    reverse_proxy 127.0.0.1:8081
}
```

**Lock the EC2 security group** so port 443 only accepts traffic from Render's static egress IPs (Render publishes these per region — Singapore is closest to Mumbai). The bearer token is a backup, **not the primary defense**.

Test from outside: `curl -H "Authorization: Bearer $TOKEN" https://executor.yourdomain.com/v1/healthz`.

### Phase 5 — Validate the wire format end-to-end on EC2

Set `EXECUTION_MODE=remote` and `EXECUTOR_AGENT_BASE_URL=https://executor.yourdomain.com` on the **existing EC2 backend** (not Render yet). Now the same JVM is going through the public network path to its own agent on the same box. This validates serialization, auth, error handling, and the circuit breaker without changing where the JVM runs.

Run all four languages, plus deliberate failure cases: compilation error, TLE, MLE, runtime error. Watch logs on both sides.

### Phase 6 — Stand up backend on Render

Create a Render Web Service:
- Connect to your GitHub repo, root directory `Codex_backend/`
- Use the existing `Dockerfile` (multi-stage; produces the same fat JAR)
- Region: **Singapore** (closest to EC2 Mumbai, ~50-80 ms RTT)
- Plan: Starter ($7/mo, always-on) — Free tier sleeps after inactivity which breaks the queue worker
- Environment variables — copy the `prod` set from EC2's `.env.production`, then add:
  ```
  SPRING_PROFILES_ACTIVE=prod
  EXECUTION_MODE=remote
  EXECUTOR_AGENT_BASE_URL=https://executor.yourdomain.com
  EXECUTOR_AGENT_TOKEN=<same-token-as-EC2-agent>
  APP_CORS_ALLOWED_ORIGINS=https://codex-front-beryl.vercel.app
  ```
  **Drop** all `EXECUTION_DOCKER_*` and `EXECUTION_TEMP_DIR` vars — they no longer apply.
- Health check path: `/actuator/health`

The Render service connects to the same Neon Postgres and Upstash Redis as the EC2 backend. Both backends running simultaneously is **safe** because:
- Submissions are de-queued atomically by Redisson (only one worker grabs each)
- The agent is idempotent on `submissionId`
- DB writes use the same schema

Run a few test submissions through the Render URL. Verify they execute on EC2 and results land in the DB.

### Phase 7 — Cutover

1. Update Vercel proxy `BACKEND_URL` env var from `http://3.109.238.141:8080/api` to `https://<render-app>.onrender.com/api`
2. Redeploy frontend (Vercel auto-redeploys on env var change)
3. Watch logs on both EC2 backend and Render backend for ~24 hours
4. Once stable, **stop the EC2 `codex-app` container** (keep `codex-executor-agent` running): `docker compose stop codex-app`
5. EC2 now hosts only the agent + Docker daemon + executor images. RAM pressure relieved.

If anything goes wrong, the cutover is reversible: flip the Vercel env var back, restart `codex-app` on EC2. Both backends share the same DB so no data loss.

### Phase 8 — Cleanup

- Delete `codex-app` container and image from EC2 once Render has been stable for a week
- Document the new architecture in `Codex_backend/dev_docs/problems.md`
- Optionally: rotate the `EXECUTOR_AGENT_TOKEN` and any other secrets that were ever pasted in chat

---

## Concerns to flag

- **Latency budget**: ~120 ms added per submission (1 RTT Singapore-Mumbai). Acceptable for a coding judge where compile+run is 500 ms – 5 s. HTTP/2 keepalive avoids repeated TLS handshakes.
- **In-memory rate limiter**: if you scale Render to >1 instance, the per-user submission limit desyncs. Move to Redisson `RRateLimiter` (you already have Redis). Worth doing during Phase 2.
- **SSE emitter map**: same issue — `SseService` holds emitters in JVM memory. With 1 Render instance it's fine. With autoscaling, fan out status updates via Redis pub/sub. Flag, don't fix in v1.
- **EC2 single point of failure**: Render backend is now strictly dependent on one EC2 box. Add a Render-side health check that surfaces "executor unavailable" cleanly instead of hanging requests.
- **Security**: the agent runs arbitrary user code. If breached, attacker owns EC2. Defense in order of importance: (1) SG locked to Render egress IPs, (2) bearer token, (3) Caddy TLS, (4) agent process runs as a non-root user in the `docker` group. **Do not skip the SG restriction.**
- **Worker pool**: the existing `EXECUTION_WORKER_COUNT=1` worker thread on Render is now blocked on a network call instead of a local Docker call — semantically the same, but the **agent** is now the real bottleneck, not Render. Tune `EXECUTOR_AGENT_MAX_CONCURRENT` to match.

---

## Verification

After Phase 7 cutover, test end-to-end:

1. **Health checks**:
   - `curl https://<render-app>.onrender.com/actuator/health` → `UP`
   - `curl -H "Authorization: Bearer $TOKEN" https://executor.yourdomain.com/v1/healthz` → `UP`

2. **Auth flow**:
   - Login at frontend, verify httpOnly cookie set, verify `/problems` page loads, verify Render logs show successful auth

3. **Submission for each language** (C++, Java, Python, JavaScript):
   - Submit a known-good solution → expect `ACCEPTED`
   - Submit a wrong solution → expect `WRONG_ANSWER`
   - Submit code with infinite loop → expect `TIME_LIMIT_EXCEEDED`
   - Submit code that doesn't compile → expect `COMPILATION_ERROR`
   - Verify SSE status updates appear in real time on frontend
   - Verify Submissions tab on the problem page shows the new entries

4. **Cross-machine flow validation**:
   - Tail Render logs and EC2 agent logs simultaneously during a submission
   - Confirm: Render receives submission → enqueues → worker dequeues → POSTs to agent → agent creates container → returns response → Render persists result → SSE event sent

5. **Failure modes**:
   - Stop the agent on EC2 → submit code → expect Render to surface "executor unavailable" cleanly (not a 30s hang)
   - Restart agent → submit again → expect success
   - Send the same `submissionId` twice → expect cached result, not re-execution

6. **Memory observation**:
   - On EC2, `free -h` should show much lower JVM memory usage (no `codex-app` JVM, only the much smaller agent)
   - During a C++ submission, check that the executor container has headroom

7. **Load smoke test**:
   - Fire 5 submissions in 30 seconds via the frontend
   - Confirm Redis queue drains, all 5 complete, no OOMs, no orphaned `/tmp/codex/exec-*` directories on EC2

---

## Rough effort estimate

| Phase | Effort |
|---|---|
| Phase 0 — Stabilize EC2 (swap + optional upgrade) | 30 min |
| Phase 1 — Build Executor Agent module | 4–6 hours |
| Phase 2 — `ExecutorAgentClient` + flag in backend | 2–3 hours |
| Phase 3 — Ship agent on EC2, smoke test | 1 hour |
| Phase 4 — Caddy + DNS + SG lock | 1 hour |
| Phase 5 — Wire-format validation on EC2 | 30 min |
| Phase 6 — Render deployment | 1 hour |
| Phase 7 — Cutover + watch | 1 hour active + 24 hr observation |
| Phase 8 — Cleanup + docs | 30 min |

**Total: ~1.5–2 days of focused work**, with the cutover itself being a 5-minute Vercel env var change.
