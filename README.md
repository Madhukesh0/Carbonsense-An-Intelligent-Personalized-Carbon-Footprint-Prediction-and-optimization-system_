# CarbonSense — Intelligent Personalized Carbon Footprint Prediction & Optimization

CarbonSense estimates a personal monthly carbon footprint two ways from a
15-question survey, explains the result, and turns it into impact-ranked
actions:

1. **AI prediction** — a deployed XGBoost model (`final-xgboost-v25`) trained
   on the `carbonsense-synthetic-v2.5` dataset (10,000 rows, cited-factor
   targets), with TreeSHAP contribution explanations and a 90% split-conformal
   interval (±71.3 kg, 91.4% coverage).
2. **Transparent baseline** — the deterministic form of the same cited-factor
   construction: Ember 2025 country grid factors, IPCC 2006 fuel chemistry,
   Scarborough 2023 diet bands, OWID air-travel bands, EEA clothing, IPCC
   waste. Both paths share one factor set, so the AI-vs-baseline gap isolates
   model behaviour, not factor drift.

Everything — estimates, dynamic impact-ranked recommendations, goal-based
plans, the What-if simulator, and the personal Prophet/ETS activity forecast —
is served by **one FastAPI process** (the SPA fallback serves the built React
frontend in production).

## Features

- 15-question survey → AI estimate + auditable baseline, side by side
- TreeSHAP "which of my choices raised or lowered this" breakdown
- Impact-ranked recommendations, re-scored after every submission, with a
  goal slider ("accept these 3 actions ≈ −180 kg of your 647 kg estimate")
- What-if scenario simulator (model + baseline recompute)
- Personal activity ledger → Prophet forecast once 12 consecutive months /
  90+ recorded days exist (ETS from 6 months, labelled fallback before)
- Organizations: admin invite flows (both directions), join requests,
  member reminders, aggregate contributor analytics (consent-filtered)
- Role-gated governance with audit logging; three account types:
  `individual`, `org_admin`, `super_admin`
- AI assistant (Gemini free tier, grounded on workspace context) with a
  rule-based fallback

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 19 + Vite + Tailwind 4 + shadcn/radix |
| Backend | FastAPI (single-process production mode) |
| ML | XGBoost 2.5 runtime (SHAP + conformal), scikit-learn |
| Forecasting | Prophet / statsmodels ETS |
| Database | MongoDB Atlas (motor) |
| Auth | JWT access/refresh cookies + argon2 password hashing + CSRF |
| AI assistant | Gemini API (optional; graceful fallback) |

## Run locally

Requirements: Python 3.12, Node 22, corepack.

```bash
py -3.12 -m pip install -r requirements.txt -r requirements-deploy.txt
corepack pnpm install
```

Create `.env` beside `package.json`:

```env
MONGODB_URI=mongodb+srv://USER:PASS@CLUSTER/carbonsense_fastapi?retryWrites=true&w=majority
JWT_SECRET=a-long-random-secret
GEMINI_API_KEY=            # optional
```

Start the dev server (Node proxy + FastAPI child):

```bash
NODE_ENV=development pnpm exec tsx watch server/_core/index.ts
```

Open http://localhost:3000 — the Node server spawns FastAPI on port 8015.

## Deploy (free tier)

Single Python process on Render (free), MongoDB Atlas M0 (free forever),
Gemini free tier. See [DEPLOY.md](DEPLOY.md) — build + start commands are in
`render.yaml`.

```bash
pnpm run build
FRONTEND_DIST=dist/public uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

## Repo layout

```
backend/app/        FastAPI routers, services, schemas (the production API)
client/src/         React SPA (pages, components, hooks)
server/_core/       Dev-only Express proxy + Vite middleware
server/model_runtime/artifacts_v25/   Frozen model artifacts (hash-verified)
data/v2_training/   The v2.5 dataset (clean_dataset_v2.csv)
scripts/            Dataset generator, trainer, audits, seeding utilities
citations/          Factor provenance (sources, worked examples)
tests               backend/tests (pytest) + client/server *.test.ts (vitest)
```

## Honest boundaries

The dataset and target are synthetic and formula-derived, as documented in
`DATASET_FREEZE.md` and the model metadata. Estimates are indicative planning
guidance — not direct measurements of real-world personal emissions, and not
verified reductions.

## Verification

```bash
pnpm run check        # TypeScript
pnpm test             # vitest suites (client + server contracts)
py -3.12 -m unittest discover -s backend/tests   # backend tests
```
