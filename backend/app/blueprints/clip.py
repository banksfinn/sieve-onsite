from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import clip_table_name
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ClipModel(BaseEntityModel):
    __tablename__ = clip_table_name

    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.id"), nullable=False)
    dataset_version_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset_versions.id"), nullable=False)
    uri: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    avg_face_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_num_faces: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_full_body: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_overlay: Mapped[bool | None] = mapped_column(Boolean, nullable=True)


class Clip(BaseEntity):
    video_id: int
    dataset_version_id: int
    uri: str
    start_time: float
    end_time: float
    duration: float
    avg_face_size: float | None = None
    max_num_faces: int | None = None
    is_full_body: bool | None = None
    has_overlay: bool | None = None


class ClipCreateRequest(BaseEntityCreateRequest):
    video_id: int
    dataset_version_id: int
    uri: str
    start_time: float
    end_time: float
    duration: float
    avg_face_size: float | None = None
    max_num_faces: int | None = None
    is_full_body: bool | None = None
    has_overlay: bool | None = None


class ClipUpdateRequest(BaseEntityUpdateRequest):
    avg_face_size: float | None = None
    max_num_faces: int | None = None
    is_full_body: bool | None = None
    has_overlay: bool | None = None


class ClipQuery(BaseEntityQuery):
    video_id: int | None = None
    dataset_version_id: int | None = None
