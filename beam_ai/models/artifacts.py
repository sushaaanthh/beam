"""Model artifact persistence under beam-models/.

Layout per spec::

    beam-models/<model-name>/v001/
        config.json           # HuggingFace model architecture config
        training_config.json  # training configuration snapshot
        metadata.json         # registry-grade metadata + REAL metrics or null
        tokenizer files       # HF save_pretrained output
        model files           # weights (safetensors)
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from beam_ai.utils.paths import MODELS_DIR

VERSION_RE = re.compile(r"^v(\d{3,})$")
ARTIFACT_VERSION = "artifact-1.0"


def next_model_version(model_name: str, models_root: Path | None = None) -> str:
    """Return the next free version folder name for a model (v001...)."""
    root = (models_root or MODELS_DIR) / model_name
    if not root.exists():
        return "v001"
    versions = [
        int(VERSION_RE.match(p.name).group(1))
        for p in root.iterdir()
        if p.is_dir() and VERSION_RE.match(p.name)
    ]
    return f"v{max(versions, default=0) + 1:03d}"


def artifact_dir_for(model_name: str, version: str, models_root: Path | None = None) -> Path:
    return (models_root or MODELS_DIR) / model_name / version


def save_artifact(
    model,  # HFEmotionModel
    directory: str | Path,
    *,
    training_config_snapshot: dict | None = None,
    dataset_version: str | None = None,
    metrics: dict | None = None,
    status: str = "training",
) -> Path:
    """Persist a complete, reloadable artifact.

    ``metrics`` MUST be either None ("not measured yet") or real measured
    values produced by beam_ai.evaluation — never placeholders.
    """
    import json

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    model.hf_model.save_pretrained(str(directory))
    model.tokenizer_pipeline.tokenizer.save_pretrained(str(directory))

    snapshot = training_config_snapshot or {}
    metadata = {
        "schema_version": ARTIFACT_VERSION,
        "model_name": snapshot.get("model_name", model.__class__.__name__),
        "model_version": snapshot.get("model_version"),
        "task": "emotion_classification",
        "dataset_version": dataset_version or snapshot.get("dataset_version"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "labels": list(model.labels.labels),
        "num_labels": model.num_labels,
        "label_to_id": model.labels.label_to_id,
        "max_sequence_length": model.tokenizer_pipeline.max_length,
        "training_config": snapshot,
        # Honesty contract: null until a real evaluation has measured it.
        "metrics": metrics,
        "status": status,
        "untrained_weights": bool(snapshot.get("model_init") == "tiny_random"),
    }
    (directory / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if training_config_snapshot:
        # NOTE: must NOT be named config.json — that filename belongs to
        # the HuggingFace model config and is required to reload weights.
        (directory / "training_config.json").write_text(
            json.dumps(training_config_snapshot, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    return directory


def load_artifact_metadata(artifact_dir: str | Path) -> dict:
    path = Path(artifact_dir) / "metadata.json"
    if not path.exists():
        raise FileNotFoundError(f"No trained model artifact available at {path.parent}")
    return json.loads(path.read_text(encoding="utf-8"))
