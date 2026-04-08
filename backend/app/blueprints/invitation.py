from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import invitation_table_name
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class InvitationModel(BaseEntityModel):
    __tablename__ = invitation_table_name

    email_address: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="customer")
    access_level: Mapped[str] = mapped_column(String, nullable=False, default="regular")
    invited_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Invitation(BaseEntity):
    email_address: str
    role: str
    access_level: str
    invited_by: int
    accepted: bool = False


class InvitationCreateRequest(BaseEntityCreateRequest):
    email_address: str
    role: str = "customer"
    access_level: str = "regular"


class InvitationUpdateRequest(BaseEntityUpdateRequest):
    accepted: bool | None = None


class InvitationQuery(BaseEntityQuery):
    email_address: str | None = None
    accepted: bool | None = None
