# B.E.A.M. Annotation Interface

Streamlit-based human annotation interface for the B.E.A.M. emotion taxonomy pilot.

## Installation

```bash
cd beam-ai
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run beam-ai/annotation_app/app.py
```

## Annotator Configuration

Each annotator must set a pseudonymous annotator ID before starting:

```bash
export ANNOTATOR_ID=ANNOTATOR_A
streamlit run beam-ai/annotation_app/app.py
```

Valid annotator IDs contain only letters, numbers, and underscores (e.g., `ANNOTATOR_A`, `ANNOTATOR_B`, `ANNOTATOR_C`).

Do **not** use real names, emails, or Reddit usernames.

## Pilot Dataset

- **Source:** `beam-datasets/raw/sample_reddit.jsonl` (16 records, read-only)
- **Annotations:** `beam-datasets/annotations/pilot/ANNOTATOR_A.jsonl`
- **Manifest:** `beam-datasets/annotations/pilot/pilot_manifest.json`

## How to Resume Annotation

The application automatically loads existing annotations. You can:

- Update an existing annotation by navigating to the record and saving again
- See your progress in the progress bar
- Navigate between records using Previous/Next/Skip/Jump

## Privacy Rules

- Reddit usernames are **never** displayed or stored
- No external APIs are contacted
- Annotations are stored locally only
- Each annotator's work is isolated in their own file
- Annotators cannot see each other's labels during independent annotation

## Independent Annotation Procedure

1. Each annotator runs the application with their own `ANNOTATOR_ID`
2. Annotators work independently — do not discuss records or compare labels
3. Complete all 16 records in the pilot
4. Submit annotations by clicking "Save Annotation"
5. The application creates `ANNOTATOR_X.jsonl` in the pilot annotations directory

After all three annotators complete the pilot, the annotation lead will compute agreement metrics and adjudicate disagreements.

## Troubleshooting

**"ANNOTATOR_ID environment variable is not set"**
→ Set `ANNOTATOR_ID` before running Streamlit.

**"Failed to load required data"**
→ Ensure the authoritative files exist:
- `beam-datasets/annotation/taxonomy.yaml`
- `beam-datasets/annotation/schema.json`
- `beam-datasets/raw/sample_reddit.jsonl`

**"Validation failed"**
→ Check the error message. Common issues:
- Primary and secondary emotions are identical
- Intensity or confidence out of range
- Invalid context flag selected
