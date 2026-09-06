from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ActivityCreateRequest(BaseModel):
    category: Literal["transport", "electricity", "diet", "fuel"]
    activity_date: datetime
    quantity: int = Field(gt=0)
    unit: str = Field(min_length=1, max_length=32)
    co2_kg: int = Field(ge=0)
    notes: str | None = Field(default=None, max_length=500)


class GoalCreateRequest(BaseModel):
    baseline_kg: int = Field(gt=0)
    target_kg: int = Field(gt=0)
    deadline: datetime


class RecommendationAcceptRequest(BaseModel):
    recommendation_key: str = Field(min_length=1, max_length=120)


class RecommendationCompleteRequest(BaseModel):
    self_reported_change_note: str | None = Field(default=None, max_length=500)


class RecommendationAssignRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    recommendation_key: str = Field(min_length=1, max_length=120)


class ReportCreateRequest(BaseModel):
    category: Literal["data_question", "privacy", "recommendation", "technical", "other"]
    details: str = Field(min_length=10, max_length=2000)


class ReportStatusRequest(BaseModel):
    status: Literal["open", "in_review", "resolved", "dismissed"]
