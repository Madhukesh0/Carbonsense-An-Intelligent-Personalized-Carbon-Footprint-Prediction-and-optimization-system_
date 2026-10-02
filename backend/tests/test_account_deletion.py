"""Behavioral tests for self-service account deletion (DELETE /profile).

Follows the same in-memory substitution approach as test_auth_behavior.py: the
production route function runs against a fake database and never touches Atlas.
"""

from __future__ import annotations

import copy
import unittest
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from fastapi import HTTPException, Response
from starlette.requests import Request

from backend.app.core.security import CSRF_COOKIE, hash_password, require_roles
from backend.app.db.mongo import utc_now
from backend.app.routers.profile import delete_account
from backend.app.schemas.governance import AccountDeleteRequest

PASSWORD = "SecurePass1234"


def request_with_csrf() -> Request:
    return Request({
        "type": "http",
        "method": "DELETE",
        "scheme": "http",
        "path": "/api/v1/profile",
        "query_string": b"",
        "headers": [
            (b"cookie", f"{CSRF_COOKIE}=csrf-token".encode()),
            (b"x-csrf-token", b"csrf-token"),
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    })


def matches(document: dict, query: dict) -> bool:
    for key, expected in query.items():
        actual = document.get(key)
        if isinstance(expected, dict):
            if "$gt" in expected and not (actual is not None and actual > expected["$gt"]):
                return False
            if "$ne" in expected and not (actual != expected["$ne"]):
                return False
        elif actual != expected:
            return False
    return True


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict] = []

    def _matching(self, query: dict) -> list[dict]:
        return [document for document in self.documents if matches(document, query)]

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

    async def update_many(self, query: dict, update: dict):
        matched = self._matching(query)
        for document in matched:
            if "$set" in update:
                document.update(copy.deepcopy(update["$set"]))
        return SimpleNamespace(matched_count=len(matched), modified_count=len(matched))

    async def delete_one(self, query: dict):
        for index, document in enumerate(self.documents):
            if matches(document, query):
                del self.documents[index]
                return SimpleNamespace(deleted_count=1)
        return SimpleNamespace(deleted_count=0)

    async def delete_many(self, query: dict):
        matched = self._matching(query)
        self.documents = [document for document in self.documents if not matches(document, query)]
        return SimpleNamespace(deleted_count=len(matched))

    async def count_documents(self, query: dict) -> int:
        return len(self._matching(query))


class FakeDatabase:
    def __init__(self) -> None:
        self._collections: dict[str, FakeCollection] = {}

    def __getattr__(self, name: str) -> FakeCollection:
        collection = self._collections.setdefault(name, FakeCollection())
        object.__setattr__(self, name, collection)
        return collection

    def documents_of(self, name: str) -> list[dict]:
        return getattr(self, name).documents


def seed_user(user_id: str, *, role: str, organization_id: str | None = None, email: str | None = None) -> dict:
    now = utc_now()
    return {
        "_id": user_id,
        "email": email or f"{user_id}@example.invalid",
        "name": f"Member {user_id}",
        "password_hash": hash_password(PASSWORD),
        "role": role,
        "organization_id": organization_id,
        "share_aggregates": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }


class AccountDeletionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.db = FakeDatabase()
        self.request = request_with_csrf()

    async def delete(self, user: dict, password: str = PASSWORD) -> Response:
        response = Response()
        result = await delete_account(AccountDeleteRequest(password=password), self.request, response, user, self.db)
        assert result is response
        return response

    async def test_wrong_password_is_rejected_and_account_survives(self) -> None:
        user = seed_user("user-1", role="individual")
        await self.db.users.insert_one(user)
        with self.assertRaises(HTTPException) as rejected:
            await self.delete(user, password="WrongPass1234")
        self.assertEqual(rejected.exception.status_code, 400)
        self.assertEqual(len(self.db.users.documents), 1)

    async def test_super_admin_is_not_allowed_to_self_delete(self) -> None:
        super_admin = seed_user("root-1", role="super_admin")
        role_dependency = require_roles("individual", "org_admin")
        with self.assertRaises(HTTPException) as forbidden:
            await role_dependency(super_admin)
        self.assertEqual(forbidden.exception.status_code, 403)

    async def test_individual_deletion_removes_personal_data_and_leaves_the_organization(self) -> None:
        user = seed_user("user-1", role="individual", organization_id="org-1")
        other = seed_user("user-2", role="individual", organization_id="org-1")
        for document in (user, other):
            await self.db.users.insert_one(document)
        await self.db.organizations.insert_one({"_id": "org-1", "name": "Green Horizon Collective", "member_count": 2})
        await self.db.sessions.insert_one({"_id": "s1", "user_id": "user-1", "session_hash": "h1", "revoked_at": None, "expires_at": datetime.now(UTC) + timedelta(days=1)})
        for collection, document in {
            "login_events": {"_id": "l1", "user_id": "user-1"},
            "footprint_runs": {"_id": "f1", "user_id": "user-1", "predicted_kg": 120},
            "activity_ledger": {"_id": "a1", "user_id": "user-1"},
            "carbon_goals": {"_id": "g1", "user_id": "user-1"},
            "user_recommendations": {"_id": "r1", "user_id": "user-1"},
            "organization_join_requests": {"_id": "j1", "user_id": "user-1", "organization_id": "org-1"},
            "organization_invitations": {"_id": "i1", "user_id": "user-1", "organization_id": "org-1"},
            "reminders": {"_id": "m1", "user_id": "user-1", "organization_id": "org-1"},
        }.items():
            await getattr(self.db, collection).insert_one(document)
        await self.db.report_requests.insert_one({"_id": "rep1", "user_id": "user-1", "organization_id": "org-1", "assigned_to_user_id": "user-2"})
        await self.db.report_requests.insert_one({"_id": "rep2", "user_id": "user-2", "organization_id": "org-1", "assigned_to_user_id": "user-1"})

        response = await self.delete(user)

        self.assertEqual([document["_id"] for document in self.db.users.documents], ["user-2"])
        self.assertEqual(self.db.organizations.documents[0]["member_count"], 1)
        for collection in ("sessions", "login_events", "footprint_runs", "activity_ledger", "carbon_goals", "user_recommendations", "organization_join_requests", "organization_invitations", "reminders"):
            self.assertEqual(self.db.documents_of(collection), [], f"{collection} should be empty for the deleted user")
        remaining_reports = self.db.report_requests.documents
        self.assertEqual([report["_id"] for report in remaining_reports], ["rep2"])
        self.assertIsNone(remaining_reports[0]["assigned_to_user_id"])
        audits = self.db.governance_audit_logs.documents
        self.assertEqual(len(audits), 1)
        self.assertEqual(audits[0]["action"], "delete_account")
        self.assertEqual(audits[0]["actor_user_id"], "user-1")
        cookies = response.headers.getlist("set-cookie")
        self.assertTrue(any(cookie.split("=")[0] == "cs_access" for cookie in cookies))
        self.assertTrue(any(cookie.split("=")[0] == "cs_refresh" for cookie in cookies))
        self.assertTrue(any(cookie.split("=")[0] == "cs_csrf" for cookie in cookies))

    async def test_org_admin_with_other_members_is_blocked(self) -> None:
        admin = seed_user("admin-1", role="org_admin", organization_id="org-1")
        member = seed_user("user-1", role="individual", organization_id="org-1")
        for document in (admin, member):
            await self.db.users.insert_one(document)
        await self.db.organizations.insert_one({"_id": "org-1", "name": "Green Horizon Collective", "member_count": 2})

        with self.assertRaises(HTTPException) as blocked:
            await self.delete(admin)

        self.assertEqual(blocked.exception.status_code, 409)
        self.assertEqual(len(self.db.users.documents), 2)
        self.assertEqual(len(self.db.organizations.documents), 1)

    async def test_last_org_admin_deletion_retires_the_organization(self) -> None:
        admin = seed_user("admin-1", role="org_admin", organization_id="org-1")
        await self.db.users.insert_one(admin)
        await self.db.organizations.insert_one({"_id": "org-1", "name": "Green Horizon Collective", "member_count": 1})
        for collection, document in {
            "organization_join_requests": {"_id": "j1", "user_id": "admin-1", "organization_id": "org-1"},
            "organization_invitations": {"_id": "i1", "user_id": "invited-1", "organization_id": "org-1"},
            "reminders": {"_id": "m1", "user_id": "admin-1", "organization_id": "org-1"},
            "report_requests": {"_id": "rep1", "user_id": "admin-1", "organization_id": "org-1"},
            "organization_recommendations": {"_id": "or1", "organization_id": "org-1"},
        }.items():
            await getattr(self.db, collection).insert_one(document)

        await self.delete(admin)

        self.assertEqual(self.db.users.documents, [])
        self.assertEqual(self.db.organizations.documents, [])
        for collection in ("organization_join_requests", "organization_invitations", "reminders", "report_requests", "organization_recommendations"):
            self.assertEqual(self.db.documents_of(collection), [], f"{collection} should not outlive the organization")
        self.assertEqual(self.db.governance_audit_logs.documents[0]["action"], "delete_account")
