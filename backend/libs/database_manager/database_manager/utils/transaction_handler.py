from collections.abc import Callable, Coroutine
from contextvars import ContextVar
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from database_manager.clients.database_client import database_client
from logging_manager.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

# These set up sessions and context for transactions
session_context: ContextVar[AsyncSession | None] = ContextVar("session", default=None)
savepoint_context: ContextVar[AsyncSessionTransaction | None] = ContextVar("savepoint", default=None)
logger = get_logger()

P = ParamSpec("P")
T = TypeVar("T")


# This defines a decorator to ensure that we have atomic transactions
def atomic(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        existing_session = session_context.get(None)

        if existing_session is not None:
            # Check if the current transaction is active
            if existing_session.is_active:
                logger.debug("Nested transaction detected, creating savepoint")
                # We're in a nested transaction, create a savepoint
                savepoint = await existing_session.begin_nested()
                savepoint_token = savepoint_context.set(savepoint)
                try:
                    result = await func(*args, **kwargs)
                    logger.debug("Savepoint committed")
                    await savepoint.commit()
                    return result
                except Exception as e:
                    logger.debug("Savepoint rolled back")
                    await savepoint.rollback()
                    raise e
                finally:
                    logger.debug("Savepoint context reset")
                    savepoint_context.reset(savepoint_token)
            else:
                logger.warning("Attempted to create nested transaction in aborted state")
                raise ValueError("Cannot create nested transaction: current transaction is aborted")
        else:
            # This is the outermost transaction, create a new session
            async with database_client.session_scope() as session:
                logger.debug("New session created")
                session_token = session_context.set(session)
                try:
                    return await func(*args, **kwargs)
                finally:
                    logger.debug("Session context reset")
                    session_context.reset(session_token)

    return wrapper


def get_current_session() -> AsyncSession | None:
    session = session_context.get(None)
    return session


async def close_all_db_connections():
    logger.info("Closing all database connections")
    current_session = get_current_session()

    if current_session:
        logger.debug("Closing current session")
        await current_session.close()
        session_context.set(None)

    logger.info("All database connections closed")
