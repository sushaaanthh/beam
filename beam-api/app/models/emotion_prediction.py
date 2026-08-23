from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base

# Portable JSON: JSONB on PostgreSQL, plain JSON elsewhere (e.g. SQLite tests).
EmotionDistributionType = JSON().with_variant(JSONB(none_as_null=True), "postgresql")


class EmotionPrediction(Base):
    __tablename__ = "emotion_predictions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    primary_emotion: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    inference_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    emotion_distribution: Mapped[list[dict[str, object]] | None] = mapped_column(
        EmotionDistributionType,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    session: Mapped["AnalysisSession"] = relationship(back_populates="prediction")
