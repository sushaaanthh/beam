"""Deterministic text cleaning.

Design principles (documented per the research brief):

* Meaningful linguistic signal is PRESERVED. Punctuation (repeated runs are
  collapsed but not removed), emojis, negations and capitalization are kept
  because future emotion models may rely on them. Only genuinely
  information-free surface noise is removed:
    - HTML tags/entities
    - URLs (replaced with a ` URL ` placeholder; count is kept as a feature)
    - Reddit markdown (quote markers, bold/italic/links, code backticks,
      strikethrough, spoiler tags, zero-width characters)
    - escaped characters and control characters
    - collapsed whitespace
* The function is pure: same input -> same output, no locale or randomness.
"""

from __future__ import annotations

import html
import re

URL_PLACEHOLDER = " URL "

# Order matters: each pattern assumes the previous ones already applied.
_REDDIT_LINK = re.compile(r"\[([^\]]*)\]\((?:/u/|/r/|https?://)[^)]*\)")
_MENTION = re.compile(r"(?<![\w])/?(?:u|r)/[A-Za-z0-9_-]{2,}\b")
_MD_BOLD_ASTERISK = re.compile(r"\*\*([^*\n]+)\*\*")
_MD_ITALIC_ASTERISK = re.compile(r"\*([^*\n]+)\*")
_MD_BOLD_UNDERSCORE = re.compile(r"(?<![\w])__([^_\n]+?)__(?![\w])")
_MD_ITALIC_UNDERSCORE = re.compile(r"(?<![\w])_([^_\n]+?)_(?![\w])")
_MD_STRIKE = re.compile(r"~~(.+?)~~")
_MD_SPOILER = re.compile(r">!(.+?)!<")
_MD_QUOTE = re.compile(r"(?m)^\s*>\s?")
_MD_CODE = re.compile(r"`([^`]*)`")
_HTML_TAG = re.compile(r"<[^>]+>")
_URL = re.compile(r"https?://\S+|www\.\S+")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u2060\uFEFF]")
_MULTI_SPACE = re.compile(r"[ \t\f\v]+")
_MULTI_NEWLINE = re.compile(r"\n{3,}")
_REPEATED_PUNCT = re.compile(r"([!?.,;:])\1{2,}")  # collapse 3+ repeats to one


def clean_text(raw: str | None) -> str:
    """Clean one text document deterministically. Never raises on text input."""
    if raw is None:
        return ""

    text = str(raw)

    # 1. Unicode escapes / HTML entities first so later regexes see plain text.
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = html.unescape(text)

    # 2. Zero-width + control characters.
    text = _ZERO_WIDTH.sub("", text)
    text = _CONTROL.sub(" ", text)

    # 3. URLs before markdown links so link targets do not leave fragments.
    text = _URL.sub(URL_PLACEHOLDER.strip(), text)

    # 4. Reddit markdown.
    text = _REDDIT_LINK.sub(r"\1", text)      # [label](target) -> label
    text = _MD_SPOILER.sub(r"\1", text)
    text = _MD_STRIKE.sub(r"\1", text)
    text = _MD_CODE.sub(r"\1", text)
    text = _MD_BOLD_ASTERISK.sub(r"\1", text)
    text = _MD_ITALIC_ASTERISK.sub(r"\1", text)
    text = _MD_BOLD_UNDERSCORE.sub(r"\1", text)
    text = _MD_ITALIC_UNDERSCORE.sub(r"\1", text)
    text = _MENTION.sub(" MENTION ", text)     # u/name, r/subreddit
    text = _MD_QUOTE.sub("", text)

    # 5. Stray HTML (after entity decoding).
    text = _HTML_TAG.sub(" ", text)

    # 6. Surface normalization that keeps signal:
    text = _REPEATED_PUNCT.sub(r"\1", text)   # "!!!" -> "!" (kept once)
    text = _MULTI_SPACE.sub(" ", text)
    text = _MULTI_NEWLINE.sub("\n\n", text)

    return text.strip()
