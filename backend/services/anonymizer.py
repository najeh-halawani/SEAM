"""Anonymization service using spaCy NER + rule-based redaction.

Preserves original text separately while producing a redacted version
with entity placeholders. Designed to protect participant identity
while preserving the meaning and structure of statements.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── Lazy-loaded spaCy model ───────────────────────────────────────────

_nlp = None


def _get_nlp():
    """Lazily load the spaCy model."""
    global _nlp
    if _nlp is None:
        import spacy
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model 'en_core_web_sm' not found. Downloading...")
            from spacy.cli import download
            download("en_core_web_sm")
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


# ── Rule-based patterns ──────────────────────────────────────────────

# Email addresses
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

# Phone numbers (international & local formats)
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s-]?)?"       # optional country code
    r"(?:\(?\d{1,4}\)?[\s-]?)?"     # optional area code
    r"\d{3,4}[\s-]?\d{3,4}"        # main number
)

# Common ID patterns (e.g., employee IDs, national IDs)
_ID_RE = re.compile(r"\b(?:ID|id|Id)[:\s#]?\s*\d{3,}\b")

# Arabic names patterns — common prefixes
_ARABIC_NAME_PREFIXES = re.compile(
    r"\b(السيد|السيدة|الأستاذ|الأستاذة|المهندس|المهندسة|الدكتور|الدكتورة|أبو|أم|بن|ابن|آل)\s+[\u0600-\u06FF]+"
)

# Specific location patterns in Arabic
_ARABIC_LOCATION_RE = re.compile(
    r"\b(شارع|منطقة|حي|مدينة|محافظة|قرية|بناية|مبنى|طابق)\s+[\u0600-\u06FF\s]+"
)


# ── Entity replacement map ───────────────────────────────────────────

NER_LABEL_MAP = {
    "PERSON": "[PERSON]",
    "ORG": "[ORGANIZATION]",
    "GPE": "[LOCATION]",
    "LOC": "[LOCATION]",
    "FAC": "[FACILITY]",
    "NORP": "[GROUP]",
}


def anonymize(text: str) -> str:
    """Anonymize a text string by replacing identifiable entities.

    Process order:
    1. Rule-based redaction (emails, phones, IDs) — most reliable
    2. Arabic-specific patterns
    3. spaCy NER for English entities

    Args:
        text: The raw text to anonymize.

    Returns:
        Anonymized text with entity placeholders.
    """
    if not text or not text.strip():
        return text

    result = text

    # 1) Rule-based: emails
    result = _EMAIL_RE.sub("[EMAIL]", result)

    # 2) Rule-based: phone numbers
    result = _PHONE_RE.sub("[PHONE]", result)

    # 3) Rule-based: ID numbers
    result = _ID_RE.sub("[ID]", result)

    # 4) Arabic name prefixes
    result = _ARABIC_NAME_PREFIXES.sub("[PERSON]", result)

    # 5) Arabic location patterns
    result = _ARABIC_LOCATION_RE.sub("[LOCATION]", result)

    # 6) spaCy NER for English entities
    try:
        nlp = _get_nlp()
        doc = nlp(result)
        # Process entities in reverse order to preserve character offsets
        entities = sorted(doc.ents, key=lambda e: e.start_char, reverse=True)
        for ent in entities:
            replacement = NER_LABEL_MAP.get(ent.label_)
            if replacement:
                result = result[:ent.start_char] + replacement + result[ent.end_char:]
    except Exception as e:
        logger.warning(f"spaCy NER failed, using rule-based only: {e}")

    # Clean up multiple consecutive placeholders of the same type
    result = re.sub(r"(\[(?:PERSON|ORGANIZATION|LOCATION|EMAIL|PHONE|ID|FACILITY|GROUP)\])\s*\1+", r"\1", result)

    return result


def anonymize_with_original(text: str) -> dict:
    """Anonymize text and return both versions.

    Returns:
        dict with 'original' and 'anonymized' keys.
    """
    return {
        "original": text,
        "anonymized": anonymize(text),
    }
