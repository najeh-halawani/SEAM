"""Shared test fixtures for the SEAM assessment backend tests."""

import asyncio
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Override database URL before importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_seam.db"
os.environ["OPENAI_API_KEY"] = "test-key-not-real"
os.environ["APP_SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["CONSULTANT_PASSWORD"] = "testpassword123"

from backend.database import Base
from backend.models import InterviewSession, ChatMessage, FieldNote


# Use a separate test database
TEST_DB_URL = "sqlite+aiosqlite:///./test_seam.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_engine():
    """Create a fresh test database engine for each test."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

    # Clean up test db file
    if os.path.exists("./test_seam.db"):
        os.remove("./test_seam.db")


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Provide an async database session for each test."""
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def sample_session(db_session: AsyncSession):
    """Create a sample interview session in the test database."""
    session = InterviewSession(
        participant_code="TEST-001",
        department="IT",
        role_level="operational",
        language_pref="en",
        status="active",
    )
    db_session.add(session)
    await db_session.flush()
    await db_session.commit()
    return session


@pytest_asyncio.fixture
async def completed_session_with_notes(db_session: AsyncSession):
    """Create a completed session with field notes for summary testing."""
    from datetime import datetime, timezone

    session = InterviewSession(
        participant_code="TEST-002",
        department="HR",
        role_level="managerial",
        language_pref="en",
        status="completed",
        completed_at=datetime.now(timezone.utc),
    )
    db_session.add(session)
    await db_session.flush()

    # Add chat messages
    messages = [
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content="Welcome to the interview.",
            language="en",
        ),
        ChatMessage(
            session_id=session.id,
            role="user",
            content="We don't get clear direction from management.",
            language="en",
        ),
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content="Can you tell me more about that?",
            language="en",
        ),
        ChatMessage(
            session_id=session.id,
            role="user",
            content="The office is too noisy and equipment is outdated.",
            language="en",
        ),
    ]
    for msg in messages:
        db_session.add(msg)

    # Add field notes
    field_notes = [
        FieldNote(
            session_id=session.id,
            original_text="We don't get clear direction from John the manager.",
            anonymized_text="We don't get clear direction from [PERSON] the manager.",
            primary_category="strategic_implementation",
            secondary_category=None,
            tags=["unclear_priorities", "vision_misalignment"],
            confidence=85,
            language="en",
        ),
        FieldNote(
            session_id=session.id,
            original_text="The office is too noisy and equipment is outdated.",
            anonymized_text="The office is too noisy and equipment is outdated.",
            primary_category="working_conditions",
            secondary_category=None,
            tags=["poor_tools", "stress"],
            confidence=90,
            language="en",
        ),
    ]
    for note in field_notes:
        db_session.add(note)

    await db_session.commit()
    return session
