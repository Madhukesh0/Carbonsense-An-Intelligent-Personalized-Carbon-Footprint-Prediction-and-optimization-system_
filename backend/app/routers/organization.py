from __future__ import annotations

from collections import Counter
from secrets import token_urlsafe
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user, require_csrf, require_roles
from ..db.mongo import get_database, utc_now
from ..schemas.organization import InvitationDecisionRequest, InviteIndividualRequest, OrganizationCreateRequest, OrganizationJoinDecisionRequest, OrganizationJoinRequest, ReminderCreateRequest, ReminderStatusRequest


router = APIRouter(prefix="/organization", tags=["organization"])


def scoped_members_query(user: dict[str, Any]) -> dict[str, Any]:
    return {} if user["role"] == "super_admin" else {"organization_id": user.get("organization_id")}


# ---------------------------------------------------------------------------
# Organization CRUD
# ---------------------------------------------------------------------------

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreateRequest,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    """Create a new organization and make the creator an org_admin."""
    if user.get("organization_id"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already belong to an organization.")
    invite_code = token_urlsafe(8)
    org = {
        "_id": str(uuid4()),
        "name": payload.name.strip(),
        "description": payload.description.strip() if payload.description else None,
        "invite_code": invite_code,
        "created_by": str(user["_id"]),
        "member_count": 1,
        "created_at": utc_now(),
    }
    await db.organizations.insert_one(org)
    await db.users.update_one(
        {"_id": str(user["_id"])},
        {"$set": {"organization_id": org["_id"], "role": "org_admin", "updated_at": utc_now()}},
    )
    return {
        "id": org["_id"],
        "name": org["name"],
        "inviteCode": invite_code,
        "role": "org_admin",
    }


@router.get("/list")
async def list_organizations(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> list[dict[str, Any]]:
    """Return the organizations available for enrollment during sign-up."""
    orgs = await db.organizations.find({}, {"invite_code": 1, "name": 1, "description": 1, "member_count": 1, "created_at": 1}).sort("member_count", -1).to_list(200)
    return [{
        "id": str(org["_id"]),
        "name": org["name"],
        "description": org.get("description"),
        "inviteCode": org.get("invite_code"),
        "memberCount": org.get("member_count", 0),
        "createdAt": org.get("created_at"),
    } for org in orgs]


@router.post("/join", status_code=status.HTTP_202_ACCEPTED)
async def join_organization(
    payload: OrganizationJoinRequest,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    """Request to join an organization; membership starts only after an admin approves."""
    if user.get("organization_id"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already belong to an organization. Leave your current organization first.")
    resolver = payload.resolver
    if not resolver:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide an invite code or a selected organization id.")
    if payload.organization_id:
        org = await db.organizations.find_one({"_id": payload.organization_id})
    else:
        org = await db.organizations.find_one({"invite_code": payload.invite_code})
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite code or organization selection.")
    user_id = str(user["_id"])
    if await db.organization_join_requests.find_one({"user_id": user_id, "status": "pending"}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already have a pending join request waiting for approval.")
    now = utc_now()
    join_request = {
        "_id": str(uuid4()),
        "user_id": user_id,
        "user_name": user.get("name"),
        "user_email": user.get("email"),
        "organization_id": org["_id"],
        "status": "pending",
        "source": "invite_or_selection",
        "created_at": now,
        "decided_at": None,
        "decided_by": None,
    }
    await db.organization_join_requests.insert_one(join_request)
    await db.governance_audit_logs.insert_one({
        "_id": str(uuid4()),
        "actor_user_id": user_id,
        "organization_id": org["_id"],
        "entity_type": "join_request",
        "entity_id": join_request["_id"],
        "action": "create_join_request",
        "details": f"{user.get('name')} requested to join {org['name']}.",
        "created_at": now,
    })
    return {
        "requestId": join_request["_id"],
        "organizationId": org["_id"],
        "status": "pending",
    }


@router.get("/join-requests/mine")
async def my_join_request(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any] | None:
    """Return the current user's latest join request with its approval status."""
    join_request = await db.organization_join_requests.find_one(
        {"user_id": str(user["_id"])}, sort=[("created_at", -1)]
    )
    if not join_request:
        return None
    org = await db.organizations.find_one({"_id": join_request["organization_id"]}, {"name": 1})
    return {
        "id": join_request["_id"],
        "organizationId": join_request["organization_id"],
        "organizationName": org["name"] if org else "Unknown organization",
        "status": join_request["status"],
        "source": join_request.get("source"),
        "createdAt": join_request["created_at"],
        "decidedAt": join_request.get("decided_at"),
    }


@router.get("/join-requests")
async def pending_join_requests(
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> list[dict[str, Any]]:
    """List pending join requests for the admin's organization."""
    query: dict[str, Any] = {"status": "pending"}
    if user["role"] != "super_admin":
        query["organization_id"] = user.get("organization_id")
    requests = await db.organization_join_requests.find(query).sort("created_at", 1).to_list(200)
    return [{
        "id": item["_id"],
        "userId": item["user_id"],
        "userName": item.get("user_name"),
        "userEmail": item.get("user_email"),
        "organizationId": item["organization_id"],
        "status": item["status"],
        "source": item.get("source"),
        "createdAt": item["created_at"],
    } for item in requests]


@router.post("/join-requests/{request_id}/decision", status_code=status.HTTP_200_OK)
async def decide_join_request(
    request_id: str,
    payload: OrganizationJoinDecisionRequest,
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    """Approve or reject a pending join request; approval grants membership."""
    join_request = await db.organization_join_requests.find_one({"_id": request_id})
    if not join_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Join request not found.")
    if user["role"] != "super_admin" and join_request["organization_id"] != user.get("organization_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This join request belongs to a different organization.")
    if join_request["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"This join request was already {join_request['status']}.")
    now = utc_now()
    if payload.decision == "approved":
        target = await db.users.find_one({"_id": join_request["user_id"]})
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The requester no longer exists.")
        if target.get("organization_id"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The requester already belongs to another organization.")
        await db.users.update_one(
            {"_id": join_request["user_id"]},
            {"$set": {"organization_id": join_request["organization_id"], "role": "individual", "updated_at": now}},
        )
        await db.organizations.update_one({"_id": join_request["organization_id"]}, {"$inc": {"member_count": 1}})
    await db.organization_join_requests.update_one(
        {"_id": request_id},
        {"$set": {"status": payload.decision, "decided_at": now, "decided_by": str(user["_id"])}},
    )
    await db.governance_audit_logs.insert_one({
        "_id": str(uuid4()),
        "actor_user_id": str(user["_id"]),
        "organization_id": join_request["organization_id"],
        "entity_type": "join_request",
        "entity_id": request_id,
        "action": f"join_request_{payload.decision}",
        "details": f"{user.get('name')} {payload.decision} the join request from {join_request.get('user_name')}.",
        "created_at": now,
    })
    return {"id": request_id, "status": payload.decision, "success": True}


# ---------------------------------------------------------------------------
# Organization-initiated invitations: admins invite available individuals,
# the individual accepts or declines.
# ---------------------------------------------------------------------------

@router.get("/available-individuals")
async def available_individuals(
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> list[dict[str, Any]]:
    """Individuals with no organization and no pending invitation — the pool
    an organization admin can invite."""
    pending_user_ids = {doc["user_id"] async for doc in db.organization_invitations.find(
        {"status": "pending", "organization_id": user.get("organization_id") if user["role"] != "super_admin" else {"$ne": None}},
        {"user_id": 1},
    )}
    rows = await db.users.find(
        {"is_active": True, "role": "individual", "organization_id": None},
        {"name": 1, "email": 1, "country": 1},
    ).sort("created_at", -1).to_list(200)
    return [{
        "id": str(row["_id"]),
        "name": row.get("name"),
        "email": row.get("email"),
        "country": row.get("country"),
        "alreadyInvited": str(row["_id"]) in pending_user_ids,
    } for row in rows]


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_individual(
    payload: InviteIndividualRequest,
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    """Invite an unaffiliated individual to the admin's organization."""
    if user["role"] != "super_admin" and not user.get("organization_id"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Create your organization before sending invitations.")
    organization_id = user.get("organization_id")
    org = await db.organizations.find_one({"_id": organization_id})
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    target = await db.users.find_one({"_id": payload.user_id, "is_active": True})
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="That individual no longer exists.")
    if target.get("organization_id"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="That individual already belongs to an organization.")
    if target.get("role") != "individual":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only individual accounts can be invited.")
    if await db.organization_invitations.find_one({"user_id": payload.user_id, "organization_id": organization_id, "status": "pending"}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An invitation for this person is already pending.")
    now = utc_now()
    invitation = {
        "_id": str(uuid4()),
        "user_id": payload.user_id,
        "user_email": target.get("email"),
        "organization_id": organization_id,
        "organization_name": org.get("name", "the organization"),
        "invited_by": str(user["_id"]),
        "invited_by_name": user.get("name"),
        "status": "pending",
        "created_at": now,
        "decided_at": None,
    }
    await db.organization_invitations.insert_one(invitation)
    await db.governance_audit_logs.insert_one({
        "_id": str(uuid4()),
        "actor_user_id": str(user["_id"]),
        "organization_id": organization_id,
        "entity_type": "invitation",
        "entity_id": invitation["_id"],
        "action": "create_invitation",
        "details": f"{user.get('name')} invited {target.get('email')} to {org.get('name')}.",
        "created_at": now,
    })
    return {"id": invitation["_id"], "status": "pending", "success": True}


@router.get("/invitations/mine")
async def my_invitations(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> list[dict[str, Any]]:
    """Pending (and recently decided) invitations addressed to the current user."""
    rows = await db.organization_invitations.find(
        {"user_id": str(user["_id"])}, sort=[("created_at", -1)]
    ).to_list(50)
    return [{
        "id": row["_id"],
        "organizationName": row.get("organization_name"),
        "invitedByName": row.get("invited_by_name"),
        "status": row["status"],
        "createdAt": row["created_at"],
    } for row in rows]


@router.post("/invitations/{invitation_id}/decision", status_code=status.HTTP_200_OK)
async def decide_invitation(
    invitation_id: str,
    payload: InvitationDecisionRequest,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    """The invited individual accepts or declines their own invitation."""
    invitation = await db.organization_invitations.find_one({"_id": invitation_id})
    if not invitation or invitation["user_id"] != str(user["_id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")
    if invitation["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"This invitation was already {invitation['status']}.")
    now = utc_now()
    if payload.decision == "accepted":
        target = await db.users.find_one({"_id": invitation["user_id"]})
        if not target or target.get("organization_id"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already belong to an organization.")
        await db.users.update_one(
            {"_id": invitation["user_id"]},
            {"$set": {"organization_id": invitation["organization_id"], "updated_at": now}},
        )
        await db.organizations.update_one({"_id": invitation["organization_id"]}, {"$inc": {"member_count": 1}})
    await db.organization_invitations.update_one(
        {"_id": invitation_id},
        {"$set": {"status": payload.decision, "decided_at": now}},
    )
    await db.governance_audit_logs.insert_one({
        "_id": str(uuid4()),
        "actor_user_id": str(user["_id"]),
        "organization_id": invitation["organization_id"],
        "entity_type": "invitation",
        "entity_id": invitation_id,
        "action": f"invitation_{payload.decision}",
        "details": f"{user.get('name')} {payload.decision} the invitation from {invitation.get('organization_name')}.",
        "created_at": now,
    })
    return {"id": invitation_id, "status": payload.decision, "success": True}


@router.get("/invitations")
async def list_organization_invitations(
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> list[dict[str, Any]]:
    """Invitations sent by the admin's organization, newest first."""
    query: dict[str, Any] = {}
    if user["role"] != "super_admin":
        query["organization_id"] = user.get("organization_id")
    rows = await db.organization_invitations.find(query).sort("created_at", -1).to_list(200)
    return [{
        "id": row["_id"],
        "userEmail": row.get("user_email"),
        "status": row["status"],
        "createdAt": row["created_at"],
    } for row in rows]


@router.post("/leave", status_code=status.HTTP_200_OK)
async def leave_organization(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, bool]:
    """Leave the current organization."""
    if not user.get("organization_id"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not a member of any organization.")
    await db.users.update_one(
        {"_id": str(user["_id"])},
        {"$set": {"organization_id": None, "role": "individual", "updated_at": utc_now()}},
    )
    await db.organizations.update_one(
        {"_id": user["organization_id"]},
        {"$inc": {"member_count": -1}},
    )
    return {"success": True}


@router.get("/me")
async def my_organization(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any] | None:
    """Return the user's current organization details, or null."""
    if not user.get("organization_id"):
        return None
    org = await db.organizations.find_one({"_id": user["organization_id"]})
    if not org:
        return None
    members = await db.users.find(
        {"organization_id": org["_id"]}, {"password_hash": 0}
    ).to_list(200)
    return {
        "id": org["_id"],
        "name": org["name"],
        "description": org.get("description"),
        "inviteCode": org.get("invite_code") if user.get("role") in ("org_admin", "super_admin") else None,
        "memberCount": len(members),
        "members": [{"id": str(m["_id"]), "name": m.get("name"), "role": m.get("role"), "country": m.get("country")} for m in members],
        "yourRole": user.get("role"),
    }


# ---------------------------------------------------------------------------
# Org members list (for admin features like reminders)
# ---------------------------------------------------------------------------

@router.get("/members")
async def org_members(
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> list[dict[str, Any]]:
    """List members in the admin's organization."""
    query = {} if user["role"] == "super_admin" else {"organization_id": user.get("organization_id")}
    members = await db.users.find(query, {"password_hash": 0}).to_list(200)
    return [{"id": str(m["_id"]), "name": m.get("name"), "email": m.get("email"), "role": m.get("role"), "country": m.get("country")} for m in members]


# ---------------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------------

@router.post("/reminders", status_code=status.HTTP_201_CREATED)
async def create_reminder(
    payload: ReminderCreateRequest,
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    """Create a reminder for a member."""
    target = await db.users.find_one({"_id": payload.user_id})
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user["role"] != "super_admin" and target.get("organization_id") != user.get("organization_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only send reminders to your organization members.")
    reminder = {
        "_id": str(uuid4()),
        "user_id": payload.user_id,
        "organization_id": user.get("organization_id"),
        "sender_id": str(user["_id"]),
        "sender_name": user.get("name"),
        "title": payload.title.strip(),
        "message": payload.message.strip(),
        "reminder_type": payload.reminder_type,
        "status": "pending",
        "created_at": utc_now(),
        "acknowledged_at": None,
    }
    await db.reminders.insert_one(reminder)
    await db.governance_audit_logs.insert_one({
        "_id": str(uuid4()),
        "actor_user_id": str(user["_id"]),
        "organization_id": user.get("organization_id"),
        "entity_type": "reminder",
        "entity_id": reminder["_id"],
        "action": "create_reminder",
        "details": f"Sent '{payload.reminder_type}' reminder to {payload.user_id}.",
        "created_at": utc_now(),
    })
    return {"id": reminder["_id"], "success": True}


@router.get("/reminders")
async def my_reminders(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> list[dict[str, Any]]:
    """Get reminders sent to the current user."""
    reminders = await db.reminders.find(
        {"user_id": str(user["_id"])}
    ).sort("created_at", -1).to_list(50)
    return [
        {
            "id": r["_id"],
            "title": r["title"],
            "message": r["message"],
            "reminderType": r.get("reminder_type", "general"),
            "status": r["status"],
            "senderName": r.get("sender_name"),
            "createdAt": r["created_at"],
            "acknowledgedAt": r.get("acknowledged_at"),
        }
        for r in reminders
    ]


@router.post("/reminders/{reminder_id}/acknowledge")
async def acknowledge_reminder(
    reminder_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, bool]:
    """Acknowledge a reminder."""
    await db.reminders.update_one(
        {"_id": reminder_id, "user_id": str(user["_id"])},
        {"$set": {"status": "acknowledged", "acknowledged_at": utc_now()}},
    )
    return {"success": True}


@router.post("/reminders/{reminder_id}/dismiss")
async def dismiss_reminder(
    reminder_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, bool]:
    """Dismiss a reminder."""
    await db.reminders.update_one(
        {"_id": reminder_id, "user_id": str(user["_id"])},
        {"$set": {"status": "dismissed"}},
    )
    return {"success": True}


# ---------------------------------------------------------------------------
# Summary (org viewer / admin)
# ---------------------------------------------------------------------------

@router.get("/summary")
async def summary(
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    members = await db.users.find(scoped_members_query(user)).to_list(500)
    consenting = [member for member in members if member.get("share_aggregates")]
    allowed = [str(member["_id"]) for member in consenting]
    runs = await db.footprint_runs.find({"user_id": {"$in": allowed}}).to_list(500)
    assignments = await db.user_recommendations.find({"user_id": {"$in": allowed}}).to_list(500)
    regions = []
    for key in ("mixed", "renewable_heavy"):
        regional_runs = [run for run in runs if run.get("region") == key]
        regions.append({
            "region": key,
            "averageKg": round(sum(run["predicted_kg"] for run in regional_runs) / len(regional_runs)) if regional_runs else 0,
        })
    return {
        "organizationId": user.get("organization_id"),
        "sharedUsers": len(consenting),
        "regions": regions,
        "countries": dict(Counter(member.get("country") or "unspecified" for member in consenting)),
        "completion": {
            "assigned": len(assignments),
            "completed": len([item for item in assignments if item.get("status") == "completed"]),
            "verified": len([item for item in assignments if item.get("verification_status") == "verified"]),
        },
        "disclaimer": "Only users who opted into aggregate sharing are included; no individual records are exposed.",
    }


@router.get("/contributors")
async def contributors(
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    country: str | None = None,
    region: str | None = None,
) -> dict[str, Any]:
    members = await db.users.find(scoped_members_query(user)).to_list(500)
    scoped = [
        member for member in members
        if member.get("share_aggregates") and (not country or member.get("country") == country)
    ]
    allowed = [str(member["_id"]) for member in scoped]
    run_query: dict[str, Any] = {"user_id": {"$in": allowed}}
    if region:
        run_query["region"] = region
    runs = await db.footprint_runs.find(run_query).to_list(2_000)
    return {
        "countries": sorted({member.get("country") for member in members if member.get("share_aggregates") and member.get("country")}),
        "selectedCountry": country,
        "selectedRegion": region,
        "regions": [{"region": key, "value": len([run for run in runs if run.get("region") == key])} for key in ("mixed", "renewable_heavy")],
        "countryCounts": [{"country": key, "value": value} for key, value in Counter(member.get("country") or "Unspecified" for member in scoped).most_common()],
        "disclaimer": "Filters operate on consented aggregate records only. No individual history is exposed.",
    }


@router.get("/summaries")
async def organization_summaries(
    user: Annotated[dict[str, Any], Depends(require_roles("org_admin", "super_admin"))],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> list[dict[str, Any]]:
    members = await db.users.find(scoped_members_query(user), {"organization_id": 1, "share_aggregates": 1}).to_list(500)
    groups: dict[str, dict[str, int]] = {}
    for member in members:
        organization_id = member.get("organization_id") or "Unassigned"
        current = groups.setdefault(organization_id, {"members": 0, "consentingMembers": 0})
        current["members"] += 1
        current["consentingMembers"] += int(bool(member.get("share_aggregates")))
    return [{"organizationId": organization_id, **counts} for organization_id, counts in sorted(groups.items(), key=lambda item: item[1]["consentingMembers"], reverse=True)]


@router.get("/quests")
async def quests(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    country: str | None = None,
) -> dict[str, Any]:
    members = await db.users.find({"share_aggregates": True}).to_list(500)
    eligible = [member for member in members if not country or member.get("country") == country]
    member_ids = [str(member["_id"]) for member in eligible]
    runs = await db.footprint_runs.find({"user_id": {"$in": member_ids}}).to_list(2_000)
    completed = await db.user_recommendations.find({"user_id": {"$in": member_ids}, "status": "completed", "verification_status": "verified"}).to_list(2_000)
    score = lambda uid: len([run for run in runs if run["user_id"] == uid]) * 120 + len([item for item in completed if item["user_id"] == uid]) * 250
    own_score = score(str(user["_id"]))
    rank = sorted([score(str(member["_id"])) for member in eligible], reverse=True).index(own_score) + 1 if any(str(member["_id"]) == str(user["_id"]) for member in eligible) else None
    countries = sorted({member.get("country") for member in members if member.get("country")})
    leaderboard = [
        {
            "country": item,
            "score": sum(score(str(member["_id"])) for member in members if member.get("country") == item),
            "participants": len([member for member in members if member.get("country") == item]),
        }
        for item in countries if not country or item == country
    ]
    return {
        "rank": rank,
        "participantCount": len(eligible),
        "country": country,
        "countries": countries,
        "leaderboard": sorted(leaderboard, key=lambda item: item["score"], reverse=True),
        "disclaimer": "Rank and leaderboard cards use consented aggregate participation only. No individual member names or private activity histories are displayed.",
    }
