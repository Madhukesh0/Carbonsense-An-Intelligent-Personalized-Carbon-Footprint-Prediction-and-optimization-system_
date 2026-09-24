from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ProfileUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    country: str | None = Field(default=None, max_length=64)
    region: Literal["mixed", "renewable_heavy"] | None = None
    share_aggregates: bool | None = None


class RoleUpdateRequest(BaseModel):
    role: Literal["individual", "org_admin", "super_admin"]


class ActiveUpdateRequest(BaseModel):
    is_active: bool


class PasswordResetRequest(BaseModel):
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def require_strong_password(cls, value: str) -> str:
        if not (any(character.islower() for character in value) and any(character.isupper() for character in value) and any(character.isdigit() for character in value)):
            raise ValueError("Use at least 12 characters with uppercase, lowercase, and a number")
        return value
