"""Behavioral security tests for the clean MongoDB-native FastAPI auth flow.

These tests use a small asynchronous in-memory collection substitute. They execute
the production route and security functions but never connect to Atlas or create
accounts in a real collection.
"""

from __future__ import annotations

import copy
import unittest
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from fastapi import HTTPException, Response
from starlette.requests import Request

from backend.app.core.security import (
    ACCESS_COOKIE,
    CSRF_COOKIE,
    REFRESH_COOKIE,
    get_current_user,
    hash_password,
    issue_token,
    session_hash,
)
from backend.app.db.mongo import utc_now
from backend.app.routers.auth import login, logout, refresh, register
from backend.app.schemas.auth import LoginRequest, RegisterRequest


def request_with_cookies(cookies: dict[str, str], headers: dict[str, str] | None = None) -> Request:
    combined_headers = {"cookie": "; ".join(f"{key}={value}" for key, value in cookies.items()), **(headers or {})}
    return Request({
        "type": "http",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/auth/test",
        "query_string": b"",
        "headers": [(key.lower().encode(), value.encode()) for key, value in combined_headers.items()],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    })


def matches(document: dict, query: dict) -> bool:
    for key, expected in query.items():
        actual = document.get(key)
        if isinstance(expected, dict):
            if "$gt" in expected and not (actual is not None and actual > expected["$gt"]):
                return False
        elif actual != expected:
            return False
    return True


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict] = []

    async def find_one(self, query: dict, projection: dict | None = None):
        for document in self.documents:
            if matches(document, query):
                result = copy.deepcopy(document)
                if projection:
                    for field, included in projection.items():
                        if included == 0:
                            result.pop(field, None)
                return result
        return None

    async def insert_one(self, document: dict):
        self.documents.append(copy.deepcopy(document))
        return SimpleNamespace(inserted_id=document["_id"])

    async def update_one(self, query: dict, update: dict):
        for document in self.documents:
            if matches(document, query):
                if "$set" in update:
                    document.update(copy.deepcopy(update["$set"]))
                if "$inc" in update:
                    for key, amount in update["$inc"].items():
                        document[key] = document.get(key, 0) + amount
                return SimpleNamespace(matched_count=1, modified_count=1)
        return SimpleNamespace(matched_count=0, modified_count=0)


class FakeDatabase:
    def __init__(self) -> None:
        self.users = FakeCollection()
        self.sessions = FakeCollection()
        self.organizations = FakeCollection()


class FastApiNativeAuthBehaviorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.db = FakeDatabase()
        self.payload = RegisterRequest(name="Native Auth Test", email="native-auth-test@example.invalid", password="SecurePass1234")

    async def create_user(self) -> tuple[dict, Response]:
        response = Response()
        await register(self.payload, response, self.db)
        return self.db.users.documents[0], response

    async def test_registration_stores_only_argon2_hash_and_creates_a_session(self) -> None:
        user, response = await self.create_user()
        self.assertNotIn("password", user)
        self.assertTrue(user["password_hash"].startswith("$argon2"))
        self.assertNotEqual(user["password_hash"], self.payload.password)
        self.assertEqual(len(self.db.sessions.documents), 1)
        self.assertNotIn("sid", self.db.sessions.documents[0])
        cookies = response.headers.getlist("set-cookie")
        self.assertTrue(any(f"{ACCESS_COOKIE}=" in cookie and "HttpOnly" in cookie for cookie in cookies))
        self.assertTrue(any(f"{REFRESH_COOKIE}=" in cookie and "HttpOnly" in cookie for cookie in cookies))
        self.assertTrue(any(f"{CSRF_COOKIE}=" in cookie and "HttpOnly" not in cookie for cookie in cookies))

    async def test_registration_can_attach_a_member_to_an_existing_organization(self) -> None:
        org = {"_id": "org-1", "name": "Green Horizon Collective", "invite_code": "join-code", "member_count": 1}
        await self.db.organizations.insert_one(org)

        joined = await register(RegisterRequest(
            email="aisha@example.invalid",
            password="SecurePass1234",
            name="Aisha Patel",
            country="India",
            organization_id="org-1",
        ), Response(), self.db)

        self.assertEqual(joined.user.organization_id, "org-1")
        self.assertEqual(self.db.users.documents[-1]["organization_id"], "org-1")
        updated_org = self.db.organizations.documents[0]
        self.assertEqual(updated_org["member_count"], 2)

    async def test_duplicate_email_and_wrong_password_are_rejected(self) -> None:
        await self.create_user()
        with self.assertRaises(HTTPException) as duplicate:
            await register(self.payload, Response(), self.db)
        self.assertEqual(duplicate.exception.status_code, 409)

        with self.assertRaises(HTTPException) as wrong_password:
            await login(LoginRequest(email=self.payload.email, password="WrongPass1234"), Response(), self.db)
        self.assertEqual(wrong_password.exception.status_code, 401)

        login_response = Response()
        signed_in = await login(LoginRequest(email=self.payload.email, password=self.payload.password), login_response, self.db)
        self.assertEqual(signed_in.user.email, self.payload.email)
        self.assertEqual(len(self.db.sessions.documents), 2)
        self.assertTrue(any(f"{ACCESS_COOKIE}=" in cookie for cookie in login_response.headers.getlist("set-cookie")))

    async def test_access_token_requires_a_live_unrevoked_session_and_active_user(self) -> None:
        user, _ = await self.create_user()
        session_id = "test-session-id"
        self.db.sessions.documents.append({
            "_id": "session-1",
            "session_hash": session_hash(session_id),
            "user_id": user["_id"],
            "revoked_at": None,
            "expires_at": datetime.now(UTC) + timedelta(days=1),
        })
        token = issue_token(user_id=user["_id"], role=user["role"], session_id=session_id, token_type="access", expires_in=timedelta(minutes=5))
        request = request_with_cookies({ACCESS_COOKIE: token})
        current = await get_current_user(request, self.db)
        self.assertEqual(current["_id"], user["_id"])

        self.db.sessions.documents[-1]["revoked_at"] = utc_now()
        with self.assertRaises(HTTPException) as revoked:
            await get_current_user(request, self.db)
        self.assertEqual(revoked.exception.status_code, 401)

        self.db.sessions.documents[-1]["revoked_at"] = None
        self.db.users.documents[0]["is_active"] = False
        with self.assertRaises(HTTPException) as disabled:
            await get_current_user(request, self.db)
        self.assertEqual(disabled.exception.status_code, 401)

    async def test_logout_revokes_the_matching_session_and_refresh_requires_csrf(self) -> None:
        user, _ = await self.create_user()
        session_id = "logout-session-id"
        self.db.sessions.documents.append({
            "_id": "session-logout",
            "session_hash": session_hash(session_id),
            "user_id": user["_id"],
            "revoked_at": None,
            "expires_at": datetime.now(UTC) + timedelta(days=1),
        })
        access = issue_token(user_id=user["_id"], role=user["role"], session_id=session_id, token_type="access", expires_in=timedelta(minutes=5))
        refresh_token = issue_token(user_id=user["_id"], role=user["role"], session_id=session_id, token_type="refresh", expires_in=timedelta(days=1))
        request = request_with_cookies({ACCESS_COOKIE: access, CSRF_COOKIE: "csrf-token"}, {"X-CSRF-Token": "csrf-token"})
        await logout(request, Response(), user, self.db)
        self.assertIsNotNone(self.db.sessions.documents[-1]["revoked_at"])

        csrf_missing = request_with_cookies({REFRESH_COOKIE: refresh_token, CSRF_COOKIE: "csrf-token"})
        with self.assertRaises(HTTPException) as missing_csrf:
            await refresh(csrf_missing, Response(), self.db)
        self.assertEqual(missing_csrf.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
