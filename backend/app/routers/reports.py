from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user, require_roles
from ..db.mongo import get_database, utc_now
from ..schemas.features import ReportCreateRequest, ReportStatusRequest


router = APIRouter(prefix="/reports", tags=["reports"])


def as_report_response(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(report["_id"]),
        "category": report["category"],
        "details": report["details"],
        "status": report["status"],
        "createdAt": report["created_at"],
        "updatedAt": report["updated_at"],
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_report(payload: ReportCreateRequest, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, bool]:
    await db.report_requests.insert_one({"_id": str(uuid4()), "user_id": str(user["_id"]), "organization_id": user.get("organization_id"), **payload.model_dump(), "status": "open", "assigned_to_user_id": None, "created_at": utc_now(), "updated_at": utc_now()})
    return {"success": True}


@router.get("/mine")
async def mine(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    rows = await db.report_requests.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(20)
    return [as_report_response(row) for row in rows]


@router.get("/admin")
async def admin_list(user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    query = {} if user["role"] == "super_admin" else {"organization_id": user.get("organization_id")}
    rows = await db.report_requests.find(query).sort("created_at", -1).to_list(100)
    return [as_report_response(row) for row in rows]


@router.patch("/{report_id}")
async def update_status(report_id: str, payload: ReportStatusRequest, user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, bool]:
    report = await db.report_requests.find_one({"_id": report_id})
    if not report or (user["role"] != "super_admin" and report.get("organization_id") != user.get("organization_id")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update reports in your organization.")
    await db.report_requests.update_one({"_id": report_id}, {"$set": {"status": payload.status, "assigned_to_user_id": str(user["_id"]), "updated_at": utc_now()}})
    await db.governance_audit_logs.insert_one({"_id": str(uuid4()), "actor_user_id": str(user["_id"]), "organization_id": user.get("organization_id"), "entity_type": "report_request", "entity_id": report_id, "action": "status_change", "details": f"Status changed to {payload.status}.", "created_at": utc_now()})
    return {"success": True}
