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

- [[User Model]] - User with role (customer/gtm/researcher) and access level (regular/admin)
- [[User Roles and Access]] - Role system, authorization dependencies, invitation flow
- `app/blueprints/dataset.py` - Dataset and DatasetVersion
- `app/blueprints/dataset_assignment.py` - Links users to datasets with a relationship role
- `app/blueprints/invitation.py` - Admin-created invitations consumed on first login
- `app/blueprints/video.py` - Video entity
- `app/blueprints/clip.py` - Clip entity
- `app/blueprints/delivery.py` - Delivery entity
- `app/blueprints/delivery_access.py` - Delivery access control
- `app/blueprints/clip_feedback.py` - Clip-level feedback
- `app/blueprints/delivery_feedback.py` - Delivery-level feedback

## Pydantic Configuration

All entity Pydantic models need `model_config = ConfigDict(from_attributes=True)` to support conversion from SQLAlchemy models. The base `BaseEntity` already has this configured.

## Relationships

For foreign keys, always specify cascade behavior:

```python
parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"))
```

Use `relationship()` on the SQLAlchemy model, but always eager-load via `selectinload_fields` on the store - never rely on lazy loading in async context (see [[Async-First Backend]]).

## Adding a New Entity

1. Create blueprint in `app/blueprints/{entity}/` with Model, Entity, Query, CreateRequest, UpdateRequest
2. Import the Model in `app/models.py` for Alembic discovery
3. Create a store in `app/stores/` extending [[BaseEntityStore]]
4. Generate migration: `make db_generate_migration "add {entity}"`
5. Apply migration: `make db_apply_migration` before running tests
6. Create routes in `app/api/routes/`
7. Register routes in `app/api/router.py`
8. Run `make sync_openapi` to generate frontend types

## See Also

- [[BaseEntity]]
- [[Blueprint Pattern]]
- [[BaseEntityStore]]
