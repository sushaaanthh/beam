"""Text cleaning + normalization tests (deterministic, signal-preserving)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from beam_ai.preprocessing.normalization import normalize_text, shingles, word_tokens
from beam_ai.preprocessing.text_cleaning import clean_text


class TestCleaning:
    def test_html_tags_and_entities_removed(self) -> None:
        cleaned = clean_text("<p>I&#39;m &#8220;happy&#8221; today!</p>")
        assert cleaned == "I'm “happy” today!"

    def test_urls_replaced_with_placeholder(self) -> None:
        cleaned = clean_text("look at https://example.com/x?a=1 please")
        assert "https://" not in cleaned
        assert "URL" in cleaned
        assert "look at" in cleaned and "please" in cleaned

    def test_reddit_markdown_stripped_but_words_kept(self) -> None:
        cleaned = clean_text("**Really** *great* ~~bad~~ >!hidden joy!</> and `code`")
        for word in ("Really", "great", "bad", "joy", "code"):
            assert word in cleaned
        for marker in ("**", "~~", ">!", "`"):
            assert marker not in cleaned

    def test_reddit_link_keeps_label_drops_target(self) -> None:
        cleaned = clean_text("see [this guide](https://reddit.com/r/help) now")
        assert "guide" in cleaned
        assert "reddit.com/r/help" not in cleaned

    def test_mentions_replaced_with_token(self) -> None:
        cleaned = clean_text("thanks u/helper and r/AskReddit folks")
        assert "helper" not in cleaned.split()
        assert "MENTION" in cleaned

    def test_repeated_punctuation_collapsed_not_deleted(self) -> None:
        assert clean_text("wow!!!! really???") == "wow! really?"

    def test_whitespace_and_escapes_normalized(self) -> None:
        cleaned = clean_text("line one\n\n\n\nline   two\t\tthree\\n")
        assert "\n\n" in cleaned
        assert "   " not in cleaned

    def test_special_char_preserved(self) -> None:
        assert "@" in clean_text("feeling good today @")

    def test_negation_and_capitalization_preserved(self) -> None:
        assert "NOT" in clean_text("I am NOT okay")
        assert "Okay" in clean_text("I am Okay")

    def test_empty_and_none_inputs(self) -> None:
        assert clean_text(None) == ""
        assert clean_text("") == ""

    def test_deterministic(self) -> None:
        sample = "**Hey** u/user check https://x.co @\n\n\nwow!!!"
        assert clean_text(sample) == clean_text(sample)


class TestNormalization:
    def test_lowercase_contractions_expanded_whitespace_collapsed(self) -> None:
        normalized = normalize_text("I  CAN'T believe it's   done!")
        assert normalized == "i can not believe it is done!"

    def test_original_views_all_stored_conceptually(self) -> None:
        raw = "**So** happy!!! @"
        cleaned = clean_text(raw)
        normalized = normalize_text(cleaned)
        # Raw preserved by caller; cleaned keeps emphasis words; normalized is canonical.
        assert cleaned == "So happy! @"
        assert normalized == "so happy! @"

    def test_word_tokens_simple(self) -> None:
        assert word_tokens("it's 2 o'clock-ish") == ["it's", "2", "o'clock", "ish"]

    def test_shingles_shape(self) -> None:
        result = shingles("the quick brown fox jumps")
        assert ("the", "quick", "brown") in result
        assert len(result) == 3
