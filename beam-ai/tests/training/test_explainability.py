"""Explainability preparation tests (schemas + not-implemented contract)."""

from __future__ import annotations

import pytest

from beam_ai.inference.adapter import TransformerAnalysisAdapter
from beam_ai.inference.explainability import (
    EXPLANATION_SCHEMA_VERSION,
    ExplanationPayload,
    PlaceholderExplainer,
    TokenAttribution,
)


class TestSchemas:
    def test_payload_roundtrip_keys(self):
        payload = ExplanationPayload(
            method=None,
            important_tokens=[TokenAttribution(token="happy", start=7, end=12, importance=0.9)],
            feature_importance={},
            metadata={"model": "future"},
        )
        data = payload.to_dict()
        assert set(data) == {
            "schema_version",
            "method",
            "important_tokens",
            "feature_importance",
            "metadata",
        }
        assert data["schema_version"] == EXPLANATION_SCHEMA_VERSION
        assert data["important_tokens"][0]["token"] == "happy"

    def test_empty_payload_is_valid(self):
        assert ExplanationPayload().to_dict()["important_tokens"] == []


class TestNotImplemented:
    def test_placeholder_explainer_raises(self):
        with pytest.raises(NotImplementedError, match="README"):
            PlaceholderExplainer().explain("text", prediction=None)


class TestAdapterExplanationPlaceholder:
    def test_adapter_carries_explanation_fields(self, tmp_path, tiny_model):
        from beam_ai.inference.service import TransformerInferenceService
        from beam_ai.models.artifacts import save_artifact

        artifact = save_artifact(
            tiny_model,
            tmp_path / "artifact",
            training_config_snapshot={"model_name": "tiny", "model_version": "v001"},
        )
        adapter = TransformerAnalysisAdapter(
            service=TransformerInferenceService(artifact_dir=artifact)
        )
        response = adapter.analyze("text")
        assert response["explanation"] is None  # never faked
        assert response["explanation_schema_version"] == EXPLANATION_SCHEMA_VERSION
