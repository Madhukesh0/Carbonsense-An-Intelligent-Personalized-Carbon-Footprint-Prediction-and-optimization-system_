from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_database


router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, str]:
    await db.command("ping")
    return {"status": "ok", "database": "mongodb"}
