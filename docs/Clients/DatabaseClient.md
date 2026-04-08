# DatabaseClient

Async SQLAlchemy database engine and session factory. Singleton at `backend/libs/database_manager/database_manager/clients/database_client.py`.

## Responsibilities

- Creates the async SQLAlchemy engine from `DATABASE_URL`
- Converts `postgresql://` to `postgresql+asyncpg://` automatically
- Provides `session_maker` (async session factory) to [[BaseEntityStore]]
- Handles Celery worker detection for connection pooling

## Connection Pooling

The client detects whether it's running inside a Celery worker:

- **Normal mode**: Default SQLAlchemy connection pool
- **Celery mode**: `NullPool` - creates fresh connections per task

This is necessary because each `asyncio.run()` in Celery creates a new event loop, but asyncpg connections are bound to a specific loop. See [[Async-First Backend]] for the broader rationale.

## Session Management

```python
# Query operations (read-only)
async with self._query_session() as session:
    result = await session.execute(stmt)

# Mutation operations (auto commit/rollback)
async with self._mutation_session() as session:
    session.add(entity)
    await session.flush()
```

Both context managers check for an existing session from a transaction handler (for nested operations). If none exists, they create and manage a new session. See [[BaseEntityStore]] for how stores use these.

## Configuration

Via `database_manager.core.settings`:

| Setting | Purpose |
|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `VERBOSE_DATABASE_MODE` | SQLAlchemy echo mode |

## Key Design Choice

`expire_on_commit=False` on the session maker prevents SQLAlchemy from invalidating loaded attributes after commit. This is critical in async context where lazy loading would fail.

## File Location

`backend/libs/database_manager/database_manager/clients/database_client.py`

## See Also

- [[BaseEntityStore]]
- [[Async-First Backend]]
- [[Infrastructure]]
