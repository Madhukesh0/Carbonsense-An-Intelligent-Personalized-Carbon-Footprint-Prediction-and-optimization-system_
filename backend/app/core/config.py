"""Runtime configuration for the FastAPI migration target."""

from __future__ import annotations

import os
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env", override=False)


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    mongodb_database: str
    jwt_secret: str
    access_minutes: int
    refresh_days: int
    cookie_secure: bool
    frontend_origins: tuple[str, ...]


def get_settings() -> Settings:
    mongo_uri = os.getenv("MONGODB_URI", "")
    jwt_secret = os.getenv("JWT_SECRET", "")
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI is required for the FastAPI backend")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET is required for the FastAPI backend")
    origins = tuple(origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip())
    return Settings(
        mongodb_uri=mongo_uri,
        mongodb_database=os.getenv("MONGODB_DATABASE", "carbonsense_fastapi"),
        jwt_secret=jwt_secret,
        access_minutes=int(os.getenv("JWT_ACCESS_MINUTES", "15")),
        refresh_days=int(os.getenv("JWT_REFRESH_DAYS", "30")),
        cookie_secure=_bool("COOKIE_SECURE", True),
        frontend_origins=origins,
    )


settings = get_settings()
