from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import settings


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Schema-level safety net only; the route enforces the configured limit with 413.
_SCHEMA_TEXT_HARD_MAX = settings.MAX_ANALYSIS_TEXT_CHARS * 4


class AnalysisCreate(BaseModel):
    text: str = Field(min_length=1, max_length=_SCHEMA_TEXT_HARD_MAX)
    source_type: str = Field(default="text", min_length=1, max_length=100)
    title: str | None = Field(default=None, max_length=255)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("text must not be empty or whitespace-only")
        return stripped

    @field_validator("source_type", "title")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class AnalysisCreatedResponse(BaseModel):
    session_id: UUID
    status: AnalysisStatus


class EmotionDistributionItem(BaseModel):
    label: str
    score: float


class PredictionPayload(BaseModel):
    """Model-derived prediction. All fields are null until a real model runs."""

    model_config = ConfigDict(from_attributes=True)

    primary_emotion: str | None = None
    confidence: float | None = None
    emotion_distribution: list[EmotionDistributionItem] | None = None
    inference_time_ms: int | None = None


class BehaviorMetricsPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    positivity_score: float | None = None
    negativity_score: float | None = None
    engagement_score: float | None = None
    linguistic_complexity: float | None = None
    emotional_variance: float | None = None
    posting_frequency: float | None = None


class ExplanationPayload(BaseModel):
    method: str | None = None
    summary: str | None = None
    important_keywords: list[str] | None = None


class ModelInfo(BaseModel):
    model_name: str | None = None
    model_version: str | None = None
    deployed: bool = False
    note: str | None = None


class AnalysisInputMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    char_count: int
    word_count: int
    raw_text: str
    created_at: datetime


class AnalysisSessionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    status: AnalysisStatus
    source_type: str
    title: str | None
    created_at: datetime
    completed_at: datetime | None
    primary_emotion: str | None = None
    confidence: float | None = None
    model_name: str | None = None


class AnalysisDetailResponse(AnalysisSessionSummary):
    input: AnalysisInputMetadata
    prediction: PredictionPayload | None = None
    behavior_metrics: BehaviorMetricsPayload | None = None
    explanation: ExplanationPayload | None = None
    model_info: ModelInfo


class AnalysisListResponse(BaseModel):
    items: list[AnalysisSessionSummary]
    total: int
    page: int
    page_size: int
    pages: int
