"""CLI argument parsing tests (no execution, no network)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def scrape_subreddit():
    return _load_script("scrape_subreddit")


class TestScrapeSubredditArgs:
    def test_example_command_parses(self, scrape_subreddit) -> None:
        args = scrape_subreddit.build_parser().parse_args(
            ["--subreddit", "AskReddit", "--limit", "50", "--sort", "new"]
        )
        assert args.subreddit == ["AskReddit"]
        assert args.limit == 50
        assert args.sort == "new"

    def test_top_with_time_filter(self, scrape_subreddit) -> None:
        args = scrape_subreddit.build_parser().parse_args(
            ["--subreddit", "AskReddit", "--limit", "50", "--sort", "top", "--time-filter", "month"]
        )
        assert args.sort == "top"
        assert args.time_filter == "month"

    def test_multiple_subreddits_accepted(self, scrape_subreddit) -> None:
        args = scrape_subreddit.build_parser().parse_args(
            ["--subreddit", "AskReddit", "CasualConversation", "--limit", "5"]
        )
        assert args.subreddit == ["AskReddit", "CasualConversation"]

    def test_r_prefix_stripped_later_not_rejected(self, scrape_subreddit) -> None:
        args = scrape_subreddit.build_parser().parse_args(["--subreddit", "r/AskReddit"])
        assert args.subreddit == ["r/AskReddit"]  # normalised at run time

    def test_invalid_sort_rejected(self, scrape_subreddit, capsys) -> None:
        with pytest.raises(SystemExit):
            scrape_subreddit.build_parser().parse_args(["--sort", "controversial"])
        assert "invalid choice" in capsys.readouterr().err

    def test_invalid_time_filter_rejected(self, scrape_subreddit, capsys) -> None:
        with pytest.raises(SystemExit):
            scrape_subreddit.build_parser().parse_args(["--time-filter", "decade"])

    def test_help_exits_cleanly(self, scrape_subreddit, capsys) -> None:
        with pytest.raises(SystemExit) as excinfo:
            scrape_subreddit.build_parser().parse_args(["--help"])
        assert excinfo.value.code == 0
        out = capsys.readouterr().out
        for expected in ("--subreddit", "--limit", "--sort", "--time-filter"):
            assert expected in out


class TestScrapePostArgs:
    @pytest.fixture()
    def scrape_post(self):
        return _load_script("scrape_post")

    def test_post_id_requires_subreddit_flag(self, scrape_post) -> None:
        args = scrape_post.build_parser().parse_args(["--post-id", "abc123"])
        # Validation happens at resolution time, not parse time.
        assert scrape_post.resolve_target(args) is None

    def test_url_form_parses_without_subreddit(self, scrape_post) -> None:
        args = scrape_post.build_parser().parse_args(
            [
                "--url",
                "https://www.reddit.com/r/AskReddit/comments/abc123/some_title/",
            ]
        )
        resolved = scrape_post.resolve_target(args)
        assert resolved == ("AskReddit", "abc123")

    def test_unrelated_url_rejected(self, scrape_post, capsys) -> None:
        args = scrape_post.build_parser().parse_args(["--url", "https://example.com/x"])
        assert scrape_post.resolve_target(args) is None


class TestExportArgs:
    @pytest.fixture()
    def export_data(self):
        return _load_script("export_data")

    def test_defaults(self, export_data) -> None:
        args = export_data.build_parser().parse_args([])
        assert args.format == "csv"
        assert args.comments is False

    def test_jsonl_comments(self, export_data) -> None:
        args = export_data.build_parser().parse_args(["--format", "jsonl", "--comments"])
        assert args.format == "jsonl"
        assert args.comments is True
