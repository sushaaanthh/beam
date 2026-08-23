"""Deduplication: exact + near-duplicate detection.

Method (documented per the brief):

* **Exact duplicates** - identical `normalized_text` (lowercase,
  contraction-expanded, whitespace-collapsed), scoped per subreddit: the
  same text posted to two communities is treated as two legitimate
  observations (crossposts), while repeats inside one community are
  duplicates. First occurrence wins.
* **Near duplicates** - word-3-gram Jaccard similarity within the same
  subreddit. A pair is flagged when similarity >=
  `near_duplicate_threshold` (default 0.9, deliberately high so
  legitimately similar discussions are NOT removed).

Determinism: records are processed in a stable order (created_utc, then
record id) and candidate neighbors are scanned in sorted-key order, so the
same input always yields the same survivor set.

Complexity is O(n^2) in shingle-set comparisons within a subreddit; fine for
research-scale corpora (tens of thousands), documented as a limitation.
"""

from __future__ import annotations

from dataclasses import dataclass

from beam_ai.preprocessing.normalization import shingles


@dataclass(frozen=True, slots=True)
class DedupeVerdict:
    duplicate: bool
    reason: str | None  # 'duplicate_exact' | 'duplicate_near' | None


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    if intersection == 0:
        return 0.0
    return intersection / len(a | b)


class Deduplicator:
    """Streaming deduplicator with fixed processing order."""

    def __init__(self, near_threshold: float = 0.9, enabled: bool = True) -> None:
        self.enabled = enabled
        self.near_threshold = near_threshold
        # subreddit -> set of normalized texts already kept
        self._seen_exact: dict[str, set[str]] = {}
        # subreddit -> list[(sort_key, shingles)]
        self._near_index: dict[str, list[tuple[str, frozenset]]] = {}

    def check(
        self,
        *,
        record_id: str,
        sort_key: str,
        subreddit: str,
        normalized_text: str,
    ) -> DedupeVerdict:
        if not self.enabled:
            return DedupeVerdict(False, None)

        if not normalized_text:
            return DedupeVerdict(False, None)

        seen_exact = self._seen_exact.setdefault(subreddit, set())

        # --- exact (within subreddit) ---------------------------------------
        if normalized_text in seen_exact:
            return DedupeVerdict(True, "duplicate_exact")

        # --- near (within subreddit only) -----------------------------------
        current = shingles(normalized_text)
        bucket = self._near_index.setdefault(subreddit, [])
        for _, other in bucket:
            if jaccard(current, other) >= self.near_threshold:
                # Register exact form even on rejection so later dupes of the
                # rejected text resolve to the same reason deterministically.
                seen_exact.add(normalized_text)
                return DedupeVerdict(True, "duplicate_near")

        # --- keep: register --------------------------------------------------
        seen_exact.add(normalized_text)
        bucket.append((f"{sort_key}|{record_id}", current))
        return DedupeVerdict(False, None)
