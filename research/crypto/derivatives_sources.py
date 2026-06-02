"""Public-only derivatives source adapters: endpoint allowlist, safety guards,
and venue payload parsers → canonical records.

Hard safety posture (CRYPTO_DERIVATIVES_PUBLIC_DATA_SOURCE_REVIEW.md §8):
- public market-data endpoints only (explicit allowlist);
- no API key, no signature, no account / order / position / leverage endpoint;
- a guard that refuses to proceed if an API-key-shaped env var would be required.

Parsers accept venue-shaped payloads (mirrored by the synthetic fixtures) and
emit the dataclasses from ``derivatives_models``. No network I/O lives in this
module — fetching is done by the dry-run-default script.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import urlparse

from research.crypto.derivatives_models import (
    FundingRateRecord,
    MarkIndexRecord,
    OpenInterestRecord,
    PerpOhlcvRecord,
)
from research.crypto.derivatives_registry import (
    quote_ccy,
    resolve_canonical,
    venue_symbol,
)

DataClass = Literal["funding", "open_interest", "mark_index", "perp_ohlcv"]

# Allowlisted PUBLIC market-data base URLs. Any URL whose host is not exactly one
# of these is refused. Private/authenticated hosts (e.g. *.binance.com signed
# endpoints) are simply absent from the list.
PUBLIC_BASE_URLS: dict[str, str] = {
    "binance-usdm": "https://fapi.binance.com",
    "bybit": "https://api.bybit.com",
    "kraken-futures": "https://futures.kraken.com",
    "okx": "https://www.okx.com",
    "deribit": "https://www.deribit.com",
}

# Substrings that must never appear in a market-data path/query — they indicate
# private/account/trading surfaces.
_FORBIDDEN_URL_MARKERS: tuple[str, ...] = (
    "/order",
    "/account",
    "/position",
    "/leverage",
    "/margin",
    "/private",
    "/withdraw",
    "/transfer",
    "/userDataStream",
    "apiKey=",
    "signature=",
    "api_key=",
    "sign=",
)

# Env var name fragments that look like exchange credentials. If a public adapter
# would require any of these, we refuse — public data must need no credential.
_CREDENTIAL_ENV_MARKERS: tuple[str, ...] = (
    "API_KEY",
    "API_SECRET",
    "APIKEY",
    "SECRET_KEY",
    "PASSPHRASE",
    "PRIVATE_KEY",
)


class UnsafeSourceError(RuntimeError):
    """Raised when a requested fetch would violate the public-only posture."""


@dataclass(frozen=True)
class SourceEndpoint:
    venue: str
    data_class: DataClass
    path: str
    note: str = ""


# Documented public endpoints per venue/data-class (paths re-confirmed at pilot).
PUBLIC_ENDPOINTS: tuple[SourceEndpoint, ...] = (
    SourceEndpoint("binance-usdm", "funding", "/fapi/v1/fundingRate", "8h funding history"),
    SourceEndpoint("binance-usdm", "perp_ohlcv", "/fapi/v1/klines", "perp candles"),
    SourceEndpoint("binance-usdm", "mark_index", "/fapi/v1/markPriceKlines", "mark price candles"),
    SourceEndpoint("bybit", "open_interest", "/v5/market/open-interest", "OI history"),
    SourceEndpoint("bybit", "funding", "/v5/market/funding/history", "8h funding history"),
    SourceEndpoint("kraken-futures", "funding", "/derivatives/api/v3/historicalfundingrates", "USD perp funding"),
    SourceEndpoint("okx", "funding", "/api/v5/public/funding-rate-history", "8h funding history"),
    SourceEndpoint("okx", "open_interest", "/api/v5/public/open-interest", "current OI snapshot"),
)


def is_public_url(url: str) -> bool:
    """True only if ``url`` is on an allowlisted public host with no private marker."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False
    allowed_hosts = {urlparse(base).netloc for base in PUBLIC_BASE_URLS.values()}
    if parsed.netloc not in allowed_hosts:
        return False
    lowered = url.lower()
    return not any(marker.lower() in lowered for marker in _FORBIDDEN_URL_MARKERS)


def assert_public_url(url: str) -> str:
    if not is_public_url(url):
        raise UnsafeSourceError(f"refusing non-public / non-allowlisted URL: {url!r}")
    return url


def assert_no_credentials_required(environ: dict[str, str] | None = None) -> None:
    """Refuse if any credential-shaped env var is present that an adapter might use.

    Public market data needs no credentials; the mere presence of an exchange key
    in the environment is treated as a signal that the operator may be reaching
    for an authenticated path. We fail loudly rather than silently authenticate.
    """
    env = environ or {}
    offending = [
        name
        for name in env
        if any(marker in name.upper() for marker in _CREDENTIAL_ENV_MARKERS)
        and any(ex in name.upper() for ex in ("BINANCE", "BYBIT", "KRAKEN", "OKX", "DERIBIT", "COINBASE"))
    ]
    if offending:
        raise UnsafeSourceError(
            "exchange credential env vars present; this layer is public-only and "
            f"must not authenticate: {sorted(offending)}"
        )


def endpoint_for(venue: str, data_class: DataClass) -> SourceEndpoint:
    for ep in PUBLIC_ENDPOINTS:
        if ep.venue == venue and ep.data_class == data_class:
            return ep
    raise UnsafeSourceError(f"no public endpoint registered for {venue}/{data_class}")


def build_request_url(venue: str, data_class: DataClass) -> str:
    base = PUBLIC_BASE_URLS.get(venue)
    if base is None:
        raise UnsafeSourceError(f"unsupported venue: {venue}")
    url = base + endpoint_for(venue, data_class).path
    return assert_public_url(url)


def _ms_to_utc(value: int | str | float) -> datetime:
    return datetime.fromtimestamp(int(value) / 1000.0, tz=UTC)


# ---------------------------------------------------------------------------
# Parsers — venue payload shapes mirrored by research/crypto/fixtures/derivatives
# ---------------------------------------------------------------------------


def parse_binance_funding(
    payload: list[dict[str, Any]], *, venue: str = "binance-usdm"
) -> list[FundingRateRecord]:
    """Binance USDⓈ-M ``/fapi/v1/fundingRate`` → FundingRateRecord list."""
    out: list[FundingRateRecord] = []
    for row in payload:
        canonical = resolve_canonical(str(row["symbol"]), venue)
        out.append(
            FundingRateRecord(
                canonical_id=canonical,
                venue=venue,
                venue_symbol=str(row["symbol"]),
                funding_time_utc=_ms_to_utc(row["fundingTime"]),
                funding_rate=float(row["fundingRate"]),
                funding_interval_hours=8,
                mark_price=float(row["markPrice"]) if row.get("markPrice") not in (None, "") else None,
            )
        )
    out.sort(key=lambda r: r.funding_time_utc)
    return _dedup(out, key=lambda r: r.funding_time_utc)


def parse_binance_perp_klines(
    payload: list[list[Any]],
    *,
    canonical_id: str,
    granularity: str,
    venue: str = "binance-usdm",
) -> list[PerpOhlcvRecord]:
    """Binance ``/fapi/v1/klines`` arrays → PerpOhlcvRecord list.

    Array layout: [openTime, open, high, low, close, volume, closeTime, ...].
    """
    native = venue_symbol(canonical_id, venue)
    quote = quote_ccy(canonical_id, venue)
    out: list[PerpOhlcvRecord] = []
    for row in payload:
        if len(row) < 6:
            continue
        out.append(
            PerpOhlcvRecord(
                canonical_id=canonical_id,
                venue=venue,
                venue_symbol=native,
                granularity=granularity,
                time_utc=_ms_to_utc(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                quote_ccy=quote,
            )
        )
    out.sort(key=lambda r: r.time_utc)
    return _dedup(out, key=lambda r: r.time_utc)


def parse_binance_mark_klines(
    payload: list[list[Any]],
    *,
    canonical_id: str,
    granularity: str,
    venue: str = "binance-usdm",
) -> list[MarkIndexRecord]:
    """Binance ``/fapi/v1/markPriceKlines`` arrays → MarkIndexRecord (mark close)."""
    out: list[MarkIndexRecord] = []
    for row in payload:
        if len(row) < 5:
            continue
        out.append(
            MarkIndexRecord(
                canonical_id=canonical_id,
                venue=venue,
                granularity=granularity,
                time_utc=_ms_to_utc(row[0]),
                mark_close=float(row[4]),
                index_close=None,
            )
        )
    out.sort(key=lambda r: r.time_utc)
    return _dedup(out, key=lambda r: r.time_utc)


def parse_bybit_open_interest(
    payload: dict[str, Any],
    *,
    canonical_id: str,
    interval: str,
    venue: str = "bybit",
) -> list[OpenInterestRecord]:
    """Bybit v5 ``/v5/market/open-interest`` → OpenInterestRecord list.

    Payload shape: ``{"result": {"list": [{"openInterest": ..., "timestamp": ms}]}}``.
    """
    rows = payload.get("result", {}).get("list", [])
    out: list[OpenInterestRecord] = []
    for row in rows:
        out.append(
            OpenInterestRecord(
                canonical_id=canonical_id,
                venue=venue,
                time_utc=_ms_to_utc(row["timestamp"]),
                interval=interval,
                open_interest_base=float(row["openInterest"]) if row.get("openInterest") not in (None, "") else None,
                open_interest_usd=float(row["openInterestValue"]) if row.get("openInterestValue") not in (None, "") else None,
            )
        )
    out.sort(key=lambda r: r.time_utc)
    return _dedup(out, key=lambda r: r.time_utc)


def parse_okx_funding(
    payload: dict[str, Any], *, venue: str = "okx"
) -> list[FundingRateRecord]:
    """OKX ``/api/v5/public/funding-rate-history`` → FundingRateRecord list.

    Payload shape: ``{"code": "0", "data": [{"instId", "fundingRate", "fundingTime"}]}``.
    """
    out: list[FundingRateRecord] = []
    for row in payload.get("data", []):
        canonical = resolve_canonical(str(row["instId"]), venue)
        out.append(
            FundingRateRecord(
                canonical_id=canonical,
                venue=venue,
                venue_symbol=str(row["instId"]),
                funding_time_utc=_ms_to_utc(row["fundingTime"]),
                funding_rate=float(row["fundingRate"]),
                funding_interval_hours=8,
            )
        )
    out.sort(key=lambda r: r.funding_time_utc)
    return _dedup(out, key=lambda r: r.funding_time_utc)


def parse_okx_open_interest(
    payload: dict[str, Any], *, interval: str = "snapshot", venue: str = "okx"
) -> list[OpenInterestRecord]:
    """OKX ``/api/v5/public/open-interest`` → OpenInterestRecord list (current snapshot)."""
    out: list[OpenInterestRecord] = []
    for row in payload.get("data", []):
        canonical = resolve_canonical(str(row["instId"]), venue)
        out.append(
            OpenInterestRecord(
                canonical_id=canonical,
                venue=venue,
                time_utc=_ms_to_utc(row["ts"]),
                interval=interval,
                open_interest_base=float(row["oiCcy"]) if row.get("oiCcy") not in (None, "") else None,
                open_interest_usd=float(row["oiUsd"]) if row.get("oiUsd") not in (None, "") else None,
            )
        )
    out.sort(key=lambda r: r.time_utc)
    return _dedup(out, key=lambda r: r.time_utc)


def count_payload_rows(payload: Any) -> int:
    """Best-effort row count across venue payload shapes (list / result.list / data)."""
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        if "data" in payload and isinstance(payload["data"], list):
            return len(payload["data"])
        return len(payload.get("result", {}).get("list", []))
    return 0


def _dedup(records: list[Any], *, key: Any) -> list[Any]:
    seen: set[Any] = set()
    out: list[Any] = []
    for rec in records:
        k = key(rec)
        if k in seen:
            continue
        seen.add(k)
        out.append(rec)
    return out
