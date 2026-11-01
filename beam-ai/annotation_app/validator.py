"""Validation utilities for annotations."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .config import ANNOTATIONS_DIR, SOURCE_DATA_PATH, validate_annotator_id
from .loader import Schema, SourceRecord, load_schema, load_source_records


class ValidationError(Exception):
    """Raised when an annotation fails validation."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class AnnotationValidator:
    """Validates annotations against schema and business rules."""

    def __init__(self, schema: Schema, source_records: list[SourceRecord]):
        self.schema = schema
        self.source_ids = {r.record_id for r in source_records}
        self.existing_annotations: dict[str, dict] = {}

    def load_existing(self, annotator_id: str) -> None:
        """Load existing annotations for an annotator to check duplicates."""
        self.existing_annotations.clear()
        path = ANNOTATIONS_DIR / f"{annotator_id}.jsonl"
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ann = json.loads(line)
                    rid = ann.get("record_id")
                    if rid:
                        self.existing_annotations[rid] = ann
                except json.JSONDecodeError:
                    continue

    def validate(self, annotation: dict) -> None:
        """Validate an annotation record. Raises ValidationError on failure."""
        for field in self.schema.required:
            if field not in annotation:
                raise ValidationError(field, f"Required field '{field}' is missing")

        record_id = str(annotation.get("record_id", ""))
        if record_id not in self.source_ids:
            raise ValidationError("record_id", f"Record ID '{record_id}' not found in source dataset")

        primary = str(annotation.get("primary_emotion", ""))
        if primary not in self.schema.primary_emotions:
            raise ValidationError("primary_emotion", f"'{primary}' is not a valid emotion ID")

        secondary = annotation.get("secondary_emotion")
        if secondary is not None:
            secondary_str = str(secondary)
            if secondary_str not in self.schema.secondary_emotions:
                raise ValidationError("secondary_emotion", f"'{secondary_str}' is not a valid emotion ID")
            if secondary_str == primary:
                raise ValidationError("secondary_emotion", "Secondary emotion must differ from primary emotion")

        intensity = annotation.get("intensity")
        if not isinstance(intensity, int) or not (self.schema.get_intensity_range()[0] <= intensity <= self.schema.get_intensity_range()[1]):
            min_i, max_i = self.schema.get_intensity_range()
            raise ValidationError("intensity", f"Intensity must be an integer between {min_i} and {max_i}")

        confidence = annotation.get("confidence")
        if not isinstance(confidence, int) or not (self.schema.get_confidence_range()[0] <= confidence <= self.schema.get_confidence_range()[1]):
            min_c, max_c = self.schema.get_confidence_range()
            raise ValidationError("confidence", f"Confidence must be an integer between {min_c} and {max_c}")

        flags = annotation.get("context_flags", [])
        if not isinstance(flags, list):
            raise ValidationError("context_flags", "Context flags must be a list")
        for flag in flags:
            if flag not in self.schema.context_flags:
                raise ValidationError("context_flags", f"'{flag}' is not a valid context flag")

        annotator_id = str(annotation.get("annotator_id", ""))
        if not validate_annotator_id(annotator_id):
            raise ValidationError("annotator_id", "Annotator ID must be alphanumeric with underscores")

        ts = annotation.get("annotation_timestamp")
        if not ts or not str(ts).endswith("Z"):
            raise ValidationError("annotation_timestamp", "Timestamp must be ISO-8601 UTC format ending with 'Z'")

        notes = annotation.get("notes")
        if notes is not None and not isinstance(notes, str):
            raise ValidationError("notes", "Notes must be a string or null")

        allowed_fields = set(self.schema.properties.keys()) | {"record_id", "text"}
        unknown = set(annotation.keys()) - allowed_fields
        if unknown:
            raise ValidationError("unknown_fields", f"Unknown fields: {', '.join(sorted(unknown))}")

    def check_duplicate(self, annotator_id: str, record_id: str) -> dict | None:
        """Check if annotation already exists. Returns existing annotation or None."""
        return self.existing_annotations.get(record_id)
