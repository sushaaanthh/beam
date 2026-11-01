"""B.E.A.M. Human Annotation Interface — Streamlit application."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from annotation_app.config import (
    ANNOTATIONS_DIR,
    ANNOTATOR_ID,
    MANIFEST_PATH,
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
from annotation_app.ui import render_annotation_form, render_guidelines_expander, render_progress, render_record
from annotation_app.validator import AnnotationValidator, ValidationError


def init_session_state(records: list[SourceRecord]) -> None:
    """Initialize Streamlit session state."""
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "records" not in st.session_state:
        st.session_state.records = records
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "validation_error" not in st.session_state:
        st.session_state.validation_error = None
    if "navigate_to" not in st.session_state:
        st.session_state.navigate_to = None


def ensure_pilot_manifest(records: list[SourceRecord], taxonomy: Taxonomy, schema: Schema) -> None:
    """Ensure pilot manifest exists."""
    if not MANIFEST_PATH.exists():
        manifest = generate_pilot_manifest(records, taxonomy, schema)
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        st.info(f"Created pilot manifest with {len(records)} records.")


def main() -> None:
    """Main application entry point."""
    st.set_page_config(
        page_title="B.E.A.M. Annotation Interface",
        page_icon="📝",
        layout="wide",
    )

    if not ANNOTATOR_ID or not validate_annotator_id(ANNOTATOR_ID):
        st.error(
            "**ANNOTATOR_ID environment variable is not set or invalid.**\n\n"
            "Please set it before running the application:\n\n"
            "```bash\n"
            "export ANNOTATOR_ID=ANNOTATOR_A\n"
            "streamlit run beam-ai/annotation_app/app.py\n"
            "```\n\n"
            "Valid IDs contain only letters, numbers, and underscores (e.g., ANNOTATOR_A, ANNOTATOR_B)."
        )
        st.stop()

    try:
        taxonomy = load_taxonomy()
        schema = load_schema()
        records = load_source_records()
    except Exception as e:
        st.error(f"Failed to load required data: {e}")
        st.stop()

    ensure_pilot_manifest(records, taxonomy, schema)

    init_session_state(records)

    storage = AnnotationStorage(ANNOTATOR_ID)
    validator = AnnotationValidator(schema, records)
    validator.load_existing(ANNOTATOR_ID)

    st.title("📝 B.E.A.M. Annotation Interface")
    st.caption(f"Annotator: `{ANNOTATOR_ID}` | Pilot: v001 ({len(records)} records)")

    render_guidelines_expander()

    st.divider()

    current_index = st.session_state.current_index
    total = len(records)
    completed = storage.get_completed_count()

    if st.session_state.navigate_to is not None:
        idx = st.session_state.navigate_to
        if 0 <= idx < total:
            st.session_state.current_index = idx
            st.session_state.submitted = False
            st.session_state.validation_error = None
        st.session_state.navigate_to = None
        st.rerun()

    render_progress(completed, total, current_index)

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    with col1:
        if st.button("⏮️ Previous", disabled=current_index == 0):
            st.session_state.current_index = max(0, current_index - 1)
            st.session_state.submitted = False
            st.session_state.validation_error = None
            st.rerun()
    with col2:
        if st.button("⏭️ Next", disabled=current_index >= total - 1):
            st.session_state.current_index = min(total - 1, current_index + 1)
            st.session_state.submitted = False
            st.session_state.validation_error = None
            st.rerun()
    with col3:
        if st.button("⏭️ Skip"):
            st.session_state.current_index = min(total - 1, current_index + 1)
            st.session_state.submitted = False
            st.session_state.validation_error = None
            st.rerun()
    with col4:
        jump = st.number_input("Jump to", min_value=1, max_value=total, value=current_index + 1, label_visibility="collapsed")
        if st.button("Go"):
            st.session_state.navigate_to = jump - 1
            st.rerun()
    with col5:
        st.metric("Completed", f"{completed} / {total}")

    st.divider()

    record = records[current_index]
    render_record(record, current_index, total)

    st.divider()

    existing = storage.get_annotation(record.record_id)
    if existing:
        st.success("✅ Annotation exists for this record. You can update it below.")
    else:
        st.info("📝 No annotation yet for this record. Please complete the form below.")

    result = render_annotation_form(record, existing, taxonomy, schema, key_prefix="ann")

    if result:
        try:
            validator.validate(result)

            storage.save(result)

            st.session_state.submitted = True
            st.session_state.validation_error = None
            st.success(f"✅ Annotation saved for record {record.record_id}")

            import time
            time.sleep(0.5)
            if current_index < total - 1:
                st.session_state.current_index = current_index + 1
                st.session_state.submitted = False
                st.rerun()

        except ValidationError as e:
            st.session_state.validation_error = str(e)
            st.error(f"❌ Validation failed: {e}")
        except Exception as e:
            st.error(f"❌ Failed to save annotation: {e}")

    if st.session_state.validation_error:
        st.error(st.session_state.validation_error)

    st.divider()
    st.caption(
        "B.E.A.M. Annotation Interface | Pilot v001 | "
        "Annotations are stored locally in `beam-datasets/annotations/pilot/`"
    )


if __name__ == "__main__":
    main()
