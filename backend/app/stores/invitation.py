from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.invitation import (
    Invitation,
    InvitationCreateRequest,
    InvitationModel,
    InvitationQuery,
    InvitationUpdateRequest,
)


class InvitationStore(
    BaseEntityStore[
        InvitationModel,
        Invitation,
        InvitationQuery,
        InvitationCreateRequest,
        InvitationUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = InvitationModel
    entity = Invitation
    entity_query = InvitationQuery
    entity_create_request = InvitationCreateRequest
    entity_update_request = InvitationUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: InvitationQuery, stmt: Select[tuple[InvitationModel]]
    ) -> Select[tuple[InvitationModel]]:
        if query.email_address:
            stmt = stmt.filter(InvitationModel.email_address == query.email_address)
        if query.accepted is not None:
            stmt = stmt.filter(InvitationModel.accepted == query.accepted)
        return stmt


invitation_store = InvitationStore()
