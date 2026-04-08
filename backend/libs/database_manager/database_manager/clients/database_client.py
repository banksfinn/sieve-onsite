import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from database_manager.core.settings import database_manager_settings
from logging_manager.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool


def _is_celery_worker() -> bool:
    """Detect if we're running inside a Celery worker process."""
    # Celery sets this when forking worker processes
    return "celery" in os.environ.get("_", "") or os.environ.get("CELERY_WORKER", "") == "1"


class DatabaseClient:
    def __init__(self):
        # Read in the DB url and convert to async format
        db_url = database_manager_settings.DATABASE_URL
        # Convert postgresql:// to postgresql+asyncpg://
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        self.db_url = db_url

        # Use NullPool for Celery workers to avoid event loop mismatch issues.
        # Each asyncio.run() in Celery creates a new event loop, but asyncpg
        # connections are bound to a specific loop. NullPool ensures fresh
        # connections for each task.
        pool_class = NullPool if _is_celery_worker() else None

        # Create the async engine
        self.engine: AsyncEngine = create_async_engine(
            self.db_url,
            echo=database_manager_settings.VERBOSE_DATABASE_MODE,
            poolclass=pool_class,
        )
        # Create async session maker
        self.session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )
        # Create the logger
        self.logger = get_logger()

    @asynccontextmanager
    async def session_scope(self) -> AsyncIterator[AsyncSession]:
        session = self.session_maker()
        try:
            yield session
            await session.commit()
        except Exception as e:
            self.logger.warning("DB Rollback occuring")
            await session.rollback()
            raise e
        finally:
            await session.close()


database_client = DatabaseClient()
