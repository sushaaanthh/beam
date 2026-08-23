from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

# In-memory stores isolated per user ID
_user_journals: dict[str, list[dict[str, Any]]] = {}
_user_voice_notes: dict[str, list[dict[str, Any]]] = {}
_user_chat_messages: dict[str, list[dict[str, Any]]] = {}
_user_notifications: dict[str, list[dict[str, Any]]] = {}

def get_journals(user_id: str = "default") -> list[dict[str, Any]]:
    return _user_journals.get(user_id, [])

def add_journal(entry: dict[str, Any], user_id: str = "default") -> dict[str, Any]:
    if "id" not in entry:
        entry["id"] = f"JRN-{uuid.uuid4().hex[:6].upper()}"
    if "created_at" not in entry:
        entry["created_at"] = datetime.utcnow().isoformat() + "Z"
    
    if user_id not in _user_journals:
        _user_journals[user_id] = []
    
    _user_journals[user_id].insert(0, entry)
    return entry

def delete_journal(journal_id: str, user_id: str = "default") -> bool:
    items = _user_journals.get(user_id, [])
    initial_len = len(items)
    _user_journals[user_id] = [j for j in items if j["id"] != journal_id]
    return len(_user_journals[user_id]) < initial_len

def get_voice_notes(user_id: str = "default") -> list[dict[str, Any]]:
    return _user_voice_notes.get(user_id, [])

def add_voice_note(note: dict[str, Any], user_id: str = "default") -> dict[str, Any]:
    if "id" not in note:
        note["id"] = f"VOX-{uuid.uuid4().hex[:6].upper()}"
    if "created_at" not in note:
        note["created_at"] = datetime.utcnow().isoformat() + "Z"
    
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
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    ])

def mark_notification_read(notif_id: str, user_id: str = "default") -> bool:
    notifs = _user_notifications.get(user_id, [])
    for n in notifs:
        if n["id"] == notif_id:
            n["read"] = True
            return True
    return False
