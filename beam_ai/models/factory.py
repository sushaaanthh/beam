"""Model factory.

``pretrained``  -> AutoModelForSequenceClassification.from_pretrained(model_name)
                    works for BERT / RoBERTa / DistilBERT / any HF classifier
                    without changing the training pipeline.
``tiny_random`` -> tiny randomly-initialised DistilBERT built from a local
                    config. Offline, CPU-fast. Used ONLY by the smoke test
                    and unit tests to verify plumbing — never presented as
                    a trained model.
"""

from __future__ import annotations

from pathlib import Path

from beam_ai.models.base import HFEmotionModel
from beam_ai.training.config import TrainingConfig
from beam_ai.training.labels import LabelConfig
from beam_ai.training.tokenization import TokenizerPipeline


def create_model(
    config: TrainingConfig,
    label_config: LabelConfig,
    tokenizer: TokenizerPipeline | None = None,
) -> HFEmotionModel:
    """Build the model described by the configuration (weights NOT trained)."""
    try:
        from transformers import (
            AutoConfig,
            AutoModelForSequenceClassification,
            AutoTokenizer,
            DistilBertConfig,
            DistilBertForSequenceClassification,
        )
    except ImportError as exc:
        raise RuntimeError(
            "transformers/torch are required to instantiate models. "
            "Install beam-ai/requirements.txt."
        ) from exc

    num_labels = label_config.num_labels

    if config.model_init == "tiny_random":
        hf_config = DistilBertConfig(
            vocab_size=(tokenizer.vocab_size if tokenizer else 30522),
            n_layers=2,
            n_heads=2,
            dim=64,
            hidden_dim=128,
            max_position_embeddings=config.max_sequence_length + 8,
            num_labels=num_labels,
            seed=config.random_seed,
        )
        hf_model = DistilBertForSequenceClassification(hf_config)
        if tokenizer is None:
            raise ValueError("tiny_random init requires a tokenizer (offline vocab).")
        pipeline = tokenizer
        device = "cpu"  # tiny models exist for plumbing checks; keep them on CPU
    else:
        hf_config = AutoConfig.from_pretrained(config.model_name, num_labels=num_labels)
        hf_model = AutoModelForSequenceClassification.from_pretrained(
            config.model_name, config=hf_config
        )
        pipeline = tokenizer or TokenizerPipeline(
            AutoTokenizer.from_pretrained(config.tokenizer_source or config.model_name),
            max_length=config.max_sequence_length,
        )
        device = config.device

    return HFEmotionModel(
        hf_model=hf_model,
        tokenizer_pipeline=pipeline,
        labels=label_config,
        device=device,
    )


def load_model_from_artifact(artifact_dir: str | Path, device: str = "auto") -> HFEmotionModel:
    """Rebuild a model previously saved via artifacts.save_artifact."""
    artifact_dir = Path(artifact_dir)
    metadata_file = artifact_dir / "metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"No model artifact at {artifact_dir} (metadata.json missing).")

    import json

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("transformers is required to load artifacts.") from exc

    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    label_config = LabelConfig(labels=metadata["labels"])
    tokenizer_pipeline = TokenizerPipeline(
        AutoTokenizer.from_pretrained(str(artifact_dir)),
        max_length=int(metadata.get("max_sequence_length", 128)),
    )
    hf_model = AutoModelForSequenceClassification.from_pretrained(str(artifact_dir))
    return HFEmotionModel(hf_model, tokenizer_pipeline, label_config, device=device)
