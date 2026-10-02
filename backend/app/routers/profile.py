from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.config import settings
from ..core.security import (
    ACCESS_COOKIE,
    CSRF_COOKIE,
    REFRESH_COOKIE,
    get_current_user,
    require_csrf,
    require_roles,
    verify_password,
)
from ..db.mongo import get_database, utc_now
from ..routers.auth import as_user_response
from ..schemas.governance import AccountDeleteRequest, ProfileUpdateRequest


router = APIRouter(prefix="/profile", tags=["profile"])


@router.patch("")
async def update_profile(payload: ProfileUpdateRequest, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]):
    update = {key: value for key, value in payload.model_dump().items() if value is not None}
    update["updated_at"] = utc_now()
    await db.users.update_one({"_id": str(user["_id"])}, {"$set": update})
    updated = await db.users.find_one({"_id": str(user["_id"])}, {"password_hash": 0})
    return as_user_response(updated)


# Personal records removed with the account; governance audit entries are
# intentionally retained as an immutable historical record.
USER_SCOPED_COLLECTIONS = (
    "sessions",
    "login_events",
    "footprint_runs",
    "activity_ledger",
    "carbon_goals",
    "user_recommendations",
    "report_requests",
    "organization_join_requests",
    "organization_invitations",
    "reminders",
)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    payload: AccountDeleteRequest,
    request: Request,
    response: Response,
    user: Annotated[dict[str, Any], Depends(require_roles("individual", "org_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> Response:
    """Permanently delete the signed-in member's own account after password
    confirmation. super_admin accounts cannot be self-deleted this way."""
    require_csrf(request)
    user_id = str(user["_id"])
    stored = await db.users.find_one({"_id": user_id}, {"password_hash": 1})
    if not stored or not verify_password(payload.password, stored.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The password you entered is incorrect.")
    organization_id = user.get("organization_id")

    if user["role"] == "org_admin" and organization_id:
        remaining_members = await db.users.count_documents({"organization_id": organization_id, "_id": {"$ne": user_id}})
        if remaining_members:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Your organization still has other members. Remove them first, then delete your account.")
        # The last organization administrator is leaving: retire the organization
        # and everything scoped to it so no orphaned records remain.
        await db.organizations.delete_one({"_id": organization_id})
        for collection in ("organization_join_requests", "organization_invitations", "reminders", "report_requests", "organization_recommendations", "user_recommendations"):
            await getattr(db, collection).delete_many({"organization_id": organization_id})
    elif organization_id:
        await db.organizations.update_one({"_id": organization_id}, {"$inc": {"member_count": -1}})

    for collection in USER_SCOPED_COLLECTIONS:
        await getattr(db, collection).delete_many({"user_id": user_id})
    await db.report_requests.update_many({"assigned_to_user_id": user_id}, {"$set": {"assigned_to_user_id": None}})
    await db.users.delete_one({"_id": user_id})
    await db.governance_audit_logs.insert_one({
        "_id": str(uuid4()),
        "actor_user_id": user_id,
        "organization_id": organization_id,
        "entity_type": "user",
        "entity_id": user_id,
        "action": "delete_account",
        "details": f"{user.get('name')} ({user.get('email')}) permanently deleted their own account and all personal records.",
        "created_at": utc_now(),
    })
    for cookie in (ACCESS_COOKIE, REFRESH_COOKIE, CSRF_COOKIE):
        response.delete_cookie(cookie, path="/", secure=settings.cookie_secure, samesite="lax")
    return response
