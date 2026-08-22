"""
Social media NLP preprocessor for Twitter and Reddit text data.
Normalizes mentions, hashtags, URLs, emojis, Reddit markdown, and extracts chronological [Date, Time, Text] sequences.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import html
import re
import unicodedata
from typing import Any, Dict, List, Tuple


class TextPreprocessor:
    """Preprocesses raw social media text from Twitter and Reddit for transformer models."""

    # Regex patterns for social media text
    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
    TWITTER_USER_PATTERN = re.compile(r"@[\w_]+", re.IGNORECASE)
    REDDIT_USER_PATTERN = re.compile(r"u/[\w_-]+", re.IGNORECASE)
    REDDIT_SUB_PATTERN = re.compile(r"r/[\w_-]+", re.IGNORECASE)
    HASHTAG_PATTERN = re.compile(r"#(\w+)")
    MULTIPLE_SPACES = re.compile(r"\s+")
    REPEATED_CHARS = re.compile(r"(.)\1{2,}")
    REPEATED_PUNCT = re.compile(r"([!?.,;:]){2,}")
    REDDIT_MARKDOWN = re.compile(r"(\*{1,3}|_{1,3}|~{2}|`{1,3}|>|#+)")

    # Common date and timestamp patterns
    DATE_TIME_PATTERNS = [
        # 2026-08-15 14:30 or 2026/08/15 14:30:00
        re.compile(r"(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}(?:[T\s]\d{1,2}:\d{2}(?::\d{2})?)?)", re.IGNORECASE),
        # Aug 15, 2026 2:30 PM or 15 Aug 2026
        re.compile(r"([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)?)", re.IGNORECASE),
        # [01] or [02] index headers
        re.compile(r"\[(\d{1,3})\]", re.IGNORECASE),
    ]

    EMOJI_MAP = {
        "❤️": " love ", "💖": " love ", "😍": " adoration ", "🥰": " affection ",
        "😊": " happiness ", "😃": " joy ", "😄": " joy ", "😁": " delight ",
        "🔥": " excitement ", "🚀": " ambition ", "🎉": " celebration ", "✨": " inspiration ",
        "😢": " sadness ", "😭": " grief ", "😞": " disappointment ", "😔": " regret ",
        "😡": " anger ", "🤬": " rage ", "😤": " frustration ", "😠": " annoyance ",
        "🤔": " curiosity ", "🧐": " contemplation ", "💡": " insight ", "🤯": " astonishment ",
        "😱": " fear ", "😨": " anxiety ", "😰": " apprehension ", "😬": " nervous ",
        "👍": " approval ", "👎": " disapproval ", "👏": " praise ", "🙏": " gratitude ",
        "💯": " perfection ", "💀": " humor ", "😂": " amusement ", "🤣": " laughter ",
    }

    def __init__(self, preserve_social_tags: bool = True):
        self.preserve_social_tags = preserve_social_tags

    def clean_text(self, text: str) -> str:
        """Cleans and standardizes raw social media text."""
        if not text or not isinstance(text, str):
            return ""

        # Unescape HTML entities (common in Reddit/Twitter feeds)
        cleaned = html.unescape(text)
        cleaned = unicodedata.normalize("NFKC", cleaned)

        # Replace emojis with affective keywords
        for emoji_char, replacement in self.EMOJI_MAP.items():
            cleaned = cleaned.replace(emoji_char, replacement)

        # Replace URLs
        cleaned = self.URL_PATTERN.sub(" ", cleaned)

        # Normalize Twitter and Reddit mentions
        cleaned = self.TWITTER_USER_PATTERN.sub("@user", cleaned)
        cleaned = self.REDDIT_USER_PATTERN.sub("u/user", cleaned)
        cleaned = self.REDDIT_SUB_PATTERN.sub(r"\g<0>", cleaned)

        # Strip markdown syntax while keeping words
        cleaned = self.REDDIT_MARKDOWN.sub(" ", cleaned)

        # Unpack hashtags (e.g., #MachineLearning -> MachineLearning)
        cleaned = self.HASHTAG_PATTERN.sub(r"\1", cleaned)

        # Normalize repeated characters (e.g., "sooo goood" -> "soo good")
        cleaned = self.REPEATED_CHARS.sub(r"\1\1", cleaned)

        # Normalize repeated punctuation
        cleaned = self.REPEATED_PUNCT.sub(r"\1", cleaned)

        # Collapse whitespace
        cleaned = self.MULTIPLE_SPACES.sub(" ", cleaned).strip()

        return cleaned

    def clean_chronological_document(self, raw_document: str) -> str:
        """
        Cleans uploaded multi-entry documents, stripping noise/metadata and formatting strictly into
        chronological '[YYYY-MM-DD HH:MM] <Cleaned Text>' entries for behavioral trend analysis.
        """
        if not raw_document or not isinstance(raw_document, str):
            return ""

        lines = raw_document.strip().split("\n")
        structured_entries: List[str] = []
        base_date = datetime(2026, 8, 1, 9, 0)
        current_dt = base_date
        current_text_buf: List[str] = []

        entry_pattern = re.compile(
            r"(?:^|\n)(?:\[?(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}[^\]\n]*)\]?|\[(\d{1,3})\][^\n]*)",
            re.IGNORECASE
        )

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Ignore system headers like USER_ID:, PLATFORM:, COMMENTS:
            if re.match(r"^(USER_ID|PLATFORM|COMMENTS|METADATA|HEADER|AUTHOR):", line_str, re.IGNORECASE):
                continue

            # Check if this line starts a new dated entry
            date_match = re.search(r"(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})(?:[T\s](\d{1,2}:\d{2}))?", line_str)
            index_match = re.search(r"^\[(\d{1,3})\]", line_str)

            if date_match or index_match:
                # Flush previous entry
                if current_text_buf:
                    cleaned_body = self.clean_text(" ".join(current_text_buf))
                    # Remove trailing/leading junk or emotion hints
                    cleaned_body = re.sub(r"subreddit=\w+\s*\|\s*emotion_hint=\w+", "", cleaned_body, flags=re.IGNORECASE).strip()
                    if cleaned_body:
                        structured_entries.append(f"[{current_dt.strftime('%Y-%m-%d %H:%M')}] {cleaned_body}")
                    current_text_buf = []

                if date_match:
                    date_part = date_match.group(1).replace("/", "-").replace(".", "-")
                    time_part = date_match.group(2) if date_match.group(2) else "12:00"
                    try:
                        current_dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
                    except Exception:
                        current_dt += timedelta(days=1, hours=2)
                elif index_match:
                    idx = int(index_match.group(1))
                    current_dt = base_date + timedelta(days=idx // 2, hours=(idx % 12) * 2)

                # Strip entry metadata from line
                clean_line = re.sub(r"^\[.*?\]\s*", "", line_str)
                clean_line = re.sub(r"subreddit=\w+\s*\|\s*emotion_hint=\w+", "", clean_line, flags=re.IGNORECASE).strip()
                if clean_line:
                    current_text_buf.append(clean_line)
            else:
                current_text_buf.append(line_str)

        # Flush final entry
        if current_text_buf:
            cleaned_body = self.clean_text(" ".join(current_text_buf))
            cleaned_body = re.sub(r"subreddit=\w+\s*\|\s*emotion_hint=\w+", "", cleaned_body, flags=re.IGNORECASE).strip()
            if cleaned_body:
                structured_entries.append(f"[{current_dt.strftime('%Y-%m-%d %H:%M')}] {cleaned_body}")

        if structured_entries:
            return "\n\n".join(structured_entries)
        
        # Fallback if no dates detected
        return self.clean_text(raw_document)

    def extract_lexical_features(self, text: str) -> Dict[str, Any]:
        """Extracts behavioral and linguistic statistics from text."""
        words = re.findall(r"\b\w+\b", text)
        word_count = len(words)
        char_count = len(text)
        unique_words = set(w.lower() for w in words)
        type_token_ratio = len(unique_words) / word_count if word_count > 0 else 0.0

        # Punctuation burstiness (frequency of !, ?, ellipses)
        exclamation_count = text.count("!")
        question_count = text.count("?")
        burstiness = (exclamation_count * 1.5 + question_count) / max(1, word_count)

        # Capitalization density (shouting/intensity indicator)
        alpha_chars = [c for c in text if c.isalpha()]
        uppercase_ratio = sum(1 for c in alpha_chars if c.isupper()) / max(1, len(alpha_chars))

        # Sentence count estimation
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_len = word_count / max(1, len(sentences))

        return {
            "char_count": char_count,
            "word_count": word_count,
            "unique_word_count": len(unique_words),
            "type_token_ratio": round(type_token_ratio, 3),
            "burstiness": round(burstiness, 3),
            "uppercase_ratio": round(uppercase_ratio, 3),
            "sentence_count": len(sentences),
            "avg_sentence_length": round(avg_sentence_len, 2),
        }

    def tokenize_words(self, text: str) -> List[str]:
        """Splits text into tokens preserving punctuation boundaries for saliency mapping."""
        return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
