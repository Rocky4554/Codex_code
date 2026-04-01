# CI/CD Pipeline — GitHub Actions + GHCR + AWS EC2

Automated pipeline that builds a Docker image on every push to `main`, publishes it to GitHub Container Registry (GHCR), and deploys it to your EC2 instance via SSH.

---

## How It Works (Overview)

```
Push to main
    │
    ▼
GitHub Actions triggers (.github/workflows/deploy.yml)
    │
    ├─► Job 1: build-and-push
    │     • Checks out code
    │     • Logs into GHCR using GITHUB_TOKEN
    │     • Builds Docker image (multi-stage: Maven build → JRE runtime)
    │     • Tags image as `latest` + short commit SHA
    │     • Pushes to ghcr.io/rocky4554/codex_code
    │
    └─► Job 2: deploy (runs after build-and-push succeeds)
          • SSHs into EC2
          • Logs into GHCR on EC2
          • Pulls the latest image
          • Restarts containers via docker compose
          • Prunes old images
```

---

## Files Involved

| File | Location | Purpose |
|------|----------|---------|
| `deploy.yml` | `.github/workflows/deploy.yml` | GitHub Actions workflow definition |
| `docker-compose.prod.yml` | Project root | Production compose file (uses GHCR image instead of local build) |
| `docker-compose.yml` | EC2: `~/codex/docker-compose.yml` | Copy of `docker-compose.prod.yml` placed on EC2 |
| `.env.production` | EC2: `~/codex/.env.production` | Environment variables for production |
| `promtail-config.yml` | EC2: `~/codex/promtail-config.yml` | Promtail log shipping config |

---

## Step-by-Step Setup Guide

### Step 1: Create a GitHub Personal Access Token (PAT)

The EC2 instance needs a token to pull images from GHCR.

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a descriptive name: `codex-ec2-ghcr-pull`
4. Set expiration (recommend 90 days — set a reminder to rotate)
5. Select scope: **`read:packages`** (only this one is needed)
6. Click **Generate token**
7. **Copy the token immediately** — you won't see it again

### Step 2: Add GitHub Repository Secrets

Go to your repo: **Settings → Secrets and variables → Actions → New repository secret**

Add these 5 secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `EC2_HOST` | EC2 public IP or Elastic IP | `54.123.45.67` |
| `EC2_USERNAME` | SSH username on EC2 | `ubuntu` (Ubuntu AMI) or `ec2-user` (Amazon Linux) |
| `EC2_SSH_KEY` | Full contents of your `.pem` private key file | Paste the entire file including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----` |
| `GHCR_PAT` | The PAT you created in Step 1 | `ghp_xxxxxxxxxxxxxxxxxxxx` |
| `GHCR_USERNAME` | Your GitHub username | `Rocky4554` |

**How to get your `.pem` key contents:**
```bash
# On your local machine (Windows)
cat C:\path\to\your-key.pem

# Copy the ENTIRE output including BEGIN/END lines
```

### Step 3: Enable Workflow Permissions

1. Go to repo **Settings → Actions → General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests** (optional)
5. Click **Save**

This allows the workflow to push images to GHCR using `GITHUB_TOKEN`.

### Step 4: Set Up EC2 Instance

SSH into your EC2:

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

#### 4a. Install Docker (if not already installed)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose-plugin

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# IMPORTANT: Log out and log back in for the group change to take effect
exit
# SSH back in
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Verify Docker works without sudo
docker ps
```

#### 4b. Create project directory

```bash
mkdir -p ~/codex
```

#### 4c. Copy files to EC2

From your **local machine**, run:

```bash
# Copy the production compose file (rename it to docker-compose.yml on EC2)
scp -i your-key.pem docker-compose.prod.yml ubuntu@YOUR_EC2_IP:~/codex/docker-compose.yml

# Copy promtail config
scp -i your-key.pem promtail-config.yml ubuntu@YOUR_EC2_IP:~/codex/promtail-config.yml

# Copy environment file
scp -i your-key.pem .env.production ubuntu@YOUR_EC2_IP:~/codex/.env.production
```

**On Windows (PowerShell), use full paths:**
```powershell
scp -i C:\path\to\your-key.pem "E:\Personal Projects\Codex_backend\docker-compose.prod.yml" ubuntu@YOUR_EC2_IP:~/codex/docker-compose.yml
scp -i C:\path\to\your-key.pem "E:\Personal Projects\Codex_backend\promtail-config.yml" ubuntu@YOUR_EC2_IP:~/codex/promtail-config.yml
scp -i C:\path\to\your-key.pem "E:\Personal Projects\Codex_backend\.env.production" ubuntu@YOUR_EC2_IP:~/codex/.env.production
```

#### 4d. Create Docker network for monitoring

```bash
docker network create monitoring
```

#### 4e. Verify .env.production exists and has correct values

```bash
cat ~/codex/.env.production
```

It should contain:
```env
NEON_DB_HOST=your-neon-host.neon.tech
NEON_DB_PORT=5432
NEON_DB_NAME=codex
NEON_DB_USERNAME=your-user
NEON_DB_PASSWORD=your-password
REDIS_URL=redis://your-redis-host:6379
REDIS_PASSWORD=your-redis-password
JWT_SECRET=your-256-bit-secret
APP_CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

#### 4f. Test manual pull (optional, to verify GHCR access)

```bash
# Login to GHCR on EC2
echo "YOUR_GHCR_PAT" | docker login ghcr.io -u Rocky4554 --password-stdin

# Try pulling (will fail if image hasn't been pushed yet — that's OK)
docker pull ghcr.io/rocky4554/codex_code:latest
```

### Step 5: Configure EC2 Security Group

Make sure your EC2 security group allows:

| Type | Port | Source | Purpose |
|------|------|--------|---------|
| SSH | 22 | Your IP / GitHub Actions IPs | SSH access for deployment |
| Custom TCP | 8080 | 0.0.0.0/0 | App traffic |

**Note:** For tighter security, you can restrict SSH to GitHub Actions IP ranges, but `0.0.0.0/0` on port 22 works for simplicity (your key-based auth protects access).

### Step 6: Push Code to Trigger the Pipeline

```bash
git add .
git commit -m "add CI/CD pipeline"
git push origin main
```

Then go to your repo's **Actions** tab to watch the pipeline run.

---

## Monitoring & Troubleshooting

### Check pipeline status
- Go to: `https://github.com/Rocky4554/Codex_code/actions`
- Click on the latest workflow run to see logs for each step

### Common failures and fixes

#### Build fails: "unauthorized" when pushing to GHCR
- Go to repo **Settings → Actions → General → Workflow permissions**
- Make sure **Read and write permissions** is selected

#### Deploy fails: "ssh: connect to host ... port 22: Connection timed out"
- Check EC2 Security Group allows inbound SSH (port 22)
- Check `EC2_HOST` secret has the correct IP
- If using Elastic IP, make sure it's still associated with the instance

#### Deploy fails: "permission denied (publickey)"
- Make sure `EC2_SSH_KEY` contains the entire `.pem` file contents
- Make sure `EC2_USERNAME` is correct (`ubuntu` for Ubuntu, `ec2-user` for Amazon Linux)

#### Deploy fails: "docker: command not found" on EC2
- Docker isn't installed — follow Step 4a

#### App starts but can't connect to database/Redis
- Check `~/codex/.env.production` has correct values
- Check EC2 security group allows outbound traffic to Neon/Redis Cloud

### SSH into EC2 to debug manually

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Check running containers
docker ps

# Check app logs
docker logs codex-app --tail 100

# Check if image was pulled
docker images | grep codex

# Restart manually
cd ~/codex
docker compose --env-file .env.production up -d --pull always

# Check compose logs
docker compose logs -f
```

---

## Useful Commands

### On EC2

```bash
# Stop the app
cd ~/codex && docker compose down

# Restart with fresh pull
cd ~/codex && docker compose --env-file .env.production up -d --pull always

# View real-time logs
docker logs -f codex-app

# Check disk space (images can pile up)
docker system df
docker image prune -a  # Remove ALL unused images
```

### On GitHub

```bash
# Manually trigger a rebuild (re-push same commit)
git commit --allow-empty -m "trigger rebuild"
git push origin main
```

---

## Rotating the GHCR PAT

The PAT you created has an expiration date. When it expires:

1. Create a new PAT (repeat Step 1)
2. Update the `GHCR_PAT` secret in GitHub repo settings (Step 2)
3. Update the token on EC2 if you logged in manually:
   ```bash
   echo "NEW_PAT" | docker login ghcr.io -u Rocky4554 --password-stdin
   ```

---

## Architecture Diagram

```
┌──────────────┐     push to main     ┌──────────────────┐
│  Developer   │ ──────────────────►  │  GitHub Actions   │
│  (local)     │                      │                   │
└──────────────┘                      │  1. Build image   │
                                      │  2. Push to GHCR  │
                                      │  3. SSH into EC2  │
                                      └────────┬─────────┘
                                               │
                                               │ SSH + docker pull
                                               ▼
┌──────────────┐                      ┌──────────────────┐
│  GHCR        │ ◄─── docker pull ──  │  AWS EC2         │
│  (Registry)  │                      │                   │
│  ghcr.io/    │                      │  docker compose   │
│  rocky4554/  │                      │  up -d            │
│  codex_code  │                      │                   │
└──────────────┘                      └──────────────────┘
```

---

## Workflow File Reference

The workflow lives at `.github/workflows/deploy.yml`. Key sections:

- **Trigger:** `on: push: branches: [main]` — only runs on main branch pushes
- **Job 1 (build-and-push):** Uses `docker/build-push-action` with GHCR login
- **Job 2 (deploy):** Uses `appleboy/ssh-action` to SSH and run deploy commands
- **Image tags:** Every build gets `latest` + the short commit SHA (e.g., `a1b2c3d`) for rollback capability

### Rolling back to a previous version

```bash
# On EC2, pull a specific commit SHA tag instead of latest
docker pull ghcr.io/rocky4554/codex_code:a1b2c3d

# Update docker-compose.yml to use that tag, or run directly:
docker stop codex-app
docker rm codex-app
docker run -d --name codex-app \
  --env-file ~/codex/.env.production \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/codex:/tmp/codex \
  ghcr.io/rocky4554/codex_code:a1b2c3d
```
