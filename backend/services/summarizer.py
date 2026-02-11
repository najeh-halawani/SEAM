"""Post-interview diagnostic summary generator.

After an interview session is completed, this service takes all anonymized
field notes and produces a structured SEAM diagnostic brief using GPT.
"""

import json
import logging
from openai import AsyncOpenAI

from backend.config import settings
from backend.seam.categories import SEAM_CATEGORIES

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


SUMMARY_SYSTEM_PROMPT = """You are a senior SEAM (Socio-Economic Approach to Management) consultant synthesizing diagnostic interview data.

You will receive a set of anonymized field notes from a single participant interview. Each note has been classified into SEAM dysfunction categories with thematic tags.

## Your Task
Produce a **structured diagnostic brief** that synthesizes the participant's observations. This will be used by the lead consultant to prepare the mirror effect presentation and convergence analysis.

## SEAM Dysfunction Categories for Reference:
""" + "\n".join([
    f"{i+1}. **{c['name_en']}** ({c['name_ar']}): {c['description_en']}"
    for i, c in enumerate(SEAM_CATEGORIES)
]) + """

## Output Structure (use this exact markdown format):

### Key Findings

A 3-5 sentence executive summary of the most critical dysfunctions observed.

### Dysfunction Analysis

For each category where dysfunctions were identified (skip categories with no relevant notes):

#### [Category Name]
- **Severity**: High / Medium / Low (based on frequency and intensity of mentions)
- **Core issues**: Brief synthesis of the problems identified
- **Key verbatim**: 1-2 representative anonymized quotes
- **Tags**: List the relevant thematic tags

### Cross-Cutting Themes

Identify patterns or connections that span multiple categories (e.g., "Communication breakdowns appear to be both a cause and consequence of poor work organization").

### Priority Dysfunctions

Rank the top 3 dysfunctions by impact, with a one-line justification for each.

## Rules:
1. Use ONLY the anonymized field notes provided — do not invent or assume.
2. Preserve the participant's voice by including direct (anonymized) quotes.
3. Be analytical but neutral — describe, don't prescribe.
4. If notes are in Arabic, produce the summary in Arabic. If mixed, produce bilingual summary.
5. Be concise — the entire summary should fit on 1-2 pages.
"""


async def generate_session_summary(
    field_notes: list[dict],
    participant_info: dict,
) -> str:
    """Generate a structured SEAM diagnostic summary from session field notes.

    Args:
        field_notes: List of dicts with keys:
            - anonymized_text
            - primary_category
            - secondary_category
            - tags
            - confidence
            - language
        participant_info: Dict with participant_code, department, role_level.

    Returns:
        Markdown-formatted diagnostic summary string.
    """
    if not field_notes:
        return "No field notes available for this session."

    # Build the input for GPT
    notes_text = []
    for i, note in enumerate(field_notes, 1):
        category = note.get("primary_category", "uncategorized")
        secondary = note.get("secondary_category")
        tags = ", ".join(note.get("tags", []))
        conf = note.get("confidence", 0)
        lang = note.get("language", "en")

        entry = f"**Note {i}** [Category: {category}"
        if secondary:
            entry += f" | Secondary: {secondary}"
        entry += f" | Tags: {tags} | Confidence: {conf}% | Language: {lang}]"
        entry += f"\n\"{note['anonymized_text']}\""
        notes_text.append(entry)

    user_message = f"""## Participant Profile
- Code: {participant_info.get('participant_code', 'N/A')}
- Department: {participant_info.get('department', 'N/A')}
- Role Level: {participant_info.get('role_level', 'N/A')}
- Total Notes: {len(field_notes)}

## Anonymized Field Notes

{chr(10).join(notes_text)}

---
Please produce the structured diagnostic brief now."""

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,  # Lower temperature for more consistent output
            max_tokens=2000,
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        return f"Error generating summary: {str(e)}"
