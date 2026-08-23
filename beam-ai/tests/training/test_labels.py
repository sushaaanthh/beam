"""Label configuration tests (no torch required)."""

from __future__ import annotations

import json

import pytest

from beam_ai.training.config import TrainingConfig
from beam_ai.training.labels import LabelConfig, LabelSchemaError


def _config(tmp_path, dataset_version="v001", labels=None):
    return TrainingConfig(
        model_name="m",
        dataset_version=dataset_version,
        datasets_root=tmp_path,
        labels=labels,
    )


class TestMappings:
    def test_bidirectional_mapping_consistency(self):
        labels = LabelConfig(labels=["anger", "fear", "joy", "sadness"])
        assert labels.label_to_id == {"anger": 0, "fear": 1, "joy": 2, "sadness": 3}
        assert labels.id_to_label == {0: "anger", 1: "fear", 2: "joy", 3: "sadness"}
        for label, label_id in labels.label_to_id.items():
            assert labels.id_to_label[label_id] == label

    def test_unknown_label_raises(self):
        labels = LabelConfig(labels=["joy", "sadness"])
        with pytest.raises(LabelSchemaError, match="Unknown label"):
            labels.id_for("fury")
        with pytest.raises(LabelSchemaError, match="Unknown label id"):
            labels.label_for(9)

    def test_minimum_two_labels(self):
        with pytest.raises(Exception):
            LabelConfig(labels=["only"])


class TestResolution:
    def test_explicit_labels_win(self, tmp_path):
        config = _config(tmp_path, labels=["a", "b"])
        resolved = LabelConfig.resolve(config)
        assert resolved.labels == ["a", "b"]

    def test_metadata_label_schema_used(self, tmp_path):
        meta_dir = tmp_path / "metadata"
        meta_dir.mkdir()
        (meta_dir / "dataset_v001.json").write_text(
            json.dumps(
                {
                    "label_type": "emotion_6",
                    "label_schema": {"labels": ["joy", "sadness", "anger"]},
                }
            ),
            encoding="utf-8",
        )
        resolved = LabelConfig.resolve(_config(tmp_path))
        assert resolved.labels == ["joy", "sadness", "anger"]

    def test_unlabeled_dataset_refused(self, tmp_path):
        meta_dir = tmp_path / "metadata"
        meta_dir.mkdir()
        (meta_dir / "dataset_v001.json").write_text(
            json.dumps({"label_type": "unlabeled"}), encoding="utf-8"
        )
        with pytest.raises(LabelSchemaError, match="unlabeled"):
            LabelConfig.resolve(_config(tmp_path))

    def test_missing_metadata_refused(self, tmp_path):
        with pytest.raises(LabelSchemaError, match="not found"):
            LabelConfig.resolve(_config(tmp_path))

    def test_metadata_without_schema_refused(self, tmp_path):
        meta_dir = tmp_path / "metadata"
        meta_dir.mkdir()
        (meta_dir / "dataset_v001.json").write_text("{}", encoding="utf-8")
        with pytest.raises(LabelSchemaError, match="label_schema"):
            LabelConfig.resolve(_config(tmp_path))
