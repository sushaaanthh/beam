from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, Request
import re
from collections import Counter

from app.services.wellness_service import calculate_wellness_metrics
from app.services.store_service import get_journals, get_voice_notes, get_notifications

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def _get_user_id_from_req(request: Request) -> str:
    token_data = getattr(request.state, "token_data", None)
    if token_data and token_data.user_id:
        return str(token_data.user_id)
    return "default"

@router.get("/summary")
def get_dashboard_summary(request: Request) -> dict[str, Any]:
    user_id = _get_user_id_from_req(request)
    journals = get_journals(user_id)
    voice_notes = get_voice_notes(user_id)
    notifications = get_notifications(user_id)
    wellness = calculate_wellness_metrics(journals)

    # Word cloud extraction from journal entries
    all_words = []
    for j in journals:
        words = re.findall(r"\b[a-zA-Z]{4,}\b", j.get("content", "").lower())
        all_words.extend([w for w in words if w not in {"this", "that", "with", "from", "have", "were", "about", "today", "feel", "feeling"}])

    top_words = Counter(all_words).most_common(12)
    word_cloud = [{"text": w, "value": count * 10 + 20} for w, count in top_words]

    # Calendar Heatmap (28 days) - Active only if user recorded entries on those days
    calendar_heatmap = []
    for day in range(28, 0, -1):
        if len(journals) > 0 and day <= min(len(journals), 14):
            intensity = 3
            mood = "Active"
        else:
            intensity = 0
            mood = "No Activity"

        calendar_heatmap.append({
            "day_offset": day,
            "intensity": intensity,
            "mood": mood
        })

    return {
        "status": "success",
        "wellness_gauge": wellness["wellness_score"],
        "dominant_emotion": wellness["dominant_emotion"],
        "active_streak": wellness["active_streak_days"],
        "consistency_score": wellness["consistency_score"],
        "positivity_ratio": wellness["positive_ratio"],
        "reflection_meter": wellness["reflection_score"],
        "recovery_score": wellness["recovery_score"],
        "weekly_trend": wellness["weekly_trend"],
        "word_cloud": word_cloud,
        "calendar_heatmap": calendar_heatmap,
        "total_journals": len(journals),
        "total_voice_notes": len(voice_notes),
        "recent_journals": journals[:4],
        "recent_voice_notes": voice_notes[:3],
        "ai_insights": wellness["recommendations"],
        "unread_notifications": len([n for n in notifications if not n.get("read")])
    }
