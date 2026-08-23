"""Storage tests: deduplication, mutable-metadata updates, indexes, cascade."""

from __future__ import annotations

import pytest
from sqlalchemy import inspect, select

from reddit.models import RedditComment, RedditPost
from reddit.schemas import BodyStatus, parse_comment, parse_submission
from reddit.storage import Storage
from tests.conftest import make_comment, make_submission


@pytest.fixture()
def storage(tmp_path) -> Storage:
    storage = Storage(f"sqlite:///{tmp_path / 'scraper_test.db'}")
    storage.create_schema()
    return storage


class TestPostDeduplication:
    def test_same_post_id_inserted_once(self, storage: Storage) -> None:
        with storage.session() as session:
            first = storage.save_post(session, parse_submission(make_submission(score=10)))
            second = storage.save_post(session, parse_submission(make_submission(score=99)))
            session.commit()

            assert first == "inserted"
            assert second == "updated"
            posts = list(session.scalars(select(RedditPost)))
            assert len(posts) == 1
            assert posts[0].score == 99  # mutable metadata refreshed

    def test_identical_repost_is_unchanged(self, storage: Storage) -> None:
        with storage.session() as session:
            storage.save_post(session, parse_submission(make_submission()))
            action = storage.save_post(session, parse_submission(make_submission()))
            session.commit()
            assert action == "unchanged"

    def test_retrieved_at_preserved_on_update(self, storage: Storage) -> None:
        original = parse_submission(make_submission())
        with storage.session() as session:
            storage.save_post(session, original)
            session.commit()

        later = parse_submission(make_submission(score=77), retrieved_at=None)
        with storage.session() as session:
            storage.save_post(session, later)
            session.commit()
            stored = session.scalar(select(RedditPost))
            # SQLite drops tzinfo; compare wall-clock instants.
            assert stored.retrieved_at.replace(tzinfo=None) == original.retrieved_at.replace(tzinfo=None)


class TestCommentDeduplication:
    def test_comments_require_parent_post(self, storage: Storage) -> None:
        # FK: comment cannot outlive/precede its post.
        with pytest.raises(Exception):
            with storage.session() as session:
                record = parse_comment(
                    make_comment(), post_id="ghost", subreddit="AskReddit", depth=0
                )
                storage.save_comment(session, record)
                session.commit()

    def test_comment_upsert_updates_score(self, storage: Storage) -> None:
        with storage.session() as session:
            post = parse_submission(make_submission())
            storage.save_post(session, post)
            storage.save_comment(
                session,
                parse_comment(make_comment(score=1), post_id=post.reddit_post_id, subreddit=post.subreddit, depth=0),
            )
            session.commit()

        with storage.session() as session:
            action = storage.save_comment(
                session,
                parse_comment(make_comment(score=500), post_id="abc123", subreddit="AskReddit", depth=0),
            )
            session.commit()
            comments = list(session.scalars(select(RedditComment)))
            assert action == "updated"
            assert len(comments) == 1
            assert comments[0].score == 500

    def test_deleting_post_cascades_to_comments(self, storage: Storage) -> None:
        with storage.session() as session:
            post = parse_submission(make_submission())
            storage.save_post(session, post)
            storage.save_comment(
                session,
                parse_comment(make_comment(), post_id=post.reddit_post_id, subreddit=post.subreddit, depth=0),
            )
            session.commit()

        with storage.session() as session:
            stored_post = session.scalar(select(RedditPost))
            session.delete(stored_post)
            session.commit()
            assert session.scalars(select(RedditComment)).all() == []


class TestSchemaAndIndexes:
    def test_unique_constraints_and_indexes_exist(self, storage: Storage) -> None:
        inspector = inspect(storage.engine)

        post_indexes = {idx["name"] for idx in inspector.get_indexes("reddit_posts")}
        comment_indexes = {idx["name"] for idx in inspector.get_indexes("reddit_comments")}

        assert "ix_reddit_posts_subreddit" in post_indexes
        assert "ix_reddit_posts_created_utc" in post_indexes
        assert "ix_reddit_posts_subreddit_created" in post_indexes
        assert "ix_reddit_comments_post_id" in comment_indexes
        assert "ix_reddit_comments_reddit_comment_id" in comment_indexes

        uniques = {
            constraint["name"]
            for constraint in inspector.get_unique_constraints("reddit_posts")
        }
        assert "uq_reddit_posts_reddit_post_id" in uniques

    def test_removed_content_stored_with_status(self, storage: Storage) -> None:
        removed = parse_submission(make_submission(selftext="[removed]"))
        with storage.session() as session:
            storage.save_post(session, removed)
            session.commit()
            stored = session.scalar(select(RedditPost))
            assert stored.body is None
            assert stored.body_status == BodyStatus.REMOVED.value
