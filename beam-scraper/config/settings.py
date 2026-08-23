"""Central scraper configuration via environment variables (Pydantic Settings).

Credentials are never hardcoded; see .env.example for the expected variables.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SortMode = Literal["hot", "new", "top", "rising"]
TimeFilter = Literal["day", "week", "month", "year", "all"]


class SettingsError(Exception):
    """Raised when configuration is incomplete or invalid."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../beam-config/env/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Reddit credentials -------------------------------------------------
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "windows:beam-research-scraper:v1.0 (research data collection)"

    # --- Storage ------------------------------------------------------------
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/beam_db"

    # --- Collection defaults (CLI can override per run) ----------------------
    SUBREDDITS: str = "AskReddit,CasualConversation"
    POST_LIMIT: int = Field(default=100, ge=1, le=1000)
    COMMENT_LIMIT: int = Field(default=200, ge=0, le=2000)
    SCRAPE_SORT: SortMode = "new"
    TIME_FILTER: TimeFilter = "month"
    INCLUDE_COMMENTS: bool = True

    # --- Politeness / observability ------------------------------------------
    MIN_REQUEST_INTERVAL_SECONDS: float = Field(default=1.1, ge=0.1)
    MAX_RETRIES: int = Field(default=5, ge=1, le=10)
    BACKOFF_BASE_SECONDS: float = Field(default=2.0, gt=0)
    LOG_LEVEL: str = "INFO"

    @field_validator("REDDIT_USER_AGENT")
    @classmethod
    def _user_agent_not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("REDDIT_USER_AGENT must describe the research client")
        return value.strip()

    @property
    def subreddit_list(self) -> list[str]:
        """Configured subreddits as a cleaned, de-duplicated list."""
        seen: set[str] = set()
        result: list[str] = []
        for raw in self.SUBREDDITS.split(","):
            name = raw.strip().removeprefix("r/")
            if name and name.lower() not in seen:
                seen.add(name.lower())
                result.append(name)
        return result

    def require_reddit_credentials(self) -> None:
        if not self.REDDIT_CLIENT_ID or not self.REDDIT_CLIENT_SECRET:
            raise SettingsError(
                "Reddit credentials missing. Set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET in the environment (see .env.example)."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
