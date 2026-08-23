"""Typed records parsed from Reddit objects, plus data-quality handling.

Parsing is a pure layer: it knows nothing about PRAW sessions or the
database. Collectors feed it raw attribute bags (real PRAW objects in
production, mocks in tests) and receive validated records or a raised
`ParseError` for unusable items.

Content policy:
* `[removed]`, `[deleted]` and empty bodies are flagged via `body_status`
  and stored as NULL text — never silently discarded.
* Author names are pseudonymous public handles kept only where Reddit
  itself exposes them; deleted authors become NULL.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

REMOVED_MARKERS = {"[removed]", "[deleted]"}


class BodyStatus(str, Enum):
    AVAILABLE = "available"
    REMOVED = "removed"
    DELETED = "deleted"
    EMPTY = "empty"


class ParseError(Exception):
    """A record is unusable for the research dataset (e.g. missing id)."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _clean_text(value: object) -> str | None:
    """Normalize free text; collapse the API's deletion markers to None."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in REMOVED_MARKERS:
        return None
    return text


def classify_body(raw_body: object) -> tuple[str | None, BodyStatus]:
    text = _clean_text(raw_body)
    raw = str(raw_body or "").strip().lower()
    if text is not None:
        return text, BodyStatus.AVAILABLE
    if raw in REMOVED_MARKERS:
        return None, BodyStatus.REMOVED if raw == "[removed]" else BodyStatus.DELETED
    return None, BodyStatus.EMPTY


def clean_author(raw_author: object) -> str | None:
    """Deleted/suspended authors arrive as '[deleted]' or None."""
    return _clean_text(raw_author)


class PostRecord(BaseModel):
    """Normalized reddit_posts row payload."""

    model_config = ConfigDict(frozen=True)

    reddit_post_id: str = Field(min_length=1, max_length=32)
    subreddit: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1)
    body: str | None = None
    body_status: BodyStatus = BodyStatus.EMPTY
    author: str | None = None
    created_utc: datetime
    score: int = 0
    upvote_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    num_comments: int = 0
    url: str | None = None
    permalink: str | None = None
    is_nsfw: bool = False
    is_spoiler: bool = False
    stickied: bool = False
    retrieved_at: datetime = Field(default_factory=utc_now)

    @field_validator("reddit_post_id", "subreddit", "title")
    @classmethod
    def _required_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("required field is empty")
        return cleaned


class CommentRecord(BaseModel):
    """Normalized reddit_comments row payload."""

    model_config = ConfigDict(frozen=True)

    reddit_comment_id: str = Field(min_length=1, max_length=32)
    post_id: str = Field(min_length=1, max_length=32)
    subreddit: str = Field(min_length=1, max_length=100)
    body: str | None = None
    body_status: BodyStatus = BodyStatus.EMPTY
    author: str | None = None
    parent_id: str | None = None
    depth: int = Field(default=0, ge=0)
    created_utc: datetime
    score: int = 0
    retrieved_at: datetime = Field(default_factory=utc_now)

    @field_validator("reddit_comment_id", "post_id", "subreddit")
    @classmethod
    def _required_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("required field is empty")
        return cleaned


# --------------------------------------------------------------------------
# Parsers (attribute-bag based so tests can pass simple mocks)
# --------------------------------------------------------------------------

def parse_submission(submission: object, retrieved_at: datetime | None = None) -> PostRecord:
    reddit_id = getattr(submission, "id", None)
    if not reddit_id or not str(reddit_id).strip():
        raise ParseError("submission has no id")

    title = getattr(submission, "title", None)
    if not title or not str(title).strip():
        raise ParseError(f"submission {reddit_id} has no title")

    body, body_status = classify_body(getattr(submission, "selftext", "") or "")
    created = getattr(submission, "created_utc", None)
    if created is None:
        raise ParseError(f"submission {reddit_id} has no created_utc")

    return PostRecord(
        reddit_post_id=str(reddit_id),
        subreddit=str(getattr(submission, "subreddit", "") or "").removeprefix("r/"),
        title=str(title),
        body=body,
        body_status=body_status,
        author=clean_author(getattr(submission, "author", None)),
        created_utc=datetime.fromtimestamp(float(created), tz=timezone.utc),
        score=int(getattr(submission, "score", 0) or 0),
        upvote_ratio=float(getattr(submission, "upvote_ratio", 0.0) or 0.0),
        num_comments=int(getattr(submission, "num_comments", 0) or 0),
        url=getattr(submission, "url", None),
        permalink=getattr(submission, "permalink", None),
        is_nsfw=bool(getattr(submission, "over_18", False)),
        is_spoiler=bool(getattr(submission, "spoiler", False)),
        stickied=bool(getattr(submission, "stickied", False)),
        retrieved_at=retrieved_at or utc_now(),
    )


def parse_comment(
    comment: object,
    *,
    post_id: str,
    subreddit: str,
    depth: int,
    retrieved_at: datetime | None = None,
) -> CommentRecord:
    reddit_id = getattr(comment, "id", None)
    if not reddit_id or not str(reddit_id).strip():
        raise ParseError("comment has no id")

    # MoreComment objects have no body/created_utc and are expanded by PRAW.
    created = getattr(comment, "created_utc", None)
    if created is None:
        raise ParseError(f"comment {reddit_id} has no created_utc")

    body, body_status = classify_body(getattr(comment, "body", "") or "")

    parent_raw = getattr(comment, "parent_id", None)
    parent_id = str(parent_raw).removeprefix("t1_").removeprefix("t3_") if parent_raw else None

    return CommentRecord(
        reddit_comment_id=str(reddit_id),
        post_id=post_id,
        subreddit=subreddit,
        body=body,
        body_status=body_status,
        author=clean_author(getattr(comment, "author", None)),
        parent_id=parent_id,
        depth=max(0, int(depth)),
        created_utc=datetime.fromtimestamp(float(created), tz=timezone.utc),
        score=int(getattr(comment, "score", 0) or 0),
        retrieved_at=retrieved_at or utc_now(),
    )
