from redis.asyncio import Redis

from src.dto.auth.register import CodeInfoDTO
from src.infrastructure.dao.registrations.interface import RegistrationsFlow


class RedisRegistrationsFlow(RegistrationsFlow):
    def __init__(self, redis: Redis, prefix: str, ttl: int, max_count: int) -> None:
        self._redis = redis
        self._prefix = prefix
        self._ttl = ttl
        self._max_count = max_count

    def _get_key(self, email: str) -> str:
        return f"{self._prefix}:{email}"

    async def create(self, data: CodeInfoDTO) -> None:
        key = self._get_key(data.email)
        await self._redis.hset(key, mapping=data.model_dump())
        await self._redis.expire(key, self._ttl)

    async def get(self, email: str) -> CodeInfoDTO | None:
        key = self._get_key(email)
        data = await self._redis.hgetall(key)
        return CodeInfoDTO(**data) if data else None

    async def update_code(self, email: str, code: str) -> None:
        key = self._get_key(email)
        await self._redis.hset(key, "code", code)
        await self._redis.expire(key, self._ttl)

    async def update_attempts(self, email: str, attempts: int) -> None:
        key = self._get_key(email)
        await self._redis.hset(key, "attempts_count", str(attempts))

    async def delete(self, email: str) -> None:
        key = self._get_key(email)
        await self._redis.delete(key)
