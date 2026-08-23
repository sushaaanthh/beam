"""Optional NLP features with graceful degradation.

Backends (all optional; the pipeline reports which are active):

* VADER (`vaderSentiment` package) -> vader_positive / vader_negative /
  vader_neutral / vader_compound. IMPORTANT: these are auxiliary lexical
  sentiment scores, NOT ground-truth emotion labels and NOT model
  predictions.
* spaCy (`en_core_web_sm`)         -> coarse POS distribution + entity count.

When a backend is unavailable the feature columns are None and an
availability flag is recorded - nothing crashes and nothing is faked.
"""

from __future__ import annotations

VADER_FIELDS = ("vader_positive", "vader_negative", "vader_neutral", "vader_compound")

_vader_analyzer = None
_spacy_nlp = None


def _get_vader():
    global _vader_analyzer
    if _vader_analyzer is False:
        return None
    if _vader_analyzer is None:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

            _vader_analyzer = SentimentIntensityAnalyzer()
        except Exception:
            _vader_analyzer = False
            return None
    return _vader_analyzer


def _get_spacy():
    global _spacy_nlp
    if _spacy_nlp is False:
        return None
    if _spacy_nlp is None:
        try:
            import spacy

            _spacy_nlp = spacy.load("en_core_web_sm")
        except Exception:
            _spacy_nlp = False
            return None
    return _spacy_nlp


def nlp_availability() -> dict[str, bool]:
    return {
        "vader_available": _get_vader() is not None,
        "spacy_available": _get_spacy() is not None,
    }


def extract_vader_features(cleaned_text: str) -> dict[str, float | None]:
    analyzer = _get_vader()
    if analyzer is None or not cleaned_text:
        return {field: None for field in VADER_FIELDS}

    scores = analyzer.polarity_scores(cleaned_text)
    return {
        "vader_positive": round(float(scores.get("pos", 0.0)), 4),
        "vader_negative": round(float(scores.get("neg", 0.0)), 4),
        "vader_neutral": round(float(scores.get("neu", 0.0)), 4),
        "vader_compound": round(float(scores.get("compound", 0.0)), 4),
    }


def extract_pos_features(normalized_text: str) -> dict[str, object]:
    """Coarse POS distribution as a JSON string + named-entity count."""
    nlp = _get_spacy()
    if nlp is None or not normalized_text:
        return {"pos_distribution": None, "entity_count": None}

    doc = nlp(normalized_text[:5000])  # bound cost on pathological inputs
    counts: dict[str, int] = {}
    for token in doc:
        pos = token.pos_ or "X"
        counts[pos] = counts.get(pos, 0) + 1

    total = sum(counts.values()) or 1
    distribution = {pos: round(count / total, 4) for pos, count in sorted(counts.items())}
    import json

    return {
        "pos_distribution": json.dumps(distribution, sort_keys=True),
        "entity_count": len(doc.ents),
    }
