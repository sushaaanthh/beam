"""Deterministic train/validation/test splitting.

Strategy (documented per the brief):

* **Group-aware, thread-level split.** The group key is `thread_id` (the
  parent Reddit post id). Every record from one comment tree - including
  the post itself - lands in exactly one split, so related texts never leak
  across train/validation/test.
* **Deterministic assignment without randomness:** groups are ordered by
  sha256(seed + group_key), then whole groups are assigned to splits in
  that order according to the configured ratios (largest-remainder method
  so the counts add up exactly). Same input + same seed => identical splits,
  on any machine.
* Ratios are configurable; they must sum to ~1.0.
"""

from __future__ import annotations

import hashlib
from typing import Any

SPLIT_NAMES = ("train", "validation", "test")


def _group_sort_key(seed: int, group_key: str) -> str:
    digest = hashlib.sha256(f"{seed}:{group_key}".encode("utf-8")).hexdigest()
    return digest


def assign_splits(
    thread_ids: list[str],
    *,
    train_ratio: float,
    validation_ratio: float,
    test_ratio: float,
    seed: int,
) -> dict[str, str]:
    """Map each thread_id to a split name deterministically."""
    total = train_ratio + validation_ratio + test_ratio
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"split ratios must sum to 1.0 (got {total:.6f})")

    ordered_groups = sorted(set(thread_ids), key=lambda g: _group_sort_key(seed, g))
    total_groups = len(ordered_groups)

    n_train = int(round(train_ratio * total_groups))
    n_validation = int(round(validation_ratio * total_groups))
    # Largest-remainder correction so the three counts sum exactly.
    n_test = total_groups - n_train - n_validation

    assignment: dict[str, str] = {}
    for index, group in enumerate(ordered_groups):
        if index < n_train:
            assignment[group] = "train"
        elif index < n_train + n_validation:
            assignment[group] = "validation"
        else:
            assignment[group] = "test"

    return assignment


def split_statistics(rows: list[dict[str, Any]]) -> dict[str, int]:
    stats = {name: 0 for name in SPLIT_NAMES}
    for row in rows:
        split_name = row.get("split")
        if split_name in stats:
            stats[split_name] += 1
    return stats
