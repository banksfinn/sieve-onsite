from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import clip_feedback_table_name
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.schemas.enums import ClipRating


class ClipFeedbackModel(BaseEntityModel):
    __tablename__ = clip_feedback_table_name

    clip_id: Mapped[int] = mapped_column(Integer, ForeignKey("clips.id"), nullable=False)
    delivery_id: Mapped[int] = mapped_column(Integer, ForeignKey("deliveries.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    rating: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class ClipFeedback(BaseEntity):
    clip_id: int
    delivery_id: int
    user_id: int
    rating: ClipRating
    comment: str | None = None


class ClipFeedbackCreateRequest(BaseEntityCreateRequest):
    clip_id: int
    delivery_id: int
    user_id: int
    rating: ClipRating
    comment: str | None = None


class ClipFeedbackUpdateRequest(BaseEntityUpdateRequest):
    rating: ClipRating | None = None
    comment: str | None = None


class ClipFeedbackQuery(BaseEntityQuery):
    clip_id: int | None = None
    delivery_id: int | None = None
    user_id: int | None = None
