#!/usr/bin/env python3
"""Scrape public posts (and optionally comments) from a subreddit.

Usage:
    python scripts/scrape_subreddit.py --subreddit AskReddit --limit 50 --sort new
    python scripts/scrape_subreddit.py --subreddit AskReddit --limit 50 --sort top --time-filter month
    python scripts/scrape_subreddit.py --subreddit CasualConversation --limit 10 --no-comments

Credentials come from the environment (see .env.example) - never flags.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import SettingsError, get_settings  # noqa: E402
from reddit.client import RedditClient, RedditClientError  # noqa: E402
from reddit.collector import SubredditCollector  # noqa: E402
from reddit.logging_setup import configure_logging  # noqa: E402
from reddit.post_collector import SORT_MODES, TIME_FILTERS  # noqa: E402
from reddit.rate_limit import RateLimitExceeded, RateLimiter  # noqa: E402
from reddit.storage import Storage  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scrape_subreddit",
        description=(
            "Collect publicly available Reddit posts and comments from one or "
            "more subreddits into the B.E.A.M. research database. Data is "
            "deduplicated by Reddit ID and rate limits are respected."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--subreddit",
        nargs="+",
        default=None,
        metavar="NAME",
        help="subreddit name(s), with or without the r/ prefix; defaults to SUBREDDITS env var",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="maximum number of posts to collect per subreddit (1-1000)",
    )
    parser.add_argument(
        "--sort",
        choices=SORT_MODES,
        default=None,
        help="listing sort mode",
    )
    parser.add_argument(
        "--time-filter",
        choices=TIME_FILTERS,
        default=None,
        dest="time_filter",
        help="time window when --sort top is used",
    )
    parser.add_argument(
        "--comment-limit",
        type=int,
        default=None,
        dest="comment_limit",
        help="maximum number of comments collected per post",
    )
    parser.add_argument(
        "--no-comments",
        action="store_true",
        help="skip comment collection entirely",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    settings = get_settings()

    subreddits = args.subreddit or settings.subreddit_list
    limit = args.limit if args.limit is not None else settings.POST_LIMIT
    sort = args.sort or settings.SCRAPE_SORT
    time_filter = args.time_filter or settings.TIME_FILTER
    comment_limit = args.comment_limit if args.comment_limit is not None else settings.COMMENT_LIMIT
    include_comments = settings.INCLUDE_COMMENTS and not args.no_comments

    if limit < 1:
        parser = build_parser()
        parser.error("--limit must be >= 1")

    try:
        settings.require_reddit_credentials()
        client = RedditClient(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
        )
        client.validate_connection()
    except (SettingsError, RedditClientError) as error:
        print(f"error: {error}", file=sys.stderr)
        print("Set credentials in .env (see .env.example).", file=sys.stderr)
        return 2

    storage = Storage(settings.DATABASE_URL)
    storage.create_schema()

    limiter = RateLimiter(
        min_interval_seconds=settings.MIN_REQUEST_INTERVAL_SECONDS,
        max_retries=settings.MAX_RETRIES,
        backoff_base_seconds=settings.BACKOFF_BASE_SECONDS,
    )
    collector = SubredditCollector(client.reddit, storage, limiter)

    exit_code = 0
    for name in subreddits:
        try:
            summary = collector.collect_subreddit(
                subreddit=name.removeprefix("r/"),
                limit=limit,
                sort=sort,
                time_filter=time_filter,
                include_comments=include_comments,
                comment_limit=comment_limit,
            )
        except RateLimitExceeded as error:
            print(f"error: {error}", file=sys.stderr)
            exit_code = 1
            continue

        print(
            f"[r/{summary.subreddit}] posts discovered={summary.posts_discovered} "
            f"inserted={summary.posts_inserted} updated={summary.posts_updated} "
            f"duplicates={summary.duplicates} comments inserted={summary.comments_inserted} "
            f"errors={len(summary.parse_errors) + len(summary.storage_errors)} "
            f"status={summary.status} duration={summary.duration_seconds}s"
        )

    return exit_code


def main(argv: list[str] | None = None) -> int:
    from config.settings import get_settings as _settings

    configure_logging(_settings().LOG_LEVEL)
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
