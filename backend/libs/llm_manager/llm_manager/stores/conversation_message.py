"""Database store for LLM conversation messages."""

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy import asc
from sqlalchemy.sql import Select

from llm_manager.blueprints.conversation_message import (
    LLMConversationMessageCreateRequest,
    LLMConversationMessageEntity,
    LLMConversationMessageModel,
    LLMConversationMessageQuery,
    LLMConversationMessageUpdateRequest,
)
from llm_manager.conversation.conversation import LLMConversationStore
from llm_manager.schemas.messages import LLMMessage, LLMMessagePayload, LLMRole


class LLMConversationMessageStore(
    BaseEntityStore[
        LLMConversationMessageModel,
        LLMConversationMessageEntity,
        LLMConversationMessageQuery,
        LLMConversationMessageCreateRequest,
        LLMConversationMessageUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    """Database store for conversation messages using BaseEntityStore."""

    entity_model = LLMConversationMessageModel
    entity = LLMConversationMessageEntity
    entity_query = LLMConversationMessageQuery
    entity_create_request = LLMConversationMessageCreateRequest
    entity_update_request = LLMConversationMessageUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self,
        query: LLMConversationMessageQuery,
        stmt: Select[tuple[LLMConversationMessageModel]],
    ) -> Select[tuple[LLMConversationMessageModel]]:
        if query.conversation_id:
            stmt = stmt.filter(LLMConversationMessageModel.conversation_id == query.conversation_id)
        if query.user_id:
            stmt = stmt.filter(LLMConversationMessageModel.user_id == query.user_id)
        if query.role:
            stmt = stmt.filter(LLMConversationMessageModel.role == query.role)
        # Always order by id ascending to maintain message order
        stmt = stmt.order_by(asc(LLMConversationMessageModel.id))
        return stmt


class LLMDatabaseStore(LLMConversationStore):
    """Implements LLMConversationStore using the database via LLMConversationMessageStore."""

    def __init__(self) -> None:
        self._message_store = LLMConversationMessageStore()

    def _entity_to_message(self, entity: LLMConversationMessageEntity) -> LLMMessage:
        """Convert database entity to LLMMessage."""
        return LLMMessage(
            role=LLMRole(entity.role),
            content=entity.content,
            payload=LLMMessagePayload.model_validate(entity.payload),
        )

    def _message_to_create_request(
        self, conversation_id: str, message: LLMMessage, user_id: str | None = None
    ) -> LLMConversationMessageCreateRequest:
        """Convert LLMMessage to create request."""
        return LLMConversationMessageCreateRequest(
            conversation_id=conversation_id,
            user_id=user_id,
            role=message.role.value,
            content=message.content,
            payload=message.payload.model_dump(),
        )

    async def load(self, conversation_id: str) -> list[LLMMessage]:
        """Load messages for a conversation."""
        query = LLMConversationMessageQuery(
            conversation_id=conversation_id,
            limit=10000,  # High limit to get all messages
        )
        result = await self._message_store.search_entities(query)
        return [self._entity_to_message(entity) for entity in result.entities]

    async def append(self, conversation_id: str, message: LLMMessage) -> None:
        """Append a single message to a conversation."""
        request = self._message_to_create_request(conversation_id, message)
        await self._message_store.create_entity(request)

    async def append_many(self, conversation_id: str, messages: list[LLMMessage]) -> None:
        """Append multiple messages to a conversation."""
        for message in messages:
            await self.append(conversation_id, message)

    async def delete(self, conversation_id: str) -> None:
        """Delete all messages in a conversation."""
        query = LLMConversationMessageQuery(
            conversation_id=conversation_id,
            limit=10000,
        )
        result = await self._message_store.search_entities(query)
        for entity in result.entities:
            await self._message_store.delete_entity(BaseEntityDeleteRequest(id=entity.id))

    async def list_conversations(self, user_id: str | None = None) -> list[str]:
        """List all conversation IDs, optionally filtered by user."""
        query = LLMConversationMessageQuery(
            user_id=user_id,
            limit=10000,
        )
        result = await self._message_store.search_entities(query)
        # Get unique conversation IDs
        conversation_ids = list({entity.conversation_id for entity in result.entities})
        return conversation_ids


llm_conversation_message_store = LLMConversationMessageStore()
llm_database_store = LLMDatabaseStore()
