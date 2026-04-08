from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import (
    tag_table_name,
    user_table_name,
)
from pydantic import ConfigDict
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.blueprints.tag_member import TagMemberModel

TagRole = Literal["creator", "member"]


class TagModel(BaseEntityModel):
    __tablename__ = tag_table_name

    name: Mapped[str] = mapped_column(String)
    icon: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey(user_table_name + ".id"))

    # Slack channel for notifications (optional)
    slack_channel_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    slack_channel_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Relationship to members - will be loaded via selectinload
    members: Mapped[list["TagMemberModel"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan",
    )

    def to_dict(self, exclude: set[str] | None = None):
        """Override to include members relationship."""
        if not exclude:
            exclude = set()
        result = super().to_dict(exclude)
        if "members" not in exclude:
            result["members"] = [m.to_dict(exclude={"tag"}) for m in self.members]
        return result


class TagMember(BaseEntity):
    """Pydantic model for tag membership."""

    model_config = ConfigDict(from_attributes=True)

    tag_id: int
    user_id: int
    role: TagRole
    color: str | None = None


class Tag(BaseEntity):
    """Pydantic model for tags."""

    name: str
    icon: str | None = None
    created_by: int
    members: list[TagMember] = []
    slack_channel_id: str | None = None
    slack_channel_name: str | None = None


class TagCreateRequest(BaseEntityCreateRequest):
    name: str
    icon: str | None = None
    created_by: int | None = None  # Set by route handler
    color: str | None = None  # Creator's initial color preference


class TagUpdateRequest(BaseEntityUpdateRequest):
    name: str | None = None
    icon: str | None = None
    slack_channel_id: str | None = None
    slack_channel_name: str | None = None


class TagQuery(BaseEntityQuery):
    user_id: int | None = None  # Filter tags by membership
