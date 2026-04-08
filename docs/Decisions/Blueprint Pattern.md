# Blueprint Pattern

## Decision

Every database entity is defined as a "blueprint" - a standardized set of types that fully describe its schema, queries, and mutations.

## Rationale

- **Consistency**: Every entity follows the same structure, making the codebase predictable
- **Type safety**: Generic [[BaseEntityStore]] leverages these types for compile-time correctness
- **Code generation friendly**: Standardized types enable tooling and patterns

## Blueprint Structure

Each entity defines these types in a single file:

```python
# Model - SQLAlchemy table definition
class ThingModel(BaseEntityModel):
    __tablename__ = "things"
    name: Mapped[str] = mapped_column(String)

# Entity - Pydantic response object
class Thing(BaseEntity):
    name: str

# Query - Search filters
class ThingQuery(BaseEntityQuery):
    name: str | None = None

# Create request
class ThingCreateRequest(BaseEntityCreateRequest):
    name: str

# Update request
class ThingUpdateRequest(BaseEntityUpdateRequest):
    name: str | None = None  # Optional for partial updates
```

## File Organization

- **Lib entities** (shared): `backend/libs/{lib}/blueprints/{entity}.py` (e.g., [[User Model]])
- **App entities** (domain-specific): `backend/app/blueprints/{entity}/{entity}.py`

## Relationship to [[BaseEntityStore]]

The store is parameterized by blueprint types:

```python
class ThingStore(BaseEntityStore[
    ThingModel,          # SQLAlchemy model
    Thing,               # Pydantic entity
    ThingQuery,          # Query parameters
    ThingCreateRequest,  # Creation fields
    ThingUpdateRequest,  # Update fields
    BaseEntityDeleteRequest,  # Reuse base delete
]):
    entity_model = ThingModel
    entity = Thing
    # ... class attributes binding types
```

## Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Model | `{Entity}Model` | `UserModel` |
| Entity | `{Entity}` | `User` |
| Query | `{Entity}Query` | `UserQuery` |
| Create | `{Entity}CreateRequest` | `UserCreateRequest` |
| Update | `{Entity}UpdateRequest` | `UserUpdateRequest` |
| Store | `{Entity}Store` | `UserStore` |

## See Also

- [[BaseEntity]]
- [[BaseEntityStore]]
- [[Data Model Overview]]
