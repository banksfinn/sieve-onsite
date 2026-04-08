---
id: database-patterns
title: Database Patterns
purpose: SQLAlchemy models, Pydantic schemas, BaseEntityStore pattern, and Alembic
  migrations.
scope:
  paths:
  - backend/app/blueprints/**
  - backend/app/stores/**
  - backend/tools/alembic/**
  tags:
  - database
  - sqlalchemy
  - pydantic
  - migrations
---

# Database Patterns

## Items

<!-- @item source:user status:active enforcement:strict -->
Blueprint files define four components: `FooModel` (SQLAlchemy model), `Foo` (Pydantic entity), `FooCreateRequest`, and `FooUpdateRequest`.

<!-- @item source:user status:active enforcement:strict -->
Data access stores inherit from `BaseEntityStore` with generic type parameters for the model and entity types.

<!-- @item source:user status:active enforcement:strict -->
Alembic `env.py` must import all models for migration discovery. When adding new models, ensure they are imported there.

<!-- @item source:user status:active enforcement:recommended -->
Terminology: "Model" refers to SQLAlchemy database models (in `blueprints/`). "Entity" refers to Pydantic BaseModel representations.

<!-- @item source:user status:active enforcement:strict -->
Use `model_config = ConfigDict(from_attributes=True)` for Pydantic models that map from SQLAlchemy (Pydantic v2 pattern).

<!-- @item source:user status:active -->
**Creating a new entity**: 1) Define blueprints (FooModel, Foo, FooCreateRequest, FooUpdateRequest), 2) Add FooModel import to `models.py` for Alembic discovery, 3) Create FooStore inheriting from BaseEntityStore with generic type parameters.

<!-- @item source:user status:active -->
**Custom queries**: Override `_apply_entity_specific_search(query, search)` in your store to add entity-specific filtering logic.

<!-- @item source:user status:active -->
**ForeignKey relationships**: Define with `mapped_column(ForeignKey(table + ".id", ondelete="CASCADE"))` and load as object with `relationship()`. Example: `sub_item_model_id: Mapped[int]` + `sub_item_model: Mapped[SubItemModel] = relationship()`.

<!-- @item source:user status:active -->
**Eager loading joins**: Add related models to `selectinload_fields` in the store. Override `to_dict(exclude)` on the model to include related entities, calling `self.related_model.to_dict()` for each relationship.

<!-- @item source:user status:active enforcement:strict -->
**Alembic migrations**: Alembic (`tools/alembic/`) manages database migrations. Use `make db_generate_migration` to create new migrations. Nothing should import from alembic; it's a top-level consumer.

<!-- @item source:llm status:proposed -->
**Alembic workflow**: After creating a migration with `make db_generate_migration`, always: 1) Review the generated migration file to verify it's correct, 2) Apply the migration with `make db_apply_migration` before testing or syncing OpenAPI types.

<!-- @item source:llm status:proposed enforcement:strict -->
**Async database access**: All database operations use async SQLAlchemy with `asyncpg`. Store methods (`get_entity_by_id()`, `search_entities()`, `create_entity()`, `update_entity()`, `delete_entity()`) are all async and must be awaited. The `@atomic` decorator now wraps async functions.

<!-- @item source:llm status:proposed enforcement:recommended -->
**Celery async integration**: The `@locked_task` decorator now expects async functions. Write Celery tasks as `async def` and use `await` for database operations. The decorator handles running via `asyncio.run()` internally.

<!-- @item source:llm status:proposed enforcement:strict -->
**Query syntax change**: Entity-specific search filters now use SQLAlchemy 2.0 `Select` statements instead of legacy `Query` objects. Override `_apply_entity_specific_search(query, stmt: Select)` using `stmt.filter()` method chaining.

<!-- @item source:llm status:proposed -->
**Async lazy loading gotcha**: In `create_entity`, after `flush()` the new model has no loaded relationships. Calling `to_dict()` on models with relationships triggers lazy loading, which fails in async context with `MissingGreenlet`. The fix: re-fetch the entity with `selectinload_fields` after flush before calling `convert_model_to_entity()`. This pattern ensures all relationships are eagerly loaded.
