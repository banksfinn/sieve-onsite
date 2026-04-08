from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import (
    todo_table_name,
    user_table_name,
)
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.blueprints.todo_tag import todo_tags_table

if TYPE_CHECKING:
    from app.blueprints.tag import TagModel

RecurrenceType = Literal["fixed_schedule", "from_completion"]


class TodoModel(BaseEntityModel):
    __tablename__ = todo_table_name

    user_id: Mapped[int] = mapped_column(ForeignKey(user_table_name + ".id"))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    slack_notification: Mapped[bool] = mapped_column(Boolean, default=False)

    # Notification timing override - JSON string array, None means use user default
    # e.g., '["at_due_time", "30_minutes_before", "morning_of"]'
    notification_timing_override: Mapped[str | None] = mapped_column(String, nullable=True)

    # Recurrence fields
    recurrence_rule: Mapped[str | None] = mapped_column(String, nullable=True)
    recurrence_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recurrence_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recurrence_type: Mapped[str | None] = mapped_column(String, nullable=True)

    # Tags relationship (many-to-many through todo_tags)
    tags: Mapped[list["TagModel"]] = relationship(secondary=todo_tags_table)

    def to_dict(self, exclude: set[str] | None = None):
        """Override to include tags relationship."""
        if not exclude:
            exclude = set()
        result = super().to_dict(exclude)
        if "tags" not in exclude:
            result["tags"] = [t.to_dict(exclude={"members"}) for t in self.tags]
        return result


class TodoTag(BaseEntity):
    """Lightweight tag representation for todo responses (without members)."""

    name: str
    icon: str | None = None
    created_by: int


class Todo(BaseEntity):
    user_id: int
    title: str
    description: str | None = None
    completed: bool

    # This indicates when the todo is due and should be completed
    due_at: datetime | None = None

    # This indicates if a notification has been sent for the todo
    due_notification_sent: bool = False
    # This indicates if the user wants Slack notifications for this todo (only relevant if due_at is set)
    slack_notification: bool = False
    # Notification timing override - None means use user default
    notification_timing_override: list[str] | None = None

    # Recurrence fields
    recurrence_rule: str | None = None  # RRule format string
    recurrence_start: datetime | None = None  # Start of recurrence window
    recurrence_end: datetime | None = None  # End of recurrence window
    recurrence_type: RecurrenceType | None = None  # "fixed_schedule" or "from_completion"

    # Tags associated with this todo
    tags: list[TodoTag] = []


class TodoCreateRequest(BaseEntityCreateRequest):
    user_id: int | None = None
    title: str
    description: str | None = None
    due_at: datetime | None = None
    slack_notification: bool = False
    notification_timing_override: list[str] | None = None  # None means use user default
    recurrence_rule: str | None = None
    recurrence_start: datetime | None = None
    recurrence_end: datetime | None = None
    recurrence_type: RecurrenceType | None = None
    tag_ids: list[int] = []  # IDs of tags to associate with this todo


class TodoUpdateRequest(BaseEntityUpdateRequest):
    completed: bool | None = None
    title: str | None = None
    description: str | None = None
    due_notification_sent: bool | None = None
    due_at: datetime | None = None
    slack_notification: bool | None = None
    notification_timing_override: list[str] | None = None
    recurrence_rule: str | None = None
    recurrence_start: datetime | None = None
    recurrence_end: datetime | None = None
    recurrence_type: RecurrenceType | None = None
    tag_ids: list[int] | None = None  # Set to update tags, None to leave unchanged


class TodoQuery(BaseEntityQuery):
    user_id: int | None = None
    due_before: datetime | None = None
    due_notification_sent: bool | None = None
    completed: bool | None = None
