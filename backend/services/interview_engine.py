"""GPT-powered SEAM interview engine.

Manages the conversational flow of semi-structured diagnostic interviews,
cycling through the six SEAM dysfunction categories with adaptive follow-up.
"""

import logging
from openai import AsyncOpenAI

from backend.config import settings
from backend.seam.prompts import (
    INTERVIEW_SYSTEM_PROMPT,
    GREETING_EN,
    GREETING_AR,
    CATEGORY_CONTEXT_TEMPLATE,
    COMPLETION_MESSAGE_EN,
    COMPLETION_MESSAGE_AR,
)
from backend.seam.categories import SEAM_CATEGORIES
from backend.seam.questions import QUESTION_BANK, CATEGORY_ORDER
from backend.services.language_detector import detect_language

logger = logging.getLogger(__name__)

_client = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openrouter_base_url,
        )
    return _client


def build_greeting(language: str) -> str:
    """Build the opening greeting with the first question.

    Args:
        language: 'en', 'ar', or 'auto' (defaults to English).

    Returns:
        Formatted greeting string.
    """
    first_category = CATEGORY_ORDER[0]
    first_q = QUESTION_BANK[first_category]["opening"][0]

    if language == "ar":
        return GREETING_AR.format(first_question=first_q["ar"])
    else:
        return GREETING_EN.format(first_question=first_q["en"])


def _format_questions(questions: list[dict], language: str = "en") -> str:
    """Format a list of question dicts into a numbered string."""
    lang_key = "ar" if language == "ar" else "en"
    lines = []
    for i, q in enumerate(questions, 1):
        lines.append(f"  {i}. {q[lang_key]}")
    return "\n".join(lines)


def build_category_context(
    category_index: int,
    language: str = "en",
    role_level: str = "operational",
) -> str:
    """Build the category context message for GPT.

    Args:
        category_index: Index (0-based) into CATEGORY_ORDER.
        language: 'en' or 'ar'.
        role_level: Participant's role level for depth scaling.

    Returns:
        Formatted category context string for the system message.
    """
    if category_index >= len(CATEGORY_ORDER):
        return ""

    cat_key = CATEGORY_ORDER[category_index]
    cat_info = next(c for c in SEAM_CATEGORIES if c["key"] == cat_key)
    questions = QUESTION_BANK[cat_key]

    # Format all question pools for the LLM
    opening_qs = _format_questions(questions["opening"], language)
    probing_qs = _format_questions(questions["probing"], language)
    closing_qs = _format_questions(questions["closing"], language)

    # Build next category preview
    next_idx = category_index + 1
    if next_idx < len(CATEGORY_ORDER):
        next_key = CATEGORY_ORDER[next_idx]
        next_info = next(c for c in SEAM_CATEGORIES if c["key"] == next_key)
        next_questions = QUESTION_BANK[next_key]
        next_opening = next_questions["opening"][0]
        next_opening_text = next_opening["ar"] if language == "ar" else next_opening["en"]
        next_category_info = (
            f"The NEXT category is: **{next_info['name_en']}** ({next_info['name_ar']})\n"
            f"Description: {next_info['description_ar'] if language == 'ar' else next_info['description_en']}\n"
            f'Suggested opening question for the next category: "{next_opening_text}"'
        )
    else:
        next_category_info = (
            "This is the LAST category. After gathering enough insights, "
            "wrap up warmly and include [ADVANCE_CATEGORY] to complete the interview."
        )

    return CATEGORY_CONTEXT_TEMPLATE.format(
        index=category_index + 1,
        name_en=cat_info["name_en"],
        name_ar=cat_info["name_ar"],
        description=cat_info["description_ar"] if language == "ar" else cat_info["description_en"],
        opening_questions=opening_qs,
        probing_questions=probing_qs,
        closing_questions=closing_qs,
        next_category_info=next_category_info,
        role_level=role_level,
    )


async def generate_reply(
    conversation_history: list[dict],
    category_index: int,
    language: str = "en",
    role_level: str = "operational",
) -> dict:
    """Generate the next interview reply using GPT.

    Args:
        conversation_history: List of {role, content} message dicts.
        category_index: Current SEAM category index (0-based).
        language: Detected language of the conversation.
        role_level: Participant's role level for depth scaling.

    Returns:
        dict with:
            - reply: The assistant's response text.
            - should_advance: Whether to move to the next category.
            - is_complete: Whether the interview is finished.
    """
    # Check if all categories have been covered
    if category_index >= len(CATEGORY_ORDER):
        completion_msg = COMPLETION_MESSAGE_AR if language == "ar" else COMPLETION_MESSAGE_EN
        return {
            "reply": completion_msg,
            "should_advance": False,
            "is_complete": True,
        }

    # Determine depth threshold based on role level
    depth_map = {
        "operational": (3, 5),
        "teacher": (3, 5),
        "coordinator": (5, 7),
        "managerial": (5, 7),
        "executive": (6, 8),
    }
    min_depth, max_depth = depth_map.get(role_level, (3, 5))

    # Count actual exchanges (user messages) in the conversation so far
    user_message_count = sum(1 for m in conversation_history if m["role"] == "user")

    # Build message list for GPT
    messages = [
        {"role": "system", "content": INTERVIEW_SYSTEM_PROMPT},
        {"role": "system", "content": build_category_context(category_index, language, role_level)},
        {
            "role": "system",
            "content": (
                f"DEPTH STATUS: This is exchange #{user_message_count} overall. "
                f"For this participant's role level ({role_level}), aim for "
                f"{min_depth}–{max_depth} exchanges per category. "
                f"Count ALL exchanges — even short answers count as valid exchanges. "
                f"When the participant's answers are consistently brief, that signals "
                f"they've shared what they comfortably can on this topic — respect that "
                f"and advance rather than pushing for more detail. "
                f"When you've reached the depth threshold OR the participant clearly "
                f"has nothing more to add, include the EXACT marker [ADVANCE_CATEGORY] "
                f"at the very end of your message. "
                f"REMEMBER: Your transition message MUST include an opening question "
                f"for the next category — never leave the participant with nothing to respond to."
            ),
        },
    ]
    messages.extend(conversation_history)

    # Retry loop for empty responses
    for attempt in range(2):
        try:
            client = _get_client()
            response = await client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=0.75,
                max_tokens=600,
            )

            reply_text = response.choices[0].message.content or ""
            reply_text = reply_text.strip()

            # Check for category advancement marker
            should_advance = "[ADVANCE_CATEGORY]" in reply_text
            # Remove the marker from the visible reply
            reply_text = reply_text.replace("[ADVANCE_CATEGORY]", "").strip()

            # Enforce em-dash removal (user dislikes them)
            reply_text = reply_text.replace("—", ", ")

            if reply_text:
                break
            
            if attempt == 0:
                logger.warning("Empty response from interview engine, retrying...")
                
        except Exception as e:
            logger.error(f"Interview engine error (attempt {attempt}): {e}")
            if attempt == 1:
                fallback = (
                    "أعتذر، حدث خطأ تقني. هل يمكنك إعادة ما قلته؟"
                    if language == "ar"
                    else "I apologize, there was a technical issue. Could you please repeat what you said?"
                )
                return {
                    "reply": fallback,
                    "should_advance": False,
                    "is_complete": False,
                }

    # If reply is still empty after stripping marker, provide a fallback
    if not reply_text:
        if should_advance:
            # LLM sent only the marker — provide a transition with next question
            next_idx = category_index + 1
            if next_idx < len(CATEGORY_ORDER):
                next_key = CATEGORY_ORDER[next_idx]
                next_questions = QUESTION_BANK[next_key]
                next_opening = next_questions["opening"][0]
                if language == "ar":
                    reply_text = (
                        f"شكراً لمشاركتك. "
                        f"دعنا ننتقل إلى موضوع مختلف — "
                        f"{next_opening['ar']}"
                    )
                else:
                    reply_text = (
                        f"Thanks for that. "
                        f"Let's move on to something else. "
                        f"{next_opening['en']}"
                    )
            else:
                if language == "ar":
                    reply_text = "شكراً لك."
                else:
                    reply_text = "Thanks for your time."
        else:
            # General empty reply fallback
            if language == "ar":
                reply_text = ".."
            else:
                reply_text = "Could you say a bit more?"

    return {
        "reply": reply_text,
        "should_advance": should_advance,
        "is_complete": False,
    }
