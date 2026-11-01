# Infrastructure — What Runs Where

Current production setup for SprintCode (as of 2026-11-01). This is the source of truth; older docs (`deploy.md`, `DEPLOY-AWS-EC2.md`) describe the previous all-on-EC2 setup.

## Overview

```
Browser
   │  HTTPS
   ▼
Frontend — Next.js 16 on Vercel            https://sprintcode.vercel.app
   │  /api/proxy/*  (server-side, forwards httpOnly JWT cookie as Bearer)
   ▼
Backend — Spring Boot 3 on Render          https://codex-code-el37.onrender.com
   ├──► PostgreSQL — Supabase (ap-south-1, Mumbai), via pooler :6543
   ├──► Redis — Redis Cloud (queue, locks, rate limits, result cache, OTPs)
   ├──► Executor Agent — AWS EC2 (Mumbai), runs user code in Docker
   └──► Gemini API — AI problem authoring + CodeBot assistant
```

## Services

| Layer | Service | Where | Notes |
|-------|---------|-------|-------|
| Frontend | Next.js 16 (React 19, React Query, Zustand, Tailwind 4, Monaco) | **Vercel** — project `codex-front` | Auto-deploys on push to `main` of `Rocky4554/codex-front`. Functions currently run in `iad1` (US East). |
| Backend API | Spring Boot 3.2, Java 17 | **Render** Web Service — `codex-code-el37` | Built from `Dockerfile`, `SPRING_PROFILES_ACTIVE=prod`. Auto-deploys on push to `main` of `Rocky4554/Codex_code`. Region: **Oregon** (`gcp-us-west1`) — should be Singapore, see below. |
| Database | PostgreSQL | **Supabase** — `aws-1-ap-south-1.pooler.supabase.com:6543` | Transaction-mode pooler, so JDBC URL needs `prepareThreshold=0`. Schema managed by Hibernate `ddl-auto=update`. |
| Cache / queue | Redis 8 | **Redis Cloud** (`*.db.redis.io`) | Used via Redisson: submission queue, per-submission locks, rate limiters, submission result cache, password-reset OTPs, leaderboard cache. |
| Code execution | Executor Agent (`executor-agent/`) | **AWS EC2**, Mumbai (`:8081`) | Backend runs with `EXECUTION_MODE=remote` and POSTs submissions to the agent with a shared token. Agent drives Docker locally. |
| AI | Google Gemini (`gemini-3.1-flash-lite`) | Google API | `GEMINI_API_KEY` on the backend. |
| Email | Gmail SMTP via Nodemailer | Vercel route `app/api/internal/send-mail` | Backend calls the webhook (`MAIL_NODEMAILER_WEBHOOK_URL`) for password-reset OTPs; Spring Mail is the fallback. |
| Logs | Grafana Loki (optional) | — | Frontend `/api/log` ships client errors and slow API calls when `LOKI_*` is set. |

## Request Path

1. Browser calls same-origin `/api/proxy/<path>` on Vercel (avoids CORS/mixed content; JWT never touches JS).
2. The proxy route reads the `auth_token` httpOnly cookie and forwards to `${BACKEND_URL}/<path>` with `Authorization: Bearer …`.
3. `JwtAuthenticationFilter` validates the token; `tokenVersion` is checked against a 30s in-memory cache (`TokenVersionCache`) instead of a DB hit per request.
4. Controllers query Supabase / Redis and respond; SSE streams (submission status, CodeBot) pass through the proxy unbuffered.

## Environment Variables

**Vercel (`codex-front`)**

| Variable | Purpose |
|----------|---------|
| `BACKEND_URL` | Backend base URL incl. `/api`, e.g. `https://codex-code-el37.onrender.com/api` |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `MAIL_FROM` | Gmail SMTP for Nodemailer |
| `MAIL_WEBHOOK_SECRET` | Shared secret the backend sends to `/api/internal/send-mail` |
| `LOKI_URL` / `LOKI_USERNAME` / `LOKI_PASSWORD` | Optional log shipping |

**Render (`codex-code-el37`)**

| Variable | Purpose |
|----------|---------|
| `SPRING_PROFILES_ACTIVE` | `prod` |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USERNAME` / `DB_PASSWORD` | Supabase Postgres (pooler host, port `6543`) |
| `REDIS_URL` / `REDIS_PASSWORD` | Redis Cloud |
| `JWT_SECRET` / `JWT_EXPIRATION` | Auth tokens |
| `EXECUTION_MODE` | `remote` |
| `EXECUTOR_AGENT_BASE_URL` / `EXECUTOR_AGENT_TOKEN` | EC2 executor agent |
| `GEMINI_API_KEY` | AI features |
| `MAIL_NODEMAILER_WEBHOOK_URL` / `MAIL_NODEMAILER_WEBHOOK_SECRET` | `https://sprintcode.vercel.app/api/internal/send-mail` + matching secret |
| `APP_CORS_ALLOWED_ORIGINS` | `https://sprintcode.vercel.app` |

## Local Development

- Frontend: `npm run dev` in `codex-front` with `.env.local` containing `BACKEND_URL=http://localhost:8080/api`.
- Backend: `JAVA_HOME=$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home mvn spring-boot:run` (Lombok 1.18.30 doesn't build on JDK 21+ defaults like JDK 27).
- The `dev` profile defaults point at the **same cloud Supabase + Redis Cloud** as prod and the EC2 executor (override with `DB_URL`, `REDIS_*`, `EXECUTOR_AGENT_BASE_URL` to use local services).

## Known Issue — Region Mismatch

The Render backend is in Oregon while Supabase is in Mumbai, so every SQL query costs ~220 ms and each API call takes ~1.3s. Fix:

1. Create a new Render Web Service in **Singapore** from the same repo and copy all env vars (Render can't change region in place).
2. Update `BACKEND_URL` in Vercel, redeploy, delete the Oregon service.
3. Pin Vercel functions to Mumbai (`bom1`) — only after step 1.

Details and measurements: `problems.md` #31.

## Health Checks

```bash
curl https://codex-code-el37.onrender.com/actuator/health     # backend: db, redis
curl -s -o /dev/null -w "%{time_starttransfer}\n" https://sprintcode.vercel.app/api/proxy/languages
```
