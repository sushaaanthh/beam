"""Post/comment parsing and data-quality handling tests."""

from __future__ import annotations

import pytest

from reddit.schemas import BodyStatus, CommentRecord, ParseError, PostRecord, parse_comment, parse_submission
from tests.conftest import make_comment, make_submission


class TestPostParsing:
    def test_full_post_parses_all_fields(self) -> None:
        record = parse_submission(make_submission())
        assert isinstance(record, PostRecord)
        assert record.reddit_post_id == "abc123"
        assert record.subreddit == "AskReddit"
        assert record.body_status is BodyStatus.AVAILABLE
        assert record.author == "research_observer"
        assert record.is_nsfw is False
        assert record.score == 42
        assert record.created_utc.tzinfo is not None

    def test_removed_body_is_flagged_not_dropped(self) -> None:
        record = parse_submission(make_submission(selftext="[removed]"))
        assert record.body is None
        assert record.body_status is BodyStatus.REMOVED

    def test_deleted_body_is_flagged(self) -> None:
        record = parse_submission(make_submission(selftext="[deleted]"))
        assert record.body_status is BodyStatus.DELETED

    def test_empty_selftext_marks_empty(self) -> None:
        record = parse_submission(make_submission(selftext=""))
        assert record.body is None
        assert record.body_status is BodyStatus.EMPTY

    def test_link_only_posts_have_empty_body(self) -> None:
        record = parse_submission(make_submission(selftext=None))
        assert record.body_status is BodyStatus.EMPTY

    def test_deleted_author_becomes_none(self) -> None:
        record = parse_submission(make_submission(author="[deleted]"))
        assert record.author is None

    def test_nsfw_spoiler_stickied_flags(self) -> None:
        record = parse_submission(
            make_submission(over_18=True, spoiler=True, stickied=True)
        )
        assert record.is_nsfw and record.is_spoiler and record.stickied

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"id": ""},
            {"id": "   "},
            {"title": ""},
            {"created_utc": None},
        ],
    )
    def test_invalid_submissions_raise_parse_error(self, kwargs) -> None:
        with pytest.raises(ParseError):
            parse_submission(make_submission(**kwargs))


class TestCommentParsing:
    def test_comment_parses_with_parent_and_depth(self) -> None:
        record: CommentRecord = parse_comment(
            make_comment(),
            post_id="abc123",
            subreddit="AskReddit",
            depth=2,
        )
        assert record.reddit_comment_id == "c1"
        assert record.post_id == "abc123"
        assert record.parent_id == "abc123"  # t3_ prefix stripped
        assert record.depth == 2
        assert record.body_status is BodyStatus.AVAILABLE

    def test_removed_comment_flagged(self) -> None:
        record = parse_comment(
            make_comment(body="[removed]"),
            post_id="abc123",
            subreddit="AskReddit",
            depth=0,
        )
        assert record.body is None
        assert record.body_status is BodyStatus.REMOVED

    def test_deleted_author_none(self) -> None:
        record = parse_comment(
            make_comment(author="[deleted]"),
            post_id="abc123",
            subreddit="AskReddit",
            depth=0,
        )
        assert record.author is None

    def test_missing_id_raises(self) -> None:
        with pytest.raises(ParseError):
            parse_comment(
                make_comment(id=""),
                post_id="abc123",
                subreddit="AskReddit",
                depth=0,
            )

    def test_negative_depth_clamped_to_zero(self) -> None:
        record = parse_comment(
            make_comment(), post_id="abc123", subreddit="AskReddit", depth=-3
        )
        assert record.depth == 0
