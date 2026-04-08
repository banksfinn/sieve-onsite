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
    ) -> LLMMessage: ...

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
    ) -> ProviderChatRequest: ...

    @abstractmethod
    def parse_response(self, response: ProviderChatResponse) -> LLMMessage: ...
