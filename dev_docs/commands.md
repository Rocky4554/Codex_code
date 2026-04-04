# Codex Platform Commands

This document contains a list of useful commands for running, testing, and managing the Codex Platform and its infrastructure.

---

## 🚀 Spring Boot App

**Run the Spring Boot application locally**
```bash
mvn spring-boot:run
```

**Build the Spring Boot application (skipping tests)**
```bash
mvn clean package -DskipTests
```

**Run unit tests**
```bash
mvn test
```

---

## 🐳 Docker Containers (Main Services)

Your main services (Redis, Database) are defined in `docker-compose.yml`.

**Start all services in the background**
```bash
docker compose up -d
```

**Stop all services**
```bash
docker compose down
```

**View logs for all services**
```bash
docker compose logs -f
```

**View logs for a specific service (e.g., redis)**
```bash
docker compose logs -f redis
```

---

## 📊 Monitoring (Prometheus & Grafana)

Your monitoring stack is defined separately in `docker-compose.monitoring.yml`.

**Start the monitoring stack**
```bash
docker compose -f docker-compose.monitoring.yml up -d
```

**Stop the monitoring stack**
```bash
docker compose -f docker-compose.monitoring.yml down
```

**View monitoring logs**
```bash
docker compose -f docker-compose.monitoring.yml logs -f
```

---

## 💻 Docker CLI Commands

Useful general-purpose Docker commands for managing servers.

**List all running containers**
```bash
docker ps
```

**List all containers (running and stopped)**
```bash
docker ps -a
```

**Restart a specific container**
```bash
docker restart <container_name_or_id>
```

**Stop a specific container**
```bash
docker stop <container_name_or_id>
```

**Remove a specific container**
```bash
docker rm <container_name_or_id>
```

**View logs of a specific container**
```bash
docker logs -f <container_name_or_id>
```

**Execute an interactive shell inside a running container**
```bash
docker exec -it <container_name_or_id> /bin/bash
# or sh if bash is not available:
# docker exec -it <container_name_or_id> sh
```

---

## 🚀 EC2 Production (CI/CD)

The app runs on EC2 at `~/Codex_code/`. The CI/CD pipeline auto-deploys on every push to `main`.

**SSH into EC2**
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

**Check running containers**
```bash
docker ps
```

**View app logs**
```bash
docker logs codex-app --tail 100
docker logs -f codex-app   # follow live
```

**Restart app manually (force fresh pull from GHCR)**
```bash
cd ~/Codex_code
docker compose --env-file .env.production up -d --pull always
```

**Stop the app**
```bash
cd ~/Codex_code && docker compose down
```

**Trigger a rebuild without code changes**
```bash
git commit --allow-empty -m "trigger rebuild"
git push origin main
```

**Check disk usage (images pile up over time)**
```bash
docker system df
docker image prune -f   # remove dangling images only
```

---

## 🧹 Cleanup Operations

**Remove all stopped containers, unused networks, and dangling images (Safe)**
```bash
docker system prune
```

**Remove EVERYTHING (Stopped containers, ALL unused networks, ALL unused images, build cache)**
*⚠️ Warning: Use with caution!*
```bash
docker system prune -a --volumes
```
