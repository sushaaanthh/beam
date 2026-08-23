"""HuggingFace tokenizer pipeline.

Wraps ``AutoTokenizer`` and guarantees deterministic preprocessing:
fixed truncation length, batch-longest padding (deterministic given a
batch), explicit attention masks, sorted-free stable input order.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from transformers import PreTrainedTokenizerBase


class TokenizerPipeline:
    """Deterministic encode step shared by training and inference."""

    def __init__(self, tokenizer: "PreTrainedTokenizerBase", max_length: int) -> None:
        self.tokenizer = tokenizer
        self.max_length = max_length

    @classmethod
    def from_pretrained(cls, name_or_path: str, max_length: int) -> "TokenizerPipeline":
        try:
            from transformers import AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "transformers is required for tokenization. "
                "Install beam-ai/requirements.txt."
            ) from exc
        return cls(AutoTokenizer.from_pretrained(name_or_path), max_length=max_length)

    @property
    def vocab_size(self) -> int:
        return len(self.tokenizer)

    def encode_batch(self, texts: list[str]) -> dict:
        """Encode texts -> {input_ids, attention_mask} tensors.

        padding=True pads to the longest sequence in the batch; truncation
        cuts to ``max_length``. Attention masks make padding explicit for
        the model.
        """
        encoded = self.tokenizer(
            list(texts),
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        # Keep only what models need — deterministic column order.
        return {
            "input_ids": encoded["input_ids"],
            "attention_mask": encoded["attention_mask"],
        }
