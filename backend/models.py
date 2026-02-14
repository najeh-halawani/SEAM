"""SQLAlchemy ORM models for the SEAM Assessment system."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer, JSON
)
from sqlalchemy.orm import relationship

from backend.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


def _new_id():
    return str(uuid.uuid4())


class InterviewSession(Base):
    """Represents one diagnostic interview session with a participant."""
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=_new_id)
    participant_code = Column(String(50), nullable=False)
    department = Column(String(100), default="")
    role_level = Column(String(50), default="")  # e.g. operational, managerial, executive
    language_pref = Column(String(10), default="auto")  # en, ar, auto
    status = Column(String(20), default="active")  # active, completed, cancelled
    current_category_index = Column(Integer, default=0)
    summary = Column(Text, nullable=True)  # GPT-generated diagnostic brief
    created_at = Column(DateTime, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    field_notes = relationship("FieldNote", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual message in an interview conversation."""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=_new_id)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    role = Column(String(10), nullable=False)  # "assistant" or "user"
    content = Column(Text, nullable=False)
    language = Column(String(10), default="en")  # detected language
    timestamp = Column(DateTime, default=_utcnow)

    session = relationship("InterviewSession", back_populates="messages")


class FieldNote(Base):
    """A processed diagnostic field note extracted from interview responses."""
    __tablename__ = "field_notes"

    id = Column(String(36), primary_key=True, default=_new_id)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    original_text = Column(Text, nullable=False)         # verbatim (access-restricted)
    anonymized_text = Column(Text, nullable=False)        # after NER + rule redaction
    primary_category = Column(String(60), nullable=True)  # SEAM dysfunction category
    secondary_category = Column(String(60), nullable=True)
    tags = Column(JSON, default=list)                     # thematic tags
    confidence = Column(Integer, default=0)               # classification confidence 0-100
    cluster_id = Column(Integer, nullable=True)
    embedding = Column(JSON, nullable=True)               # stored as list of floats
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=_utcnow)

    session = relationship("InterviewSession", back_populates="field_notes")


class ClusterRun(Base):
    """Persisted result of a clustering run."""
    __tablename__ = "cluster_runs"

    id = Column(String(36), primary_key=True, default=_new_id)
    ran_at = Column(DateTime, default=_utcnow, nullable=False)
    session_count = Column(Integer, default=0)  # sessions at time of run
    result = Column(JSON, nullable=False)       # full cluster output
