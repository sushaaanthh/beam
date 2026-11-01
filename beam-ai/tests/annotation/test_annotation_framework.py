"""Tests for the B.E.A.M. annotation framework.

Validates:
- Taxonomy structure and uniqueness
- Schema constraints
- Example annotations
- Allowed values for emotions, intensity, confidence, and context flags
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from beam_ai.dataset_pipeline.io_utils import read_jsonl



TAXONOMY_PATH = PROJECT_ROOT / "beam-datasets" / "annotation" / "taxonomy.yaml"
SCHEMA_PATH = PROJECT_ROOT / "beam-datasets" / "annotation" / "schema.json"
EXAMPLES_PATH = PROJECT_ROOT / "beam-datasets" / "annotation" / "examples.jsonl"
GUIDELINES_PATH = PROJECT_ROOT / "beam-datasets" / "annotation" / "annotation_guidelines.md"
QUALITY_PATH = PROJECT_ROOT / "beam-datasets" / "annotation" / "quality_protocol.md"



def _load_yaml(path: Path) -> dict:
    """Load a YAML file without adding a runtime dependency."""
    try:
        import yaml
    except ImportError as exc:
        pytest.skip(f"PyYAML not installed: {exc}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))



class TestTaxonomyFile:
    """taxonomy.yaml must exist and be parseable."""

    def test_taxonomy_file_exists(self) -> None:
        assert TAXONOMY_PATH.exists(), f"Missing taxonomy file: {TAXONOMY_PATH}"

    def test_taxonomy_is_valid_yaml(self) -> None:
        data = _load_yaml(TAXONOMY_PATH)
        assert isinstance(data, dict)

    def test_taxonomy_version_present(self) -> None:
        data = _load_yaml(TAXONOMY_PATH)
        assert "taxonomy_version" in data
        assert "1.0.0" in str(data["taxonomy_version"])

    def test_taxonomy_has_ten_emotions(self) -> None:
        data = _load_yaml(TAXONOMY_PATH)
        emotions = data.get("emotions", [])
        assert len(emotions) == 10, f"Expected 10 emotions, found {len(emotions)}"

    def test_taxonomy_ids_are_stable_machine_readable(self) -> None:
        data = _load_yaml(TAXONOMY_PATH)
        expected_ids = {
            "JOY_FULFILLMENT",
            "PRIDE_ACCOMPLISHMENT",
            "HOPE_OPTIMISM",
            "CURIOSITY_FOCUS",
            "CALM_SERENITY",
            "NEUTRAL_ANALYTICAL",
            "APPREHENSION_ANXIETY",
            "FRUSTRATION_FRICTION",
            "SADNESS_DEJECTION",
            "OVERWHELMED_BURNOUT",
        }
        actual_ids = {e["id"] for e in data.get("emotions", [])}
        assert actual_ids == expected_ids, f"Emotion IDs mismatch: {actual_ids}"

    def test_taxonomy_ids_are_unique(self) -> None:
        data = _load_yaml(TAXONOMY_PATH)
        ids = [e["id"] for e in data.get("emotions", [])]
        assert len(ids) == len(set(ids)), "Duplicate emotion IDs found"

    def test_each_emotion_has_required_fields(self) -> None:
        required = {
            "id",
            "display_name",
            "valence",
            "definition",
            "inclusion_criteria",
            "exclusion_criteria",
            "linguistic_indicators",
            "behavioral_contextual_indicators",
            "hedonic_eudaimonic_relationship",
            "examples",
            "confusing_neighbors",
        }
        data = _load_yaml(TAXONOMY_PATH)
        for emotion in data.get("emotions", []):
            missing = required - emotion.keys()
            assert not missing, f"Emotion {emotion.get('id')} missing fields: {missing}"

    def test_each_emotion_valence_is_valid(self) -> None:
        valid_valences = {"positive", "negative", "neutral"}
        data = _load_yaml(TAXONOMY_PATH)
        for emotion in data.get("emotions", []):
            assert emotion["valence"] in valid_valences, (
                f"Emotion {emotion['id']} has invalid valence: {emotion['valence']}"
            )

    def test_neutral_analytical_valence_is_neutral(self) -> None:
        data = _load_yaml(TAXONOMY_PATH)
        for emotion in data.get("emotions", []):
            if emotion["id"] == "NEUTRAL_ANALYTICAL":
                assert emotion["valence"] == "neutral"
                break
        else:
            pytest.fail("NEUTRAL_ANALYTICAL emotion not found in taxonomy")

    def test_no_extra_emotion_classes(self) -> None:
        data = _load_yaml(TAXONOMY_PATH)
        ids = {e["id"] for e in data.get("emotions", [])}
        assert len(ids) == 10, "Do not introduce additional emotion classes without documented taxonomy revision"



class TestSchemaFile:
    """schema.json must exist and be valid JSON with correct constraints."""

    def test_schema_file_exists(self) -> None:
        assert SCHEMA_PATH.exists(), f"Missing schema file: {SCHEMA_PATH}"

    def test_schema_is_valid_json(self) -> None:
        data = _load_json(SCHEMA_PATH)
        assert isinstance(data, dict)

    def test_schema_title(self) -> None:
        data = _load_json(SCHEMA_PATH)
        assert "B.E.A.M. Annotation Record" in data.get("title", "")

    def test_schema_requires_primary_emotion(self) -> None:
        data = _load_json(SCHEMA_PATH)
        required = data.get("required", [])
        assert "primary_emotion" in required

    def test_schema_primary_emotion_enum_matches_taxonomy(self) -> None:
        taxonomy = _load_yaml(TAXONOMY_PATH)
        expected_ids = {e["id"] for e in taxonomy.get("emotions", [])}
        schema = _load_json(SCHEMA_PATH)
        primary_enum = set(schema["properties"]["primary_emotion"]["enum"])
        assert primary_enum == expected_ids, f"Schema primary_emotion enum does not match taxonomy: {primary_enum} vs {expected_ids}"

    def test_schema_secondary_emotion_allows_null(self) -> None:
        schema = _load_json(SCHEMA_PATH)
        secondary = schema["properties"]["secondary_emotion"]
        assert "null" in secondary.get("type", []), "secondary_emotion must allow null"

    def test_schema_intensity_range_1_to_5(self) -> None:
        schema = _load_json(SCHEMA_PATH)
        intensity = schema["properties"]["intensity"]
        assert intensity["minimum"] == 1
        assert intensity["maximum"] == 5

    def test_schema_confidence_range_1_to_3(self) -> None:
        schema = _load_json(SCHEMA_PATH)
        confidence = schema["properties"]["confidence"]
        assert confidence["minimum"] == 1
        assert confidence["maximum"] == 3

    def test_schema_context_flags_enum_is_closed(self) -> None:
        schema = _load_json(SCHEMA_PATH)
        flags = schema["properties"]["context_flags"]["items"]["enum"]
        assert len(flags) == 23, f"Expected 23 context flags, found {len(flags)}"
        assert "PERSONAL_EXPERIENCE" in flags
        assert "HEALTH" in flags
        assert "FINANCIAL" in flags

    def test_schema_no_additional_properties(self) -> None:
        schema = _load_json(SCHEMA_PATH)
        assert schema.get("additionalProperties") is False



class TestExampleAnnotations:
    """examples.jsonl must contain valid annotations matching the schema."""

    def test_examples_file_exists(self) -> None:
        assert EXAMPLES_PATH.exists(), f"Missing examples file: {EXAMPLES_PATH}"

    def test_examples_are_valid_jsonl(self) -> None:
        records = list(read_jsonl(EXAMPLES_PATH))
        assert len(records) >= 1, "examples.jsonl is empty"

    def test_every_example_has_required_fields(self) -> None:
        required = {
            "record_id",
            "text",
            "primary_emotion",
            "secondary_emotion",
            "intensity",
            "confidence",
            "context_flags",
            "annotator_id",
            "annotation_timestamp",
        }
        for record in read_jsonl(EXAMPLES_PATH):
            missing = required - record.keys()
            assert not missing, f"Example {record.get('record_id')} missing fields: {missing}"

    def test_every_example_has_valid_primary_emotion(self) -> None:
        taxonomy = _load_yaml(TAXONOMY_PATH)
        valid_ids = {e["id"] for e in taxonomy.get("emotions", [])}
        for record in read_jsonl(EXAMPLES_PATH):
            assert record["primary_emotion"] in valid_ids, (
                f"Example {record['record_id']} has invalid primary_emotion: {record['primary_emotion']}"
            )

    def test_every_example_has_valid_secondary_emotion_or_null(self) -> None:
        taxonomy = _load_yaml(TAXONOMY_PATH)
        valid_ids = {e["id"] for e in taxonomy.get("emotions", [])}
        for record in read_jsonl(EXAMPLES_PATH):
            secondary = record.get("secondary_emotion")
            assert secondary is None or secondary in valid_ids, (
                f"Example {record['record_id']} has invalid secondary_emotion: {secondary}"
            )

    def test_primary_and_secondary_are_distinct(self) -> None:
        for record in read_jsonl(EXAMPLES_PATH):
            primary = record.get("primary_emotion")
            secondary = record.get("secondary_emotion")
            if secondary is not None:
                assert primary != secondary, (
                    f"Example {record['record_id']} has identical primary and secondary emotion"
                )

    def test_every_example_has_valid_intensity(self) -> None:
        for record in read_jsonl(EXAMPLES_PATH):
            intensity = record.get("intensity")
            assert isinstance(intensity, int) and 1 <= intensity <= 5, (
                f"Example {record['record_id']} has invalid intensity: {intensity}"
            )

    def test_every_example_has_valid_confidence(self) -> None:
        for record in read_jsonl(EXAMPLES_PATH):
            confidence = record.get("confidence")
            assert isinstance(confidence, int) and 1 <= confidence <= 3, (
                f"Example {record['record_id']} has invalid confidence: {confidence}"
            )

    def test_every_example_has_valid_context_flags(self) -> None:
        schema = _load_json(SCHEMA_PATH)
        valid_flags = set(schema["properties"]["context_flags"]["items"]["enum"])
        for record in read_jsonl(EXAMPLES_PATH):
            for flag in record.get("context_flags", []):
                assert flag in valid_flags, (
                    f"Example {record['record_id']} has invalid context flag: {flag}"
                )

    def test_every_example_has_valid_annotator_id(self) -> None:
        for record in read_jsonl(EXAMPLES_PATH):
            annotator_id = record.get("annotator_id", "")
            assert annotator_id, "annotator_id must not be empty"
            assert " " not in annotator_id and "@" not in annotator_id, (
                f"Example {record['record_id']} has personal-looking annotator_id: {annotator_id}"
            )

    def test_every_example_has_iso_timestamp(self) -> None:
        for record in read_jsonl(EXAMPLES_PATH):
            ts = record.get("annotation_timestamp", "")
            assert ts.endswith("Z"), f"Example {record['record_id']} timestamp is not ISO-8601 UTC: {ts}"

    def test_examples_are_synthetic_not_real_reddit(self) -> None:
        for record in read_jsonl(EXAMPLES_PATH):
            assert "reddit" not in record.get("text", "").lower(), (
                f"Example {record['record_id']} appears to contain Reddit platform references"
            )

    def test_examples_cover_diverse_scenarios(self) -> None:
        records = list(read_jsonl(EXAMPLES_PATH))
        primary_emotions = {r["primary_emotion"] for r in records}
        assert len(primary_emotions) >= 5, (
            f"Examples cover only {len(primary_emotions)} emotion classes; expected broader coverage"
        )
        has_secondary = any(r.get("secondary_emotion") for r in records)
        assert has_secondary, "Examples should include at least one primary+secondary annotation"
        has_null_secondary = any(r.get("secondary_emotion") is None for r in records)
        assert has_null_secondary, "Examples should include at least one annotation with null secondary_emotion"



class TestAnnotationFiles:
    """All required annotation files must exist."""

    def test_annotation_guidelines_exists(self) -> None:
        assert GUIDELINES_PATH.exists(), f"Missing annotation guidelines: {GUIDELINES_PATH}"

    def test_quality_protocol_exists(self) -> None:
        assert QUALITY_PATH.exists(), f"Missing quality protocol: {QUALITY_PATH}"



class TestDatasetV001Unlabeled:
    """v001 must not be modified to pretend it is labeled."""

    def test_v001_metadata_remains_unlabeled(self) -> None:
        metadata_path = PROJECT_ROOT / "beam-datasets" / "metadata" / "dataset_v001.json"
        if not metadata_path.exists():
            pytest.skip("v001 metadata not yet created")
        metadata = _load_json(metadata_path)
        assert metadata.get("label_type") == "unlabeled", (
            "dataset_v001 must remain unlabeled; create dataset_v002 for supervised annotations"
        )
