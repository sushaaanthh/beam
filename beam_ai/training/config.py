"""Central training configuration.

Every tunable value lives here (or in a YAML file loaded through
``TrainingConfig.from_yaml``). Training code must read configuration from
this object and never hardcode hyperparameters.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator

from beam_ai.utils.paths import DATASETS_DIR, MODELS_DIR


class ConfigError(ValueError):
    """Raised when a training configuration is invalid."""


class TrainingConfig(BaseModel):
    """Single source of truth for one training run."""

    # --- model ---
    model_name: str = Field(..., description="Hub id or local path, e.g. distilbert-base-uncased")
    model_type: str = Field(
        default="transformer_classifier",
        description="Descriptive family tag (bert / roberta / distilbert ...); "
        "the factory resolves the concrete class automatically.",
    )
    model_init: Literal["pretrained", "tiny_random"] = "pretrained"
    tokenizer_source: str | None = Field(
        default=None,
        description="Optional tokenizer source override (local vocab dir for "
        "offline/tiny runs); defaults to model_name.",
    )

    # --- data ---
    dataset_version: str = Field(..., description="Dataset version under beam-datasets/, e.g. v001")
    datasets_root: Path = Field(default_factory=lambda: DATASETS_DIR)
    text_column: str = "cleaned_text"
    label_column: str = "label"
    labels: list[str] | None = Field(
        default=None,
        description="Explicit emotion label set. When None it is read from the "
        "dataset metadata label schema.",
    )
    split_files: dict[str, Path] | None = Field(
        default=None,
        description="Optional explicit split file overrides {train|validation|test: path}. "
        "Used by smoke tests; defaults to versioned files under <datasets_root>/splits/.",
    )

    # --- optimization ---
    learning_rate: float = 2e-5
    batch_size: int = 16
    epochs: int = 3
    max_sequence_length: int = 128
    random_seed: int = 42
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    gradient_clip_norm: float = 1.0

    # --- imbalance handling (kept OFF until evidence justifies them) ---
    class_weighting: Literal["none", "balanced"] = "none"
    sampling_strategy: Literal["none", "inverse_frequency"] = "none"

    # --- output / runtime ---
    output_directory: Path = Field(default_factory=lambda: MODELS_DIR)
    device: Literal["auto", "cpu", "cuda", "gpu"] = "auto"

    @field_validator("labels")
    @classmethod
    def _validate_labels(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        cleaned = [label.strip() for label in value]
        if len(cleaned) < 2:
            raise ConfigError("At least two labels are required.")
        if any(not label for label in cleaned):
            raise ConfigError("Labels must be non-empty strings.")
        if len(set(cleaned)) != len(cleaned):
            raise ConfigError(f"Duplicate labels are not allowed: {cleaned}")
        return cleaned

    @field_validator("learning_rate")
    @classmethod
    def _validate_lr(cls, value: float) -> float:
        if not 0 < value < 1:
            raise ConfigError(f"learning_rate must be in (0, 1), got {value}")
        return value

    @field_validator("batch_size")
    @classmethod
    def _validate_batch(cls, value: int) -> int:
        if value < 1:
            raise ConfigError("batch_size must be >= 1")
        return value

    @field_validator("epochs")
    @classmethod
    def _validate_epochs(cls, value: int) -> int:
        if value < 1:
            raise ConfigError("epochs must be >= 1")
        return value

    @field_validator("max_sequence_length")
    @classmethod
    def _validate_seq_len(cls, value: int) -> int:
        if value < 8 or value > 512:
            raise ConfigError("max_sequence_length must be within [8, 512]")
        return value

    @field_validator("warmup_ratio")
    @classmethod
    def _validate_warmup(cls, value: float) -> float:
        if not 0.0 <= value < 1.0:
            raise ConfigError("warmup_ratio must be within [0, 1)")
        return value

    @field_validator("weight_decay")
    @classmethod
    def _validate_weight_decay(cls, value: float) -> float:
        if value < 0:
            raise ConfigError("weight_decay must be >= 0")
        return value

    def to_serialisable(self) -> dict[str, Any]:
        """JSON-safe snapshot for experiment tracking."""
        return json.loads(self.model_dump_json())

    # ---------- derived paths ----------

    @property
    def metadata_file(self) -> Path:
        return self.datasets_root / "metadata" / f"dataset_{self.dataset_version}.json"

    def split_file(self, split: str) -> Path:
        allowed = ("train", "validation", "test")
        if split not in allowed:
            raise ConfigError(f"Unknown split {split!r}; expected one of {allowed}")
        if self.split_files and split in self.split_files:
            return Path(self.split_files[split])
        return self.datasets_root / "splits" / f"dataset_{self.dataset_version}_{split}.jsonl"

    # ---------- loaders ----------

    @classmethod
    def from_yaml(cls, path: str | Path) -> "TrainingConfig":
        path = Path(path)
        if not path.exists():
            raise ConfigError(f"Configuration file not found: {path}")
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ConfigError(f"Configuration root must be a mapping, got {type(raw).__name__}")
        config = cls(**raw)
        # Resolve relative paths against the YAML location, then repo root.
        config = cls(**_resolve_paths(json.loads(config.model_dump_json()), path))
        return config


def _resolve_paths(data: dict[str, Any], yaml_path: Path) -> dict[str, Any]:
    from beam_ai.utils.paths import REPO_ROOT

    yaml_dir = yaml_path.resolve().parent

    def resolve(value: Any) -> str:
        p = Path(value)
        return str(p if p.is_absolute() else (yaml_dir / p if (yaml_dir / p).exists() else REPO_ROOT / p))

    if isinstance(data.get("datasets_root"), (str, Path)):
        data["datasets_root"] = resolve(data["datasets_root"])
    if isinstance(data.get("output_directory"), (str, Path)):
        data["output_directory"] = resolve(data["output_directory"])
    if isinstance(data.get("split_files"), dict):
        data["split_files"] = {k: resolve(v) for k, v in data["split_files"].items()}
    return data
