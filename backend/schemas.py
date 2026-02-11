"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field


# ──────────────────────────── Interview ────────────────────────────

class InterviewStartRequest(BaseModel):
    participant_code: str = ""  # auto-generated if empty
    department: str = ""
    role_level: str = ""  # operational, managerial, executive
    language_pref: str = "auto"  # en, ar, auto


class InterviewStartResponse(BaseModel):
    session_id: str
    greeting: str


class InterviewMessageRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1)


class InterviewMessageResponse(BaseModel):
    reply: str
    category_hint: str = ""  # current SEAM category being explored
    is_complete: bool = False


class InterviewEndRequest(BaseModel):
    session_id: str


class InterviewEndResponse(BaseModel):
    session_id: str
    status: str
    total_messages: int
    field_notes_count: int


# ──────────────────────────── Dashboard ────────────────────────────

class SessionSummary(BaseModel):
    id: str
    participant_code: str
    department: str
    role_level: str
    status: str
    language_pref: str
    created_at: datetime
    completed_at: datetime | None = None
    message_count: int = 0
    field_notes_count: int = 0
    has_summary: bool = False


class FieldNoteOut(BaseModel):
    id: str
    anonymized_text: str
    primary_category: str | None
    secondary_category: str | None
    tags: list[str]
    confidence: int
    cluster_id: int | None
    language: str
    created_at: datetime


class SessionDetail(BaseModel):
    session: SessionSummary
    field_notes: list[FieldNoteOut]
    summary: str | None = None


class SummaryResponse(BaseModel):
    session_id: str
    participant_code: str
    summary: str
    generated: bool = True


class CategoryStat(BaseModel):
    category: str
    count: int
    percentage: float


class AnalyticsResponse(BaseModel):
    total_sessions: int
    completed_sessions: int
    total_field_notes: int
    category_distribution: list[CategoryStat]
    top_tags: list[dict]


class ClusterOut(BaseModel):
    cluster_id: int
    size: int
    representative_text: str
    category: str | None
    sample_texts: list[str]


# ──────────────────────────── Auth ─────────────────────────────────

class LoginRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
