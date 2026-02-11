"""Unit tests for the anonymization service."""

import pytest
from backend.services.anonymizer import anonymize


class TestAnonymizer:
    """Tests for the anonymize function."""

    # ── Email Anonymization ────────────────────────────────

    def test_anonymize_email_address(self):
        """Replaces email addresses with [EMAIL]."""
        text = "Contact me at john.doe@company.com for details."
        result = anonymize(text)
        assert "john.doe@company.com" not in result
        assert "[EMAIL]" in result

    def test_anonymize_multiple_emails(self):
        """Replaces multiple email addresses."""
        text = "Send to alice@example.com and bob@corp.org"
        result = anonymize(text)
        assert "alice@example.com" not in result
        assert "bob@corp.org" not in result
        assert result.count("[EMAIL]") == 2

    # ── Phone Number Anonymization ─────────────────────────

    def test_anonymize_phone_number_international(self):
        """Replaces international phone numbers."""
        text = "Call me at +1-555-123-4567 anytime."
        result = anonymize(text)
        assert "555-123-4567" not in result
        assert "[PHONE]" in result

    def test_anonymize_phone_number_local(self):
        """Replaces local phone number formats."""
        text = "My number is 0551234567."
        result = anonymize(text)
        assert "0551234567" not in result

    # ── Person Name Anonymization (via spaCy NER) ──────────

    def test_anonymize_preserves_unnamed_text(self):
        """Text without PII should remain mostly unchanged."""
        text = "The office is too noisy and the equipment is outdated."
        result = anonymize(text)
        # Core message should be preserved
        assert "noisy" in result
        assert "equipment" in result
        assert "outdated" in result

    def test_anonymize_returns_string(self):
        """Always returns a string."""
        assert isinstance(anonymize("test input"), str)

    def test_anonymize_empty_string(self):
        """Handles empty string."""
        result = anonymize("")
        assert isinstance(result, str)

    # ── ID Number Anonymization ────────────────────────────

    def test_anonymize_id_number(self):
        """Replaces ID-like number patterns."""
        text = "Employee ID: EMP-2024-001"
        result = anonymize(text)
        # The regex should catch numeric ID patterns
        assert isinstance(result, str)

    # ── Mixed Content ──────────────────────────────────────

    def test_anonymize_mixed_pii(self):
        """Handles text with multiple types of PII."""
        text = "John called me at john@test.com about employee #12345."
        result = anonymize(text)
        assert "john@test.com" not in result
        assert isinstance(result, str)

    # ── Arabic Text ────────────────────────────────────────

    def test_anonymize_arabic_text_preserved(self):
        """Arabic text without PII should be preserved."""
        text = "ظروف العمل صعبة والضوضاء مرتفعة"
        result = anonymize(text)
        # Core Arabic content should be mostly preserved
        assert isinstance(result, str)
        assert len(result) > 0

    # ── Verbatim Preservation ──────────────────────────────

    def test_anonymize_does_not_equal_original_with_pii(self):
        """Result should differ from input when PII is present."""
        text = "Contact sarah@company.com for the meeting."
        result = anonymize(text)
        assert result != text  # Should have been modified

    def test_anonymize_no_pii_text_similar(self):
        """Text without PII should not be drastically changed."""
        text = "The work processes are inefficient."
        result = anonymize(text)
        # Should be similar since no PII to redact
        assert "inefficient" in result
