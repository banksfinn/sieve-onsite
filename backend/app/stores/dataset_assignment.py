from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.dataset_assignment import (
    DatasetAssignment,
    DatasetAssignmentCreateRequest,
    DatasetAssignmentModel,
    DatasetAssignmentQuery,
    DatasetAssignmentUpdateRequest,
)


class DatasetAssignmentStore(
    BaseEntityStore[
        DatasetAssignmentModel,
        DatasetAssignment,
        DatasetAssignmentQuery,
        DatasetAssignmentCreateRequest,
        DatasetAssignmentUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = DatasetAssignmentModel
    entity = DatasetAssignment
    entity_query = DatasetAssignmentQuery
    entity_create_request = DatasetAssignmentCreateRequest
    entity_update_request = DatasetAssignmentUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: DatasetAssignmentQuery, stmt: Select[tuple[DatasetAssignmentModel]]
    ) -> Select[tuple[DatasetAssignmentModel]]:
        if query.dataset_id:
            stmt = stmt.filter(DatasetAssignmentModel.dataset_id == query.dataset_id)
        if query.user_id:
            stmt = stmt.filter(DatasetAssignmentModel.user_id == query.user_id)
        if query.role:
            stmt = stmt.filter(DatasetAssignmentModel.role == query.role)
        return stmt


dataset_assignment_store = DatasetAssignmentStore()
