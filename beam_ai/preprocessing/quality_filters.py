"""Configurable quality filtering.

Every rejected record gets a machine-readable reason stored alongside it -
nothing is silently discarded. Thresholds come from PipelineSettings so they
can be tuned per dataset version without touching code.
"""

from __future__ import annotations

from dataclasses import dataclass

from beam_ai.configs.pipeline_settings import PipelineSettings
from beam_ai.preprocessing.normalization import word_tokens

# Body statuses produced by the scraper for deleted/removed content.
DELETED_STATUSES = {"removed", "deleted"}


@dataclass(frozen=True, slots=True)
class FilterDecision:
    kept: bool
    reason: str | None  # None when kept; otherwise a stable machine-readable tag


def evaluate_quality(
    *,
    raw_text: str,
    cleaned_text: str,
    body_status: str | None,
    settings: PipelineSettings,
) -> FilterDecision:
    """Apply filters in a fixed order; first failure wins (stable reasons)."""
    status = (body_status or "").lower()

    if not raw_text or not cleaned_text:
        return FilterDecision(False, "empty_text")

    if not settings.keep_deleted and status in DELETED_STATUSES:
        return FilterDecision(False, f"content_{status}")

    char_count = len(cleaned_text)
    if char_count < settings.min_chars:
        return FilterDecision(False, "too_short")
    if char_count > settings.max_chars:
        return FilterDecision(False, "too_long")

    if len(word_tokens(cleaned_text)) < settings.min_words:
        return FilterDecision(False, "too_few_words")

    return FilterDecision(True, None)
