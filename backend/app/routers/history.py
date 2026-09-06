from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user
from ..db.mongo import get_database


router = APIRouter(prefix="/history", tags=["history"])


def as_history_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(run["_id"]),
        "runType": run["run_type"],
        "predictedKg": run["predicted_kg"],
        "baselineKg": run.get("baseline_kg"),
        "region": run["region"],
        "modelVersion": run.get("model_version"),
        "createdAt": run["created_at"],
    }


@router.get("")
async def list_history(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    rows = await db.footprint_runs.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(30)
    return [as_history_run(row) for row in rows]


@router.delete("")
async def clear_history(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, bool]:
    await db.footprint_runs.delete_many({"user_id": str(user["_id"])})
    return {"success": True}
