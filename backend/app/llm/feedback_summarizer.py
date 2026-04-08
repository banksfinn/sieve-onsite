"""LLM-powered summarization of clip feedback for a delivery."""

from pydantic import BaseModel, SecretStr

from llm_manager.clients.openai_client import OpenAIProvider
from llm_manager.schemas.config import LLMProviderConfig
from llm_manager.schemas.messages import LLMMessage

from app.blueprints.clip_feedback import ClipFeedback
from app.config import settings

SYSTEM_PROMPT = """You are a video dataset quality analyst at Sieve. Your job is to summarize clip-level feedback from customers reviewing video samples.

Given a list of clip feedback entries (each with a rating, optional comment, optional timestamp, and optional metadata field), produce a structured summary that helps researchers quickly understand:

1. **Overall Sentiment**: What proportion of clips were rated good/bad/unsure?
2. **Key Issues**: What are the most common problems reported? Group by theme (e.g., face detection issues, overlay problems, clip duration concerns).
3. **Metadata-Specific Feedback**: If feedback targets specific metadata fields (avg_face_size, max_num_faces, is_full_body, has_overlay), highlight patterns.
4. **Actionable Recommendations**: Based on the feedback patterns, what should researchers prioritize fixing in the next dataset version?

Be concise and specific. Use bullet points. Reference clip counts where relevant."""


class FeedbackSummary(BaseModel):
    delivery_id: int
    total_feedback_count: int
    summary: str


async def summarize_delivery_feedback(delivery_id: int, feedback_items: list[ClipFeedback]) -> FeedbackSummary:
    """Summarize clip feedback for a delivery using the LLM."""
    if not feedback_items:
        return FeedbackSummary(
            delivery_id=delivery_id,
            total_feedback_count=0,
            summary="No feedback has been submitted for this delivery yet.",
        )

    feedback_text = _format_feedback_for_llm(feedback_items)

    config = LLMProviderConfig(
        api_key=SecretStr(settings.OPENAI_API_KEY),
        model="gpt-4o",
    )
    provider = OpenAIProvider(config)

    messages = [LLMMessage.user(feedback_text)]
    response = await provider.chat(
        messages=messages,
        system=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=1500,
    )

    return FeedbackSummary(
        delivery_id=delivery_id,
        total_feedback_count=len(feedback_items),
        summary=response.content or "Unable to generate summary.",
    )


def _format_feedback_for_llm(feedback_items: list[ClipFeedback]) -> str:
    """Format feedback entries into a text block for the LLM."""
    lines = [f"Feedback for delivery with {len(feedback_items)} clip reviews:\n"]

    for fb in feedback_items:
        parts = [f"- Clip #{fb.clip_id}: rating={fb.rating.value}"]
        if fb.comment:
            parts.append(f'comment="{fb.comment}"')
        if fb.timestamp is not None:
            parts.append(f"at timestamp={fb.timestamp:.1f}s")
        if fb.metadata_field:
            parts.append(f"re: {fb.metadata_field}")
        if fb.is_resolved:
            parts.append("(resolved)")
        lines.append(", ".join(parts))

    return "\n".join(lines)
