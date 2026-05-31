"""Canonical crypto instrument registry for research ingestion."""

from __future__ import annotations

CANONICAL_INSTRUMENTS: tuple[str, ...] = ("BTC_USD", "ETH_USD")

PRIMARY_VENUE = "coinbase"

VENUE_SYMBOLS: dict[str, str] = {
    "BTC_USD": "BTC-USD",
    "ETH_USD": "ETH-USD",
}

# Assumed half-spread in basis points (see CRYPTO_DATA_VALIDATION_REQUIREMENTS.md).
HALF_SPREAD_BPS: dict[str, float] = {
    "BTC_USD": 5.0,
    "ETH_USD": 8.0,
}

CRYPTO_SOURCE = "coinbase-spot"

CRYPTO_MATERIALIZED_FROM_M1: tuple[str, ...] = ("M5", "M15", "H1", "H4", "D1")

_INSTRUMENT_RE = __import__("re").compile(r"^[A-Z]{3,4}_USD$")


def validate_instrument(instrument: str) -> str:
    if instrument not in CANONICAL_INSTRUMENTS:
        raise ValueError(f"unsupported crypto instrument: {instrument}")
    if not _INSTRUMENT_RE.match(instrument):
        raise ValueError(f"invalid crypto instrument format: {instrument}")
    return instrument


def venue_symbol(instrument: str) -> str:
    validate_instrument(instrument)
    return VENUE_SYMBOLS[instrument]


def half_spread_bps(instrument: str) -> float:
    validate_instrument(instrument)
    return HALF_SPREAD_BPS[instrument]
