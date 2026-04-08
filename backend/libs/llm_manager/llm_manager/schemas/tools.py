"""Tool-related types for the LLM manager library."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LLMToolDefinition(BaseModel):
    """Schema definition for a tool."""

    name: str = Field(...)
    description: str = Field(...)
    parameters: dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}, "required": []},
    )


class LLMToolContext(BaseModel):
    """Context passed to tool handlers during execution."""

    model_config = ConfigDict(extra="allow")

    conversation_id: str | None = Field(default=None)
    user_id: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
