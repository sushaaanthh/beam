"""Explainability PREPARATION — schemas and interface only.

Per project rules, SHAP / LIME / token-level attribution are NOT
implemented yet. What exists today:

- ``TokenAttribution`` / ``ExplanationPayload`` result schemas so future
  explainers have a stable contract to fill;
- ``ExplainerProtocol`` describing the seam where an explainer plugs in.

Anything beyond that raises NotImplementedError with a pointer to the
roadmap. No fake importance scores are ever produced.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

EXPLANATION_SCHEMA_VERSION = "explain-0.1"


@dataclass
class TokenAttribution:
    token: str
    start: int
    end: int
    importance: float  # real score from the explaining method


@dataclass
class ExplanationPayload:
    schema_version: str = EXPLANATION_SCHEMA_VERSION
    method: str | None = None  # e.g. "shap", "lime", "gradient"
    important_tokens: list[TokenAttribution] = field(default_factory=list)
    feature_importance: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "method": self.method,
            "important_tokens": [
                {
                    "token": t.token,
                    "start": t.start,
                    "end": t.end,
                    "importance": t.importance,
                }
                for t in self.important_tokens
            ],
            "feature_importance": dict(self.feature_importance),
            "metadata": dict(self.metadata),
        }


class ExplainerProtocol(ABC):
    """Seam for future explainers (SHAP, LIME, token attribution)."""

    @abstractmethod
    def explain(self, text: str, prediction) -> ExplanationPayload:
        """Return a populated ExplanationPayload for one prediction."""


class PlaceholderExplainer(ExplainerProtocol):
    """Explicit not-implemented stand-in; never returns invented values."""

    def explain(self, text: str, prediction) -> ExplanationPayload:
        raise NotImplementedError(
            "Explainability is planned but not implemented. See "
            "beam-ai/README.md 'Future SHAP integration' for the roadmap."
        )
