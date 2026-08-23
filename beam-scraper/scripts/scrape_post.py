#!/usr/bin/env python3
"""Scrape one Reddit post and its nested comments by ID.

Usage:
    python scripts/scrape_post.py --post-id abc123 --subreddit AskReddit
    python scripts/scrape_post.py --url https://www.reddit.com/r/AskReddit/comments/abc123/title/

The parent post is stored first so its comments can reference it.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import SettingsError, get_settings  # noqa: E402
from reddit.client import RedditClient, RedditClientError  # noqa: E402
from reddit.collector import SubredditCollector  # noqa: E402
from reddit.logging_setup import configure_logging  # noqa: E402
from reddit.rate_limit import RateLimiter  # noqa: E402
from reddit.storage import Storage  # noqa: E402

REDDIT_POST_URL = re.compile(
    r"reddit\.com/(?:r/)?(?P<subreddit>[A-Za-z0-9_]+)/comments/(?P<id>[A-Za-z0-9]+)",
    re.IGNORECASE,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scrape_post",
        description=(
            "Collect a single public Reddit thread (post body plus its nested "
            "comment tree) into the B.E.A.M. research database."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--post-id", dest="post_id", help="base36 Reddit submission id")
    target.add_argument("--url", help="full Reddit permalink to the post")

    parser.add_argument(
        "--subreddit",
        default=None,
        help="required with --post-id when the URL form is not used",
    )
    parser.add_argument(
        "--comment-limit",
        type=int,
        default=None,
        dest="comment_limit",
        help="maximum number of comments collected",
    )
    return parser


def resolve_target(args: argparse.Namespace) -> tuple[str, str] | None:
    if args.url:
        match = REDDIT_POST_URL.search(args.url)
        if not match:
            print("error: could not parse a Reddit post URL", file=sys.stderr)
            return None
        return match.group("subreddit"), match.group("id")
    if not args.subreddit:
        print("error: --subreddit is required with --post-id", file=sys.stderr)
        return None
    return args.subreddit.removeprefix("r/"), args.post_id


def run(args: argparse.Namespace) -> int:
    settings = get_settings()
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

    resolved = resolve_target(args)
    if resolved is None:
        return 2
    subreddit, post_id = resolved

    storage = Storage(settings.DATABASE_URL)
    storage.create_schema()

    collector = SubredditCollector(
        client.reddit,
        storage,
        RateLimiter(
            min_interval_seconds=settings.MIN_REQUEST_INTERVAL_SECONDS,
            max_retries=settings.MAX_RETRIES,
            backoff_base_seconds=settings.BACKOFF_BASE_SECONDS,
        ),
    )

    summary = collector.collect_single_post(
        subreddit=subreddit,
        post_id=post_id,
        comment_limit=args.comment_limit
        if args.comment_limit is not None
        else settings.COMMENT_LIMIT,
    )

    print(
        f"[r/{summary.subreddit}] post {post_id}: inserted={summary.posts_inserted} "
        f"duplicates={summary.duplicates} comments inserted={summary.comments_inserted} "
        f"errors={len(summary.parse_errors) + len(summary.storage_errors)} "
        f"status={summary.status} duration={summary.duration_seconds}s"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    configure_logging(get_settings().LOG_LEVEL)
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
