from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base

JsonPortableType = JSON().with_variant(JSONB(none_as_null=True), "postgresql")


class RedditCache(Base):
    __tablename__ = "reddit_cache"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # composite: e.g. "{user_id}:{source_type}:{cleaned_identifier}"
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    identifier: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="username")
    data: Mapped[dict[str, object]] = mapped_column(JsonPortableType, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User | None"] = relationship(back_populates="reddit_caches")
