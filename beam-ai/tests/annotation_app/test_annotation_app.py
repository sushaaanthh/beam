"""Tests for the B.E.A.M. annotation application."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from annotation_app.config import (
    ANNOTATIONS_DIR,
    ANNOTATOR_ID,
    MANIFEST_PATH,
    SCHEMA_PATH,
    SOURCE_DATA_PATH,
    TAXONOMY_PATH,
    validate_annotator_id,
)
from annotation_app.loader import (
    Schema,
    SourceRecord,
    Taxonomy,
    generate_pilot_manifest,
    load_pilot_manifest,
    load_schema,
    load_source_records,
    load_taxonomy,
)
from annotation_app.storage import AnnotationStorage
from annotation_app.validator import AnnotationValidator, ValidationError



PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_ANNOTATOR = "TEST_ANNOTATOR_X"



@pytest.fixture(scope="module")
def taxonomy() -> Taxonomy:
    return load_taxonomy()


@pytest.fixture(scope="module")
def schema() -> Schema:
    return load_schema()


@pytest.fixture(scope="module")
def source_records() -> list[SourceRecord]:
    return load_source_records()


@pytest.fixture(scope="module")
def pilot_manifest(source_records: list[SourceRecord], taxonomy: Taxonomy, schema: Schema) -> dict:
    return generate_pilot_manifest(source_records, taxonomy, schema)


@pytest.fixture
def validator(schema: Schema, source_records: list[SourceRecord]) -> AnnotationValidator:
    return AnnotationValidator(schema, source_records)


@pytest.fixture
def temp_annotations_dir(tmp_path: Path) -> Path:
    """Temporary annotations directory for isolation."""
    return tmp_path



class TestPilotSourceLoading:
    """Test loading of pilot source data."""

    def test_source_file_exists(self) -> None:
        assert SOURCE_DATA_PATH.exists(), f"Source file not found: {SOURCE_DATA_PATH}"

    def test_loads_all_16_records(self, source_records: list[SourceRecord]) -> None:
        assert len(source_records) == 16, f"Expected 16 records, got {len(source_records)}"

    def test_records_have_valid_ids(self, source_records: list[SourceRecord]) -> None:
        for record in source_records:
            assert record.record_id, f"Record missing ID: {record.raw}"

    def test_records_have_types(self, source_records: list[SourceRecord]) -> None:
        posts = [r for r in source_records if r.record_type == "post"]
        comments = [r for r in source_records if r.record_type == "comment"]
        assert len(posts) == 8, f"Expected 8 posts, got {len(posts)}"
        assert len(comments) == 8, f"Expected 8 comments, got {len(comments)}"

    def test_no_usernames_in_display(self, source_records: list[SourceRecord]) -> None:
        for record in source_records:
            text = record.display_text
            assert "p0a1b2c3d4e5f607" not in text, "Raw author pseudonym leaked into display text"
            assert "c0a1b2c3d4e5f607" not in text, "Raw author pseudonym leaked into display text"

    def test_source_file_unchanged(self) -> None:
        """Verify source file is not modified by loading."""
        original_hash = hash(SOURCE_DATA_PATH.read_bytes())
        _ = load_source_records()
        new_hash = hash(SOURCE_DATA_PATH.read_bytes())
        assert original_hash == new_hash, "Source file was modified during loading"



class TestPilotManifest:
    """Test pilot manifest generation."""

    def test_manifest_has_required_fields(self, pilot_manifest: dict) -> None:
        required = [
            "dataset_version",
            "source_file",
            "source_record_count",
            "record_ids",
            "taxonomy_version",
            "schema_version",
            "creation_timestamp",
        ]
        for field in required:
            assert field in pilot_manifest, f"Manifest missing field: {field}"

    def test_manifest_dataset_version_v001(self, pilot_manifest: dict) -> None:
        assert pilot_manifest["dataset_version"] == "v001"

    def test_manifest_record_count_16(self, pilot_manifest: dict) -> None:
        assert pilot_manifest["source_record_count"] == 16

    def test_manifest_has_all_16_record_ids(self, pilot_manifest: dict, source_records: list[SourceRecord]) -> None:
        expected_ids = {r.record_id for r in source_records}
        actual_ids = set(pilot_manifest["record_ids"])
        assert actual_ids == expected_ids, f"Manifest record IDs mismatch: {actual_ids} vs {expected_ids}"

    def test_manifest_deterministic_ids(self, pilot_manifest: dict, source_records: list[SourceRecord], taxonomy: Taxonomy, schema: Schema) -> None:
        manifest2 = generate_pilot_manifest(source_records, taxonomy, schema)
        assert pilot_manifest["record_ids"] == manifest2["record_ids"], "Manifest record IDs not deterministic"
        assert pilot_manifest["record_ids_hash"] == manifest2["record_ids_hash"], "Manifest hash not deterministic"

    def test_manifest_has_taxonomy_version(self, pilot_manifest: dict, taxonomy: Taxonomy) -> None:
        assert pilot_manifest["taxonomy_version"] == taxonomy.version

    def test_manifest_save_and_load(self, pilot_manifest: dict, tmp_path: Path) -> None:
        test_path = tmp_path / "test_manifest.json"
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(pilot_manifest, f)
        with open(test_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded["dataset_version"] == "v001"
        assert len(loaded["record_ids"]) == 16



class TestTaxonomyLoading:
    """Test taxonomy loading and structure."""

    def test_taxonomy_file_exists(self) -> None:
        assert TAXONOMY_PATH.exists(), f"Taxonomy file not found: {TAXONOMY_PATH}"

    def test_load_taxonomy(self, taxonomy: Taxonomy) -> None:
        assert taxonomy.version == "1.0.0"
        assert len(taxonomy.emotions) == 10

    def test_taxonomy_ids_stable(self, taxonomy: Taxonomy) -> None:
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
        assert set(taxonomy.ids) == expected_ids

    def test_taxonomy_get_by_id(self, taxonomy: Taxonomy) -> None:
        joy = taxonomy.get("JOY_FULFILLMENT")
        assert joy is not None
        assert joy["display_name"] == "Joy / Fulfillment"

    def test_taxonomy_validate_id(self, taxonomy: Taxonomy) -> None:
        assert taxonomy.validate_id("JOY_FULFILLMENT")
        assert not taxonomy.validate_id("INVALID_EMOTION")



class TestSchemaValidation:
    """Test schema loading and validation."""

    def test_schema_file_exists(self) -> None:
        assert SCHEMA_PATH.exists(), f"Schema file not found: {SCHEMA_PATH}"

    def test_load_schema(self, schema: Schema) -> None:
        assert schema.title == "B.E.A.M. Annotation Record"
        assert len(schema.primary_emotions) == 10
        assert len(schema.context_flags) > 0

    def test_valid_annotation(self, validator: AnnotationValidator, source_records: list[SourceRecord]) -> None:
        record = source_records[0]
        annotation = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": None,
            "intensity": 3,
            "confidence": 2,
            "context_flags": ["PERSONAL_EXPERIENCE"],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        validator.validate(annotation)

    def test_invalid_primary_emotion(self, validator: AnnotationValidator, source_records: list[SourceRecord]) -> None:
        record = source_records[0]
        annotation = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "INVALID_EMOTION",
            "secondary_emotion": None,
            "intensity": 3,
            "confidence": 2,
            "context_flags": [],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        with pytest.raises(ValidationError, match="primary_emotion"):
            validator.validate(annotation)

    def test_invalid_secondary_emotion(self, validator: AnnotationValidator, source_records: list[SourceRecord]) -> None:
        record = source_records[0]
        annotation = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": "INVALID_EMOTION",
            "intensity": 3,
            "confidence": 2,
            "context_flags": [],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        with pytest.raises(ValidationError, match="secondary_emotion"):
            validator.validate(annotation)

    def test_primary_equals_secondary_rejection(self, validator: AnnotationValidator, source_records: list[SourceRecord]) -> None:
        record = source_records[0]
        annotation = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": "JOY_FULFILLMENT",
            "intensity": 3,
            "confidence": 2,
            "context_flags": [],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        with pytest.raises(ValidationError, match="secondary_emotion"):
            validator.validate(annotation)

    def test_invalid_intensity(self, validator: AnnotationValidator, source_records: list[SourceRecord]) -> None:
        record = source_records[0]
        annotation = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": None,
            "intensity": 6,
            "confidence": 2,
            "context_flags": [],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        with pytest.raises(ValidationError, match="intensity"):
            validator.validate(annotation)

    def test_invalid_confidence(self, validator: AnnotationValidator, source_records: list[SourceRecord]) -> None:
        record = source_records[0]
        annotation = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": None,
            "intensity": 3,
            "confidence": 5,
            "context_flags": [],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        with pytest.raises(ValidationError, match="confidence"):
            validator.validate(annotation)

    def test_invalid_context_flag(self, validator: AnnotationValidator, source_records: list[SourceRecord]) -> None:
        record = source_records[0]
        annotation = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": None,
            "intensity": 3,
            "confidence": 2,
            "context_flags": ["INVALID_FLAG"],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        with pytest.raises(ValidationError, match="context_flags"):
            validator.validate(annotation)

    def test_missing_record_id_rejected(self, validator: AnnotationValidator) -> None:
        annotation = {
            "record_id": "NONEXISTENT",
            "text": "test",
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": None,
            "intensity": 3,
            "confidence": 2,
            "context_flags": [],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        with pytest.raises(ValidationError, match="record_id"):
            validator.validate(annotation)



class TestDuplicateHandling:
    """Test duplicate annotation handling."""

    def test_duplicate_annotation_detected(self, validator: AnnotationValidator, source_records: list[SourceRecord]) -> None:
        record = source_records[0]
        validator.existing_annotations[record.record_id] = {"record_id": record.record_id}
        existing = validator.check_duplicate(TEST_ANNOTATOR, record.record_id)
        assert existing is not None

    def test_no_duplicate_for_new_record(self, validator: AnnotationValidator, source_records: list[SourceRecord]) -> None:
        record = source_records[1]
        existing = validator.check_duplicate(TEST_ANNOTATOR, record.record_id)
        assert existing is None



class TestAnnotationPersistence:
    """Test annotation storage and persistence."""

    def test_save_and_load_annotation(self, tmp_path: Path, source_records: list[SourceRecord]) -> None:
        import os
        os.environ["ANNOTATOR_ID"] = TEST_ANNOTATOR
        from annotation_app.config import ANNOTATIONS_DIR as REAL_DIR
        storage = AnnotationStorage(TEST_ANNOTATOR)
        record = source_records[0]
        annotation = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": None,
            "intensity": 3,
            "confidence": 2,
            "context_flags": ["PERSONAL_EXPERIENCE"],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": "Test note",
        }
        storage.save(annotation)
        loaded = storage.get_annotation(record.record_id)
        assert loaded is not None
        assert loaded["primary_emotion"] == "JOY_FULFILLMENT"
        assert loaded["notes"] == "Test note"

    def test_update_existing_annotation(self, tmp_path: Path, source_records: list[SourceRecord]) -> None:
        storage = AnnotationStorage(TEST_ANNOTATOR)
        record = source_records[0]
        annotation1 = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": None,
            "intensity": 2,
            "confidence": 2,
            "context_flags": [],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        annotation2 = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "CALM_SERENITY",
            "secondary_emotion": None,
            "intensity": 4,
            "confidence": 3,
            "context_flags": ["PERSONAL_EXPERIENCE"],
            "annotator_id": TEST_ANNOTATOR,
            "annotation_timestamp": "2026-10-05T01:00:00Z",
            "notes": "Updated",
        }
        storage.save(annotation1)
        storage.save(annotation2)
        loaded = storage.get_annotation(record.record_id)
        assert loaded["primary_emotion"] == "CALM_SERENITY"
        assert loaded["intensity"] == 4
        all_anns = storage.load_all()
        record_ids = [a["record_id"] for a in all_anns]
        assert record_ids.count(record.record_id) == 1

    def test_annotator_isolation(self, tmp_path: Path, source_records: list[SourceRecord]) -> None:
        annotator_a = "TEST_ANNOTATOR_A"
        annotator_b = "TEST_ANNOTATOR_B"
        storage_a = AnnotationStorage(annotator_a)
        storage_b = AnnotationStorage(annotator_b)
        record = source_records[0]
        annotation = {
            "record_id": record.record_id,
            "text": record.display_text,
            "primary_emotion": "JOY_FULFILLMENT",
            "secondary_emotion": None,
            "intensity": 3,
            "confidence": 2,
            "context_flags": [],
            "annotator_id": annotator_a,
            "annotation_timestamp": "2026-10-05T00:00:00Z",
            "notes": None,
        }
        storage_a.save(annotation)
        b_ann = storage_b.get_annotation(record.record_id)
        assert b_ann is None, "Annotator isolation violated: B can see A's annotation"
        a_ann = storage_a.get_annotation(record.record_id)
        assert a_ann is not None



class TestSourceDatasetUnchanged:
    """Verify source dataset is not modified."""

    def test_raw_file_exists(self) -> None:
        assert SOURCE_DATA_PATH.exists()

    def test_raw_file_not_modified(self) -> None:
        original_content = SOURCE_DATA_PATH.read_bytes()
        _ = load_source_records()
        new_content = SOURCE_DATA_PATH.read_bytes()
        assert original_content == new_content, "Raw source file was modified"

    def test_processed_file_not_modified(self) -> None:
        processed = PROJECT_ROOT / "beam-datasets" / "processed" / "dataset_v001.jsonl"
        if processed.exists():
            original = processed.read_bytes()
            _ = load_source_records()
            assert processed.read_bytes() == original, "Processed file was modified"
