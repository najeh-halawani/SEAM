"""Unit tests for the SEAM categorizer service.

These tests mock the OpenAI API to test classification logic
without requiring a real API key.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.services.categorizer import categorize_field_note


class TestCategorizerWithMock:
    """Tests for categorize_field_note using mocked OpenAI responses."""

    @pytest.fixture
    def mock_openai_response(self):
        """Create a mock OpenAI API response factory."""
        def _make_response(content: str):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = content
            return mock_response
        return _make_response

    @pytest.mark.asyncio
    async def test_categorize_working_conditions(self, mock_openai_response):
        """Correctly parses a working conditions classification."""
        api_response = json.dumps({
            "primary_category": "working_conditions",
            "secondary_category": None,
            "tags": ["poor_tools", "stress"],
            "confidence": 90
        })

        with patch("backend.services.categorizer._get_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_openai_response(api_response)
            )

            result = await categorize_field_note("The office is too noisy and the equipment is outdated.")

            assert result["primary_category"] == "working_conditions"
            assert result["confidence"] == 90
            assert "poor_tools" in result["tags"]
            assert "stress" in result["tags"]

    @pytest.mark.asyncio
    async def test_categorize_strategic_implementation(self, mock_openai_response):
        """Correctly parses a strategic implementation classification."""
        api_response = json.dumps({
            "primary_category": "strategic_implementation",
            "secondary_category": "communication_3cs",
            "tags": ["unclear_priorities", "vision_misalignment"],
            "confidence": 85
        })

        with patch("backend.services.categorizer._get_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_openai_response(api_response)
            )

            result = await categorize_field_note("We don't get clear direction from management.")

            assert result["primary_category"] == "strategic_implementation"
            assert result["secondary_category"] == "communication_3cs"
            assert result["confidence"] == 85

    @pytest.mark.asyncio
    async def test_categorize_time_management(self, mock_openai_response):
        """Correctly parses time management classification."""
        api_response = json.dumps({
            "primary_category": "time_management",
            "secondary_category": None,
            "tags": ["excessive_meetings", "time_waste"],
            "confidence": 78
        })

        with patch("backend.services.categorizer._get_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_openai_response(api_response)
            )

            result = await categorize_field_note("We spend hours in meetings that could be emails.")

            assert result["primary_category"] == "time_management"
            assert "excessive_meetings" in result["tags"]

    @pytest.mark.asyncio
    async def test_categorize_with_secondary_category(self, mock_openai_response):
        """Tests that secondary categories are properly parsed."""
        api_response = json.dumps({
            "primary_category": "work_organization",
            "secondary_category": "communication_3cs",
            "tags": ["role_ambiguity", "coordination_gaps"],
            "confidence": 72
        })

        with patch("backend.services.categorizer._get_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_openai_response(api_response)
            )

            result = await categorize_field_note("Nobody knows who is responsible for what.")

            assert result["primary_category"] == "work_organization"
            assert result["secondary_category"] == "communication_3cs"

    @pytest.mark.asyncio
    async def test_categorize_returns_required_keys(self, mock_openai_response):
        """Result always contains required keys."""
        api_response = json.dumps({
            "primary_category": "integrated_training",
            "secondary_category": None,
            "tags": ["skill_gaps"],
            "confidence": 65
        })

        with patch("backend.services.categorizer._get_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_openai_response(api_response)
            )

            result = await categorize_field_note("We never receive training on new systems.")

            assert "primary_category" in result
            assert "secondary_category" in result
            assert "tags" in result
            assert "confidence" in result

    @pytest.mark.asyncio
    async def test_categorize_handles_api_error(self):
        """Gracefully handles API errors."""
        with patch("backend.services.categorizer._get_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                side_effect=Exception("API error")
            )

            result = await categorize_field_note("Test text")

            # Should return fallback values, not crash
            assert isinstance(result, dict)
            assert "primary_category" in result

    @pytest.mark.asyncio
    async def test_categorize_handles_malformed_json(self, mock_openai_response):
        """Handles malformed JSON from the API gracefully."""
        with patch("backend.services.categorizer._get_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_openai_response("not valid json {{{")
            )

            result = await categorize_field_note("Test text")

            assert isinstance(result, dict)
            assert "primary_category" in result


class TestCategorizerValidation:
    """Tests for categorizer output validation."""

    @pytest.mark.asyncio
    async def test_confidence_is_integer(self):
        """Confidence score should be an integer."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "primary_category": "working_conditions",
            "secondary_category": None,
            "tags": ["stress"],
            "confidence": 85
        })

        with patch("backend.services.categorizer._get_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_response
            )

            result = await categorize_field_note("The office is uncomfortable.")
            assert isinstance(result["confidence"], int)

    @pytest.mark.asyncio
    async def test_tags_is_list(self):
        """Tags should always be a list."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "primary_category": "time_management",
            "secondary_category": None,
            "tags": ["time_waste"],
            "confidence": 70
        })

        with patch("backend.services.categorizer._get_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_response
            )

            result = await categorize_field_note("Too many meetings.")
            assert isinstance(result["tags"], list)
