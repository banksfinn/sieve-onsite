"""Recurrence pattern extraction using LLM."""

import json
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel

from app.llm.prompts.recurrence_extractor import RECURRENCE_EXTRACTOR_PROMPT
from llm_manager.clients.provider_base import LLMProvider
from llm_manager.schemas.messages import LLMMessage


RecurrenceType = Literal["fixed_schedule", "from_completion"]


class RecurrenceExtractionResult(BaseModel):
    """Result of recurrence pattern extraction."""

    recurrence_rule: str | None = None
    recurrence_type: RecurrenceType | None = None
    recurrence_start: datetime | None = None
    recurrence_end: datetime | None = None


async def extract_recurrence(
    provider: LLMProvider,
    text: str,
    time_expressions: list[str] | None = None,
    current_time: datetime | None = None,
) -> RecurrenceExtractionResult:
    """Extract recurrence pattern from natural language text.

    Args:
        provider: LLM provider to use for extraction
        text: The text to extract recurrence from
        time_expressions: Already extracted time expressions (from due date extraction)
        current_time: Current time for reference (defaults to now)

    Returns:
        RecurrenceExtractionResult with extracted recurrence information
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    time_expr_str = ""
    if time_expressions:
        time_expr_str = f"\nAlready extracted time expressions: {time_expressions}"

    user_message = f"""Current date/time: {current_time.isoformat()}
{time_expr_str}

Extract recurrence pattern from this task description:
"{text}"

Respond with only the JSON object, no other text."""

    messages = [LLMMessage.user(user_message)]

    response = await provider.chat(
        messages=messages,
        system=RECURRENCE_EXTRACTOR_PROMPT,
        temperature=0.0,  # Deterministic for extraction
    )

    # Parse the response
    try:
        content = response.content or "{}"
        # Handle markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content.strip())

        recurrence_type = data.get("recurrence_type")
        if recurrence_type not in ("fixed_schedule", "from_completion"):
            recurrence_type = None

        return RecurrenceExtractionResult(
            recurrence_rule=data.get("recurrence_rule"),
            recurrence_type=recurrence_type,
            recurrence_start=_parse_datetime(data.get("recurrence_start")),
            recurrence_end=_parse_datetime(data.get("recurrence_end")),
        )
    except (json.JSONDecodeError, KeyError):
        # If parsing fails, return empty result
        return RecurrenceExtractionResult()


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO datetime string."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None
