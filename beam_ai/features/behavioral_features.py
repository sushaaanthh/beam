"""Behavioral / metadata features - observable, non-psychological.

Derived from scraper metadata only (score, comment counts, timestamps,
subreddit). Missing values stay None rather than being imputed.
"""

from __future__ import annotations

from datetime import datetime


def extract_behavioral_features(
    *,
    created_utc: datetime | None,
    score: int | float | None = None,
    num_comments: int | None = None,
    subreddit: str | None = None,
) -> dict[str, object]:
    features: dict[str, object] = {
        "score": int(score) if score is not None else None,
        "comment_count": int(num_comments) if num_comments is not None else None,
        "subreddit": subreddit or None,
        "posting_hour": None,
        "posting_weekday": None,
        "is_weekend": None,
    }

    if created_utc is not None:
        # Reddit timestamps are epoch seconds; keep UTC for determinism.
        hour = created_utc.hour
        weekday = created_utc.weekday()  # 0=Monday
        features["posting_hour"] = hour
        features["posting_weekday"] = weekday
        features["is_weekend"] = weekday >= 5

    return features
