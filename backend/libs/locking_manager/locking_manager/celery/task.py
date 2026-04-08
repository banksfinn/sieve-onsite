"""Celery task utilities with automatic Redis locking.

This module provides a decorator and base class for creating Celery tasks
with automatic Redis-based distributed locking to prevent duplicate execution.
All tasks are assumed to be async and are run via asyncio.run().
"""

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, cast

from celery import Task, shared_task  # type: ignore[reportUnknownVariableType]
from redis.exceptions import LockNotOwnedError
from redis.lock import Lock

from locking_manager.celery.task_id import generate_task_id
from locking_manager.clients.redis_client import redis_client
from logging_manager.logger import get_logger

LOCK_TIMEOUT_BUFFER = 60  # seconds beyond time_limit
DEFAULT_TASK_TIMEOUT = 600  # seconds


def generate_lock_key(task_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Generate a lock key from task name and arguments.

    Format: lock:task:module.task_name:arg0=val0:kwarg1=val1
    """
    parts = [f"lock:task:{task_name}"]
    for i, arg in enumerate(args):
        parts.append(f"arg{i}={arg}")
    for key in sorted(kwargs.keys()):
        parts.append(f"{key}={kwargs[key]}")
    return ":".join(parts)


class LockedTask(Task):
    """Celery task with automatic Redis locking and logging hooks.

    This task class automatically acquires a Redis lock before execution
    and releases it after completion. If the lock cannot be acquired,
    the task is skipped gracefully.

    All tasks are assumed to be async and are executed via asyncio.run().
    """

    use_lock: bool = True
    lock_timeout: int | None = None
    _async_func: Callable[..., Coroutine[Any, Any, Any]] | None = None

    def apply_locked_task(self, *args: Any, countdown: int | None = None, **kwargs: Any) -> Any:
        """Apply task with a deterministic task ID.

        This method generates a deterministic task ID based on the task name
        and arguments, preventing duplicate tasks from being queued.
        """
        task_name = self.name
        if not task_name:
            raise ValueError("Task name is required to generate a deterministic task ID")
        task_id = generate_task_id(task_name, args, kwargs)
        return self.apply_async(args=args, kwargs=kwargs, task_id=task_id, countdown=countdown)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]

    def on_failure(
        self,
        exc: BaseException,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        logger = get_logger()
        logger.error(
            "Task failed",
            task_id=task_id,
            task_name=self.name,
            args=args,
            kwargs=kwargs,
            exception=str(exc),
            traceback=str(einfo),
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)  # type: ignore[reportUnknownMemberType]

    def on_retry(
        self,
        exc: BaseException,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        logger = get_logger()
        logger.warning(
            "Task retrying",
            task_id=task_id,
            task_name=self.name,
            args=args,
            kwargs=kwargs,
            exception=str(exc),
            traceback=str(einfo),
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)  # type: ignore[reportUnknownMemberType]

    def after_return(
        self,
        status: str,
        retval: Any,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        logger = get_logger()
        logger.debug(
            "Task completed",
            task_id=task_id,
            task_name=self.name,
            status=status,
            args=args,
            kwargs=kwargs,
        )
        super().after_return(status, retval, task_id, args, kwargs, einfo)  # type: ignore[reportUnknownMemberType]

    def _get_lock_timeout(self) -> int:
        """Get the lock timeout, defaulting to time_limit + buffer."""
        if self.lock_timeout:
            return self.lock_timeout
        time_limit = getattr(self, "time_limit", None) or DEFAULT_TASK_TIMEOUT
        return time_limit + LOCK_TIMEOUT_BUFFER

    def _get_lock_key(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        """Get the lock key for this task invocation."""
        task_name = self.name or "unknown_task"
        return generate_lock_key(task_name, args, kwargs)

    def _run_async(self, *args: Any, **kwargs: Any) -> Any:
        """Run the async function via asyncio.run()."""
        if self._async_func is None:
            raise ValueError("No async function set for this task")
        return asyncio.run(self._async_func(*args, **kwargs))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the task with automatic locking."""
        logger = get_logger()

        if not self.use_lock:
            return self._run_async(*args, **kwargs)

        lock_key = self._get_lock_key(args, kwargs)
        lock = Lock(
            redis_client.client,
            lock_key,
            timeout=self._get_lock_timeout(),
            blocking=False,
        )

        if not lock.acquire(blocking=False):
            logger.info(
                "Lock not acquired, skipping task",
                task=self.name,
                lock_key=lock_key,
            )
            return None

        try:
            return self._run_async(*args, **kwargs)
        finally:
            try:
                lock.release()
            except LockNotOwnedError as e:
                logger.warning(
                    "Error releasing lock, likely already released",
                    task=self.name,
                    lock_key=lock_key,
                    error=str(e),
                )


def locked_task(
    time_limit: int = DEFAULT_TASK_TIMEOUT,
    use_lock: bool = True,
    lock_timeout: int | None = None,
    **celery_kwargs: Any,
) -> Callable[[Callable[..., Coroutine[Any, Any, Any]]], Task]:
    """Decorator for creating an async Celery task with automatic Redis locking.

    This decorator creates a Celery task that automatically:
    - Runs the async function via asyncio.run()
    - Acquires a Redis lock before execution based on task name + arguments
    - Releases the lock after completion (success or failure)
    - Skips execution gracefully if the lock cannot be acquired

    Args:
        time_limit: Maximum time in seconds for task execution
        use_lock: Whether to use distributed locking (default True)
        lock_timeout: Optional custom lock timeout (defaults to time_limit + 60s)
        **celery_kwargs: Additional arguments passed to @shared_task

    Returns:
        A decorated Celery task

    Example:
        @locked_task(time_limit=300)
        async def my_task(user_id: int) -> None:
            # This task will acquire a lock based on task name + user_id
            # Only one instance of my_task(user_id=123) can run at a time
            result = await some_async_operation()
            pass
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]) -> Task:
        # Create a sync wrapper that will be registered with Celery
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # This is just a placeholder - actual execution happens in __call__
            pass

        # Copy function metadata to wrapper
        sync_wrapper.__name__ = func.__name__
        sync_wrapper.__module__ = func.__module__
        sync_wrapper.__doc__ = func.__doc__

        task_class = type(
            f"{func.__name__}Task",
            (LockedTask,),
            {"use_lock": use_lock, "lock_timeout": lock_timeout, "_async_func": staticmethod(func)},
        )
        return cast(Task, shared_task(time_limit=time_limit, base=task_class, **celery_kwargs)(sync_wrapper))

    return decorator
