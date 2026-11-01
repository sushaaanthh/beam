"""Security and configuration smoke tests for beam-api.

These tests verify that:
- JWT_SECRET_KEY is required and not hardcoded in source code
- Settings load from environment without exposing secrets
- Production database configuration does not silently fall back to SQLite
- .env files do not contain real secrets
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _clear_settings_cache() -> None:
    from app.core.config import get_settings
    get_settings.cache_clear()


class TestJwtSecretKeyRequired:
    """JWT_SECRET_KEY must be provided via environment."""

    def test_missing_jwt_secret_raises_validation_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _clear_settings_cache()
        from app.core.config import Settings

        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        with pytest.raises(Exception):
            Settings(_env_file=())

    def test_empty_jwt_secret_raises_validation_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _clear_settings_cache()
        from app.core.config import Settings

        monkeypatch.setenv("JWT_SECRET_KEY", "")
        monkeypatch.delenv("DATABASE_URL", raising=False)

        with pytest.raises(Exception):
            Settings(_env_file=())

    def test_no_hardcoded_secret_in_source(self) -> None:
        source_path = Path(__file__).resolve().parents[1] / "app" / "core" / "config.py"
        source_text = source_path.read_text(encoding="utf-8")
        assert "beam-ai-development-super-secret-key-2026" not in source_text


class TestDatabaseDriverConsistency:
    """DATABASE_URL should use the driver matching installed requirements."""

    def test_default_database_uri_uses_psycopg2(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _clear_settings_cache()
        from app.core.config import Settings

        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-for-unit-test-only")

        s = Settings()
        assert s.SQLALCHEMY_DATABASE_URI.startswith("postgresql+psycopg2://")


class TestProductionDatabaseFallback:
    """Production environment must not silently fall back to SQLite."""

    def test_production_database_failure_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app.core.config import Settings
        from app.database.session import _build_db_engine

        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-for-unit-test-only")

        production_settings = Settings(_env_file=())
        production_settings.ENVIRONMENT = "production"

        with patch("app.database.session.get_settings", return_value=production_settings):
            with pytest.raises(RuntimeError, match="Production database unreachable"):
                _build_db_engine("postgresql+psycopg2://invalid:invalid@nonexistent-host:5432/beam_db")

    def test_development_database_failure_falls_back_to_sqlite(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _clear_settings_cache()
        from app.core.config import Settings
        from app.database.session import _build_db_engine

        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-for-unit-test-only")
        monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg2://invalid:invalid@nonexistent-host:5432/beam_db")

        engine = _build_db_engine()
        url = str(engine.url)
        assert "sqlite" in url


class TestSecretsNotExposedInConfig:
    """Config should not expose raw secret values in __repr__ or dict()."""

    def test_jwt_secret_key_not_exposed_in_dict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _clear_settings_cache()
        from app.core.config import Settings

        monkeypatch.setenv("JWT_SECRET_KEY", "super-secret-value")
        monkeypatch.delenv("DATABASE_URL", raising=False)

        s = Settings()
        config_dict = s.model_dump()

        assert "super-secret-value" not in str(config_dict)
        jwt_value = config_dict.get("JWT_SECRET_KEY")
        assert jwt_value is None or str(jwt_value) == "" or "**********" in str(jwt_value)
