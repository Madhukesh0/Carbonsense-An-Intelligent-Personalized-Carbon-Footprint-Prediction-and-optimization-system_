from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user, hash_password, require_roles
from ..db.mongo import get_database, utc_now
from ..schemas.governance import ActiveUpdateRequest, PasswordResetRequest, RoleUpdateRequest


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
    rows = await db.users.find({}, {"password_hash": 0}).sort("created_at", -1).to_list(100)
    return [{
        "id": str(row["_id"]),
        "name": row.get("name"),
        "email": row.get("email"),
        "role": row.get("role"),
        "country": row.get("country"),
        "organizationId": row.get("organization_id"),
        "isActive": row.get("is_active", True),
        "lastSignedIn": row.get("last_signed_in"),
        "createdAt": row.get("created_at"),
    } for row in rows]


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


@router.get("/users/{user_id}/detail")
async def user_detail(user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))], user_id: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    """Individual member record (runs, goal, activity, recommendations) for an
    admin's organization. Every read is written to the governance audit log."""
    target = await db.users.find_one({"_id": user_id}, {"password_hash": 0})
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user["role"] != "super_admin" and target.get("organization_id") != user.get("organization_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="That user is not a member of your organization.")
    runs = await db.footprint_runs.find({"user_id": user_id}).sort("created_at", -1).to_list(12)
    goal = await db.carbon_goals.find_one({"user_id": user_id, "status": "active"}, sort=[("created_at", -1)])
    activities = await db.activity_ledger.find({"user_id": user_id}).sort("activity_date", -1).to_list(15)
    assignments = await db.user_recommendations.find({"user_id": user_id}).to_list(200)
    await audit(db, user, "member_detail", user_id, "view_member_detail", f"{user.get('name')} viewed the individual record of {target.get('email') or user_id}.")
    return {
        "id": user_id,
        "name": target.get("name"),
        "email": target.get("email"),
        "role": target.get("role"),
        "country": target.get("country"),
        "lastSignedIn": target.get("last_signed_in"),
        "createdAt": target.get("created_at"),
        "runs": [{"id": str(r["_id"]), "predictedKg": r.get("predicted_kg"), "region": r.get("region"), "createdAt": r.get("created_at")} for r in runs],
        "activeGoal": {"baselineKg": goal.get("baseline_kg"), "targetKg": goal.get("target_kg"), "deadline": goal.get("deadline"), "createdAt": goal.get("created_at")} if goal else None,
        "activities": [{"id": str(a["_id"]), "activityDate": a.get("activity_date"), "category": a.get("category"), "quantity": a.get("quantity"), "unit": a.get("unit"), "co2Kg": a.get("co2_kg"), "notes": a.get("notes")} for a in activities],
        "recommendations": {
            "assigned": len(assignments),
            "accepted": len([a for a in assignments if a.get("status") in ("accepted", "completed")]),
            "completed": len([a for a in assignments if a.get("status") == "completed"]),
            "verified": len([a for a in assignments if a.get("verification_status") == "verified"]),
        },
    }


@router.get("/users/{user_id}/logins")
async def user_login_history(user: Annotated[dict[str, Any], Depends(require_roles("super_admin"))], user_id: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    rows = await db.login_events.find({"user_id": user_id}).sort("created_at", -1).to_list(50)
    return [{"id": str(r["_id"]), "email": r.get("email"), "ip": r.get("ip"), "createdAt": r.get("created_at")} for r in rows]


@router.post("/users/{user_id}/password")
async def reset_password(
    user_id: str,
    payload: PasswordResetRequest,
    user: Annotated[dict[str, Any], Depends(require_roles("super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    """Set a member's password directly (super_admin) and revoke all their
    active sessions so the change takes effect immediately."""
    if user_id == str(user["_id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Change your own password from your profile instead.")
    if not await db.users.find_one({"_id": user_id}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    await db.users.update_one({"_id": user_id}, {"$set": {"password_hash": hash_password(payload.password), "updated_at": utc_now()}})
    await db.sessions.update_many({"user_id": user_id, "revoked_at": None}, {"$set": {"revoked_at": utc_now()}})
    await audit(db, user, "user", user_id, "reset_password", "Password reset; all active sessions revoked.")
    return {"success": True}
