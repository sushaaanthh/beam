"""Post/comment parsing and data-quality handling tests."""

from __future__ import annotations

import re

import pytest

from reddit.schemas import (
    BodyStatus,
    CommentRecord,
    ParseError,
    PostRecord,
    parse_comment,
    parse_submission,
    pseudonymize_author,
)
from tests.conftest import make_comment, make_submission

PSEUDONYM_PATTERN = re.compile(r"^[0-9a-f]{16}$")


class TestPostParsing:
    def test_full_post_parses_all_fields(self) -> None:
        record = parse_submission(make_submission())
        assert isinstance(record, PostRecord)
        assert record.reddit_post_id == "abc123"
        assert record.subreddit == "AskReddit"
        assert record.body_status is BodyStatus.AVAILABLE
        assert PSEUDONYM_PATTERN.match(record.author or "")
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


class TestAuthorAnonymization:
    """Raw Reddit handles must never reach the stored records."""

    def test_handle_replaced_by_deterministic_pseudonym(self) -> None:
        record = parse_submission(make_submission(author="research_observer"))
        # Not the raw handle, stable across calls, 16 lowercase hex chars.
        assert record.author != "research_observer"
        assert PSEUDONYM_PATTERN.match(record.author or "")
        again = parse_submission(make_submission(author="research_observer"))
        assert again.author == record.author

    def test_different_authors_get_different_pseudonyms(self) -> None:
        a = parse_submission(make_submission(author="user_a"))
        b = parse_submission(make_submission(author="user_b"))
        assert a.author != b.author

    def test_same_author_across_posts_and_comments_matches(self) -> None:
        post = parse_submission(make_submission(author="same_person"))
        comment: CommentRecord = parse_comment(
            make_comment(author="same_person"),
            post_id="abc123",
            subreddit="AskReddit",
            depth=0,
        )
        assert post.author == comment.author
        assert PSEUDONYM_PATTERN.match(post.author or "")

    def test_deleted_author_is_null_not_pseudonym(self) -> None:
        record = parse_submission(make_submission(author="[deleted]"))
        assert record.author is None

    def test_missing_author_is_null(self) -> None:
        record = parse_submission(make_submission(author=None))
        assert record.author is None

    def test_salt_change_reanonymizes_future_records(self, monkeypatch) -> None:
        from config.settings import get_settings

        first = pseudonymize_author("someone")
        monkeypatch.setenv("AUTHOR_HASH_SALT", "different-salt-value")
        get_settings.cache_clear()
        try:
            second = pseudonymize_author("someone")
        finally:
            get_settings.cache_clear()
        assert first != second
        assert PSEUDONYM_PATTERN.match(second or "")
