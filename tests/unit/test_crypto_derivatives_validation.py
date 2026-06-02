from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.crypto.derivatives_models import (  # noqa: E402
    FundingRateRecord,
    MarkIndexRecord,
    OpenInterestRecord,
    PerpOhlcvRecord,
)
from research.crypto.derivatives_validation import (  # noqa: E402
    basis_computable,
    summarize,
    validate_funding,
    validate_mark_index,
    validate_open_interest,
    validate_perp_ohlcv,
)

T0 = datetime(2024, 6, 1, tzinfo=UTC)


def _funding(n=3, interval_h=8, canonical="BTC_PERP_USD", rate=0.0001):
    return [
        FundingRateRecord(
            canonical_id=canonical,
            venue="binance-usdm",
            venue_symbol="BTCUSDT",
            funding_time_utc=T0 + timedelta(hours=interval_h * i),
            funding_rate=rate,
            funding_interval_hours=interval_h,
        )
        for i in range(n)
    ]


def test_clean_funding_passes():
    v = validate_funding(_funding())
    assert v.status == "PASS"
    assert v.row_count == 3


def test_funding_duplicate_ts_fails():
    recs = _funding()
    recs.append(recs[0])
    v = validate_funding(recs)
    assert v.status == "FAIL"
    assert any(i.code == "duplicate_ts" for i in v.issues)


def test_funding_gap_warns():
    recs = _funding(n=2)
    recs.append(
        FundingRateRecord("BTC_PERP_USD", "binance-usdm", "BTCUSDT", T0 + timedelta(hours=40), 0.0001, 8)
    )
    v = validate_funding(recs)
    assert v.status == "WARN"
    assert any(i.code == "funding_gap" for i in v.issues)


def test_funding_outlier_warns():
    recs = _funding(rate=0.05)
    v = validate_funding(recs)
    assert any(i.code == "funding_outlier" for i in v.issues)


def test_non_btc_eth_perp_fails():
    recs = [FundingRateRecord("SOL_PERP_USD", "binance-usdm", "SOLUSDT", T0, 0.0001, 8)]
    v = validate_funding(recs)
    assert v.status == "FAIL"
    assert any(i.code == "non_btc_eth" for i in v.issues)


def test_empty_funding_warns_not_fails():
    v = validate_funding([])
    assert v.status == "WARN"


def test_open_interest_absence_is_warn():
    v = validate_open_interest([])
    assert v.status == "WARN"
    assert any(i.code == "oi_unavailable" for i in v.issues)


def test_open_interest_all_null_fails():
    recs = [OpenInterestRecord("BTC_PERP_USD", "bybit", T0, "1h", None, None)]
    v = validate_open_interest(recs)
    assert v.status == "FAIL"


def test_perp_ohlcv_insane_fails():
    recs = [PerpOhlcvRecord("BTC_PERP_USD", "binance-usdm", "BTCUSDT", "H1", T0, 1, 0.5, 2, 1, 10, "USDT")]
    v = validate_perp_ohlcv(recs)
    assert v.status == "FAIL"  # high < low


def test_perp_ohlcv_clean_passes():
    recs = [
        PerpOhlcvRecord("BTC_PERP_USD", "binance-usdm", "BTCUSDT", "H1", T0 + timedelta(hours=i), 100, 110, 90, 105, 5, "USDT")
        for i in range(3)
    ]
    v = validate_perp_ohlcv(recs)
    assert v.status == "PASS"


def test_mark_index_all_null_fails():
    recs = [MarkIndexRecord("BTC_PERP_USD", "binance-usdm", "H1", T0, None, None)]
    v = validate_mark_index(recs)
    assert v.status == "FAIL"


def test_basis_computable_overlap():
    perp = [
        PerpOhlcvRecord("BTC_PERP_USD", "binance-usdm", "BTCUSDT", "H1", T0 + timedelta(hours=i), 100, 110, 90, 105, 5, "USDT")
        for i in range(3)
    ]
    spot_times = [T0, T0 + timedelta(hours=2)]  # 2 of 3 overlap
    matched, total = basis_computable(perp, spot_times)
    assert (matched, total) == (2, 3)


def test_summarize_overall_status():
    good = validate_funding(_funding())
    bad = validate_open_interest([OpenInterestRecord("BTC_PERP_USD", "bybit", T0, "1h", None, None)])
    assert summarize([good]).get("overall_status") == "PASS"
    assert summarize([good, bad]).get("overall_status") == "FAIL"
