"""Input/output helpers: CSV + JSONL readers, JSONL writer, db input.

Readers normalize heterogeneous inputs (scraper exports, raw dumps,
database rows) into a common in-memory record shape:

    {
      source: 'reddit_post' | 'reddit_comment',
      source_id, thread_id, subreddit,
      raw_text, body_status,
      created_utc: datetime | None,
      author_pseudonym, score, num_comments
    }

Raw data is only ever READ here; nothing writes into beam-datasets/raw.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

POST_FIELDS = {"reddit_post_id", "subreddit", "title"}
COMMENT_FIELDS = {"reddit_comment_id", "post_id"}


def _parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    # Numeric epoch seconds.
    try:
        return datetime.fromtimestamp(float(text), tz=timezone.utc)
    except ValueError:
        pass
    # ISO-8601 (scraper exports use trailing Z).
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _as_bool(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def _to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def normalize_row(row: dict[str, Any]) -> dict[str, Any] | None:
    """Map one input row to the common shape; None for unusable rows."""
    row = {k.strip(): v for k, v in row.items() if k}

    if "reddit_post_id" in row or ("title" in row and "reddit_comment_id" not in row):
        source = "reddit_post"
        source_id = str(row.get("reddit_post_id") or "").strip()
        thread_id = source_id
        title = str(row.get("title") or "").strip()
        body = str(row.get("body") or "").strip()
        raw_text = f"{title}\n\n{body}".strip() if title else body
        num_comments = _to_int(row.get("num_comments"))
        subreddit = str(row.get("subreddit") or "").strip()
    elif "reddit_comment_id" in row:
        source = "reddit_comment"
        source_id = str(row.get("reddit_comment_id") or "").strip()
        thread_id = str(row.get("post_id") or "").strip()
        raw_text = str(row.get("body") or "").strip()
        num_comments = None
        subreddit = str(row.get("subreddit") or "").strip()
    else:
        return None

    if not source_id:
        return None

    return {
        "source": source,
        "source_id": source_id,
        "thread_id": thread_id or source_id,
        "subreddit": subreddit,
        "raw_text": raw_text,
        "body_status": str(row.get("body_status") or "").strip().lower() or None,
        "created_utc": _parse_datetime(row.get("created_utc")),
        "author_pseudonym": str(row.get("author") or "").strip() or None,
        "score": _to_int(row.get("score")),
        "num_comments": num_comments,
        "is_nsfw": _as_bool(row.get("is_nsfw")),
        "is_spoiler": _as_bool(row.get("is_spoiler")),
        "stickied": _as_bool(row.get("stickied")),
    }


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def read_csv(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def iter_input_rows(input_path: Path) -> Iterator[dict[str, Any]]:
    """Yield normalized records from a file OR every csv/jsonl in a directory.

    Also accepts 'db' / 'db:<url>' to stream rows through the scraper's own
    storage layer when it is installed alongside this repository.
    """
    if input_path.is_dir():
        files = sorted(
            p for p in input_path.iterdir() if p.suffix.lower() in {".jsonl", ".csv"}
        )
        for file_path in files:
            yield from _iter_single_file(file_path)
        return

    yield from _iter_single_file(input_path)


def _iter_single_file(path: Path) -> Iterator[dict[str, Any]]:
    suffix = path.suffix.lower()
    reader = read_jsonl if suffix == ".jsonl" else read_csv
    for row in reader(path):
        normalized = normalize_row(row)
        if normalized is not None:
            yield normalized


def iter_database_rows(database_url: str | None = None) -> Iterator[dict[str, Any]]:
    """Stream posts+comments via beam-scraper's storage layer (read-only)."""
    import sys

    scraper_root = str(Path(__file__).resolve().parents[3] / "beam-scraper")
    if scraper_root not in sys.path:
        sys.path.insert(0, scraper_root)

    from reddit.storage import Storage  # noqa: PLC0415 - deliberate lazy import

    if not database_url:
        raise ValueError("db input requires DATABASE_URL (e.g. --db-url or DATABASE_URL env)")

    storage = Storage(database_url)
    storage.create_schema()

    def post_to_row(post: Any) -> dict[str, Any]:
        return {
            "reddit_post_id": post.reddit_post_id,
            "subreddit": post.subreddit,
            "title": post.title,
            "body": post.body or "",
            "body_status": post.body_status,
            "author": post.author,
            "created_utc": post.created_utc.isoformat(),
            "score": post.score,
            "num_comments": post.num_comments,
        }

    def comment_to_row(comment: Any) -> dict[str, Any]:
        return {
            "reddit_comment_id": comment.reddit_comment_id,
            "post_id": comment.post_id,
            "subreddit": comment.subreddit,
            "body": comment.body or "",
            "body_status": comment.body_status,
            "author": comment.author,
            "created_utc": comment.created_utc.isoformat(),
            "score": comment.score,
        }

    if database_url:
        for row in storage.iter_posts():
            yield post_to_row(row)
        for row in storage.iter_comments():
            yield comment_to_row(row)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return len(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
