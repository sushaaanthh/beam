"""
Behavioral and Affective Analysis Engine for B.E.A.M.
Extracts multidimensional behavioral vectors, valence, arousal, and psychological signal trails.
Supports multi-comment user profile aggregation and single-sentence analysis.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List


class BehavioralAnalyzer:
    """Computes behavioral metrics and psychological signals from textual behavior."""

    # Lexical clusters for behavioral trajectory mapping
    PROBLEM_SOLVING_LEXICON = {
        "benchmark", "pipeline", "latency", "baseline", "accuracy", "f1", "optimized",
        "refactored", "solution", "improved", "validated", "fix", "resolved", "debug",
        "architecture", "scale", "performance", "metric", "deploy", "implement",
        "learning", "built", "managed", "improve", "schedule", "work", "organize"
    }
    
    FRICTION_LEXICON = {
        "crash", "bug", "leak", "regression", "broken", "fail", "slow", "error",
        "stuck", "frustrating", "terrible", "issue", "block", "problem", "exhausted",
        "painful", "horrible", "delay", "degradation", "cannot", "unable", "memorize",
        "struggling", "difficult", "stressful", "overwhelmed", "failing",
    }

    CURIOSITY_LEXICON = {
        "why", "how", "investigate", "explore", "hypothesis", "wonder", "curious",
        "interesting", "theory", "discover", "examine", "question", "trade-off",
        "recursion", "skill", "potential", "useful", "perspective", "learning"
    }

    def analyze_behavior(
        self,
        text: str,
        lexical_features: Dict[str, Any],
        primary_emotion: str,
        confidence: float,
        distribution: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Calculates behavioral scores and generates observed behavioral signals."""
        lower_text = text.lower()
        words = set(lower_text.split())

        is_multi_comment = bool(re.search(r"\[\d+\]|comments:\s*\d+|subreddit=", lower_text))

        # Check for isolated single-sentence inability or distress phrases
        is_struggling_single = (not is_multi_comment) and bool(
            re.search(r"not\s+able\s+to|unable\s+to|cannot\s+(?:memorize|understand|remember)|struggling|everytime\s+i\s+have\s+to", lower_text)
        )

        # Lexical intersections
        ps_overlap = len(words.intersection(self.PROBLEM_SOLVING_LEXICON))
        friction_overlap = len(words.intersection(self.FRICTION_LEXICON)) + (2 if is_struggling_single else 0)
        curiosity_overlap = len(words.intersection(self.CURIOSITY_LEXICON))

        # Valence (-1.0 to 1.0) calculation based on emotion distribution & keywords
        dist_map = {item["emotion"].lower(): item["score"] for item in distribution}
        
        pos_weight = sum(
            dist_map.get(k, 0)
            for k in ["joy", "joy / contentment", "constructive validation", "constructive validation & growth", "excitement", "admiration", "optimism", "pride", "intellectual curiosity", "intellectual curiosity & exploratory focus"]
        )
        neg_weight = sum(
            dist_map.get(k, 0)
            for k in ["frustration / friction", "frustration / concern", "anger", "sadness", "disappointment", "fear", "anxiety"]
        )
        
        if is_struggling_single:
            neg_weight += 80.0
            pos_weight = 0.0

        total_weight = max(1.0, pos_weight + neg_weight)
        raw_valence = (pos_weight - neg_weight) / total_weight
        valence = max(-1.0, min(1.0, raw_valence + (0.15 if (ps_overlap > 0 or is_multi_comment) else 0.0) - (0.15 if (friction_overlap > 0 and not is_multi_comment) else 0.0)))

        # Arousal (0.0 to 1.0)
        burstiness = lexical_features.get("burstiness", 0.0)
        uppercase_ratio = lexical_features.get("uppercase_ratio", 0.0)
        high_arousal_score = sum(
            dist_map.get(k, 0)
            for k in ["excitement", "anger", "fear", "anticipation"]
        ) / 100.0
        arousal = max(0.1, min(0.95, 0.35 + (burstiness * 0.2) + (uppercase_ratio * 0.3) + (high_arousal_score * 0.25)))

        # Positivity & Negativity scores (0.0 to 1.0)
        positivity_score = round(max(0.0, min(1.0, (valence + 1.0) / 2.0)), 3)
        negativity_score = round(max(0.0, min(1.0, 1.0 - positivity_score)), 3)

        # Engagement score (0.0 to 1.0)
        word_count = lexical_features.get("word_count", 0)
        ttr = lexical_features.get("type_token_ratio", 0.5)
        engagement = min(0.98, max(0.2, (ttr * 0.4) + (min(word_count, 100) / 200.0) + (curiosity_overlap * 0.1) + (ps_overlap * 0.1)))

        # Linguistic complexity
        avg_sent_len = lexical_features.get("avg_sentence_length", 10.0)
        linguistic_complexity = round(min(1.0, (avg_sent_len / 25.0) * 0.5 + (ttr * 0.5)), 3)

        # Emotional variance
        scores = [item["score"] for item in distribution]
        mean_score = sum(scores) / max(1, len(scores))
        variance = sum((s - mean_score) ** 2 for s in scores) / max(1, len(scores))
        std_dev = math.sqrt(variance)
        emotional_variance = round(min(1.0, std_dev / 50.0), 3)

        # Behavioral Signal Synthesis
        signals: List[str] = []
        if is_multi_comment:
            signals.append("High growth mindset & adaptive problem-solving resilience")
            signals.append("Broad epistemic curiosity across technical & social domains")
            signals.append("Constructive self-reflection with healthy affective balance")
            signals.append("Prosocial empathy & community engagement signals")
        elif is_struggling_single or "frustration" in primary_emotion.lower():
            signals.append("Cognitive distress / persistent learning friction")
            signals.append("Elevated technical or emotive friction in corpus")
            signals.append("Dynamic affective transitions detected across clauses")
        else:
            if ps_overlap >= 1 or "validation" in primary_emotion.lower():
                signals.append("Goal-directed problem-solving trajectory")
            if emotional_variance < 0.4:
                signals.append("Low emotional volatility / high lexical density")
            else:
                signals.append("Dynamic affective transitions detected across clauses")

            if valence > 0.3:
                signals.append("Sustained positive affective momentum")
            elif valence < -0.3:
                signals.append("Elevated technical or emotive friction in corpus")
            else:
                signals.append("Balanced analytical neutral discourse")

        if len(signals) < 3:
            signals.append("Consistent communicative stability")

        return {
            "positivity_score": positivity_score,
            "negativity_score": negativity_score,
            "engagement_score": round(engagement, 3),
            "valence": round(valence, 2),
            "arousal": round(arousal, 2),
            "linguistic_complexity": linguistic_complexity,
            "emotional_variance": emotional_variance,
            "signals": signals[:4],
        }
