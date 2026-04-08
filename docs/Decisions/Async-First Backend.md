# Async-First Backend

## Decision

All backend code uses async/await with asyncpg and SQLAlchemy 2.0's async API. No synchronous database operations.

## Rationale

- **Concurrency**: FastAPI + asyncpg handles many concurrent requests without thread overhead
- **Streaming**: Prepares for async streaming responses (e.g., video metadata)
- **Consistency**: One concurrency model everywhere avoids mixed sync/async pitfalls

## Consequences

### No Lazy Loading

SQLAlchemy lazy loading triggers synchronous I/O, which fails in async context. [[BaseEntityStore]] works around this:

- `selectinload_fields` on each store class defines relationships to eager-load
- After `create_entity` and `update_entity`, the store re-fetches with selectinload
- `expire_on_commit=False` on [[DatabaseClient]] session maker prevents attribute invalidation

### Celery Compatibility

Celery workers use `asyncio.run()` per task, creating new event loops. asyncpg connections are bound to their creating loop. Solution: [[DatabaseClient]] uses `NullPool` when it detects a Celery worker process.

### Session Context Managers

[[BaseEntityStore]] provides `_query_session()` and `_mutation_session()` that handle:
- Session creation and cleanup
- Transaction commit/rollback (mutations only)
- Reuse of existing session when inside a transaction handler

## Rules

- All route handlers must be `async def`
- All store methods must be awaited
- Never use `relationship()` lazy loading - use `selectinload_fields`
- Celery tasks wrap async calls in `asyncio.run()`

## See Also

- [[DatabaseClient]]
- [[BaseEntityStore]]
- [[Backend Architecture]]
