from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import user_table_name
from pydantic import EmailStr
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

# Default notification timing: 30 minutes before
DEFAULT_NOTIFICATION_TIMING = '["30_minutes_before"]'


# Define a model
class UserModel(BaseEntityModel):
    __tablename__ = user_table_name

    email_address: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)

    # Notification preferences - stored as JSON string array
    # e.g., '["at_due_time", "30_minutes_before", "morning_of"]'
    notification_timing: Mapped[str | None] = mapped_column(String, nullable=True)
    notification_custom_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)


class User(BaseEntity):
    email_address: EmailStr
    name: str
    notification_timing: list[str] | None = None
    notification_custom_minutes: int | None = None


class UserCreateRequest(BaseEntityCreateRequest):
    email_address: EmailStr
    name: str


class UserUpdateRequest(BaseEntityUpdateRequest):
    notification_timing: list[str] | None = None
    notification_custom_minutes: int | None = None


class UserQuery(BaseEntityQuery):
    email_address: EmailStr | None = None
