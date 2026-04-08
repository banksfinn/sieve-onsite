"""Tag extraction using LLM."""

import json

from pydantic import BaseModel

from app.llm.prompts.tag_extractor import TAG_EXTRACTOR_PROMPT
from llm_manager.clients.provider_base import LLMProvider
from llm_manager.schemas.messages import LLMMessage


class TagExtractionResult(BaseModel):
    """Result of tag extraction."""

    tag_names: list[str] = []
    confidence: float = 0.0


async def extract_tags(
    provider: LLMProvider,
    text: str,
    available_tags: list[str],
) -> TagExtractionResult:
    """Extract relevant tags from natural language text.

    Args:
        provider: LLM provider to use for extraction
        text: The task description to match tags for
        available_tags: List of available tag names to match against

    Returns:
        TagExtractionResult with matched tag names
    """
    if not available_tags:
        return TagExtractionResult()

    user_message = f"""Available tags: {json.dumps(available_tags)}

Determine which tags are relevant for this task:
"{text}"

Respond with only the JSON object, no other text."""

    messages = [LLMMessage.user(user_message)]

    response = await provider.chat(
        messages=messages,
        system=TAG_EXTRACTOR_PROMPT,
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

        # Validate that returned tags are in the available list
        tag_names = data.get("tag_names", [])
        available_lower: dict[str, str] = {t.lower(): t for t in available_tags}
        valid_tags: list[str] = []
        for name in tag_names:
            if isinstance(name, str):
                # Match case-insensitively but return the original case
                original = available_lower.get(name.lower())
                if original:
                    valid_tags.append(original)

        return TagExtractionResult(
            tag_names=valid_tags,
            confidence=float(data.get("confidence", 0.0)),
        )
    except (json.JSONDecodeError, KeyError):
        # If parsing fails, return empty result
        return TagExtractionResult()
