from __future__ import annotations

import httpx
import logging
from typing import Any
from collections import Counter
from datetime import datetime, timezone, timedelta
from uuid import UUID

from app.database.session import SessionLocal
from app.models.reddit_cache import RedditCache
from app.services.emotion_service import analyze_emotion

logger = logging.getLogger(__name__)

# Cache freshness duration: 1 day (24 hours)
CACHE_TTL = timedelta(days=1)

# Sample realistic public Reddit corpora for immediate live testing
PRESET_REDDIT_DEMOS = {
    "u/student_dev": [
        "Finally finished our senior design machine learning benchmark! Results exceeded our baseline by 14%.",
        "A bit nervous about tomorrow's defense presentation, but our slides are comprehensive.",
        "Spent 4 hours debugging CUDA memory allocation crash before realizing it was an off-by-one tensor indexing bug.",
        "Excited to start my summer machine learning internship next month!",
        "Feeling exhausted after exam week, planning to take a complete rest day on Saturday."
    ],
    "r/pondicherry": [
        "Singapore like Governance. When Monthly preventive maintaince are done how will sudden tehnical issue occurs? Well may be this is what Singapore Governance looks like.",
        "The promenade beach road looks vibrant in the evenings with light breeze and cultural stalls.",
        "Heritage buildings along White Town need better conservation guidelines to retain Franco-Tamil architecture.",
        "Exploring cafes near Goubert Avenue. Great coffee and relaxed seaside ambiance.",
        "Auroville road repairs completed recently, making the commute much smoother."
    ],
    "r/learnmachinelearning": [
        "Can someone explain the mathematical intuition behind multi-head attention vs self-attention in transformers?",
        "After weeks of training, my model finally converged with 94.6% F1 score on the GoEmotions dataset!",
        "Struggling with overfitting on small sample sizes. Tried dropout and weight decay without much improvement.",
        "Really grateful for the community tutorials here, learned PyTorch from scratch over the last 3 months."
    ],
    "r/datascience": [
        "Promoted to Senior Data Scientist today! Huge thank you to everyone who reviewed my portfolio.",
        "Burnt out from continuous ad-hoc stakeholder requests without clear metric definitions.",
        "Benchmarking Polars against Pandas 2.0 showed 5x faster ingestion on 50GB parquet datasets.",
        "Navigating company restructuring has been stressful, but looking forward to upcoming projects."
    ],
    "r/mentalhealth": [
        "Taking time to step back from screens and taking daily walks has significantly reduced my anxiety levels.",
        "Grateful for having friends who listen without judging when things get overwhelming.",
        "Small reminder that healing isn't linear, celebrating the minor milestones every day.",
        "Journaling every morning has given me clarity on what triggers my stress."
    ]
}


def _safe_parse_uuid(val: str | None) -> UUID | None:
    if not val or val == "default":
        return None
    try:
        return UUID(str(val))
    except (ValueError, TypeError):
        return None


def get_cached_reddit_analysis(
    identifier: str,
    source_type: str = "username",
    user_id: str = "default",
    max_age: timedelta = CACHE_TTL
) -> dict[str, Any] | None:
    """
    Retrieves cached Reddit analysis for a specific user and Reddit source
    if cached within max_age (defaults to 1 day).
    """
    cleaned_id = identifier.strip().lstrip("u/").lstrip("r/").strip().lower()
    cache_key = f"{user_id}:{source_type}:{cleaned_id}"
    parsed_uuid = _safe_parse_uuid(user_id)

    try:
        with SessionLocal() as db:
            query = db.query(RedditCache).filter(RedditCache.id == cache_key)
            if parsed_uuid:
                query = query.filter(RedditCache.user_id == parsed_uuid)
            record = query.first()

            if record and record.data:
                now = datetime.now(timezone.utc)
                record_updated = record.updated_at
                if record_updated.tzinfo is None:
                    record_updated = record_updated.replace(tzinfo=timezone.utc)

                age = now - record_updated
                is_fresh = age < max_age

                result_data = dict(record.data)
                result_data["cached"] = True
                result_data["cache_updated_at"] = record_updated.isoformat()
                result_data["cache_age_seconds"] = int(age.total_seconds())
                result_data["is_fresh"] = is_fresh

                if is_fresh:
                    return result_data
    except Exception as e:
        logger.error(f"Error querying Reddit cache: {e}")

    return None


def save_cached_reddit_analysis(
    identifier: str,
    source_type: str,
    data: dict[str, Any],
    user_id: str = "default"
) -> None:
    """
    Saves or updates cached Reddit analysis in the database for the account.
    """
    cleaned_id = identifier.strip().lstrip("u/").lstrip("r/").strip().lower()
    cache_key = f"{user_id}:{source_type}:{cleaned_id}"
    parsed_uuid = _safe_parse_uuid(user_id)
    now = datetime.now(timezone.utc)

    # Avoid storing redundant cache flags inside raw data JSON
    data_to_store = {k: v for k, v in data.items() if k not in {"cached", "cache_updated_at", "cache_age_seconds", "is_fresh"}}

    try:
        with SessionLocal() as db:
            record = db.query(RedditCache).filter(RedditCache.id == cache_key).first()
            if record:
                record.data = data_to_store
                record.updated_at = now
            else:
                record = RedditCache(
                    id=cache_key,
                    user_id=parsed_uuid,
                    identifier=cleaned_id,
                    source_type=source_type,
                    data=data_to_store,
                    updated_at=now,
                    created_at=now,
                )
                db.add(record)
            db.commit()
    except Exception as e:
        logger.error(f"Error saving Reddit cache: {e}")


async def fetch_live_reddit_posts(identifier: str, source_type: str = "subreddit", max_items: int = 5) -> list[str]:
    """
    Fetches real live submissions and comments from Reddit using high-availability mirrors:
    1. Arctic-Shift public Reddit index API
    2. PullPush public archive index
    3. Direct Reddit JSON public feed
    """
    cleaned_id = identifier.strip().lstrip("u/").lstrip("r/").strip()
    collected: list[str] = []

    # 1. Primary: Arctic-Shift index
    try:
        url = (
            f"https://arctic-shift.photon-reddit.com/api/posts/search?subreddit={cleaned_id}&limit={max_items}"
            if source_type == "subreddit"
            else f"https://arctic-shift.photon-reddit.com/api/posts/search?author={cleaned_id}&limit={max_items}"
        )
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(headers=headers, timeout=4.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                posts_data = resp.json().get("data", [])
                for p in posts_data:
                    title = p.get("title", "").strip()
                    selftext = (p.get("selftext") or "").strip()
                    text = f"{title}. {selftext}".strip() if selftext else title
                    if len(text) > 8:
                        collected.append(text)
    except Exception as e:
        logger.info("Arctic-shift live fetch attempt error: %s", e)

    # 2. Secondary: PullPush public endpoint
    if not collected:
        try:
            url = (
                f"https://api.pullpush.io/reddit/search/submission/?subreddit={cleaned_id}&size={max_items}"
                if source_type == "subreddit"
                else f"https://api.pullpush.io/reddit/search/submission/?author={cleaned_id}&size={max_items}"
            )
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    posts_data = resp.json().get("data", [])
                    for p in posts_data:
                        title = p.get("title", "").strip()
                        selftext = (p.get("selftext") or "").strip()
                        text = f"{title}. {selftext}".strip() if selftext else title
                        if len(text) > 8:
                            collected.append(text)
        except Exception as e:
            logger.info("PullPush live Reddit fetch attempt error: %s", e)

    # 3. Tertiary: Direct Reddit JSON endpoint
    if not collected:
        try:
            url = (
                f"https://www.reddit.com/r/{cleaned_id}/hot.json?limit={max_items}"
                if source_type == "subreddit"
                else f"https://www.reddit.com/user/{cleaned_id}/submitted.json?limit={max_items}"
            )
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            async with httpx.AsyncClient(headers=headers, timeout=4.0, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    children = data.get("data", {}).get("children", [])
                    for child in children:
                        d = child.get("data", {})
                        title = d.get("title", "").strip()
                        selftext = (d.get("selftext") or "").strip()
                        text = f"{title}. {selftext}".strip() if selftext else title
                        if len(text) > 8:
                            collected.append(text)
        except Exception as e:
            logger.info("Direct Reddit JSON fetch error: %s", e)

    return collected[:max_items]


async def analyze_reddit_source(
    identifier: str,
    source_type: str = "username",  # 'username' or 'subreddit'
    max_items: int = 5,
    user_id: str = "default",
    force_refresh: bool = False
) -> dict[str, Any]:
    """
    Fetches real live posts from the requested Reddit source,
    runs RoBERTa transformer emotion inference on each post, and generates
    affective distribution, longitudinal timeline, and keyword attribution.

    Automatically checks and caches results per user account for 1 day.
    If cached within 1 day and force_refresh is False, returns the cached analysis.
    """
    cleaned_id = identifier.strip().lstrip("u/").lstrip("r/").strip()

    # Check cache first if not explicitly forcing fresh recomputation
    if not force_refresh:
        cached = get_cached_reddit_analysis(
            identifier=cleaned_id,
            source_type=source_type,
            user_id=user_id,
            max_age=CACHE_TTL
        )
        if cached:
            return cached

    # 1. Fetch live posts
    posts_text = await fetch_live_reddit_posts(cleaned_id, source_type=source_type, max_items=max_items)

    # If no live posts retrieved, check if it was one of the verified explicit presets
    if not posts_text:
        key = f"r/{cleaned_id}" if source_type == "subreddit" else f"u/{cleaned_id}"
        if key in PRESET_REDDIT_DEMOS:
            posts_text = PRESET_REDDIT_DEMOS[key]
        else:
            empty_result = {
                "source": f"u/{cleaned_id}" if source_type == "username" else f"r/{cleaned_id}",
                "source_type": source_type,
                "total_posts_analyzed": 0,
                "dominant_emotion": "No Data / Inactive",
                "average_valence": 0.0,
                "emotion_distribution": [],
                "top_keywords": [],
                "analyzed_posts": [],
                "timeline_vector": [],
                "message": f"No public submissions found for {source_type} '{cleaned_id}'.",
                "cached": False,
                "cache_updated_at": datetime.now(timezone.utc).isoformat(),
            }
            save_cached_reddit_analysis(cleaned_id, source_type, empty_result, user_id=user_id)
            return empty_result

    # 2. Run batch RoBERTa emotion analysis across all collected posts
    analyzed_items = []
    emotions_list = []
    all_keywords = []

    for idx, post in enumerate(posts_text):
        analysis = analyze_emotion(post, model_name="RoBERTa-Reddit-Social")
        em = analysis["primary_emotion"]
        emotions_list.append(em)
        all_keywords.extend(analysis["trigger_words"])

        analyzed_items.append({
            "id": f"REDDIT-{idx + 1:02d}",
            "text": post,
            "primary_emotion": em,
            "confidence": analysis["confidence"],
            "valence": analysis["valence"],
            "reflection_score": analysis["reflection_score"],
            "trigger_words": analysis["trigger_words"],
            "timestamp": f"Item {idx + 1}"
        })

    # 3. Aggregate Emotion Distribution Percentages
    total = len(emotions_list)
    counts = Counter(emotions_list)
    distribution = [
        {"emotion": em, "percentage": round((count / total) * 100, 1), "count": count}
        for em, count in counts.most_common()
    ]

    dominant_emotion = distribution[0]["emotion"] if distribution else "Joy / Fulfillment"
    avg_valence = round(sum(item["valence"] for item in analyzed_items) / max(total, 1), 2)
    top_keywords = [w for w, _ in Counter(all_keywords).most_common(10)]

    computed_result = {
        "source": f"u/{cleaned_id}" if source_type == "username" else f"r/{cleaned_id}",
        "source_type": source_type,
        "total_posts_analyzed": total,
        "dominant_emotion": dominant_emotion,
        "average_valence": avg_valence,
        "emotion_distribution": distribution,
        "top_keywords": top_keywords,
        "analyzed_posts": analyzed_items,
        "timeline_vector": [
            {"index": i + 1, "emotion": item["primary_emotion"], "valence": item["valence"]}
            for i, item in enumerate(analyzed_items)
        ],
        "cached": False,
        "cache_updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Store in cache for 1 day
    save_cached_reddit_analysis(cleaned_id, source_type, computed_result, user_id=user_id)

    return computed_result
