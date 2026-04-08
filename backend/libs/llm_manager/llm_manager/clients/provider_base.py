"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from llm_manager.schemas.config import LLMProviderConfig
from llm_manager.schemas.messages import LLMMessage
from llm_manager.schemas.provider import ProviderChatRequest, ProviderChatResponse
from llm_manager.schemas.tools import LLMToolDefinition


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMProviderConfig):
        """Initialize the provider with configuration."""
        self.config = config

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        tools: list[LLMToolDefinition] | None = None,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> LLMMessage:
        """Send a chat completion request.

        Args:
            messages: List of conversation messages
            tools: Optional list of tool definitions
            system: Optional system prompt
            temperature: Optional temperature for sampling
            max_tokens: Optional maximum tokens in response
            model: Optional model override

        Returns:
            The assistant's response message
        """
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[LLMMessage],
        tools: list[LLMToolDefinition] | None = None,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> AsyncIterator[LLMMessage]:
        """Send a streaming chat completion request.

        Yields:
            Partial response messages as they arrive
        """
        ...
        if False:
            yield LLMMessage.assistant()

    @abstractmethod
    def build_request(
        self,
        messages: list[LLMMessage],
        tools: list[LLMToolDefinition] | None,
        system: str | None,
        temperature: float | None,
        max_tokens: int | None,
        model: str | None,
        stream: bool,
    ) -> ProviderChatRequest:
        """Build a provider-agnostic chat request."""
        ...

    @abstractmethod
    def parse_response(self, response: ProviderChatResponse) -> LLMMessage:
        """Parse a provider response into an LLMMessage."""
        ...
