from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import clip_feedback_table_name
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.schemas.enums import ClipRating


class ClipFeedbackModel(BaseEntityModel):
    __tablename__ = clip_feedback_table_name

    clip_id: Mapped[int] = mapped_column(Integer, ForeignKey("clips.id"), nullable=False)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"), nullable=False)
    dataset_version_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset_versions.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    rating: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Timestamp in the video where this feedback applies
    timestamp: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Which metadata field this feedback is about (e.g. "avg_face_size", "max_num_faces")
    metadata_field: Mapped[str | None] = mapped_column(String, nullable=True)
    # Which dataset version resolved this issue (null = unresolved)
    resolved_in_version_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dataset_versions.id"), nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ClipFeedback(BaseEntity):
    clip_id: int
    dataset_id: int
    dataset_version_id: int
    user_id: int
    rating: ClipRating
    comment: str | None = None
    timestamp: float | None = None
    metadata_field: str | None = None
    resolved_in_version_id: int | None = None
    is_resolved: bool = False


class ClipFeedbackCreateRequest(BaseEntityCreateRequest):
    clip_id: int
    dataset_id: int
    dataset_version_id: int
    user_id: int
    rating: ClipRating
    comment: str | None = None
    timestamp: float | None = None
    metadata_field: str | None = None


class ClipFeedbackUpdateRequest(BaseEntityUpdateRequest):
    rating: ClipRating | None = None
    comment: str | None = None
    resolved_in_version_id: int | None = None
    is_resolved: bool | None = None


class ClipFeedbackQuery(BaseEntityQuery):
    clip_id: int | None = None
    dataset_id: int | None = None
    dataset_version_id: int | None = None
    user_id: int | None = None
    is_resolved: bool | None = None
