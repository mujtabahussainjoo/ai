"""Structured JSON logging with request-scoped context."""

from __future__ import annotations

import json
import logging
import threading
from collections import deque
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = request_id_var.get()
        if request_id:
            payload["request_id"] = request_id
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)
        return json.dumps(payload, default=str, sort_keys=True)


class RingBufferHandler(logging.Handler):
    """Keep the most recent structured log records in memory for the admin logs API.

    Uses the same payload shape as JsonFormatter so the /admin/logs endpoint can
    return records without re-formatting them.
    """

    def __init__(self, max_records: int = 400) -> None:
        super().__init__(level=logging.NOTSET)
        self._buffer: deque[dict[str, Any]] = deque(maxlen=max_records)
        self._lock = threading.Lock()
        self._formatter = logging.Formatter()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry: dict[str, Any] = {
                "ts": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            request_id = request_id_var.get()
            if request_id:
                entry["request_id"] = request_id
            if record.exc_info:
                entry["exc_info"] = self._formatter.formatException(record.exc_info)
            extra = getattr(record, "extra_fields", None)
            if isinstance(extra, dict):
                for key, value in extra.items():
                    entry[key] = value
            with self._lock:
                self._buffer.append(entry)
        except Exception:
            self.handleError(record)

    def snapshot(self, *, min_level: int, limit: int) -> list[dict[str, Any]]:
        with self._lock:
            records = list(self._buffer)
        filtered = [r for r in records if (r.get("level") or "INFO") in _LEVEL_RANK]
        ordered = [
            r for r in filtered if (_LEVEL_RANK.get(r["level"]) or 0) >= min_level
        ]
        return ordered[-limit:]


_LEVEL_RANK = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

ring_buffer = RingBufferHandler()


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler, ring_buffer]
    root.setLevel(level.upper())

    # Quiet noisy transport libs; our structured logs carry the signal.
    for noisy in ("uvicorn.access", "httpx", "httpcore", "aiosqlite"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
        logging.getLogger(noisy).propagate = False


def recent_logs(*, min_level: str = "WARNING", limit: int = 100) -> list[dict[str, Any]]:
    """Return the most recent buffered log records at or above min_level."""
    return ring_buffer.snapshot(
        min_level=_LEVEL_RANK.get(min_level.upper(), logging.WARNING),
        limit=limit,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


logger = get_logger("myaibuddy")
