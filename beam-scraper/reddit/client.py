"""Reusable Reddit client: authentication, validation, configured user agent.

This module deliberately contains NO scraping logic — collectors receive a
`RedditClient` (or any object exposing `.reddit`) and drive it themselves.
"""

from __future__ import annotations

import logging

import praw
import prawcore

logger = logging.getLogger(__name__)


class RedditClientError(Exception):
    """Raised when the Reddit client cannot be created or validated."""


class RedditClient:
    """Thin, reusable wrapper around PRAW."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        request_timeout: float = 30.0,
    ) -> None:
        if not client_id or not client_id.strip():
            raise RedditClientError("client_id is required")
        if not client_secret or not client_secret.strip():
            raise RedditClientError("client_secret is required")
        if not user_agent or not user_agent.strip():
            raise RedditClientError(
                "user_agent is required and must identify the research client"
            )

        self.user_agent = user_agent.strip()
        try:
            self._reddit = praw.Reddit(
                client_id=client_id.strip(),
                client_secret=client_secret.strip(),
                user_agent=self.user_agent,
                timeout=int(request_timeout),
                check_for_updates=False,
                check_for_async=False,
            )
            # Read-only: the scraper never authenticates as a user account.
            self._reddit.read_only = True
        except Exception as error:  # config errors from PRAW
            raise RedditClientError(f"failed to initialise Reddit client: {error}") from error

    @property
    def reddit(self) -> praw.Reddit:
        return self._reddit

    def validate_connection(self) -> bool:
        """Cheap read-only call to confirm credentials and connectivity."""
        try:
            _ = self._reddit.auth.scopes()
        except prawcore.exceptions.InsufficientScope:
            # Expected for script apps in read-only mode; credentials are valid.
            return True
        except prawcore.exceptions.OAuthException as error:
            raise RedditClientError(f"Reddit rejected the credentials: {error}") from error
        except prawcore.exceptions.PrawcoreException as error:
            raise RedditClientError(f"Reddit is unreachable: {error}") from error
        return True
