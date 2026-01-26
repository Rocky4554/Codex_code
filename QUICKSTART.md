# Quick Start Guide - Codex Platform

## Prerequisites Check

Before running the application, ensure you have:

- ✅ Java 17 or higher
- ✅ Maven 3.6+
- ✅ Docker (running)
- ✅ PostgreSQL (or use Docker)
- ✅ Redis (or use Docker)

## Quick Setup (Using Docker for Dependencies)

### 1. Start PostgreSQL and Redis

```powershell
# Start PostgreSQL
docker run -d --name codex-postgres `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=codex `
  -p 5432:5432 `
  postgres:14

# Start Redis
docker run -d --name codex-redis `
  -p 6379:6379 `
  redis:7

# Pull language Docker images
docker pull python:3.11-slim
docker pull openjdk:17-slim
docker pull gcc:latest
docker pull node:20-slim
```

### 2. Configure Environment

Create `.env` file (or set environment variables):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=codex
DB_USERNAME=postgres
DB_PASSWORD=postgres

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

JWT_SECRET=your-super-secret-256-bit-key-change-this-in-production-please-make-it-long-enough

# Windows Docker:
DOCKER_HOST=tcp://localhost:2375

# Linux/Mac Docker:
# DOCKER_HOST=unix:///var/run/docker.sock
```

> **Windows Users**: Enable "Expose daemon on tcp://localhost:2375 without TLS" in Docker Desktop Settings

### 3. Build and Run

```powershell
cd "e:\Personal Projects\Codex"

# Build the project
mvnw.cmd clean install

# Run the application
mvnw.cmd spring-boot:run
```

Application will start at: http://localhost:8080

## Quick Test

### 1. Register a User

```powershell
curl -X POST http://localhost:8080/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"testuser\",\"email\":\"test@test.com\",\"password\":\"test123\"}'
```

### 2. Login

```powershell
curl -X POST http://localhost:8080/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"testuser\",\"password\":\"test123\"}'
```

Copy the `token` from the response.

### 3. Get Problems

```powershell
curl http://localhost:8080/api/problems
```

### 4. Get Languages

```powershell
curl http://localhost:8080/api/languages
```

Copy a `problemId` and `languageId` from the responses.

### 5. Submit Code

**Python "Hello World" solution:**

```powershell
$token = "your-jwt-token-here"
$problemId = "problem-uuid-here"
$languageId = "python-language-uuid-here"

curl -X POST http://localhost:8080/api/submissions `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d "{\"problemId\":\"$problemId\",\"languageId\":\"$languageId\",\"sourceCode\":\"print('Hello, World!')\"}"
```

Copy the `submissionId` from the response.

### 6. Watch Real-time Status (SSE)

```powershell
curl http://localhost:8080/api/submissions/$submissionId/events `
  -H "Authorization: Bearer $token"
```

You should see status updates:
- `QUEUED`
- `RUNNING`
- `ACCEPTED` (or other verdict)

## Common Issues

### Docker Connection Error

**Windows Error:** `Cannot connect to Docker daemon`
- Solution: Enable "Expose daemon on tcp://localhost:2375" in Docker Desktop
- Set: `DOCKER_HOST=tcp://localhost:2375`

**Linux/Mac Error:** `Permission denied on /var/run/docker.sock`
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### PostgreSQL Connection Error

Check if PostgreSQL is running:
```powershell
docker ps | findstr postgres
```

Test connection:
```powershell
docker exec -it codex-postgres psql -U postgres -d codex
```

### Redis Connection Error

Check if Redis is running:
```powershell
docker ps | findstr redis
```

Test connection:
```powershell
docker exec -it codex-redis redis-cli ping
# Should return: PONG
```

### Port Already in Use

If port 8080 is already in use, change it:
```env
PORT=8081
```

Or in `application.yml`:
```yaml
server:
  port: 8081
```

## What Happens When You Submit Code?

1. ✅ **Submission Created** - Your code is saved with status `QUEUED`
2. 📤 **Queued to Redis** - Submission ID is added to the processing queue
3. ⚙️ **Worker Picks Up** - Background worker dequeues and acquires lock
4. 🐳 **Docker Execution** - Code runs in isolated container with security constraints
5. 🧪 **Test Cases Run** - Each test case is executed and output is compared
6. 📊 **Results Saved** - Verdict and results are saved to database
7. 📡 **Real-time Update** - SSE sends final status to frontend
8. 🧹 **Cleanup** - Docker container and temp files are removed

## Monitoring

### Check Running Containers

```powershell
docker ps
```

You should NOT see code execution containers lingering (they're auto-cleaned).

### Check Logs

```powershell
# Application logs show execution flow
# Look for: "Submission worker started"
# Look for: "Dequeued submission: ..."
# Look for: "Execution completed for submission: ..."
```

## Next Steps

1. ✅ Test with different languages (Java, C++, JavaScript)
2. ✅ Test with different verdicts (wrong answer, TLE, etc.)
3. ✅ Verify SSE events are received
4. ✅ Check database for submission results
5. ✅ Monitor Docker container cleanup

## Database Inspection

```powershell
docker exec -it codex-postgres psql -U postgres -d codex

# View tables
\dt

# View submissions
SELECT id, user_id, problem_id, status FROM submissions;

# View results
SELECT * FROM submission_results;

# View user progress
SELECT * FROM user_problem_status;
```

## Stop Services

```powershell
# Stop application (Ctrl+C)

# Stop Docker containers
docker stop codex-postgres codex-redis
docker rm codex-postgres codex-redis
```

---

🎉 **You're all set!** The code execution platform is ready to judge code submissions.
