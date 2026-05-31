from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.crypto.registry import (
    CANONICAL_INSTRUMENTS,
    VENUE_SYMBOLS,
    half_spread_bps,
    validate_instrument,
    venue_symbol,
)


def test_canonical_instruments():
    assert CANONICAL_INSTRUMENTS == ("BTC_USD", "ETH_USD")


def test_venue_symbol_mapping():
    assert venue_symbol("BTC_USD") == "BTC-USD"
    assert venue_symbol("ETH_USD") == "ETH-USD"
    assert VENUE_SYMBOLS["BTC_USD"] == "BTC-USD"


def test_half_spread_bps():
    assert half_spread_bps("BTC_USD") == 5.0
    assert half_spread_bps("ETH_USD") == 8.0


def test_invalid_instrument_rejected():
    with pytest.raises(ValueError, match="unsupported crypto instrument"):
        validate_instrument("SOL_USD")
