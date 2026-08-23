"""Storage layer: session management + deduplicating persistence.

Upsert semantics:
* new Reddit ID  -> INSERT
* known Reddit ID -> UPDATE mutable metadata only (score, counts, flags,
  body availability); the original `retrieved_at` is preserved and
  `updated_at` is refreshed. Duplicates are never inserted.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from reddit.models import Base, RedditComment, RedditPost
from reddit.schemas import CommentRecord, PostRecord, utc_now

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class StorageStats:
    posts_inserted: int = 0
    posts_updated: int = 0
    comments_inserted: int = 0
    comments_updated: int = 0
    errors: list[str] = field(default_factory=list)

    def merge(self, other: "StorageStats") -> None:
        self.posts_inserted += other.posts_inserted
        self.posts_updated += other.posts_updated
        self.comments_inserted += other.comments_inserted
        self.comments_updated += other.comments_updated
        self.errors.extend(other.errors)


def _make_engine(database_url: str) -> Engine:
    if database_url.startswith("sqlite"):
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        # SQLite ignores FKs unless explicitly enabled per connection.
        from sqlalchemy import event

        @event.listens_for(engine, "connect")
        def _enable_sqlite_fk(dbapi_connection, _record):  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine
    return create_engine(database_url, pool_pre_ping=True)


class Storage:
    """Owns the engine and provides deduplicating save + read-only queries."""

    def __init__(self, database_url: str) -> None:
        self._engine = _make_engine(database_url)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    @property
    def engine(self) -> Engine:
        return self._engine

    def create_schema(self) -> None:
        Base.metadata.create_all(self._engine)

    def session(self) -> Session:
        return self._session_factory()

    # -- Posts ---------------------------------------------------------------

    def save_post(self, session: Session, record: PostRecord) -> str:
        """Insert or update a post. Returns 'inserted' | 'updated' | 'unchanged'."""
        post = session.scalar(
            select(RedditPost).where(RedditPost.reddit_post_id == record.reddit_post_id)
        )

        if post is None:
            session.add(
                RedditPost(
                    reddit_post_id=record.reddit_post_id,
                    subreddit=record.subreddit,
                    title=record.title,
                    body=record.body,
                    body_status=record.body_status.value,
                    author=record.author,
                    created_utc=record.created_utc,
                    score=record.score,
                    upvote_ratio=record.upvote_ratio,
                    num_comments=record.num_comments,
                    url=record.url,
                    permalink=record.permalink,
                    is_nsfw=record.is_nsfw,
                    is_spoiler=record.is_spoiler,
                    stickied=record.stickied,
                    retrieved_at=record.retrieved_at,
                )
            )
            return "inserted"

        changed = (
            post.score != record.score
            or post.num_comments != record.num_comments
            or post.body_status != record.body_status.value
            or (post.body or None) != (record.body or None)
            or post.is_nsfw != record.is_nsfw
            or post.stickied != record.stickied
        )
        # Mutable metadata refresh; first-seen `retrieved_at` is kept.
        post.title = record.title
        post.body = record.body
        post.body_status = record.body_status.value
        post.author = record.author
        post.score = record.score
        post.upvote_ratio = record.upvote_ratio
        post.num_comments = record.num_comments
        post.url = record.url
        post.permalink = record.permalink
        post.is_nsfw = record.is_nsfw
        post.is_spoiler = record.is_spoiler
        post.stickied = record.stickied
        post.updated_at = utc_now()
        return "updated" if changed else "unchanged"

    # -- Comments --------------------------------------------------------------

    def save_comment(self, session: Session, record: CommentRecord) -> str:
        comment = session.scalar(
            select(RedditComment).where(RedditComment.reddit_comment_id == record.reddit_comment_id)
        )
        if comment is None:
            session.add(
                RedditComment(
                    post_id=record.post_id,
                    reddit_comment_id=record.reddit_comment_id,
                    subreddit=record.subreddit,
                    body=record.body,
                    body_status=record.body_status.value,
                    author=record.author,
                    parent_id=record.parent_id,
                    depth=record.depth,
                    created_utc=record.created_utc,
                    score=record.score,
                    retrieved_at=record.retrieved_at,
                )
            )
            return "inserted"

        changed = (
            comment.score != record.score
            or comment.body_status != record.body_status.value
            or (comment.body or None) != (record.body or None)
        )
        comment.body = record.body
        comment.body_status = record.body_status.value
        comment.author = record.author
        comment.score = record.score
        comment.updated_at = utc_now()
        return "updated" if changed else "unchanged"

    # -- Read helpers (used by export utility; strictly read-only) ---------------

    def iter_posts(self, subreddit: str | None = None):
        with self.session() as session:
            stmt = select(RedditPost).order_by(RedditPost.created_utc.desc())
            if subreddit:
                stmt = stmt.where(RedditPost.subreddit == subreddit)
            for row in session.scalars(stmt):
                yield row

    def iter_comments(self, subreddit: str | None = None):
        with self.session() as session:
            stmt = select(RedditComment).order_by(RedditComment.created_utc.desc())
            if subreddit:
                stmt = stmt.where(RedditComment.subreddit == subreddit)
            for row in session.scalars(stmt):
                yield row
