"""Async MongoDB lifecycle and required collection indexes."""

from __future__ import annotations

from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..core.config import settings


_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_mongo() -> None:
    global _client, _database
    if _database is not None:
        return
    _client = AsyncIOMotorClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=30_000,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    _database = _client[settings.mongodb_database]
    await _database.command("ping")
    await ensure_indexes(_database)


async def close_mongo() -> None:
    global _client, _database
    if _client is not None:
        _client.close()
    _client = None
    _database = None


def get_database() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("MongoDB has not been initialized")
    return _database


async def ensure_indexes(database: AsyncIOMotorDatabase) -> None:
    await database.users.create_index("email", unique=True)
    await database.users.create_index("legacy_id", unique=True, sparse=True)
    await database.sessions.create_index("expires_at", expireAfterSeconds=0)
    await database.sessions.create_index("session_hash", unique=True)
    await database.footprint_runs.create_index([("user_id", 1), ("created_at", -1)])
    await database.footprint_runs.create_index([("organization_id", 1), ("created_at", -1)])
    await database.activity_ledger.create_index([("user_id", 1), ("activity_date", -1)])
    await database.carbon_goals.create_index([("user_id", 1), ("status", 1)])
    await database.user_recommendations.create_index([("user_id", 1), ("status", 1)])
    await database.report_requests.create_index([("organization_id", 1), ("status", 1)])
    await database.governance_audit_logs.create_index([("organization_id", 1), ("created_at", -1)])


def utc_now() -> datetime:
    return datetime.now(UTC)
