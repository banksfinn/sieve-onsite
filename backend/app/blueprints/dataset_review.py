from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import (
    dataset_review_table_name,
    dataset_review_reply_table_name,
)
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.schemas.enums import ReviewStatus, ReviewType


# --- DatasetReview ---


class DatasetReviewModel(BaseEntityModel):
    __tablename__ = dataset_review_table_name

    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"), nullable=False)
    dataset_version_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset_versions.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    review_type: Mapped[str] = mapped_column(String, nullable=False)
    clip_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clips.id"), nullable=True)
    clip_timestamp: Mapped[float | None] = mapped_column(Float, nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default=ReviewStatus.open.value)
    resolved_in_version_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("dataset_versions.id"), nullable=True
    )


class DatasetReview(BaseEntity):
    dataset_id: int
    dataset_version_id: int
    user_id: int
    review_type: ReviewType
    clip_id: int | None = None
    clip_timestamp: float | None = None
    comment: str
    status: ReviewStatus = ReviewStatus.open
    resolved_in_version_id: int | None = None


class DatasetReviewCreateRequest(BaseEntityCreateRequest):
    dataset_id: int
    dataset_version_id: int
    user_id: int
    review_type: ReviewType
    clip_id: int | None = None
    clip_timestamp: float | None = None
    comment: str


class DatasetReviewUpdateRequest(BaseEntityUpdateRequest):
    status: ReviewStatus | None = None
    resolved_in_version_id: int | None = None


class DatasetReviewQuery(BaseEntityQuery):
    dataset_id: int | None = None
    dataset_version_id: int | None = None
    clip_id: int | None = None
    user_id: int | None = None
    status: ReviewStatus | None = None
    review_type: ReviewType | None = None


# --- DatasetReviewReply ---


class DatasetReviewReplyModel(BaseEntityModel):
    __tablename__ = dataset_review_reply_table_name

    review_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset_reviews.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)


class DatasetReviewReply(BaseEntity):
    review_id: int
    user_id: int
    comment: str


class DatasetReviewReplyCreateRequest(BaseEntityCreateRequest):
    review_id: int
    user_id: int
    comment: str


class DatasetReviewReplyUpdateRequest(BaseEntityUpdateRequest):
    comment: str | None = None


class DatasetReviewReplyQuery(BaseEntityQuery):
    review_id: int | None = None
