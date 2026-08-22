# B.E.A.M. Datasets Repository

This directory contains the training, fine-tuning, and evaluation benchmark corpora used by B.E.A.M. for affective and behavioral emotion analysis.

---

## 🗃️ Active Datasets

| ID | Dataset Name | Source | Total Samples | Labels / Taxonomy | Status | File Location |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DS-01** | **GoEmotions Benchmark Corpus** | Reddit Curated Feed | `58,009` | 28 Fine-grained Emotions | `ACTIVE` | [`raw/goemotions_train.tsv`](file:///d:/Unnati%20Saxena/Proj/beam-main/beam-datasets/raw/goemotions_train.tsv)<br>[`processed/goemotions_reddit_full.json`](file:///d:/Unnati%20Saxena/Proj/beam-main/beam-datasets/processed/goemotions_reddit_full.json) |
| **DS-02** | **Developer Affective Telemetry** | Dev Community & Forum | `14,240` | 6 Valence/Arousal Dimensions | `ACTIVE` | [`processed/developer_affective_telemetry.json`](file:///d:/Unnati%20Saxena/Proj/beam-main/beam-datasets/processed/developer_affective_telemetry.json) |
| **DS-03** | **Technical Retrospective Corpus** | Engineering Logs | `8,920` | 12 Behavioral Categories | `SYNCING` | [`processed/technical_retrospective.json`](file:///d:/Unnati%20Saxena/Proj/beam-main/beam-datasets/processed/technical_retrospective.json) |
| **DS-04** | **EmpatheticDialogues Split** | Academic Benchmark | `24,850` | 32 Emotional Situations | `ACTIVE` | [`processed/empathetic_dialogues.json`](file:///d:/Unnati%20Saxena/Proj/beam-main/beam-datasets/processed/empathetic_dialogues.json) |

---

## 📥 Ingestion & Download Pipeline

To re-download, sync, or update the benchmark corpora from scratch:
```bash
.\venv\Scripts\python.exe beam-datasets/download_datasets.py
```

---

## 📂 Directory Layout
- `raw/`: Raw, uncompressed dataset downloads directly from origin repositories.
- `processed/`: Standardized JSON and tokenized vectors for model training and evaluation.
- `external/`: Third-party academic benchmark splits.
- `exports/`: Ingested social scrape batches and annotated exports.