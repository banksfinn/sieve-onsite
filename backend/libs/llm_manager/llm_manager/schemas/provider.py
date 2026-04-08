"""Generic provider input/output types for SDK isolation.

These types provide a clean interface between the LLM manager and provider SDKs.
Provider implementations convert to/from these types at the boundary.
"""

from typing import Any

from pydantic import BaseModel, Field


class ProviderToolCallFunction(BaseModel):
    """Function details within a tool call."""

    name: str
    arguments: str  # JSON string


class ProviderToolCall(BaseModel):
    """Generic representation of a tool call from any provider."""

    id: str
    type: str = "function"
    function: ProviderToolCallFunction


class ProviderMessage(BaseModel):
    """Generic representation of a chat message for any provider."""

    role: str
    content: str | None = None
    tool_calls: list[ProviderToolCall] | None = None
    tool_call_id: str | None = None  # For tool result messages


class ProviderToolFunction(BaseModel):
    """Function definition within a tool."""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ProviderTool(BaseModel):
    """Generic representation of a tool definition for any provider."""

    type: str = "function"
    function: ProviderToolFunction


class ProviderChatRequest(BaseModel):
    """Generic chat completion request."""

    model: str
    messages: list[ProviderMessage]
    tools: list[ProviderTool] | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False


class ProviderChatResponse(BaseModel):
    """Generic chat completion response."""

    content: str | None = None
    tool_calls: list[ProviderToolCall] | None = None
    finish_reason: str | None = None
