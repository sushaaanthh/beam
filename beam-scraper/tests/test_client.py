"""Reddit client initialization tests (no network access)."""

from __future__ import annotations

import pytest

from reddit.client import RedditClient, RedditClientError


def test_client_requires_client_id() -> None:
    with pytest.raises(RedditClientError, match="client_id"):
        RedditClient(client_id="", client_secret="s", user_agent="ua")


def test_client_requires_client_secret() -> None:
    with pytest.raises(RedditClientError, match="client_secret"):
        RedditClient(client_id="id", client_secret="  ", user_agent="ua")


def test_client_requires_user_agent() -> None:
    with pytest.raises(RedditClientError, match="user_agent"):
        RedditClient(client_id="id", client_secret="secret", user_agent="")


def test_client_initialises_read_only(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakePrawReddit:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)
            self.read_only = False
            self.auth = type("Auth", (), {"scopes": staticmethod(lambda: ["identity"])})()

    import reddit.client as client_module

    monkeypatch.setattr(client_module.praw, "Reddit", FakePrawReddit)

    client = RedditClient(
        client_id=" my-id ",
        client_secret="my-secret",
        user_agent="windows:beam-research-scraper:v1.0",
    )

    assert client.user_agent == "windows:beam-research-scraper:v1.0"
    assert captured["user_agent"] == "windows:beam-research-scraper:v1.0"
    assert client.reddit is not None
    assert client.validate_connection() is True


def test_client_rejects_bad_credentials(monkeypatch) -> None:
    import prawcore
    import reddit.client as client_module

    class FailingPrawReddit:
        def __init__(self, **kwargs) -> None:
            self.auth = type("Auth", (), {})()

            def scopes():
                raise prawcore.exceptions.OAuthException(401, "invalid credentials")

            self.auth.scopes = scopes

    monkeypatch.setattr(client_module.praw, "Reddit", FailingPrawReddit)

    with pytest.raises(RedditClientError, match="rejected the credentials"):
        RedditClient(client_id="id", client_secret="bad", user_agent="ua").validate_connection()
