"""SQLAlchemy storage models for collected Reddit research data.

These tables belong to the scraper's own schema (reddit_posts /
reddit_comments) and are intentionally independent from the beam-api
domain tables. Communication with the rest of B.E.A.M. happens through
the database and the typed records in `schemas.py` only.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Portable PK type: real UUIDs on PostgreSQL, 32-char text elsewhere.
# Defaults are uuid4().hex so the value binds cleanly on every dialect.
UuidType = String(32).with_variant(UUID(as_uuid=True), "postgresql")


def new_uuid() -> str:
    return uuid4().hex


class Base(DeclarativeBase):
    pass


class RedditPost(Base):
    __tablename__ = "reddit_posts"

    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=new_uuid)
    reddit_post_id: Mapped[str] = mapped_column(String(32), nullable=False)
    subreddit: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_status: Mapped[str] = mapped_column(String(20), nullable=False, default="empty")
    author: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    upvote_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    num_comments: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    permalink: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_nsfw: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_spoiler: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    stickied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )

    comments: Mapped[list["RedditComment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("reddit_post_id", name="uq_reddit_posts_reddit_post_id"),
        Index("ix_reddit_posts_reddit_post_id", "reddit_post_id"),
        Index("ix_reddit_posts_subreddit_created", "subreddit", "created_utc"),
    )


class RedditComment(Base):
    __tablename__ = "reddit_comments"

    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=new_uuid)
    post_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("reddit_posts.reddit_post_id", ondelete="CASCADE"), nullable=False, index=True
    )
    reddit_comment_id: Mapped[str] = mapped_column(String(32), nullable=False)
    subreddit: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_status: Mapped[str] = mapped_column(String(20), nullable=False, default="empty")
    author: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parent_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )

    post: Mapped["RedditPost"] = relationship(back_populates="comments")

    __table_args__ = (
        UniqueConstraint("reddit_comment_id", name="uq_reddit_comments_reddit_comment_id"),
        Index("ix_reddit_comments_reddit_comment_id", "reddit_comment_id"),
        Index("ix_reddit_comments_subreddit_created", "subreddit", "created_utc"),
    )
