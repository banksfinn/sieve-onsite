from __future__ import annotations

from datetime import datetime
from typing import Literal

from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import (
    notification_log_table_name,
    todo_table_name,
)
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

NotificationTimingType = Literal[
    "at_due_time",
    "15_minutes_before",
    "30_minutes_before",
    "60_minutes_before",
    "morning_of",
    "night_before",
]

RecipientType = Literal["dm", "channel"]


class NotificationLogModel(BaseEntityModel):
    """Tracks sent notifications to support multiple timing types per todo."""

    __tablename__ = notification_log_table_name

    todo_id: Mapped[int] = mapped_column(ForeignKey(todo_table_name + ".id", ondelete="CASCADE"))
    timing_type: Mapped[str] = mapped_column(String)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recipient_type: Mapped[str] = mapped_column(String)
    recipient_id: Mapped[str] = mapped_column(String)


class NotificationLog(BaseEntity):
    """Pydantic model for notification logs."""

    todo_id: int
    timing_type: str
    sent_at: datetime
    recipient_type: str
    recipient_id: str


class NotificationLogCreateRequest(BaseEntityCreateRequest):
    todo_id: int
    timing_type: str
    sent_at: datetime
    recipient_type: str
    recipient_id: str


class NotificationLogUpdateRequest(BaseEntityUpdateRequest):
    pass


class NotificationLogQuery(BaseEntityQuery):
    todo_id: int | None = None
    timing_type: str | None = None
