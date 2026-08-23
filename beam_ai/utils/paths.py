"""Canonical filesystem locations for the AI workspace."""

from __future__ import annotations

from pathlib import Path

# beam_ai/utils/paths.py -> parents[0]=utils, [1]=beam_ai, [2]=repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

DATASETS_DIR = REPO_ROOT / "beam-datasets"
MODELS_DIR = REPO_ROOT / "beam-models"


def metadata_path(dataset_version: str) -> Path:
    return DATASETS_DIR / "metadata" / f"dataset_{dataset_version}.json"


def split_path(dataset_version: str, split: str) -> Path:
    return DATASETS_DIR / "splits" / f"dataset_{dataset_version}_{split}.jsonl"


def model_root(model_name: str) -> Path:
    return MODELS_DIR / model_name
