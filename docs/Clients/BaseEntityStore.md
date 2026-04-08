# BaseEntityStore

Generic CRUD store pattern at `backend/libs/database_manager/database_manager/store/base_store.py`. All entity stores inherit from this.

## Type Parameters

```python
class BaseEntityStore(Generic[
    BaseEntityModelType,      # SQLAlchemy model
    BaseEntityType,           # Pydantic entity
    BaseEntityQueryType,      # Search/filter parameters
    BaseEntityCreateRequestType,
    BaseEntityUpdateRequestType,
    BaseEntityDeleteRequestType,
])
```

## CRUD Operations

| Method | Purpose |
|--------|---------|
| `get_entity_by_id(id)` | Fetch single entity |
| `search_entities(query)` | Filtered, paginated search |
| `create_entity(request)` | Insert new entity |
| `update_entity(request)` | Update existing entity |
| `delete_entity(request)` | Delete entity |

## Session Management

Uses [[DatabaseClient]] sessions via two context managers:

- `_query_session()` - Read-only, no commit
- `_mutation_session()` - Auto commit on success, rollback on exception

Both support nesting: if a `transaction_handler` session already exists, they reuse it instead of creating a new one.

## Extension Points

Subclasses customize behavior via:

| Hook | Purpose |
|------|---------|
| `_apply_entity_specific_search()` | Add WHERE clauses for entity-specific filters |
| `_after_create()` | Post-insert logic (e.g., association tables) |
| `_after_update()` | Post-update logic |
| `handle_backpopulation_deletion()` | Clean up related records before delete |
| `convert_create_request_to_dict()` | Transform create request before insert |
| `apply_update_to_model()` | Apply partial updates to existing model |

## Eager Loading

The `selectinload_fields` class variable controls relationship eager loading. After every `create_entity` and `update_entity`, the store re-fetches the entity with selectinload to avoid lazy-loading errors in async context. This is a deliberate tradeoff - see [[Async-First Backend]].

## Search Response

Search returns `BaseEntitySearchResponse` containing:
- `entities: list[EntityType]` - Paginated results
- `metadata: SearchResponseMetadata` - `total_count`, `limit`, `offset`

## File Location

`backend/libs/database_manager/database_manager/store/base_store.py`

## See Also

- [[DatabaseClient]]
- [[BaseEntity]]
- [[Blueprint Pattern]]
- [[UserStore]]
