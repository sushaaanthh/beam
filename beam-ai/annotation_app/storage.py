"""Annotation persistence and deduplication."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import ANNOTATIONS_DIR, ANNOTATOR_ID, validate_annotator_id
from .loader import load_pilot_manifest


class AnnotationStorage:
    """Handles annotation persistence with deduplication."""

    def __init__(self, annotator_id: str):
        if not validate_annotator_id(annotator_id):
            raise ValueError(f"Invalid annotator ID: {annotator_id}")
        self.annotator_id = annotator_id
        self.path = ANNOTATIONS_DIR / f"{annotator_id}.jsonl"
        self._index: dict[str, int] = {}
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Build index of existing annotations."""
        self._index.clear()
        if not self.path.exists():
            return
        with open(self.path, "r", encoding="utf-8") as f:
            pos = 0
            for line in f:
                line = line.strip()
                if not line:
                    pos += 1
                    continue
                try:
                    ann = json.loads(line)
                    rid = ann.get("record_id")
                    if rid:
                        self._index[rid] = pos
                except json.JSONDecodeError:
                    pass
                pos += 1

    def exists(self, record_id: str) -> bool:
        """Check if annotation for record_id already exists."""
        return record_id in self._index

    def load_all(self) -> list[dict]:
        """Load all annotations for this annotator."""
        if not self.path.exists():
            return []
        annotations = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    annotations.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return annotations

    def save(self, annotation: dict) -> None:
        """Save annotation. Updates existing or appends new."""
        if annotation.get("annotator_id") != self.annotator_id:
            raise ValueError("Annotation annotator_id does not match storage annotator_id")

        record_id = annotation.get("record_id")
        if not record_id:
            raise ValueError("Annotation missing record_id")

        if "annotation_timestamp" not in annotation:
            annotation["annotation_timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        line = json.dumps(annotation, ensure_ascii=False) + "\n"

        if record_id in self._index:
            self._update_existing(annotation, line)
        else:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line)
            self._index[record_id] = self.path.stat().st_size - len(line) if self.path.exists() else 0

    def _update_existing(self, annotation: dict, new_line: str) -> None:
        """Update an existing annotation by rewriting the file."""
        if not self.path.exists():
            return
        lines = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    existing = json.loads(line)
                    if existing.get("record_id") == annotation.get("record_id"):
                        lines.append(new_line.rstrip("\n"))
                    else:
                        lines.append(line)
                except json.JSONDecodeError:
                    lines.append(line)
        with open(self.path, "w", encoding="utf-8") as f:
            for l in lines:
                f.write(l + "\n")
        self._rebuild_index()

    def get_completed_count(self) -> int:
        """Get count of completed annotations."""
        return len(self._index)

    def get_annotation(self, record_id: str) -> dict | None:
        """Get existing annotation for a record if it exists."""
        if not self.path.exists():
            return None
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ann = json.loads(line)
                    if ann.get("record_id") == record_id:
                        return ann
                except json.JSONDecodeError:
                    continue
        return None
