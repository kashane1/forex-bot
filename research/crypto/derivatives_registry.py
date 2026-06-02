"""Canonical crypto **derivatives** instrument registry (BTC/ETH perps only).

Spot registry lives in ``research/crypto/registry.py`` and is unchanged. This
module adds perpetual canonical IDs and venue-native symbol resolution with hard
BTC/ETH-only guards. See CRYPTO_DERIVATIVES_DATA_MODEL.md §1.
"""

from __future__ import annotations

import re

# Authorized perpetual instruments — BTC and ETH only. No altcoins, no third perp.
CANONICAL_PERPS: tuple[str, ...] = ("BTC_PERP_USD", "ETH_PERP_USD")

# Perp -> underlying spot canonical (spot IDs from research/crypto/registry.py).
PERP_UNDERLYING: dict[str, str] = {
    "BTC_PERP_USD": "BTC_USD",
    "ETH_PERP_USD": "ETH_USD",
}

# venue -> {canonical_perp: (native_symbol, quote_ccy)}.
# USDT-quoted (linear) series are flagged non-interchangeable with USD without
# basis adjustment; inverse-USD perps are true USD-quoted.
VENUE_NATIVE_SYMBOLS: dict[str, dict[str, tuple[str, str]]] = {
    "binance-usdm": {
        "BTC_PERP_USD": ("BTCUSDT", "USDT"),
        "ETH_PERP_USD": ("ETHUSDT", "USDT"),
    },
    "bybit": {
        "BTC_PERP_USD": ("BTCUSDT", "USDT"),
        "ETH_PERP_USD": ("ETHUSDT", "USDT"),
    },
    "kraken-futures": {
        "BTC_PERP_USD": ("PI_XBTUSD", "USD"),
        "ETH_PERP_USD": ("PI_ETHUSD", "USD"),
    },
    "okx": {
        "BTC_PERP_USD": ("BTC-USDT-SWAP", "USDT"),
        "ETH_PERP_USD": ("ETH-USDT-SWAP", "USDT"),
    },
    "deribit": {
        "BTC_PERP_USD": ("BTC-PERPETUAL", "USD"),
        "ETH_PERP_USD": ("ETH-PERPETUAL", "USD"),
    },
}

SUPPORTED_VENUES: tuple[str, ...] = tuple(VENUE_NATIVE_SYMBOLS)

_PERP_RE = re.compile(r"^[A-Z]{3,4}_PERP_USD$")


def validate_perp(canonical_id: str) -> str:
    """Return ``canonical_id`` if it is an authorized BTC/ETH perp, else raise."""
    if not _PERP_RE.match(canonical_id):
        raise ValueError(f"invalid perp instrument format: {canonical_id}")
    if canonical_id not in CANONICAL_PERPS:
        raise ValueError(f"unsupported crypto perp instrument: {canonical_id}")
    return canonical_id


def validate_venue(venue: str) -> str:
    if venue not in VENUE_NATIVE_SYMBOLS:
        raise ValueError(f"unsupported derivatives venue: {venue}")
    return venue


def perp_underlying(canonical_id: str) -> str:
    validate_perp(canonical_id)
    return PERP_UNDERLYING[canonical_id]


def venue_symbol(canonical_id: str, venue: str) -> str:
    validate_perp(canonical_id)
    validate_venue(venue)
    return VENUE_NATIVE_SYMBOLS[venue][canonical_id][0]


def quote_ccy(canonical_id: str, venue: str) -> str:
    validate_perp(canonical_id)
    validate_venue(venue)
    return VENUE_NATIVE_SYMBOLS[venue][canonical_id][1]


def resolve_canonical(native_symbol: str, venue: str) -> str:
    """Reverse-map a venue-native symbol to its authorized canonical perp.

    Raises ``ValueError`` for any symbol that is not an authorized BTC/ETH perp
    on that venue — this is the BTC/ETH-only guard for inbound payloads.
    """
    validate_venue(venue)
    for canonical_id, (native, _quote) in VENUE_NATIVE_SYMBOLS[venue].items():
        if native == native_symbol:
            return canonical_id
    raise ValueError(f"unauthorized / unknown {venue} symbol: {native_symbol!r}")
