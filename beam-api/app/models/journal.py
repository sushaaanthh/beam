from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Float, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base

JsonPortableType = JSON().with_variant(JSONB(none_as_null=True), "postgresql")


class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="Daily Journal Entry")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mood_emoji: Mapped[str | None] = mapped_column(String(50), nullable=True, default="")
    primary_emotion: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    valence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    arousal: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reflection_score: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    reflection_depth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    emotional_clarity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vocab_richness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_insight: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifestyle_prescription: Mapped[dict[str, object] | None] = mapped_column(JsonPortableType, nullable=True)
    tokens: Mapped[list[dict[str, object]] | None] = mapped_column(JsonPortableType, nullable=True)
    trigger_words: Mapped[list[str] | None] = mapped_column(JsonPortableType, nullable=True)
    distribution: Mapped[list[dict[str, object]] | None] = mapped_column(JsonPortableType, nullable=True)
    signals: Mapped[list[str] | None] = mapped_column(JsonPortableType, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    user: Mapped["User | None"] = relationship(back_populates="journals")
