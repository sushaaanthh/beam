from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.services.emotion_service import analyze_emotion, analyze_live_emotion
from app.services.store_service import add_journal, get_journals, delete_journal

router = APIRouter(prefix="/journal", tags=["journal"])

def _get_user_id_from_req(request: Request) -> str:
    token_data = getattr(request.state, "token_data", None)
    if token_data and token_data.user_id:
        return str(token_data.user_id)
    return "default"

class LiveJournalRequest(BaseModel):
    text: str = Field(..., max_length=5000)

class JournalCreateRequest(BaseModel):
    title: str | None = Field(default="Daily Journal Entry")
    content: str = Field(..., min_length=2)
    mood_emoji: str | None = Field(default="")
    model_name: str | None = Field(default="RoBERTa-v1.2")

@router.post("/live")
def live_emotion_detection(payload: LiveJournalRequest) -> dict[str, Any]:
    """Debounced real-time keystroke emotion prediction while typing."""
    return analyze_live_emotion(payload.text)

@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/analyze", status_code=status.HTTP_201_CREATED)
def create_journal_entry(payload: JournalCreateRequest, request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    emotion_res = analyze_emotion(payload.content, model_name=payload.model_name or "RoBERTa-v1.2")
    
    entry = {
        "title": payload.title or "Daily Journal Entry",
        "content": payload.content,
        "mood_emoji": payload.mood_emoji or "",
        "primary_emotion": emotion_res["primary_emotion"],
        "confidence": emotion_res["confidence"],
        "valence": emotion_res["valence"],
        "arousal": emotion_res["arousal"],
        "reflection_score": emotion_res["reflection_score"],
        "reflection_depth": emotion_res["reflection_depth"],
        "emotional_clarity": emotion_res["emotional_clarity"],
        "vocab_richness": emotion_res["vocab_richness"],
        "ai_insight": emotion_res["ai_insight"],
        "lifestyle_prescription": emotion_res.get("lifestyle_prescription"),
        "tokens": emotion_res["tokens"],
        "trigger_words": emotion_res["trigger_words"],
        "distribution": emotion_res["distribution"],
        "signals": emotion_res["signals"],
        "latency_ms": emotion_res["latency_ms"],
        "model_name": emotion_res["model_name"]
    }
    
    saved = add_journal(entry, user_id=user_id)
    return {
        "status": "success",
        "message": "Journal analyzed and saved successfully",
        "data": saved
    }

@router.get("/trends")
def get_journal_trends(request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    items = get_journals(user_id=user_id)
    return {
        "status": "success",
        "total": len(items),
        "trends": [
            {
                "id": j["id"],
                "title": j["title"],
                "emotion": j["primary_emotion"],
                "valence": j["valence"],
                "reflection_score": j.get("reflection_score", 80),
                "created_at": j["created_at"]
            }
            for j in items
        ]
    }

@router.get("/history")
def get_journal_history(request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    items = get_journals(user_id=user_id)
    return {
        "status": "success",
        "total": len(items),
        "data": items
    }

@router.get("/{journal_id}")
def get_single_journal(journal_id: str, request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    for item in get_journals(user_id=user_id):
        if item["id"] == journal_id:
            return {"status": "success", "data": item}
    raise HTTPException(status_code=404, detail="Journal entry not found")

@router.delete("/{journal_id}")
def remove_journal_entry(journal_id: str, request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    deleted = delete_journal(journal_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"status": "success", "message": "Journal entry erased"}
