"""Broker error taxonomy. The executor uses these to decide whether to retry,
block, or reconcile."""

from __future__ import annotations


class BrokerError(Exception):
    """Base class for all broker errors."""


class BrokerAuthError(BrokerError):
    """Token rejected or invalid. Bot must exit."""


class BrokerInvalidAccountError(BrokerError):
    """Account or instrument is not valid. Bot must block."""


class BrokerOrderRejectError(BrokerError):
    """4xx order validation rejection. Record, block this signal, do not retry blindly."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


class BrokerRateLimitError(BrokerError):
    """429 or temporary throttling. Safe to retry with backoff."""


class BrokerServerError(BrokerError):
    """5xx. Safe to retry idempotent GETs with backoff."""


class BrokerUnknownStatusError(BrokerError):
    """We submitted but do not know if the order took effect. Block + reconcile."""
