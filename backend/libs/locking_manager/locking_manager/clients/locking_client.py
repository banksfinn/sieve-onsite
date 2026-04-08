from contextlib import contextmanager
from typing import Generator

from redis.lock import Lock

from locking_manager.clients.redis_client import RedisClient, redis_client


class LockingClient:
    """Generic Redis-based distributed locking client."""

    def __init__(self, redis_client_instance: "RedisClient | None" = None):
        self._redis_client = redis_client_instance or redis_client

    def acquire_lock(
        self,
        lock_key: str,
        timeout: int = 60,
        blocking: bool = False,
        blocking_timeout: float | None = None,
    ) -> Lock | None:
        """Acquire a distributed lock.

        Args:
            lock_key: Unique identifier for the lock
            timeout: Lock expiration time in seconds
            blocking: If True, wait for the lock to become available
            blocking_timeout: Max time to wait for lock if blocking

        Returns:
            Lock object if acquired, None otherwise
        """
        lock = Lock(
            self._redis_client.client,
            lock_key,
            timeout=timeout,
            blocking=blocking,
            blocking_timeout=blocking_timeout,
        )
        if lock.acquire(blocking=blocking, blocking_timeout=blocking_timeout):
            return lock
        return None

    def release_lock(self, lock: Lock) -> bool:
        """Release a distributed lock.

        Args:
            lock: Lock object to release

        Returns:
            True if released successfully, False if lock was not owned
        """
        try:
            lock.release()
            return True
        except Exception:
            return False

    @contextmanager
    def lock_context(
        self,
        lock_key: str,
        timeout: int = 60,
        blocking: bool = False,
        blocking_timeout: float | None = None,
    ) -> Generator[Lock | None, None, None]:
        """Context manager for acquiring and releasing a lock.

        Args:
            lock_key: Unique identifier for the lock
            timeout: Lock expiration time in seconds
            blocking: If True, wait for the lock to become available
            blocking_timeout: Max time to wait for lock if blocking

        Yields:
            Lock object if acquired, None otherwise
        """
        lock = self.acquire_lock(lock_key, timeout, blocking, blocking_timeout)
        try:
            yield lock
        finally:
            if lock is not None:
                self.release_lock(lock)


locking_client = LockingClient()
