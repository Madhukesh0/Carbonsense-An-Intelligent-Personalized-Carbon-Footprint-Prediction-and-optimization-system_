"""JWT, password, CSRF, and role dependencies for the FastAPI application."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from typing import Annotated, Any, Callable

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from .config import settings
from ..db.mongo import get_database


PASSWORD_HASHER = PasswordHasher()
ACCESS_COOKIE = "cs_access"
REFRESH_COOKIE = "cs_refresh"
CSRF_COOKIE = "cs_csrf"
ROLE_VALUES = {"individual", "org_admin", "super_admin"}


def hash_password(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(password_hash, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False


def session_hash(session_id: str) -> str:
    return sha256(session_id.encode("utf-8")).hexdigest()


def issue_token(*, user_id: str, role: str, session_id: str, token_type: str, expires_in: timedelta) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": user_id,
        "role": role,
        "sid": session_id,
        "typ": token_type,
        "iat": now,
        "exp": now + expires_in,
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session") from error
    if claims.get("typ") != expected_type or not isinstance(claims.get("sub"), str) or not isinstance(claims.get("sid"), str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session type")
    return claims


def new_session_id() -> str:
    return token_urlsafe(32)


def new_csrf_token() -> str:
    return token_urlsafe(32)


def require_csrf(request: Request) -> None:
    cookie = request.cookies.get(CSRF_COOKIE)
    header = request.headers.get("X-CSRF-Token")
    if not cookie or not header or cookie != header:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")


async def get_current_user(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    claims = decode_token(token, "access")
    session = await db.sessions.find_one({
        "session_hash": session_hash(claims["sid"]),
        "user_id": claims["sub"],
        "revoked_at": None,
        "expires_at": {"$gt": datetime.now(UTC)},
    })
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Active session required")
    user = await db.users.find_one({"_id": claims["sub"]}, {"password_hash": 0})
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Active account required")
    return user


def require_roles(*roles: str) -> Callable[..., Any]:
    allowed = set(roles)
    if not allowed <= ROLE_VALUES:
        raise ValueError("Unknown role in authorization dependency")

    async def role_dependency(user: Annotated[dict[str, Any], Depends(get_current_user)]) -> dict[str, Any]:
        if user.get("role") not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return role_dependency
