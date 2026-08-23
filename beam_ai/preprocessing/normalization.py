"""Normalization layer.

`clean_text` removes noise; `normalize_text` produces a canonical,
lowercased, contraction-expanded form intended for *lexical statistics and
deduplication only*.

The original raw text is never modified or discarded: the pipeline stores
raw_text, cleaned_text and normalized_text side by side. Downstream emotion
models will choose which view to feed; capitalization/punctuation survive in
cleaned_text on purpose.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

# Small, high-frequency contraction map (documented expansion only).
_CONTRACTIONS = {
    "won't": "will not",
    "can't": "can not",
    "n't": " not",
    "'re": " are",
    "'ve": " have",
    "'ll": " will",
    "'m": " am",
    "it's": "it is",
    "that's": "that is",
    "there's": "there is",
    "what's": "what is",
    "let's": "let us",
    "i'd": "i would",
    "they'd": "they would",
}

_WHITESPACE = re.compile(r"\s+")


@lru_cache(maxsize=1)
def _contraction_patterns() -> list[tuple[re.Pattern[str], str]]:
    # Longer keys first so e.g. "won't" wins over the generic "n't".
    items = sorted(_CONTRACTIONS.items(), key=lambda kv: -len(kv[0]))
    return [(re.compile(re.escape(k), re.IGNORECASE), v) for k, v in items]


def normalize_text(cleaned: str | None) -> str:
    """Canonical lowercase form used for dedup + lexical stats."""
    if not cleaned:
        return ""

    text = unicodedata.normalize("NFKC", cleaned)
    for pattern, replacement in _contraction_patterns():
        text = pattern.sub(replacement, text)

    text = _WHITESPACE.sub(" ", text).strip().lower()
    return text


def word_tokens(normalized_or_plain: str) -> list[str]:
    """Simple deterministic word tokenization (letters/digits/apostrophes)."""
    if not normalized_or_plain:
        return []
    return re.findall(r"[a-zA-Z0-9']+", normalized_or_plain)


def shingles(text: str, k: int = 3) -> frozenset[tuple[str, ...]]:
    """Word k-gram shingle set used by near-duplicate detection."""
    tokens = word_tokens(text.lower())
    if len(tokens) < k:
        return frozenset({tuple(tokens)}) if tokens else frozenset()
    return frozenset(tuple(tokens[i : i + k]) for i in range(len(tokens) - k + 1))
