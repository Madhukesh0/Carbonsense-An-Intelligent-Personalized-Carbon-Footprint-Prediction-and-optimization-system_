# Deploying CarbonSense for $0 (free tier, no Docker)

The production setup is **one Python process**: FastAPI serves both the REST
API (`/api/v1/...`) and the built React SPA. MongoDB stays on Atlas's free
M0 tier, and the assistant uses the Gemini free tier with the built-in
rule-based fallback when the daily quota runs out.

## What is free forever

| Piece | Service | Free tier |
|---|---|---|
| Web app + API | Render web service (750 hrs/mo) | Spins down after 15 min idle; first request wakes it (~50 s) |
| Database | MongoDB Atlas M0 cluster | 512 MB — plenty for this app |
| AI assistant | Google Gemini free tier | Falls back to rule-based replies automatically |

## One-time setup

1. **Push the repo to GitHub** (private repo is fine).
2. **MongoDB Atlas** (you already have the cluster):
   - Network Access → *Add IP* → allow `0.0.0.0/0` (Render's egress IPs rotate).
   - Keep using the same `carbonsense_fastapi` database.
3. **Gemini key** (optional): AI Studio key works as-is.

## Create the Render service (~5 minutes)

1. Go to **dashboard.render.com** → **New → Web Service**.
2. **Connect your GitHub repo** (grant Render access when prompted).
3. Render detects `render.yaml`; if not, set manually:
   - **Runtime:** Python 3.12
   - **Build command:**
     ```
     pip install -r requirements.txt -r requirements-deploy.txt
     npx pnpm install --frozen-lockfile
     npx pnpm install --frozen-lockfile
     npx pnpm run build
     ```
   - **Start command:**
     ```
     uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Health check path:** `/api/v1/health`
4. **Environment variables** (Render dashboard → Environment):
   | Key | Value |
   |---|---|
   | `MONGODB_URI` | your Atlas connection string (same one as local `.env`) |
   | `JWT_SECRET` | any long random string (Render can generate one) |
   | `GEMINI_API_KEY` | your AI Studio key (optional) |
   | `COOKIE_SECURE` | `true` |
   | `FRONTEND_DIST` | `dist/public` |
5. **Create Web Service.** First build takes ~5–8 minutes.

Your app is then live at `https://<service-name>.onrender.com`.

## How the single process works

- `FRONTEND_DIST=dist/public` tells FastAPI to serve the built SPA
  (`backend/app/main.py` SPA fallback: API routes always win, unknown paths
  return `index.html`).
- The Node/Express dev proxy is **not used in production** — the browser talks
  to FastAPI directly, and `/api/v1/...` paths exist on the same origin, so
  cookies and CSRF work unchanged.
- Model artifacts (`server/model_runtime/artifacts_v25/`, ~1 MB) ship with the
  repo and are hash-verified at startup.

## Free-tier behavior to expect

- **Cold starts:** after 15 idle minutes the service sleeps; the next page
  load takes ~50 s to wake it. Health-check pings (e.g. UptimeRobot free tier
  every 5 min) prevent sleeping entirely if you want.
- **Bandwidth:** 100 GB/month — far above this app's needs.
- **Atlas M0:** never expires; 512 MB holds millions of ledger rows.

## Updating the deployment

Push to `main` — Render auto-rebuilds and redeploys. Verify locally before
pushing with the exact production commands:

```bash
pnpm run build
MONGODB_URI=... JWT_SECRET=... COOKIE_SECURE=false FRONTEND_DIST=dist/public \
  py -3.12 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8090
```

Then open http://127.0.0.1:8090 — the same single process that runs on Render.
