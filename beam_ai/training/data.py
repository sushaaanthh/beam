"""Dataset loading for training/evaluation.

Consumes the JSONL split files produced by the dataset engineering
pipeline (``beam-datasets/splits/dataset_<v>_{train,validation,test}.jsonl``).

Rows lacking a label are counted and skipped (reported, never silently
mixed in). Label ids come exclusively from :class:`LabelConfig`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

from beam_ai.training.labels import LabelSchemaError

if TYPE_CHECKING:  # pragma: no cover
    from beam_ai.training.config import TrainingConfig
    from beam_ai.training.labels import LabelConfig

VALID_SPLITS = ("train", "validation", "test")


@dataclass
class SplitData:
    name: str
    texts: list[str]
    record_ids: list[str]
    labels: list[str] = field(default_factory=list)
    label_ids: list[int] | None = None
    skipped_unlabeled: int = 0
    source_file: str = ""

    def __len__(self) -> int:
        return len(self.texts)

    @property
    def class_counts(self) -> dict[str, int]:
        counts = {label: 0 for label in self.labels}
        for label in self.labels:
            counts[label] += 1
        return counts


def iter_jsonl(path: Path) -> Iterator[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Split file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON ({exc})") from exc


def load_split(
    path: str | Path,
    *,
    split: str,
    label_config: "LabelConfig",
    text_column: str = "cleaned_text",
    label_column: str = "label",
) -> SplitData:
    """Load one split file into a validated SplitData."""
    path = Path(path)
    texts: list[str] = []
    record_ids: list[str] = []
    labels: list[str] = []
    skipped = 0

    for row in iter_jsonl(path):
        text = row.get(text_column)
        if not isinstance(text, str) or not text.strip():
            skipped += 1
            continue
        raw_label = row.get(label_column)
        if raw_label is None or (isinstance(raw_label, str) and not raw_label.strip()):
            skipped += 1
            continue
        raw_label = str(raw_label).strip()
        if raw_label not in label_config.label_to_id:
            raise LabelSchemaError(
                f"{path.name}: record {row.get('record_id', '?')!r} carries unknown "
                f"label {raw_label!r} not present in the label schema."
            )
        texts.append(text)
        record_ids.append(str(row.get("record_id", "")))
        labels.append(raw_label)

    return SplitData(
        name=split,
        texts=texts,
        record_ids=record_ids,
        labels=labels,
        label_ids=[label_config.id_for(label) for label in labels],
        skipped_unlabeled=skipped,
        source_file=str(path),
    )


def load_dataset_splits(
    config: "TrainingConfig",
    label_config: "LabelConfig",
    splits: tuple[str, ...] = VALID_SPLITS,
) -> dict[str, SplitData]:
    loaded: dict[str, SplitData] = {}
    for split in splits:
        loaded[split] = load_split(
            config.split_file(split),
            split=split,
            label_config=label_config,
            text_column=config.text_column,
            label_column=config.label_column,
        )
    return loaded


def build_sampler(label_ids: list[int], strategy: str):
    """Optional sampling strategy for imbalanced classes.

    ``none``              -> plain sequential/shuffled DataLoader.
    ``inverse_frequency`` -> WeightedRandomSampler with per-sample weights
    inversely proportional to class frequency.

    Complex augmentation/resampling techniques are deliberately NOT added;
    enable them only when class distribution evidence justifies it.
    """
    if strategy == "none":
        return None
    if strategy == "inverse_frequency":
        try:
            from torch.utils.data import WeightedRandomSampler
        except ImportError as exc:
            raise RuntimeError("PyTorch is required for sampling strategies.") from exc

        counts: dict[int, int] = {}
        for label_id in label_ids:
            counts[label_id] = counts.get(label_id, 0) + 1
        total = len(label_ids)
        weights = [total / counts[label_id] for label_id in label_ids]
        return WeightedRandomSampler(weights, num_samples=total, replacement=True)
    raise ValueError(f"Unknown sampling_strategy {strategy!r}")
