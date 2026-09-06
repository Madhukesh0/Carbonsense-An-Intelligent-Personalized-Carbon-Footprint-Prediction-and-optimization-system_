from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user
from ..db.mongo import get_database, utc_now
from ..routers.auth import as_user_response
from ..schemas.governance import ProfileUpdateRequest


router = APIRouter(prefix="/profile", tags=["profile"])


@router.patch("")
async def update_profile(payload: ProfileUpdateRequest, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]):
    update = {key: value for key, value in payload.model_dump().items() if value is not None}
    update["updated_at"] = utc_now()
    await db.users.update_one({"_id": str(user["_id"])}, {"$set": update})
    updated = await db.users.find_one({"_id": str(user["_id"])}, {"password_hash": 0})
    return as_user_response(updated)
