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
  "dockerImage": "python:3.11-slim",
  "fileExtension": ".py",
  "compileCommand": "",
  "executeCommand": "python solution.py"
}
```

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
