"""Unit tests for database models."""

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import InterviewSession, ChatMessage, FieldNote


class TestInterviewSessionModel:
    """Tests for the InterviewSession model."""

    @pytest.mark.asyncio
    async def test_create_session(self, db_session: AsyncSession):
        """Can create a session with required fields."""
        session = InterviewSession(
            participant_code="TEST-100",
            department="Finance",
            role_level="executive",
            language_pref="en",
        )
        db_session.add(session)
        await db_session.commit()

        result = await db_session.execute(
            select(InterviewSession).where(
                InterviewSession.participant_code == "TEST-100"
            )
        )
        saved = result.scalar_one()

        assert saved.participant_code == "TEST-100"
        assert saved.department == "Finance"
        assert saved.status == "active"
        assert saved.current_category_index == 0
        assert saved.id is not None
        assert saved.created_at is not None
        assert saved.completed_at is None
        assert saved.summary is None

    @pytest.mark.asyncio
    async def test_session_generates_uuid(self, db_session: AsyncSession):
        """Session ID is auto-generated as UUID."""
        session = InterviewSession(participant_code="UUID-TEST")
        db_session.add(session)
        await db_session.flush()

        assert session.id is not None
        assert len(session.id) == 36  # UUID format

    @pytest.mark.asyncio
    async def test_session_default_status(self, db_session: AsyncSession):
        """Default status is 'active'."""
        session = InterviewSession(participant_code="STATUS-TEST")
        db_session.add(session)
        await db_session.flush()

        assert session.status == "active"

    @pytest.mark.asyncio
    async def test_session_default_language(self, db_session: AsyncSession):
        """Default language preference is 'auto'."""
        session = InterviewSession(participant_code="LANG-TEST")
        db_session.add(session)
        await db_session.flush()

        assert session.language_pref == "auto"


class TestChatMessageModel:
    """Tests for the ChatMessage model."""

    @pytest.mark.asyncio
    async def test_create_message(self, sample_session, db_session: AsyncSession):
        """Can create a chat message linked to a session."""
        msg = ChatMessage(
            session_id=sample_session.id,
            role="user",
            content="Hello, this is a test message.",
            language="en",
        )
        db_session.add(msg)
        await db_session.commit()

        result = await db_session.execute(
            select(ChatMessage).where(ChatMessage.session_id == sample_session.id)
        )
        saved = result.scalar_one()

        assert saved.role == "user"
        assert saved.content == "Hello, this is a test message."
        assert saved.language == "en"
        assert saved.timestamp is not None

    @pytest.mark.asyncio
    async def test_message_roles(self, sample_session, db_session: AsyncSession):
        """Both 'user' and 'assistant' roles are valid."""
        msgs = [
            ChatMessage(session_id=sample_session.id, role="assistant", content="Hi!"),
            ChatMessage(session_id=sample_session.id, role="user", content="Hello!"),
        ]
        for m in msgs:
            db_session.add(m)
        await db_session.commit()

        result = await db_session.execute(
            select(ChatMessage).where(ChatMessage.session_id == sample_session.id)
        )
        saved = result.scalars().all()
        roles = {m.role for m in saved}

        assert "assistant" in roles
        assert "user" in roles


class TestFieldNoteModel:
    """Tests for the FieldNote model."""

    @pytest.mark.asyncio
    async def test_create_field_note(self, sample_session, db_session: AsyncSession):
        """Can create a field note with all fields."""
        note = FieldNote(
            session_id=sample_session.id,
            original_text="John said the office is noisy.",
            anonymized_text="[PERSON] said the office is noisy.",
            primary_category="working_conditions",
            secondary_category=None,
            tags=["poor_tools", "stress"],
            confidence=85,
            language="en",
        )
        db_session.add(note)
        await db_session.commit()

        result = await db_session.execute(
            select(FieldNote).where(FieldNote.session_id == sample_session.id)
        )
        saved = result.scalar_one()

        assert saved.original_text == "John said the office is noisy."
        assert saved.anonymized_text == "[PERSON] said the office is noisy."
        assert saved.primary_category == "working_conditions"
        assert saved.tags == ["poor_tools", "stress"]
        assert saved.confidence == 85

    @pytest.mark.asyncio
    async def test_field_note_stores_json_tags(self, sample_session, db_session: AsyncSession):
        """Tags are stored and retrieved as JSON list."""
        tags = ["tag1", "tag2", "tag3"]
        note = FieldNote(
            session_id=sample_session.id,
            original_text="Test",
            anonymized_text="Test",
            tags=tags,
        )
        db_session.add(note)
        await db_session.commit()

        result = await db_session.execute(
            select(FieldNote).where(FieldNote.session_id == sample_session.id)
        )
        saved = result.scalar_one()

        assert saved.tags == tags
        assert isinstance(saved.tags, list)

    @pytest.mark.asyncio
    async def test_field_note_optional_cluster(self, sample_session, db_session: AsyncSession):
        """Cluster ID is nullable by default."""
        note = FieldNote(
            session_id=sample_session.id,
            original_text="Test",
            anonymized_text="Test",
        )
        db_session.add(note)
        await db_session.commit()

        result = await db_session.execute(
            select(FieldNote).where(FieldNote.session_id == sample_session.id)
        )
        saved = result.scalar_one()
        assert saved.cluster_id is None

    @pytest.mark.asyncio
    async def test_field_note_embedding_json(self, sample_session, db_session: AsyncSession):
        """Embedding can be stored as JSON list of floats."""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        note = FieldNote(
            session_id=sample_session.id,
            original_text="Test",
            anonymized_text="Test",
            embedding=embedding,
        )
        db_session.add(note)
        await db_session.commit()

        result = await db_session.execute(
            select(FieldNote).where(FieldNote.session_id == sample_session.id)
        )
        saved = result.scalar_one()
        assert saved.embedding == embedding
