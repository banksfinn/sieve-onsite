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

    id: str = Field(...)
    name: str = Field(...)
    arguments: dict[str, Any] = Field(default_factory=dict)


class LLMToolResult(BaseModel):
    """Result of executing a tool."""

    tool_call_id: str = Field(...)
    content: str = Field(...)
    is_error: bool = Field(default=False)


class LLMMessagePayload(BaseModel):
    """Complex payload data stored as JSONB."""

    tool_calls: list[LLMToolCall] | None = None
    tool_results: list[LLMToolResult] | None = None


class LLMMessage(BaseModel):
    """A message in a conversation."""

    role: LLMRole = Field(...)
    content: str | None = Field(default=None)
    payload: LLMMessagePayload = Field(default_factory=LLMMessagePayload)

    @property
    def tool_calls(self) -> list[LLMToolCall] | None:
        return self.payload.tool_calls

    @property
    def tool_results(self) -> list[LLMToolResult] | None:
        return self.payload.tool_results

    @classmethod
    def user(cls, content: str) -> "LLMMessage":
        return cls(role=LLMRole.user, content=content)

    @classmethod
    def assistant(cls, content: str | None = None, tool_calls: list[LLMToolCall] | None = None) -> "LLMMessage":
        return cls(
            role=LLMRole.assistant,
            content=content,
            payload=LLMMessagePayload(tool_calls=tool_calls),
        )

    @classmethod
    def tool_result(cls, results: list[LLMToolResult]) -> "LLMMessage":
        return cls(
            role=LLMRole.tool_result,
            payload=LLMMessagePayload(tool_results=results),
        )
