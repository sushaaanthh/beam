"""Run evaluation of a saved artifact against a dataset split.

Rules:
- if no trained artifact exists -> explicit ``ArtifactNotFoundError``;
  nothing is fabricated;
- metrics are computed from actual model outputs on the chosen split;
- results are written to ``<artifact>/evaluation.json`` and, when run via
  the registry helper, flip status training -> validated.

CLI::

    python -m beam_ai.evaluation.evaluate --artifact beam-models/<name>/v001 \
        [--split-file path.jsonl] [--batch-size 32] [--device auto]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


class ArtifactNotFoundError(FileNotFoundError):
    """No trained model artifact is available at the requested location."""


@dataclass
class EvaluationReport:
    artifact_dir: Path
    split_file: Path
    sample_count: int
    skipped_unlabeled: int
    metrics: dict

    def to_dict(self) -> dict:
        return {
            "artifact_dir": str(self.artifact_dir),
            "split_file": str(self.split_file),
            "sample_count": self.sample_count,
            "skipped_unlabeled": self.skipped_unlabeled,
            "metrics": self.metrics,
        }


def require_artifact(artifact_dir: str | Path) -> Path:
    directory = Path(artifact_dir)
    if not (directory / "metadata.json").exists() or not any(directory.glob("*.safetensors")) and not (
        directory / "pytorch_model.bin"
    ).exists():
        raise ArtifactNotFoundError(
            f"No trained model artifact available at '{directory}'. "
            f"Train a model first (python -m beam_ai.training --config ...) or "
            f"point --artifact at an existing versioned directory."
        )
    return directory


def collect_predictions(model, texts: list[str], batch_size: int = 32) -> list[int]:
    """Batched argmax ids — real forward passes only."""
    predictions: list[int] = []
    for start in range(0, len(texts), max(1, batch_size)):
        probabilities = model.predict_proba(texts[start : start + batch_size])
        predictions.extend(int(row.argmax()) for row in probabilities)
    return predictions


def evaluate_split(
    model,
    split_data,  # SplitData
    *,
    batch_size: int = 32,
) -> dict:
    y_true = list(split_data.label_ids or [])
    y_pred = collect_predictions(model, split_data.texts, batch_size=batch_size)
    return compute_metrics_safe(y_true, y_pred, model.labels.labels)


def compute_metrics_safe(y_true: list[int], y_pred: list[int], labels: list[str]) -> dict:
    from beam_ai.evaluation.metrics import compute_classification_metrics

    return compute_classification_metrics(y_true, y_pred, labels)


def evaluate_artifact(
    artifact_dir: str | Path,
    split_file: str | Path | None = None,
    *,
    text_column: str = "cleaned_text",
    label_column: str = "label",
    batch_size: int = 32,
    device: str = "auto",
) -> EvaluationReport:
    """Evaluate a saved artifact on a JSONL split. Real numbers or error."""
    from beam_ai.models.factory import load_model_from_artifact
    from beam_ai.training.data import load_split
    from beam_ai.training.labels import LabelConfig

    directory = require_artifact(artifact_dir)
    metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    label_config = LabelConfig(labels=metadata["labels"])

    split_path = Path(split_file) if split_file else _default_test_split(metadata)
    if not split_path.exists():
        raise FileNotFoundError(f"Split file for evaluation not found: {split_path}")

    split_data = load_split(
        split_path,
        split="test",
        label_config=label_config,
        text_column=text_column,
        label_column=label_column,
    )
    if len(split_data) == 0:
        raise ValueError(
            f"Split {split_path} contains no labeled rows; cannot evaluate."
        )

    model = load_model_from_artifact(directory, device=device)
    metrics = evaluate_split(model, split_data, batch_size=batch_size)

    report = EvaluationReport(
        artifact_dir=directory,
        split_file=split_path,
        sample_count=len(split_data),
        skipped_unlabeled=split_data.skipped_unlabeled,
        metrics=metrics,
    )

    # Persist next to the artifact so the registry can pick it up.
    metadata["metrics"] = metrics
    metadata["status"] = "validated" if metadata.get("status") == "training" else metadata.get("status")
    (directory / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (directory / "evaluation.json").write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report


def _default_test_split(metadata: dict) -> Path:
    from beam_ai.utils.paths import DATASETS_DIR

    version = metadata.get("dataset_version") or "v001"
    return DATASETS_DIR / "splits" / f"dataset_{version}_test.jsonl"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate a saved B.E.A.M. model artifact")
    parser.add_argument("--artifact", required=True, help="Path like beam-models/<name>/v001")
    parser.add_argument("--split-file", default=None, help="JSONL split (default: test split of the artifact's dataset)")
    parser.add_argument("--text-column", default="cleaned_text")
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", default="auto")
    args = parser.parse_args(argv)

    try:
        report = evaluate_artifact(
            args.artifact,
            args.split_file,
            text_column=args.text_column,
            label_column=args.label_column,
            batch_size=args.batch_size,
            device=args.device,
        )
    except ArtifactNotFoundError as exc:
        print(f"EVALUATION UNAVAILABLE: {exc}")
        return 2

    print(json.dumps(report.metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
