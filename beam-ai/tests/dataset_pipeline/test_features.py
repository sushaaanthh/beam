"""Feature extraction tests - pure math on synthetic text."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from beam_ai.features.behavioral_features import extract_behavioral_features
from beam_ai.features.linguistic_features import extract_linguistic_features
from beam_ai.features.nlp_features import extract_vader_features, nlp_availability


class TestLinguisticFeatures:
    def test_counts_are_exact(self) -> None:
        cleaned = "Why is this happening?! I asked twice??"
        normalized = normalized_of(cleaned)
        features = extract_linguistic_features(cleaned, normalized)

        assert features["question_count"] == 3  # ? ! ? — question marks only
        assert features["exclamation_count"] == 1
        assert features["word_count"] == 7
        assert features["sentence_count"] == 2
        assert features["character_count"] == len(cleaned)

    def test_uppercase_ratio(self) -> None:
        features = extract_linguistic_features("ALL CAPS shout", normalized_of("ALL CAPS shout"))
        # letters: A L L C A P S s h o u t = 12; uppercase = 7
        assert abs(features["uppercase_ratio"] - round(7 / 12, 4)) < 1e-9

    def test_lexical_diversity(self) -> None:
        features = extract_linguistic_features(
            "happy happy sad day", normalized_of("happy happy sad day")
        )
        assert abs(features["lexical_diversity"] - round(3 / 4, 4)) < 1e-9

    def test_url_counted_via_placeholder(self) -> None:
        features = extract_linguistic_features("see URL now", normalized_of("see URL now"))
        assert features["url_count"] == 1

    def test_emoji_count(self) -> None:
        features = extract_linguistic_features("great 😊 day 🔥", normalized_of("great 😊 day 🔥"))
        assert features["emoji_count"] == 2

    def test_empty_text_zero_safe(self) -> None:
        features = extract_linguistic_features("", "")
        assert features["word_count"] == 0
        assert features["average_word_length"] == 0.0
        assert features["lexical_diversity"] == 0.0


class TestBehavioralFeatures:
    def test_timestamp_derived_fields(self) -> None:
        from datetime import datetime, timezone

        created = datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc)  # Saturday
        features = extract_behavioral_features(
            created_utc=created, score=12, num_comments=3, subreddit="AskReddit"
        )
        assert features["posting_hour"] == 13
        assert features["posting_weekday"] == 5
        assert features["is_weekend"] is True
        assert features["score"] == 12
        assert features["comment_count"] == 3
        assert features["subreddit"] == "AskReddit"

    def test_missing_metadata_stays_none(self) -> None:
        features = extract_behavioral_features(created_utc=None)
        assert features["score"] is None
        assert features["posting_hour"] is None
        assert features["is_weekend"] is None


class TestOptionalNlpFeatures:
    def test_vader_scores_present_when_backend_available(self) -> None:
        availability = nlp_availability()
        if not availability["vader_available"]:
            import pytest

            pytest.skip("vaderSentiment not installed")
        scores = extract_vader_features("I am absolutely thrilled and overjoyed!")
        assert scores["vader_positive"] > scores["vader_negative"]
        assert scores["vader_compound"] > 0

    def test_vader_scores_are_auxiliary_not_labels(self) -> None:
        # Contract: fields exist with float-or-None values and no label column.
        scores = extract_vader_features("anything")
        assert set(scores) == {"vader_positive", "vader_negative", "vader_neutral", "vader_compound"}
        for value in scores.values():
            assert value is None or isinstance(value, float)


def normalized_of(text: str) -> str:
    from beam_ai.preprocessing.text_cleaning import clean_text
    from beam_ai.preprocessing.normalization import normalize_text

    return normalize_text(clean_text(text))
