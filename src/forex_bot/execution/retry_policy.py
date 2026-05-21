"""Retry policy for safe GETs and broker stream re-connects.

Mutating endpoints (order submit, close) NEVER retry blindly — see the
executor for the idempotency-check-first policy.
"""

from __future__ import annotations

from dataclasses import dataclass

from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from forex_bot.broker.errors import BrokerRateLimitError, BrokerServerError


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_seconds: float = 0.5
    max_seconds: float = 5.0

    def for_safe_get(self) -> Retrying:
        return Retrying(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential_jitter(initial=self.base_seconds, max=self.max_seconds),
            retry=retry_if_exception_type((BrokerRateLimitError, BrokerServerError)),
            reraise=True,
        )
