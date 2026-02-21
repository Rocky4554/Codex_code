# Deploy Codex Platform on AWS EC2

You have Docker (and Docker Compose) on EC2. Follow these steps to run the app in production.

---

## 1. Prerequisites on EC2

- **Docker** and **Docker Compose** (v2+) installed
- **Port 8080** open in the EC2 security group (Inbound: TCP 8080 from your IP or `0.0.0.0/0` for public access)
- A **Neon** (or other) PostgreSQL database
- **Redis Cloud** (or other hosted Redis) — no Redis container on EC2
- **Optional:** Domain and SSL (e.g. Nginx + Let’s Encrypt) — can add later

---

## 2. Get the code on EC2

```bash
# Clone (if using Git)
git clone <your-repo-url> codex
cd codex

# Or upload the project (e.g. rsync/scp) and cd into the project root
```

---

## 3. Create `.env.production` on EC2

Create a file named `.env.production` in the project root (same folder as `docker-compose.prod.yml`). **Do not commit this file.**

### Neon DB + Redis Cloud

```env
# Spring
SPRING_PROFILES_ACTIVE=prod

# Neon PostgreSQL (from Neon dashboard: connection string / connection details)
NEON_DB_HOST=your-neon-host.neon.tech
NEON_DB_PORT=5432
NEON_DB_NAME=your-db-name
NEON_DB_USERNAME=your-username
NEON_DB_PASSWORD=your-password

# Redis Cloud (from Redis Cloud dashboard: host, port, default user password)
REDIS_PROTOCOL=rediss
REDIS_HOST=your-redis-cloud-host.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=your-redis-cloud-password

# JWT (generate a long random secret, e.g. 32+ chars)
JWT_SECRET=your-256-bit-secret-key-change-this-in-production-must-be-at-least-256-bits-long
JWT_EXPIRATION=86400000

# CORS (your frontend URL; use * only for quick tests)
APP_CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

# Logging
LOG_LEVEL=INFO
```

- **Neon:** [Neon Console](https://console.neon.tech) → your project → Connection details.
- **Redis Cloud:** [Redis Cloud](https://app.redislabs.com) → your database → **Connect** → copy **Public endpoint** (host:port) and **Default user password**. Use `REDIS_PROTOCOL=rediss` (with TLS) for Redis Cloud; use `redis` if your plan has no TLS. Port is often non-standard (e.g. 12345).
- **JWT_SECRET:** e.g. `openssl rand -base64 32`.

---

## 4. Build and run on EC2

From the project root on EC2:

```bash
# Build and start (Codex app only; DB and Redis are cloud-hosted)
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Check logs
docker compose -f docker-compose.prod.yml logs -f codex-app
```

- First run may take a few minutes (Maven build in Docker).
- App will be available at: `http://<EC2-PUBLIC-IP>:8080`.

---

## 5. Verify

- **Health/API:** `http://<EC2-PUBLIC-IP>:8080` (e.g. any public endpoint you have).
- **Logs:** `docker compose -f docker-compose.prod.yml logs -f codex-app`
- **Containers:** `docker compose -f docker-compose.prod.yml ps` — `codex-app` should be Up.

---

## 6. Useful commands

| Task | Command |
|------|--------|
| Stop | `docker compose -f docker-compose.prod.yml --env-file .env.production down` |
| Restart app only | `docker compose -f docker-compose.prod.yml --env-file .env.production restart codex-app` |
| Rebuild after code change | `docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build` |
| View logs | `docker compose -f docker-compose.prod.yml logs -f` |

---

## 7. Optional: Nginx + HTTPS in front of the app

1. Install Nginx on EC2: `sudo apt install nginx` (Ubuntu/Debian).
2. Point a domain (A record) to the EC2 public IP.
3. Configure Nginx as reverse proxy to `http://127.0.0.1:8080` and add SSL with Certbot: `sudo apt install certbot python3-certbot-nginx && sudo certbot --nginx -d yourdomain.com`.

---

## 8. Troubleshooting

- **App can’t connect to DB:** Check Neon IP allowlist (Neon often allows all; if not, add EC2 outbound IP). Confirm `NEON_DB_*` in `.env.production`.
- **App can’t connect to Redis:** Use Redis Cloud **Public endpoint** (host only, no `rediss://`) as `REDIS_HOST`, and the port from the endpoint. Use `REDIS_PROTOCOL=rediss` for TLS; set `REDIS_PASSWORD` to the default user password from Redis Cloud.
- **Code execution fails:** App needs access to Docker. The compose file mounts `/var/run/docker.sock`; ensure Docker is running on the host and the socket is available.
- **Port 8080 not reachable:** Open TCP 8080 in the EC2 security group (Inbound rules).

Once `.env.production` is set and the security group allows 8080, `docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build` is enough to run the platform on EC2.
