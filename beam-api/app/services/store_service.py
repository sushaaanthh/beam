from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.database.session import SessionLocal
from app.models.journal import Journal

logger = logging.getLogger(__name__)

# Fallback in-memory stores for unauthenticated/demo sessions or if DB fails
_user_journals: dict[str, list[dict[str, Any]]] = {}
_user_voice_notes: dict[str, list[dict[str, Any]]] = {}
_user_chat_messages: dict[str, list[dict[str, Any]]] = {}
_user_notifications: dict[str, list[dict[str, Any]]] = {}


def _journal_model_to_dict(j: Journal) -> dict[str, Any]:
    created_at_str = (
        j.created_at.isoformat()
        if j.created_at
        else datetime.now(timezone.utc).isoformat()
    )
    if not created_at_str.endswith("Z") and "+" not in created_at_str:
        created_at_str += "Z"

    return {
        "id": j.id,
        "user_id": str(j.user_id) if j.user_id else None,
        "title": j.title,
        "content": j.content,
        "mood_emoji": j.mood_emoji or "",
        "primary_emotion": j.primary_emotion,
        "confidence": j.confidence,
        "valence": j.valence,
        "arousal": j.arousal,
        "reflection_score": j.reflection_score,
        "reflection_depth": j.reflection_depth,
        "emotional_clarity": j.emotional_clarity,
        "vocab_richness": j.vocab_richness,
        "ai_insight": j.ai_insight,
        "lifestyle_prescription": j.lifestyle_prescription,
        "tokens": j.tokens or [],
        "trigger_words": j.trigger_words or [],
        "distribution": j.distribution or [],
        "signals": j.signals or [],
        "latency_ms": j.latency_ms,
        "model_name": j.model_name,
        "created_at": created_at_str,
    }


def _safe_parse_uuid(val: str | None) -> UUID | None:
    if not val or val == "default":
        return None
    try:
        return UUID(str(val))
    except (ValueError, TypeError):
        return None


def get_journals(user_id: str = "default") -> list[dict[str, Any]]:
    parsed_uuid = _safe_parse_uuid(user_id)
    if parsed_uuid:
        try:
            with SessionLocal() as db:
                records = (
                    db.query(Journal)
                    .filter(Journal.user_id == parsed_uuid)
                    .order_by(Journal.created_at.desc())
                    .all()
                )
                return [_journal_model_to_dict(r) for r in records]
        except Exception as e:
            logger.error(f"Error reading journals from database for user {user_id}: {e}")

    # Fallback to in-memory store
    return _user_journals.get(user_id, [])


def add_journal(entry: dict[str, Any], user_id: str = "default") -> dict[str, Any]:
    if "id" not in entry or not entry["id"]:
        entry["id"] = f"JRN-{uuid.uuid4().hex[:6].upper()}"
    if "created_at" not in entry or not entry["created_at"]:
        entry["created_at"] = datetime.now(timezone.utc).isoformat()

    parsed_uuid = _safe_parse_uuid(user_id)
    if parsed_uuid:
        try:
            with SessionLocal() as db:
                journal_row = Journal(
                    id=entry["id"],
                    user_id=parsed_uuid,
                    title=entry.get("title") or "Daily Journal Entry",
                    content=entry.get("content") or "",
                    mood_emoji=entry.get("mood_emoji") or "",
                    primary_emotion=entry.get("primary_emotion") or "Neutral",
                    confidence=float(entry.get("confidence") or 0.0),
                    valence=float(entry.get("valence") or 0.0),
                    arousal=float(entry.get("arousal") or 0.0),
                    reflection_score=int(entry.get("reflection_score") or 80),
                    reflection_depth=entry.get("reflection_depth"),
                    emotional_clarity=entry.get("emotional_clarity"),
                    vocab_richness=entry.get("vocab_richness"),
                    ai_insight=entry.get("ai_insight"),
                    lifestyle_prescription=entry.get("lifestyle_prescription"),
                    tokens=entry.get("tokens") or [],
                    trigger_words=entry.get("trigger_words") or [],
                    distribution=entry.get("distribution") or [],
                    signals=entry.get("signals") or [],
                    latency_ms=entry.get("latency_ms"),
                    model_name=entry.get("model_name"),
                )
                db.add(journal_row)
                db.commit()
                db.refresh(journal_row)
                return _journal_model_to_dict(journal_row)
        except Exception as e:
            logger.error(f"Error persisting journal to database for user {user_id}: {e}")

    # Also keep in in-memory for fallback
    if user_id not in _user_journals:
        _user_journals[user_id] = []
    _user_journals[user_id].insert(0, entry)
    return entry


def delete_journal(journal_id: str, user_id: str = "default") -> bool:
    parsed_uuid = _safe_parse_uuid(user_id)
    deleted_db = False
    if parsed_uuid:
        try:
            with SessionLocal() as db:
                item = (
                    db.query(Journal)
                    .filter(Journal.id == journal_id, Journal.user_id == parsed_uuid)
                    .first()
                )
                if item:
                    db.delete(item)
                    db.commit()
                    deleted_db = True
        except Exception as e:
            logger.error(f"Error deleting journal from database: {e}")

    items = _user_journals.get(user_id, [])
    initial_len = len(items)
    _user_journals[user_id] = [j for j in items if j["id"] != journal_id]
    deleted_mem = len(_user_journals[user_id]) < initial_len

    return deleted_db or deleted_mem


def get_voice_notes(user_id: str = "default") -> list[dict[str, Any]]:
    return _user_voice_notes.get(user_id, [])


def add_voice_note(note: dict[str, Any], user_id: str = "default") -> dict[str, Any]:
    if "id" not in note:
        note["id"] = f"VOX-{uuid.uuid4().hex[:6].upper()}"
    if "created_at" not in note:
        note["created_at"] = datetime.now(timezone.utc).isoformat()

    if user_id not in _user_voice_notes:
        _user_voice_notes[user_id] = []

    _user_voice_notes[user_id].insert(0, note)
    return note


def get_chat_history(user_id: str = "default") -> list[dict[str, Any]]:
    return _user_chat_messages.get(user_id, [])


def add_chat_pair(user_entry: dict[str, Any], companion_entry: dict[str, Any], user_id: str = "default") -> None:
    if user_id not in _user_chat_messages:
        _user_chat_messages[user_id] = []
    _user_chat_messages[user_id].append(user_entry)
    _user_chat_messages[user_id].append(companion_entry)


def clear_chat_history(user_id: str = "default") -> None:
    _user_chat_messages[user_id] = []


def get_notifications(user_id: str = "default") -> list[dict[str, Any]]:
    return _user_notifications.get(user_id, [
        {
            "id": f"NOTIF-WELCOME-{user_id[:6]}",
            "title": "Welcome to BEAM AI",
            "message": "Your workspace is ready. Write your first reflection in Affective Studio to unlock your emotion timeline.",
            "type": "welcome",
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ])


def mark_notification_read(notif_id: str, user_id: str = "default") -> bool:
    notifs = _user_notifications.get(user_id, [])
    for n in notifs:
        if n["id"] == notif_id:
            n["read"] = True
            return True
    return False
