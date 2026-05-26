"""Unit tests for synthetic weekly momentum features (CAMPAIGN_016)."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytest

from forex_bot.features.weekly_momentum import (
    aggregate_h4_to_weekly_closes,
    is_rebalance_bar,
    rank_pairs_by_score,
    vol_adjusted_momentum_score,
    week_id,
    week_start_monday_utc,
    weekly_return_over_weeks,
    weekly_volatility,
)


def _ts(y, m, d, h=0):
    return pd.Timestamp(datetime(y, m, d, h, tzinfo=UTC))


def test_week_start_monday_utc_deterministic():
    wed = _ts(2024, 3, 13, 12)
    assert week_start_monday_utc(wed) == _ts(2024, 3, 11, 0)
    mon = _ts(2024, 3, 11, 8)
    assert week_start_monday_utc(mon) == _ts(2024, 3, 11, 0)


def test_week_id_stable():
    a = _ts(2024, 1, 2, 4)
    b = _ts(2024, 1, 7, 20)
    assert week_id(a) == week_id(b)


def test_aggregate_h4_to_weekly_closes_last_close_per_week():
    idx = pd.DatetimeIndex(
        [
            _ts(2024, 3, 11, 0),
            _ts(2024, 3, 11, 4),
            _ts(2024, 3, 11, 8),
            _ts(2024, 3, 18, 0),
        ]
    )
    closes = pd.Series([1.0, 1.1, 1.2, 1.5], index=idx)
    weekly = aggregate_h4_to_weekly_closes(idx, closes)
    assert len(weekly) == 2
    assert weekly.iloc[0] == pytest.approx(1.2)
    assert weekly.iloc[1] == pytest.approx(1.5)


def test_aggregate_rejects_non_monotonic():
    idx = pd.DatetimeIndex([_ts(2024, 3, 12), _ts(2024, 3, 11)])
    closes = pd.Series([1.0, 1.1], index=idx)
    with pytest.raises(ValueError, match="monotonic"):
        aggregate_h4_to_weekly_closes(idx, closes)


def test_is_rebalance_bar_first_bar_of_week():
    t0 = _ts(2024, 3, 11, 0)
    t1 = _ts(2024, 3, 11, 4)
    t2 = _ts(2024, 3, 18, 0)
    assert not is_rebalance_bar(t0, None)
    assert not is_rebalance_bar(t1, t0)
    assert is_rebalance_bar(t2, t1)


def test_weekly_return_no_lookahead():
    weeks = pd.Series(
        [1.0, 1.1, 1.2, 1.3, 1.4],
        index=pd.DatetimeIndex(
            [_ts(2024, 1, 1), _ts(2024, 1, 8), _ts(2024, 1, 15),
             _ts(2024, 1, 22), _ts(2024, 1, 29)],
            tz="UTC",
        ),
    )
    import math
    ret = weekly_return_over_weeks(weeks, 2, as_of_week_exclusive=_ts(2024, 1, 29))
    assert ret == pytest.approx(math.log(1.3 / 1.1))


def test_weekly_volatility_rejects_tiny():
    weeks = pd.Series([1.0] * 14, index=pd.DatetimeIndex(
        pd.date_range("2024-01-01", periods=14, freq="7D", tz="UTC")
    ))
    assert weekly_volatility(weeks, 12) is None


def test_vol_adjusted_score_blend():
    idx = pd.date_range("2023-01-02", periods=20, freq="7D", tz="UTC")
    closes = pd.Series([1.0 + 0.01 * i for i in range(20)], index=idx)
    out = vol_adjusted_momentum_score(
        closes,
        fast_weeks=4,
        slow_weeks=8,
        vol_weeks=8,
        as_of_week_exclusive=idx[-1],
    )
    assert out["score"] is not None
    assert out["fast_return_vol_adjusted"] is not None
    assert out["slow_return_vol_adjusted"] is not None


def test_rank_pairs_alphabetic_tiebreak():
    ranked = rank_pairs_by_score({"GBP_USD": 1.0, "EUR_USD": 1.0, "AUD_USD": 0.5})
    assert ranked[0][0] == "EUR_USD"
    assert ranked[0][2] == 1
    assert ranked[-1][0] == "AUD_USD"
    assert ranked[-1][2] == 3
