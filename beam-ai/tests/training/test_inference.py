"""Inference service + adapter tests (unavailable state and real tiny model)."""

from __future__ import annotations

import pytest

pytest.importorskip("torch")


def _tmp_registry(tmp_path):
    from beam_ai.registry.registry import Registry

    return Registry(path=tmp_path / "registry.json")


class TestUnavailableState:
    def test_predict_raises_when_no_artifact(self, tmp_path):
        from beam_ai.inference.service import ModelUnavailableError, TransformerInferenceService

        service = TransformerInferenceService(registry=_tmp_registry(tmp_path), device="cpu")
        assert not service.available
        with pytest.raises(ModelUnavailableError, match="No trained model artifact"):
            service.predict("I feel great")

    def test_safe_predict_returns_unavailable_payload(self, tmp_path):
        from beam_ai.inference.service import TransformerInferenceService

        service = TransformerInferenceService(registry=_tmp_registry(tmp_path), device="cpu")
        response = service.safe_predict("hello")
        assert response["status"] == "model_unavailable"
        assert response["result"] is None
        assert "message" in response

    def test_missing_artifact_dir_reported(self, tmp_path):
        from beam_ai.inference.service import ModelUnavailableError, TransformerInferenceService

        service = TransformerInferenceService(
            artifact_dir=tmp_path / "ghost", registry=_tmp_registry(tmp_path)
        )
        with pytest.raises(ModelUnavailableError):
            service.predict("text")

    def test_empty_text_rejected(self, tmp_path, tiny_model, label_config):
        from beam_ai.models.artifacts import save_artifact
        from beam_ai.inference.service import TransformerInferenceService

        artifact = save_artifact(
            tiny_model,
            tmp_path / "artifact",
            training_config_snapshot={"model_name": "tiny", "model_version": "v001"},
        )
        service = TransformerInferenceService(artifact_dir=artifact)
        response = service.safe_predict("   ")
        assert response["status"] == "invalid_input"


class TestRealPredictions:
    @pytest.fixture()
    def loaded_service(self, tmp_path, tiny_model):
        from beam_ai.inference.service import TransformerInferenceService
        from beam_ai.models.artifacts import save_artifact

        artifact = save_artifact(
            tiny_model,
            tmp_path / "artifact",
            training_config_snapshot={
                "model_name": "tiny-smoke",
                "model_version": "v001",
            },
            dataset_version="smoke",
            status="training",
        )
        return TransformerInferenceService(artifact_dir=artifact)

    def test_predict_returns_required_fields(self, loaded_service):
        result = loaded_service.predict("I feel happy about this")
        payload = result.to_dict()
        for field in (
            "primary_emotion",
            "confidence",
            "emotion_distribution",
            "model_name",
            "model_version",
            "inference_time_ms",
        ):
            assert field in payload

    def test_distribution_sums_to_one(self, loaded_service):
        distribution = loaded_service.predict("text").emotion_distribution
        assert sum(distribution.values()) == pytest.approx(1.0, abs=1e-5)

    def test_primary_is_argmax_and_measured_time_positive(self, loaded_service):
        result = loaded_service.predict("some text")
        best = max(result.emotion_distribution.items(), key=lambda kv: kv[1])
        assert result.primary_emotion == best[0]
        assert result.confidence == pytest.approx(best[1])
        assert result.inference_time_ms > 0.0


class TestAdapter:
    def test_adapter_reports_unavailable_without_faking(self, tmp_path):
        from beam_ai.inference.adapter import TransformerAnalysisAdapter
        from beam_ai.inference.service import TransformerInferenceService

        adapter = TransformerAnalysisAdapter(
            service=TransformerInferenceService(
                registry=_tmp_registry(tmp_path), device="cpu"
            )
        )
        response = adapter.analyze("anything")
        assert response["status"] == "model_unavailable"
        assert response["engine"] == "transformer"
        assert response["explanation"] is None

    def test_adapter_ok_shape_with_tiny_model(self, tmp_path, tiny_model):
        from beam_ai.inference.adapter import TransformerAnalysisAdapter
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
        response = adapter.analyze("I am glad")
        assert response["status"] == "ok"
        for field in (
            "primary_emotion",
            "confidence",
            "emotion_distribution",
            "model_name",
            "model_version",
            "inference_time_ms",
            "explanation_schema_version",
        ):
            assert field in response
