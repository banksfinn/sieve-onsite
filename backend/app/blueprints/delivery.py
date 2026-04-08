from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import delivery_table_name
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.schemas.enums import DeliveryStatus


class DeliveryModel(BaseEntityModel):
    __tablename__ = delivery_table_name

    dataset_version_id: Mapped[int] = mapped_column(Integer, ForeignKey("dataset_versions.id"), nullable=False)
    customer_request_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default=DeliveryStatus.draft.value)


class Delivery(BaseEntity):
    dataset_version_id: int
    customer_request_description: str | None = None
    created_by: int
    status: DeliveryStatus = DeliveryStatus.draft


class DeliveryCreateRequest(BaseEntityCreateRequest):
    dataset_version_id: int
    customer_request_description: str | None = None
    created_by: int
    status: DeliveryStatus = DeliveryStatus.draft


class DeliveryUpdateRequest(BaseEntityUpdateRequest):
    status: DeliveryStatus | None = None
    customer_request_description: str | None = None


class DeliveryQuery(BaseEntityQuery):
    status: DeliveryStatus | None = None
    dataset_version_id: int | None = None
    created_by: int | None = None
