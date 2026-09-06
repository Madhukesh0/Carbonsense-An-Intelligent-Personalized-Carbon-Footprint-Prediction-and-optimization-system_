from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user
from ..db.mongo import get_database, utc_now
from ..schemas.features import GoalCreateRequest


router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("")
async def list_goals(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    return await db.carbon_goals.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(10)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_goal(payload: GoalCreateRequest, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, bool]:
    if payload.target_kg >= payload.baseline_kg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your target must be below your baseline.")
    await db.carbon_goals.update_many({"user_id": str(user["_id"]), "status": "active"}, {"$set": {"status": "superseded", "updated_at": utc_now()}})
    await db.carbon_goals.insert_one({"_id": str(uuid4()), "user_id": str(user["_id"]), **payload.model_dump(), "status": "active", "created_at": utc_now(), "updated_at": utc_now()})
    return {"success": True}
