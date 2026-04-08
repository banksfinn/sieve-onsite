from http import HTTPStatus

from database_manager.store.base_store import BaseEntityStore
from fastapi.exceptions import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.blueprints.tag_member import (
    TagMember,
    TagMemberCreateRequest,
    TagMemberDeleteRequest,
    TagMemberModel,
    TagMemberQuery,
    TagMemberUpdateRequest,
)


class TagMemberStore(
    BaseEntityStore[
        TagMemberModel,
        TagMember,
        TagMemberQuery,
        TagMemberCreateRequest,
        TagMemberUpdateRequest,
        TagMemberDeleteRequest,
    ]
):
    """Store for TagMember with composite key operations."""

    entity_model = TagMemberModel
    entity = TagMember
    entity_query = TagMemberQuery
    entity_create_request = TagMemberCreateRequest
    entity_update_request = TagMemberUpdateRequest
    entity_delete_request = TagMemberDeleteRequest

    def _apply_entity_specific_search(
        self, query: TagMemberQuery, stmt: Select[tuple[TagMemberModel]]
    ) -> Select[tuple[TagMemberModel]]:
        if query.tag_id is not None:
            stmt = stmt.filter(TagMemberModel.tag_id == query.tag_id)
        if query.user_id is not None:
            stmt = stmt.filter(TagMemberModel.user_id == query.user_id)
        return stmt

    # --- Composite key lookup methods ---

    async def _get_model_by_composite_key(self, tag_id: int, user_id: int, session: AsyncSession) -> TagMemberModel | None:
        """Get model by composite key (tag_id, user_id)."""
        stmt = select(TagMemberModel).where(
            TagMemberModel.tag_id == tag_id,
            TagMemberModel.user_id == user_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_member(self, tag_id: int, user_id: int) -> TagMember | None:
        """Get a specific membership by tag_id and user_id."""
        async with self._query_session() as session:
            model = await self._get_model_by_composite_key(tag_id, user_id, session)
            if model:
                return self.convert_model_to_entity(model)
            return None

    async def get_members_for_tag(self, tag_id: int) -> list[TagMember]:
        """Get all members of a tag."""
        result = await self.search_entities(TagMemberQuery(tag_id=tag_id))
        return result.entities

    async def get_tags_for_user(self, user_id: int) -> list[int]:
        """Returns tag_ids the user has access to."""
        async with self._query_session() as session:
            stmt = select(TagMemberModel.tag_id).where(TagMemberModel.user_id == user_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def add_member(self, request: TagMemberCreateRequest) -> TagMember:
        """Add a new member to a tag."""
        async with self._mutation_session() as session:
            # Check if membership already exists
            existing = await self._get_model_by_composite_key(request.tag_id, request.user_id, session)
            if existing:
                raise HTTPException(HTTPStatus.CONFLICT, "User is already a member of this tag")

            model = TagMemberModel(
                tag_id=request.tag_id,
                user_id=request.user_id,
                role=request.role,
                color=request.color,
            )
            session.add(model)
            await session.flush()
            return self.convert_model_to_entity(model)

    async def update_member(self, request: TagMemberUpdateRequest) -> TagMember:
        """Update a member's preferences (color, role)."""
        async with self._mutation_session() as session:
            model = await self._get_model_by_composite_key(request.tag_id, request.user_id, session)
            if not model:
                raise HTTPException(HTTPStatus.NOT_FOUND, "Tag membership not found")

            if request.color is not None:
                model.color = request.color
            if request.role is not None:
                model.role = request.role

            await session.flush()
            return self.convert_model_to_entity(model)

    async def remove_member(self, tag_id: int, user_id: int) -> None:
        """Remove a member from a tag."""
        async with self._mutation_session() as session:
            stmt = delete(TagMemberModel).where(
                TagMemberModel.tag_id == tag_id,
                TagMemberModel.user_id == user_id,
            )
            await session.execute(stmt)


tag_member_store = TagMemberStore()
