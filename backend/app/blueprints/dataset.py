from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import (
    dataset_table_name,
    dataset_version_table_name,
    dataset_version_video_table_name,
)
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.schemas.enums import DatasetStatus


class DatasetModel(BaseEntityModel):
    __tablename__ = dataset_table_name

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default=DatasetStatus.requested.value)
    bucket_path: Mapped[str | None] = mapped_column(String, nullable=True)


class Dataset(BaseEntity):
    name: str
    description: str | None = None
    status: str = DatasetStatus.requested.value
    bucket_path: str | None = None


class DatasetCreateRequest(BaseEntityCreateRequest):
    name: str
    description: str | None = None
    bucket_path: str | None = None


class DatasetUpdateRequest(BaseEntityUpdateRequest):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    bucket_path: str | None = None


class DatasetQuery(BaseEntityQuery):
    name: str | None = None
    status: str | None = None


class DatasetVersionModel(BaseEntityModel):
    __tablename__ = dataset_version_table_name

    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_version_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dataset_versions.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)


class DatasetVersion(BaseEntity):
    dataset_id: int
    version_number: int
    parent_version_id: int | None = None
    created_by: int


class DatasetVersionCreateRequest(BaseEntityCreateRequest):
    dataset_id: int
    version_number: int
    parent_version_id: int | None = None
    created_by: int


class DatasetVersionUpdateRequest(BaseEntityUpdateRequest):
    pass


class DatasetVersionQuery(BaseEntityQuery):
    dataset_id: int | None = None


class DatasetVersionVideoModel(BaseEntityModel):
    __tablename__ = dataset_version_video_table_name

    dataset_version_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset_versions.id"), nullable=False)
    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.id"), nullable=False)


class DatasetVersionVideo(BaseEntity):
    dataset_version_id: int
    video_id: int


class DatasetVersionVideoCreateRequest(BaseEntityCreateRequest):
    dataset_version_id: int
    video_id: int


class DatasetVersionVideoQuery(BaseEntityQuery):
    dataset_version_id: int | None = None
