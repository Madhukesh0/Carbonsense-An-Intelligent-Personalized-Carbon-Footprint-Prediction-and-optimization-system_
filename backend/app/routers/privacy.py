from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from ..core.security import get_current_user
from ..db.mongo import get_database, utc_now


router = APIRouter(prefix="/privacy", tags=["privacy"])


class PrivacyUpdateRequest(BaseModel):
    share_aggregates: bool


@router.get("")
async def get_privacy(user: Annotated[dict[str, Any], Depends(get_current_user)]) -> dict[str, bool]:
    return {"shareAggregates": bool(user.get("share_aggregates"))}


@router.patch("")
async def update_privacy(payload: PrivacyUpdateRequest, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, bool]:
    await db.users.update_one({"_id": str(user["_id"])}, {"$set": {"share_aggregates": payload.share_aggregates, "updated_at": utc_now()}})
    return {"success": True, "shareAggregates": payload.share_aggregates}
