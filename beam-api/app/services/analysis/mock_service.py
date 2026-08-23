"""Placeholder analysis service — development only.

This service deliberately does NOT produce emotion predictions, behavior
metrics, or explanations: the transformer model does not exist yet, and
fabricating results would corrupt the research record. It only drives the
session lifecycle (pending -> processing -> completed) so the full API and
UI workflow can be exercised end to end.

Replace via `get_analysis_service()` with a `TransformerAnalysisService`
implementation once RoBERTa weights are available. The API contract,
schemas, database layout, and frontend remain unchanged by that swap.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.analysis_input import AnalysisInput
from app.models.analysis_session import AnalysisSession
from app.schemas.analysis import AnalysisStatus
from app.services.analysis.base import AnalysisService, InferenceOutcome


class MockAnalysisService(AnalysisService):
    model_name = "beam-mock"
    model_version = "0.1.0-dev"
    deployed = False

    def run(
        self,
        db: Session,
        session: AnalysisSession,
        analysis_input: AnalysisInput,
    ) -> InferenceOutcome:
        started = time.perf_counter()

        session.status = AnalysisStatus.PROCESSING.value
        db.flush()

        # --- Placeholder boundary -------------------------------------
        # A real implementation would tokenize `analysis_input.cleaned_text`,
        # run the transformer forward pass, compute SHAP attributions and
        # persist EmotionPrediction / BehaviorMetric / Explanation rows here.
        # None of that exists yet; nothing is fabricated below.
        # ----------------------------------------------------------------

        elapsed_ms = max(0, round((time.perf_counter() - started) * 1000))
        session.status = AnalysisStatus.COMPLETED.value
        session.completed_at = datetime.now(timezone.utc)

        return InferenceOutcome(
            status=AnalysisStatus.COMPLETED,
            prediction=None,
            behavior_metric=None,
            explanation=None,
            model_name=self.model_name,
            model_version=self.model_version,
            inference_time_ms=elapsed_ms,
            distribution=None,
        )
