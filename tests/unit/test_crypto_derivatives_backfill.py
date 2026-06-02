from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.crypto.derivatives_backfill import (  # noqa: E402
    DAY_MS,
    HOUR_MS,
    chunk_time_windows,
    expected_hourly_rows,
)
from research.crypto.derivatives_sources import (  # noqa: E402
    parse_deribit_chart,
    parse_deribit_funding,
    parse_deribit_index_from_funding,
    parse_okx_oi_volume,
)

FIX = ROOT / "research" / "crypto" / "fixtures" / "derivatives"


def _load(name: str):
    return json.loads((FIX / name).read_text())


# --- chunking ---------------------------------------------------------------


def test_chunk_time_windows_basic():
    w = chunk_time_windows(0, 100, 30)
    assert w[0] == (0, 29)
    assert w[-1][1] == 100
    # contiguous, non-overlapping
    for (_a, b), (c, _d) in zip(w, w[1:], strict=False):
        assert c == b + 1


def test_chunk_time_windows_single():
    assert chunk_time_windows(0, 10, 1000) == [(0, 10)]


def test_chunk_time_windows_invalid():
    with pytest.raises(ValueError):
        chunk_time_windows(10, 0, 5)
    with pytest.raises(ValueError):
        chunk_time_windows(0, 10, 0)


def test_expected_hourly_rows():
    assert expected_hourly_rows(0, HOUR_MS) == 2
    assert expected_hourly_rows(0, DAY_MS) == 25


# --- Deribit / OKX-rubik parsers -------------------------------------------


def test_parse_deribit_funding_uses_interest_1h_hourly():
    recs = parse_deribit_funding(_load("deribit_funding_btc.json")["result"], canonical_id="BTC_PERP_USD")
    assert len(recs) == 3
    assert all(r.funding_interval_hours == 1 for r in recs)
    assert all(r.venue == "deribit" for r in recs)
    assert recs[0].funding_rate == pytest.approx(0.00001)
    assert recs[0].venue_symbol == "BTC-PERPETUAL"


def test_parse_deribit_index_from_funding():
    recs = parse_deribit_index_from_funding(_load("deribit_funding_btc.json")["result"], canonical_id="BTC_PERP_USD")
    assert len(recs) == 3
    assert recs[0].index_close == pytest.approx(68000.5)
    assert recs[0].mark_close is None


def test_parse_deribit_chart():
    recs = parse_deribit_chart(_load("deribit_chart_btc.json")["result"], canonical_id="BTC_PERP_USD", granularity="H1")
    assert len(recs) == 3
    assert recs[0].quote_ccy == "USD"
    assert all(r.high >= r.low for r in recs)
    assert recs[0].venue_symbol == "BTC-PERPETUAL"


def test_parse_okx_oi_volume_usd_notional():
    recs = parse_okx_oi_volume(_load("okx_oi_volume_btc.json"), canonical_id="BTC_PERP_USD")
    assert len(recs) == 2
    assert recs[0].open_interest_usd is not None
    assert recs[0].open_interest_base is None
    assert recs[0].interval == "1D"
    assert [r.time_utc for r in recs] == sorted(r.time_utc for r in recs)
