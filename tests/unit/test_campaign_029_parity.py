"""Parity: the independent verifier must match the primary engine on the same inputs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from forex_bot.data.non_time_bars import RangeBar
from forex_bot.research.campaign_029_parity import compare, independent_verify
from forex_bot.research.range_bar_execution import M1Index, run_range_bar_execution
from forex_bot.strategies.usdjpy_range_bar_mtf_breakout import RangeBarMtfBreakoutConfig

_T0 = datetime(2024, 3, 1, tzinfo=UTC)
_PARAMS = RangeBarMtfBreakoutConfig()


def _rb(idx, reason, *, o, h, lo, c, thresholds=1, overshoot=0.0):
    ot = _T0 + timedelta(minutes=10 * idx)
    return RangeBar(
        instrument="USD_JPY", price_basis="mid", threshold_pips=10.0, open=o, high=h, low=lo, close=c,
        volume=100, open_time=ot, close_time=ot + timedelta(minutes=9), source_count=10,
        source_start_time=ot, source_end_time=ot + timedelta(minutes=9),
        completion_reason=reason, thresholds_crossed=thresholds, overshoot_pips=overshoot, incomplete=False,
    )


def _series(n=40):
    reasons = ["range_up", "range_up", "range_down", "range_up", "range_down", "range_up"]
    reasons += (["range_up", "range_down"] * n)[: n - 6]
    bars = []
    for i in range(n):
        c = 150.0 + 0.10 * (i % 7) + 0.02 * i
        bars.append(_rb(i, reasons[i], o=c - 0.05, h=c + 0.06, lo=c - 0.06, c=c))
    return bars


def _m1(bars, low_overrides=None, spread=0.02):
    low_overrides = low_overrides or {}
    times, lows, highs, opens, hs = [], [], [], [], []
    for k, b in enumerate(bars):
        times.append(b.open_time)
        lows.append(low_overrides.get(k, b.low))
        highs.append(b.high)
        opens.append(b.open)
        hs.append(spread / 2 / 0.01)
    import numpy as np

    return M1Index(times=times, mid_low=np.array(lows), mid_high=np.array(highs), mid_open=np.array(opens), half_spread=np.array(hs))


def _run_both(bars, m1, trends, regimes):
    primary = run_range_bar_execution(
        range_bars=bars, m1_index=m1, h4_trends=trends, d1_regimes=regimes, params=_PARAMS, fixed_slippage_pips=0.2
    )
    verifier = independent_verify(
        range_bars=bars, m1_index=m1, h4_trends=trends, d1_regimes=regimes, params=_PARAMS, fixed_slippage_pips=0.2
    )
    return primary, verifier


def test_parity_time_exit_path() -> None:
    bars = _series(40)
    n = len(bars)
    trends = [("bullish", _T0, None)] * n
    regimes = [("unavailable", None, "HTF_UNAVAILABLE")] * n
    primary, verifier = _run_both(bars, _m1(bars), trends, regimes)
    assert primary, "expected trades"
    rep = compare(primary, verifier)
    assert rep["status"] == "PASS", rep


def test_parity_stop_exit_path() -> None:
    bars = _series(40)
    n = len(bars)
    trends = [("bullish", _T0, None)] * n
    regimes = [("unavailable", None, "HTF_UNAVAILABLE")] * n
    # pierce some lows to force stop exits
    primary0, _ = _run_both(bars, _m1(bars), trends, regimes)
    entry = primary0[0].entry_bar_index
    m1 = _m1(bars, low_overrides={entry + 2: 100.0})
    primary, verifier = _run_both(bars, m1, trends, regimes)
    rep = compare(primary, verifier)
    assert rep["status"] == "PASS", rep
    assert any(t.exit_reason == "stop" for t in primary)
