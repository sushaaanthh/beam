"""Model abstraction + factory tests (tiny random model, CPU, offline)."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("torch")


class TestFactory:
    def test_creates_hf_model(self, label_config, tiny_tokenizer):
        from beam_ai.models.base import HFEmotionModel
        from beam_ai.training.config import TrainingConfig
        from beam_ai.models.factory import create_model

        config = TrainingConfig(model_name="tiny", dataset_version="v0", model_init="tiny_random")
        model = create_model(config, label_config, tokenizer=tiny_tokenizer)
        assert isinstance(model, HFEmotionModel)
        assert model.num_labels == 4
        assert model.device == "cpu"

    def test_tiny_random_requires_tokenizer(self, label_config):
        from beam_ai.training.config import TrainingConfig
        from beam_ai.models.factory import create_model

        config = TrainingConfig(model_name="tiny", dataset_version="v0", model_init="tiny_random")
        with pytest.raises(ValueError, match="tokenizer"):
            create_model(config, label_config, tokenizer=None)


class TestForward:
    def test_logits_shape(self, tiny_model):
        batch = tiny_model.tokenizer_pipeline.encode_batch(["I feel happy", "so sad"])
        logits = tiny_model.forward_batch(batch["input_ids"], batch["attention_mask"])
        assert tuple(logits.shape) == (2, 4)

    def test_predict_proba_rows_sum_to_one(self, tiny_model):
        probabilities = tiny_model.predict_proba(["I feel happy today"])
        assert probabilities.shape == (1, 4)
        assert float(probabilities.sum()) == pytest.approx(1.0, abs=1e-5)

    def test_predict_pairs_use_label_schema(self, tiny_model):
        pairs = tiny_model.predict(["neutral report text"])
        assert len(pairs) == 1
        label, confidence = pairs[0]
        assert label in {"joy", "sadness", "anger", "neutral"}
        assert 0.0 <= confidence <= 1.0


class TestArtifactRoundtrip:
    def test_save_then_load_reproduces_probabilities(self, tmp_path, tiny_model):
        from beam_ai.models.artifacts import save_artifact
        from beam_ai.models.factory import load_model_from_artifact

        snapshot = {
            "model_name": "tiny-smoke",
            "model_version": None,
            "dataset_version": "smoke",
            "model_init": "tiny_random",
        }
        artifact_dir = save_artifact(
            tiny_model,
            tmp_path / "artifact",
            training_config_snapshot=snapshot,
            dataset_version="smoke",
            metrics=None,
            status="training",
        )

        metadata_file = artifact_dir / "metadata.json"
        assert metadata_file.exists()
        assert (artifact_dir / "training_config.json").exists()
        assert (artifact_dir / "config.json").exists()  # HF model config

        loaded = load_model_from_artifact(artifact_dir)
        text = ["I feel happy today"]
        original = tiny_model.predict_proba(text)
        restored = loaded.predict_proba(text)
        np.testing.assert_allclose(original, restored, atol=1e-6)

    def test_load_missing_artifact_raises(self, tmp_path):
        from beam_ai.models.factory import load_model_from_artifact

        with pytest.raises(FileNotFoundError, match="metadata.json"):
            load_model_from_artifact(tmp_path / "nothing")
