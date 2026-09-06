"""FastAPI application entry point for the staged CarbonSense migration."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .db.mongo import close_mongo, connect_mongo
from .routers import activity, admin, assistant, auth, goals, health, history, insights, model, organization, planning, privacy, profile, recommendations, reports


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_mongo()
    try:
        yield
    finally:
        await close_mongo()


app = FastAPI(
    title="CarbonSense FastAPI",
    version="1.0.0-migration",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.frontend_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(model.router, prefix="/api/v1")
app.include_router(activity.router, prefix="/api/v1")
app.include_router(goals.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(planning.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(organization.router, prefix="/api/v1")
app.include_router(privacy.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(assistant.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Optional single-process deployment: when FRONTEND_DIST points at a built
# Vite bundle, FastAPI serves the SPA directly (API routes always take
# precedence). This removes the Node/Express proxy layer in production.
# ---------------------------------------------------------------------------

from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

FRONTEND_DIST = os.getenv("FRONTEND_DIST", "")

if FRONTEND_DIST:
    _dist = Path(FRONTEND_DIST)
    if _dist.is_dir():
        assets = _dist / "assets"
        if assets.is_dir():
            app.mount("/assets", StaticFiles(directory=assets), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(full_path: str):
            candidate = (_dist / full_path).resolve()
            if full_path and candidate.is_file() and str(candidate).startswith(str(_dist.resolve())):
                return FileResponse(candidate)
            return FileResponse(_dist / "index.html")

        print(f"[deploy] serving built frontend from {_dist}")
    else:
        print(f"[deploy] FRONTEND_DIST={FRONTEND_DIST} does not exist — API-only mode")


# Static file serving is handled by Express on port 3000 in development.
# In production single-process mode the SPA fallback above serves the build.
