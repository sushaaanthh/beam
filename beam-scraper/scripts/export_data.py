#!/usr/bin/env python3
"""Export collected research data to CSV or JSONL.

Read-only: the database is never modified. Files land under
beam-datasets/exports/ by default with a timestamped name.

Usage:
    python scripts/export_data.py --format csv --subreddit AskReddit --limit 100
    python scripts/export_data.py --format jsonl --comments --out my_export.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import get_settings  # noqa: E402
from reddit.models import RedditComment, RedditPost  # noqa: E402
from reddit.storage import Storage  # noqa: E402

DEFAULT_EXPORT_DIR = Path(__file__).resolve().parents[2] / "beam-datasets" / "raw"

POST_FIELDS = [
    "reddit_post_id",
    "subreddit",
    "title",
    "body",
    "body_status",
    "author",
    "created_utc",
    "score",
    "upvote_ratio",
    "num_comments",
    "url",
    "permalink",
    "is_nsfw",
    "is_spoiler",
    "stickied",
    "retrieved_at",
]

COMMENT_FIELDS = [
    "reddit_comment_id",
    "post_id",
    "subreddit",
    "body",
    "body_status",
    "author",
    "parent_id",
    "depth",
    "created_utc",
    "score",
    "retrieved_at",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="export_data",
        description=(
            "Export collected Reddit research data to CSV or JSONL "
            "(read-only; database records are never modified)."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--format", choices=("csv", "jsonl"), default="csv", help="output format")
    parser.add_argument("--comments", action="store_true", help="export comments instead of posts")
    parser.add_argument("--subreddit", default=None, help="restrict export to one subreddit")
    parser.add_argument("--limit", type=int, default=None, help="maximum rows to export")
    parser.add_argument("--out", default=None, help="output file path (default: timestamped file in beam-datasets/raw)")
    return parser


def _row(obj, fields: list[str]) -> dict[str, object]:
    row: dict[str, object] = {}
    for field_name in fields:
        value = getattr(obj, field_name)
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        row[field_name] = value
    return row


def run(args: argparse.Namespace) -> int:
    settings = get_settings()
    storage = Storage(settings.DATABASE_URL)

    out_path = (
        Path(args.out)
        if args.out
        else DEFAULT_EXPORT_DIR
        / f"{'comments' if args.comments else 'posts'}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.{args.format}"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    source = storage.iter_comments(args.subreddit) if args.comments else storage.iter_posts(args.subreddit)
    fields = COMMENT_FIELDS if args.comments else POST_FIELDS

    written = 0
    if args.format == "jsonl":
        with out_path.open("w", encoding="utf-8", newline="\n") as handle:
            for obj in source:
                if args.limit is not None and written >= args.limit:
                    break
                handle.write(json.dumps(_row(obj, fields), ensure_ascii=False) + "\n")
                written += 1
    else:
        with out_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for obj in source:
                if args.limit is not None and written >= args.limit:
                    break
                writer.writerow(_row(obj, fields))
                written += 1

    print(f"exported {written} {'comments' if args.comments else 'posts'} -> {out_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
