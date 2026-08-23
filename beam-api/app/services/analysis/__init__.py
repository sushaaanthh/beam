"""Service registry.

Single swap point for the inference backend:

    def get_analysis_service() -> AnalysisService:
        return TransformerAnalysisService()   # future

Until then the placeholder runs.
"""

from __future__ import annotations

from app.services.analysis.base import AnalysisService
from app.services.analysis.mock_service import MockAnalysisService


def get_analysis_service() -> AnalysisService:
    return MockAnalysisService()
