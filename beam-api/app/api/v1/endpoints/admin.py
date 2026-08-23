from __future__ import annotations

from typing import Any
from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
def get_admin_telemetry() -> dict[str, Any]:
    return {
        "status": "success",
        "total_users": 1420,
        "daily_analyses": 4846,
        "active_models": [
            {"name": "RoBERTa-v1.2 (Hedonic Emotion)", "status": "ONLINE", "avg_latency_ms": 14.8},
            {"name": "Whisper-Base (Speech STT)", "status": "ONLINE", "avg_latency_ms": 42.1},
            {"name": "SHAP Explainer Pipeline", "status": "ONLINE", "avg_latency_ms": 8.4}
        ],
        "api_throughput_rpm": 340,
        "error_rate_percentage": 0.02,
        "system_health": "OPTIMAL"
    }
