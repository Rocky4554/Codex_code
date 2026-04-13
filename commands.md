# Codex Commands Reference

## EC2 Server Commands (Executor Agent)

### SSH into Server
```bash
ssh -i C:\keys\koder.pem ubuntu@3.109.238.141
```

### Check Server Status
```bash
# Check system resources
uptime
free -h
df -h /

# Check Docker containers
docker ps -a
docker stats --no-stream

# Check executor agent health
curl http://localhost:8081/v1/healthz
```

### Manage Executor Agent
```bash
# View logs
docker logs codex-executor-agent -f

# Restart executor agent
docker restart codex-executor-agent

# Stop executor agent
docker stop codex-executor-agent

# Start executor agent
cd /home/ubuntu/codex-execution
docker compose -f docker-compose.ec2.yml --env-file .env up -d

# Rebuild and start (after config changes)
docker stop codex-executor-agent
docker rm codex-executor-agent
docker compose -f docker-compose.ec2.yml --env-file .env up -d
```

### Test Executor (All Languages)
```bash
# Run language tests
/home/ubuntu/test-all-languages.sh
```

### Manual Cleanup
```bash
# Run cleanup script manually
/home/ubuntu/codex-cleanup.sh

# Or run Docker cleanup directly
docker container prune -f
docker image prune -f

# Free RAM cache
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
```

### Check Cron Jobs
```bash
# View scheduled cleanup jobs
crontab -l

# View cleanup logs
cat /home/ubuntu/codex-cleanup.log
```

### Build Language Images
```bash
cd /home/ubuntu/codex-execution
bash docker/executors/build-all.sh
```

---

## Backend Seeding Commands

### Quick Seed (Default URL)
```bash
# From Codex_backend folder
cd "E:\Personal Projects\Codex\Codex_backend"
node seed-problems.js
```

### Seed to Custom URL
```bash
# Production Render URL
node seed-problems.js https://your-backend.onrender.com

# Local development
node seed-problems.js http://localhost:8080
```

### Using Batch File (Windows)
```bash
# Default URL
seed

# Custom URL
seed http://localhost:8080
```

---

## Backend Development Commands

### Build & Run Locally
```bash
# Compile
cd "E:\Personal Projects\Codex\Codex_backend"
mvn clean compile -DskipTests

# Package
mvn clean package -DskipTests

# Run locally
mvn spring-boot:run

# Or run the JAR
java -jar target/codex-platform-1.0.0.jar
```

### Docker Build
```bash
# Build Docker image
docker build -t codex-backend:latest .

# Run locally with Docker
docker run -p 8080:8080 --env-file .env codex-backend:latest
```

---

## Git Commands (Deploy to Render)

```bash
# Add all changes
git add .

# Commit
git commit -m "Your commit message"

# Push to trigger Render deployment
git push origin main
```

---

## API Testing Commands

### Test Executor Agent Directly
```bash
# Health check
curl http://3.109.238.141:8081/v1/healthz

# Execute Python code
curl -X POST http://3.109.238.141:8081/v1/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 57b4f75e92c1f14732b8d80bea36f12a1525af9a2b20444ce65c64e85b4be93b" \
  -d '{
    "submissionId":"test-001",
    "language":"PYTHON",
    "sourceCode":"print(2+3)",
    "fileExtension":".py",
    "dockerImage":"codex-python:latest",
    "compileCommand":null,
    "executeCommand":"python3 /workspace/solution.py",
    "compileTimeoutMs":10000,
    "runTimeoutMs":5000,
    "memoryLimitMb":256,
    "testCases":[{"id":"tc1","stdin":"","expectedStdout":"5"}]
  }'
```

---

## File Locations

| File | Path |
|------|------|
| SSH Key | `C:\keys\koder.pem` |
| Seed Script | `E:\Personal Projects\Codex\Codex_backend\seed-problems.js` |
| Seed Batch | `E:\Personal Projects\Codex\Codex_backend\seed.bat` |
| EC2 Cleanup Script | `/home/ubuntu/codex-cleanup.sh` |
| EC2 Test Script | `/home/ubuntu/test-all-languages.sh` |
| EC2 Compose File | `/home/ubuntu/codex-execution/docker-compose.ec2.yml` |
| EC2 Env File | `/home/ubuntu/codex-execution/.env` |

---

## Quick Reference

| Task | Command |
|------|---------|
| SSH to EC2 | `ssh -i C:\keys\koder.pem ubuntu@3.109.238.141` |
| Check executor health | `curl http://3.109.238.141:8081/v1/healthz` |
| Seed problems | `node seed-problems.js` |
| Test all languages | `/home/ubuntu/test-all-languages.sh` |
| Restart executor | `docker restart codex-executor-agent` |
| View executor logs | `docker logs codex-executor-agent -f` |
| Manual cleanup | `/home/ubuntu/codex-cleanup.sh` |
| Build backend | `mvn clean package -DskipTests` |
| Deploy to Render | `git push origin main` |
