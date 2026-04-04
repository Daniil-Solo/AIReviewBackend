import asyncio
from collections import deque
from contextlib import suppress
import json
import logging
import threading
import time

import httpx

from src.infrastructure.logging.format import build_log_dict


class LokiLogsSender:
    def __init__(
        self, url: str, flush_interval: float, batch_size: int, max_buffer_size: int, labels: dict[str, str]
    ) -> None:
        self._url = f"{url.rstrip('/')}/loki/api/v1/push"
        self._labels = labels
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._max_buffer_size = max_buffer_size
        self._buffer: deque[tuple[int, str]] = deque(maxlen=max_buffer_size)
        self._lock = threading.Lock()
        self._task: asyncio.Task[None] | None = None
        self._running = False
        self._client = httpx.AsyncClient(timeout=5.0)
        self._stats = {"sent": 0, "dropped": 0}

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._flush_timer())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        await self.flush()
        await self._client.aclose()

    async def flush(self) -> None:
        if not self._buffer:
            return

        with self._lock:
            batch = list(self._buffer)
            self._buffer.clear()

        streams = {
            "stream": self._labels,
            "values": [[str(ts_ns), log_line] for ts_ns, log_line in batch],
        }
        payload = {"streams": [streams]}

        try:
            await self._client.post(self._url, json=payload)
            self._stats["sent"] += len(batch)
        except Exception:
            self._stats["dropped"] += len(batch)

    def add_log(self, log_line: str) -> None:
        ts_ns = int(time.time() * 1_000_000_000)
        with self._lock:
            if len(self._buffer) >= self._max_buffer_size:
                self._buffer.popleft()
                self._stats["dropped"] += 1
            self._buffer.append((ts_ns, log_line))

        if len(self._buffer) >= self._batch_size:
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(lambda: asyncio.create_task(self.flush()))
            except RuntimeError:
                pass

    async def _flush_timer(self) -> None:
        while self._running:
            await asyncio.sleep(self._flush_interval)
            await self.flush()

    @property
    def stats(self) -> dict[str, int]:
        return self._stats.copy()


class LokiHandler(logging.Handler):
    def __init__(self, sender: LokiLogsSender) -> None:
        super().__init__()
        self._sender = sender

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_line = json.dumps(
                build_log_dict(
                    record=record,
                ),
                ensure_ascii=False,
            )
            self._sender.add_log(log_line)
        except Exception:
            self.handleError(record)
