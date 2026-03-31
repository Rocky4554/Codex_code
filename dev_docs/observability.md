# Codex Platform — Centralized Observability Stack

## Overview

A **centralized, reusable monitoring stack** (Prometheus + Loki + Grafana) that runs as an independent service on EC2. Any application — **Spring Boot, Node.js, Python, Go, or any other language** — can plug into it to get metrics and logs visualized in Grafana.

> [!TIP]
> **You deploy the monitoring stack once. Every new app just exposes endpoints and connects — no central config changes needed for logs.**

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    CENTRALIZED MONITORING STACK                          │
│                    (Deploy once, shared by all apps)                     │
│                    Docker Network: "monitoring"                          │
│                                                                         │
│   ┌─────────────┐      ┌──────────┐      ┌──────────────┐              │
│   │ Prometheus  │─────▶│ Grafana  │◀─────│    Loki      │              │
│   │ :9090       │      │ :3000    │      │   :3100      │              │
│   │ (metrics DB)│      │ (UI)     │      │  (logs DB)   │              │
│   └──────┬──────┘      └──────────┘      └──────┬───────┘              │
│          │ PULLS metrics                         │ RECEIVES logs        │
│          │ from /metrics endpoints               │ from Promtail        │
└──────────┼───────────────────────────────────────┼─────────────────────-┘
           │                                       │
  ─ ─ ─ ─ ┼ ─ ─ ─ ─ ─ ─ ─ ANY APP ─ ─ ─ ─ ─ ─ ─ ┼ ─ ─ ─ ─ ─ ─ ─ ─
           │                                       │
    ┌──────┼───────────────────────────────────────┼──────┐
    │      ▼               APP 1                   ▲      │
    │ ┌──────────┐    (Spring Boot)         ┌──────────┐  │
    │ │ codex-app│    exposes               │ promtail │  │
    │ │ :8080    │    /actuator/prometheus   │ (sidecar)│  │
    │ │          │──logs──▶ shared volume ──▶│          │  │
    │ └──────────┘                          └──────────┘  │
    └─────────────────────────────────────────────────────-┘
    ┌─────────────────────────────────────────────────────-┐
    │                      APP 2                           │
    │ ┌──────────┐    (Node.js)             ┌──────────┐  │
    │ │ payment  │    exposes               │ promtail │  │
    │ │ :3001    │    /metrics              │ (sidecar)│  │
    │ │          │──logs──▶ shared volume ──▶│          │  │
    │ └──────────┘                          └──────────┘  │
    └─────────────────────────────────────────────────────-┘
    ┌─────────────────────────────────────────────────────-┐
    │                      APP 3                           │
    │ ┌──────────┐    (Python Flask)        ┌──────────┐  │
    │ │ analytics│    exposes               │ promtail │  │
    │ │ :5000    │    /metrics              │ (sidecar)│  │
    │ │          │──logs──▶ shared volume ──▶│          │  │
    │ └──────────┘                          └──────────┘  │
    └─────────────────────────────────────────────────────-┘
```

### How Each Connection Works

| # | From | To | Method | What Happens |
|---|------|----|--------|-------------|
| 1 | **App** | **Log file** | File write | App writes logs to a shared Docker volume |
| 2 | **Promtail (sidecar)** | **Log file** | File read | Reads logs from the same shared volume |
| 3 | **Promtail** | **Loki** | HTTP push | Pushes logs to `http://loki:3100/loki/api/v1/push` |
| 4 | **Prometheus** | **App** | HTTP pull | Scrapes app's `/metrics` or `/actuator/prometheus` endpoint every 15s |
| 5 | **Grafana** | **Prometheus** | Internal query | Queries `http://prometheus:9090` for metrics |
| 6 | **Grafana** | **Loki** | Internal query | Queries `http://loki:3100` for logs |
| 7 | **You (browser)** | **Grafana** | HTTP | Access `http://<EC2-IP>:3000` |

---

## Part 1: Centralized Monitoring Stack (Deploy Once)

These files live in a dedicated folder on your EC2 (e.g., `~/monitoring/`).

### File: `docker-compose.monitoring.yml`

```yaml
# ~/monitoring/docker-compose.monitoring.yml
# Deploy ONCE. All apps connect to this.
# Usage: docker compose -f docker-compose.monitoring.yml up -d

version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: always
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      - '--storage.tsdb.retention.size=1GB'
      - '--web.enable-lifecycle'            # Allows config reload via API
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    networks:
      - monitoring

  loki:
    image: grafana/loki:2.9.4
    container_name: loki
    restart: always
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml:ro
      - loki-data:/loki
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"                         # Only Grafana exposed to internet
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-changeme}
      - GF_USERS_ALLOW_SIGN_UP=false
    depends_on:
      - prometheus
      - loki
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    networks:
      - monitoring

volumes:
  prometheus-data:
  loki-data:
  grafana-data:

networks:
  monitoring:
    driver: bridge
    name: monitoring                        # Fixed name so any app can join
```

### File: `prometheus.yml`

```yaml
# ~/monitoring/prometheus.yml
# Add one entry per app that exposes a metrics endpoint.
# This is the ONLY central config that needs a new line per app.

global:
  scrape_interval: 15s

scrape_configs:
  # ── Codex Platform (Spring Boot) ──
  - job_name: 'codex-platform'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['codex-app:8080']

  # ── Payment Service (Node.js) ── (example)
  # - job_name: 'payment-service'
  #   metrics_path: '/metrics'
  #   static_configs:
  #     - targets: ['payment-app:3001']

  # ── Analytics Service (Python) ── (example)
  # - job_name: 'analytics-service'
  #   metrics_path: '/metrics'
  #   static_configs:
  #     - targets: ['analytics-app:5000']
```

> [!NOTE]
> **Prometheus is pull-based**, so you must add one entry per app here. This is just 3 lines per app. After adding, reload config without restart:
> ```bash
> curl -X POST http://localhost:9090/-/reload
> ```

### File: `loki-config.yaml`

```yaml
# ~/monitoring/loki-config.yaml
# NO app-specific config here. Loki just receives whatever is pushed to it.

auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 1h
  max_chunk_age: 1h
  chunk_target_size: 1048576
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    cache_ttl: 24h
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

compactor:
  working_directory: /loki/boltdb-shipper-compactor
  shared_store: filesystem
  retention_enabled: true

limits_config:
  retention_period: 168h               # 7 days auto-deletion
  ingestion_rate_mb: 4
  ingestion_burst_size_mb: 6
```

### File: `grafana/provisioning/datasources/datasources.yaml`

```yaml
# ~/monitoring/grafana/provisioning/datasources/datasources.yaml
# Auto-configures Prometheus and Loki in Grafana on first boot.

apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true
```

### Monitoring Stack Folder Structure

```
~/monitoring/
├── docker-compose.monitoring.yml
├── prometheus.yml
├── loki-config.yaml
└── grafana/
    └── provisioning/
        └── datasources/
            └── datasources.yaml
```

---

## Part 2: How Each App Connects (Sidecar Pattern)

Each app bundles its own **Promtail sidecar** for logs and joins the `monitoring` network. No central Promtail config changes needed.

### What Each App Needs to Do

| Task | For Metrics (Prometheus) | For Logs (Loki) |
|------|-------------------------|-----------------|
| **App-side** | Expose a `/metrics` endpoint using a client library | Write logs to a file |
| **Docker-side** | Join the `monitoring` network | Add a Promtail sidecar + shared volume |
| **Central config** | Add 3 lines in `prometheus.yml` | ❌ Nothing — Promtail pushes directly |

---

### Example A: Spring Boot App (Codex)

#### `pom.xml` (already done ✅)

```xml
<!-- Actuator + Micrometer = exposes /actuator/prometheus -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
    <scope>runtime</scope>
</dependency>
```

#### `application-prod.properties` (already done ✅)

```properties
management.endpoints.web.exposure.include=health,prometheus
management.prometheus.metrics.export.enabled=true
```

#### `logback-spring.xml` (already done ✅)

Writes logs to `logs/codex-platform.log`.

#### `docker-compose.yml` (updated)

```yaml
services:
  codex-app:
    build: .
    container_name: codex-app
    restart: always
    ports:
      - "8080:8080"
    env_file:
      - .env.production
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DB_HOST: ${NEON_DB_HOST}
      DB_PORT: ${NEON_DB_PORT:-5432}
      DB_NAME: ${NEON_DB_NAME}
      DB_USERNAME: ${NEON_DB_USERNAME}
      DB_PASSWORD: ${NEON_DB_PASSWORD}
      REDIS_URL: ${REDIS_URL}
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      JWT_SECRET: ${JWT_SECRET}
      JWT_EXPIRATION: ${JWT_EXPIRATION:-86400000}
      EXECUTION_DOCKER_HOST: unix:///var/run/docker.sock
      EXECUTION_TEMP_DIR: /tmp/codex/submissions
      EXECUTION_WORKER_COUNT: 1
      APP_CORS_ALLOWED_ORIGINS: ${APP_CORS_ALLOWED_ORIGINS:-*}
      LOG_LEVEL: INFO
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp/codex:/tmp/codex
      - codex-logs:/app/logs                   # Shared log volume
    networks:
      - default
      - monitoring                              # Join monitoring network

  # ── Promtail Sidecar (ships with this app) ──
  codex-promtail:
    image: grafana/promtail:2.9.4
    container_name: codex-promtail
    restart: always
    volumes:
      - codex-logs:/var/log/app:ro              # Read app logs
      - ./promtail-config.yml:/etc/promtail/config.yml:ro
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - codex-app
    networks:
      - monitoring

volumes:
  codex-logs:

networks:
  monitoring:
    external: true
    name: monitoring
```

#### `promtail-config.yml` (ships with Codex app)

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: codex-logs
    static_configs:
      - targets: [localhost]
        labels:
          app: codex-platform
          language: java
          environment: production
          __path__: /var/log/app/*log
```

---

### Example B: Node.js App

#### Install metrics library

```bash
npm install prom-client
```

#### `metrics.js` — Expose `/metrics` endpoint

```javascript
const client = require('prom-client');

// Collect default metrics (CPU, memory, event loop, etc.)
client.collectDefaultMetrics({ prefix: 'payment_' });

// Custom metric example
const httpRequestCount = new client.Counter({
  name: 'payment_http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status'],
});

module.exports = { client, httpRequestCount };
```

#### `app.js` — Add metrics endpoint

```javascript
const express = require('express');
const { client, httpRequestCount } = require('./metrics');

const app = express();

// Your app routes
app.get('/api/payments', (req, res) => {
  httpRequestCount.inc({ method: 'GET', route: '/api/payments', status: 200 });
  res.json({ payments: [] });
});

// Metrics endpoint — Prometheus scrapes this
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});

app.listen(3001, () => console.log('Payment service on :3001'));
```

#### Logging — Use Winston to write to file

```bash
npm install winston
```

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: '/app/logs/payment-service.log' }),
  ],
});
```

#### `docker-compose.yml` (Payment Service)

```yaml
services:
  payment-app:
    build: .
    container_name: payment-app
    restart: always
    ports:
      - "3001:3001"
    volumes:
      - payment-logs:/app/logs
    networks:
      - default
      - monitoring

  payment-promtail:
    image: grafana/promtail:2.9.4
    container_name: payment-promtail
    restart: always
    volumes:
      - payment-logs:/var/log/app:ro
      - ./promtail-config.yml:/etc/promtail/config.yml:ro
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - payment-app
    networks:
      - monitoring

volumes:
  payment-logs:

networks:
  monitoring:
    external: true
    name: monitoring
```

#### `promtail-config.yml` (ships with Payment Service)

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: payment-logs
    static_configs:
      - targets: [localhost]
        labels:
          app: payment-service
          language: nodejs
          environment: production
          __path__: /var/log/app/*log
```

---

### Example C: Python (Flask/FastAPI) App

#### Install metrics library

```bash
pip install prometheus-flask-instrumentator
# or for FastAPI:
pip install prometheus-fastapi-instrumentator
```

#### `app.py` — Flask with metrics

```python
from flask import Flask
from prometheus_flask_instrumentator import FlaskInstrumentator
import logging

app = Flask(__name__)

# Metrics — auto-instruments all routes, exposes /metrics
FlaskInstrumentator().instrument(app).expose(app, endpoint="/metrics")

# Logging — write to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s : %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/analytics-service.log'),
    ]
)

@app.route('/api/analytics')
def analytics():
    app.logger.info('Analytics endpoint hit')
    return {'data': []}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### Docker Compose follows the same sidecar pattern as Node.js above.

---

## Part 3: Deployment on EC2

### Step 1: Start the Monitoring Stack (once)

```bash
# SSH into EC2
ssh -i ~/.ssh/your-key.pem ubuntu@<EC2-IP>

# Create monitoring directory
mkdir -p ~/monitoring/grafana/provisioning/datasources

# Copy monitoring files (from local machine or git)
# Put docker-compose.monitoring.yml, prometheus.yml,
# loki-config.yaml, datasources.yaml in ~/monitoring/

# Start the stack
cd ~/monitoring
docker compose -f docker-compose.monitoring.yml up -d

# Verify
docker ps
# Should show: grafana, prometheus, loki
```

### Step 2: Deploy Your App (with sidecar)

```bash
cd ~/Codex

# Start app + its promtail sidecar
docker compose -f docker-compose.yml --env-file .env.production up -d --build

# Verify
docker ps
# Should show: codex-app, codex-promtail (+ grafana, prometheus, loki)
```

### Step 3: Add app to Prometheus (one-time, 3 lines)

Edit `~/monitoring/prometheus.yml` and add the app's target. Then reload:

```bash
# Reload Prometheus config without restart
curl -X POST http://localhost:9090/-/reload
```

### Step 4: Verify in Grafana

1. Open `http://<EC2-PUBLIC-IP>:3000`
2. Login: `admin` / `<your password>`
3. **Logs:** Explore → Loki → `{app="codex-platform"}`
4. **Metrics:** Explore → Prometheus → `jvm_memory_used_bytes{job="codex-platform"}`

---

## Part 4: Adding a New App (Checklist)

When you build any new app in any language, follow these 4 steps:

- [ ] **1. Expose metrics endpoint** — Add the client library for your language and expose `/metrics`
- [ ] **2. Write logs to file** — Configure your logging framework to write to `/app/logs/`
- [ ] **3. Add Promtail sidecar** — Copy the sidecar pattern in your `docker-compose.yml`, change the `app` label
- [ ] **4. Add to `prometheus.yml`** — Add 3 lines with the app's `job_name` and `target`, then reload

| Language | Metrics Library | Metrics Endpoint | Logging Library |
|----------|----------------|-----------------|-----------------|
| **Java (Spring)** | Micrometer + Actuator | `/actuator/prometheus` | Logback (built-in) |
| **Node.js** | `prom-client` | `/metrics` | `winston` / `pino` |
| **Python** | `prometheus-flask-instrumentator` | `/metrics` | `logging` (built-in) |
| **Go** | `promhttp` | `/metrics` | `zap` / `logrus` |
| **Ruby** | `prometheus-client` | `/metrics` | `Logger` (built-in) |
| **Rust** | `prometheus` crate | `/metrics` | `tracing` / `log4rs` |

---

## Useful Grafana Queries

### Loki (Logs)

```logql
# All logs from a specific app
{app="codex-platform"}

# Errors only
{app="codex-platform"} |= "ERROR"

# All apps' errors
{environment="production"} |= "ERROR"

# Filter by language
{language="nodejs"} |= "Exception"

# All apps combined
{app=~".+"}
```

### Prometheus (Metrics)

```promql
# JVM memory (Spring Boot)
jvm_memory_used_bytes{job="codex-platform"}

# HTTP request rate (any app)
rate(http_server_requests_seconds_count[5m])

# Node.js custom metric
payment_http_requests_total{job="payment-service"}

# All apps CPU usage
process_cpu_usage

# DB connection pool (Spring/HikariCP)
hikaricp_connections_active{job="codex-platform"}
```

---

## EC2 Security Group Rules

| Port | Service | Expose to Internet? |
|------|---------|-------------------|
| 22 | SSH | Your IP only |
| 8080 | Codex API | Yes (or via Nginx) |
| **3000** | **Grafana** | **Your IP only** |
| 9090 | Prometheus | ❌ Never |
| 3100 | Loki | ❌ Never |

---

## Maintenance Commands

```bash
# View all monitoring logs
cd ~/monitoring
docker compose -f docker-compose.monitoring.yml logs -f

# Restart monitoring stack
docker compose -f docker-compose.monitoring.yml restart

# Check disk usage
docker system df -v | grep -E "prometheus|loki|grafana"

# Reset Grafana admin password
docker exec -it grafana grafana-cli admin reset-admin-password newpassword

# Reload Prometheus config (after editing prometheus.yml)
curl -X POST http://localhost:9090/-/reload

# Stop monitoring (keeps data)
docker compose -f docker-compose.monitoring.yml down

# Stop AND delete all data
docker compose -f docker-compose.monitoring.yml down -v
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Grafana shows "No data" for Loki | Check if Promtail sidecar is running: `docker logs codex-promtail` |
| Prometheus target shows DOWN | Ensure app and Prometheus are on the same `monitoring` network: `docker network inspect monitoring` |
| `host.docker.internal` doesn't work | Use Docker container name instead (e.g., `codex-app:8080`). `host.docker.internal` only works on Docker Desktop, not Linux. |
| Disk filling up | Reduce retention: Prometheus `--storage.tsdb.retention.time=7d`, Loki `retention_period: 72h` |
| High memory | Run `docker stats`. Consider upgrading EC2 to t3.medium (4GB). |
| New app logs not appearing | Verify: (1) app writes to `/app/logs/`, (2) volume is shared, (3) Promtail labels have `__path__` matching the log files |

---

## Memory Budget (t2.small — 2GB)

| Component | RAM |
|-----------|-----|
| OS + Docker | ~300 MB |
| Monitoring (Prometheus + Loki + Grafana) | ~300-400 MB |
| codex-app (JVM `-Xmx384m`) | ~400 MB |
| Promtail sidecar | ~30 MB |
| 1 code-exec container | ~256 MB |
| **Total** | **~1.3 - 1.4 GB** |
| **Headroom** | **~600 MB** |

> [!WARNING]
> If you add more apps on the same EC2, consider upgrading to **t3.medium (4GB)** or **t3.large (8GB)**.

---

## File Summary

### Monitoring Stack (deploy once in `~/monitoring/`)

| File | Purpose |
|------|---------|
| `docker-compose.monitoring.yml` | Prometheus + Loki + Grafana containers |
| `prometheus.yml` | Which apps to scrape (add 3 lines per new app) |
| `loki-config.yaml` | Loki storage + 7-day retention (no app-specific config) |
| `grafana/provisioning/datasources/datasources.yaml` | Auto-configure data sources |

### Per-App Files (ship with each app)

| File | Purpose |
|------|---------|
| `docker-compose.yml` | App container + Promtail sidecar |
| `promtail-config.yml` | Promtail config with app-specific label |
| Metrics library | Expose `/metrics` or `/actuator/prometheus` |
| Log config | Write logs to `/app/logs/` directory |
