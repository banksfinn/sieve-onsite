from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.delivery import (
    Delivery,
    DeliveryCreateRequest,
    DeliveryModel,
    DeliveryQuery,
    DeliveryUpdateRequest,
)


class DeliveryStore(
    BaseEntityStore[
        DeliveryModel,
        Delivery,
        DeliveryQuery,
        DeliveryCreateRequest,
        DeliveryUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = DeliveryModel
    entity = Delivery
    entity_query = DeliveryQuery
    entity_create_request = DeliveryCreateRequest
    entity_update_request = DeliveryUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(self, query: DeliveryQuery, stmt: Select[tuple[DeliveryModel]]) -> Select[tuple[DeliveryModel]]:
        if query.status:
            stmt = stmt.filter(DeliveryModel.status == query.status.value)
        if query.dataset_version_id:
            stmt = stmt.filter(DeliveryModel.dataset_version_id == query.dataset_version_id)
        if query.created_by:
            stmt = stmt.filter(DeliveryModel.created_by == query.created_by)
        return stmt


delivery_store = DeliveryStore()
