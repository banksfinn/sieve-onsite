"""Due date extraction using LLM."""

import json
from datetime import datetime, timezone

from pydantic import BaseModel

from app.llm.prompts.due_date_extractor import DUE_DATE_EXTRACTOR_PROMPT
from llm_manager.clients.provider_base import LLMProvider
from llm_manager.schemas.messages import LLMMessage


class DueDateExtractionResult(BaseModel):
    """Result of due date extraction."""

    due_date: datetime | None = None
    start_date: datetime | None = None
    time_expressions: list[str] = []
    has_recurrence_signal: bool = False


async def extract_due_date(
    provider: LLMProvider,
    text: str,
    current_time: datetime | None = None,
    user_timezone: str | None = None,
) -> DueDateExtractionResult:
    """Extract due date information from natural language text.

    Args:
        provider: LLM provider to use for extraction
        text: The text to extract dates from
        current_time: Current time for reference (defaults to now)
        user_timezone: User's IANA timezone (e.g., 'America/New_York') for interpreting times

    Returns:
        DueDateExtractionResult with extracted date information
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    # Build context with timezone info
    timezone_info = ""
    if user_timezone:
        try:
            import zoneinfo

            tz = zoneinfo.ZoneInfo(user_timezone)
            local_time = current_time.astimezone(tz)
            timezone_info = f"\nUser's timezone: {user_timezone}\nLocal time in user's timezone: {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        except Exception:
            # Invalid timezone, proceed without local time
            timezone_info = f"\nUser's timezone: {user_timezone}"

    # Include current time and timezone in the prompt for correct date calculation
    user_message = f"""Current date/time (UTC): {current_time.isoformat()}{timezone_info}

Extract date/time information from this task description:
"{text}"

Respond with only the JSON object, no other text."""

    messages = [LLMMessage.user(user_message)]

    response = await provider.chat(
        messages=messages,
        system=DUE_DATE_EXTRACTOR_PROMPT,
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

        return DueDateExtractionResult(
            due_date=_parse_datetime(data.get("due_date")),
            start_date=_parse_datetime(data.get("start_date")),
            time_expressions=data.get("time_expressions", []),
            has_recurrence_signal=data.get("has_recurrence_signal", False),
        )
    except (json.JSONDecodeError, KeyError):
        # If parsing fails, return empty result
        return DueDateExtractionResult()


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO datetime string."""
    if not value:
        return None
    try:
        # Handle various formats
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None
