from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.services.chat_service import generate_companion_reply, generate_daily_chat_summary
from app.services.store_service import add_chat_pair, clear_chat_history, get_chat_history, get_journals

router = APIRouter(prefix="/chat", tags=["chat"])

def _get_user_id_from_req(request: Request) -> str:
    token_data = getattr(request.state, "token_data", None)
    if token_data and token_data.user_id:
        return str(token_data.user_id)
    return "default"

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)

@router.post("")
@router.post("/message")
def send_chat_message(payload: ChatMessageRequest, request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    history = get_chat_history(user_id=user_id)
    recent_journals = get_journals(user_id=user_id)
    
    companion_output = generate_companion_reply(payload.message, history, recent_journals=recent_journals)
    
    now_iso = datetime.utcnow().isoformat() + "Z"
    
    user_entry = {
        "id": f"MSG-{uuid.uuid4().hex[:6].upper()}",
        "sender": "user",
        "message": payload.message,
        "detected_emotion": companion_output["emotion_telemetry"]["detected_emotion"],
        "confidence": companion_output["emotion_telemetry"]["confidence"],
        "valence": companion_output["emotion_telemetry"]["valence"],
        "trigger_words": companion_output["emotion_telemetry"]["trigger_words"],
        "tokens": companion_output["emotion_telemetry"].get("tokens", []),
        "created_at": now_iso
    }
    
    companion_entry = {
        "id": f"MSG-{uuid.uuid4().hex[:6].upper()}",
        "sender": "companion",
        "message": companion_output["reply"],
        "detected_emotion": "Empathetic Support",
        "confidence": 96.0,
        "created_at": now_iso
    }
    
    add_chat_pair(user_entry, companion_entry, user_id=user_id)
    
    return {
        "status": "success",
        "reply": companion_output["reply"],
        "telemetry": companion_output["emotion_telemetry"],
        "history": get_chat_history(user_id=user_id)
    }

@router.get("/summary")
def get_chat_daily_summary(request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    history = get_chat_history(user_id=user_id)
    summary_data = generate_daily_chat_summary(history)
    return {
        "status": "success",
        "data": summary_data
    }

@router.get("/history")
def fetch_chat_history(request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    return {
        "status": "success",
        "data": get_chat_history(user_id=user_id)
    }

@router.delete("/clear")
def clear_chat(request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    clear_chat_history(user_id=user_id)
    return {
        "status": "success",
        "message": "Chat conversation cleared"
    }
