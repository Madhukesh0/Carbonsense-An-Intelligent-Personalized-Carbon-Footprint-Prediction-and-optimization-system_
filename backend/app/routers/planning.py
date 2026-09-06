from __future__ import annotations

import asyncio
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from ..core.security import get_current_user
from ..db.mongo import get_database
from ..schemas.model import SurveyPayload
from ..services.baseline import calculate_baseline
from ..services.prediction import run_prediction_v25


router = APIRouter(prefix="/planning", tags=["planning"])


class WhatIfRequest(BaseModel):
    input: SurveyPayload
    changes: dict[str, Any]
    starting_point: Literal["ai_estimate", "transparent_baseline"] = "ai_estimate"


async def latest_completed(db: AsyncIOMotorDatabase, user_id: str) -> dict[str, Any] | None:
    return await db.footprint_runs.find_one({"user_id": user_id, "run_type": "prediction"}, sort=[("created_at", -1)])


@router.get("/latest-completed")
async def latest_completed_result(user: Annotated[dict[str, Any], Depends(get_current_user)], db: AsyncIOMotorDatabase = Depends(get_database)) -> dict[str, Any]:
    run = await latest_completed(db, str(user["_id"]))
    if not run:
        return {"available": False, "reason": "Complete an AI prediction and transparent baseline with the same answers before opening a What-if scenario.", "profile": None, "predictionKg": None, "baselineKg": None, "completedAt": None}
    profile = run["input_payload"]
    # Same pairing rule as result-led: reuse a stored baseline run only when
    # its answers match the latest prediction; otherwise compute it on the fly
    # so both numbers always describe the same submitted answers.
    baseline_run = await db.footprint_runs.find_one({"user_id": str(user["_id"]), "run_type": "baseline", "baseline_kg": {"$ne": None}}, sort=[("created_at", -1)])
    if baseline_run and baseline_run.get("input_payload") == profile:
        baseline_kg = float(baseline_run["baseline_kg"])
    else:
        baseline_kg = float(calculate_baseline(profile)["total"])
    return {"available": True, "reason": None, "profile": profile, "predictionKg": run["predicted_kg"], "baselineKg": round(baseline_kg, 1), "completedAt": run["created_at"]}


@router.post("/what-if")
async def what_if(payload: WhatIfRequest, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> dict[str, Any]:
    del user
    before = payload.input.model_dump()
    after = SurveyPayload(**{**before, **payload.changes}).model_dump()
    if payload.starting_point == "transparent_baseline":
        before_value = calculate_baseline(before)["total"]
        after_value = calculate_baseline(after)["total"]
        label = "Transparent baseline"
    else:
        before_value = (await asyncio.to_thread(run_prediction_v25, before))["predictedKg"]
        after_value = (await asyncio.to_thread(run_prediction_v25, after))["predictedKg"]
        label = "AI estimate"
    return {"before": before_value, "after": after_value, "delta": round(after_value - before_value, 1), "startingPoint": payload.starting_point, "startingPointLabel": label, "interpretation": f"This scenario {'lowers' if after_value < before_value else 'raises'} the selected {label.lower()}. It is a planning comparison, not a verified outcome."}
