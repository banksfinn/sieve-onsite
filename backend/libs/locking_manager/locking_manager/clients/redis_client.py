import redis

from locking_manager.core.settings import locking_manager_settings


class RedisClient:
    """Simple Redis client wrapper."""

    def __init__(self, redis_url: str | None = None):
        self._redis_url = redis_url or locking_manager_settings.REDIS_URL
        self._client: redis.Redis | None = None

    @property
    def client(self) -> redis.Redis:
        """Lazily initialize and return the Redis client."""
        if self._client is None:
            self._client = redis.from_url(self._redis_url, decode_responses=True)  # type: ignore[reportUnknownMemberType]
        return self._client

    def ping(self) -> bool:
        """Check if Redis is reachable."""
        try:
            result = self.client.ping()  # type: ignore[reportUnknownMemberType]
            return bool(result)
        except redis.ConnectionError:
            return False


redis_client = RedisClient()
