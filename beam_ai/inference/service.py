"""TransformerInferenceService — clean ``predict(text)`` interface.

Honesty contract:
- if no model artifact is available, callers get an explicit
  "model unavailable" state (ModelUnavailableError or the structured
  response from ``safe_predict``) — never a fabricated prediction.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from beam_ai.registry.registry import Registry


class ModelUnavailableError(RuntimeError):
    """No trained model artifact could be loaded for inference."""


@dataclass
class PredictionResult:
    primary_emotion: str
    confidence: float
    emotion_distribution: dict[str, float]
    model_name: str
    model_version: str
    inference_time_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary_emotion": self.primary_emotion,
            "confidence": self.confidence,
            "emotion_distribution": dict(self.emotion_distribution),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "inference_time_ms": round(self.inference_time_ms, 3),
        }


class TransformerInferenceService:
    """Loads a versioned artifact once; serves real predictions."""

    def __init__(
        self,
        artifact_dir: str | Path | None = None,
        *,
        model_name: str | None = None,
        model_version: str | None = None,
        registry: Registry | None = None,
        device: str = "auto",
    ) -> None:
        self.device = device
        self._model = None
        self._load_error: str | None = None
        self._artifact_dir: Path | None = None
        self._model_name: str | None = None
        self._model_version: str | None = None
        self._registry = registry or Registry()

        target: Path | None = None
        if artifact_dir:
            target = Path(artifact_dir)
        elif model_name and model_version:
            entry = self._registry.get(model_name, model_version)
            if entry and entry.get("artifact_path"):
                target = Path(entry["artifact_path"])
            else:
                self._load_error = (
                    f"No registered artifact for {model_name} {model_version}."
                )
        elif model_name:
            entry = self._registry.get_production(model_name)
            if entry and entry.get("artifact_path"):
                target = Path(entry["artifact_path"])
            else:
                self._load_error = (
                    "No trained model artifact available: no production model "
                    f"registered for {model_name!r}."
                )
        else:
            entry = self._registry.get_production()
            if entry and entry.get("artifact_path"):
                target = Path(entry["artifact_path"])
            else:
                self._load_error = (
                    "No trained model artifact available. Train and register a "
                    "model (python -m beam_ai.training --config ...) before inference."
                )

        if target is not None:
            self._try_load(target)

    # ------------------------------------------------------------------ #

    def _try_load(self, artifact_dir: Path) -> None:
        try:
            from beam_ai.models.factory import load_model_from_artifact

            metadata_file = artifact_dir / "metadata.json"
            if not metadata_file.exists():
                raise ModelUnavailableError(
                    f"No trained model artifact available at '{artifact_dir}'. "
                    f"Train a model first; the service will not fabricate predictions."
                )
            self._model = load_model_from_artifact(artifact_dir, device=self.device)
            self._artifact_dir = artifact_dir
            self._load_error = None
            from beam_ai.models.artifacts import load_artifact_metadata

            metadata = load_artifact_metadata(artifact_dir)
            self._model_name = metadata.get("model_name")
            self._model_version = metadata.get("model_version")
        except Exception as exc:  # surface as explicit unavailable state
            self._model = None
            self._load_error = f"Failed to load artifact '{artifact_dir}': {exc}"

    @property
    def available(self) -> bool:
        return self._model is not None

    @property
    def unavailability_reason(self) -> str | None:
        return self._load_error if not self.available else None

    @property
    def model_identity(self) -> tuple[str | None, str | None]:
        return self._model_name, self._model_version

    # ------------------------------------------------------------------ #

    def predict(self, text: str) -> PredictionResult:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("predict(text) requires non-empty text.")

        if not self.available:
            raise ModelUnavailableError(
                self._load_error
                or "No trained model artifact available; predictions are unavailable."
            )

        started = time.perf_counter()
        probabilities = self._model.predict_proba([text])[0]
        elapsed_ms = (time.perf_counter() - started) * 1000.0

        distribution = {
            label: float(probabilities[index])
            for index, label in enumerate(self._model.labels.labels)
        }
        distribution = dict(
            sorted(distribution.items(), key=lambda item: item[1], reverse=True)
        )
        best_label = next(iter(distribution))

        return PredictionResult(
            primary_emotion=best_label,
            confidence=distribution[best_label],
            emotion_distribution=distribution,
            model_name=self._model_name or "unknown",
            model_version=self._model_version or "unknown",
            inference_time_ms=elapsed_ms,
        )

    def safe_predict(self, text: str) -> dict[str, Any]:
        """API-friendly variant: never raises for unavailable models."""
        if not self.available:
            return {
                "status": "model_unavailable",
                "message": self.unavailability_reason,
                "result": None,
            }
        try:
            result = self.predict(text)
        except ValueError as exc:
            return {"status": "invalid_input", "message": str(exc), "result": None}
        return {"status": "ok", "result": result.to_dict()}
