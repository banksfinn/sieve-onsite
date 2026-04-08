from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import clip_table_name
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class ClipModel(BaseEntityModel):
    __tablename__ = clip_table_name

    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.id"), nullable=False)
    dataset_version_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset_versions.id"), nullable=False)
    uri: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    extra_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class Clip(BaseEntity):
    video_id: int
    dataset_version_id: int
    uri: str
    start_time: float
    end_time: float
    duration: float
    extra_metadata: dict | None = None


class ClipCreateRequest(BaseEntityCreateRequest):
    video_id: int
    dataset_version_id: int
    uri: str
    start_time: float
    end_time: float
    duration: float
    extra_metadata: dict | None = None


class ClipUpdateRequest(BaseEntityUpdateRequest):
    extra_metadata: dict | None = None


class ClipQuery(BaseEntityQuery):
    video_id: int | None = None
    dataset_version_id: int | None = None
