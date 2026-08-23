"""Quality report + dataset metadata generation (JSON, sort_keys=True)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beam_ai import PROCESSING_VERSION
from beam_ai.dataset_pipeline.io_utils import write_json
from beam_ai.features.nlp_features import nlp_availability


def build_quality_report(
    *,
    total_input_rows: int,
    unusable_rows: int,
    kept: list[dict[str, Any]],
    filtered: list[str],
    duplicates: list[str],
    feature_names: list[str] | None = None,
) -> dict[str, Any]:
    reasons: dict[str, int] = {}
    for reason in filtered:
        reasons[reason] = reasons.get(reason, 0) + 1

    duplicate_reasons: dict[str, int] = {}
    for reason in duplicates:
        duplicate_reasons[reason] = duplicate_reasons.get(reason, 0) + 1

    text_lengths = [len(row["cleaned_text"]) for row in kept]
    languages: dict[str, int] = {}
    subreddits: dict[str, int] = {}
    sources: dict[str, int] = {}
    for row in kept:
        languages[row["language"]] = languages.get(row["language"], 0) + 1
        subreddit = row["subreddit"] or "(none)"
        subreddits[subreddit] = subreddits.get(subreddit, 0) + 1
        sources[row["source"]] = sources.get(row["source"], 0) + 1

    return {
        "total_records": total_input_rows,
        "unusable_input_rows": unusable_rows,
        "valid_records": len(kept),
        "filtered_records": len(filtered),
        "duplicate_records": len(duplicates),
        "filter_reasons": dict(sorted(reasons.items())),
        "duplicate_reasons": dict(sorted(duplicate_reasons.items())),
        "average_cleaned_text_length": round(sum(text_lengths) / len(text_lengths), 2)
        if text_lengths
        else 0.0,
        "language_distribution": dict(sorted(languages.items())),
        "subreddit_distribution": dict(sorted(subreddits.items())),
        "source_distribution": dict(sorted(sources.items())),
        "feature_names": sorted(feature_names or []),
        "feature_count": len(feature_names or []),
        "nlp_backends": nlp_availability(),
    }


def build_metadata(
    *,
    dataset_version: str,
    settings: Any,
    source_description: str,
    quality_report: dict[str, Any],
    split_stats: dict[str, int],
    created_at: str,
    files: dict[str, str],
) -> dict[str, Any]:
    return {
        "dataset_version": dataset_version,
        "processing_version": PROCESSING_VERSION,
        "created_at": created_at,
        "source": source_description,
        "record_count": quality_report["valid_records"],
        "feature_count": quality_report["feature_count"],
        "label_type": "unlabeled",
        "intended_use": (
            "Research corpus for future emotion-model development. No emotion "
            "labels are claimed; VADER scores are auxiliary lexical features."
        ),
        "configuration": {
            "min_chars": settings.min_chars,
            "max_chars": settings.max_chars,
            "min_words": settings.min_words,
            "keep_deleted": settings.keep_deleted,
            "dedupe_enabled": settings.dedupe_enabled,
            "near_duplicate_threshold": settings.near_duplicate_threshold,
            "near_duplicate_method": "word-3gram jaccard within subreddit",
            "language_mode": settings.language_mode,
            "languages": sorted(settings.resolved_languages()),
            "split": {
                "train_ratio": settings.train_ratio,
                "validation_ratio": settings.validation_ratio,
                "test_ratio": settings.test_ratio,
                "seed": settings.random_seed,
                "strategy": "grouped by thread_id, sha256(seed:group) ordering",
            },
        },
        "split_statistics": split_stats,
        "quality_report": quality_report,
        "files": files,
    }


def write_metadata_and_report(
    metadata_dir: Path,
    *,
    dataset_version: str,
    metadata: dict[str, Any],
    quality_report: dict[str, Any],
) -> tuple[str, str]:
    metadata_path = metadata_dir / f"dataset_{dataset_version}.json"
    report_path = metadata_dir / f"quality_report_{dataset_version}.json"
    write_json(metadata_path, metadata)
    write_json(report_path, quality_report)
    return str(metadata_path), str(report_path)
