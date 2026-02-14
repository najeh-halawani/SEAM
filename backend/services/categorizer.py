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
    """Extract JSON object from a response that may contain extra text.

    Handles nested structures (arrays, nested objects) and markdown fences.
    """
    if not text:
        return None

    # Strip markdown code fences if present
    cleaned = re.sub(r'```(?:json)?\s*', '', text).strip()
    cleaned = cleaned.rstrip('`').strip()

    # predefined replacements for common LLM json errors
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)  # remove trailing commas

    logger.debug(f"Categorizer extraction attempt on: {cleaned[:200]}...")

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.debug(f"Direct JSON parse failed: {e}")

    # Use bracket counting to find the outermost {...} object
    start = cleaned.find('{')
    if start == -1:
        logger.debug("No opening brace found in response")
        return None

    depth = 0
    in_string = False
    escape_next = False
    for i in range(start, len(cleaned)):
        ch = cleaned[i]
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                candidate = cleaned[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError as e:
                    logger.debug(f"Candidate JSON parse failed: {e}")
                    # Last ditch effort: try to fix unquoted keys or single quotes
                    try:
                         # Very basic repair for simple cases
                         import ast
                         return ast.literal_eval(candidate)
                    except Exception as ast_e:
                        logger.debug(f"AST literal eval failed: {ast_e}")
                        return None
    logger.debug("Could not find balanced braces for JSON object")
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

        # Allow one retry if the LLM returns empty / unparseable
        for attempt in range(2):
            logger.info(f"Categorizing note (attempt {attempt+1}): {text[:50]}...")
            
            response = await client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": CATEGORIZATION_SYSTEM_PROMPT},
                    {"role": "user", "content": f'Classify this field note:\n\n"{text}"'},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000,
            )

            raw_content = response.choices[0].message.content or ""
            logger.debug(f"Categorizer raw response: {raw_content}")
            
            result = _extract_json(raw_content)

            if result:
                # Validate and normalize the result
                return {
                    "primary_category": result.get("primary_category"),
                    "secondary_category": result.get("secondary_category"),
                    "tags": result.get("tags", []),
                    "confidence": min(100, max(0, int(result.get("confidence", 50)))),
                }

            if attempt == 0:
                reason = "empty response" if not raw_content.strip() else f"non-JSON content (len={len(raw_content)})"
                logger.warning(f"Categorizer failed validation: {reason}. Retrying...")

        # Both attempts failed
        logger.error(f"Categorizer failed after retry for text: {text[:50]}...")
        return {
            "primary_category": None,
            "secondary_category": None,
            "tags": [],
            "confidence": 0,
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
