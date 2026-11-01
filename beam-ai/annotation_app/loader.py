"""Data loading utilities for the annotation application."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .config import GUIDELINES_PATH, SCHEMA_PATH, SOURCE_DATA_PATH, TAXONOMY_PATH


class Taxonomy:
    """Loaded emotion taxonomy."""

    def __init__(self, data: dict):
        self._data = data
        self.version = str(data.get("taxonomy_version", ""))
        self.name = str(data.get("taxonomy_name", ""))
        self.emotions = [
            {
                "id": e["id"],
                "display_name": e["display_name"],
                "valence": e["valence"],
                "definition": e.get("definition", ""),
                "inclusion_criteria": e.get("inclusion_criteria", []),
                "exclusion_criteria": e.get("exclusion_criteria", []),
                "linguistic_indicators": e.get("linguistic_indicators", []),
                "behavioral_contextual_indicators": e.get("behavioral_contextual_indicators", []),
                "hedonic_eudaimonic_relationship": e.get("hedonic_eudaimonic_relationship", ""),
                "examples": e.get("examples", []),
                "confusing_neighbors": e.get("confusing_neighbors", []),
            }
            for e in data.get("emotions", [])
        ]
        self.ids = [e["id"] for e in self.emotions]
        self.by_id = {e["id"]: e for e in self.emotions}

    def get(self, emotion_id: str) -> dict | None:
        """Get emotion by ID."""
        return self.by_id.get(emotion_id)

    def validate_id(self, emotion_id: str) -> bool:
        """Check if emotion ID is valid."""
        return emotion_id in self.ids


def load_taxonomy() -> Taxonomy:
    """Load taxonomy from YAML."""
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Taxonomy(data)


class Schema:
    """Loaded JSON schema."""

    def __init__(self, data: dict):
        self._data = data
        self.title = data.get("title", "")
        self.required = data.get("required", [])
        self.properties = data.get("properties", {})
        self.context_flags = self.properties.get("context_flags", {}).get("items", {}).get("enum", [])
        self.primary_emotions = self.properties.get("primary_emotion", {}).get("enum", [])
        self.secondary_emotions = self.properties.get("secondary_emotion", {}).get("enum", [])

    def get_intensity_range(self) -> tuple[int, int]:
        """Get valid intensity range."""
        prop = self.properties.get("intensity", {})
        return int(prop.get("minimum", 1)), int(prop.get("maximum", 5))

    def get_confidence_range(self) -> tuple[int, int]:
        """Get valid confidence range."""
        prop = self.properties.get("confidence", {})
        return int(prop.get("minimum", 1)), int(prop.get("maximum", 3))


def load_schema() -> Schema:
    """Load schema from JSON."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Schema(data)


class SourceRecord:
    """A single source record from the pilot dataset."""

    def __init__(self, data: dict):
        self.raw = data
        self.record_id = str(data.get("reddit_post_id") or data.get("reddit_comment_id", ""))
        self.record_type = "post" if "reddit_post_id" in data else "comment"
        self.subreddit = data.get("subreddit", "")
        self.title = data.get("title", "")
        self.body = data.get("body", "")
        self.body_status = data.get("body_status", "available")
        self.created_utc = data.get("created_utc", "")
        self.score = data.get("score")
        self.num_comments = data.get("num_comments")
        self.url = data.get("url", "")
        self.parent_id = data.get("parent_id")
        self.depth = data.get("depth")

    @property
    def display_text(self) -> str:
        """Get the text to display to annotators (title + body, no usernames)."""
        parts = []
        if self.title and self.record_type == "post":
            parts.append(self.title)
        if self.body and self.body_status == "available":
            parts.append(self.body)
        return "\n\n".join(parts) if parts else "(no text available)"

    @property
    def safe_metadata(self) -> dict:
        """Get safe metadata for display (no usernames)."""
        meta = {
            "record_type": self.record_type,
            "subreddit": self.subreddit,
            "created_utc": self.created_utc,
        }
        if self.record_type == "post":
            meta["score"] = self.score
            meta["num_comments"] = self.num_comments
        else:
            meta["parent_id"] = self.parent_id
            meta["depth"] = self.depth
        return meta


def load_source_records() -> list[SourceRecord]:
    """Load all source records from the pilot JSONL file."""
    records = []
    with open(SOURCE_DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            records.append(SourceRecord(data))
    return records


def generate_pilot_manifest(records: list[SourceRecord], taxonomy: Taxonomy, schema: Schema) -> dict:
    """Generate the pilot manifest."""
    record_ids = [r.record_id for r in records]
    record_ids.sort()

    manifest = {
        "dataset_version": "v001",
        "source_file": str(SOURCE_DATA_PATH),
        "source_record_count": len(records),
        "record_ids": record_ids,
        "taxonomy_version": taxonomy.version,
        "schema_version": schema.title,
        "creation_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    ids_string = ",".join(record_ids)
    manifest["record_ids_hash"] = hashlib.sha256(ids_string.encode()).hexdigest()[:16]

    return manifest


def load_pilot_manifest() -> dict | None:
    """Load existing pilot manifest if it exists."""
    if not MANIFEST_PATH.exists():
        return None
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
