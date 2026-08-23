"""Pipeline configuration (Pydantic Settings).

Every threshold used anywhere in the pipeline lives here - no magic
numbers inside the processing code. All values can be overridden by
environment variables (prefix BEAM_AI_) or CLI flags.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BEAM_AI_",
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Quality filters ------------------------------------------------------
    # Defaults chosen for short-form social text: Reddit comments are often
    # very short yet emotionally expressive ("so happy for you"), so floors
    # are deliberately low. Tune via config, not code.
    min_chars: int = Field(default=10, ge=1)
    max_chars: int = Field(default=8000, ge=1)
    min_words: int = Field(default=3, ge=0)
    keep_deleted: bool = False  # removed/deleted bodies are dropped by default

    # --- Deduplication ----------------------------------------------------------
    # exact: normalized_text equality.
    # near : word-3-gram Jaccard similarity >= threshold within the same
    #        subreddit. 0.9 keeps legitimately similar discussions separate;
    #        lower it only if you accept losing near-identical variants.
    dedupe_enabled: bool = True
    near_duplicate_threshold: float = Field(default=0.9, ge=0.0, le=1.0)

    # --- Language -----------------------------------------------------------------
    # mode:
    #   off      -> no language detection (language recorded as 'unknown')
    #   allowlist-> detect language when langdetect is installed and keep only
    #               `languages`; others are filtered WITH a recorded reason.
    # If langdetect is not installed, allowlist mode degrades to 'off' and the
    # quality report says so - nothing is silently discarded.
    language_mode: str = Field(default="allowlist", pattern="^(off|allowlist)$")
    languages: str = "en"  # comma-separated allowlist

    # --- Split ----------------------------------------------------------------------
    train_ratio: float = Field(default=0.70, gt=0, lt=1)
    validation_ratio: float = Field(default=0.15, ge=0, lt=1)
    test_ratio: float = Field(default=0.15, ge=0, lt=1)
    random_seed: int = Field(default=42)

    # --- Identity ---------------------------------------------------------------------
    dataset_version: str = "v001"
    namespace_uuid: str = "6f6f6e6b-beam-beam-beam-beam00000000"

    def resolved_languages(self) -> list[str]:
        return [lang.strip().lower() for lang in self.languages.split(",") if lang.strip()]

    def validate_ratios(self) -> None:
        total = self.train_ratio + self.validation_ratio + self.test_ratio
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"train+validation+test ratios must sum to 1.0 (got {total:.6f})"
            )


@lru_cache
def get_pipeline_settings() -> PipelineSettings:
    return PipelineSettings()
