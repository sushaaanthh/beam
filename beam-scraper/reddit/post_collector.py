"""Post listing collection for one subreddit.

Supports hot / new / top / rising listings, with time filters for `top`,
configurable limits and conservative pacing via the shared RateLimiter.

Malformed submissions never abort the run: they are logged and counted,
and healthy records are still returned.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from reddit.rate_limit import RateLimitExceeded, RateLimiter
from reddit.schemas import ParseError, PostRecord, parse_submission

logger = logging.getLogger(__name__)

SORT_MODES = ("hot", "new", "top", "rising")
TIME_FILTERS = ("day", "week", "month", "year", "all")


@dataclass(slots=True)
class PostBatch:
    subreddit: str
    sort: str
    time_filter: str
    requested: int
    records: list[PostRecord] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)


class PostCollector:
    """Fetches and parses submissions; storage is handled upstream."""

    def __init__(self, reddit: Any, rate_limiter: RateLimiter) -> None:
        self._reddit = reddit
        self._limiter = rate_limiter

    def _listing(self, subreddit_name: str, sort: str, time_filter: str):
        if sort not in SORT_MODES:
            raise ValueError(f"unsupported sort mode: {sort!r}")
        if sort == "top" and time_filter not in TIME_FILTERS:
            raise ValueError(f"unsupported time filter: {time_filter!r}")

        subreddit = self._reddit.subreddit(subreddit_name)
        if sort == "hot":
            return subreddit.hot
        if sort == "new":
            return subreddit.new
        if sort == "rising":
            return subreddit.rising
        # top: Reddit requires an explicit time filter.
        return lambda **kwargs: subreddit.top(time_filter=time_filter, **kwargs)

    def fetch_submission(self, subreddit: str, post_id: str) -> Any:
        """Fetch one submission by id through the paced limiter."""
        return self._limiter.call(
            lambda: self._reddit.submission(id=post_id),
            description=f"submission {post_id}",
        )

    def collect(
        self,
        *,
        subreddit: str,
        limit: int,
        sort: str = "new",
        time_filter: str = "month",
    ) -> PostBatch:
        batch = PostBatch(
            subreddit=subreddit,
            sort=sort,
            time_filter=time_filter,
            requested=limit,
        )
        listing = self._listing(subreddit, sort, time_filter)

        try:
            submissions = self._limiter.call(
                lambda: listing(limit=limit),
                description=f"list r/{subreddit} {sort}",
            )
        except RateLimitExceeded as error:
            logger.error(
                "post_listing_failed",
                extra={"subreddit": subreddit, "error": str(error)},
            )
            raise

        seen_ids: set[str] = set()
        for submission in submissions:
            if len(batch.records) >= limit:
                break
            try:
                record = parse_submission(submission)
                batch.records.append(record)
            except ParseError as error:
                batch.parse_errors.append(str(error))
                logger.warning(
                    "post_parse_skipped",
                    extra={"subreddit": subreddit, "reason": str(error)},
                )

        logger.info(
            "posts_collected",
            extra={
                "subreddit": subreddit,
                "sort": sort,
                "requested": limit,
                "parsed": len(batch.records),
                "parse_errors": len(batch.parse_errors),
            },
        )
        return batch
