"""Dataset loader tests."""

from __future__ import annotations

import json

import pytest

from beam_ai.training.config import TrainingConfig
from beam_ai.training.data import build_sampler, load_split
from beam_ai.training.labels import LabelSchemaError, LabelConfig


def _config(split_file):
    return TrainingConfig(
        model_name="m",
        dataset_version="v001",
        datasets_root=split_file.parent,
        split_files={"train": split_file},
    )


class TestLoadSplit:
    def test_loads_texts_and_label_ids(self, split_file, label_config):
        data = load_split(split_file, split="train", label_config=label_config)
        assert len(data) == 12
        assert all(label in label_config.label_to_id for label in data.labels)
        assert data.label_ids == [label_config.id_for(l) for l in data.labels]
        assert data.skipped_unlabeled == 0

    def test_unlabeled_rows_counted_and_skipped(self, tmp_path, label_config):
        path = tmp_path / "s.jsonl"
        rows = [
            {"record_id": "1", "cleaned_text": "happy text", "label": "joy"},
            {"record_id": "2", "cleaned_text": "no label here"},
            {"record_id": "3", "cleaned_text": "", "label": "joy"},
        ]
        path.write_text("\n".join(__import__("json").dumps(r) for r in rows), encoding="utf-8")
        data = load_split(path, split="train", label_config=label_config)
        assert len(data) == 1
        assert data.skipped_unlabeled == 2

    def test_unknown_label_rejected(self, split_file, label_config):
        bad = split_file.parent / "bad.jsonl"
        row = {"record_id": "x", "cleaned_text": "text", "label": "euphoria"}
        bad.write_text(json.dumps(row), encoding="utf-8")
        with pytest.raises(LabelSchemaError, match="unknown label"):
            load_split(bad, split="train", label_config=label_config)

    def test_missing_file(self, tmp_path, label_config):
        with pytest.raises(FileNotFoundError):
            load_split(tmp_path / "ghost.jsonl", split="train", label_config=label_config)

    def test_text_column_override(self, tmp_path, label_config):
        path = tmp_path / "alt.jsonl"
        row = {"record_id": "1", "raw_text": "using raw column", "label": "joy"}
        path.write_text(json.dumps(row), encoding="utf-8")
        data = load_split(path, split="train", label_config=label_config, text_column="raw_text")
        assert data.texts == ["using raw column"]


class TestSampling:
    def test_none_returns_no_sampler(self):
        assert build_sampler([0, 1, 0], "none") is None

    def test_invalid_strategy_rejected(self):
        with pytest.raises(ValueError, match="sampling_strategy"):
            build_sampler([0], "smote_everything")

    def test_inverse_frequency_needs_torch(self):
        pytest.importorskip("torch")
        sampler = build_sampler([0, 0, 0, 1], "inverse_frequency")
        assert sampler is not None
        # minority class upweighted: weight ratio = count(majority)/count(minority) = 3
        weights = list(sampler.weights)
        assert weights[3] == pytest.approx(weights[0] * 3)
