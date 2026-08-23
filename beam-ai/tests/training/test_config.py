"""Training configuration tests (no torch required)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from beam_ai.training.config import ConfigError, TrainingConfig


def _base_kwargs(**overrides):
    defaults = {"model_name": "distilbert-base-uncased", "dataset_version": "v001"}
    defaults.update(overrides)
    return defaults


class TestDefaults:
    def test_minimal_config_loads(self):
        config = TrainingConfig(**_base_kwargs())
        assert config.learning_rate == 2e-5
        assert config.batch_size == 16
        assert config.epochs == 3
        assert config.max_sequence_length == 128
        assert config.random_seed == 42
        assert config.warmup_ratio == 0.1
        assert config.weight_decay == 0.01
        assert config.device == "auto"
        assert config.model_init == "pretrained"

    def test_split_file_paths(self, tmp_path):
        config = TrainingConfig(**_base_kwargs(datasets_root=tmp_path))
        assert (
            config.split_file("train")
            == tmp_path / "splits" / "dataset_v001_train.jsonl"
        )
        with pytest.raises(ConfigError):
            config.split_file("holdout")

    def test_metadata_file(self, tmp_path):
        config = TrainingConfig(**_base_kwargs(datasets_root=tmp_path))
        assert config.metadata_file == tmp_path / "metadata" / "dataset_v001.json"


class TestValidators:
    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("learning_rate", 0.0),
            ("learning_rate", 1.5),
            ("batch_size", 0),
            ("epochs", 0),
            ("max_sequence_length", 4),
            ("max_sequence_length", 1024),
            ("warmup_ratio", 1.0),
            ("weight_decay", -0.1),
        ],
    )
    def test_invalid_values_rejected(self, field, value):
        # pydantic wraps validator ValueErrors into ValidationError.
        with pytest.raises(ValidationError):
            TrainingConfig(**_base_kwargs(**{field: value}))

    def test_duplicate_labels_rejected(self):
        with pytest.raises(ValidationError, match="Duplicate"):
            TrainingConfig(**_base_kwargs(labels=["joy", "joy"]))

    def test_single_label_rejected(self):
        with pytest.raises(ValidationError):
            TrainingConfig(**_base_kwargs(labels=["joy"]))


class TestYamlLoading:
    def test_from_yaml_roundtrip(self, tmp_path):
        yaml_file = tmp_path / "train.yaml"
        yaml_file.write_text(
            """
model_name: roberta-base
model_type: roberta
dataset_version: v002
learning_rate: 3.0e-05
batch_size: 8
epochs: 2
max_sequence_length: 64
random_seed: 7
warmup_ratio: 0.05
weight_decay: 0.02
labels: [anger, fear, joy]
device: cpu
""",
            encoding="utf-8",
        )
        config = TrainingConfig.from_yaml(yaml_file)
        assert config.model_name == "roberta-base"
        assert config.learning_rate == pytest.approx(3e-5)
        assert config.labels == ["anger", "fear", "joy"]
        assert config.random_seed == 7

    def test_missing_yaml_raises(self, tmp_path):
        with pytest.raises(ConfigError, match="not found"):
            TrainingConfig.from_yaml(tmp_path / "nope.yaml")

    def test_invalid_yaml_structure_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("- just\n- a\n- list\n", encoding="utf-8")
        with pytest.raises(ConfigError, match="mapping"):
            TrainingConfig.from_yaml(bad)

    def test_bundled_smoke_config_is_valid(self):
        from pathlib import Path

        smoke = Path(__file__).resolve().parents[2] / "configs" / "smoke_test.yaml"
        config = TrainingConfig.from_yaml(smoke)
        assert config.model_init == "tiny_random"
        assert config.device == "cpu"
        assert set(config.split_files) == {"train", "validation", "test"}

    def test_serialisable_snapshot_is_json_safe(self):
        import json

        snapshot = TrainingConfig(**_base_kwargs()).to_serialisable()
        assert json.loads(json.dumps(snapshot))["model_name"] == "distilbert-base-uncased"
