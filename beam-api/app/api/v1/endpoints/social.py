from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field

from app.services.reddit_service import (
    analyze_reddit_source,
    get_cached_reddit_analysis,
    CACHE_TTL
)

router = APIRouter(prefix="/social", tags=["social"])


def _get_user_id_from_req(request: Request) -> str:
    token_data = getattr(request.state, "token_data", None)
    if token_data and token_data.user_id:
        return str(token_data.user_id)
    return "default"


class RedditAnalysisRequest(BaseModel):
    identifier: str = Field(default="u/student_dev", min_length=2)
    source_type: str = Field(default="username")  # 'username' or 'subreddit'
    max_items: int = Field(default=5, ge=1, le=100)
    force_refresh: bool = Field(default=False)


@router.post("/reddit")
async def analyze_reddit(payload: RedditAnalysisRequest, request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    result = await analyze_reddit_source(
        identifier=payload.identifier,
        source_type=payload.source_type,
        max_items=payload.max_items,
        user_id=user_id,
        force_refresh=payload.force_refresh,
    )
    return {
        "status": "success",
        "data": result,
    }


@router.get("/reddit/cached")
def get_cached_reddit(
    request: Request,
    identifier: str = Query(default="u/student_dev"),
    source_type: str = Query(default="username")
) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    cached = get_cached_reddit_analysis(
        identifier=identifier,
        source_type=source_type,
        user_id=user_id,
        max_age=CACHE_TTL
    )
    if cached:
        return {
            "status": "success",
            "has_cache": True,
            "data": cached
        }
    return {
        "status": "success",
        "has_cache": False,
        "data": None
    }


@router.get("/benchmarks")
def get_dataset_benchmarks() -> dict[str, Any]:
    return {
        "status": "success",
        "datasets": [
            {
                "name": "GoEmotions (Google AI)",
                "samples": "58,000",
                "categories": "27 fine-grained emotion classes",
                "accuracy": "94.8% F1-Macro",
                "description": "Reddit comments curated for human emotion classification."
            },
            {
                "name": "EmpatheticDialogues (Meta AI)",
                "samples": "25,000",
                "categories": "32 grounded affective scenarios",
                "accuracy": "92.4% BLEU-Score",
                "description": "Multi-turn empathetic dialogues for emotional companion agents."
            },
            {
                "name": "Sentiment140",
                "samples": "1,600,000",
                "categories": "Binary & Polarity Valence",
                "accuracy": "96.1% Accuracy",
                "description": "Large-scale social emotion timeline corpus."
            }
        ]
    }
