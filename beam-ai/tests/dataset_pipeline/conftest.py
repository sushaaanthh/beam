"""Synthetic fixtures for the dataset pipeline tests. No Reddit access."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from beam_ai.configs.pipeline_settings import PipelineSettings  # noqa: E402


def make_settings(**overrides) -> PipelineSettings:
    settings = PipelineSettings(_env_file=None)
    for key, value in overrides.items():
        setattr(settings, key, value)
    return settings


def post_row(
    *,
    post_id: str,
    title: str = "A title",
    body: str = "Some meaningful discussion body text.",
    subreddit: str = "AskReddit",
    created_utc: str = "2026-08-01T12:00:00Z",
    score: int = 5,
    num_comments: int = 2,
    body_status: str | None = "available",
) -> dict:
    return {
        "reddit_post_id": post_id,
        "subreddit": subreddit,
        "title": title,
        "body": body,
        "body_status": body_status or "",
        # Scraper already pseudonymizes authors before storage/export.
        "author": f"{post_id}a1b2c3d4e5f60718"[:16],
        "created_utc": created_utc,
        "score": score,
        "num_comments": num_comments,
        "url": f"https://reddit.com/r/{subreddit}/comments/{post_id}/",
    }


def comment_row(
    *,
    comment_id: str,
    post_id: str,
    body: str = "A thoughtful reply.",
    subreddit: str = "AskReddit",
    created_utc: str = "2026-08-01T13:00:00Z",
    score: int = 1,
) -> dict:
    return {
        "reddit_comment_id": comment_id,
        "post_id": post_id,
        "subreddit": subreddit,
        "body": body,
        "body_status": "available",
        "author": f"{comment_id}a1b2c3d4e5f60718"[:16],
        "created_utc": created_utc,
        "score": score,
        "parent_id": post_id,
        "depth": 1,
    }


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    return path


@pytest.fixture()
def default_settings() -> PipelineSettings:
    # Deterministic settings; language allowlist off unless a test opts in.
    settings = make_settings(language_mode="off")
    yield settings
