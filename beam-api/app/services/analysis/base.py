"""Analysis service interface.

The API layer depends only on this abstraction. When the real RoBERTa
weights are trained and exported, implement `TransformerAnalysisService`
against the same interface and register it in `get_analysis_service()`.
No route or schema change is required for that swap.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.analysis_input import AnalysisInput
from app.models.analysis_session import AnalysisSession
from app.models.behavior_metric import BehaviorMetric
from app.models.emotion_prediction import EmotionPrediction
from app.models.explanation import Explanation
from app.schemas.analysis import AnalysisStatus


@dataclass(slots=True)
class InferenceOutcome:
    """Everything a service may attach to a session. None = not produced."""

    status: AnalysisStatus
    prediction: EmotionPrediction | None = None
    behavior_metric: BehaviorMetric | None = None
    explanation: Explanation | None = None
    model_name: str | None = None
    model_version: str | None = None
    inference_time_ms: int | None = None
    error_detail: str | None = None
    distribution: list[dict[str, object]] | None = field(default=None)


class AnalysisService(ABC):
    """Contract for turning an AnalysisInput into persisted inference output."""

    model_name: str = "unknown"
    model_version: str = "0.0.0"
    deployed: bool = False

    @abstractmethod
    def run(self, db: Session, session: AnalysisSession, analysis_input: AnalysisInput) -> InferenceOutcome:
        """Execute inference for the given session.

        Implementations must persist any child records (prediction,
        behavior metric, explanation) themselves and return an outcome;
        the caller owns transaction commit/rollback.
        """
        raise NotImplementedError
