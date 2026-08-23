from __future__ import annotations

import json
import logging
from typing import Any
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

def analyze_emotion_with_gemini(text: str) -> dict[str, Any] | None:
    """
    Executes deep emotion, SHAP explainability, and lifestyle behavioral analysis
    using Google's Gemini 3.1 Flash Lite model.
    """
    api_key = settings.GEMINI_API_KEY
    model = settings.GEMINI_MODEL or "gemini-3.1-flash-lite"

    if not api_key:
        return None

    prompt = f"""
You are the BEAM AI Affective & Behavioral Emotion Intelligence engine.
Analyze the following daily journal/voice text:
"{text}"

Extract:
1. primary_emotion (e.g. "Cognitive Fatigue / Sedentary Load", "Pride / Accomplishment", "Joy / Fulfillment", "Apprehension / Anxiety", "Hope & Optimism", "Curiosity & Focus", "Overwhelmed / Burnout")
2. confidence (0.0 to 100.0)
3. valence (-1.0 to +1.0)
4. arousal (0.0 to 1.0)
5. reflection_score (0 to 100)
6. reflection_depth (0 to 100)
7. emotional_clarity (0 to 100)
8. vocab_richness (0 to 100)
9. ai_insight (actionable, empathetic 1-sentence observation)
10. trigger_words (list of up to 6 key emotional/behavioral words)
11. lifestyle_prescription:
    - title (e.g. "🏃 Physical Movement & Outdoor Exposure Needed")
    - prescription (what the behavioral analysis detected, e.g. extended indoor room duration)
    - recommended_action (actionable physical/mental advice, e.g. 20-30 min brisk walk or light stretching)
    - wellness_target (e.g. "Physical Exercise & Fresh Air")
    - urgency ("LOW", "MEDIUM", or "HIGH")
    - behavioral_tags (e.g. ["⏱️ Duration: 10 hrs", "🏠 Environment: Confined Indoors", "💻 Load: High Cognitive Work"])

Return strictly valid JSON matching this schema.
"""

    url = f"{GEMINI_API_URL}/{model}:generateContent?key={api_key}"
    
    try:
        with httpx.Client(timeout=12.0) as client:
            res = client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
            )
            if res.status_code == 200:
                data = res.json()
                raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(raw_json)
                parsed["model_name"] = f"Gemini 3.1 Flash Lite"
                return parsed
            else:
                logger.warning("Gemini API error %d: %s", res.status_code, res.text)
    except Exception as e:
        logger.warning("Gemini analysis call failed: %s", e)

    return None

def generate_chat_with_gemini(
    user_message: str,
    recent_journals: list[dict[str, Any]] | None = None,
    past_messages: list[dict[str, Any]] | None = None
) -> str | None:
    """Generates empathetic companion response using Gemini 3.1 Flash Lite."""
    api_key = settings.GEMINI_API_KEY
    model = settings.GEMINI_MODEL or "gemini-3.1-flash-lite"

    if not api_key:
        return None

    context_lines = []
    if recent_journals:
        latest = recent_journals[0]
        context_lines.append(f"User's Latest Journal: \"{latest.get('title', '')}\" - Emotion: {latest.get('primary_emotion', '')} (Content: {latest.get('content', '')[:100]})")

    context_str = "\n".join(context_lines)

    prompt = f"""
You are the BEAM AI Empathetic Companion, an expert mental wellness and behavioral support AI for students and working professionals.
You provide encouraging, insightful, science-backed guidance with emotional validation.

{context_str}

User says: "{user_message}"

Respond warmly, concisely (2-3 sentences), and offer a constructive reflection or physical/mental micro-action if appropriate.
"""

    url = f"{GEMINI_API_URL}/{model}:generateContent?key={api_key}"
    try:
        with httpx.Client(timeout=12.0) as client:
            res = client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}]
                }
            )
            if res.status_code == 200:
                data = res.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return reply
    except Exception as e:
        logger.warning("Gemini companion chat call failed: %s", e)

    return None
