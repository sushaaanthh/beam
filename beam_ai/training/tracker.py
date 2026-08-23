"""Lightweight JSONL experiment tracking (MLflow-compatible seam).

One JSON object per training run / epoch at
``beam-models/experiments/runs.jsonl``. Records only facts the code
actually observed: configuration, seed, timestamps, wall-clock duration,
checkpoint paths and metrics produced by real evaluation passes.

No secrets are ever written here (configs contain none).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from beam_ai.utils.paths import MODELS_DIR


class ExperimentTracker:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else MODELS_DIR / "experiments" / "runs.jsonl"

    def new_run(self, *, model_name: str, dataset_version: str, config_snapshot: dict) -> str:
        run_id = f"{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
        record = {
            "event": "run_started",
            "run_id": run_id,
            "model_name": model_name,
            "model_version": config_snapshot.get("model_version"),
            "dataset_version": dataset_version,
            "random_seed": config_snapshot.get("random_seed"),
            "training_config": config_snapshot,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._append(record)
        return run_id

    def log_epoch(
        self,
        run_id: str,
        *,
        epoch: int,
        train_loss: float,
        val_metrics: dict,
        checkpoint_path: str | None = None,
        duration_seconds: float,
    ) -> None:
        self._append(
            {
                "event": "epoch_completed",
                "run_id": run_id,
                "epoch": epoch,
                "train_loss": train_loss,
                # Real values computed on the validation split this epoch.
                "val_metrics": {
                    key: value
                    for key, value in val_metrics.items()
                    if isinstance(value, (int, float))
                },
                "checkpoint_path": checkpoint_path,
                "duration_seconds": round(duration_seconds, 3),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def finalize_run(
        self,
        run_id: str,
        *,
        status: str,
        metrics: dict | None,
        artifact_path: str | None,
        duration_seconds: float,
    ) -> None:
        self._append(
            {
                "event": "run_finished",
                "run_id": run_id,
                "status": status,
                # None until a real evaluation has measured something.
                "metrics": metrics,
                "artifact_path": artifact_path,
                "training_duration_seconds": round(duration_seconds, 3),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def _append(self, record: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
