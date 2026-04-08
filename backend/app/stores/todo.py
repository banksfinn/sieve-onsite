import json
from http import HTTPStatus
from typing import Any

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from fastapi.exceptions import HTTPException
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from app.blueprints.tag_member import TagMemberModel
from app.blueprints.todo import (
    Todo,
    TodoCreateRequest,
    TodoModel,
    TodoQuery,
    TodoUpdateRequest,
)
from app.blueprints.todo_tag import todo_tags_table


class TodoStore(
    BaseEntityStore[
        TodoModel,
        Todo,
        TodoQuery,
        TodoCreateRequest,
        TodoUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = TodoModel
    entity = Todo
    query = TodoQuery
    create_request = TodoCreateRequest
    update_request = TodoUpdateRequest
    delete_request = BaseEntityDeleteRequest

    # Eager load tags for each todo
    selectinload_fields: list[Any] = [selectinload(TodoModel.tags)]

    def _apply_entity_specific_search(self, query: TodoQuery, stmt: Select[tuple[TodoModel]]) -> Select[tuple[TodoModel]]:
        if query.user_id:
            # User can see:
            # 1. Their own todos (user_id = current_user)
            # 2. Any todos with tags they have access to

            # Subquery: tag_ids user has access to
            accessible_tags = select(TagMemberModel.tag_id).where(TagMemberModel.user_id == query.user_id)

            # Subquery: todos with accessible tags
            todos_with_accessible_tags = select(todo_tags_table.c.todo_id).where(todo_tags_table.c.tag_id.in_(accessible_tags))

            stmt = stmt.filter(
                or_(
                    TodoModel.user_id == query.user_id,
                    TodoModel.id.in_(todos_with_accessible_tags),
                )
            )
        if query.due_before:
            stmt = stmt.filter(TodoModel.due_at <= query.due_before)
        if query.due_notification_sent is not None:
            stmt = stmt.filter(TodoModel.due_notification_sent == query.due_notification_sent)
        if query.completed is not None:
            stmt = stmt.filter(TodoModel.completed == query.completed)
        return stmt

    def convert_create_request_to_dict(self, request: TodoCreateRequest) -> dict[str, Any]:
        """Exclude tag_ids from the model creation - handled in _after_create.
        Also serialize notification_timing_override to JSON string for storage.
        """
        data = request.model_dump()
        data.pop("tag_ids", None)
        # Serialize list to JSON string for database storage
        if data.get("notification_timing_override") is not None:
            data["notification_timing_override"] = json.dumps(data["notification_timing_override"])
        return data

    def apply_update_to_model(self, request: TodoUpdateRequest, existing_entity: TodoModel) -> TodoModel:
        """Convert update request to model, serializing notification_timing_override."""
        updates = request.model_dump(exclude_unset=True)
        for field, new_value in updates.items():
            if field == "notification_timing_override" and new_value is not None:
                new_value = json.dumps(new_value)
            setattr(existing_entity, field, new_value)
        return existing_entity

    def convert_model_to_entity(self, model: TodoModel) -> Todo:
        """Convert model to entity, deserializing notification_timing_override from JSON."""
        data = model.to_dict()
        # Deserialize JSON string back to list
        if data.get("notification_timing_override") is not None:
            data["notification_timing_override"] = json.loads(data["notification_timing_override"])
        return Todo.model_validate(data)

    async def _get_user_accessible_tags(self, user_id: int, session: AsyncSession) -> set[int]:
        """Get tag IDs the user has access to."""
        stmt = select(TagMemberModel.tag_id).where(TagMemberModel.user_id == user_id)
        result = await session.execute(stmt)
        return set(result.scalars().all())

    async def _validate_tag_access(self, user_id: int, tag_ids: list[int], session: AsyncSession) -> None:
        """Validate user has access to all specified tags."""
        if not tag_ids:
            return
        accessible = await self._get_user_accessible_tags(user_id, session)
        for tag_id in tag_ids:
            if tag_id not in accessible:
                raise HTTPException(HTTPStatus.FORBIDDEN, f"No access to tag {tag_id}")

    async def _set_tags(self, todo_id: int, tag_ids: list[int], session: AsyncSession) -> None:
        """Replace all tags for a todo."""
        # Remove existing tags
        await session.execute(delete(todo_tags_table).where(todo_tags_table.c.todo_id == todo_id))
        # Add new tags
        for tag_id in tag_ids:
            await session.execute(todo_tags_table.insert().values(todo_id=todo_id, tag_id=tag_id))

    async def _after_create(
        self,
        request: TodoCreateRequest,
        entity_model: TodoModel,
        session: AsyncSession,
    ) -> None:
        """Handle tag associations after todo creation."""
        if request.tag_ids and request.user_id:
            await self._validate_tag_access(request.user_id, request.tag_ids, session)
        if request.tag_ids:
            await self._set_tags(entity_model.id, request.tag_ids, session)

    async def _after_update(
        self,
        request: TodoUpdateRequest,
        entity_model: TodoModel,
        session: AsyncSession,
    ) -> None:
        """Handle tag associations after todo update."""
        if request.tag_ids is not None:
            if entity_model.user_id:
                await self._validate_tag_access(entity_model.user_id, request.tag_ids, session)
            await self._set_tags(entity_model.id, request.tag_ids, session)

    async def delete_entity(self, request: BaseEntityDeleteRequest) -> Todo:
        """Delete a todo (cascade will handle tag associations)."""
        async with self._mutation_session() as session:
            existing_entity = await self._get_entity_model_by_id(request.id, session)
            if not existing_entity:
                raise HTTPException(HTTPStatus.NOT_FOUND, "No todo with ID found")

            converted_entity = self.convert_model_to_entity(existing_entity)
            await session.delete(existing_entity)
            return converted_entity


todo_store = TodoStore()
