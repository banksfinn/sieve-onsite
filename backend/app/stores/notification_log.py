from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.notification_log import (
    NotificationLog,
    NotificationLogCreateRequest,
    NotificationLogModel,
    NotificationLogQuery,
    NotificationLogUpdateRequest,
)


class NotificationLogStore(
    BaseEntityStore[
        NotificationLogModel,
        NotificationLog,
        NotificationLogQuery,
        NotificationLogCreateRequest,
        NotificationLogUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = NotificationLogModel
    entity = NotificationLog
    query = NotificationLogQuery
    create_request = NotificationLogCreateRequest
    update_request = NotificationLogUpdateRequest
    delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: NotificationLogQuery, stmt: Select[tuple[NotificationLogModel]]
    ) -> Select[tuple[NotificationLogModel]]:
        if query.todo_id is not None:
            stmt = stmt.filter(NotificationLogModel.todo_id == query.todo_id)
        if query.timing_type is not None:
            stmt = stmt.filter(NotificationLogModel.timing_type == query.timing_type)
        return stmt

    async def has_been_sent(self, todo_id: int, timing_type: str) -> bool:
        """Check if a notification has already been sent for this todo and timing type."""
        query = NotificationLogQuery(todo_id=todo_id, timing_type=timing_type, limit=1)
        result = await self.search_entities(query)
        return len(result.entities) > 0


notification_log_store = NotificationLogStore()
