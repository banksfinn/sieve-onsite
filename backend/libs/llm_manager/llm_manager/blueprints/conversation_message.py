"""Database models for LLM conversation messages."""

from typing import Any

from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import llm_conversation_message_table_name
from pydantic import Field
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class LLMConversationMessageModel(BaseEntityModel):
    """SQLAlchemy model for LLM conversation messages."""

    __tablename__ = llm_conversation_message_table_name

    conversation_id: Mapped[str] = mapped_column(String, index=True)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str | None] = mapped_column(String, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class LLMConversationMessageEntity(BaseEntity):
    """Pydantic entity for LLM conversation messages."""

    conversation_id: str
    user_id: str | None = None
    role: str
    content: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class LLMConversationMessageCreateRequest(BaseEntityCreateRequest):
    """Request to create a conversation message."""

    conversation_id: str
    user_id: str | None = None
    role: str
    content: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class LLMConversationMessageUpdateRequest(BaseEntityUpdateRequest):
    """Request to update a conversation message."""

    pass


class LLMConversationMessageQuery(BaseEntityQuery):
    """Query for conversation messages."""

    conversation_id: str | None = None
    user_id: str | None = None
    role: str | None = None
