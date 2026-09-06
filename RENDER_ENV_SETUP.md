# CarbonSense — Render Deployment Cheat Sheet

**Where your real values live:** `D:\proj\.env` (open it with Notepad — File → Open → type `D:\proj\.env`)

Copy the FULL values from that file into the Render dashboard → your Web Service → **Environment** → Add Environment Variable.

---

## Environment variables to add on Render

### Required

| Key | Value |
|---|---|
| `MONGODB_URI` | *(paste the full `MONGODB_URI=` line from `D:\proj\.env`)* |
| `JWT_SECRET` | *(paste the full `JWT_SECRET=` line from `D:\proj\.env`)* |

### Optional — AI assistant

| Key | Value |
|---|---|
| `GEMINI_API_KEY` | *(paste the full `GEMINI_API_KEY=` line from `D:\proj\.env`)* |
| `GEMINI_MODEL` | `gemini-3.6-flash` |

### Optional — recommended settings

| Key | Value | Why |
|---|---|---|
| `COOKIE_SECURE` | `true` | Cookies sent over HTTPS only (correct for the live site) |
| `FRONTEND_DIST` | `dist/public` | FastAPI serves the built frontend (single-process mode) |
| `PYTHON_VERSION` | `3.12.10` | Matches your development Python |

### Do NOT add

| Key | Reason |
|---|---|
| `PORT` | Render assigns it automatically |
| `FASTAPI_INTERNAL_PORT` | Only used by the local dev proxy |
| `VITE_ANALYTICS_*`, `OAUTH_SERVER_URL` | Optional local features, not needed on Render |

---

## Build & Start commands (Native Python path)

**Build command:**
```bash
pip install -r requirements.txt -r requirements-deploy.txt && npm install -g corepack@latest && corepack pnpm install --frozen-lockfile && corepack pnpm run build
```

**Start command:**
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

**Health check path:** `/api/v1/health`

---

## Pre-deploy checklist

1. ✅ Atlas **Network Access** includes `0.0.0.0/0` (cloud.mongodb.com → your cluster → Network Access)
2. ✅ `MONGODB_URI` password is URL-encoded (no raw `@ # %` characters)
3. ✅ `.env` file itself is NOT committed to GitHub (it isn't — already gitignored)

## After deployment

Open `https://<your-service>.onrender.com` → log in with any documented account
→ run a prediction → confirm the AI-vs-baseline panel appears.

Service sleeps after 15 idle minutes (~50 s wake). Keep it awake with a free
UptimeRobot ping to `/api/v1/health` every 5 minutes.
