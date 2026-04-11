from redis.asyncio import Redis

from src.application.exceptions import RateLimitError


class RateLimiter:
    def __init__(self, redis: Redis, prefix: str, ttl: int, max_count: int):
        self._redis = redis
        self._prefix = prefix
        self._ttl = ttl
        self._max_count = max_count

    def _get_key(self, email: str) -> str:
        return f"{self._prefix}:{email}"

    async def check_limit(self, email: str) -> None:
        key = self._get_key(email)
        current = await self._redis.incr(key)
        if current == 1:
            await self._redis.expire(key, self._ttl)
        elif current > self._max_count:
            raise RateLimitError("Лимит отправок кода по данной электронной почте превышен")

    async def reset(self, email: str) -> None:
        key = self._get_key(email)
        await self._redis.delete(key)
