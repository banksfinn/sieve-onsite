from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import delivery_feedback_table_name
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.schemas.enums import DeliveryFeedbackStatus


class DeliveryFeedbackModel(BaseEntityModel):
    __tablename__ = delivery_feedback_table_name

    delivery_id: Mapped[int] = mapped_column(Integer, ForeignKey("deliveries.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class DeliveryFeedback(BaseEntity):
    delivery_id: int
    user_id: int
    status: DeliveryFeedbackStatus
    summary: str | None = None


class DeliveryFeedbackCreateRequest(BaseEntityCreateRequest):
    delivery_id: int
    user_id: int
    status: DeliveryFeedbackStatus
    summary: str | None = None


class DeliveryFeedbackUpdateRequest(BaseEntityUpdateRequest):
    status: DeliveryFeedbackStatus | None = None
    summary: str | None = None


class DeliveryFeedbackQuery(BaseEntityQuery):
    delivery_id: int | None = None
    user_id: int | None = None
