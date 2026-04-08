"""Core message types for LLM conversations."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LLMRole(str, Enum):
    """Role of a message in a conversation."""

    user = "user"
    assistant = "assistant"
    tool_result = "tool_result"


class LLMToolCall(BaseModel):
    """Represents an LLM's request to invoke a tool."""

    id: str = Field(..., description="Unique identifier for this tool call")
    name: str = Field(..., description="Name of the tool to invoke")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to the tool")


class LLMToolResult(BaseModel):
    """Result of executing a tool."""

    tool_call_id: str = Field(..., description="ID of the tool call this is a result for")
    content: str = Field(..., description="The result content")
    is_error: bool = Field(default=False, description="Whether this result represents an error")


class LLMMessagePayload(BaseModel):
    """Complex payload data stored as JSONB."""

    tool_calls: list[LLMToolCall] | None = None
    tool_results: list[LLMToolResult] | None = None


class LLMMessage(BaseModel):
    """A message in a conversation."""

    role: LLMRole = Field(..., description="Role of this message")
    content: str | None = Field(default=None, description="Text content of the message")
    payload: LLMMessagePayload = Field(default_factory=LLMMessagePayload, description="Complex payload data")

    @property
    def tool_calls(self) -> list[LLMToolCall] | None:
        """Get tool calls from payload."""
        return self.payload.tool_calls

    @property
    def tool_results(self) -> list[LLMToolResult] | None:
        """Get tool results from payload."""
        return self.payload.tool_results

    @classmethod
    def user(cls, content: str) -> "LLMMessage":
        """Create a user message."""
        return cls(role=LLMRole.user, content=content)

    @classmethod
    def assistant(cls, content: str | None = None, tool_calls: list[LLMToolCall] | None = None) -> "LLMMessage":
        """Create an assistant message."""
        return cls(
            role=LLMRole.assistant,
            content=content,
            payload=LLMMessagePayload(tool_calls=tool_calls),
        )

    @classmethod
    def tool_result(cls, results: list[LLMToolResult]) -> "LLMMessage":
        """Create a tool result message."""
        return cls(
            role=LLMRole.tool_result,
            payload=LLMMessagePayload(tool_results=results),
        )
