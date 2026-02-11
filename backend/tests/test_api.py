"""Integration tests for API endpoints.

These tests use mocked OpenAI calls to test the full request/response
cycle through the FastAPI application.
"""

import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

# Set test env vars before importing app
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_api_seam.db"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["APP_SECRET_KEY"] = "test-secret"
os.environ["CONSULTANT_PASSWORD"] = "testpass"

from backend.main import app


@pytest_asyncio.fixture
async def client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clean up test database
    if os.path.exists("./test_api_seam.db"):
        os.remove("./test_api_seam.db")


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    """Get authentication headers for dashboard endpoints."""
    response = await client.post(
        "/api/auth/login",
        json={"password": "testpass"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoint:
    """Tests for basic server health."""

    @pytest.mark.asyncio
    async def test_root_returns_200(self, client: AsyncClient):
        """Root endpoint should return 200."""
        response = await client.get("/")
        # Either returns the landing page or a redirect
        assert response.status_code in (200, 307)


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_correct_password(self, client: AsyncClient):
        """Login with correct password returns token."""
        response = await client.post(
            "/api/auth/login",
            json={"password": "testpass"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Login with wrong password returns 401."""
        response = await client.post(
            "/api/auth/login",
            json={"password": "wrongpass"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_empty_password(self, client: AsyncClient):
        """Login with empty password returns error."""
        response = await client.post(
            "/api/auth/login",
            json={"password": ""},
        )
        assert response.status_code in (401, 422)


class TestInterviewEndpoints:
    """Tests for interview API endpoints."""

    @pytest.mark.asyncio
    async def test_start_interview(self, client: AsyncClient):
        """Starting an interview creates a session and returns greeting."""
        response = await client.post(
            "/api/interview/start",
            json={
                "participant_code": "TEST-001",
                "department": "IT",
                "role_level": "operational",
                "language_pref": "en",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "greeting" in data
        assert len(data["session_id"]) == 36  # UUID format
        assert len(data["greeting"]) > 0

    @pytest.mark.asyncio
    async def test_start_interview_arabic(self, client: AsyncClient):
        """Starting an interview with Arabic returns Arabic greeting."""
        response = await client.post(
            "/api/interview/start",
            json={
                "participant_code": "TEST-AR",
                "language_pref": "ar",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Arabic greeting should contain Arabic characters
        assert any(
            "\u0600" <= c <= "\u06FF" for c in data["greeting"]
        ), "Greeting should contain Arabic text"

    @pytest.mark.asyncio
    async def test_start_interview_missing_code(self, client: AsyncClient):
        """Starting without participant_code returns 422."""
        response = await client.post(
            "/api/interview/start",
            json={"department": "IT"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_send_message_to_nonexistent_session(self, client: AsyncClient):
        """Sending message to invalid session returns 404."""
        response = await client.post(
            "/api/interview/message",
            json={
                "session_id": "nonexistent-session-id",
                "message": "Hello",
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_send_message_flow(self, client: AsyncClient):
        """Full message send flow with mocked GPT."""
        # Start session
        start_resp = await client.post(
            "/api/interview/start",
            json={"participant_code": "FLOW-TEST", "language_pref": "en"},
        )
        session_id = start_resp.json()["session_id"]

        # Mock GPT responses
        mock_categorize_response = MagicMock()
        mock_categorize_response.choices = [MagicMock()]
        mock_categorize_response.choices[0].message.content = json.dumps({
            "primary_category": "working_conditions",
            "secondary_category": None,
            "tags": ["stress"],
            "confidence": 80,
        })

        mock_reply_response = MagicMock()
        mock_reply_response.choices = [MagicMock()]
        mock_reply_response.choices[0].message.content = "That sounds challenging. Can you tell me more?"

        with patch("backend.services.categorizer._get_client") as mock_cat, \
             patch("backend.services.interview_engine._get_client") as mock_eng:

            mock_cat.return_value.chat.completions.create = AsyncMock(
                return_value=mock_categorize_response
            )
            mock_eng.return_value.chat.completions.create = AsyncMock(
                return_value=mock_reply_response
            )

            response = await client.post(
                "/api/interview/message",
                json={
                    "session_id": session_id,
                    "message": "The office is too noisy.",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "reply" in data
            assert "is_complete" in data
            assert isinstance(data["is_complete"], bool)

    @pytest.mark.asyncio
    async def test_end_interview(self, client: AsyncClient):
        """Ending an interview marks session as completed."""
        # Start session
        start_resp = await client.post(
            "/api/interview/start",
            json={"participant_code": "END-TEST"},
        )
        session_id = start_resp.json()["session_id"]

        # End session
        response = await client.post(
            "/api/interview/end",
            json={"session_id": session_id},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_get_session_status(self, client: AsyncClient):
        """Can retrieve session status by ID."""
        # Start session
        start_resp = await client.post(
            "/api/interview/start",
            json={"participant_code": "STATUS-TEST"},
        )
        session_id = start_resp.json()["session_id"]

        response = await client.get(f"/api/interview/{session_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["current_category_index"] == 0


class TestDashboardEndpoints:
    """Tests for consultant dashboard API endpoints."""

    @pytest.mark.asyncio
    async def test_sessions_requires_auth(self, client: AsyncClient):
        """Dashboard endpoints require authentication."""
        response = await client.get("/api/dashboard/sessions")
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_list_sessions(self, client: AsyncClient, auth_headers):
        """Can list sessions when authenticated."""
        response = await client.get(
            "/api/dashboard/sessions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_analytics(self, client: AsyncClient, auth_headers):
        """Analytics endpoint returns expected structure."""
        response = await client.get(
            "/api/dashboard/analytics",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_sessions" in data
        assert "completed_sessions" in data
        assert "total_field_notes" in data
        assert "category_distribution" in data
        assert "top_tags" in data

    @pytest.mark.asyncio
    async def test_session_detail_not_found(self, client: AsyncClient, auth_headers):
        """Getting a non-existent session returns 404."""
        response = await client.get(
            "/api/dashboard/session/nonexistent-id",
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_export_not_found(self, client: AsyncClient, auth_headers):
        """Exporting non-existent session returns 404."""
        response = await client.get(
            "/api/dashboard/export/nonexistent-id?format=json",
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_summary_not_found(self, client: AsyncClient, auth_headers):
        """Summary for non-existent session returns 404."""
        response = await client.get(
            "/api/dashboard/summary/nonexistent-id",
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_full_dashboard_flow(self, client: AsyncClient, auth_headers):
        """Complete flow: start interview → list on dashboard."""
        # Start an interview
        await client.post(
            "/api/interview/start",
            json={"participant_code": "DASH-TEST", "department": "HR"},
        )

        # Check it appears in dashboard
        response = await client.get(
            "/api/dashboard/sessions",
            headers=auth_headers,
        )
        sessions = response.json()
        assert len(sessions) >= 1
        codes = [s["participant_code"] for s in sessions]
        assert "DASH-TEST" in codes
