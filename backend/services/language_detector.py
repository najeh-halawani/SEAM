"""Language detection for Arabic / English content.

Uses Unicode character ranges for fast Arabic detection with
langdetect as a fallback for ambiguous content.
"""

import re
from langdetect import detect, LangDetectException

# Unicode range covering Arabic script (basic + supplement + extended)
_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")


def detect_language(text: str) -> str:
    """Detect whether text is primarily Arabic or English.

    Returns:
        'ar' for Arabic, 'en' for English, 'mixed' if heavily mixed.
    """
    if not text or not text.strip():
        return "en"

    # Count Arabic vs Latin characters
    arabic_chars = len(_ARABIC_RE.findall(text))
    latin_chars = len(re.findall(r"[a-zA-Z]", text))
    total = arabic_chars + latin_chars

    if total == 0:
        return "en"

    arabic_ratio = arabic_chars / total

    if arabic_ratio > 0.6:
        return "ar"
    elif arabic_ratio < 0.2:
        return "en"
    else:
        # Ambiguous — use langdetect as fallback
        try:
            lang = detect(text)
            if lang == "ar":
                return "ar"
            return "en"
        except LangDetectException:
            return "mixed"


def is_arabic(text: str) -> bool:
    """Quick check if the text is primarily Arabic."""
    return detect_language(text) == "ar"


def is_rtl(text: str) -> bool:
    """Check if text should be rendered right-to-left."""
    return detect_language(text) in ("ar", "mixed")
