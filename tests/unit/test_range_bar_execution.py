"""Unit tests for the CAMPAIGN_029 M1-resolved range-bar execution engine."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.data.non_time_bars import RangeBar
from forex_bot.domain.candles import Candle
from forex_bot.research.range_bar_execution import (
    run_range_bar_execution,
    summarize_trades,
)
from forex_bot.strategies.usdjpy_range_bar_mtf_breakout import (
    EXIT_EOD,
    EXIT_STOP,
    EXIT_TIME,
    RangeBarMtfBreakoutConfig,
)

_T0 = datetime(2024, 3, 1, 0, 0, 0, tzinfo=UTC)


def _rb(idx: int, reason: str, *, o: float, h: float, lo: float, c: float, thresholds: int = 1, overshoot: float = 0.0) -> RangeBar:
    open_t = _T0 + timedelta(minutes=10 * idx)
    close_t = open_t + timedelta(minutes=9)
    return RangeBar(
        instrument="USD_JPY", price_basis="mid", threshold_pips=10.0,
        open=o, high=h, low=lo, close=c, volume=100,
        open_time=open_t, close_time=close_t, source_count=10,
        source_start_time=open_t, source_end_time=close_t,
        completion_reason=reason, thresholds_crossed=thresholds, overshoot_pips=overshoot, incomplete=False,
    )


def _m1_for_bars(bars: list[RangeBar], *, low_overrides: dict[int, float] | None = None, high_overrides: dict[int, float] | None = None, spread: float = 0.02) -> list[Candle]:
    """One M1 row per range bar at its open_time, mid OHLC straddling the bar's range."""
    low_overrides = low_overrides or {}
    high_overrides = high_overrides or {}
    out: list[Candle] = []
    for k, b in enumerate(bars):
        lo = low_overrides.get(k, b.low)
        hi = high_overrides.get(k, b.high)
        mo, mh, ml, mc = (Decimal(str(round(v, 3))) for v in (b.open, hi, lo, b.close))
        half = Decimal(str(spread / 2))
        out.append(
            Candle(
                instrument="USD_JPY", granularity="M1", time=b.open_time, complete=True, volume=10,
                mid_o=mo, mid_h=mh, mid_l=ml, mid_c=mc,
                bid_o=mo - half, bid_h=mh - half, bid_l=ml - half, bid_c=mc - half,
                ask_o=mo + half, ask_h=mh + half, ask_l=ml + half, ask_c=mc + half,
            )
        )
    return out


def _bullish_long_series(n: int = 20) -> list[RangeBar]:
    """A pullback (range_down) then a range_up reclaim at index 5, uptrending mids."""
    reasons = ["range_up", "range_up", "range_down", "range_up", "range_down", "range_up"] + ["range_up"] * (n - 6)
    bars: list[RangeBar] = []
    for i in range(n):
        c = 150.00 + 0.10 * i
        bars.append(_rb(i, reasons[i], o=c - 0.05, h=c + 0.06, lo=c - 0.06, c=c))
    return bars


_PARAMS = RangeBarMtfBreakoutConfig()


def _trends(n: int, kind: str = "bullish") -> list[tuple[str, datetime | None, str | None]]:
    return [(kind, _T0, None)] * n


def _regimes(n: int) -> list[tuple[str, datetime | None, str | None]]:
    return [("unavailable", None, "HTF_UNAVAILABLE")] * n


def _run(bars, m1, **kw):
    n = len(bars)
    return run_range_bar_execution(
        range_bars=bars, m1_candles=m1,
        h4_trends=kw.get("h4_trends", _trends(n)),
        d1_regimes=kw.get("d1_regimes", _regimes(n)),
        params=kw.get("params", _PARAMS),
        fixed_slippage_pips=kw.get("fixed_slippage_pips", 0.2),
    )


# --------------------------------------------------------------------------- #
def test_no_same_bar_fill_entry_is_next_bar() -> None:
    bars = _bullish_long_series()
    trades = _run(bars, _m1_for_bars(bars))
    assert trades, "expected at least one trade"
    t = trades[0]
    # trigger at index 5 (the reclaim); entry strictly the next bar.
    assert t.signal_bar_index == 5
    assert t.entry_bar_index == t.signal_bar_index + 1
    assert t.entry_source_timestamp > t.signal_bar_time


def test_time_stop_at_exactly_max_bars_when_no_stop() -> None:
    bars = _bullish_long_series(n=30)
    # never hit stop: keep all lows well above any stop (uptrend already does)
    trades = _run(bars, _m1_for_bars(bars))
    t = trades[0]
    assert t.exit_reason == EXIT_TIME
    assert t.bars_held == _PARAMS.max_bars_in_trade  # exactly 12 range bars


def test_no_take_profit_exit_reason() -> None:
    bars = _bullish_long_series(n=30)
    trades = _run(bars, _m1_for_bars(bars))
    assert all(t.exit_reason in (EXIT_STOP, EXIT_TIME, EXIT_EOD) for t in trades)


def test_stop_before_time_when_both_valid() -> None:
    bars = _bullish_long_series(n=30)
    m1 = _m1_for_bars(bars)
    trades_no_stop = _run(bars, m1)
    t0 = trades_no_stop[0]
    # Force a deep low on the bar right after entry so the stop triggers first.
    entry_idx = t0.entry_bar_index
    m1_stop = _m1_for_bars(bars, low_overrides={entry_idx + 1: 100.0})
    trades = _run(bars, m1_stop)
    t = trades[0]
    assert t.exit_reason == EXIT_STOP
    assert t.exit_bar_index < t0.exit_bar_index  # stopped earlier than the time exit


def test_conservative_ambiguous_m1_ordering_takes_stop() -> None:
    # An M1 candle whose LOW pierces the stop but whose mid stays favourable:
    # conservatively we must register the stop, not assume we escaped.
    bars = _bullish_long_series(n=30)
    trades0 = _run(bars, _m1_for_bars(bars))
    entry_idx = trades0[0].entry_bar_index
    # pierce only the low of one holding bar; open/close stay high (bar OHLC unchanged)
    m1 = _m1_for_bars(bars, low_overrides={entry_idx + 2: 100.0})
    t = _run(bars, m1)[0]
    assert t.exit_reason == EXIT_STOP


def test_no_lookahead_source_rows_exit_after_entry() -> None:
    bars = _bullish_long_series(n=30)
    for t in _run(bars, _m1_for_bars(bars)):
        assert t.exit_source_timestamp >= t.entry_source_timestamp
        assert t.entry_source_timestamp > t.signal_bar_time
        if t.h4_feature_time is not None:
            assert t.h4_feature_time <= t.signal_bar_time


def test_deterministic_ledger() -> None:
    bars = _bullish_long_series(n=30)
    m1 = _m1_for_bars(bars)
    a = _run(bars, m1)
    b = _run(bars, m1)
    assert [t.to_row() for t in a] == [t.to_row() for t in b]


def test_h4_block_suppresses_all_trades() -> None:
    bars = _bullish_long_series(n=30)
    trades = _run(bars, _m1_for_bars(bars), h4_trends=[("neutral", None, "HTF_UNAVAILABLE")] * len(bars))
    assert trades == []


def test_d1agg_opposing_blocks_long() -> None:
    bars = _bullish_long_series(n=30)
    regimes = [("not_bullish_only", _T0, None)] * len(bars)  # opposes long
    trades = _run(bars, _m1_for_bars(bars), d1_regimes=regimes)
    assert trades == []


def test_summary_block_is_serialisable_and_flags_no_approval() -> None:
    bars = _bullish_long_series(n=30)
    trades = _run(bars, _m1_for_bars(bars))
    s = summarize_trades(trades, label="unit")
    assert s["approved"] is False
    assert s["trades"] == len(trades)
    assert "expectancy_r" in s and "expectancy_r_cost_2x" in s
    import json

    json.dumps(s)  # must not raise


def test_empty_summary() -> None:
    s = summarize_trades([], label="empty")
    assert s["trades"] == 0 and s["approved"] is False


def test_vectorised_h4_aligner_matches_strategy_rule() -> None:
    # The engine's precompute_h4_trends must agree with the strategy's per-bar
    # aligned_h4_trend (same frozen rule) — guards against divergence.
    from forex_bot.domain.candles import CandleFrame
    from forex_bot.research.range_bar_execution import precompute_h4_trends
    from forex_bot.strategies.usdjpy_range_bar_mtf_breakout import aligned_h4_trend

    base = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    candles = []
    for i in range(80):
        c = 149.0 + 0.03 * i  # uptrend
        t = base + timedelta(hours=4 * i)
        candles.append(
            Candle(
                instrument="USD_JPY", granularity="H4", time=t, complete=True, volume=100,
                mid_o=Decimal(str(round(c - 0.02, 3))), mid_h=Decimal(str(round(c + 0.03, 3))),
                mid_l=Decimal(str(round(c - 0.03, 3))), mid_c=Decimal(str(round(c, 3))),
            )
        )
    frame = CandleFrame.from_candles("USD_JPY", "H4", candles)
    decisions = [base + timedelta(hours=4 * i + 1) for i in (60, 65, 70, 75)]
    batch = precompute_h4_trends(frame, decisions, _PARAMS)
    for d, (trend_b, time_b, block_b) in zip(decisions, batch, strict=True):
        trend_s, time_s, block_s = aligned_h4_trend(
            frame, d, ema_fast=_PARAMS.h4_ema_fast, ema_slow=_PARAMS.h4_ema_slow, slope_bars=_PARAMS.h4_ema_slope_bars
        )
        assert trend_b == trend_s
        assert (block_b is None) == (block_s is None)
        if time_b is not None and time_s is not None:
            assert time_b == time_s

    # staleness bound: a decision far past the last completed H4 bar is HTF_STALE.
    last_close = base + timedelta(hours=4 * 79)
    far = last_close + timedelta(hours=30)
    stale = precompute_h4_trends(frame, [far], _PARAMS, max_staleness_seconds=8 * 3600)[0]
    assert stale[2] == "HTF_STALE"
    fresh = precompute_h4_trends(frame, [last_close + timedelta(hours=1)], _PARAMS, max_staleness_seconds=8 * 3600)[0]
    assert fresh[2] is None
