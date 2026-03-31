# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Codex** is a Spring Boot backend for a code execution platform (like LeetCode). Users submit code, which runs in isolated Docker containers against test cases. Built with Java 17, Spring Boot 3.2.1, PostgreSQL, and Redis.

## Build & Run Commands

```bash
# Build fat JAR (skip tests)
mvn clean package -DskipTests

# Run locally (uses dev profile by default)
mvn spring-boot:run

# Run with explicit profile
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# Run tests
mvn test

# Build Docker image
docker build -t codex:latest .
```

## Local Development Setup

The app requires PostgreSQL and Redis running locally before starting:

```bash
# Start Redis only (Postgres runs locally, not in Docker for dev)
docker-compose up redis -d

# Start full monitoring stack (separate compose file)
docker compose -f docker-compose.monitoring.yml up -d
```

Dev profile config (`application-dev.properties`):
- PostgreSQL: `localhost:5432/codex`
- Redis: `localhost:6379`
- Docker Host: `npipe:////./pipe/docker_engine` (Windows Docker Desktop)
- Temp dir: `C:/temp/codex/submissions`

Production profile (`prod`) uses Neon Cloud PostgreSQL + Redis Cloud. Set via `SPRING_PROFILES_ACTIVE=prod` and populate `.env.production`.

## Architecture

### Domain-Driven Package Structure

Code is organized by business domain under `com.codex.platform/`:

- **`auth/`** — JWT-based stateless auth (register/login, `JwtAuthenticationFilter`, `JwtUtil`)
- **`submission/`** — Submission lifecycle: create → queue → execute → result
- **`execution/`** — Docker-based code execution (`ExecutionService`, `DockerExecutor`)
- **`queue/`** — Redis job queue + distributed locking (`QueueService`, `SubmissionWorker`)
- **`realtime/`** — Server-Sent Events for live submission status updates
- **`problem/`** — Problem definitions and test cases (mostly read-only)
- **`user/`** — User profiles and per-problem progress tracking
- **`monitoring/`** — Health and Prometheus metrics endpoints
- **`config/`** — `SecurityConfig`, `DockerConfig`, `RedissonConfig`, `DataInitializer`
- **`common/`** — Enums, global exception handler, `OutputNormalizer`

### Code Execution Flow

1. `POST /api/submissions` → saves Submission (status=QUEUED), pushes ID to Redis queue
2. `SubmissionWorker` (background thread pool) dequeues IDs
3. Worker acquires **Redisson RLock** per submission to prevent duplicate execution
4. `ExecutionService` → `DockerExecutor`:
   - Writes source code to temp dir
   - Creates one Docker container per submission (not per test case)
   - Compiles once, then runs all test cases in same container
   - Applies CPU/memory/PID/network constraints
   - Cleans up container after completion
5. `ResultProcessor` saves results, updates `UserProblemStatus`
6. `SseService` broadcasts status events to frontend SSE listeners

### Key Design Decisions

- **One container per submission** (not per test case) — reduces overhead, enables single compilation
- **SSE over WebSockets** — simpler HTTP-based real-time updates
- **Redisson RLock** — distributed lock prevents race conditions across workers
- **`@EnableAsync`** on main class — worker threads run asynchronously
- **UTC timezone** forced at startup — prevents PostgreSQL JDBC timestamp issues
- **Hibernate `ddl-auto=update`** — no migration framework (schema auto-managed)

### Security Configuration (`SecurityConfig`)

Public endpoints (no JWT required):
- `POST /api/auth/**`
- `GET /api/problems/**`
- `GET /api/languages`
- `/actuator/**`

All other endpoints require a valid JWT Bearer token.

## Environment Variables

Key variables (see `.env.example`):

| Variable | Purpose |
|----------|---------|
| `SPRING_PROFILES_ACTIVE` | `dev` or `prod` |
| `JWT_SECRET` | Must be 256+ bit secret |
| `NEON_DB_*` | Prod PostgreSQL (Neon) credentials |
| `REDIS_URL` / `REDIS_PASSWORD` | Redis connection |
| `EXECUTION_DOCKER_HOST` | Docker socket path |
| `EXECUTION_TEMP_DIR` | Working dir for code files |
| `EXECUTION_WORKER_COUNT` | Number of background worker threads |
| `APP_CORS_ALLOWED_ORIGINS` | Comma-separated allowed frontend URLs |

## Observability

- **Prometheus** scrapes `/actuator/prometheus` every 5s (custom metrics: submission counts, execution time)
- **Loki** receives logs via Promtail sidecar (reads from `/app/logs` Docker volume)
- **Grafana** visualizes both — configured in `docker-compose.monitoring.yml`
- Monitoring stack runs on an external Docker network named `monitoring`

## Developer Docs

Detailed guides are in `dev_docs/`:
- `api-docs.md` — Full REST API reference
- `QUICKSTART.md` — Step-by-step local setup with Postman examples
- `commands.md` — Useful Docker & Maven commands
- `observability.md` — Monitoring stack setup
- `problems.md` — Troubleshooting common issues
