from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, field_validator


Role = Literal["individual", "org_admin", "super_admin"]


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=12, max_length=128)
    name: str = Field(min_length=1, max_length=160)
    country: str | None = Field(default=None, max_length=64)
    region: Literal["mixed", "renewable_heavy"] | None = None
    organization_id: str | None = Field(default=None, max_length=64, validation_alias=AliasChoices("organization_id", "organizationId"))

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("A valid email address is required")
        return normalized

    @field_validator("password")
    @classmethod
    def require_strong_password(cls, value: str) -> str:
        if not (any(character.islower() for character in value) and any(character.isupper() for character in value) and any(character.isdigit() for character in value)):
            raise ValueError("Use at least 12 characters with uppercase, lowercase, and a number")
        return value


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: Role
    organization_id: str | None = Field(default=None, serialization_alias="organizationId")
    country: str | None = None
    region: str | None = None
    share_aggregates: bool = Field(serialization_alias="shareAggregates")
    is_active: bool = Field(serialization_alias="isActive")
    created_at: datetime = Field(serialization_alias="createdAt")


class AuthResponse(BaseModel):
    user: UserResponse
    csrf_token: str
