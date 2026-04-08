"""Generic provider input/output types for SDK isolation."""

from typing import Any

from pydantic import BaseModel, Field


class ProviderToolCallFunction(BaseModel):
    name: str
    arguments: str  # JSON string


class ProviderToolCall(BaseModel):
    id: str
    type: str = "function"
    function: ProviderToolCallFunction


class ProviderMessage(BaseModel):
    role: str
    content: str | None = None
    tool_calls: list[ProviderToolCall] | None = None
    tool_call_id: str | None = None


class ProviderToolFunction(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ProviderTool(BaseModel):
    type: str = "function"
    function: ProviderToolFunction


class ProviderChatRequest(BaseModel):
    model: str
    messages: list[ProviderMessage]
    tools: list[ProviderTool] | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False


class ProviderChatResponse(BaseModel):
    content: str | None = None
    tool_calls: list[ProviderToolCall] | None = None
    finish_reason: str | None = None
