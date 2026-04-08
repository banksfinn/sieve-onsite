from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import delivery_access_table_name
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.schemas.enums import DeliveryAccessRole


class DeliveryAccessModel(BaseEntityModel):
    __tablename__ = delivery_access_table_name

    delivery_id: Mapped[int] = mapped_column(Integer, ForeignKey("deliveries.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default=DeliveryAccessRole.viewer.value)


class DeliveryAccess(BaseEntity):
    delivery_id: int
    user_id: int
    role: DeliveryAccessRole = DeliveryAccessRole.viewer


class DeliveryAccessCreateRequest(BaseEntityCreateRequest):
    delivery_id: int
    user_id: int
    role: DeliveryAccessRole = DeliveryAccessRole.viewer


class DeliveryAccessUpdateRequest(BaseEntityUpdateRequest):
    role: DeliveryAccessRole | None = None


class DeliveryAccessQuery(BaseEntityQuery):
    delivery_id: int | None = None
    user_id: int | None = None
