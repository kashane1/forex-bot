"""D1AGG + htf_align equivalence tests for regime switcher path."""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pandas as pd

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.features import d1agg_htf
from forex_bot.strategies.regime_switcher_atr_percentile import (
    _compute_regime,
    _df_to_completed_h4_candle_list,
    _wilder_atr_over_d1agg,
)


def _candle(t: datetime, close: float) -> Candle:
    spread = Decimal("0.0001")
    return Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=t,
        complete=True,
        volume=100,
        bid_o=Decimal(str(close)) - spread,
        bid_h=Decimal(str(close + 0.001)),
        bid_l=Decimal(str(close - 0.001)),
        bid_c=Decimal(str(close)),
        ask_o=Decimal(str(close)),
        ask_h=Decimal(str(close + 0.001)),
        ask_l=Decimal(str(close - 0.001)),
        ask_c=Decimal(str(close)) + spread,
    )


def test_regime_helpers_match_d1agg_htf_module() -> None:
    hours = (22, 2, 6, 10, 14, 18)
    base = datetime(2022, 1, 3, 22, tzinfo=UTC)
    candles = [
        _candle(base + timedelta(hours=4 * i), 1.1 + 0.001 * (i % 30))
        for i in range(600)
    ]
    agg = aggregate_h4_to_d1(candles, instrument="EUR_USD")
    d1 = agg.candles
    s1 = _wilder_atr_over_d1agg(d1, 14)
    s2 = d1agg_htf.wilder_atr_over_d1agg(d1, 14)
    assert len(s1) == len(s2)
    for a, b in zip(s1, s2, strict=True):
        if a == b:
            continue
        assert math.isnan(a) and math.isnan(b)
    r1 = _compute_regime(s1, lookback_days=60, percentile_threshold=0.7)
    r2 = d1agg_htf.compute_regime_label(s1, lookback_days=60, percentile_threshold=0.7)
    assert r1 == r2


def _aligned_frame(n_days: int = 120) -> pd.DataFrame:
    start = datetime(2024, 11, 4, 22, tzinfo=UTC)
    candles: list[Candle] = []
    for day in range(n_days):
        day_start = start + timedelta(days=day)
        for slot in range(6):
            t = day_start + timedelta(hours=4 * slot)
            candles.append(_candle(t, 1.05))
    return CandleFrame.from_candles("EUR_USD", "H4", candles).df


def test_aligned_atr_matches_reference_at_signal_bar() -> None:
    df = _aligned_frame(120)
    h4_list = _df_to_completed_h4_candle_list(df, "EUR_USD")
    gate = d1agg_htf.regime_gate_from_h4_candles(
        h4_list,
        instrument="EUR_USD",
        daily_atr_len=14,
        regime_lookback=60,
        regime_threshold=0.7,
    )
    assert gate is not None
    _label, reference, _pct, d1_time, _count = gate
    decision = df.index[-1].to_pydatetime()
    aligned_atr, aligned_time, _reason = d1agg_htf.aligned_d1_atr_at_decision(
        h4_list,
        decision,
        instrument="EUR_USD",
        daily_atr_len=14,
    )
    assert aligned_atr is not None
    assert abs(aligned_atr - reference) < 1e-9
    if d1_time and aligned_time:
        assert aligned_time == d1_time
