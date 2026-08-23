"""Configurable emotion label system.

The final label set depends on whichever labeled dataset is selected for
training, so labels are NEVER hardcoded here. Resolution order:

1. explicit ``labels`` list in the training config / YAML;
2. ``label_schema.labels`` inside the dataset metadata produced by the
   dataset pipeline (``beam-datasets/metadata/dataset_<v>.json``);
3. otherwise: a clear error — unlabeled datasets cannot define classes.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:  # pragma: no cover
    from beam_ai.training.config import TrainingConfig


class LabelSchemaError(ValueError):
    """Raised when no usable label schema can be resolved."""


class LabelConfig(BaseModel):
    labels: list[str] = Field(..., min_length=2)

    # ---------- mappings (explicit by design) ----------

    @property
    def label_to_id(self) -> dict[str, int]:
        return {label: index for index, label in enumerate(self.labels)}

    @property
    def id_to_label(self) -> dict[int, str]:
        return {index: label for index, label in enumerate(self.labels)}

    @property
    def num_labels(self) -> int:
        return len(self.labels)

    def id_for(self, label: str) -> int:
        try:
            return self.label_to_id[label]
        except KeyError:
            raise LabelSchemaError(
                f"Unknown label {label!r}. Known labels: {self.labels}"
            ) from None

    def label_for(self, label_id: int) -> str:
        try:
            return self.id_to_label[label_id]
        except KeyError:
            raise LabelSchemaError(
                f"Unknown label id {label_id!r}. Valid ids: 0..{len(self.labels) - 1}"
            ) from None

    # ---------- resolution ----------

    @classmethod
    def resolve(cls, config: "TrainingConfig") -> "LabelConfig":
        """Resolve the label schema from the training config or dataset metadata."""
        if config.labels:
            return cls(labels=list(config.labels))

        metadata_file = config.metadata_file
        if not metadata_file.exists():
            raise LabelSchemaError(
                f"No explicit labels configured and dataset metadata not found at "
                f"{metadata_file}. Provide 'labels' in the training configuration."
            )
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))

        if metadata.get("label_type") == "unlabeled":
            raise LabelSchemaError(
                f"Dataset {config.dataset_version} is marked 'unlabeled'. Emotion "
                f"classification requires a labeled dataset; add a label schema to "
                f"the metadata or supply explicit labels in the training config."
            )

        schema = metadata.get("label_schema") or {}
        labels = schema.get("labels") if isinstance(schema, dict) else None
        if not labels and isinstance(metadata.get("labels"), list):
            labels = metadata["labels"]
        if not labels:
            raise LabelSchemaError(
                f"Dataset metadata {metadata_file} contains no 'label_schema.labels'. "
                f"Provide explicit labels in the training configuration instead."
            )
        return cls(labels=[str(label) for label in labels])
