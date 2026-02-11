"""Interview chat API endpoints."""

import logging
import secrets
import string
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import InterviewSession, ChatMessage, FieldNote
from backend.schemas import (
    InterviewStartRequest, InterviewStartResponse,
    InterviewMessageRequest, InterviewMessageResponse,
    InterviewEndRequest, InterviewEndResponse,
)
from backend.services.interview_engine import build_greeting, generate_reply
from backend.services.language_detector import detect_language
from backend.services.anonymizer import anonymize
from backend.services.categorizer import categorize_field_note
from backend.seam.questions import CATEGORY_ORDER

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/start", response_model=InterviewStartResponse)
async def start_interview(
    request: InterviewStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new interview session and return the greeting."""
    # Auto-generate participant code if not provided
    code = request.participant_code.strip()
    if not code:
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        code = f"P-{random_part}"

    session = InterviewSession(
        participant_code=code,
        department=request.department,
        role_level=request.role_level,
        language_pref=request.language_pref,
    )
    db.add(session)
    await db.flush()  # Materialize session.id before referencing it

    # Build greeting
    lang = request.language_pref if request.language_pref != "auto" else "en"
    greeting = build_greeting(lang)

    # Save greeting as first assistant message
    msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=greeting,
        language=lang,
    )
    db.add(msg)
    await db.commit()

    return InterviewStartResponse(session_id=session.id, greeting=greeting)


@router.post("/message", response_model=InterviewMessageResponse)
async def send_message(
    request: InterviewMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a participant message and get the bot's response."""
    # Fetch session
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == request.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is not active")

    # Detect language of user message
    user_lang = detect_language(request.message)
    if session.language_pref == "auto":
        lang = user_lang
    else:
        lang = session.language_pref

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message,
        language=user_lang,
    )
    db.add(user_msg)

    # Only save as a field note if the message has enough substance
    # (skip trivial inputs, greetings, and dismissive responses)
    cleaned_text = request.message.strip().lower()
    word_count = len(cleaned_text.split())
    # Common non-substantive phrases that shouldn't be field notes
    dismissive_phrases = [
        # Non-substantive / dismissive
        "i don't know", "i dont know", "no idea", "not sure",
        "nothing to add", "i can't think", "you tell me",
        "i don't have", "i dont have", "no comment",
        "i'm not sure", "im not sure", "pass", "next",
        "that's all", "thats all", "nothing else",
        # Meta-conversational (talking TO the bot, not about the org)
        "don't understand", "dont understand", "what do you mean",
        "can you explain", "can you rephrase", "repeat the question",
        "make the question clear", "unclear question", "what question",
        "can you clarify", "i need clarification", "rephrase",
        "say that again", "come again",
    ]
    is_dismissive = any(phrase in cleaned_text for phrase in dismissive_phrases)
    is_substantive = len(cleaned_text) >= 15 and word_count >= 3 and not is_dismissive
    if is_substantive:
        # Process the user's response as a field note
        # (anonymize + categorize in background)
        anonymized = anonymize(request.message)
        categorization = await categorize_field_note(anonymized)

        field_note = FieldNote(
            session_id=session.id,
            original_text=request.message,
            anonymized_text=anonymized,
            primary_category=categorization["primary_category"],
            secondary_category=categorization["secondary_category"],
            tags=categorization["tags"],
            confidence=categorization["confidence"],
            language=user_lang,
        )
        db.add(field_note)

    # Build conversation history for GPT
    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.timestamp)
    )
    all_messages = messages_result.scalars().all()

    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in all_messages
    ]
    # Add the current user message
    conversation_history.append({"role": "user", "content": request.message})

    # Generate bot reply
    reply_data = await generate_reply(
        conversation_history=conversation_history,
        category_index=session.current_category_index,
        language=lang,
        role_level=session.role_level or "operational",
    )

    # Check if we should advance to next category
    if reply_data["should_advance"]:
        session.current_category_index += 1

    # Check if interview is complete
    if reply_data["is_complete"]:
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)

    # Save bot response
    bot_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=reply_data["reply"],
        language=lang,
    )
    db.add(bot_msg)

    await db.commit()

    # Build category hint
    cat_hint = ""
    if session.current_category_index < len(CATEGORY_ORDER):
        cat_hint = CATEGORY_ORDER[session.current_category_index]

    return InterviewMessageResponse(
        reply=reply_data["reply"],
        category_hint=cat_hint,
        is_complete=reply_data["is_complete"],
    )


@router.post("/end", response_model=InterviewEndResponse)
async def end_interview(
    request: InterviewEndRequest,
    db: AsyncSession = Depends(get_db),
):
    """Manually end an interview session."""
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == request.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)

    # Count messages and field notes
    msg_count = await db.execute(
        select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session.id)
    )
    note_count = await db.execute(
        select(func.count(FieldNote.id)).where(FieldNote.session_id == session.id)
    )

    await db.commit()

    return InterviewEndResponse(
        session_id=session.id,
        status="completed",
        total_messages=msg_count.scalar() or 0,
        field_notes_count=note_count.scalar() or 0,
    )


@router.get("/{session_id}/status")
async def get_session_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the current status of an interview session."""
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.id,
        "status": session.status,
        "current_category_index": session.current_category_index,
        "current_category": (
            CATEGORY_ORDER[session.current_category_index]
            if session.current_category_index < len(CATEGORY_ORDER)
            else "completed"
        ),
        "progress": min(100, int((session.current_category_index / len(CATEGORY_ORDER)) * 100)),
    }
