"""Abstract base class for tool implementations."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from llm_manager.schemas.tools import LLMToolContext, LLMToolDefinition

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT")


class LLMToolHandler(ABC, Generic[InputT, OutputT]):
    """Abstract base class for tool implementations."""

    @property
    @abstractmethod
    def definition(self) -> LLMToolDefinition:
        """Return the tool's definition."""
        ...

    @property
    def input_model(self) -> type[InputT] | None:
        """Optional Pydantic model for input validation.

        If provided, arguments will be validated against this model before execution.
        """
        return None

    @abstractmethod
    async def execute(self, input: InputT | dict[str, Any], context: LLMToolContext) -> OutputT:
        """Execute the tool with the given input and context.

        Args:
            input: The validated input (if input_model is set) or raw arguments dict
            context: Execution context with conversation and user info

        Returns:
            The tool's output, which will be serialized to string for the LLM
        """
        ...
