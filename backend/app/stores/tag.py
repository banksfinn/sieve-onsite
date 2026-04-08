from typing import Any

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from app.blueprints.tag import Tag, TagCreateRequest, TagModel, TagQuery, TagUpdateRequest
from app.blueprints.tag_member import TagMemberModel


class TagStore(
    BaseEntityStore[
        TagModel,
        Tag,
        TagQuery,
        TagCreateRequest,
        TagUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = TagModel
    entity = Tag
    query = TagQuery
    create_request = TagCreateRequest
    update_request = TagUpdateRequest
    delete_request = BaseEntityDeleteRequest

    selectinload_fields: list[Any] = [selectinload(TagModel.members)]

    def _apply_entity_specific_search(self, query: TagQuery, stmt: Select[tuple[TagModel]]) -> Select[tuple[TagModel]]:
        if query.user_id:
            # Filter to only tags where user is a member
            stmt = stmt.join(TagMemberModel).filter(TagMemberModel.user_id == query.user_id)
        return stmt

    def convert_create_request_to_dict(self, request: TagCreateRequest) -> dict[str, Any]:
        """Exclude color from the tag creation - it's for the membership."""
        data = request.model_dump()
        data.pop("color", None)
        return data


tag_store = TagStore()
