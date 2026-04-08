"""Conversation history management."""

import uuid
from abc import ABC, abstractmethod

from llm_manager.schemas.messages import LLMMessage


class LLMConversationStore(ABC):
    """Abstract base class for conversation persistence."""

    @abstractmethod
    async def load(self, conversation_id: str) -> list[LLMMessage]: ...

    @abstractmethod
    async def append(self, conversation_id: str, message: LLMMessage) -> None: ...

    @abstractmethod
    async def append_many(self, conversation_id: str, messages: list[LLMMessage]) -> None: ...

    @abstractmethod
    async def delete(self, conversation_id: str) -> None: ...

    @abstractmethod
    async def list_conversations(self, user_id: str | None = None) -> list[str]: ...


class LLMInMemoryStore(LLMConversationStore):
    """In-memory conversation store for development and testing."""

    def __init__(self) -> None:
        self._conversations: dict[str, list[LLMMessage]] = {}
        self._user_conversations: dict[str, set[str]] = {}

    async def load(self, conversation_id: str) -> list[LLMMessage]:
        return list(self._conversations.get(conversation_id, []))

    async def append(self, conversation_id: str, message: LLMMessage) -> None:
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        self._conversations[conversation_id].append(message)

    async def append_many(self, conversation_id: str, messages: list[LLMMessage]) -> None:
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        self._conversations[conversation_id].extend(messages)

    async def delete(self, conversation_id: str) -> None:
        self._conversations.pop(conversation_id, None)
        for user_convos in self._user_conversations.values():
            user_convos.discard(conversation_id)

    async def list_conversations(self, user_id: str | None = None) -> list[str]:
        if user_id is not None:
            return list(self._user_conversations.get(user_id, set()))
        return list(self._conversations.keys())

    def associate_user(self, conversation_id: str, user_id: str) -> None:
        if user_id not in self._user_conversations:
            self._user_conversations[user_id] = set()
        self._user_conversations[user_id].add(conversation_id)


class LLMConversation:
    """Manages conversation history with optional persistence."""

    def __init__(
        self,
        id: str | None = None,
        store: LLMConversationStore | None = None,
    ) -> None:
        self.id = id or str(uuid.uuid4())
        self._store = store
        self._messages: list[LLMMessage] = []
        self._loaded = False

    async def load(self) -> None:
        if self._store and not self._loaded:
            self._messages = await self._store.load(self.id)
            self._loaded = True

    async def append(self, message: LLMMessage) -> None:
        self._messages.append(message)
        if self._store:
            await self._store.append(self.id, message)

    async def append_many(self, messages: list[LLMMessage]) -> None:
        self._messages.extend(messages)
        if self._store:
            await self._store.append_many(self.id, messages)

    @property
    def messages(self) -> list[LLMMessage]:
        return list(self._messages)

    def get_recent(self, n: int) -> list[LLMMessage]:
        return self._messages[-n:] if n > 0 else []

    async def clear(self) -> None:
        self._messages = []
        if self._store:
            await self._store.delete(self.id)

    def __len__(self) -> int:
        return len(self._messages)
