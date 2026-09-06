from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, Field


class OrganizationCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


class OrganizationJoinRequest(BaseModel):
    organization_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        validation_alias=AliasChoices("organization_id", "organizationId"),
    )
    invite_code: str | None = Field(
        default=None,
        min_length=6,
        max_length=32,
        validation_alias=AliasChoices("invite_code", "inviteCode"),
    )

    @property
    def resolver(self) -> str | None:
        return self.organization_id or self.invite_code


class OrganizationJoinDecisionRequest(BaseModel):
    decision: Literal["approved", "rejected"]


class InvitationDecisionRequest(BaseModel):
    decision: Literal["accepted", "declined"]


class InviteIndividualRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)


class ReminderCreateRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=5, max_length=1000)
    reminder_type: Literal["nudge", "deadline", "achievement", "general"] = "general"


class ReminderStatusRequest(BaseModel):
    status: Literal["pending", "acknowledged", "dismissed"]
