from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import user_table_name
from pydantic import EmailStr
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(BaseEntityModel):
    __tablename__ = user_table_name

    email_address: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="customer")
    access_level: Mapped[str] = mapped_column(String, default="regular")


class User(BaseEntity):
    email_address: EmailStr
    name: str
    role: str = "customer"
    access_level: str = "regular"


class UserCreateRequest(BaseEntityCreateRequest):
    email_address: EmailStr
    name: str
    role: str = "customer"
    access_level: str = "regular"


class UserUpdateRequest(BaseEntityUpdateRequest):
    role: str | None = None
    access_level: str | None = None


class UserQuery(BaseEntityQuery):
    email_address: EmailStr | None = None
    role: str | None = None
