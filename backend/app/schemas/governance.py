from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    country: str | None = Field(default=None, max_length=64)
    region: Literal["mixed", "renewable_heavy"] | None = None
    share_aggregates: bool | None = None


class RoleUpdateRequest(BaseModel):
    role: Literal["individual", "org_admin", "super_admin"]


class ActiveUpdateRequest(BaseModel):
    is_active: bool
