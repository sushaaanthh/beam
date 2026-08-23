"""Smoke-test mode: verify the full pipeline in seconds, CPU-only.

Checks (per architecture spec):
  1. configuration loads
  2. dataset loads (train/validation/test)
  3. labels load with explicit mappings
  4. tokenizer initializes and encodes
  5. model factory initializes a model
  6. one batch passes through the model (forward + backward)

The smoke test uses an UNTRAINED randomly-initialised tiny model and a
clearly-synthetic fixture dataset. It proves plumbing works; it does NOT
train anything and reports NO quality metrics.
"""

from __future__ import annotations

import argparse
import sys

from beam_ai.training.config import TrainingConfig


def run_smoke_test(config_path: str) -> int:
    checks: list[tuple[str, bool, str]] = []

    def record(name: str, error: BaseException | None = None, detail: str = "") -> None:
        ok = error is None
        message = detail if ok else f"{type(error).__name__}: {error}"
        checks.append((name, ok, message))

    # 1. configuration ---------------------------------------------------
    config: TrainingConfig | None = None
    try:
        config = TrainingConfig.from_yaml(config_path)
        detail = f"{config.model_name} / dataset {config.dataset_version} / seed {config.random_seed}"
    except Exception as exc:  # noqa: BLE001 - report any failure honestly
        record("configuration loads", exc)
    else:
        record("configuration loads", None, detail)

    if config is None:
        _report(checks)
        return 1

    # 3. labels (before data so mappings exist) ----------------------------
    label_config = None
    try:
        from beam_ai.training.labels import LabelConfig

        label_config = LabelConfig.resolve(config)
        record(
            "labels load",
            None,
            f"{label_config.num_labels} classes -> {label_config.labels}",
        )
    except Exception as exc:
        record("labels load", exc)
        _report(checks)
        return 1

    # 2. dataset -----------------------------------------------------------
    splits = None
    try:
        from beam_ai.training.data import load_dataset_splits

        splits = load_dataset_splits(
            config,
            label_config,
            splits=("train", "validation", "test"),
        )
        counts = {name: len(data) for name, data in splits.items()}
        if any(count == 0 for count in counts.values()):
            raise ValueError(f"Empty split detected: {counts}")
        skipped = sum(d.skipped_unlabeled for d in splits.values())
        record("dataset loads", None, f"{counts}, unlabeled-skipped={skipped}")
    except Exception as exc:
        record("dataset loads", exc)
        _report(checks)
        return 1

    try:
        import torch  # noqa: F401
        from transformers import PreTrainedTokenizerFast  # noqa: F401

        from beam_ai.training.offline import build_tiny_tokenizer
        from beam_ai.training.tokenization import TokenizerPipeline
    except Exception as exc:
        record("tokenizer initializes", exc)
        _report(checks)
        return 1

    # 4. tokenizer ---------------------------------------------------------
    tokenizer_pipeline = None
    try:
        tokenizer_pipeline = TokenizerPipeline(
            build_tiny_tokenizer(),
            max_length=config.max_sequence_length,
        )
        sample = tokenizer_pipeline.encode_batch(["I feel happy today"])
        assert sample["input_ids"].shape[0] == 1
        record(
            "tokenizer initializes",
            None,
            f"vocab_size={tokenizer_pipeline.vocab_size}",
        )
    except Exception as exc:
        record("tokenizer initializes", exc)

    # 5. model factory --------------------------------------------------------
    model = None
    try:
        from beam_ai.models.factory import create_model

        model = create_model(config, label_config, tokenizer=tokenizer_pipeline)
        record(
            "model factory initializes",
            None,
            f"{type(model.hf_model).__name__} num_labels={model.num_labels} device={model.device}",
        )
    except Exception as exc:
        record("model factory initializes", exc)
        _report(checks)
        return 1

    # 6. one batch through the model -----------------------------------------
    try:
        texts = splits["train"].texts[: config.batch_size]
        labels = splits["train"].label_ids[: config.batch_size]
        batch = tokenizer_pipeline.encode_batch(texts)

        # Inference path: no_grad logits with expected shape.
        logits = model.forward_batch(batch["input_ids"], batch["attention_mask"])
        expected = (len(texts), label_config.num_labels)
        if tuple(logits.shape) != expected:
            raise AssertionError(f"logits shape {tuple(logits.shape)} != {expected}")

        # Training path: mirrors Trainer — grad-enabled forward/backward.
        model.hf_model.train()
        output = model.hf_model(
            input_ids=batch["input_ids"], attention_mask=batch["attention_mask"]
        )
        loss = torch.nn.functional.cross_entropy(output.logits, torch.tensor(labels))
        loss.backward()
        grads = sum(1 for p in model.hf_model.parameters() if p.grad is not None)
        if grads == 0:
            raise AssertionError("backward pass produced no gradients")
        record(
            "one batch forward+backward",
            None,
            f"logits={tuple(logits.shape)}, loss={float(loss.detach()):.4f}, grad_tensors={grads}",
        )
    except Exception as exc:
        record("one batch forward+backward", exc)

    _report(checks)
    return 0 if all(ok for _, ok, _ in checks) else 1


def _report(checks: list[tuple[str, bool, str]]) -> None:
    print("=" * 64)
    print("B.E.A.M. SMOKE TEST")
    print("(untrained tiny model + synthetic fixture — plumbing only)")
    print("=" * 64)
    failed = False
    for name, ok, message in checks:
        status = "PASS" if ok else "FAIL"
        failed |= not ok
        print(f"  [{status}] {name}: {message}")
    print("-" * 64)
    print("SMOKE TEST " + ("FAILED" if failed else "PASSED"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="B.E.A.M. training smoke test")
    parser.add_argument(
        "--config",
        default=None,
        help="YAML config path (default: bundled smoke_test.yaml)",
    )
    args = parser.parse_args(argv)

    config_path = args.config
    if config_path is None:
        from pathlib import Path

        config_path = str(
            Path(__file__).resolve().parents[2] / "beam-ai" / "configs" / "smoke_test.yaml"
        )
    return run_smoke_test(str(config_path))


if __name__ == "__main__":
    sys.exit(main())
