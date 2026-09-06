from __future__ import annotations

import asyncio
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user
from ..db.mongo import get_database
from .history import as_history_run
from ..services.activity_bootstrap import ensure_ledger_history
from ..services.forecasting import run_forecast


router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/history")
async def history(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    rows = await db.footprint_runs.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(100)
    return [as_history_run(row) for row in rows]


@router.get("/forecast")
async def forecast(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    user_id = str(user["_id"])
    rows = await db.activity_ledger.find({"user_id": user_id}).sort("activity_date", 1).to_list(5000)
    # Accounts with a submitted estimate but a short ledger get their history
    # bootstrapped from their own run (labelled entries) so the forecast tiers
    # can engage instead of falling back forever.
    if len(rows) < 380:
        latest = await db.footprint_runs.find_one({"user_id": user_id, "run_type": "prediction"}, sort=[("created_at", -1)])
        if latest:
            inserted = await ensure_ledger_history(db, user_id, latest["input_payload"])
            if inserted:
                rows = await db.activity_ledger.find({"user_id": user_id}).sort("activity_date", 1).to_list(5000)
    return await asyncio.to_thread(run_forecast, rows)
