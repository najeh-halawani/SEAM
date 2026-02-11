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


def build_category_context(category_index: int, language: str = "en", role_level: str = "operational") -> str:
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

    # Pick the first opening question in the appropriate language
    opening_q = questions["opening"][0]
    opening_text = opening_q["ar"] if language == "ar" else opening_q["en"]

    return CATEGORY_CONTEXT_TEMPLATE.format(
        index=category_index + 1,
        name_en=cat_info["name_en"],
        name_ar=cat_info["name_ar"],
        description=cat_info["description_ar"] if language == "ar" else cat_info["description_en"],
        opening_question=opening_text,
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

    # Build message list for GPT
    messages = [
        {"role": "system", "content": INTERVIEW_SYSTEM_PROMPT},
        {"role": "system", "content": build_category_context(category_index, language, role_level)},
        {
            "role": "system",
            "content": (
                f"IMPORTANT: For this participant's role level ({role_level}), you should have "
                f"{min_depth}–{max_depth} meaningful exchanges per category before considering advancement. "
                "A 'meaningful exchange' is one where the participant shares a concrete experience, "
                "opinion, or specific example — not just a brief acknowledgment. "
                "When the participant has shared enough rich insights (meeting the depth threshold) "
                "OR explicitly says they have nothing more to add, include the EXACT marker "
                "[ADVANCE_CATEGORY] at the very end of your message (after your visible response). "
                "This marker will NOT be shown to the participant. Do NOT include this marker "
                "if the participant is still actively sharing valuable insights."
            ),
        },
    ]
    messages.extend(conversation_history)

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

        # If reply is empty after stripping marker, provide a fallback
        if not reply_text:
            if should_advance:
                # LLM sent only the marker — provide a transition message
                if language == "ar":
                    reply_text = "شكراً لمشاركتك القيّمة في هذا المحور. دعنا ننتقل إلى الموضوع التالي."
                else:
                    reply_text = "Thank you for sharing those valuable insights. Let's move on to explore the next area together."
            else:
                # General empty reply fallback
                if language == "ar":
                    reply_text = "شكراً لمشاركتك. هل يمكنك التوسع أكثر في ذلك؟"
                else:
                    reply_text = "Thank you for sharing that. Could you tell me a bit more about your experience with this?"

        return {
            "reply": reply_text,
            "should_advance": should_advance,
            "is_complete": False,
        }

    except Exception as e:
        logger.error(f"Interview engine error: {e}")
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
