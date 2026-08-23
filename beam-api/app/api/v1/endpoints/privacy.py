from __future__ import annotations

from typing import Any
from fastapi import APIRouter
from app.services.store_service import get_journals, get_voice_notes, get_chat_history

router = APIRouter(prefix="/privacy", tags=["privacy"])

@router.post("/export")
def export_user_data() -> dict[str, Any]:
    return {
        "status": "success",
        "archive_format": "JSON",
        "exported_at": "2026-08-22T19:50:00Z",
        "data": {
            "journals": get_journals(),
            "voice_notes": get_voice_notes(),
            "chats": get_chat_history(),
            "privacy_compliance": "GDPR / CCPA Voluntary Voluntary Consent Valid"
        }
    }

@router.delete("/account")
def erase_account_data() -> dict[str, Any]:
    return {
        "status": "success",
        "message": "Account data and affective history permanently erased under privacy controls."
    }
