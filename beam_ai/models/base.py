"""BaseEmotionModel — the clean seam between training pipeline and models.

Any future emotion classifier (BERT / RoBERTa / DistilBERT / ...) plugs
in by satisfying this interface. The concrete implementation today wraps
any HuggingFace ``AutoModelForSequenceClassification`` so the three
families above work without touching the trainer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import numpy as np

from beam_ai.training.labels import LabelConfig
from beam_ai.training.tokenization import TokenizerPipeline
from beam_ai.utils.device import resolve_device


class BaseEmotionModel(ABC):
    """Common contract used by Trainer, Evaluator and InferenceService."""

    labels: LabelConfig
    tokenizer_pipeline: TokenizerPipeline
    device: str

    @abstractmethod
    def forward_batch(self, input_ids, attention_mask):  # -> logits tensor
        ...

    @abstractmethod
    def predict_proba(self, texts: list[str]) -> np.ndarray:
        """Return softmax probabilities shaped [n_texts, n_labels]."""

    @abstractmethod
    def save(self, directory: str | Path) -> Path:
        """Persist weights + tokenizer + label schema to an artifact dir."""

    @property
    @abstractmethod
    def num_labels(self) -> int:
        ...

    # ---------- shared helpers ----------

    def predict(self, texts: list[str]) -> list[tuple[str, float]]:
        """Greedy (label, confidence) pairs — real softmax outputs."""
        probabilities = self.predict_proba(texts)
        results: list[tuple[str, float]] = []
        for row in probabilities:
            best_id = int(np.argmax(row))
            results.append((self.labels.label_for(best_id), float(row[best_id])))
        return results

    def _move_to_device(self) -> None:
        try:
            import torch
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("PyTorch is required to run models.") from exc
        self.torch_ref = torch  # kept for subclasses; avoids re-import churn
        if hasattr(self, "hf_model") and self.hf_model is not None:
            self.hf_model.to(device=torch.device(self.device))

    def model_config_summary(self) -> dict[str, Any]:
        return {
            "labels": list(self.labels.labels),
            "num_labels": self.num_labels,
            "device": self.device,
            "max_sequence_length": self.tokenizer_pipeline.max_length,
            "vocab_size": self.tokenizer_pipeline.vocab_size,
        }


class HFEmotionModel(BaseEmotionModel):
    """Wraps any HF sequence-classification checkpoint."""

    def __init__(
        self,
        hf_model,
        tokenizer_pipeline: TokenizerPipeline,
        labels: LabelConfig,
        device: str = "auto",
    ) -> None:
        self.hf_model = hf_model
        self.tokenizer_pipeline = tokenizer_pipeline
        self.labels = labels
        self.device = resolve_device(device)
        self._move_to_device()

    @property
    def num_labels(self) -> int:
        return self.labels.num_labels

    def forward_batch(self, input_ids, attention_mask):
        self.hf_model.eval()
        with self.torch_ref.no_grad():
            output = self.hf_model(input_ids=input_ids, attention_mask=attention_mask)
        return output.logits

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        import torch

        batch = self.tokenizer_pipeline.encode_batch(list(texts))
        logits = self.forward_batch(batch["input_ids"].to(self.device), batch["attention_mask"].to(self.device))
        return torch.softmax(logits, dim=-1).detach().cpu().numpy()

    def save(self, directory: str | Path) -> Path:
        from beam_ai.models.artifacts import save_artifact

        return save_artifact(self, Path(directory))
