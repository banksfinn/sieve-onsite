from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import dataset_assignment_table_name
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class DatasetAssignmentModel(BaseEntityModel):
    __tablename__ = dataset_assignment_table_name

    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)


class DatasetAssignment(BaseEntity):
    dataset_id: int
    user_id: int
    role: str


class DatasetAssignmentCreateRequest(BaseEntityCreateRequest):
    dataset_id: int
    user_id: int
    role: str


class DatasetAssignmentUpdateRequest(BaseEntityUpdateRequest):
    role: str | None = None


class DatasetAssignmentQuery(BaseEntityQuery):
    dataset_id: int | None = None
    user_id: int | None = None
    role: str | None = None
