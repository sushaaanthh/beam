"""Offline helpers for smoke tests: tiny BERT-style tokenizer, in-memory.

Transformers v5 no longer reliably builds a fast tokenizer from a bare
``vocab.txt``, so we construct the WordPiece engine explicitly via the
``tokenizers`` library. Result: a fully deterministic, network-free
tokenizer whose word list covers the synthetic smoke/test fixtures.

Special token ids follow standard BERT positions:
[PAD]=0, [UNK]=100, [CLS]=101, [SEP]=102, [MASK]=103.
"""

from __future__ import annotations

SPECIAL_TOKENS = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]

BASE_WORDS = [
    "i", "am", "is", "are", "was", "feel", "feeling", "felt", "so", "very",
    "happy", "joy", "glad", "sad", "down", "angry", "mad", "fear", "scared",
    "neutral", "ok", "fine", "today", "now", "the", "a", "and", "but",
    "not", "no", "yes", "good", "bad", "great", "terrible", "love", "hate",
    "this", "that", "it", "me", "my", "you", "we", "they", "he", "she",
    "report", "desk", "meeting", "scheduled", "tomorrow", "news", "makes",
]

FILLER = [f"tok{i}" for i in range(99)]


def build_vocab_dict() -> dict[str, int]:
    """Ordered token -> id with standard special-token positions."""
    vocab: dict[str, int] = {"[PAD]": 0}
    for index, filler in enumerate(FILLER, start=1):  # ids 1..99
        vocab[filler] = index
    vocab["[UNK]"] = 100
    vocab["[CLS]"] = 101
    vocab["[SEP]"] = 102
    vocab["[MASK]"] = 103
    next_id = 104
    for token in SPECIAL_TOKENS + BASE_WORDS:
        if token not in vocab:
            vocab[token] = next_id
            next_id += 1
    for char in "abcdefghijklmnopqrstuvwxyz":
        piece = f"##{char}"
        if piece not in vocab:
            vocab[piece] = next_id
            next_id += 1
    return vocab


def build_tiny_tokenizer():
    """Return a ``PreTrainedTokenizerFast`` with a small local WordPiece vocab."""
    from tokenizers import Tokenizer
    from tokenizers.models import WordPiece
    from tokenizers.normalizers import BertNormalizer
    from tokenizers.pre_tokenizers import BertPreTokenizer
    from tokenizers.processors import TemplateProcessing
    from transformers import PreTrainedTokenizerFast

    vocab = build_vocab_dict()
    engine = Tokenizer(
        WordPiece(
            vocab,
            unk_token="[UNK]",
            continuing_subword_prefix="##",
            max_input_chars_per_word=100,
        )
    )
    engine.normalizer = BertNormalizer(lowercase=True)
    engine.pre_tokenizer = BertPreTokenizer()
    engine.post_processor = TemplateProcessing(
        single="[CLS] $A [SEP]",
        pair="[CLS] $A [SEP] $B:1 [SEP]:1",
        special_tokens=[
            ("[CLS]", vocab["[CLS]"]),
            ("[SEP]", vocab["[SEP]"]),
        ],
    )
    return PreTrainedTokenizerFast(
        tokenizer_object=engine,
        pad_token="[PAD]",
        unk_token="[UNK]",
        cls_token="[CLS]",
        sep_token="[SEP]",
        mask_token="[MASK]",
        model_max_length=512,
    )
