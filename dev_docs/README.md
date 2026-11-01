# Codex Platform - Code Execution Backend

A Spring Boot application for executing user-submitted code in isolated Docker containers with real-time feedback.

> **Deployment:** frontend on Vercel (https://sprintcode.vercel.app), backend on Render, PostgreSQL on Supabase, Redis on Redis Cloud, code execution on an AWS EC2 executor agent. See [infrastructure.md](infrastructure.md).

## Features

- 🔐 **JWT Authentication** - Secure stateless authentication
- 🐳 **Docker Execution** - Isolated code execution with security constraints
- 📊 **Real-time Updates** - Server-Sent Events (SSE) for live status tracking
- 🔄 **Async Processing** - Redis-based job queue with distributed locking
- 💾 **PostgreSQL Database** - Persistent storage for submissions and results
- 🎯 **Multiple Languages** - Support for Python, Java, C++, JavaScript
- ⚡ **Resource Limits** - CPU and memory constraints per execution
- 🧪 **Test Case Management** - Automated testing with multiple test cases

## Architecture

### Modular Monolith Design

```
com.codex.platform
├── auth                // JWT authentication & security
├── user                // User management & profiles
├── problem             // Problems & test cases
├── submission          // Submission handling & results
├── execution           // Docker-based code execution
├── queue               // Redis queue & worker
├── realtime            // SSE real-time updates
├── config              // Configuration classes
└── common              // Shared utilities & enums
```

### System Flow

1. **User submits code** → JWT validated
2. **Submission saved** → Status: QUEUED
3. **Pushed to Redis queue** → Immediate response to user
4. **Worker picks job** → Acquires distributed lock
5. **Docker executes code** → Runs test cases
6. **Results processed** → Database updated atomically
7. **SSE sends updates** → Real-time status to frontend

## Prerequisites

- **Java 17+**
- **Maven 3.6+**
- **PostgreSQL 14+** (production uses Supabase)
- **Redis 6+**
- **Docker** (running on host machine)

## Setup

### 1. Clone Repository

```bash
cd e:/Personal Projects/Codex
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=codex
DB_USERNAME=postgres
DB_PASSWORD=your_password

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET=your-256-bit-secret-key

DOCKER_HOST=unix:///var/run/docker.sock
```

### 3. Start Dependencies

**PostgreSQL:**
```bash
# Using Docker
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:14
```

**Redis:**
```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:7
```

### 4. Build & Run

```bash
# Build
./mvnw clean install

# Run
./mvnw spring-boot:run
```

Application will start on `http://localhost:8080`

## API Endpoints

### Authentication

**Register**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Login**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepass123"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userId": "uuid",
  "username": "john_doe",
  "email": "john@example.com"
}
```

### Problems

**Get All Problems**
```bash
GET /api/problems
```

**Get Problem by ID**
```bash
GET /api/problems/{id}
```

### Submissions

**Submit Code** (Protected)
```bash
POST /api/submissions
Authorization: Bearer {token}
Content-Type: application/json

{
  "problemId": "uuid",
  "languageId": "uuid",
  "sourceCode": "print('Hello, World!')"
}

Response:
{
  "submissionId": "uuid",
  "status": "QUEUED",
  "message": "Submission queued for execution"
}
```

**Real-time Updates** (SSE)
```bash
GET /api/submissions/{id}/events
Authorization: Bearer {token}

Events:
- QUEUED
- RUNNING
- ACCEPTED
- WRONG_ANSWER
- TIME_LIMIT_EXCEEDED
- RUNTIME_ERROR
- COMPILATION_ERROR
```

### User

**Get Profile** (Protected)
```bash
GET /api/user/profile
Authorization: Bearer {token}
```

**Get My Submissions** (Protected)
```bash
GET /api/user/submissions
Authorization: Bearer {token}
```

**Get My Problems** (Protected)
```bash
GET /api/user/problems
Authorization: Bearer {token}
```

### Languages

**Get Supported Languages**
```bash
GET /api/languages
```

## Configuration

### Application Properties

Located in `src/main/resources/application.yml`

**Key configurations:**
- `execution.default-time-limit-ms`: Default time limit (5000ms)
- `execution.default-memory-limit-mb`: Default memory limit (256MB)
- `jwt.expiration`: JWT expiration time (24 hours)

### Docker Images

Supported languages and their Docker images:

| Language   | Version | Docker Image        |
|------------|---------|---------------------|
| Python     | 3.11    | python:3.11-slim    |
| Java       | 17      | openjdk:17-slim     |
| C++        | 11      | gcc:latest          |
| JavaScript | 20      | node:20-slim        |

## Security

### Docker Execution Constraints

- ✅ No network access
- ✅ CPU limits (50% quota)
- ✅ Memory limits (configurable)
- ✅ Process limits (50 PIDs)
- ✅ Time limits (per problem)
- ✅ Automatic cleanup

### Authentication

- Stateless JWT authentication
- Password hashing with BCrypt
- Protected API routes
- Token expiration

## Development

### Project Structure

```
e:/Personal Projects/Codex
├── src/main/java/com/codex/platform/
│   ├── auth/               # Authentication
│   ├── user/               # User management
│   ├── problem/            # Problems & test cases
│   ├── submission/         # Submissions & results
│   ├── execution/          # Docker execution
│   ├── queue/              # Redis queue & worker
│   ├── realtime/           # SSE
│   ├── config/             # Configuration
│   └── common/             # Utilities
├── src/main/resources/
│   └── application.yml     # Configuration
├── pom.xml                 # Maven dependencies
└── README.md
```

### Key Components

**Worker (Background Service):**
- Runs on application startup
- Continuously polls Redis queue
- Acquires distributed locks
- Processes submissions asynchronously

**Execution Service:**
- Loads submission, problem, test cases
- Executes code in Docker container
- Normalizes output for comparison
- Determines verdict (AC, WA, TLE, RE, CE)
- Saves results transactionally

**SSE Service:**
- Manages SSE emitters
- Broadcasts status updates
- Completes connection on terminal status

## Future Enhancements

This system is designed as a **modular monolith** with future microservices extraction in mind:

- 🔄 Extract worker into separate service
- 📊 Add analytics and statistics
- 🎨 Implement problem tagging/categories
- 👥 Add social features (leaderboards, contests)
- 🔍 Implement code plagiarism detection
- 📝 Add editorial/discussion sections

## Troubleshooting

### Docker Connection Issues

**Windows:**
```
DOCKER_HOST=tcp://localhost:2375
```

Enable "Expose daemon on tcp://localhost:2375 without TLS" in Docker Desktop settings.

**Linux/Mac:**
```
DOCKER_HOST=unix:///var/run/docker.sock
```

Ensure Docker daemon is running.

### Redis Connection Issues

Check Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Database Issues

Check PostgreSQL connection:
```bash
psql -h localhost -U postgres -d codex
```

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
