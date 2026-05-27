"""OANDA practice read-only endpoint allowlist for financing capture.

No order/trade/position mutation. No live hosts. Diagnostic only.
"""

from __future__ import annotations

import re
from enum import StrEnum
from urllib.parse import urlparse

PRACTICE_REST_HOST = "https://api-fxpractice.oanda.com"
LIVE_HOST_MARKER = "api-fxtrade.oanda.com"

ALLOWED_GET_SUFFIXES: frozenset[str] = frozenset(
    {
        "",
        "/summary",
        "/transactions",
        "/transactions/sinceid",
        "/transactions/idrange",
    }
)

FORBIDDEN_PATH_FRAGMENTS: frozenset[str] = frozenset(
    {
        "/orders",
        "/trades/",
        "/positions/",
        "/openTrades",
        "/openPositions",
        "/pendingOrders",
        "/transactions/stream",
        "/configure",
        "/funding",
    }
)

FORBIDDEN_METHODS: frozenset[str] = frozenset({"POST", "PUT", "PATCH", "DELETE"})

_TOKEN_LIKE = re.compile(r"(?i)(bearer\s+|authorization\s*:)")


class ReadonlyEndpointDecision(StrEnum):
    ALLOW = "allow"
    DENY_LIVE = "deny_live"
    DENY_MUTATION = "deny_mutation"
    DENY_NOT_ALLOWLISTED = "deny_not_allowlisted"


def reject_live_host(url: str) -> None:
    if LIVE_HOST_MARKER in url:
        raise ValueError("live OANDA host refused")


def validate_readonly_get_url(url: str, account_id: str) -> ReadonlyEndpointDecision:
    """Return allow/deny decision for a GET URL. Raises on deny."""
    reject_live_host(url)
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "http"}:
        return ReadonlyEndpointDecision.DENY_NOT_ALLOWLISTED
    prefix = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}"
    if not url.startswith(prefix):
        return ReadonlyEndpointDecision.DENY_NOT_ALLOWLISTED
    tail = parsed.path[len(f"/v3/accounts/{account_id}") :]
    for frag in FORBIDDEN_PATH_FRAGMENTS:
        if frag in tail:
            return ReadonlyEndpointDecision.DENY_MUTATION
    if tail in ALLOWED_GET_SUFFIXES:
        return ReadonlyEndpointDecision.ALLOW
    if tail.startswith("/transactions/") and tail.count("/") == 2:
        seg = tail.split("/")[-1]
        if seg.isdigit():
            return ReadonlyEndpointDecision.ALLOW
    return ReadonlyEndpointDecision.DENY_NOT_ALLOWLISTED


def assert_readonly_get_url(url: str, account_id: str) -> None:
    decision = validate_readonly_get_url(url, account_id)
    if decision != ReadonlyEndpointDecision.ALLOW:
        raise RuntimeError(f"readonly URL refused: {decision.value}")


def safe_log_url(url: str) -> str:
    """URL safe for logs — never includes Authorization."""
    return url.split("?", 1)[0]


def assert_no_token_in_log_line(line: str) -> None:
    if _TOKEN_LIKE.search(line):
        raise ValueError("refusing to log authorization material")
