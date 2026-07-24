from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class BehaviorMetric(Base):
    __tablename__ = "behavior_metrics"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    positivity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    negativity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    engagement_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    linguistic_complexity: Mapped[float | None] = mapped_column(Float, nullable=True)
    emotional_variance: Mapped[float | None] = mapped_column(Float, nullable=True)
    posting_frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    session: Mapped["AnalysisSession"] = relationship(back_populates="behavior_metric")
