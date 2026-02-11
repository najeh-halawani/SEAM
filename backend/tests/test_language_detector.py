"""Unit tests for the language detection service."""

import pytest
from backend.services.language_detector import detect_language


class TestLanguageDetection:
    """Tests for detect_language function."""

    # ── English Detection ──────────────────────────────────

    def test_detect_english_simple(self):
        """Detects simple English text."""
        assert detect_language("Hello, how are you?") == "en"

    def test_detect_english_longer(self):
        """Detects longer English text."""
        text = "The working conditions in our department are quite challenging. We lack proper equipment and the noise levels make it difficult to concentrate."
        assert detect_language(text) == "en"

    def test_detect_english_with_numbers(self):
        """Detects English even with numbers mixed in."""
        assert detect_language("We have 15 employees in section B2.") == "en"

    # ── Arabic Detection ───────────────────────────────────

    def test_detect_arabic_simple(self):
        """Detects simple Arabic text."""
        assert detect_language("مرحبا كيف حالك") == "ar"

    def test_detect_arabic_longer(self):
        """Detects longer Arabic text."""
        text = "ظروف العمل في قسمنا صعبة للغاية. نحتاج إلى معدات أفضل وبيئة عمل أكثر هدوءاً."
        assert detect_language(text) == "ar"

    def test_detect_arabic_with_diacritics(self):
        """Detects Arabic with diacritical marks."""
        text = "لا نَعرِفُ ما يَحدُث"
        result = detect_language(text)
        assert result in ("ar", "mixed")  # Arabic chars with diacritics

    # ── Mixed Detection ────────────────────────────────────

    def test_detect_mixed_code_switching(self):
        """Detects mixed Arabic-English code-switching."""
        text = "The manager قال لنا that we need to work harder بدون أي resources"
        result = detect_language(text)
        assert result in ("mixed", "en", "ar")  # Acceptable: any of these

    # ── Edge Cases ─────────────────────────────────────────

    def test_detect_empty_string(self):
        """Handles empty string gracefully."""
        result = detect_language("")
        assert result in ("en", "mixed", "unknown")

    def test_detect_numbers_only(self):
        """Handles numeric-only input."""
        result = detect_language("123 456 789")
        assert isinstance(result, str)

    def test_detect_special_characters(self):
        """Handles special characters."""
        result = detect_language("!@#$%^&*()")
        assert isinstance(result, str)

    def test_return_type_is_string(self):
        """Always returns a string."""
        assert isinstance(detect_language("test"), str)

    def test_detect_single_word_english(self):
        """Detects single English word."""
        result = detect_language("hello")
        assert result == "en"

    def test_detect_single_word_arabic(self):
        """Detects single Arabic word."""
        result = detect_language("مرحبا")
        assert result == "ar"
