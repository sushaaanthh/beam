"""Dedup, language filtering, splitting and end-to-end reproducibility."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beam_ai.configs.pipeline_settings import PipelineSettings
from beam_ai.dataset_pipeline.build import build_dataset
from beam_ai.dataset_pipeline.io_utils import write_jsonl
from beam_ai.dataset_pipeline.splitting import assign_splits
from beam_ai.preprocessing.deduplication import Deduplicator
from beam_ai.preprocessing.language import LanguageFilter
from tests.dataset_pipeline.conftest import comment_row, make_settings, post_row, write_jsonl


class TestDeduplication:
    def test_exact_duplicate_detected(self) -> None:
        dedupe = Deduplicator()
        first = dedupe.check(record_id="a", sort_key="1", subreddit="r", normalized_text="i love this so much")
        second = dedupe.check(record_id="b", sort_key="2", subreddit="r", normalized_text="I LOVE THIS SO MUCH".lower())
        assert not first.duplicate
        assert second.duplicate and second.reason == "duplicate_exact"

    def test_near_duplicate_within_subreddit(self) -> None:
        # 21 tokens, only the final word differs -> Jaccard = 18/20 = 0.90.
        head = (
            "i have been feeling really anxious about the upcoming exam all "
            "week long and i cannot seem to focus on"
        )
        base = f"{head} stressed"
        variant = f"{head} worried"
        dedupe = Deduplicator(near_threshold=0.9)
        first = dedupe.check(record_id="a", sort_key="1", subreddit="r", normalized_text=base)
        second = dedupe.check(record_id="b", sort_key="2", subreddit="r", normalized_text=variant)
        assert not first.duplicate
        assert second.duplicate and second.reason == "duplicate_near"

    def test_moderately_similar_discussions_survive(self) -> None:
        dedupe = Deduplicator(near_threshold=0.9)
        a = "I love working with my team on hard problems every single day"
        b = "My team struggles with deadlines but we still ship quality work"
        first = dedupe.check(record_id="a", sort_key="1", subreddit="r", normalized_text=a)
        second = dedupe.check(record_id="b", sort_key="2", subreddit="r", normalized_text=b)
        assert not first.duplicate and not second.duplicate

    def test_same_text_in_different_subreddits_survives(self) -> None:
        dedupe = Deduplicator()
        text = "identical crosspost body content here"
        first = dedupe.check(record_id="a", sort_key="1", subreddit="subA", normalized_text=text)
        second = dedupe.check(record_id="b", sort_key="2", subreddit="subB", normalized_text=text)
        assert not first.duplicate and not second.duplicate

    def test_disabled_deduplicator_keeps_everything(self) -> None:
        dedupe = Deduplicator(enabled=False)
        for rid in ("a", "b"):
            verdict = dedupe.check(record_id=rid, sort_key="1", subreddit="r", normalized_text="same words")
            assert not verdict.duplicate


class TestLanguageFiltering:
    def test_off_mode_records_unknown_and_keeps(self) -> None:
        settings = make_settings(language_mode="off")
        decision = LanguageFilter(settings).evaluate("Bonjour tout le monde")
        assert decision.language == "unknown" and decision.kept

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("langdetect"),
        reason="langdetect not installed",
    )
    def test_allowlist_filters_with_recorded_reason(self) -> None:
        settings = make_settings(language_mode="allowlist", languages="en")
        decision = LanguageFilter(settings).evaluate(
            "Ceci est un texte en français pour tester la détection de langue"
        )
        assert not decision.kept
        assert decision.reason == "language:fr"

    def test_degrades_to_off_without_langdetect(self, monkeypatch) -> None:
        import importlib.util

        real_find = importlib.util.find_spec

        def fake_find(name: str):
            if name == "langdetect":
                return None
            return real_find(name)

        monkeypatch.setattr(importlib.util, "find_spec", fake_find)
        import beam_ai.preprocessing.language as language_module

        original = language_module.LANGDETECT_AVAILABLE
        language_module.LANGDETECT_AVAILABLE = False
        try:
            settings = make_settings(language_mode="allowlist", languages="en")
            filter_instance = LanguageFilter(settings)
            assert filter_instance.degraded is True
            decision = filter_instance.evaluate("anything at all")
            assert decision.kept and decision.language == "unknown"
        finally:
            language_module.LANGDETECT_AVAILABLE = original


class TestSplitting:
    def test_ratios_respected_and_groups_intact(self) -> None:
        groups = [f"thread_{i}" for i in range(100)]
        assignment = assign_splits(groups, train_ratio=0.7, validation_ratio=0.15, test_ratio=0.15, seed=42)

        counts = {"train": 0, "validation": 0, "test": 0}
        for value in assignment.values():
            counts[value] += 1
        assert sum(counts.values()) == 100
        # Within rounding tolerance of 70/15/15.
        assert abs(counts["train"] - 70) <= 2
        assert abs(counts["validation"] - 15) <= 2
        assert abs(counts["test"] - 15) <= 2

    def test_deterministic_for_same_seed(self) -> None:
        groups = [f"g{i}" for i in range(50)]
        one = assign_splits(groups, train_ratio=0.7, validation_ratio=0.15, test_ratio=0.15, seed=7)
        two = assign_splits(groups, train_ratio=0.7, validation_ratio=0.15, test_ratio=0.15, seed=7)
        assert one == two

    def test_seed_changes_assignment(self) -> None:
        groups = [f"g{i}" for i in range(50)]
        one = assign_splits(groups, train_ratio=0.7, validation_ratio=0.15, test_ratio=0.15, seed=1)
        two = assign_splits(groups, train_ratio=0.7, validation_ratio=0.15, test_ratio=0.15, seed=999)
        assert one != two

    def test_invalid_ratios_rejected(self) -> None:
        with pytest.raises(ValueError):
            assign_splits(["a"], train_ratio=0.5, validation_ratio=0.5, test_ratio=0.5, seed=1)


def _build_from_rows(tmp_path: Path, rows: list[dict], **overrides):
    raw_file = write_jsonl(tmp_path / "raw" / "input.jsonl", rows)
    datasets_root = tmp_path / "datasets"
    settings = make_settings(language_mode="off", **overrides)
    result = build_dataset(input_path=raw_file, datasets_root=datasets_root, settings=settings)
    return result, datasets_root


class TestEndToEndBuild:
    def _sample_rows(self) -> list[dict]:
        rows = []
        for i in range(12):
            rows.append(post_row(post_id=f"p{i}", title=f"Title number {i}", body=f"This is unique discussion body number {i} with enough words to pass filters.", score=i))
            rows.append(comment_row(comment_id=f"c{i}a", post_id=f"p{i}", body=f"A reply to thread {i} sharing feelings of joy and relief today."))
        # Exact duplicate of p3 (same title AND body, different Reddit id).
        rows.append(post_row(post_id="dup", title="Title number 3", body="This is unique discussion body number 3 with enough words to pass filters."))
        rows.append(post_row(post_id="short", title="", body="hi"))
        rows.append(post_row(post_id="removed", body="[removed]", body_status="removed"))
        return rows

    def test_outputs_generated_and_raw_untouched(self, tmp_path: Path) -> None:
        raw_file = tmp_path / "raw" / "input.jsonl"
        rows = self._sample_rows()
        write_jsonl(raw_file, rows)
        raw_bytes_before = raw_file.read_bytes()

        datasets_root = tmp_path / "datasets"
        result = build_dataset(
            input_path=raw_file,
            datasets_root=datasets_root,
            settings=make_settings(language_mode="off"),
        )

        processed = Path(result.files["processed"])
        features = Path(result.files["features"])
        metadata = Path(result.files["metadata"])
        report = Path(result.files["quality_report"])

        assert processed.exists() and features.exists() and metadata.exists() and report.exists()
        for split_name in ("train", "validation", "test"):
            assert Path(result.files[f"split_{split_name}"]).exists()

        # Raw input untouched.
        assert raw_file.read_bytes() == raw_bytes_before

    def test_counts_and_duplicate_reason(self, tmp_path: Path) -> None:
        result, datasets_root = _build_from_rows(tmp_path, self._sample_rows())

        report = json.loads((datasets_root / "metadata" / "quality_report_v001.json").read_text())
        assert report["total_records"] == len(self._sample_rows())
        # The full duplicate of p3 is caught by exact normalized-text match.
        assert report["duplicate_reasons"].get("duplicate_exact", 0) >= 1
        assert "too_short" in report["filter_reasons"]
        assert "content_removed" in report["filter_reasons"]
        # 12 threads survive; the dup/short/removed rows are filtered or deduped.
        assert report["valid_records"] == 24

    def test_thread_grouping_prevents_leakage(self, tmp_path: Path) -> None:
        result, datasets_root = _build_from_rows(tmp_path, self._sample_rows())
        split_rows = []
        for split_name in ("train", "validation", "test"):
            path = datasets_root / "splits" / f"dataset_v001_{split_name}.jsonl"
            for line in path.read_text().splitlines():
                row = json.loads(line)
                split_rows.append((row["thread_id"], split_name))

        threads_by_split: dict[str, set] = {}
        for thread_id, split_name in split_rows:
            threads_by_split.setdefault(split_name, set()).add(thread_id)

        # No thread appears in more than one split.
        seen: set = set()
        for threads in threads_by_split.values():
            assert not (threads & seen), "thread leaked across splits"
            seen |= threads

    def test_metadata_fields_complete(self, tmp_path: Path) -> None:
        _, datasets_root = _build_from_rows(tmp_path, self._sample_rows())
        metadata = json.loads((datasets_root / "metadata" / "dataset_v001.json").read_text())

        for field in (
            "dataset_version",
            "processing_version",
            "created_at",
            "source",
            "record_count",
            "feature_count",
            "split_statistics",
            "configuration",
            "label_type",
            "quality_report",
            "files",
        ):
            assert field in metadata, field
        assert metadata["label_type"] == "unlabeled"

    def test_reproducibility_identical_outputs(self, tmp_path: Path) -> None:
        rows = self._sample_rows()
        raw_file = write_jsonl(tmp_path / "raw" / "input.jsonl", rows)
        raw_bytes_before = raw_file.read_bytes()

        digests_first = self._collect_digests(build_dataset(
            input_path=raw_file,
            datasets_root=tmp_path / "run_one",
            settings=make_settings(language_mode="off"),
        ))
        digests_second = self._collect_digests(build_dataset(
            input_path=raw_file,
            datasets_root=tmp_path / "run_two",
            settings=make_settings(language_mode="off"),
        ))

        assert digests_first == digests_second, "same input+config+seed must reproduce byte-identical outputs"

    @staticmethod
    def _collect_digests(result) -> dict[str, str]:
        import hashlib

        digests = {}
        for label, path in result.files.items():
            data = Path(path).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if label == "metadata":  # created_at timestamp intentionally varies
                payload = json.loads(data)
                payload.pop("created_at")
                digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            digests[label] = digest
        return digests
