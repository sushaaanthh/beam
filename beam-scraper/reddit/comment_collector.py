"""Nested comment collection for a single post.

Walks PRAW's comment forest depth-first, replacing "MoreComments" stubs
so replies are included, and records each comment's nesting depth.
Deleted/removed bodies are flagged by the parser, never silently dropped.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import praw

from reddit.rate_limit import RateLimitExceeded, RateLimiter
from reddit.schemas import CommentRecord, ParseError, parse_comment

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CommentBatch:
    subreddit: str
    post_id: str
    requested: int
    records: list[CommentRecord] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)


class CommentCollector:
    """Collects nested comments for one submission."""

    def __init__(self, reddit: Any, rate_limiter: RateLimiter) -> None:
        self._reddit = reddit
        self._limiter = rate_limiter

    def _fetch_submission(self, subreddit: str, post_id: str):
        return self._limiter.call(
            lambda: self._reddit.submission(id=post_id),
            description=f"submission {post_id}",
        )

    @staticmethod
    def _walk_forest(forest: Any, visit) -> None:
        for top_level in forest:
            stack: list[tuple[Any, int]] = [(top_level, 0)]
            while stack:
                comment, depth = stack.pop()
                if isinstance(comment, praw.models.MoreComments):
                    continue
                visit(comment, depth)
                for reply in reversed(list(getattr(comment, "replies", []) or [])):
                    stack.append((reply, depth + 1))

    def collect(
        self,
        *,
        subreddit: str,
        post_id: str,
        limit: int,
    ) -> CommentBatch:
        batch = CommentBatch(subreddit=subreddit, post_id=post_id, requested=limit)
        if limit <= 0:
            return batch

        submission = self._fetch_submission(subreddit, post_id)

        try:
            self._limiter.call(
                lambda: submission.comments.replace_more(limit=None),
                description=f"replace_more {post_id}",
            )
        except RateLimitExceeded as error:
            logger.warning(
                "comment_forest_partial",
                extra={"post_id": post_id, "error": str(error)},
            )

        def visit(comment: Any, depth: int) -> None:
            if len(batch.records) >= limit:
                return
            try:
                batch.records.append(
                    parse_comment(
                        comment,
                        post_id=post_id,
                        subreddit=subreddit,
                        depth=depth,
                    )
                )
            except ParseError as error:
                batch.parse_errors.append(str(error))
                logger.warning(
                    "comment_parse_skipped",
                    extra={"post_id": post_id, "reason": str(error)},
                )

        try:
            self._walk_forest(submission.comments, visit)
        except Exception as error:  # malformed forest node — keep what we have
            logger.warning(
                "comment_walk_error",
                extra={"post_id": post_id, "error": type(error).__name__},
            )

        logger.info(
            "comments_collected",
            extra={
                "subreddit": subreddit,
                "post_id": post_id,
                "requested": limit,
                "parsed": len(batch.records),
                "parse_errors": len(batch.parse_errors),
            },
        )
        return batch
