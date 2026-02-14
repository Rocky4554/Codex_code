# Problems Faced

## 1. Race Condition: "Submission not found" during execution

**Date:** 2026-02-13
**Status:** Solved

**Error:**
```
java.lang.IllegalArgumentException: Submission not found
    at com.codex.platform.execution.service.ExecutionService.lambda$0(ExecutionService.java:46)
```

**Root Cause:**
In `SubmissionService.submitCode()`, the database INSERT was wrapped in a `@Transactional` method, but the Redis enqueue happened immediately. The worker dequeued the ID and fetched the record before the DB transaction had committed.

**Solution:**
Used `TransactionSynchronizationManager` to ensure the Redis enqueue only happens after the DB transaction successfully commits.

```java
TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
    @Override
    public void afterCommit() {
        queueService.enqueue(submissionId);
    }
});
```

---

## 2. Docker Connection Failure on Windows

**Date:** 2026-02-13
**Status:** Solved

**Error:**
```
java.nio.file.NoSuchFileException: E:\pipe\docker_engine
```

**Root Cause:**
Incorrect Docker host path configuration for Windows environments in `application-dev.properties`.

**Solution:**
There are **two working options** on Windows. Prefer the named pipe (no insecure TCP), and keep TCP 2375 as a fallback.

1. **Recommended (Docker Desktop named pipe):**
   - Set:
     - `execution.docker.host=npipe:////./pipe/docker_engine`
   - Notes:
     - This avoids enabling the insecure “Expose daemon on tcp://localhost:2375 without TLS” setting.
     - If you accidentally set a path like `E:\\pipe\\docker_engine` you’ll get `NoSuchFileException`.

2. **Fallback (Docker Desktop TCP 2375):**
   - Enable in Docker Desktop:
     - **Settings → General → “Expose daemon on tcp://localhost:2375 without TLS”**
   - Set:
     - `execution.docker.host=tcp://localhost:2375`

3. Upgraded `docker-java` / transport dependencies (example: `docker-java-transport-zerodep`) to a newer version for improved Windows support.

---

## 3. NullPointerException in Docker Execution

**Date:** 2026-02-13
**Status:** Solved

**Error:**
```
java.lang.NullPointerException: Cannot invoke "java.lang.Long.intValue()" because the return value of "...getExitCodeLong()" is null
```

**Root Cause:**
`DockerExecutor` was calling `.intValue()` on the result of `getExitCodeLong()` without checking for null. In some cases (like immediate execution or specific Docker responses), the exit code might not be immediately available from the inspect command.

**Solution:**
Implemented null-safe handling for the exit code. If null, it defaults to `-1` to indicate an incomplete or failed execution state instead of crashing the worker thread.

```java
Long exitCodeLong = dockerClient.inspectExecCmd(execId).exec().getExitCodeLong();
int exitCode = (exitCodeLong != null) ? exitCodeLong.intValue() : -1;
```

---

## 4. Empty Callback Not Capturing stdout/stderr

**Date:** 2026-02-13
**Status:** Solved

**Error:**
```
java.lang.NullPointerException: Cannot invoke "java.lang.Long.intValue()" because the return value of "...getExitCodeLong()" is null
```

**Root Cause:**
`DockerExecutor.executeCommandInContainer()` was using an empty `ResultCallback.Adapter<>()` which doesn't capture any output. It also required a separate, redundant `logContainerCmd` call. Most critically, `awaitCompletion` on the empty adapter didn't properly wait for the command to finish, so the exit code was null when inspected.

**Solution:**
Replaced the empty adapter with `ExecStartResultCallback(stdout, stderr)` which captures output directly and waits for the command to truly finish. Removed the redundant `logContainerCmd` call.

```java
dockerClient.execStartCmd(execId)
        .exec(new ExecStartResultCallback(stdout, stderr))
        .awaitCompletion(timeLimitMs, TimeUnit.MILLISECONDS);
```

---

## 5. Deprecated Docker Image: openjdk:17-slim

**Date:** 2026-02-13
**Status:** Solved

**Error:**
```
Error response from daemon: failed to resolve reference "docker.io/library/openjdk:17-slim": not found
```

**Root Cause:**
The `openjdk` official Docker images have been deprecated and removed from Docker Hub. The `DataInitializer.java` was seeding `openjdk:17-slim` for the Java language.

**Solution:**
Replaced with `eclipse-temurin:17-jdk` (the maintained successor) in `DataInitializer.java` and updated the database record via SQL:

```sql
UPDATE languages SET docker_image = 'eclipse-temurin:17-jdk' WHERE name = 'Java';
```

---

## 6. Compilation Timeout Causing False COMPILATION_ERROR

**Date:** 2026-02-13
**Status:** Solved

**Error:**
```
WARN: Exit code is null for exec ..., command may have timed out
Execution completed for submission: ... with status: COMPILATION_ERROR
```

**Root Cause:**
The compilation step in `DockerExecutor` was using the problem's execution time limit (typically 5 seconds). Java compilation inside Docker on Windows easily exceeds this. When `awaitCompletion` timed out, Docker exec hadn't finished, so the exit code was null → defaulted to `-1` → treated as compilation failure.

**Solution:**
1. Used a separate, longer timeout for compilation (Windows Docker is slow on first run).
   - Initially increased to **30 seconds**
   - Later increased to **60 seconds** after seeing C++ compilation occasionally exceed 30s inside `gcc:latest` on Windows.
2. Checked the return value of `awaitCompletion()` to properly detect timeouts vs completions.
3. Added a retry loop (5 attempts × 500ms) when fetching the exit code, to handle Docker's brief delay in updating it after completion.

```java
int compileTimeoutMs = 60_000; // (or Math.max(timeLimitMs, 60_000))

boolean completed = dockerClient.execStartCmd(execId)
        .exec(new ExecStartResultCallback(stdout, stderr))
        .awaitCompletion(timeLimitMs, TimeUnit.MILLISECONDS);

// Retry loop for exit code
for (int i = 0; i < 5; i++) {
    Long exitCodeLong = dockerClient.inspectExecCmd(execId).exec().getExitCodeLong();
    if (exitCodeLong != null) { exitCode = exitCodeLong.intValue(); break; }
    Thread.sleep(500);
}
```

---

## 17. Docker Container Creation Hanging (Docker Desktop Unresponsive)

**Date:** 2026-02-14  
**Status:** Solved / Mitigated

**Symptom:**
- App logs stuck at:
  - `Creating container for image: gcc:latest ...`
- Even CLI commands like `docker image ls` / `docker ps` may hang.

**Root Cause:**
When Docker Desktop (WSL2 backend) becomes slow or unresponsive, docker-java calls like
`dockerClient.createContainerCmd(...).exec()` can block indefinitely. This was amplified when the
required image wasn't already present locally (implicit pull / disk pressure).

**Solution:**
1. Added an image presence check + pull:
   - `ensureImageExists(dockerImage)` uses `inspectImageCmd` and pulls missing images.
   - Pull is bounded with a timeout (5 minutes).
2. Wrapped container create+start in a hard timeout (60 seconds) so the worker fails fast instead of hanging forever.
3. Operational fix:
   - Restart Docker Desktop if Docker CLI commands hang.
   - Pre-pull language images (`gcc:latest`, `python:3.11-slim`, `eclipse-temurin:17-jdk`, `node:20-slim`) before heavy testing.

---

## 7. Password Hash Exposed in API Response

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
`GET /api/user/profile` returned the `User` entity directly, including the `passwordHash` field in the JSON response. This is a serious security vulnerability.

**Solution:**
Added `@JsonIgnore` on the `passwordHash` field in `User.java` so Jackson never serializes it.

---

## 8. Hardcoded Database Credentials

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
`application-dev.properties` had hardcoded database username/password (`postgres` / `Raunak@123`) checked into source control.

**Solution:**
Replaced with environment variable references using Spring's `${VAR:default}` syntax:
```properties
spring.datasource.url=jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:codex}
spring.datasource.username=${DB_USERNAME:postgres}
spring.datasource.password=${DB_PASSWORD:Raunak@123}
```

---

## 9. Duplicate userId Extraction Logic

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
`UserController` and `SubmissionService` both had identical `extractUserIdFromRequest()` methods that manually re-parsed the JWT from the `Authorization` header.

**Solution:**
Updated `JwtAuthenticationFilter` to store `userId` in the SecurityContext principal (as a `Map<String, Object>`). Added a static utility method `JwtAuthenticationFilter.getCurrentUserId()` that reads it from SecurityContext. Removed duplicate methods from `UserController` and `SubmissionService`.

---

## 10. ProblemController Directly Used Repository

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
`ProblemController` injected `ProblemRepository` directly, bypassing the service layer. This made it hard to add business logic (caching, filtering, etc).

**Solution:**
Created `ProblemService` with `getAllProblems(Pageable)` and `getProblemById(UUID)` methods. Updated `ProblemController` to use the service.

---

## 11. No Pagination on List Endpoints

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
`GET /api/problems` and `GET /api/user/submissions` returned ALL records with `findAll()`. With thousands of records, this would cause performance issues.

**Solution:**
Added Spring's `Pageable` parameter to both endpoints with `@PageableDefault(size = 20)`. Added `Page<Submission> findByUserId(UUID, Pageable)` to `SubmissionRepository`.

---

## 12. Hardcoded Worker Thread Count

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
`SubmissionWorker` had `int workerCount = 2` hardcoded, making it impossible to adjust concurrency without recompilation.

**Solution:**
Made it configurable via `@Value("${execution.worker-count:2}")` and added `execution.worker-count=2` to `application-dev.properties`.

---

## 13. No Graceful Worker Shutdown (RedissonShutdownException)

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
Workers were daemon threads with no shutdown hook. During application stop, Redisson would close first, and the still-running worker threads would get `RedissonShutdownException`.

**Solution:**
Added `@PreDestroy` method to `SubmissionWorker` that interrupts all worker threads and waits up to 10 seconds for them to finish. Also wrapped lock release in try-catch to handle race conditions during shutdown.

---

## 14. Inconsistent Error Responses

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
`GlobalExceptionHandler` returned ad-hoc `Map<String, String>` responses. No consistent structure for error responses across the API.

**Solution:**
Created `ErrorResponse` DTO with `timestamp`, `status`, `error`, `message`, `path`, and optional `fieldErrors`. Updated all exception handlers to use it. Added handler for `IllegalStateException` (401 Unauthorized).

---

## 15. Missing Database Indexes on Submissions

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
No indexes on `userId` or `problemId` columns in the `submissions` table. Queries filtering by these columns would do full table scans.

**Solution:**
Added `@Index` annotations on the `Submission` entity:
```java
@Table(name = "submissions", indexes = {
    @Index(name = "idx_submission_user", columnList = "userId"),
    @Index(name = "idx_submission_problem", columnList = "problemId")
})
```

---

## 16. Container-Per-Test-Case Bottleneck (Major Performance Fix)

**Date:** 2026-02-14
**Status:** Solved

**Problem:**
`ExecutionService` called `dockerExecutor.executeCode()` for EVERY test case, and `executeCode()` created a new Docker container each time. For a problem with N test cases, this meant N container creates + starts + cleanups. On Windows Docker, each container lifecycle took 5-10 seconds, making execution extremely slow.

**Solution:**
Refactored into a single-container-per-submission pattern:
1. `DockerExecutor` now exposes fine-grained lifecycle methods: `prepareTempDirectory()`, `createAndStartContainer()`, `compileInContainer()`, `runTestCase()`, `cleanup()`.
2. `ExecutionService` creates ONE container, compiles ONCE, then runs each test case via `docker exec` in the same container.
3. Cleanup runs in a `finally` block to ensure container removal even on errors.

**Impact:** ~5-10x speedup for submissions with multiple test cases.

