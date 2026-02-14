# Quick Start Guide - Codex Platform

## Prerequisites Check

Before running the application, ensure you have:

- ✅ Java 17 or higher
- ✅ Maven 3.6+
- ✅ Docker (running)
- ✅ PostgreSQL (or use Docker)
- ✅ Redis (or use Docker)

## Quick Setup (Local PostgreSQL + Docker Redis)

### 1. Start Redis (using Docker Compose)

This repo includes `docker-compose.yml` for Redis. PostgreSQL is now configured to run locally (outside Docker).

```powershell
cd "e:\Personal Projects\Codex"
docker compose up -d
```

You should see:
- Redis: `localhost:6379`

### 2. Local PostgreSQL Setup

Ensure you have PostgreSQL installed on your Windows machine and running on port **5432**.

1.  **Create Database**: Open pgAdmin and create a database named `codex`.
2.  **Verify Service**: Ensure the PostgreSQL service is running.

### 3. Configure Environment

The app defaults are set in `src/main/resources/application-dev.properties` to connect to `localhost:5432`.

If you need to override settings via environment variables:

```env
# Local settings (usually defaults)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=codex
DB_USERNAME=postgres
DB_PASSWORD=your_password

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET=your-super-secret-256-bit-key
```

### 4. Build and Run

```powershell
cd "e:\Personal Projects\Codex"

# Run the application
mvn spring-boot:run
```

Application will start at: http://localhost:8080
Once started, it will automatically create tables in your `codex` database (due to `ddl-auto=create`). 

> **Important**: After the first run, change `spring.jpa.hibernate.ddl-auto=update` in `application-dev.properties` to avoid losing data.

## Quick Test (Postman)

### 0. Create a Postman environment

Create an environment called **`Codex Local`** and add these variables:

- `baseUrl`: `http://localhost:8080`
- `token`: *(leave empty)*
- `problemId`: *(leave empty)*
- `languageId`: *(leave empty)*
- `submissionId`: *(leave empty)*

> Tip: For protected endpoints, in Postman set **Authorization → Bearer Token →** `{{token}}`.

### 1. Register

- **Method**: `POST`
- **URL**: `{{baseUrl}}/api/auth/register`
- **Headers**: `Content-Type: application/json`
- **Body** (raw → JSON):

```json
{
  "username": "testuser",
  "email": "test@test.com",
  "password": "test123"
}
```

### 2. Login (auto-save JWT token)

- **Method**: `POST`
- **URL**: `{{baseUrl}}/api/auth/login`
- **Headers**: `Content-Type: application/json`
- **Body** (raw → JSON):

```json
{
  "username": "testuser",
  "password": "test123"
}
```

In the **Tests** tab, paste this to automatically store the token:

```javascript
const json = pm.response.json();
pm.environment.set("token", json.token);
```

### 3. Get Problems (store `problemId`)

- **Method**: `GET`
- **URL**: `{{baseUrl}}/api/problems`

In the **Tests** tab:

```javascript
const problems = pm.response.json();
pm.environment.set("problemId", problems[0].id);
```

### 4. Get Languages (store `languageId`)

- **Method**: `GET`
- **URL**: `{{baseUrl}}/api/languages`

In the **Tests** tab:

```javascript
const languages = pm.response.json();
pm.environment.set("languageId", languages[0].id);
```

### 5. Submit Code (store `submissionId`)

- **Method**: `POST`
- **URL**: `{{baseUrl}}/api/submissions`
- **Authorization**: Bearer Token `{{token}}`
- **Headers**: `Content-Type: application/json`
- **Body** (raw → JSON):

```json
{
  "problemId": "{{problemId}}",
  "languageId": "{{languageId}}",
  "sourceCode": "print('Hello, World!')"
}
```

In the **Tests** tab:

```javascript
const json = pm.response.json();
pm.environment.set("submissionId", json.submissionId);
```

### 6. Watch Real-time status (SSE)

Postman doesn’t display Server-Sent Events streams nicely.

Use a terminal for the SSE stream:

```powershell
curl "{{baseUrl}}/api/submissions/{{submissionId}}/events" `
  -H "Authorization: Bearer {{token}}"
```

## Common Issues

### Docker Connection Error

**Linux/Mac Error:** `Permission denied on /var/run/docker.sock`
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### PostgreSQL Connection Error

Check if local PostgreSQL is running:
- Open **Services** (services.msc) and look for `postgresql-x64-XX`.
- Ensure it is **Running**.

Test connection via psql:
```powershell
psql -U postgres -d codex -p 5432
```

Note: This project is now configured to use port **5432** (local) instead of 5433 (Docker).

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

## API Endpoints (with headers/payload/response)

Full request/response examples for every endpoint live here:
- `api-docs/api-docs.md`

Quick index:
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/problems`
- `GET /api/problems/{id}`
- `GET /api/languages`
- `POST /api/submissions` (Authorization required)
- `GET /api/submissions/{id}/events` (SSE, Authorization required)
- `GET /api/user/profile` (Authorization required)
- `GET /api/user/submissions` (Authorization required)
- `GET /api/user/problems` (Authorization required)

## Stop Services

```powershell
# Stop application (Ctrl+C)

# Stop Docker containers
docker stop codex-postgres codex-redis
docker rm codex-postgres codex-redis
```

---

🎉 **You're all set!** The code execution platform is ready to judge code submissions.
