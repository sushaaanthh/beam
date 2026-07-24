from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"
    __table_args__ = (
        UniqueConstraint("model_name", "model_version", name="uq_model_versions_model_name_model_version"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    training_dataset: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
