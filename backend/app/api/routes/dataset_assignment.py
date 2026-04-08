from fastapi import APIRouter

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest, BaseEntitySearchResponse
from user_management.api.dependencies import UserDependency

from app.api.dependencies.authorization import InternalDependency
from app.blueprints.dataset_assignment import (
    DatasetAssignment,
    DatasetAssignmentCreateRequest,
    DatasetAssignmentQuery,
)
from app.stores.dataset_assignment import dataset_assignment_store

router = APIRouter()


@router.get("", response_model=BaseEntitySearchResponse[DatasetAssignment])
async def search_assignments(user: UserDependency, query: DatasetAssignmentQuery = DatasetAssignmentQuery()):
    return await dataset_assignment_store.search_entities(query)


@router.post("", response_model=DatasetAssignment)
async def create_assignment(user: InternalDependency, request: DatasetAssignmentCreateRequest):
    return await dataset_assignment_store.create_entity(request)


@router.delete("/{assignment_id}", response_model=DatasetAssignment)
async def delete_assignment(user: InternalDependency, assignment_id: int):
    return await dataset_assignment_store.delete_entity(BaseEntityDeleteRequest(id=assignment_id))
