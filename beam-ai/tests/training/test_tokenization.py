"""Tokenization tests: padding, truncation, attention masks, determinism."""

from __future__ import annotations

import pytest

pytest.importorskip("transformers")


class TestEncoding:
    def test_batch_pads_to_longest(self, tiny_tokenizer):
        encoded = tiny_tokenizer.encode_batch(["short", "a much longer sentence here"])
        mask_sums = encoded["attention_mask"].sum(dim=1).tolist()
        width = encoded["input_ids"].shape[1]
        assert encoded["input_ids"].shape[0] == 2
        assert max(mask_sums) <= width
        assert min(mask_sums) < max(mask_sums)

    def test_truncation_enforced(self, tiny_tokenizer):
        long_text = "word " * 200
        encoded = tiny_tokenizer.encode_batch([long_text])
        assert encoded["input_ids"].shape[1] == tiny_tokenizer.max_length

    def test_attention_mask_matches_padding(self, tiny_tokenizer):
        encoded = tiny_tokenizer.encode_batch(["I feel happy today"])
        input_ids = encoded["input_ids"][0]
        mask = encoded["attention_mask"][0]
        pad_id = tiny_tokenizer.tokenizer.pad_token_id
        assert ((input_ids != pad_id).long() == mask).all()

    def test_deterministic_encoding(self, tiny_tokenizer):
        texts = ["I feel happy today", "so sad right now"]
        first = tiny_tokenizer.encode_batch(texts)
        second = tiny_tokenizer.encode_batch(texts)
        assert first["input_ids"].tolist() == second["input_ids"].tolist()
        assert first["attention_mask"].tolist() == second["attention_mask"].tolist()

    def test_max_length_respected_for_config(self, tiny_tokenizer):
        assert tiny_tokenizer.max_length == 32
