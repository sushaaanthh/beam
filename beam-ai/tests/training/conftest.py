"""Shared fixtures for the AI infrastructure tests (CPU-only)."""

from __future__ import annotations

import json

import pytest


@pytest.fixture(scope="session")
def label_config():
    from beam_ai.training.labels import LabelConfig

    return LabelConfig(labels=["joy", "sadness", "anger", "neutral"])


@pytest.fixture(scope="session")
def tiny_tokenizer():
    pytest.importorskip("torch")  # noqa: F841 - guard heavy deps together
    pytest.importorskip("transformers")
    from beam_ai.training.offline import build_tiny_tokenizer
    from beam_ai.training.tokenization import TokenizerPipeline

    return TokenizerPipeline(build_tiny_tokenizer(), max_length=32)


@pytest.fixture(scope="session")
def tiny_model(label_config, tiny_tokenizer):
    """Untrained randomly-initialised tiny DistilBERT (plumbing checks only)."""
    from transformers import DistilBertConfig, DistilBertForSequenceClassification

    from beam_ai.models.base import HFEmotionModel

    hf_config = DistilBertConfig(
        vocab_size=tiny_tokenizer.vocab_size,
        n_layers=2,
        n_heads=2,
        dim=64,
        hidden_dim=128,
        max_position_embeddings=40,
        num_labels=label_config.num_labels,
    )
    return HFEmotionModel(
        DistilBertForSequenceClassification(hf_config), tiny_tokenizer, label_config
    )


@pytest.fixture()
def split_file(tmp_path):
    rows = []
    templates = {
        "joy": ["I feel so happy today", "Glad and full of joy"],
        "sadness": ["I feel sad and down", "Terrible news makes me sad"],
        "anger": ["I am angry about this", "This mess makes me mad"],
        "neutral": ["The report is on the desk", "Meeting scheduled tomorrow"],
    }
    index = 0
    for label, phrases in templates.items():
        for i in range(3):
            rows.append(
                {
                    "record_id": f"r{index:03d}",
                    "cleaned_text": f"{phrases[i % len(phrases)]} variant {i}",
                    "label": label,
                }
            )
            index += 1
    path = tmp_path / "split.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return path
