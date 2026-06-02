from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.crypto.derivatives_registry import (  # noqa: E402
    CANONICAL_PERPS,
    perp_underlying,
    quote_ccy,
    resolve_canonical,
    validate_perp,
    validate_venue,
    venue_symbol,
)


def test_only_btc_eth_perps_authorized():
    assert CANONICAL_PERPS == ("BTC_PERP_USD", "ETH_PERP_USD")


def test_perp_underlying_maps_to_spot():
    assert perp_underlying("BTC_PERP_USD") == "BTC_USD"
    assert perp_underlying("ETH_PERP_USD") == "ETH_USD"


def test_venue_symbol_mapping():
    assert venue_symbol("BTC_PERP_USD", "binance-usdm") == "BTCUSDT"
    assert venue_symbol("BTC_PERP_USD", "kraken-futures") == "PI_XBTUSD"
    assert venue_symbol("ETH_PERP_USD", "deribit") == "ETH-PERPETUAL"


def test_quote_ccy_flags_usdt_vs_usd():
    assert quote_ccy("BTC_PERP_USD", "binance-usdm") == "USDT"
    assert quote_ccy("BTC_PERP_USD", "kraken-futures") == "USD"


def test_resolve_canonical_reverse_map():
    assert resolve_canonical("BTCUSDT", "binance-usdm") == "BTC_PERP_USD"
    assert resolve_canonical("PI_ETHUSD", "kraken-futures") == "ETH_PERP_USD"


def test_unknown_perp_rejected():
    with pytest.raises(ValueError, match="unsupported crypto perp"):
        validate_perp("SOL_PERP_USD")


def test_bad_format_rejected():
    with pytest.raises(ValueError, match="invalid perp instrument format"):
        validate_perp("BTC_USD")


def test_unknown_venue_rejected():
    with pytest.raises(ValueError, match="unsupported derivatives venue"):
        validate_venue("ftx")


def test_altcoin_symbol_refused_on_inbound_resolve():
    with pytest.raises(ValueError, match="unauthorized / unknown"):
        resolve_canonical("SOLUSDT", "binance-usdm")
