"""Configuration tests."""

from __future__ import annotations

import pytest

from config.settings import Settings, SettingsError


def test_defaults_are_research_safe(clean_env) -> None:
    settings = Settings(_env_file=None)
    assert settings.POST_LIMIT == 100
    assert settings.SCRAPE_SORT == "new"
    assert settings.MIN_REQUEST_INTERVAL_SECONDS >= 1.0  # conservative pacing
    assert "AskReddit" in settings.subreddit_list


def test_subreddit_list_is_configurable_and_cleaned(clean_env, monkeypatch) -> None:
    monkeypatch.setenv("SUBREDDITS", " r/askreddit , CasualConversation ,, askreddit ")
    settings = Settings(_env_file=None)
    # deduplicated (case-insensitive), r/ prefix stripped
    assert settings.subreddit_list == ["askreddit", "CasualConversation"]


def test_missing_credentials_raise_settings_error(clean_env, monkeypatch) -> None:
    monkeypatch.setenv("REDDIT_CLIENT_ID", "")
    settings = Settings(_env_file=None)
    with pytest.raises(SettingsError):
        settings.require_reddit_credentials()


def test_env_overrides_apply(clean_env, monkeypatch) -> None:
    monkeypatch.setenv("REDDIT_CLIENT_ID", "id123")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "secret456")
    monkeypatch.setenv("POST_LIMIT", "25")
    monkeypatch.setenv("SCRAPE_SORT", "top")
    monkeypatch.setenv("TIME_FILTER", "week")

    settings = Settings(_env_file=None)
    assert settings.REDDIT_CLIENT_ID == "id123"
    assert settings.POST_LIMIT == 25
    assert settings.SCRAPE_SORT == "top"
    assert settings.TIME_FILTER == "week"


@pytest.mark.parametrize("value", ["0", "-5", "99999"])
def test_post_limit_bounds_are_enforced(clean_env, monkeypatch, value: str) -> None:
    monkeypatch.setenv("POST_LIMIT", value)
    with pytest.raises(ValueError):
        Settings(_env_file=None)
