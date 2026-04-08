from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.delivery_access import (
    DeliveryAccess,
    DeliveryAccessCreateRequest,
    DeliveryAccessModel,
    DeliveryAccessQuery,
    DeliveryAccessUpdateRequest,
)


class DeliveryAccessStore(
    BaseEntityStore[
        DeliveryAccessModel,
        DeliveryAccess,
        DeliveryAccessQuery,
        DeliveryAccessCreateRequest,
        DeliveryAccessUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = DeliveryAccessModel
    entity = DeliveryAccess
    entity_query = DeliveryAccessQuery
    entity_create_request = DeliveryAccessCreateRequest
    entity_update_request = DeliveryAccessUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: DeliveryAccessQuery, stmt: Select[tuple[DeliveryAccessModel]]
    ) -> Select[tuple[DeliveryAccessModel]]:
        if query.delivery_id:
            stmt = stmt.filter(DeliveryAccessModel.delivery_id == query.delivery_id)
        if query.user_id:
            stmt = stmt.filter(DeliveryAccessModel.user_id == query.user_id)
        return stmt


delivery_access_store = DeliveryAccessStore()
