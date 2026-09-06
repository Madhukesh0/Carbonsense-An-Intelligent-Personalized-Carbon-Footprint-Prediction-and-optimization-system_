from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user, require_roles
from ..db.mongo import get_database, utc_now
from ..schemas.governance import ActiveUpdateRequest, RoleUpdateRequest


router = APIRouter(prefix="/admin", tags=["admin"])


def scope_query(user: dict[str, Any]) -> dict[str, Any]:
    return {} if user["role"] == "super_admin" else {"organization_id": user.get("organization_id")}


async def audit(db: AsyncIOMotorDatabase, user: dict[str, Any], entity_type: str, entity_id: str, action: str, details: str) -> None:
    await db.governance_audit_logs.insert_one({"_id": str(uuid4()), "actor_user_id": str(user["_id"]), "organization_id": user.get("organization_id"), "entity_type": entity_type, "entity_id": entity_id, "action": action, "details": details, "created_at": utc_now()})


@router.get("/dashboard")
async def dashboard(user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    members = await db.users.find(scope_query(user)).to_list(500)
    allowed = {str(member["_id"]) for member in members if member.get("share_aggregates")}
    runs = await db.footprint_runs.find({"user_id": {"$in": list(allowed)}}).to_list(1_000)
    regions = []
    for region in ("mixed", "renewable_heavy"):
        regional_runs = [run for run in runs if run.get("region") == region]
        regions.append({"region": region, "count": len(regional_runs), "averageKg": round(sum(run["predicted_kg"] for run in regional_runs) / len(regional_runs)) if regional_runs else 0})
    countries = [{"country": country, "count": count} for country, count in Counter(member.get("country") or "Unspecified" for member in members if str(member["_id"]) in allowed).most_common()]
    now = utc_now()
    timeline = []
    for index in range(6):
        end = now - timedelta(days=(5 - index) * 7)
        start = end - timedelta(days=7)
        rows = [run for run in runs if start <= run["created_at"] < end]
        timeline.append({"week": f"W{index + 1}", "runs": len(rows), "averageKg": round(sum(row["predicted_kg"] for row in rows) / len(rows)) if rows else 0})
    return {"members": len(allowed), "runs": len(runs), "averageKg": round(sum(run["predicted_kg"] for run in runs) / len(runs)) if runs else 0, "regions": regions, "countries": countries, "timeline": timeline, "disclaimer": "All charts use consented aggregate records only. Individual histories, identities, and raw activity entries are not exposed."}


@router.get("/users")
async def list_users(user: Annotated[dict[str, Any], Depends(require_roles("super_admin"))], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    del user
    return await db.users.find({}, {"password_hash": 0}).sort("created_at", -1).to_list(100)


@router.patch("/users/{user_id}/role")
async def update_role(user_id: str, payload: RoleUpdateRequest, user: Annotated[dict[str, Any], Depends(require_roles("super_admin"))], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    if user_id == str(user["_id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot change your own role.")
    target = await db.users.find_one({"_id": user_id})
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    await db.users.update_one({"_id": user_id}, {"$set": {"role": payload.role, "updated_at": utc_now()}})
    await audit(db, user, "user", user_id, "change_role", f"Role changed from {target['role']} to {payload.role}.")
    return {"success": True, "role": payload.role}


@router.patch("/users/{user_id}/active")
async def update_active(user_id: str, payload: ActiveUpdateRequest, user: Annotated[dict[str, Any], Depends(require_roles("super_admin"))], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    if user_id == str(user["_id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot deactivate your own account.")
    if not await db.users.find_one({"_id": user_id}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    await db.users.update_one({"_id": user_id}, {"$set": {"is_active": payload.is_active, "updated_at": utc_now()}})
    await audit(db, user, "user", user_id, "activate_account" if payload.is_active else "deactivate_account", "Account active state changed.")
    return {"success": True, "isActive": payload.is_active}


@router.get("/audit")
async def audit_log(user: Annotated[dict[str, Any], Depends(require_roles("super_admin"))], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    del user
    return await db.governance_audit_logs.find({}).sort("created_at", -1).to_list(200)
