from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException

from app.services.store_service import get_notifications, mark_notification_read

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("")
def list_notifications() -> dict[str, Any]:
    notifs = get_notifications()
    return {
        "status": "success",
        "total": len(notifs),
        "data": notifs
    }

@router.put("/{notif_id}/read")
def read_notification(notif_id: str) -> dict[str, Any]:
    success = mark_notification_read(notif_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "success", "message": "Notification marked as read"}
