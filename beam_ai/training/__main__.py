"""CLI entry: python -m beam_ai.training --config <yaml>

Runs a REAL training job using the given configuration. Nothing runs
automatically; the bundled smoke configuration exists separately
(python -m beam_ai.training.smoke_test).
"""

from __future__ import annotations

import argparse
import sys

from beam_ai.training.config import TrainingConfig


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train a B.E.A.M. emotion classifier")
    parser.add_argument("--config", required=True, help="Path to training YAML")
    parser.add_argument(
        "--device",
        default=None,
        choices=["auto", "cpu", "cuda"],
        help="Override the configured device",
    )
    parser.add_argument("--dry-run", action="store_true", help="Load config/data/model then exit")
    args = parser.parse_args(argv)

    try:
        config = TrainingConfig.from_yaml(args.config)
    except Exception as exc:
        print(f"CONFIG ERROR: {exc}")
        return 2
    if args.device:
        config.device = args.device  # type: ignore[assignment]

    from beam_ai.models.factory import create_model
    from beam_ai.training.data import load_dataset_splits
    from beam_ai.training.labels import LabelConfig
    from beam_ai.training.tokenization import TokenizerPipeline
    from beam_ai.training.tracker import ExperimentTracker
    from beam_ai.training.trainer import Trainer

    label_config = LabelConfig.resolve(config)
    print(f"labels: {label_config.label_to_id}")

    splits = load_dataset_splits(config, label_config)
    for name, data in splits.items():
        print(f"{name:11} {len(data):6d} rows (unlabeled-skipped={data.skipped_unlabeled})")

    if args.dry_run:
        from beam_ai.models.factory import create_model

        tokenizer = None
        if config.model_init == "tiny_random":
            from beam_ai.training.offline import build_tiny_tokenizer
            from transformers import PreTrainedTokenizerFast  # noqa: F401

            tokenizer = TokenizerPipeline(
                build_tiny_tokenizer(), max_length=config.max_sequence_length
            )
        model = create_model(config, label_config, tokenizer=tokenizer)
        print(f"dry-run OK: {type(model.hf_model).__name__} on {model.device}")
        return 0

    result = Trainer(config, label_config, tracker=ExperimentTracker()).train()
    print("=" * 60)
    print(f"training complete: run={result.run_id}")
    print(f"best epoch       : {result.best_epoch}")
    print("best val metrics : " + ", ".join(
        f"{k}={v:.4f}" for k, v in sorted(result.best_val_metrics.items()) if isinstance(v, float)
    ))
    print(f"artifact         : {result.artifact_dir}")
    print(f"duration         : {result.duration_seconds:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
