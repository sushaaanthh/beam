"""Shared fixtures: fake Reddit objects, settings isolation, sqlite storage."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class FakeSubredditRef:
    def __init__(self, display_name: str) -> None:
        self.display_name = display_name

    def __str__(self) -> str:
        return self.display_name


def make_submission(
    *,
    id: str = "abc123",
    title: str = "A research-relevant post",
    selftext: str | None = "Some public discussion text.",
    author: str | None = "research_observer",
    subreddit: str = "AskReddit",
    created_utc: float = 1_760_000_000.0,
    score: int = 42,
    upvote_ratio: float = 0.93,
    num_comments: int = 7,
    url: str = "https://www.reddit.com/r/AskReddit/comments/abc123/",
    permalink: str = "/r/AskReddit/comments/abc123/post/",
    over_18: bool = False,
    spoiler: bool = False,
    stickied: bool = False,
) -> object:
    """Build a duck-typed stand-in for a praw Submission."""
    return type(
        "FakeSubmission",
        (),
        {
            "id": id,
            "title": title,
            "selftext": selftext,
            "author": author,
            "subreddit": FakeSubredditRef(subreddit),
            "created_utc": created_utc,
            "score": score,
            "upvote_ratio": upvote_ratio,
            "num_comments": num_comments,
            "url": url,
            "permalink": permalink,
            "over_18": over_18,
            "spoiler": spoiler,
            "stickied": stickied,
        },
    )()


def make_comment(
    *,
    id: str = "c1",
    body: str | None = "a public comment",
    author: str | None = "commenter",
    parent_id: str | None = "t3_abc123",
    created_utc: float = 1_760_000_500.0,
    score: int = 5,
) -> object:
    return type(
        "FakeComment",
        (),
        {
            "id": id,
            "body": body,
            "author": author,
            "parent_id": parent_id,
            "created_utc": created_utc,
            "score": score,
        },
    )()


@pytest.fixture()
def clean_env(monkeypatch):
    """Remove scraper-related env vars so Settings tests are deterministic."""
    keys = [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USER_AGENT",
        "DATABASE_URL",
        "SUBREDDITS",
        "POST_LIMIT",
        "COMMENT_LIMIT",
        "SCRAPE_SORT",
        "TIME_FILTER",
        "INCLUDE_COMMENTS",
        "MIN_REQUEST_INTERVAL_SECONDS",
        "MAX_RETRIES",
        "BACKOFF_BASE_SECONDS",
        "LOG_LEVEL",
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)
    # The repo-root .env would otherwise leak values; pydantic-settings reads
    # env_file relative to CWD, tests run from beam-scraper where none exists.
    yield
