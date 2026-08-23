"""Adapter preparing AnalysisService -> TransformerInferenceService wiring.

The existing FastAPI analysis contract (and therefore the frontend)
stays untouched. When a validated transformer model exists, the API can
call :meth:`TransformerAnalysisAdapter.analyze` and receive either:

- ``{"status": "ok", ...transformer fields...}`` — real model output; or
- ``{"status": "model_unavailable", ...}`` — letting the caller fall
  back to the current lexicon-based path unchanged.
"""

from __future__ import annotations

from typing import Any

from beam_ai.inference.explainability import EXPLANATION_SCHEMA_VERSION
from beam_ai.inference.service import TransformerInferenceService


class TransformerAnalysisAdapter:
    def __init__(self, service: TransformerInferenceService | None = None) -> None:
        # Default construction resolves production artifact via registry;
        # with nothing registered the adapter reports unavailable honestly.
        self.service = service or TransformerInferenceService()

    @property
    def available(self) -> bool:
        return self.service.available

    def analyze(self, text: str) -> dict[str, Any]:
        response = self.service.safe_predict(text)

        if response["status"] != "ok":
            return {
                "status": "model_unavailable",
                "engine": "transformer",
                "message": response.get("message"),
                "explanation_schema_version": EXPLANATION_SCHEMA_VERSION,
                "explanation": None,
            }

        result = response["result"]
        return {
            "status": "ok",
            "engine": "transformer",
            "primary_emotion": result["primary_emotion"],
            "confidence": result["confidence"],
            "emotion_distribution": result["emotion_distribution"],
            "model_name": result["model_name"],
            "model_version": result["model_version"],
            "inference_time_ms": result["inference_time_ms"],
            # Placeholder until an explainer is implemented (never faked).
            "explanation_schema_version": EXPLANATION_SCHEMA_VERSION,
            "explanation": None,
        }
