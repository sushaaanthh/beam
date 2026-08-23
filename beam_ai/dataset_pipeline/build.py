"""Pipeline orchestration.

    raw rows -> quality filter -> clean -> normalize -> language -> dedup
             -> features -> dataset construction -> grouped splits
             -> processed/features/splits files + metadata + quality report

Determinism: no wall-clock values enter the data files; ordering is stable
(created_utc, source_id); ids are uuid5; splits are hash-ordered. Running
twice with the same input/config/seed produces byte-identical outputs.
Only metadata JSON carries a created_at timestamp.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beam_ai import PROCESSING_VERSION
from beam_ai.configs.pipeline_settings import PipelineSettings, get_pipeline_settings
from beam_ai.dataset_pipeline.io_utils import (
    iter_database_rows,
    iter_input_rows,
    write_jsonl,
)
from beam_ai.dataset_pipeline.reporting import (
    build_metadata,
    build_quality_report,
    write_metadata_and_report,
)
from beam_ai.dataset_pipeline.schema import (
    BASE_FIELDS,
    make_record_id,
    utc_iso,
)
from beam_ai.dataset_pipeline.splitting import assign_splits, split_statistics
from beam_ai.features.behavioral_features import extract_behavioral_features
from beam_ai.features.linguistic_features import extract_linguistic_features
from beam_ai.features.nlp_features import extract_pos_features, extract_vader_features
from beam_ai.preprocessing.deduplication import Deduplicator
from beam_ai.preprocessing.language import LanguageFilter
from beam_ai.preprocessing.normalization import normalize_text
from beam_ai.preprocessing.quality_filters import evaluate_quality
from beam_ai.preprocessing.text_cleaning import clean_text

DATASETS_DIR = Path(__file__).resolve().parents[2] / "beam-datasets"


@dataclass(slots=True)
class BuildResult:
    dataset_version: str
    counts: dict[str, int]
    files: dict[str, str]


def _sort_key(row: dict[str, Any]) -> tuple[str, str]:
    return (row["created_utc"] or "", row["source_id"])


def build_dataset(
    *,
    input_path: Path | None = None,
    database_url: str | None = None,
    datasets_root: Path = DATASETS_DIR,
    settings: PipelineSettings | None = None,
) -> BuildResult:
    settings = settings or get_pipeline_settings()
    settings.validate_ratios()

    processed_dir = datasets_root / "processed"
    features_dir = datasets_root / "features"
    splits_dir = datasets_root / "splits"
    metadata_dir = datasets_root / "metadata"

    # ---- 1. Load raw rows ----------------------------------------------------
    if input_path is not None:
        raw_rows = list(iter_input_rows(input_path))
        source_description = str(input_path)
    elif database_url is not None:
        raw_rows = list(iter_database_rows(database_url))
        source_description = f"database:{database_url.split('@')[-1]}"
    else:
        raise ValueError("provide --input (file/directory) or --db-url")

    total_input = len(raw_rows)
    unusable_before = sum(1 for row in raw_rows if not row["raw_text"])

    kept: list[dict[str, Any]] = []
    filtered: list[str] = []
    duplicates: list[str] = []

    deduplicator = Deduplicator(
        near_threshold=settings.near_duplicate_threshold,
        enabled=settings.dedupe_enabled,
    )
    language_filter = LanguageFilter(settings)

    # ---- 2. Clean -> filter -> normalize -> language -> dedupe -----------------
    candidates: list[dict[str, Any]] = []
    for row in sorted(raw_rows, key=_sort_key):
        cleaned = clean_text(row["raw_text"])
        decision = evaluate_quality(
            raw_text=row["raw_text"],
            cleaned_text=cleaned,
            body_status=row["body_status"],
            settings=settings,
        )
        if not decision.kept:
            filtered.append(decision.reason or "unknown")
            continue

        normalized = normalize_text(cleaned)

        language_decision = language_filter.evaluate(cleaned)
        if not language_decision.kept:
            filtered.append(language_decision.reason or "language")
            continue

        record_id = make_record_id(row["source"], row["source_id"])
        dedupe = deduplicator.check(
            record_id=record_id,
            sort_key=row["created_utc"] or "",
            subreddit=row["subreddit"],
            normalized_text=normalized,
        )
        if dedupe.duplicate:
            duplicates.append(dedupe.reason or "duplicate")
            continue

        candidates.append(
            {
                "record_id": record_id,
                "source": row["source"],
                "source_id": row["source_id"],
                "thread_id": row["thread_id"],
                "subreddit": row["subreddit"],
                "raw_text": row["raw_text"],
                "cleaned_text": cleaned,
                "normalized_text": normalized,
                "created_utc": utc_iso(row["created_utc"]),
                "author_pseudonym": row["author_pseudonym"],
                "score": row["score"],
                "num_comments": row["num_comments"],
                "language": language_decision.language,
            }
        )

    # ---- 3. Features ------------------------------------------------------------
    for candidate in candidates:
        features: dict[str, Any] = {}
        features.update(extract_linguistic_features(candidate["cleaned_text"], candidate["normalized_text"]))
        features.update(
            extract_behavioral_features(
                created_utc=_parse_utc(candidate["created_utc"]),
                score=candidate["score"],
                num_comments=candidate["num_comments"],
                subreddit=candidate["subreddit"],
            )
        )
        features.update(extract_vader_features(candidate["cleaned_text"]))
        pos = extract_pos_features(candidate["normalized_text"])
        features.update(pos)
        candidate.update(features)

    # ---- 4. Splits (grouped by thread) -------------------------------------------
    thread_ids = [candidate["thread_id"] for candidate in candidates]
    assignment = assign_splits(
        thread_ids,
        train_ratio=settings.train_ratio,
        validation_ratio=settings.validation_ratio,
        test_ratio=settings.test_ratio,
        seed=settings.random_seed,
    )

    records: list[dict[str, Any]] = []
    base_set = set(BASE_FIELDS) | {"num_comments"}
    feature_keys: list[str] = []

    for candidate in candidates:
        split_name = assignment[candidate["thread_id"]]
        num_comments_value = candidate.pop("num_comments")
        record = {
            **{field: candidate.get(field) for field in BASE_FIELDS},
            "comment_count": num_comments_value,
            "split": split_name,
            "dataset_version": settings.dataset_version,
            "processing_version": PROCESSING_VERSION,
        }
        # Merge feature columns (everything outside identity/text/metadata).
        for key, value in candidate.items():
            if key not in base_set:
                if key not in feature_keys:
                    feature_keys.append(key)
                record[key] = value
        records.append(record)

    # ---- 5. Write outputs -----------------------------------------------------------
    version = settings.dataset_version
    processed_path = processed_dir / f"dataset_{version}.jsonl"
    features_path = features_dir / f"dataset_{version}_features.jsonl"
    split_paths: dict[str, str] = {}

    write_jsonl(processed_path, records)
    feature_rows = [
        {key: value for key, value in record.items() if key not in {"raw_text", "cleaned_text", "normalized_text"}}
        for record in records
    ]
    write_jsonl(features_path, feature_rows)

    for split_name in ("train", "validation", "test"):
        rows = [record for record in records if record["split"] == split_name]
        path = splits_dir / f"dataset_{version}_{split_name}.jsonl"
        write_jsonl(path, rows)
        split_paths[split_name] = str(path)

    quality_report = build_quality_report(
        total_input_rows=total_input,
        unusable_rows=unusable_before,
        kept=records,
        filtered=filtered,
        duplicates=duplicates,
        feature_names=feature_keys,
    )
    split_stats = split_statistics(records)

    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _relative(path_value: str | Path) -> str:
        try:
            return Path(path_value).resolve().relative_to(datasets_root.resolve()).as_posix()
        except ValueError:  # outside root — keep absolute
            return str(path_value)

    metadata = build_metadata(
        dataset_version=version,
        settings=settings,
        source_description=source_description,
        quality_report=quality_report,
        split_stats=split_stats,
        created_at=created_at,
        files={
            "processed": _relative(processed_path),
            "features": _relative(features_path),
            **{f"split_{name}": _relative(path) for name, path in split_paths.items()},
        },
    )
    _, report_path = write_metadata_and_report(
        metadata_dir,
        dataset_version=version,
        metadata=metadata,
        quality_report=quality_report,
    )

    return BuildResult(
        dataset_version=version,
        counts={
            "total_input": total_input,
            "kept": len(records),
            "filtered": len(filtered),
            "duplicates": len(duplicates),
            **split_stats,
        },
        files={
            "processed": str(processed_path),
            "features": str(features_path),
            **{f"split_{name}": str(path) for name, path in split_paths.items()},
            "metadata": str(metadata_dir / f"dataset_{version}.json"),
            "quality_report": report_path,
        },
    )


def _parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def dumps_json(payload: dict[str, Any]) -> str:
    """Stable JSON rendering used by tests to compare runs byte-for-byte."""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
