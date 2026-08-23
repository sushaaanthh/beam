"""Processed dataset schema - single source of truth for column order.

Every processed record carries identity, three text views (raw/cleaned/
normalized), provenance, behavioral metadata, all features, and versioning.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from beam_ai import PROCESSING_VERSION

# Stable namespace so record_id = uuid5(namespace, source_id) is
# reproducible across runs and machines.
_NAMESPACE = uuid.UUID("6f6f6e6b-bea1-bea2-bea3-bea000000000")

IDENTITY_FIELDS = (
    "record_id",
    "source_id",
    "source",
    "thread_id",
    "subreddit",
)

TEXT_FIELDS = ("raw_text", "cleaned_text", "normalized_text")

METADATA_FIELDS = (
    "body_status",
    "language",
    "created_utc",
    "author_pseudonym",
    "filter_reason",   # null for kept records; reason tags live in reports only
)

VERSION_FIELDS = (
    "dataset_version",
    "processing_version",
)

# Full column order used by writers (features appended at runtime).
BASE_FIELDS: tuple[str, ...] = IDENTITY_FIELDS + TEXT_FIELDS + METADATA_FIELDS + VERSION_FIELDS


def make_record_id(source: str, source_id: str) -> str:
    """Deterministic id: same source row -> same record_id forever."""
    return str(uuid.uuid5(_NAMESPACE, f"{source}:{source_id}"))


def utc_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.replace(microsecond=0).isoformat() + "Z"


def processing_version() -> str:
    return PROCESSING_VERSION
