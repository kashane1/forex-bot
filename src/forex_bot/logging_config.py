"""JSONL logging with secret redaction.

Tokens, passwords, and known sensitive env-style keys are scrubbed before
being written to any log handler.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_SECRET_KEY_PATTERNS = re.compile(
    r"(token|secret|password|access[_-]?token|api[_-]?key|account[_-]?id)",
    re.IGNORECASE,
)

_BEARER_PATTERN = re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]+", re.IGNORECASE)
_LONG_HEX_PATTERN = re.compile(r"\b[a-f0-9]{32,}\b", re.IGNORECASE)
# OANDA-style account IDs: NNN-NNN-NNNNNNN-NNN. Keep the first triplet so logs
# remain debuggable but mask the unique digits.
_OANDA_ACCOUNT_PATTERN = re.compile(r"\b(\d{3}-\d{3})-(\d{4,10})-(\d{3})\b")
# OANDA personal access tokens: 32hex-32hex.
_OANDA_TOKEN_PATTERN = re.compile(r"\b[a-f0-9]{32}-[a-f0-9]{32}\b", re.IGNORECASE)


def _scrub_value(value: Any) -> Any:
    if isinstance(value, str):
        value = _OANDA_TOKEN_PATTERN.sub("[REDACTED_TOKEN]", value)
        value = _BEARER_PATTERN.sub(r"\1[REDACTED]", value)
        value = _OANDA_ACCOUNT_PATTERN.sub(r"\1-XXXXXXX-XXX", value)
        value = _LONG_HEX_PATTERN.sub("[REDACTED]", value)
        return value
    if isinstance(value, dict):
        return _scrub_mapping(value)
    if isinstance(value, list):
        return [_scrub_value(v) for v in value]
    return value


def _scrub_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in mapping.items():
        if _SECRET_KEY_PATTERNS.search(key):
            out[key] = "[REDACTED]"
        else:
            out[key] = _scrub_value(value)
    return out


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": _scrub_value(record.getMessage()),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            payload["extra"] = _scrub_mapping(extra)
        for key, value in record.__dict__.items():
            if key in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "message",
                "module",
                "msecs",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
                "extra",
                "taskName",
            }:
                continue
            payload[key] = _scrub_value(value)
        return json.dumps(payload, default=str, sort_keys=True)


def configure_logging(level: str = "INFO", log_path: str | Path | None = None) -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    for handler in list(root.handlers):
        try:
            handler.close()
        except Exception:
            pass
        root.removeHandler(handler)

    # httpx and httpcore emit request URLs at INFO. URLs contain account IDs.
    # Our scrubber redacts on the way out, but suppress at WARNING for defense
    # in depth.
    for noisy in ("httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    formatter = JsonFormatter()
    stream = logging.StreamHandler(sys.stderr)
    stream.setFormatter(formatter)
    root.addHandler(stream)

    if log_path:
        path = Path(log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            path,
            maxBytes=10 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
