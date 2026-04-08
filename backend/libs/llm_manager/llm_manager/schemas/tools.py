"""Tool-related types for the LLM manager library."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LLMToolDefinition(BaseModel):
    """Schema definition for a tool."""

    name: str = Field(..., description="Unique name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    parameters: dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}, "required": []},
        description="JSON Schema for the tool's parameters",
    )


class LLMToolContext(BaseModel):
    """Context passed to tool handlers during execution."""

    model_config = ConfigDict(extra="allow")

    conversation_id: str | None = Field(default=None, description="ID of the current conversation")
    user_id: str | None = Field(default=None, description="ID of the current user")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the tool")
