from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import video_table_name
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class VideoModel(BaseEntityModel):
    __tablename__ = video_table_name

    delivery_id: Mapped[str] = mapped_column(String, nullable=False)
    uri: Mapped[str] = mapped_column(String, nullable=False)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str | None] = mapped_column(String, nullable=True)


class Video(BaseEntity):
    delivery_id: str
    uri: str
    fps: float | None = None
    height: int | None = None
    width: int | None = None
    source: str | None = None
    language: str | None = None


class VideoCreateRequest(BaseEntityCreateRequest):
    delivery_id: str
    uri: str
    fps: float | None = None
    height: int | None = None
    width: int | None = None
    source: str | None = None
    language: str | None = None


class VideoUpdateRequest(BaseEntityUpdateRequest):
    fps: float | None = None
    height: int | None = None
    width: int | None = None
    source: str | None = None
    language: str | None = None


class VideoQuery(BaseEntityQuery):
    delivery_id: str | None = None
    source: str | None = None
    language: str | None = None
