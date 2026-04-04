import time
import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.infrastructure.logging import bind_request_context, clear_request_context, get_logger


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.logger = get_logger()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        request_id = headers.get(b"x-request-id", b"") or str(uuid.uuid4()).encode()

        request_id_str = request_id.decode() if isinstance(request_id, bytes) else str(request_id)

        bind_request_context(request_id=request_id_str)

        start_time = time.perf_counter()
        status_code: int = 500

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                nonlocal status_code
                status_code = message["status"]
                headers_list = list(message.get("headers", []))
                headers_list.append((b"x-request-id", request_id_str.encode()))
                message["headers"] = headers_list
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            self.logger.info(
                "request_processed",
                method=scope["method"],
                path=scope["path"],
                status_code=status_code,
                duration_ms=duration_ms,
            )
        except Exception:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            self.logger.exception(
                "request_failed",
                method=scope["method"],
                path=scope["path"],
                duration_ms=duration_ms,
            )
            raise
        finally:
            clear_request_context()
