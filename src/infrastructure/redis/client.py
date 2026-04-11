from unittest.mock import AsyncMock

from redis.asyncio import Redis

from src.settings import settings


async def init_redis_client() -> Redis:
    if not settings.redis.ENABLED:
        return AsyncMock(spec=Redis)
    return Redis(
        host=settings.redis.HOST,
        port=settings.redis.PORT,
        db=settings.redis.DB,
        password=settings.redis.PASSWORD,
        encoding="utf-8",
        decode_responses=True,
    )
