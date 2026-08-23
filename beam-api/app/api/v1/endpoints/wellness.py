from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.services.wellness_service import calculate_wellness_metrics
from app.services.store_service import get_journals
from app.services.emotion_service import analyze_emotion

router = APIRouter(prefix="/wellness", tags=["wellness"])

def _get_user_id_from_req(request: Request) -> str:
    token_data = getattr(request.state, "token_data", None)
    if token_data and token_data.user_id:
        return str(token_data.user_id)
    return "default"

class WellnessCheckInRequest(BaseModel):
    energy_level: int = Field(default=7, ge=1, le=10)
    stress_level: int = Field(default=4, ge=1, le=10)
    motivation_level: int = Field(default=8, ge=1, le=10)
    sleep_quality: int = Field(default=7, ge=1, le=10)
    free_text_reflection: str | None = None

_user_checkins: dict[str, list[dict[str, Any]]] = {}

@router.post("/check-in")
def submit_check_in(payload: WellnessCheckInRequest, request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    nlp_result = None
    if payload.free_text_reflection and payload.free_text_reflection.strip():
        nlp_result = analyze_emotion(payload.free_text_reflection, model_name="RoBERTa-Wellness")

    entry = {
        "energy": payload.energy_level,
        "stress": payload.stress_level,
        "motivation": payload.motivation_level,
        "sleep": payload.sleep_quality,
        "reflection_text": payload.free_text_reflection,
        "nlp_emotion": nlp_result.get("primary_emotion") if nlp_result else "Equilibrium",
        "timestamp": "2026-08-22T20:00:00Z"
    }
    
    if user_id not in _user_checkins:
        _user_checkins[user_id] = []
    _user_checkins[user_id].append(entry)
    
    journals = get_journals(user_id=user_id)
    metrics = calculate_wellness_metrics(journals, check_in_data=entry)
    
    return {
        "status": "success",
        "message": "Weekly check-in recorded successfully",
        "metrics": metrics
    }

@router.get("/score")
def get_wellness_score(request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    journals = get_journals(user_id=user_id)
    metrics = calculate_wellness_metrics(journals)
    return {
        "status": "success",
        "data": metrics
    }
