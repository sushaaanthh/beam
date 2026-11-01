"""Streamlit UI components for the annotation application."""
from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from .config import GUIDELINES_PATH, ANNOTATOR_ID
from .loader import SourceRecord, load_schema, load_taxonomy


@st.dialog("Annotation Guidelines")
def show_guidelines_dialog() -> None:
    """Display annotation guidelines in a dialog."""
    try:
        with open(GUIDELINES_PATH, "r", encoding="utf-8") as f:
            guidelines = f.read()
        st.markdown(guidelines)
    except Exception as e:
        st.error(f"Could not load guidelines: {e}")


def render_guidelines_expander() -> None:
    """Render guidelines as an expander."""
    with st.expander("📖 Annotation Guidelines", expanded=False):
        try:
            with open(GUIDELINES_PATH, "r", encoding="utf-8") as f:
                guidelines = f.read()
            st.markdown(guidelines)
        except Exception as e:
            st.error(f"Could not load guidelines: {e}")


def render_record(record: SourceRecord, index: int, total: int) -> None:
    """Render the record being annotated."""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.metric("Record", f"{index + 1} / {total}")
        st.caption(f"ID: `{record.record_id}`")
        st.caption(f"Type: {record.record_type}")
    with col2:
        st.subheader("Text to Annotate")
        if record.title and record.record_type == "post":
            st.markdown(f"**Title:** {record.title}")
        if record.body and record.body_status == "available":
            st.markdown(f"**Body:**\n\n{record.body}")
        else:
            st.warning(f"Body unavailable (status: {record.body_status})")

    with st.expander("📊 Context (metadata)", expanded=False):
        meta = record.safe_metadata
        for k, v in meta.items():
            st.text(f"{k}: {v}")


def render_emotion_selector(
    label: str,
    options: list[str],
    display_names: dict[str, str],
    definitions: dict[str, str],
    key: str,
    required: bool = True,
) -> str | None:
    """Render an emotion selector with help text."""
    st.markdown(f"**{label}**")
    if required:
        st.caption("Required")

    selected = st.selectbox(
        label,
        options=options,
        key=key,
        format_func=lambda x: display_names.get(x, x),
        label_visibility="collapsed",
    )

    if selected:
        with st.expander(f"ℹ️ About: {display_names.get(selected, selected)}", expanded=False):
            definition = definitions.get(selected, "")
            if definition:
                st.markdown(definition)

    return selected


def render_annotation_form(
    record: SourceRecord,
    existing: dict | None,
    taxonomy,
    schema,
    key_prefix: str,
) -> dict | None:
    """Render the annotation form for a record."""
    existing = existing or {}

    form_key = f"{key_prefix}_{record.record_id}"

    with st.form(key=form_key):
        st.markdown("### Emotion Classification")

        primary_options = taxonomy.ids
        primary_display = {e["id"]: e["display_name"] for e in taxonomy.emotions}
        primary_defs = {e["id"]: e["definition"] for e in taxonomy.emotions}

        primary_default = existing.get("primary_emotion", "")
        primary_index = primary_options.index(primary_default) if primary_default in primary_options else 0

        primary = st.selectbox(
            "Primary Emotion (required)",
            options=primary_options,
            index=primary_index,
            format_func=lambda x: primary_display.get(x, x),
            help="Select the dominant expressed emotion",
        )

        if primary:
            with st.expander(f"ℹ️ About: {primary_display.get(primary, primary)}", expanded=False):
                st.markdown(primary_defs.get(primary, ""))

        st.divider()

        secondary_options = [None] + taxonomy.ids
        secondary_display = {None: "None"}
        secondary_display.update({e["id"]: e["display_name"] for e in taxonomy.emotions})

        secondary_default = existing.get("secondary_emotion")
        secondary_index = secondary_options.index(secondary_default) if secondary_default in secondary_options else 0

        secondary = st.selectbox(
            "Secondary Emotion (optional)",
            options=secondary_options,
            index=secondary_index,
            format_func=lambda x: secondary_display.get(x, "None"),
            help="Select a secondary emotion if another emotion materially contributes to the text",
        )

        if secondary and secondary != primary:
            with st.expander(f"ℹ️ About: {secondary_display.get(secondary, secondary)}", expanded=False):
                st.markdown(primary_defs.get(secondary, ""))

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            intensity = st.slider(
                "Intensity (1-5)",
                min_value=1,
                max_value=5,
                value=existing.get("intensity", 3),
                help="Strength of emotional expression (1=very low, 5=very high). NOT clinical severity.",
            )
        with col2:
            st.caption("""
            **Intensity guide:**
            1 = Very Low | 2 = Low | 3 = Moderate | 4 = High | 5 = Very High
            """)

        st.divider()

        confidence = st.slider(
            "Confidence (1-3)",
            min_value=1,
            max_value=3,
            value=existing.get("confidence", 2),
            help="Annotator certainty (1=uncertain, 2=somewhat confident, 3=confident)",
        )

        st.caption("""
        **Confidence guide:**
        1 = Uncertain | 2 = Somewhat Confident | 3 = Confident
        """)

        st.divider()

        st.markdown("**Context Flags**")
        st.caption("Select all that apply")
        context_options = schema.context_flags
        context_defaults = existing.get("context_flags", [])
        context_flags = st.multiselect(
            "Context Flags",
            options=context_options,
            default=context_defaults,
            label_visibility="collapsed",
        )

        st.divider()

        notes_default = existing.get("notes", "")
        notes = st.text_area(
            "Notes (optional)",
            value=notes_default,
            placeholder="Use for ambiguity, unusual context, difficult classification, or interpretation concerns...",
            help="Explain difficult cases or label choices. Do not enter personal identifying information.",
        )

        st.divider()

        submitted = st.form_submit_button("💾 Save Annotation", type="primary", use_container_width=True)

        if submitted:
            annotation = {
                "record_id": record.record_id,
                "text": record.display_text,
                "primary_emotion": primary,
                "secondary_emotion": secondary if secondary != primary else None,
                "intensity": intensity,
                "confidence": confidence,
                "context_flags": context_flags,
                "annotator_id": ANNOTATOR_ID,
                "annotation_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "notes": notes.strip() if notes.strip() else None,
            }
            return annotation

    return None


def render_progress(completed: int, total: int, current_index: int) -> None:
    """Render progress indicator."""
    progress = completed / total if total > 0 else 0
    st.progress(progress, text=f"Record {current_index + 1} / {total} | Completed: {completed} | Remaining: {total - completed}")
