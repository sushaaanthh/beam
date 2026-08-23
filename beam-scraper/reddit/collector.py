"""Collection orchestrator: coordinates posts, comments, storage and stats.

Produces a structured ScrapeSummary for every run — the single object the
CLI scripts log on completion. One malformed record never aborts a job.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from reddit.comment_collector import CommentCollector
from reddit.post_collector import PostCollector
from reddit.rate_limit import RateLimiter
from reddit.schemas import CommentRecord, PostRecord
from reddit.storage import Storage

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ScrapeSummary:
    subreddit: str
    sort: str = "new"
    time_filter: str = "month"
    posts_requested: int = 0
    posts_discovered: int = 0
    posts_inserted: int = 0
    posts_updated: int = 0
    duplicate_posts: int = 0
    comments_requested: int = 0
    comments_discovered: int = 0
    comments_inserted: int = 0
    comments_updated: int = 0
    duplicate_comments: int = 0
    parse_errors: list[str] = field(default_factory=list)
    storage_errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    status: str = "running"
    started_at: float = field(default_factory=time.monotonic, repr=False)

    @property
    def duplicates(self) -> int:
        """Aggregate duplicate count across posts and comments."""
        return self.duplicate_posts + self.duplicate_comments

    def finish(self) -> "ScrapeSummary":
        self.duration_seconds = round(time.monotonic() - self.started_at, 3)
        if self.status == "running":
            error_count = len(self.parse_errors) + len(self.storage_errors)
            self.status = "completed_with_errors" if error_count else "completed"
        return self


class SubredditCollector:
    """High-level entry point used by the CLI scripts."""

    def __init__(
        self,
        reddit: Any,
        storage: Storage,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        limiter = rate_limiter or RateLimiter()
        self._posts = PostCollector(reddit, limiter)
        self._comments = CommentCollector(reddit, limiter)
        self._storage = storage

    # -- persistence -----------------------------------------------------------

    def _persist_posts(self, session, records: list[PostRecord], summary: ScrapeSummary) -> None:
        for record in records:
            try:
                # Savepoint per record: one failure never rolls back the batch.
                with session.begin_nested():
                    action = self._storage.save_post(session, record)
            except SQLAlchemyError as error:
                message = f"post {record.reddit_post_id}: {type(error).__name__}"
                summary.storage_errors.append(message)
                logger.error("post_storage_error", extra={"detail": message})
                continue

            if action == "inserted":
                summary.posts_inserted += 1
            elif action == "updated":
                summary.posts_updated += 1
                summary.duplicate_posts += 1
            else:
                summary.duplicate_posts += 1

    def _persist_comments(self, session, records: list[CommentRecord], summary: ScrapeSummary) -> None:
        for record in records:
            try:
                with session.begin_nested():
                    action = self._storage.save_comment(session, record)
            except SQLAlchemyError as error:
                message = f"comment {record.reddit_comment_id}: {type(error).__name__}"
                summary.storage_errors.append(message)
                logger.error("comment_storage_error", extra={"detail": message})
                continue

            if action == "inserted":
                summary.comments_inserted += 1
            elif action == "updated":
                summary.comments_updated += 1
                summary.duplicate_comments += 1
            else:
                summary.duplicate_comments += 1

    # -- public API --------------------------------------------------------------

    def collect_subreddit(
        self,
        *,
        subreddit: str,
        limit: int,
        sort: str = "new",
        time_filter: str = "month",
        include_comments: bool = True,
        comment_limit: int = 200,
    ) -> ScrapeSummary:
        summary = ScrapeSummary(
            subreddit=subreddit,
            sort=sort,
            time_filter=time_filter,
            posts_requested=limit,
        )

        logger.info(
            "scrape_start",
            extra={
                "subreddit": subreddit,
                "sort": sort,
                "time_filter": time_filter,
                "limit": limit,
                "include_comments": include_comments,
            },
        )

        try:
            batch = self._posts.collect(
                subreddit=subreddit,
                limit=limit,
                sort=sort,
                time_filter=time_filter,
            )
        except Exception as error:  # listing failure ends this subreddit's run
            summary.parse_errors.append(f"listing failed: {error}")
            summary.status = "failed"
            logger.error(
                "subreddit_run_failed",
                extra={
                    "subreddit": subreddit,
                    "completion_status": "failed",
                    "error": type(error).__name__,
                },
            )
            return summary.finish()

        summary.posts_discovered = len(batch.records)
        summary.parse_errors.extend(batch.parse_errors)

        with self._storage.session() as session:
            self._persist_posts(session, batch.records, summary)
            session.commit()

        if include_comments:
            for post in batch.records:
                comment_batch = self._comments.collect(
                    subreddit=post.subreddit,
                    post_id=post.reddit_post_id,
                    limit=comment_limit,
                )
                summary.comments_requested += comment_batch.requested
                summary.comments_discovered += len(comment_batch.records)
                summary.parse_errors.extend(comment_batch.parse_errors)
                with self._storage.session() as session:
                    self._persist_comments(session, comment_batch.records, summary)
                    session.commit()

        logger.info(
            "scrape_complete",
            extra={
                "subreddit": summary.subreddit,
                "sort": summary.sort,
                "requested_limit": summary.posts_requested,
                "posts_discovered": summary.posts_discovered,
                "posts_inserted": summary.posts_inserted,
                "posts_updated": summary.posts_updated,
                "duplicate_posts": summary.duplicate_posts,
                "comments_requested": summary.comments_requested,
                "comments_discovered": summary.comments_discovered,
                "comments_inserted": summary.comments_inserted,
                "duplicate_comments": summary.duplicate_comments,
                "errors": len(summary.parse_errors) + len(summary.storage_errors),
                "duration_seconds": summary.duration_seconds,
                "completion_status": summary.status,
            },
        )
        return summary.finish()

    def collect_single_post(
        self,
        *,
        subreddit: str,
        post_id: str,
        comment_limit: int = 200,
    ) -> ScrapeSummary:
        summary = ScrapeSummary(subreddit=subreddit, sort="post", time_filter="n/a")

        logger.info(
            "scrape_start",
            extra={
                "subreddit": subreddit,
                "sort": "post",
                "requested_limit": comment_limit,
                "post_id": post_id,
            },
        )

        # The parent post row must exist first (comments FK onto it).
        from reddit.schemas import parse_submission

        try:
            submission = self._posts.fetch_submission(subreddit, post_id)
            record = parse_submission(submission)
            if not record.subreddit:
                record = record.model_copy(update={"subreddit": subreddit})
            with self._storage.session() as session:
                action = self._storage.save_post(session, record)
                if action == "inserted":
                    summary.posts_inserted += 1
                else:
                    summary.duplicate_posts += 1
                session.commit()
        except Exception as error:
            message = f"parent post {post_id} unavailable: {error}"
            summary.parse_errors.append(message)
            summary.status = "failed"
            logger.error(
                "parent_post_unavailable",
                extra={"post_id": post_id, "completion_status": "failed"},
            )
            return summary.finish()

        summary.posts_discovered = 1

        comment_batch = self._comments.collect(
            subreddit=record.subreddit,
            post_id=post_id,
            limit=comment_limit,
        )
        summary.comments_requested = comment_batch.requested
        summary.comments_discovered = len(comment_batch.records)
        summary.parse_errors.extend(comment_batch.parse_errors)

        with self._storage.session() as session:
            self._persist_comments(session, comment_batch.records, summary)
            session.commit()

        logger.info(
            "scrape_complete",
            extra={
                "subreddit": summary.subreddit,
                "sort": "post",
                "post_id": post_id,
                "posts_discovered": summary.posts_discovered,
                "posts_inserted": summary.posts_inserted,
                "duplicate_posts": summary.duplicate_posts,
                "comments_discovered": summary.comments_discovered,
                "comments_inserted": summary.comments_inserted,
                "duplicate_comments": summary.duplicate_comments,
                "errors": len(summary.parse_errors) + len(summary.storage_errors),
                "duration_seconds": summary.duration_seconds,
                "completion_status": summary.status,
            },
        )
        return summary.finish()
