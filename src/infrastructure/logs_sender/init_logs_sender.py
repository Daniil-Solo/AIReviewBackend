from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging
from unittest.mock import AsyncMock

from src.infrastructure.logs_sender.loki import LokiHandler, LokiLogsSender
from src.settings import settings


@asynccontextmanager
async def init_logs_sender() -> AsyncGenerator[LokiLogsSender, None]:
    if not settings.logging.LOKI_ENABLED:
        yield AsyncMock(spec=LokiLogsSender)
        return

    sender = LokiLogsSender(
        url=settings.logging.LOKI_URL,
        flush_interval=settings.logging.LOKI_FLUSH_INTERVAL,
        batch_size=settings.logging.LOKI_BATCH_SIZE,
        max_buffer_size=settings.logging.LOKI_MAX_BUFFER_SIZE,
        labels={"service": settings.APP, "env": settings.ENV},
    )

    root_logger = logging.getLogger()
    loki_handler = LokiHandler(sender=sender)
    root_logger.addHandler(loki_handler)

    await sender.start()
    yield sender
    await sender.stop()
