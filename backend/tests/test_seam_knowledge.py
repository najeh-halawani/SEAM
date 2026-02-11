"""Unit tests for SEAM knowledge base (categories and questions)."""

import pytest
from backend.seam.categories import (
    SEAM_CATEGORIES,
    CATEGORY_NAMES_EN,
    CATEGORY_NAMES_AR,
)
from backend.seam.questions import QUESTION_BANK, CATEGORY_ORDER


class TestSEAMCategories:
    """Tests for SEAM dysfunction category definitions."""

    def test_six_categories_defined(self):
        """Exactly 6 SEAM dysfunction categories exist."""
        assert len(SEAM_CATEGORIES) == 6

    def test_each_category_has_required_fields(self):
        """Each category has all required fields."""
        required_keys = {"key", "name_en", "name_ar", "description_en", "description_ar", "example_tags"}
        for cat in SEAM_CATEGORIES:
            assert required_keys.issubset(cat.keys()), f"Missing keys in {cat.get('key', 'unknown')}"

    def test_category_keys_unique(self):
        """All category keys are unique."""
        keys = [c["key"] for c in SEAM_CATEGORIES]
        assert len(keys) == len(set(keys))

    def test_english_names_lookup(self):
        """CATEGORY_NAMES_EN lookup works for all categories."""
        for cat in SEAM_CATEGORIES:
            assert cat["key"] in CATEGORY_NAMES_EN
            assert CATEGORY_NAMES_EN[cat["key"]] == cat["name_en"]

    def test_arabic_names_lookup(self):
        """CATEGORY_NAMES_AR lookup works for all categories."""
        for cat in SEAM_CATEGORIES:
            assert cat["key"] in CATEGORY_NAMES_AR
            assert CATEGORY_NAMES_AR[cat["key"]] == cat["name_ar"]

    def test_expected_categories_exist(self):
        """All expected SEAM categories are defined."""
        expected_keys = {
            "strategic_implementation",
            "working_conditions",
            "work_organization",
            "time_management",
            "communication_coordination_cooperation",
            "integrated_training",
        }
        actual_keys = {c["key"] for c in SEAM_CATEGORIES}
        assert expected_keys == actual_keys

    def test_each_category_has_tags(self):
        """Each category has at least one predefined tag."""
        for cat in SEAM_CATEGORIES:
            assert len(cat["example_tags"]) >= 1, f"No tags for {cat['key']}"

    def test_bilingual_descriptions(self):
        """Both English and Arabic descriptions are non-empty."""
        for cat in SEAM_CATEGORIES:
            assert len(cat["description_en"]) > 10, f"Short EN description for {cat['key']}"
            assert len(cat["description_ar"]) > 10, f"Short AR description for {cat['key']}"


class TestSEAMQuestions:
    """Tests for the SEAM question bank."""

    def test_questions_for_all_categories(self):
        """Question bank covers all 6 categories."""
        assert len(QUESTION_BANK) >= 6

    def test_category_order_matches(self):
        """CATEGORY_ORDER has exactly 6 entries matching category keys."""
        assert len(CATEGORY_ORDER) == 6
        for key in CATEGORY_ORDER:
            assert key in QUESTION_BANK, f"Missing questions for {key}"

    def test_each_category_has_opening_questions(self):
        """Each category has at least one opening question."""
        for key in CATEGORY_ORDER:
            questions = QUESTION_BANK[key]
            assert "opening" in questions, f"No opening questions for {key}"
            assert len(questions["opening"]) >= 1

    def test_each_category_has_probing_questions(self):
        """Each category has probing questions."""
        for key in CATEGORY_ORDER:
            questions = QUESTION_BANK[key]
            assert "probing" in questions, f"No probing questions for {key}"
            assert len(questions["probing"]) >= 1

    def test_questions_are_bilingual(self):
        """Questions have both English and Arabic versions."""
        for key in CATEGORY_ORDER:
            for qtype in ["opening", "probing"]:
                questions = QUESTION_BANK[key][qtype]
                for q in questions:
                    assert "en" in q, f"Missing EN for {key}/{qtype}"
                    assert "ar" in q, f"Missing AR for {key}/{qtype}"
                    assert len(q["en"]) > 5, f"Short EN question in {key}/{qtype}"
                    assert len(q["ar"]) > 5, f"Short AR question in {key}/{qtype}"

    def test_opening_questions_are_open_ended(self):
        """Opening questions should end with '?' (open-ended)."""
        for key in CATEGORY_ORDER:
            for q in QUESTION_BANK[key]["opening"]:
                assert q["en"].strip().endswith("?"), f"EN opening not a question in {key}: {q['en'][:50]}"
