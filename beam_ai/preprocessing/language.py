"""Language detection with graceful degradation.

Strategy (documented per the brief):

* `mode="off"`          -> language is recorded as 'unknown'; nothing filtered.
* `mode="allowlist"`    -> if `langdetect` is installed, detect and keep only
  configured languages (default: en). Unsupported languages are filtered
  WITH a recorded reason ('language:<code>') - never silently discarded.
  If langdetect is NOT installed, allowlist mode degrades to 'off' and this
  degradation is reported in the quality report.

langdetect is probabilistic; its seed is fixed for determinism.
"""

from __future__ import annotations

from dataclasses import dataclass

from beam_ai.configs.pipeline_settings import PipelineSettings

try:  # optional dependency - pipeline works without it
    from langdetect import DetectorFactory, detect as _detect

    DetectorFactory.seed = 0  # deterministic detection
    LANGDETECT_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on environment
    LANGDETECT_AVAILABLE = False


@dataclass(frozen=True, slots=True)
class LanguageDecision:
    language: str       # detected code, configured value, or 'unknown'
    kept: bool
    reason: str | None


class LanguageFilter:
    def __init__(self, settings: PipelineSettings) -> None:
        self.mode = settings.language_mode
        self.allowlist = set(settings.resolved_languages())
        self.available = LANGDETECT_AVAILABLE
        if self.mode == "allowlist" and not self.available:
            # Documented degradation instead of silent behavior.
            self.mode = "off"
            self.degraded = True
        else:
            self.degraded = False

    def evaluate(self, text: str) -> LanguageDecision:
        if self.mode == "off" or not text:
            return LanguageDecision("unknown", True, None)

        try:
            detected = (_detect(text[:1000]) or "unknown").lower()
        except Exception:
            # langdetect raises LangDetectException on e.g. digit-only text.
            return LanguageDecision("unknown", True, None)

        if detected in self.allowlist:
            return LanguageDecision(detected, True, None)
        return LanguageDecision(detected, False, f"language:{detected}")
