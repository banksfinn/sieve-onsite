from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select
from user_management.blueprints.user import (
    User,
    UserCreateRequest,
    UserModel,
    UserQuery,
    UserUpdateRequest,
)


class UserStore(
    BaseEntityStore[
        UserModel,
        User,
        UserQuery,
        UserCreateRequest,
        UserUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = UserModel
    entity = User
    query = UserQuery
    create_request = UserCreateRequest
    update_request = UserUpdateRequest
    delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(self, query: UserQuery, stmt: Select[tuple[UserModel]]) -> Select[tuple[UserModel]]:
        if query.email_address:
            stmt = stmt.filter(UserModel.email_address == query.email_address)
        if query.role:
            stmt = stmt.filter(UserModel.role == query.role)
        return stmt


user_store = UserStore()
