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
          • Creates monitoring network (if missing)
          • Restarts containers via docker compose (prod compose file)
          • Prunes old images
```

---

## Files Involved

| File | Location | Purpose |
|------|----------|---------|
| `deploy.yml` | `.github/workflows/deploy.yml` | GitHub Actions workflow definition |
| `docker-compose.prod.yml` | Project root + EC2: `~/Codex_code/` | Production compose file (pulls pre-built image from GHCR) |
| `docker-compose.yml` | Project root | Dev compose file (builds from source locally) — **not used in production** |
| `.env.production` | EC2: `~/Codex_code/.env.production` only | Environment variables for production — **not tracked in git** |
| `promtail-config.yml` | Project root + EC2: `~/Codex_code/` | Promtail log shipping config |

> **Important:** `.env.production` contains real secrets and is excluded from git via `.gitignore`. You must manually copy it to EC2 whenever you change it.

---

## EC2 Directory Structure

The deploy script expects this layout at `~/Codex_code/` on EC2:

```
~/Codex_code/
├── docker-compose.prod.yml    # Production compose (pulls from GHCR)
├── .env.production            # Secrets (DB, Redis, JWT) — manual deploy only
└── promtail-config.yml        # Promtail sidecar config
```

These files are **not** automatically synced by the pipeline. Copy them manually:

```bash
scp -i "C:\keys\koder.pem" docker-compose.prod.yml .env.production promtail-config.yml ubuntu@3.109.238.141:~/Codex_code/
```

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
| `EC2_HOST` | EC2 public IP or Elastic IP | `3.109.238.141` |
| `EC2_USERNAME` | SSH username on EC2 | `ubuntu` |
| `EC2_SSH_KEY` | Full contents of your `.pem` private key file | Paste the entire file including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----` |
| `GHCR_PAT` | The PAT you created in Step 1 | `ghp_xxxxxxxxxxxxxxxxxxxx` |
| `GHCR_USERNAME` | Your GitHub username | `Rocky4554` |

**How to get your `.pem` key contents:**
```bash
cat C:\keys\koder.pem
# Copy the ENTIRE output including BEGIN/END lines
```

### Step 3: Enable Workflow Permissions

1. Go to repo **Settings → Actions → General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Click **Save**

This allows the workflow to push images to GHCR using `GITHUB_TOKEN`.

### Step 4: Set Up EC2 Instance

SSH into your EC2:

```bash
ssh -i "C:\keys\koder.pem" ubuntu@3.109.238.141
```

#### 4a. Install Docker and Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Compose plugin
sudo apt install -y docker.io docker-compose-v2

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# IMPORTANT: Log out and log back in for the group change to take effect
exit
# SSH back in
ssh -i "C:\keys\koder.pem" ubuntu@3.109.238.141

# Verify both work without sudo
docker ps
docker compose version
```

#### 4b. Create project directory and copy files

```bash
# On EC2
mkdir -p ~/Codex_code
```

Then from your local machine:
```bash
scp -i "C:\keys\koder.pem" docker-compose.prod.yml .env.production promtail-config.yml ubuntu@3.109.238.141:~/Codex_code/
```

#### 4c. Create Docker network for monitoring

The compose file declares a `monitoring` network as external. It must exist before containers start:

```bash
docker network create monitoring
```

#### 4d. Test manual pull (optional)

```bash
# Login to GHCR on EC2
echo "YOUR_GHCR_PAT" | docker login ghcr.io -u Rocky4554 --password-stdin

# Try pulling
docker pull ghcr.io/rocky4554/codex_code:latest
```

### Step 5: Configure EC2 Security Group

Make sure your EC2 security group allows:

| Type | Port | Source | Purpose |
|------|------|--------|---------|
| SSH | 22 | Your IP / 0.0.0.0/0 | SSH access for deployment |
| Custom TCP | 8080 | 0.0.0.0/0 | App traffic |

### Step 6: Push Code to Trigger the Pipeline

```bash
git add .
git commit -m "your changes"
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
- Make sure `EC2_USERNAME` is correct (`ubuntu` for Ubuntu AMI)

#### Deploy fails: "docker compose: command not found" on EC2
- Install the compose plugin: `sudo apt install -y docker-compose-v2`

#### Deploy succeeds but compose fails: "invalid interpolation format"
- Check `.env.production` and compose files for invalid `${VAR:}` syntax
- Valid forms: `${VAR}`, `${VAR:-default}`, `${VAR-default}`
- Invalid: `${VAR:}` (colon with no default)

#### Deploy succeeds but compose fails: "network monitoring not found"
- Create it: `docker network create monitoring`
- The deploy workflow now does this automatically, but check if SSH succeeded

#### App starts but crashes with connection errors
- Check `~/Codex_code/.env.production` has correct DB/Redis values
- Test DNS resolution: `nslookup your-redis-host.com`
- Check EC2 security group allows outbound traffic to Neon/Redis Cloud

### SSH into EC2 to debug manually

```bash
ssh -i "C:\keys\koder.pem" ubuntu@3.109.238.141

# Check running containers
docker ps

# Check app logs
docker logs codex-app --tail 100

# Check if image was pulled
docker images | grep codex

# Health check
curl http://localhost:8080/actuator/health

# Restart manually
cd ~/Codex_code
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --pull always

# Check compose logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## Useful Commands

### On EC2

```bash
# Stop the app
cd ~/Codex_code && docker compose -f docker-compose.prod.yml down

# Restart with fresh pull
cd ~/Codex_code && docker compose -f docker-compose.prod.yml --env-file .env.production up -d --pull always

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

## Updating .env.production

Since `.env.production` is not in git, changes must be manually copied to EC2:

```bash
# From your local machine
scp -i "C:\keys\koder.pem" .env.production ubuntu@3.109.238.141:~/Codex_code/

# Then restart the app on EC2
ssh -i "C:\keys\koder.pem" ubuntu@3.109.238.141 \
  "cd ~/Codex_code && docker compose -f docker-compose.prod.yml --env-file .env.production up -d --force-recreate"
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
                                               │ SSH + docker compose
                                               ▼
┌──────────────┐                      ┌──────────────────┐
│  GHCR        │ ◄── --pull always ── │  AWS EC2         │
│  (Registry)  │                      │  ~/Codex_code/   │
│  ghcr.io/    │                      │                   │
│  rocky4554/  │                      │  docker-compose   │
│  codex_code  │                      │    .prod.yml      │
└──────────────┘                      │  .env.production  │
                                      └──────────────────┘
```

---

## Workflow File Reference

The workflow lives at `.github/workflows/deploy.yml`. Key sections:

- **Trigger:** `on: push: branches: [main]` — only runs on main branch pushes
- **Job 1 (build-and-push):** Uses `docker/build-push-action` with GHCR login via `GITHUB_TOKEN`
- **Job 2 (deploy):** Uses `appleboy/ssh-action` to SSH and run deploy commands
- **Image tags:** Every build gets `latest` + the short commit SHA (e.g., `d22ee09`) for rollback capability

### What the deploy script does on EC2

```bash
# 1. Login to GHCR
echo "$GHCR_PAT" | docker login ghcr.io -u $GHCR_USERNAME --password-stdin

# 2. Create monitoring network if missing
docker network create monitoring 2>/dev/null || true

# 3. Pull latest image and restart containers
cd ~/Codex_code
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --pull always

# 4. Clean up old images
docker image prune -f
```

### Rolling back to a previous version

```bash
# On EC2, pull a specific commit SHA tag instead of latest
docker pull ghcr.io/rocky4554/codex_code:d22ee09

# Then run it
docker stop codex-app && docker rm codex-app
docker run -d --name codex-app \
  --env-file ~/Codex_code/.env.production \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/codex:/tmp/codex \
  --network monitoring \
  ghcr.io/rocky4554/codex_code:d22ee09
```
