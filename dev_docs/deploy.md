# Codex Platform — EC2 Deployment Guide

## Architecture Overview

```
                    Internet
                       |
                   EC2 Instance (t2.small / t3.small recommended)
                   +-----------------------------------------+
                   |  Docker Engine                          |
                   |                                         |
                   |  +-------------+   +----------------+   |
                   |  | codex-app   |   | codex-redis    |   |
                   |  | (Spring     |-->| (Redis 7       |   |
                   |  |  Boot +     |   |  Alpine)       |   |
                   |  |  Workers)   |   |  ~50MB RAM     |   |
                   |  | ~384MB RAM  |   +----------------+   |
                   |  +------+------+                        |
                   |         |                               |
                   |         | Docker Socket                 |
                   |         v                               |
                   |  +-------------+                        |
                   |  | gcc:latest  |  (temporary per-       |
                   |  | python:3.11 |   submission            |
                   |  | node:20     |   containers)          |
                   |  +-------------+                        |
                   +-----------------------------------------+
                              |
                         Neon PostgreSQL
                         (Cloud, ap-southeast-1)
```

**Key points:**
- Single JAR — the app serves the API AND runs worker threads (no separate worker process)
- DB is Neon cloud PostgreSQL (no local Postgres container needed)
- Redis runs as a lightweight container for queue + locking
- Code execution spins up temporary Docker containers via the mounted Docker socket
- Worker concurrency = 1 (safe for 1-2 GB RAM instances)

---

## Prerequisites

| What | Why |
|------|-----|
| AWS EC2 instance | t2.small (2GB) recommended; t2.micro (1GB) is tight |
| Docker + Docker Compose installed | Runs the app + Redis + code-exec containers |
| Neon PostgreSQL account | Free tier: 0.5GB storage, connection pooling |
| Security Group | Inbound: 22 (SSH), 80/443 (HTTP/S), 8080 (app) |
| Domain (optional) | For HTTPS via Nginx reverse proxy or ALB |

---

## Step-by-step Deployment

### 1. Launch EC2 Instance

```bash
# Recommended: Amazon Linux 2023 or Ubuntu 22.04
# Instance type: t2.small (2GB RAM) or t3.small
# Storage: 20GB gp3 (need space for Docker images)
# Security group: open 22, 8080 (or 80/443 if using reverse proxy)
```

### 2. Install Docker on EC2

```bash
# Amazon Linux 2023
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose plugin
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Log out and back in for group change to take effect
exit
```

For Ubuntu:
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker ubuntu
exit
```

### 3. Pre-pull Compiler Images

These are large (~1GB each). Pull them before starting the app to avoid first-submission delays.

```bash
docker pull gcc:latest
docker pull python:3.11-slim
docker pull eclipse-temurin:17-jdk
docker pull node:20-slim
```

### 4. Clone and Configure

```bash
git clone https://github.com/YOUR_USERNAME/Codex.git
cd Codex

# Create production environment file
cp .env.production .env.production.local
nano .env.production.local
```

Fill in your real values:
```env
NEON_DB_HOST=ep-xxxxx-pooler.ap-southeast-1.aws.neon.tech
NEON_DB_PORT=5432
NEON_DB_NAME=codex-db
NEON_DB_USERNAME=neondb_owner
NEON_DB_PASSWORD=your_actual_password

JWT_SECRET=your-strong-random-secret-at-least-32-bytes-long

APP_CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

Generate a strong JWT secret:
```bash
openssl rand -base64 48
```

### 5. Build and Start

```bash
# Build and start in detached mode
docker compose -f docker-compose.prod.yml --env-file .env.production.local up -d --build

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f codex-app
```

### 6. Verify

```bash
# Health check
curl http://localhost:8080/api/problems

# Check containers
docker ps
```

You should see:
- `codex-app` — running on port 8080
- `codex-redis` — running on port 6379

---

## Memory Budget (t2.small — 2GB RAM)

| Component | RAM |
|-----------|-----|
| OS + Docker Engine | ~300MB |
| codex-app (JVM -Xmx384m) | ~400MB |
| codex-redis (50MB limit) | ~50MB |
| 1 code-exec container (256MB limit) | ~256MB |
| **Headroom** | **~500MB** |

For t2.micro (1GB), reduce JVM to `-Xmx256m` and set `execution.default-memory-limit-mb=128` in the compose environment.

---

## Common Operations

### Restart the app
```bash
docker compose -f docker-compose.prod.yml restart codex-app
```

### Rebuild after code changes
```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build codex-app
```

### View live logs
```bash
docker compose -f docker-compose.prod.yml logs -f codex-app --tail=100
```

### Stop everything
```bash
docker compose -f docker-compose.prod.yml down
```

### Clean up old images
```bash
docker image prune -f
```

---

## Optional: Nginx Reverse Proxy (HTTPS)

If you want to serve on port 80/443 with SSL:

```bash
sudo apt install -y nginx certbot python3-certbot-nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/codex
```

```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/codex /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Connection refused` to Neon DB | Check `NEON_DB_HOST`, `NEON_DB_PASSWORD` in `.env.production.local`. Verify Neon dashboard shows DB is active. |
| Code execution hangs | Run `docker ps` — check if compiler containers are stuck. Restart Docker: `sudo systemctl restart docker` |
| Out of memory | Upgrade to t2.small (2GB). Or reduce `-Xmx` and `execution.default-memory-limit-mb`. |
| Redis connection errors | `docker compose -f docker-compose.prod.yml restart redis` |
| First submission slow | Pre-pull compiler images (step 3). First container creation is always slower. |
| `permission denied` on Docker socket | Run `sudo chmod 666 /var/run/docker.sock` or add user to docker group. |

---

## Security Checklist

- [ ] `.env.production.local` is in `.gitignore` (never commit secrets)
- [ ] JWT secret is strong (32+ bytes, randomly generated)
- [ ] Neon DB password is not hardcoded anywhere in code
- [ ] EC2 security group restricts port 8080 (or use Nginx on 80/443 only)
- [ ] CORS origins are set to your actual frontend domain
- [ ] Docker socket is only accessible by the app container
