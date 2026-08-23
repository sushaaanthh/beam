"""Collector orchestration tests with a fully mocked Reddit API."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from sqlalchemy import select

from reddit.collector import SubredditCollector
from reddit.models import RedditComment, RedditPost
from reddit.rate_limit import RateLimiter
from reddit.storage import Storage
from tests.conftest import make_comment, make_submission


@dataclass
class FakeCommentForest:
    items: list
    replace_calls: int = field(default=0)

    def replace_more(self, limit=None) -> None:
        self.replace_calls += 1

    def __iter__(self):
        return iter(self.items)


class FakeReplies(list):
    pass


class FakeListing:
    def __init__(self, submissions: list) -> None:
        self._submissions = submissions

    def __call__(self, **kwargs):
        limit = kwargs.get("limit")
        return self._submissions[:limit] if limit else self._submissions


class FakeSubreddit:
    def __init__(self, submissions: list) -> None:
        self._submissions = submissions
        self.hot = FakeListing(submissions)
        self.new = FakeListing(submissions)
        self.rising = FakeListing(submissions)

    def top(self, time_filter: str = "month", **kwargs):
        return FakeListing(self._submissions)(**kwargs)


class FakeReddit:
    """Duck-typed praw.Reddit with canned data and call counters."""

    def __init__(self, submissions_by_subreddit: dict[str, list], comments_by_post: dict[str, list]) -> None:
        self._submissions = submissions_by_subreddit
        self._comments = comments_by_post
        self.listing_calls = 0

    def subreddit(self, name: str) -> FakeSubreddit:
        return FakeSubreddit(self._submissions.get(name, []))

    def submission(self, id: str):
        comments = self._comments.get(id, [])

        @dataclass
        class SubmissionStub:
            id: str
            title: str = ""
            selftext: str = "body"
            author: str | None = "op"
            subreddit: str = "AskReddit"
            created_utc: float = 1_760_000_000.0
            score: int = 1
            upvote_ratio: float = 1.0
            num_comments: int = 0
            url: str = ""
            permalink: str = ""
            over_18: bool = False
            spoiler: bool = False
            stickied: bool = False
            comments: FakeCommentForest = field(
                default_factory=lambda: FakeCommentForest(comments)
            )

        return SubmissionStub(
            id=id,
            title=f"post {id}",
            num_comments=len(comments),
        )


@pytest.fixture()
def storage(tmp_path) -> Storage:
    storage = Storage(f"sqlite:///{tmp_path / 'collector_test.db'}")
    storage.create_schema()
    return storage


def _fast_limiter() -> RateLimiter:
    return RateLimiter(min_interval_seconds=0.01, max_retries=2, backoff_base_seconds=0.01)


class TestSubredditCollection:
    def test_collects_posts_and_nested_comments(self, storage: Storage) -> None:
        reddit = FakeReddit({"AskReddit": [make_submission(id="p1"), make_submission(id="p2")]}, {})
        collector = SubredditCollector(reddit, storage, _fast_limiter())

        summary = collector.collect_subreddit(
            subreddit="AskReddit", limit=10, sort="new", include_comments=False
        )

        assert summary.posts_inserted == 2
        assert summary.duplicates == 0
        assert summary.parse_errors == []
        assert summary.duration_seconds >= 0

    def test_malformed_post_does_not_abort_run(self, storage: Storage) -> None:
        broken = make_submission(id="", title="no id")  # invalid: empty id
        good = make_submission(id="ok1")

        reddit = FakeReddit({"AskReddit": [broken, good]}, {})
        collector = SubredditCollector(reddit, storage, _fast_limiter())

        summary = collector.collect_subreddit(subreddit="AskReddit", limit=10)

        assert summary.posts_inserted == 1  # healthy record survived
        assert len(summary.parse_errors) >= 1

    def test_duplicates_counted_not_reinserted(self, storage: Storage) -> None:
        reddit = FakeReddit(
            {"AskReddit": [make_submission(id="dup", score=5), make_submission(id="dup", score=9)]},
            {},
        )
        collector = SubredditCollector(reddit, storage, _fast_limiter())

        summary = collector.collect_subreddit(
            subreddit="AskReddit", limit=10, include_comments=False
        )

        assert summary.posts_inserted == 1
        assert summary.posts_updated == 1
        assert summary.duplicates == 1

    def test_comment_collection_stores_nested_tree(self, storage: Storage) -> None:
        # Build: top comment c1 with reply c2 (depth 1).
        c1 = make_comment(id="c1", parent_id="t3_p1")
        setattr(c1, "replies", FakeReplies([make_comment(id="c2", parent_id="t1_c1")]))

        reddit = FakeReddit({"AskReddit": [make_submission(id="p1")]}, {"p1": [c1]})
        collector = SubredditCollector(reddit, storage, _fast_limiter())

        summary = collector.collect_subreddit(
            subreddit="AskReddit", limit=5, include_comments=True, comment_limit=50
        )

        with storage.session() as session:
            posts = list(session.scalars(select(RedditPost)))
            comments = {c.reddit_comment_id: c for c in session.scalars(select(RedditComment))}

        assert summary.posts_inserted == 1
        assert set(comments) == {"c1", "c2"}
        assert comments["c1"].depth == 0
        assert comments["c2"].depth == 1
        assert all(c.post_id == "p1" for c in comments.values())
        assert len(posts) == 1

    def test_single_post_mode_stores_parent_first(self, storage: Storage) -> None:
        reddit = FakeReddit({}, {"xyz": [make_comment(id="cx", parent_id="t3_xyz")]})
        collector = SubredditCollector(reddit, storage, _fast_limiter())

        summary = collector.collect_single_post(subreddit="AskReddit", post_id="xyz", comment_limit=25)

        with storage.session() as session:
            stored_post = session.scalar(select(RedditPost))
            comments = list(session.scalars(select(RedditComment)))

        assert stored_post.reddit_post_id == "xyz"
        assert summary.comments_inserted == 1
        assert comments[0].post_id == "xyz"

    def test_top_sort_passes_time_filter(self, storage: Storage) -> None:
        received: dict[str, object] = {}

        class TimeFilterSubreddit(FakeSubreddit):
            def top(self, time_filter: str = "month", **kwargs):
                received["time_filter"] = time_filter
                return FakeListing(self._submissions)(**kwargs)

        class RedditWithTF(FakeReddit):
            def subreddit(self, name: str):
                return TimeFilterSubreddit(self._submissions.get(name, []))

        reddit = RedditWithTF({"AskReddit": [make_submission()]}, {})
        collector = SubredditCollector(reddit, storage, _fast_limiter())

        summary = collector.collect_subreddit(
            subreddit="AskReddit", limit=5, sort="top", time_filter="week"
        )

        assert received["time_filter"] == "week"
        assert summary.posts_inserted == 1
