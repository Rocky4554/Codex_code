# API Management & Problems Faced

This document tracks API endpoints and solutions to various problems encountered during development, deployment, and monitoring.

## 1. Problem and Language APIs

### Problem Endpoints

- `GET /api/problems` - list problems (public)
- `GET /api/problems/{id}` - get problem by id (public)
- `POST /api/problems` - create problem (auth required)
- `PUT /api/problems/{id}` - update problem (auth required)
- `DELETE /api/problems/{id}` - delete problem (auth required)

#### Problem Request Body

```json
{
  "title": "Two Sum",
  "description": "Given an array of integers nums and an integer target...",
  "difficulty": "EASY",
  "timeLimitMs": 5000,
  "memoryLimitMb": 256
}
```

### Language Endpoints

- `GET /api/languages` - list languages (public)
- `POST /api/languages` - create language (auth required)
- `PUT /api/languages/{id}` - update language (auth required)
- `DELETE /api/languages/{id}` - delete language (auth required)

#### Language Request Body

```json
{
  "name": "Python",
  "version": "3.11",
  "dockerImage": "codex-python:latest",
  "fileExtension": ".py",
  "compileCommand": "",
  "executeCommand": "python solution.py"
}
```

### Optimized Executor Docker Images

All execution containers use custom pre-optimized images instead of stock images. See `docker/executors/` for Dockerfiles.

| Language | Custom Image | Base Image | Optimization |
|----------|---|---|---|
| C++ | `codex-cpp:latest` | `gcc:latest` | Precompiled `bits/stdc++.h` header (60s → ~2s compile) |
| Java | `codex-java:latest` | `eclipse-temurin:17-jdk` | CDS archive for fast JVM startup (3s → ~0.5s) |
| Python | `codex-python:latest` | `python:3.11-slim` | Pre-compiled `.pyc` bytecode for stdlib |
| JavaScript | `codex-javascript:latest` | `node:20-slim` | V8 built-in module cache warmup |

Build all images on EC2:
```bash
cd docker/executors
chmod +x build-all.sh
./build-all.sh
```

### Execution Container Lifecycle (Ephemeral)

Every submission gets a **fresh, ephemeral container** spawned from one of the custom images above. Containers are short-lived — created for a single submission, then destroyed.

**Flow:**
```
Submission arrives
      ↓
[1] Create NEW container from codex-<lang>:latest
      ↓
[2] Compile source code once (inside container)
      ↓
[3] Run N test cases via `docker exec` (same container, NOT a new one per test case)
      ↓
[4] cleanup() in DockerExecutor:
      • docker rm --force <containerId>   ← container destroyed
      • rm -rf /tmp/codex/submissions/<id> ← temp files deleted
```

**Container properties:**

| Property | Value |
|---|---|
| Lifespan | One submission only |
| Per test case | Same container — all tests run via `docker exec` |
| Auto-remove | `withAutoRemove(false)` — removed manually in `cleanup()` via `.withForce(true)` |
| Filesystem | Read-only root + `/workspace` mounted from host |
| Temp dir | Deleted from host after container removal |
| Network | `none` (fully isolated, no network access) |
| Memory limit | Per-problem (default 256MB) |
| CPU quota | 50000 microseconds |
| PID limit | 50 processes |
| Security | `no-new-privileges` flag |

**Image vs container:**
- The **image** (`codex-cpp:latest` etc.) is long-lived and reused. Precompiled headers / CDS archives are baked into the image layers.
- The **container** is ephemeral — fresh sandbox per submission, destroyed after cleanup.
- New containers start in ~100-300ms because the image is already loaded and the expensive setup (PCH, CDS) is paid **once** at image build time.

---

## 2. Infrastructure & Monitoring Setup

### Prometheus and Grafana Setup (Docker)

To monitor the Spring Boot application metrics, Prometheus and Grafana are configured to run in Docker containers locally.

**How it works:**
1. **Spring Boot (Local):** Spring Boot Actuator and Micrometer Prometheus registry are added to `pom.xml`. The application exposes metrics at `http://localhost:8080/actuator/prometheus`. Spring Security is configured to `permitAll()` on `/actuator/**` endpoints.
2. **Prometheus (Docker):** Runs on port `9090`. Configured via `prometheus.yml` to scrape `host.docker.internal:8080/actuator/prometheus` every 5 seconds. Using `host.docker.internal` allows the Docker container to reach the Spring Boot app running on the host machine.
3. **Grafana (Docker):** Runs on port `3000`. Connects to Prometheus as a data source and displays metrics on dashboards (e.g., using imported dashboard ID `11378`).

To start the monitoring stack:
```bash
docker compose -f docker-compose.monitoring.yml up -d
```

### Loki and Promtail Setup (Docker)

To monitor application logs, Loki and Promtail are configured alongside Prometheus and Grafana.

**How it works:**
1. **Spring Boot (Local):** Logback is configured via `logback-spring.xml` to write application logs to `logs/codex-platform.log`.
2. **Promtail (Docker):** Runs as a container and mounts the `logs/` directory. It reads `codex-platform.log` and pushes the logs to Loki. It is configured via `promtail-config.yml`.
3. **Loki (Docker):** Runs on port `3100`. It receives logs from Promtail and indexes them.
4. **Grafana (Docker):** Connects to Loki as a data source (URL: `http://loki:3100`). Logs can be queried in the "Explore" tab using LogQL (e.g., `{job="codex-platform"}`).

```bash
# Starts the entire monitoring stack including Loki & Promtail
docker compose -f docker-compose.monitoring.yml up -d
```

---

## 3. Problems Faced and Solutions

### 1. Race Condition: "Submission not found" during execution
**Status:** Solved
**Root Cause:** Redis enqueue happened before DB transaction committed.
**Solution:** Used `TransactionSynchronizationManager` to enqueue *after* commit.

### 2. Docker Connection Failure on Windows
**Status:** Solved
**Root Cause:** Incorrect Docker path.
**Solution:** Configured `execution.docker.host=npipe:////./pipe/docker_engine`.

### 3. NullPointerException in Docker Execution
**Status:** Solved
**Root Cause:** Unhandled null exit code.
**Solution:** Defaulted null exit code to `-1`.

### 4. Empty Callback Not Capturing stdout/stderr
**Status:** Solved
**Root Cause:** Empty `ResultCallback.Adapter`.
**Solution:** Used `ExecStartResultCallback(stdout, stderr)`.

### 5. Deprecated Docker Image: openjdk:17-slim
**Status:** Solved
**Root Cause:** Image removed from Docker Hub.
**Solution:** Replaced with `eclipse-temurin:17-jdk`.

### 6. Compilation Timeout Causing False COMPILATION_ERROR
**Status:** Solved
**Root Cause:** 5s timeout too short for heavy compilation on Windows Docker.
**Solution:** Increased compilation timeout to 60s and added a retry loop for exit code fetching.

### 7. Password Hash Exposed in API Response
**Status:** Solved
**Problem:** `passwordHash` was returned in JSON.
**Solution:** Added `@JsonIgnore` to the field.

### 8. Hardcoded Database Credentials
**Status:** Solved
**Problem:** Passwords in source control.
**Solution:** Used environment variables `${DB_PASSWORD:default}`.

### 9. Duplicate userId Extraction Logic
**Status:** Solved
**Problem:** Redundant JWT parsing.
**Solution:** Stored `userId` in SecurityContext via `JwtAuthenticationFilter`.

### 10. Container-Per-Test-Case Bottleneck (Major Performance Fix)
**Status:** Solved
**Problem:** New container created for every test case, causing massive slowdowns.
**Solution:** Refactored to single-container-per-submission (compile once, run N times via `docker exec`).

### 11. Redis Connection Drops Causing Worker Error Loop
**Status:** Solved
**Problem:** Tight error loops when Redis disconnected.
**Solution:** Added exponential backoff retry in `SubmissionWorker`.

### 12. Missing Authorization on Submission Read + SSE Stream
**Status:** Solved
**Problem:** Users could read other users' submissions.
**Solution:** Added ownership checks to read and SSE stream paths.

### 13. Docker Input Injection Risk + Runtime Hardening
**Status:** Solved
**Problem:** Input was written via shell command inside container.
**Solution:** Written to host workspace using Java I/O and mounted into container as read-only. Added `no-new-privileges`.

### 14. Submission Verdict Accuracy for Memory Kills
**Status:** Solved
**Problem:** OOM kills marked as generic errors.
**Solution:** Added `MEMORY_LIMIT_EXCEEDED` and mapped exit code `137` to it.

### 15. Redis Cloud Connection Issues (Local Development)
**Status:** Solved
**Problem:** `rediss://` protocol failure and auto-config conflicts.
**Solution:** Created manual `RedissonConfig.java` to explicitly connect using `redis://` to the cloud instance.

### 16. Docker Build: Maven Base Image Not Found
**Status:** Solved
**Problem:** `maven:3.9-eclipse-temurin-17-jammy` image tag didn't exist.
**Solution:** Updated Dockerfile builder stage to use `maven:3.9-eclipse-temurin-17`.

### 17. Frontend Login Sending Wrong Field (400 Bad Request)
**Status:** Solved
**Problem:** Login form sent `{ email, password }` but backend expects `{ username, password }`.
**Solution:** Changed `LoginForm.jsx` to use `username` state and `type="text"` input instead of `email`.

### 18. Mixed Content: Frontend HTTPS Calling Backend HTTP
**Status:** Solved
**Problem:** Vercel frontend (HTTPS) made direct axios calls to `http://3.109.238.141:8080/api` — browsers block mixed HTTP/HTTPS requests, causing "Network Error" on `/problems` and `/user/problems`.
**Solution:** Created a server-side catch-all proxy route at `app/api/proxy/[...path]/route.js`. All client API calls now go to `/api/proxy/*` (same-origin HTTPS), and the proxy forwards to the backend server-to-server (HTTP is fine for server-to-server).

### 19. Login Route Parsing Backend Response Incorrectly
**Status:** Solved
**Problem:** Login API route read `data.userId`, `data.username`, `data.email` (flat fields), but backend returns `{ user: { id, username, email }, token }` (nested). User object was empty `{}` after login.
**Solution:** Changed to `data.user ?? { id: data.userId, ... }` to correctly read the nested `user` object. Same fix applied to register route.

### 20. JWT Token Leaked to localStorage via Zustand Persist
**Status:** Solved
**Problem:** `authStore` used Zustand `persist` middleware which stored `{ user, token, isLoggedIn }` in localStorage. JWT was accessible via JavaScript — security violation.
**Solution:** Removed `token` from Zustand state entirely. Token now lives **only** in httpOnly cookie (set by login/register API routes). Proxy route reads the cookie and forwards it as `Authorization: Bearer` header to the backend. Client-side code never touches the token.

**Files changed:**
- `store/authStore.js` — removed `token` from state, removed `tokenStore` dependency
- `lib/axios.js` — removed `Authorization` header interceptor
- `hooks/useAuth.js` — `onSuccess` only stores `user`, not token
- `hooks/useCodeExecution.js` — removed `Authorization` header from SSE fetch
- `app/api/auth/login/route.js` — no longer sends token in JSON response
- `app/api/auth/register/route.js` — same
- `app/api/proxy/[...path]/route.js` — reads `auth_token` cookie, forwards as `Authorization: Bearer` header

### 21. Next.js Middleware Not Running (File Named Wrong)
**Status:** Solved
**Problem:** Route protection logic was in `proxy.js` with export `function proxy()`. Next.js ignores this — it expects `middleware.js` with export `function middleware()`. Result: no auth guards on routes, logged-in users see login page, unauthenticated users can access `/problems`.
**Solution:** Renamed `proxy.js` → `middleware.js` and changed export from `proxy` to `middleware`. Now:
- `/problems/*` without cookie → redirects to `/auth/login`
- `/auth/login` with valid cookie → redirects to `/problems`

### 22. C++ Compilation Timeout on EC2 (60s)
**Status:** Solved
**Problem:** `g++ -std=c++11 -o solution solution.cpp` with `#include <bits/stdc++.h>` takes 60s+ on resource-constrained EC2 Docker containers (128-256MB memory). Every C++ submission timed out with `COMPILATION_ERROR`.
**Root Cause:** `bits/stdc++.h` includes the entire C++ standard library — GCC parses it from scratch on every compilation.
**Solution:** Created custom Docker executor images with precompiled headers/optimizations baked in at build time:
- **C++:** Precompiled `bits/stdc++.h` → compile time drops from 60s to ~2s
- **Java:** CDS archive → JVM startup drops from ~3s to ~0.5s
- **Python:** Pre-compiled `.pyc` bytecode for stdlib
- **JavaScript:** V8 built-in module cache warmup

Custom Dockerfiles in `docker/executors/`. Build with `./build-all.sh` on EC2.

### 23. SSE AccessDeniedException After Result Sent
**Status:** Known (Backend)
**Problem:** After SSE emitter sends `COMPILATION_ERROR` result, Spring Security throws `AccessDeniedException: Access Denied` on the async dispatch. Error: "Unable to handle the Spring Security Exception because the response is already committed."
**Impact:** Low — the result IS delivered to the client before the error. The exception is a noisy log entry but doesn't affect functionality.
**Root Cause:** The SSE emitter's async completion callback triggers a new dispatch through the security filter chain, but the SecurityContext is empty at that point (original request context is gone).
**Potential Fix:** Configure Spring Security to permit the SSE endpoint's async dispatch, or suppress the error in a custom `AsyncUncaughtExceptionHandler`.

### 24. EBS Disk Full on EC2 (97% used)
**Status:** Solved
**Problem:** Building custom executor images failed with `no space left on device`. Only 309MB free on the 6.8GB root volume.
**Root Cause:** Accumulated unused Docker images (old `gcc:latest`, `ghcr.io/rocky4554/codex_code`, `ghcr.io/rocky4554/rag-project`, dangling layers) consumed ~3GB.
**Solution:** Ran `docker image prune -af` to remove all unused images. Freed 2.7GB.
**Ongoing concern:** The 6.8GB EBS volume is cramped. `codex-cpp:latest` alone is 1.63GB. Recommend increasing EBS to 15-20GB via AWS Console → EC2 → Volumes → Modify.

### 25. EC2 OOM During C++ Image Build
**Status:** Solved
**Problem:** Docker build of `codex-cpp:latest` with `g++ -O2 -x c++-header bits/stdc++.h` caused EC2 to become completely unresponsive (SSH timed out). Had to reboot via AWS Console.
**Root Cause:** The instance has only **911MB RAM** (not the expected 2GB of t2.small). `g++ -O2` compiling the entire C++ stdlib header needs ~800MB–1GB. Combined with the running `codex-app` JVM (~400MB), it triggered OOM kill / total memory exhaustion. No swap was configured.
**Solution:**
1. After reboot, stopped `codex-app` temporarily to free ~300MB RAM
2. Created a 1GB swap file: `sudo fallocate -l 1G /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`
3. Rewrote the Dockerfile without `-O2` (uses ~400MB instead of ~1GB)
4. Targeted the exact file path `/usr/local/include/c++/15.2.0/x86_64-linux-gnu/bits/stdc++.h` instead of `find /` (which found multiple copies and compiled each one)
5. After all 4 images built, removed the swap file to reclaim disk space
**Lesson:** Always check actual EC2 instance RAM (`free -h`) before heavy builds. Consider upgrading to t3.small (2GB) for safer builds, or build images elsewhere and push to a registry.

### 26. Executor Image Deployment Steps (Reference)
**Status:** Deployed to Production (EC2 3.109.238.141)
**Final deployed state:**

| Image | Size | Purpose |
|---|---|---|
| `codex-cpp:latest` | 1.63GB | Precompiled `bits/stdc++.h` → C++ compile time ~60s → ~1-2s |
| `codex-java:latest` | 434MB | CDS archive via `java -Xshare:dump` → JVM startup ~3s → ~0.5s |
| `codex-python:latest` | 126MB | Pre-compiled `.pyc` bytecode for stdlib |
| `codex-javascript:latest` | 200MB | V8 built-in module cache warmed |

**Deployment commands used:**
```bash
# SSH in
ssh -i <key>.pem ubuntu@3.109.238.141

# Build all images (in order — smallest first to conserve disk)
docker build -t codex-python:latest ~/executors/python
docker build -t codex-javascript:latest ~/executors/javascript
docker build -t codex-java:latest ~/executors/java
docker build -t codex-cpp:latest ~/executors/cpp  # needs swap enabled

# Restart the app
cd ~/Codex_code && docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# Verify
curl -s http://localhost:8080/api/languages
```

**Neon DB updates** (required because `DataInitializer` only inserts when table is empty):
```sql
UPDATE languages SET docker_image = 'codex-cpp:latest' WHERE name = 'C++';
UPDATE languages SET docker_image = 'codex-java:latest', execute_command = 'java -Xshare:on solution' WHERE name = 'Java';
UPDATE languages SET docker_image = 'codex-python:latest' WHERE name = 'Python';
UPDATE languages SET docker_image = 'codex-javascript:latest' WHERE name = 'JavaScript';
```

Run via `psql` on EC2 (reading credentials from `.env.production`) or through the Neon dashboard SQL editor.

### 28. Submissions Tab on Problem Page Was Non-Functional
**Status:** Solved
**Problem:** The "Submissions" tab in `ProblemPanel.jsx` was a static `<div>` with no click handler, no state, and no content. Users could not see any of their past submissions for a problem.
**Root Cause:** Two parts:
1. **Frontend:** `ProblemPanel.jsx` rendered both tab labels as plain divs. No `activeTab` state, no content switching, no submissions list component.
2. **Backend:** No endpoint existed to list the current user's submissions for a given problem. Only `POST /api/submissions` (create) and `GET /api/submissions/{id}` (get one) were available.

**Solution:**

**Backend changes:**
- `SubmissionController.java` — added `GET /api/submissions` with optional `?problemId={uuid}` query parameter. Returns a list of `SubmissionResponse` for the current user.
- `SubmissionService.java` — added `listMySubmissions(UUID problemId)` method. Uses existing `SubmissionRepository.findByUserIdAndProblemId()` (or `findByUserId` when `problemId` is null), joins with `SubmissionResult`, sorts newest-first, and maps to `SubmissionResponse` DTOs.

**Frontend changes:**
- `hooks/useProblemSubmissions.js` — new React Query hook that calls `GET /submissions?problemId={id}` (through the proxy). Only enabled when logged in and `problemId` is present. 10s staleTime.
- `components/problem-solve/ProblemPanel.jsx` — rewrote to:
  - Added `activeTab` state (`"description"` | `"submissions"`)
  - Made tabs clickable `<button>` elements with conditional styling
  - Extracted an internal `SubmissionsList` component that renders a table with Status, Language, Tests, Time, Memory, and Submitted columns
  - Added a `StatusBadge` component that colors verdicts (ACCEPTED=green, WRONG_ANSWER=red, RUNTIME/COMPILATION_ERROR=orange, TLE/MLE=amber, QUEUED/RUNNING=blue)
  - Uses `useLanguages()` hook to resolve `languageId` → language name
  - Handles loading, error, and empty states

**Endpoint:**
```
GET /api/submissions?problemId={uuid}
Authorization: Bearer <jwt>  (provided by proxy via httpOnly cookie)

Response: [
  {
    "id": "...",
    "userId": "...",
    "problemId": "...",
    "languageId": "...",
    "status": "ACCEPTED",
    "createdAt": "2026-04-06T...",
    "executionTimeMs": 45,
    "memoryUsedMb": 12,
    "passedTestCases": 2,
    "totalTestCases": 2,
    "stdout": "...",
    "stderr": null
  },
  ...
]
```

**Deployment:** Backend requires rebuild + push to GHCR + `docker compose pull && up -d` on EC2. Frontend auto-deploys via Vercel on push.

### 29. Windows Line Endings in .env.production on EC2
**Status:** Solved (workaround)
**Problem:** `source ~/Codex_code/.env.production` failed with `$'\r': command not found` on multiple lines. `psql` then got `NEON_DB_HOST` with a trailing `\r`, causing "could not translate host name" errors.
**Root Cause:** The `.env.production` file was created/edited on Windows and uploaded with CRLF line endings.
**Solution:** Used `grep ... | cut -d= -f2- | tr -d "\r"` to strip carriage returns when reading values in bash scripts.
**Permanent fix:** Run `dos2unix ~/Codex_code/.env.production` on EC2, or `sed -i 's/\r$//' ~/Codex_code/.env.production`.
