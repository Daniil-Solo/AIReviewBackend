from datetime import UTC, datetime
import logging
import traceback
from typing import Any

from structlog.contextvars import get_contextvars

from src.settings import settings


def build_log_dict(
    record: logging.LogRecord,
) -> dict[str, Any]:
    log_dict: dict[str, Any] = {
        "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
        "level": record.levelname,
        "message": record.getMessage(),
        "logger": record.name,
        "service": settings.APP,
        "env": settings.ENV,
        "module": record.module,
        "function": record.funcName,
        "line": record.lineno,
        "process_id": record.process,
    }
    if context := get_contextvars():
        log_dict["context"] = dict(context)

    if record.exc_info and record.exc_info != (None, None, None):
        log_dict["exc_info"] = "".join(
            traceback.format_exception(record.exc_info[0], record.exc_info[1], record.exc_info[2])
        )
    elif record.exc_text:
        log_dict["exc_info"] = record.exc_text

    return log_dict
