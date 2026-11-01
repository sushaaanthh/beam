"""Configuration for the B.E.A.M. annotation application."""
from __future__ import annotations

import os
from pathlib import Path

ANNOTATION_APP_DIR = Path(__file__).resolve().parent
BEAM_AI_DIR = ANNOTATION_APP_DIR.parent
PROJECT_ROOT = BEAM_AI_DIR.parent

TAXONOMY_PATH = PROJECT_ROOT / "beam-datasets" / "annotation" / "taxonomy.yaml"
SCHEMA_PATH = PROJECT_ROOT / "beam-datasets" / "annotation" / "schema.json"
GUIDELINES_PATH = PROJECT_ROOT / "beam-datasets" / "annotation" / "annotation_guidelines.md"
SOURCE_DATA_PATH = PROJECT_ROOT / "beam-datasets" / "raw" / "sample_reddit.jsonl"
ANNOTATIONS_DIR = PROJECT_ROOT / "beam-datasets" / "annotations" / "pilot"
MANIFEST_PATH = ANNOTATIONS_DIR / "pilot_manifest.json"

ANNOTATOR_ID = os.environ.get("ANNOTATOR_ID", "").strip().upper()


def validate_annotator_id(annotator_id: str) -> bool:
    """Validate annotator ID format: alphanumeric and underscores only."""
    if not annotator_id:
        return False
    return annotator_id.replace("_", "").isalnum()


def get_annotator_output_path(annotator_id: str) -> Path:
    """Get the output JSONL path for an annotator."""
    return ANNOTATIONS_DIR / f"{annotator_id}.jsonl"
