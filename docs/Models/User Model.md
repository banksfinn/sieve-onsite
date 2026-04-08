# User Model

The User entity at `backend/libs/user_management/user_management/blueprints/user.py`. Extends [[BaseEntity]] with authentication and notification fields.

## Fields

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `id` | int | Auto | Auto-increment |
| `created_at` | datetime | Auto | `now()` |
| `updated_at` | datetime | Auto | `now()` |
| `email_address` | EmailStr | Yes | - |
| `name` | str | Yes | - |
| `notification_timing` | list[str] \| None | No | `["30_minutes_before"]` |
| `notification_custom_minutes` | int \| None | No | None |

## Type Definitions

```python
UserModel          # SQLAlchemy model → database table
User               # Pydantic entity → API responses
UserCreateRequest  # email_address + name
UserUpdateRequest  # notification_timing + notification_custom_minutes
UserQuery          # email_address filter (optional)
```

## Notification Timing

Stored as a JSON string array in the database. Possible values include:
- `"at_due_time"`
- `"30_minutes_before"`
- `"morning_of"`

The `notification_custom_minutes` field allows arbitrary minute-based reminders.

## Database Table

Table name defined in `database_manager.schemas.table_names.user_table_name`.

## Migrations

1. `create_users` - Initial table with email_address
2. `add_user_name` - Added name column
3. `add_the_rest_of_items` - Added notification preferences

## See Also

- [[BaseEntity]]
- [[UserStore]]
- [[Cookie-Based JWT Auth]]
