from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.config import settings
from ..core.security import (
    ACCESS_COOKIE,
    CSRF_COOKIE,
    REFRESH_COOKIE,
    decode_token,
    get_current_user,
    hash_password,
    issue_token,
    new_csrf_token,
    new_session_id,
    require_csrf,
    session_hash,
    verify_password,
)
from ..db.mongo import get_database, utc_now
from ..schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


def as_user_response(user: dict[str, Any]) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        role=user["role"],
        organization_id=user.get("organization_id"),
        country=user.get("country"),
        region=user.get("region"),
        share_aggregates=user.get("share_aggregates", False),
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
    )


def set_session_cookies(response: Response, *, user: dict[str, Any], session_id: str, csrf_token: str) -> None:
    access = issue_token(
        user_id=str(user["_id"]), role=user["role"], session_id=session_id, token_type="access", expires_in=timedelta(minutes=settings.access_minutes)
    )
    refresh = issue_token(
        user_id=str(user["_id"]), role=user["role"], session_id=session_id, token_type="refresh", expires_in=timedelta(days=settings.refresh_days)
    )
    cookie_options = {"secure": settings.cookie_secure, "samesite": "lax", "path": "/"}
    response.set_cookie(ACCESS_COOKIE, access, max_age=settings.access_minutes * 60, httponly=True, **cookie_options)
    response.set_cookie(REFRESH_COOKIE, refresh, max_age=settings.refresh_days * 86_400, httponly=True, **cookie_options)
    response.set_cookie(CSRF_COOKIE, csrf_token, max_age=settings.refresh_days * 86_400, httponly=False, **cookie_options)


async def create_session(db: AsyncIOMotorDatabase, user: dict[str, Any]) -> tuple[str, str]:
    session_id = new_session_id()
    csrf_token = new_csrf_token()
    await db.sessions.insert_one({
        "_id": str(uuid4()),
        "session_hash": session_hash(session_id),
        "user_id": str(user["_id"]),
        "created_at": utc_now(),
        "expires_at": datetime.now(UTC) + timedelta(days=settings.refresh_days),
        "revoked_at": None,
    })
    return session_id, csrf_token


@router.post("/register", response_model=AuthResponse, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, response: Response, db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> AuthResponse:
    if await db.users.find_one({"email": payload.email}, {"_id": 1}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account already exists for this email")
    requested_organization = None
    if payload.organization_id:
        requested_organization = await db.organizations.find_one({"_id": payload.organization_id})
        if not requested_organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The selected organization could not be found.")
    now = utc_now()
    user = {
        "_id": str(uuid4()),
        "email": payload.email,
        "name": payload.name.strip(),
        "password_hash": hash_password(payload.password),
        "role": "individual",
        "organization_id": None,
        "country": payload.country.strip() if payload.country else None,
        "region": payload.region,
        "share_aggregates": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_signed_in": now,
    }
    await db.users.insert_one(user)
    if requested_organization:
        await db.organization_join_requests.insert_one({
            "_id": str(uuid4()),
            "user_id": str(user["_id"]),
            "user_name": user["name"],
            "user_email": user["email"],
            "organization_id": requested_organization["_id"],
            "status": "pending",
            "source": "registration",
            "created_at": now,
            "decided_at": None,
            "decided_by": None,
        })
    session_id, csrf_token = await create_session(db, user)
    set_session_cookies(response, user=user, session_id=session_id, csrf_token=csrf_token)
    return AuthResponse(user=as_user_response(user), csrf_token=csrf_token)


@router.post("/login", response_model=AuthResponse, response_model_by_alias=True)
async def login(payload: LoginRequest, response: Response, db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> AuthResponse:
    user = await db.users.find_one({"email": payload.email})
    if not user or not user.get("is_active", True) or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"last_signed_in": utc_now(), "updated_at": utc_now()}})
    user["last_signed_in"] = utc_now()
    session_id, csrf_token = await create_session(db, user)
    set_session_cookies(response, user=user, session_id=session_id, csrf_token=csrf_token)
    return AuthResponse(user=as_user_response(user), csrf_token=csrf_token)


@router.get("/me", response_model=UserResponse, response_model_by_alias=True)
async def me(user: Annotated[dict[str, Any], Depends(get_current_user)]) -> UserResponse:
    return as_user_response(user)


@router.post("/refresh", response_model=AuthResponse, response_model_by_alias=True)
async def refresh(request: Request, response: Response, db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> AuthResponse:
    require_csrf(request)
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session required")
    claims = decode_token(token, "refresh")
    session = await db.sessions.find_one({"session_hash": session_hash(claims["sid"]), "revoked_at": None})
    user = await db.users.find_one({"_id": claims["sub"]})
    if not session or not user or not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session is not active")
    await db.sessions.update_one({"_id": session["_id"]}, {"$set": {"revoked_at": utc_now()}})
    session_id, csrf_token = await create_session(db, user)
    set_session_cookies(response, user=user, session_id=session_id, csrf_token=csrf_token)
    return AuthResponse(user=as_user_response(user), csrf_token=csrf_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> Response:
    require_csrf(request)
    token = request.cookies.get(ACCESS_COOKIE)
    if token:
        claims = decode_token(token, "access")
        await db.sessions.update_one({"session_hash": session_hash(claims["sid"]), "user_id": str(user["_id"])}, {"$set": {"revoked_at": utc_now()}})
    for cookie in (ACCESS_COOKIE, REFRESH_COOKIE, CSRF_COOKIE):
        response.delete_cookie(cookie, path="/", secure=settings.cookie_secure, samesite="lax")
    return response
