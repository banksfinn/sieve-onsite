# UserStore

Data access layer for [[User Model|User]] entities. Extends [[BaseEntityStore]] with email-based search filtering.

## Location

`backend/libs/user_management/user_management/stores/user.py`

## Type Bindings

```python
class UserStore(BaseEntityStore[
    UserModel,
    User,
    UserQuery,
    UserCreateRequest,
    UserUpdateRequest,
    BaseEntityDeleteRequest,
])
```

## Custom Search

Overrides `_apply_entity_specific_search` to filter by `email_address` when provided in the query:

```python
UserQuery(email_address="user@example.com")
```

This is used by the [[Authentication Routes|Google login endpoint]] to check if a user already exists before creating one.

## Singleton

Exported as `user_store` - a module-level singleton used across the application.

## Dependencies

The `UserDependency` FastAPI dependency (in `user_management/api/dependencies.py`) uses this store internally to:

1. Extract JWT from HttpOnly cookie
2. Decode and validate the token
3. Fetch the user by ID from the store
4. Return the [[User Model|User]] entity or raise 401

## See Also

- [[BaseEntityStore]]
- [[User Model]]
- [[Cookie-Based JWT Auth]]
