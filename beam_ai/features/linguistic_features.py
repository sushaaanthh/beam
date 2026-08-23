"""Linguistic features - observable surface statistics only.

These are NOT psychological interpretations; they are deterministic counts
and ratios computed from cleaned/normalized text. Punctuation, emojis and
capitalization are intentionally measured (not removed) because future
emotion models may rely on them.
"""

from __future__ import annotations

import re

from beam_ai.preprocessing.normalization import word_tokens

_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s+|$)")
_URL = re.compile(r"\bURL\b")
_QUESTION_MARK = "?"
_EXCLAMATION_MARK = "!"
_PUNCTUATION = set(".,!?;:\"'()[]{}-_/\\@#%&*=+<>~`^$|")


def extract_linguistic_features(cleaned_text: str, normalized_text: str) -> dict[str, float | int]:
    cleaned = cleaned_text or ""
    normalized = normalized_text or ""

    words = word_tokens(normalized)
    word_count = len(words)

    # Sentences split on .!? followed by whitespace/end; a trailing fragment
    # without terminal punctuation still counts as one sentence if non-empty.
    parts = [p for p in _SENTENCE_SPLIT.split(cleaned) if p.strip()]
    sentence_count = len(parts) if parts else (1 if cleaned.strip() else 0)

    letters = sum(ch.isalpha() for ch in cleaned)
    uppercase = sum(ch.isupper() for ch in cleaned)

    unique_words = len(set(w.lower() for w in words))

    return {
        "character_count": len(cleaned),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "average_word_length": round(sum(len(w) for w in words) / word_count, 4)
        if word_count
        else 0.0,
        "average_sentence_length": round(word_count / sentence_count, 4)
        if sentence_count
        else 0.0,
        "punctuation_count": sum(1 for ch in cleaned if ch in _PUNCTUATION),
        "question_count": cleaned.count(_QUESTION_MARK),
        "exclamation_count": cleaned.count(_EXCLAMATION_MARK),
        "uppercase_ratio": round(uppercase / letters, 4) if letters else 0.0,
        "emoji_count": _emoji_count(cleaned),
        "url_count": len(_URL.findall(cleaned.upper())),
        "lexical_diversity": round(unique_words / word_count, 4) if word_count else 0.0,
    }


_EMOJI_RANGES = tuple(
    (ord(lo), ord(hi))
    for lo, hi in (
        ("\U0001F300", "\U0001FAFF"),
        ("\U0001F000", "\U0001F02F"),
        ("\u2600", "\u27BF"),
        ("\u2B00", "\u2BFF"),
    )
)


def _emoji_count(text: str) -> int:
    return sum(
        1
        for ch in text
        if any(lo <= ord(ch) <= hi for lo, hi in _EMOJI_RANGES)
    )
