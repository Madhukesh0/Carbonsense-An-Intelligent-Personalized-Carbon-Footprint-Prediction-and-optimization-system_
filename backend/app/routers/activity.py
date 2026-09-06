from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user
from ..db.mongo import get_database, utc_now
from ..schemas.features import ActivityCreateRequest
from ..services.progress import calculate_progress


router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("")
async def list_activity(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    return await db.activity_ledger.find({"user_id": str(user["_id"])}).sort("activity_date", -1).to_list(100)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_activity(payload: ActivityCreateRequest, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, bool]:
    await db.activity_ledger.insert_one({
        "_id": str(uuid4()), "user_id": str(user["_id"]), "organization_id": user.get("organization_id"),
        **payload.model_dump(), "created_at": utc_now(),
    })
    return {"success": True}


@router.delete("/{activity_id}")
async def remove_activity(activity_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, bool]:
    await db.activity_ledger.delete_one({"_id": activity_id, "user_id": str(user["_id"])})
    return {"success": True}


@router.get("/summary")
async def summary(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    rows = await db.activity_ledger.find({"user_id": str(user["_id"])}).to_list(500)
    categories = ["transport", "electricity", "diet", "fuel"]
    return {"totalKg": sum(row["co2_kg"] for row in rows), "entries": len(rows), "byCategory": [{"category": category, "kg": sum(row["co2_kg"] for row in rows if row["category"] == category)} for category in categories]}


@router.get("/progress")
async def progress(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    rows = await db.activity_ledger.find({"user_id": str(user["_id"])}).to_list(500)
    goal = await db.carbon_goals.find_one({"user_id": str(user["_id"]), "status": "active"}, sort=[("created_at", -1)])
    return calculate_progress(rows, goal)


@router.get("/quest-summary")
async def quest_summary(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    user_id = str(user["_id"])
    runs = await db.footprint_runs.find({"user_id": user_id}).to_list(100)
    verified = await db.user_recommendations.find({"user_id": user_id, "status": "completed", "verification_status": "verified"}).to_list(100)
    self_reported = await db.user_recommendations.find({"user_id": user_id, "status": "completed", "verification_status": "self_reported"}).to_list(100)
    score = len(runs) * 120 + len(verified) * 250
    badges = [
        "First estimate" if runs else None,
        "Action completed" if verified else None,
        "Habit tracker" if len(runs) > 2 else None,
        "Climate consistent" if len(verified) > 2 else None,
    ]
    return {
        "score": score,
        "streak": min(12, len(runs) + len(verified)),
        "badges": [badge for badge in badges if badge],
        "disclaimer": f"Points reward recorded participation and administrator-verified actions only. {len(self_reported)} self-reported completion(s) are awaiting verification; no unverified reduction is counted as proven, and points do not claim verified emissions reductions.",
    }
