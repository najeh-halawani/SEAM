"""SEAM dysfunction categorizer using OpenAI GPT.

Classifies field notes into primary and optional secondary SEAM
dysfunction categories, assigns thematic tags, and provides
confidence scores.
"""

import json
import logging
import re
from openai import AsyncOpenAI

from backend.config import settings
from backend.seam.prompts import CATEGORIZATION_SYSTEM_PROMPT

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


def _extract_json(text: str) -> dict | None:
    """Extract JSON object from a response that may contain extra text."""
    if not text:
        return None
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try to find JSON within the text
    match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


async def categorize_field_note(text: str) -> dict:
    """Classify a single field note into SEAM dysfunction categories.

    Args:
        text: The (anonymized) field note text.

    Returns:
        dict with keys: primary_category, secondary_category, tags, confidence
    """
    if not text or not text.strip():
        return {
            "primary_category": None,
            "secondary_category": None,
            "tags": [],
            "confidence": 0,
        }

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": CATEGORIZATION_SYSTEM_PROMPT},
                {"role": "user", "content": f'Classify this field note:\n\n"{text}"'},
            ],
            temperature=0.1,
            max_tokens=200,
        )

        raw_content = response.choices[0].message.content or ""
        result = _extract_json(raw_content)

        if not result:
            logger.warning(
                f"Categorizer returned non-JSON: {raw_content[:200]}"
            )
            return {
                "primary_category": None,
                "secondary_category": None,
                "tags": [],
                "confidence": 0,
            }

        # Validate and normalize the result
        return {
            "primary_category": result.get("primary_category"),
            "secondary_category": result.get("secondary_category"),
            "tags": result.get("tags", []),
            "confidence": min(100, max(0, int(result.get("confidence", 50)))),
        }

    except Exception as e:
        logger.error(f"Categorization failed for text: {text[:80]}... Error: {e}")
        return {
            "primary_category": None,
            "secondary_category": None,
            "tags": [],
            "confidence": 0,
        }


async def categorize_batch(texts: list[str]) -> list[dict]:
    """Categorize a batch of field notes.

    Processes sequentially to respect rate limits.
    """
    results = []
    for text in texts:
        result = await categorize_field_note(text)
        results.append(result)
    return results
