from __future__ import annotations

from typing import Any
from fastapi import APIRouter, File, Form, Request, UploadFile, status
from pydantic import BaseModel

from app.services.voice_service import process_voice_audio
from app.services.store_service import add_voice_note, get_voice_notes

router = APIRouter(prefix="/voice", tags=["voice"])

def _get_user_id_from_req(request: Request) -> str:
    token_data = getattr(request.state, "token_data", None)
    if token_data and token_data.user_id:
        return str(token_data.user_id)
    return "default"

@router.post("/transcribe")
async def transcribe_audio_chunk(
    file: UploadFile | None = File(None),
    transcript: str | None = Form(None)
) -> dict[str, Any]:
    """Lightweight direct audio speech-to-text for live journal dictation."""
    audio_bytes = b""
    filename = "dictation.wav"
    if file is not None:
        audio_bytes = await file.read()
        filename = file.filename or filename

    result = process_voice_audio(
        audio_bytes=audio_bytes,
        filename=filename,
        fallback_transcript=transcript
    )

    return {
        "status": "success",
        "transcript": result.get("transcript", "")
    }

@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_voice_audio(
    request: Request,
    file: UploadFile | None = File(None),
    transcript: str | None = Form(None)
) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    audio_bytes = b""
    filename = "voice_recording.wav"
    if file is not None:
        audio_bytes = await file.read()
        filename = file.filename or filename
    
    result = process_voice_audio(
        audio_bytes=audio_bytes,
        filename=filename,
        fallback_transcript=transcript
    )
    
    saved_note = add_voice_note(result, user_id=user_id)
    return {
        "status": "success",
        "message": "Voice audio transcribed and analyzed with Whisper + RoBERTa",
        "data": saved_note
    }

@router.get("/history")
def get_voice_history(request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    notes = get_voice_notes(user_id=user_id)
    return {
        "status": "success",
        "total": len(notes),
        "data": notes
    }
