# BaseEntity

Foundation types for all database entities. Defined at `backend/libs/database_manager/database_manager/blueprints/base_entity.py`.

## BaseEntityModel (SQLAlchemy)

Abstract declarative base with three auto-managed columns:

| Column | Type | Default |
|--------|------|---------|
| `id` | `Integer` (primary key) | Auto-increment |
| `created_at` | `DateTime(timezone=True)` | `func.now()` |
| `updated_at` | `DateTime(timezone=True)` | `func.now()`, updates on change |

Provides `to_dict(exclude=None)` for converting to dictionary (used by [[BaseEntityStore]] for model-to-entity conversion).

## BaseEntity (Pydantic)

Response model with typed fields:

| Field | Type |
|-------|------|
| `id` | `int` |
| `created_at` | `AnnotatedArrow` |
| `updated_at` | `AnnotatedArrow` |

`AnnotatedArrow` is from `fullstack_types.datetimes` - handles datetime serialization.

## Query, Request, and Response Types

| Type | Fields | Purpose |
|------|--------|---------|
| `BaseEntityQuery` | `limit`, `offset`, `sort_by`, `sort_order` | Pagination + sorting |
| `BaseEntityCreateRequest` | (empty) | Subclasses add creation fields |
| `BaseEntityUpdateRequest` | `id` | Subclasses add updateable fields |
| `BaseEntityDeleteRequest` | `id` | Delete by primary key |
| `SearchResponseMetadata` | `total_count`, `limit`, `offset` | Pagination metadata |
| `BaseEntitySearchResponse[T]` | `entities`, `metadata` | Generic paginated response |

## Pagination Defaults

From `fullstack_types.query`:
- `DEFAULT_LIMIT` - Maximum results per page
- `DEFAULT_OFFSET` - Starting offset (0)
- `SortOrder` - `asc` or `desc`
- Default sort: `created_at` descending

## See Also

- [[Data Model Overview]]
- [[BaseEntityStore]]
- [[Blueprint Pattern]]
