"""Unit tests for synthetic weekly volatility features (CAMPAIGN_017)."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytest

from forex_bot.features.weekly_volatility import (
    aggregate_h4_to_weekly_ohlc,
    breakout_already_consumed,
    completed_weeks_before,
    compute_h4_atr_buffer,
    label_weekly_compression,
    latest_completed_compressed_week,
    week_start_monday_utc,
)


def _ts(y, m, d, h=0):
    return pd.Timestamp(datetime(y, m, d, h, tzinfo=UTC))


def test_week_start_monday_utc_deterministic():
    wed = _ts(2024, 3, 13, 12)
    assert week_start_monday_utc(wed) == _ts(2024, 3, 11, 0)


def test_aggregate_h4_to_weekly_ohlc():
    idx = pd.DatetimeIndex(
        [
            _ts(2024, 3, 11, 0),
            _ts(2024, 3, 11, 4),
            _ts(2024, 3, 11, 8),
            _ts(2024, 3, 18, 0),
        ]
    )
    opens = pd.Series([1.0, 1.05, 1.1, 1.5], index=idx)
    highs = pd.Series([1.1, 1.15, 1.2, 1.6], index=idx)
    lows = pd.Series([0.9, 0.95, 1.0, 1.4], index=idx)
    closes = pd.Series([1.0, 1.1, 1.2, 1.5], index=idx)
    weekly = aggregate_h4_to_weekly_ohlc(idx, opens, highs, lows, closes)
    assert len(weekly) == 2
    assert weekly.iloc[0]["open"] == pytest.approx(1.0)
    assert weekly.iloc[0]["close"] == pytest.approx(1.2)
    assert weekly.iloc[0]["true_range"] == pytest.approx(1.2 - 0.9)


def test_weekly_true_range_is_high_minus_low():
    idx = pd.DatetimeIndex([_ts(2024, 3, 11, 0), _ts(2024, 3, 18, 0)])
    o = pd.Series([1.0, 1.0], index=idx)
    h = pd.Series([1.5, 2.0], index=idx)
    lo = pd.Series([0.5, 1.0], index=idx)
    c = pd.Series([1.0, 1.5], index=idx)
    weekly = aggregate_h4_to_weekly_ohlc(idx, o, h, lo, c)
    assert weekly.iloc[0]["true_range"] == pytest.approx(1.0)
    assert weekly.iloc[1]["true_range"] == pytest.approx(1.0)


def test_compression_percentile_threshold():
    idx = pd.date_range("2024-01-01", periods=14, freq="7D", tz="UTC")
    tr_values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 0.5, 0.5]
    weekly = pd.DataFrame(
        {
            "open": tr_values,
            "high": [v + 0.1 for v in tr_values],
            "low": [0.0] * len(tr_values),
            "close": tr_values,
            "true_range": tr_values,
        },
        index=idx,
    )
    labeled = label_weekly_compression(
        weekly, compression_lookback_weeks=12, compression_percentile_threshold=25,
    )
    assert not labeled.iloc[10]["is_compressed"]
    assert labeled.iloc[-1]["is_compressed"]


def test_incomplete_week_excluded_from_completed():
    idx = pd.date_range("2024-01-01", periods=3, freq="7D", tz="UTC")
    weekly = pd.DataFrame(
        {"open": [1, 1, 1], "high": [2, 2, 2], "low": [0, 0, 0],
         "close": [1, 1, 1], "true_range": [2, 2, 2]},
        index=idx,
    )
    completed = completed_weeks_before(weekly, _ts(2024, 1, 17, 4))
    assert len(completed) == 2


def test_no_lookahead_compression_label():
    idx = pd.date_range("2024-01-01", periods=13, freq="7D", tz="UTC")
    tr = [5.0] * 12 + [0.1]
    weekly = pd.DataFrame(
        {"open": tr, "high": tr, "low": [0.0] * 13, "close": tr, "true_range": tr},
        index=idx,
    )
    labeled = label_weekly_compression(
        weekly, compression_lookback_weeks=12, compression_percentile_threshold=25,
    )
    cw = latest_completed_compressed_week(labeled, _ts(2024, 3, 25, 0))
    assert cw is not None
    assert cw["compressed_week_start"] == idx[-2]


def test_latest_compressed_week_range():
    idx = pd.date_range("2024-01-01", periods=13, freq="7D", tz="UTC")
    highs = [1.1] * 11 + [1.05, 1.05]
    lows = [0.9] * 11 + [0.95, 0.95]
    tr = [h - lo for h, lo in zip(highs, lows, strict=True)]
    weekly = pd.DataFrame(
        {"open": [1.0] * 13, "high": highs, "low": lows, "close": [1.0] * 13,
         "true_range": tr},
        index=idx,
    )
    labeled = label_weekly_compression(
        weekly, compression_lookback_weeks=12, compression_percentile_threshold=25,
    )
    cw = latest_completed_compressed_week(labeled, _ts(2024, 3, 25, 0))
    assert cw is not None
    assert cw["compressed_week_high"] == pytest.approx(1.05)
    assert cw["compressed_week_low"] == pytest.approx(0.95)


def test_h4_atr_buffer_without_future_bars():
    idx = pd.date_range("2024-01-01", periods=20, freq="4h", tz="UTC")
    close = pd.Series([1.0 + 0.001 * i for i in range(20)], index=idx)
    high = close + 0.002
    low = close - 0.002
    atr_val, buf = compute_h4_atr_buffer(high, low, close, 14, 0.25)
    assert atr_val is not None and atr_val > 0
    assert buf == pytest.approx(0.25 * atr_val)


def test_breakout_already_consumed():
    idx = pd.date_range("2024-03-18", periods=5, freq="4h", tz="UTC")
    closes = pd.Series([1.0, 1.05, 1.2, 1.15, 1.18], index=idx)
    week_end = _ts(2024, 3, 18, 0)
    consumed = breakout_already_consumed(
        timestamps=idx,
        closes=closes,
        week_end=week_end,
        current_index=idx[-1],
        compressed_high=1.0,
        compressed_low=0.9,
        buffer=0.01,
    )
    assert consumed is True


def test_missing_bars_handled_deterministically():
    weekly = pd.DataFrame(columns=["open", "high", "low", "close", "true_range"])
    labeled = label_weekly_compression(
        weekly, compression_lookback_weeks=12, compression_percentile_threshold=25,
    )
    assert labeled.empty
    assert latest_completed_compressed_week(labeled, _ts(2024, 1, 1)) is None
