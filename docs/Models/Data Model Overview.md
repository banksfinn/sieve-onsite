# Data Model Overview

All entities follow the [[Blueprint Pattern]] - a standardized set of types for each domain concept.

## Type Hierarchy

```
BaseEntityModel (SQLAlchemy)     BaseEntity (Pydantic)
      │                                │
      ├── id                           ├── id
      ├── created_at                   ├── created_at
      └── updated_at                   └── updated_at
      │                                │
  UserModel                          User
      ├── email_address                ├── email_address
      ├── name                         ├── name
      ├── notification_timing          ├── notification_timing
      └── notification_custom_minutes  └── notification_custom_minutes
```

## Per-Entity Type Set

Each entity defines 5-6 types in its blueprint:

| Type | Base Class | Purpose |
|------|-----------|---------|
| `*Model` | `BaseEntityModel` | SQLAlchemy table definition |
| `*` (entity) | `BaseEntity` | Pydantic response/domain object |
| `*Query` | `BaseEntityQuery` | Search filters + pagination |
| `*CreateRequest` | `BaseEntityCreateRequest` | Fields for creation |
| `*UpdateRequest` | `BaseEntityUpdateRequest` | Partial update fields |
| `*DeleteRequest` | `BaseEntityDeleteRequest` | Delete by ID |

## Current Entities

- [[User Model]] - The only entity currently defined
- `app/blueprints/` - Empty, ready for new domain entities (Delivery, Clip, Feedback, etc.)

## Adding a New Entity

1. Create blueprint in `app/blueprints/{entity}/` with Model, Entity, Query, CreateRequest, UpdateRequest
2. Import the Model in `app/models.py` for Alembic discovery
3. Create a store in `app/stores/` extending [[BaseEntityStore]]
4. Generate migration: `make db_generate_migration "add {entity}"`
5. Create routes in `app/api/routes/`
6. Register routes in `app/api/router.py`
7. Run `make sync_openapi` to generate frontend types

## See Also

- [[BaseEntity]]
- [[Blueprint Pattern]]
- [[BaseEntityStore]]
