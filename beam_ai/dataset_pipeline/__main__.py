"""Command-line entry point.

    python -m beam_ai.dataset_pipeline --help
    python -m beam_ai.dataset_pipeline \
        --input ../beam-datasets/raw/reddit_export.jsonl \
        --dataset-version v001 --seed 42

Outputs (under beam-datasets/):
    processed/dataset_<version>.jsonl      cleaned + normalized + features
    features/dataset_<version>_features.jsonl
    splits/dataset_<version>_{train,validation,test}.jsonl
    metadata/dataset_<version>.json        versioned metadata JSON
    metadata/quality_report_<version>.json

Raw inputs are never modified.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python -m beam_ai.dataset_pipeline` from repo root OR beam-ai/.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from beam_ai.configs.pipeline_settings import PipelineSettings  # noqa: E402
from beam_ai.dataset_pipeline.build import build_dataset  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="beam_ai.dataset_pipeline",
        description=(
            "Convert raw Reddit data into clean, reproducible research "
            "datasets: quality filtering, deterministic text cleaning and "
            "normalization, deduplication, feature extraction and grouped "
            "train/validation/test splitting with versioned metadata."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="raw input file (.csv/.jsonl) or directory of such files",
    )
    parser.add_argument(
        "--db-url",
        default=None,
        help="read from PostgreSQL via the scraper storage layer instead of a file",
    )
    parser.add_argument(
        "--datasets-root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "beam-datasets",
        help="output root containing processed/, features/, splits/, metadata/",
    )
    parser.add_argument("--dataset-version", default=None, help="dataset version tag, e.g. v001")
    parser.add_argument(
        "--language",
        default=None,
        help="comma-separated language allowlist (e.g. 'en' or 'en,de'); "
        "requires langdetect for allowlist mode",
    )
    parser.add_argument("--min-length", type=int, default=None, help="minimum cleaned character count")
    parser.add_argument("--max-length", type=int, default=None, help="maximum cleaned character count")
    parser.add_argument("--min-words", type=int, default=None, help="minimum word count")
    parser.add_argument("--seed", type=int, default=None, help="random seed for split ordering")
    parser.add_argument("--train-ratio", type=float, default=None)
    parser.add_argument("--validation-ratio", type=float, default=None)
    parser.add_argument("--test-ratio", type=float, default=None)
    return parser


def _apply_overrides(settings: PipelineSettings, args: argparse.Namespace) -> PipelineSettings:
    if args.dataset_version is not None:
        settings.dataset_version = args.dataset_version
    if args.language is not None:
        settings.languages = args.language
        settings.language_mode = "allowlist"
    if args.min_length is not None:
        settings.min_chars = args.min_length
    if args.max_length is not None:
        settings.max_chars = args.max_length
    if args.min_words is not None:
        settings.min_words = args.min_words
    if args.seed is not None:
        settings.random_seed = args.seed
    ratios = [args.train_ratio, args.validation_ratio, args.test_ratio]
    if any(r is not None for r in ratios):
        settings.train_ratio = args.train_ratio or settings.train_ratio
        settings.validation_ratio = args.validation_ratio or settings.validation_ratio
        settings.test_ratio = args.test_ratio or settings.test_ratio
    return settings


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.input is None and args.db_url is None:
        print("error: provide --input (file/directory) or --db-url", file=sys.stderr)
        return 2

    settings = _apply_overrides(get_settings_snapshot(), args)

    try:
        result = build_dataset(
            input_path=args.input,
            database_url=args.db_url,
            datasets_root=args.datasets_root,
            settings=settings,
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    counts = result.counts
    print(f"dataset {result.dataset_version} built:")
    print(f"  input rows      : {counts['total_input']}")
    print(f"  kept            : {counts['kept']}")
    print(f"  filtered        : {counts['filtered']}")
    print(f"  duplicates      : {counts['duplicates']}")
    print(
        f"  splits          : train={counts.get('train', 0)} "
        f"validation={counts.get('validation', 0)} test={counts.get('test', 0)}"
    )
    for label, path in result.files.items():
        print(f"  {label:<15}: {path}")
    return 0


def get_settings_snapshot() -> PipelineSettings:
    """Fresh settings instance so CLI flags do not mutate a cached object."""
    return PipelineSettings()


if __name__ == "__main__":
    raise SystemExit(main())
