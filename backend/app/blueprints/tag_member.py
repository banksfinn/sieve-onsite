from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from database_manager.blueprints.base_entity import (
    BaseEntity,
    BaseEntityCreateRequest,
    BaseEntityDeleteRequest,
    BaseEntityModel,
    BaseEntityQuery,
    BaseEntityUpdateRequest,
)
from database_manager.schemas.table_names import (
    tag_member_table_name,
    tag_table_name,
    user_table_name,
)
from pydantic import ConfigDict
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.blueprints.tag import TagModel

TagRole = Literal["creator", "member"]


class TagMemberModel(BaseEntityModel):
    """Model for tag membership - tracks who has access to each tag."""

    __tablename__ = tag_member_table_name
    __table_args__ = (UniqueConstraint("tag_id", "user_id", name="uq_tag_member"),)

    tag_id: Mapped[int] = mapped_column(ForeignKey(tag_table_name + ".id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey(user_table_name + ".id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String, default="member")
    color: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationship back to tag
    tag: Mapped["TagModel"] = relationship(back_populates="members")

    def to_dict(self, exclude: set[str] | None = None):
        """Override to exclude relationship by default."""
        if not exclude:
            exclude = set()
        exclude.add("tag")  # Don't include tag relationship to avoid circular refs
        return super().to_dict(exclude)


class TagMember(BaseEntity):
    """Pydantic model for tag membership."""

    model_config = ConfigDict(from_attributes=True)

    tag_id: int
    user_id: int
    role: TagRole
    color: str | None = None


class TagMemberCreateRequest(BaseEntityCreateRequest):
    """Request to add a member to a tag."""

    tag_id: int
    user_id: int
    role: TagRole = "member"
    color: str | None = None


class TagMemberUpdateRequest(BaseEntityUpdateRequest):
    """Request to update a member's preferences.

    Note: Uses composite key (tag_id, user_id) instead of id.
    The id field is provided for BaseEntityStore compatibility but is ignored.
    """

    id: int = 0  # Unused - composite key used instead
    tag_id: int
    user_id: int
    color: str | None = None
    role: TagRole | None = None


class TagMemberQuery(BaseEntityQuery):
    """Query for searching tag members."""

    tag_id: int | None = None
    user_id: int | None = None


# Re-export for consistency with other entities
TagMemberDeleteRequest = BaseEntityDeleteRequest
