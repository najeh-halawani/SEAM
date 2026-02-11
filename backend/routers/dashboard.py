"""Consultant dashboard API endpoints."""

import csv
import io
import json
import logging
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import InterviewSession, ChatMessage, FieldNote
from backend.routers.auth import verify_token
from backend.schemas import (
    SessionSummary, SessionDetail, FieldNoteOut,
    AnalyticsResponse, CategoryStat, ClusterOut,
    SummaryResponse,
)
from backend.services.clusterer import cluster_field_notes
from backend.services.summarizer import generate_session_summary
from backend.seam.categories import CATEGORY_NAMES_EN

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions(
    status: str | None = None,
    department: str | None = None,
    _user: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """List all interview sessions with optional filters."""
    query = select(InterviewSession).order_by(InterviewSession.created_at.desc())

    if status:
        query = query.where(InterviewSession.status == status)
    if department:
        query = query.where(InterviewSession.department == department)

    result = await db.execute(query)
    sessions = result.scalars().all()

    summaries = []
    for s in sessions:
        # Get counts
        msg_count = await db.execute(
            select(func.count(ChatMessage.id)).where(ChatMessage.session_id == s.id)
        )
        note_count = await db.execute(
            select(func.count(FieldNote.id)).where(FieldNote.session_id == s.id)
        )
        summaries.append(SessionSummary(
            id=s.id,
            participant_code=s.participant_code,
            department=s.department,
            role_level=s.role_level,
            status=s.status,
            language_pref=s.language_pref,
            created_at=s.created_at,
            completed_at=s.completed_at,
            message_count=msg_count.scalar() or 0,
            field_notes_count=note_count.scalar() or 0,
            has_summary=bool(s.summary),
        ))

    return summaries


@router.get("/session/{session_id}", response_model=SessionDetail)
async def get_session_detail(
    session_id: str,
    _user: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Get full session detail with field notes."""
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.field_notes))
        .where(InterviewSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msg_count = await db.execute(
        select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session.id)
    )

    session_summary = SessionSummary(
        id=session.id,
        participant_code=session.participant_code,
        department=session.department,
        role_level=session.role_level,
        status=session.status,
        language_pref=session.language_pref,
        created_at=session.created_at,
        completed_at=session.completed_at,
        message_count=msg_count.scalar() or 0,
        field_notes_count=len(session.field_notes),
        has_summary=bool(session.summary),
    )

    notes = [
        FieldNoteOut(
            id=n.id,
            anonymized_text=n.anonymized_text,
            primary_category=n.primary_category,
            secondary_category=n.secondary_category,
            tags=n.tags or [],
            confidence=n.confidence,
            cluster_id=n.cluster_id,
            language=n.language,
            created_at=n.created_at,
        )
        for n in session.field_notes
    ]

    return SessionDetail(session=session_summary, field_notes=notes, summary=session.summary)


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    _user: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated analytics across all sessions."""
    # Total sessions
    total = await db.execute(select(func.count(InterviewSession.id)))
    completed = await db.execute(
        select(func.count(InterviewSession.id))
        .where(InterviewSession.status == "completed")
    )
    total_notes = await db.execute(select(func.count(FieldNote.id)))

    # Category distribution
    result = await db.execute(select(FieldNote.primary_category))
    categories = [r[0] for r in result.all() if r[0]]
    cat_counter = Counter(categories)
    total_cat = sum(cat_counter.values()) or 1

    cat_distribution = [
        CategoryStat(
            category=CATEGORY_NAMES_EN.get(cat, cat),
            count=count,
            percentage=round((count / total_cat) * 100, 1),
        )
        for cat, count in cat_counter.most_common()
    ]

    # Top tags
    result = await db.execute(select(FieldNote.tags))
    all_tags = []
    for row in result.all():
        if row[0]:
            all_tags.extend(row[0])
    tag_counter = Counter(all_tags)
    top_tags = [{"tag": tag, "count": count} for tag, count in tag_counter.most_common(15)]

    return AnalyticsResponse(
        total_sessions=total.scalar() or 0,
        completed_sessions=completed.scalar() or 0,
        total_field_notes=total_notes.scalar() or 0,
        category_distribution=cat_distribution,
        top_tags=top_tags,
    )


@router.get("/clusters", response_model=list[ClusterOut])
async def get_clusters(
    _user: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Run semantic clustering on all field notes and return results."""
    result = await db.execute(
        select(FieldNote).order_by(FieldNote.created_at)
    )
    notes = result.scalars().all()

    if not notes:
        return []

    texts = [n.anonymized_text for n in notes]
    embeddings = [n.embedding for n in notes if n.embedding]

    # Use stored embeddings if available, otherwise generate
    if len(embeddings) == len(texts):
        cluster_result = cluster_field_notes(texts, embeddings=embeddings)
    else:
        cluster_result = cluster_field_notes(texts)

    # Update cluster assignments in DB
    for i, note in enumerate(notes):
        note.cluster_id = cluster_result["cluster_labels"][i]
    await db.commit()

    # Build response — only include clusters with a valid SEAM category
    clusters = []
    for cid, cdata in cluster_result["clusters"].items():
        # Find most common category in cluster
        cluster_notes = [n for n in notes if n.cluster_id == cid]
        categories = [n.primary_category for n in cluster_notes if n.primary_category]
        most_common_cat = Counter(categories).most_common(1)
        cat_name = CATEGORY_NAMES_EN.get(most_common_cat[0][0], most_common_cat[0][0]) if most_common_cat else None

        # Skip clusters without a valid category
        if not cat_name:
            continue

        clusters.append(ClusterOut(
            cluster_id=cid,
            size=len(cdata["texts"]),
            representative_text=cdata["representative"],
            category=cat_name,
            sample_texts=cdata["texts"][:5],
        ))

    return sorted(clusters, key=lambda c: c.size, reverse=True)


@router.get("/export/{session_id}")
async def export_session(
    session_id: str,
    format: str = "json",
    _user: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Export a session's field notes as JSON or CSV."""
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.field_notes))
        .where(InterviewSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    notes_data = [
        {
            "anonymized_text": n.anonymized_text,
            "primary_category": CATEGORY_NAMES_EN.get(n.primary_category, n.primary_category),
            "secondary_category": CATEGORY_NAMES_EN.get(n.secondary_category, n.secondary_category) if n.secondary_category else None,
            "tags": ", ".join(n.tags) if n.tags else "",
            "confidence": n.confidence,
            "language": n.language,
            "cluster_id": n.cluster_id,
        }
        for n in session.field_notes
    ]

    if format == "csv":
        output = io.StringIO()
        if notes_data:
            writer = csv.DictWriter(output, fieldnames=notes_data[0].keys())
            writer.writeheader()
            writer.writerows(notes_data)
        content = output.getvalue()
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8-sig")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=session_{session_id[:8]}.csv"},
        )
    else:
        export_data = {
            "session": {
                "id": session.id,
                "participant_code": session.participant_code,
                "department": session.department,
                "role_level": session.role_level,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
            },
            "field_notes": notes_data,
        }
        content = json.dumps(export_data, ensure_ascii=False, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=session_{session_id[:8]}.json"},
        )


@router.get("/conversation/{session_id}")
async def get_conversation(
    session_id: str,
    _user: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Get the full conversation transcript for a session."""
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp)
    )
    messages = messages_result.scalars().all()

    return {
        "session_id": session_id,
        "participant_code": session.participant_code,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "language": m.language,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in messages
        ],
    }


@router.post("/summary/{session_id}", response_model=SummaryResponse)
async def generate_summary(
    session_id: str,
    _user: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Generate or regenerate the diagnostic summary for a session."""
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.field_notes))
        .where(InterviewSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.field_notes:
        raise HTTPException(status_code=400, detail="No field notes to summarize")

    # Prepare field notes for summarizer
    notes_data = [
        {
            "anonymized_text": n.anonymized_text,
            "primary_category": CATEGORY_NAMES_EN.get(n.primary_category, n.primary_category),
            "secondary_category": CATEGORY_NAMES_EN.get(n.secondary_category, n.secondary_category) if n.secondary_category else None,
            "tags": n.tags or [],
            "confidence": n.confidence,
            "language": n.language,
        }
        for n in session.field_notes
    ]

    participant_info = {
        "participant_code": session.participant_code,
        "department": session.department,
        "role_level": session.role_level,
    }

    # Generate summary via GPT
    summary_text = await generate_session_summary(notes_data, participant_info)

    # Save to database
    session.summary = summary_text
    await db.commit()

    return SummaryResponse(
        session_id=session.id,
        participant_code=session.participant_code,
        summary=summary_text,
    )


@router.get("/summary/{session_id}", response_model=SummaryResponse)
async def get_summary(
    session_id: str,
    _user: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Get the existing diagnostic summary for a session."""
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.summary:
        raise HTTPException(status_code=404, detail="No summary generated yet")

    return SummaryResponse(
        session_id=session.id,
        participant_code=session.participant_code,
        summary=session.summary,
        generated=False,
    )
