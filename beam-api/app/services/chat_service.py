from __future__ import annotations

import logging
from typing import Any
from app.services.emotion_service import analyze_emotion
from app.services.gemini_service import generate_chat_with_gemini

logger = logging.getLogger(__name__)

# Context-aware empathetic response strategies
RESPONSE_TEMPLATES = {
    "Pride / Accomplishment": [
        "That's a major milestone! Celebrating these wins builds strong psychological momentum. What part of the breakthrough felt most rewarding?",
        "Outstanding work! Finishing what you set out to do reinforces cognitive resilience. How are you planning to recharge?"
    ],
    "Joy / Fulfillment": [
        "It's uplifting to see this positive affective energy! What contributed most to your day turning out so well?",
        "Love this momentum. Anchoring these positive experiences helps maintain perspective during more demanding sprints."
    ],
    "Hope & Optimism": [
        "Having a forward-looking, optimistic outlook makes navigating uncertainty much smoother. What's the next key step on your radar?",
        "That anticipation is powerful. Trust the preparation you've put in and take it one milestone at a time."
    ],
    "Apprehension / Anxiety": [
        "It is completely natural to feel tension or nervous energy when something critical is on the line. What is one small, concrete step you can execute right now?",
        "I hear the anxiety in your message. Remember that stress is often an indicator of how deeply you care about the outcome. Let's break the challenge down together."
    ],
    "Overwhelmed / Burnout": [
        "Feeling overwhelmed is your cognitive system signaling that you need an intentional recharge. Can you take a 15-minute breather before tackling the next item?",
        "When tasks pile up, the most effective strategy is radical prioritization. What is the single highest-leverage task today, and what can safely wait?"
    ],
    "Sadness / Dejection": [
        "I'm sorry things felt heavy today. A temporary setback doesn't define your overall trajectory. Would you like to unpack what happened, or just take a moment to rest?",
        "It's okay to feel disappointed. Acknowledge the emotion without self-judgment. I'm here to listen."
    ],
    "Frustration / Friction": [
        "Friction and bottlenecks can be immensely draining. Stepping away for a short walk often provides the psychological distance needed to see a fresh angle.",
        "That frustration makes total sense given the obstacles you're encountering. Let's look at the bottleneck from a clean slate."
    ],
    "Curiosity & Focus": [
        "Diving deep into research and problem-solving is where true progress happens! What interesting pattern or insight caught your attention?",
        "Great to see you in a focused flow state! What hypothesis are you exploring right now?"
    ],
    "Neutral / Analytical": [
        "Reflecting methodically on your routine is a powerful habit. Is there anything specific on your mind you'd like to explore today?",
        "Understood. How is your energy holding up for the rest of your agenda?"
    ]
}

def generate_companion_reply(
    user_message: str, 
    history: list[dict[str, Any]], 
    recent_journals: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    # 1. Analyze emotion of the current user message with Gemini 3.1 Flash Lite
    emotion_data = analyze_emotion(user_message, model_name="Gemini 3.1 Flash Lite")
    primary_emotion = emotion_data["primary_emotion"]
    
    # 2. Try generating reply with Gemini 3.1 Flash Lite
    gemini_reply = generate_chat_with_gemini(
        user_message=user_message,
        recent_journals=recent_journals,
        past_messages=history
    )

    if gemini_reply:
        reply_text = gemini_reply
    else:
        # Contextual Memory from recent journals fallback
        memory_prefix = ""
        if recent_journals and len(recent_journals) > 0 and len(history) <= 2:
            latest_j = recent_journals[0]
            j_title = latest_j.get("title", "your recent entry")
            j_emotion = latest_j.get("primary_emotion", "")
            if "Anxiety" in j_emotion or "Stress" in j_emotion:
                memory_prefix = f"I remember in '{j_title}' you were navigating some pressure. "
            elif "Pride" in j_emotion or "Joy" in j_emotion:
                memory_prefix = f"Building on the win from '{j_title}', "

        templates = RESPONSE_TEMPLATES.get(primary_emotion, RESPONSE_TEMPLATES["Neutral / Analytical"])
        idx = (len(history) + len(user_message)) % len(templates)
        reply_text = memory_prefix + templates[idx]

    return {
        "reply": reply_text,
        "emotion_telemetry": {
            "detected_emotion": primary_emotion,
            "confidence": emotion_data["confidence"],
            "valence": emotion_data["valence"],
            "arousal": emotion_data["arousal"],
            "trigger_words": emotion_data["trigger_words"],
            "tokens": emotion_data["tokens"][:6]
        }
    }

def generate_daily_chat_summary(messages: list[dict[str, Any]]) -> dict[str, Any]:
    user_msgs = [m for m in messages if m.get("sender") == "user"]
    if not user_msgs:
        return {
            "summary": "No conversational exchanges recorded today.",
            "dominant_emotion": "Neutral",
            "interaction_count": 0
        }
    
    emotions = [m.get("detected_emotion", "Neutral") for m in user_msgs]
    from collections import Counter
    dominant = Counter(emotions).most_common(1)[0][0]

    return {
        "summary": f"Today's conversational exchanges centered primarily around {dominant.lower()} with steady communicative momentum across {len(user_msgs)} interactions.",
        "dominant_emotion": dominant,
        "interaction_count": len(user_msgs),
        "emotion_trajectory": emotions
    }
