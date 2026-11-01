"""Shared test configuration for beam-api.

Ensures required environment variables are present before any test modules
import application code that depends on them.
"""

from __future__ import annotations

import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-for-unit-test-only")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key-for-unit-tests")
