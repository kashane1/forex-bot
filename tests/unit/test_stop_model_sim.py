"""Synthetic tests for diagnostic stop-model simulation on fixed entries."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from forex_bot.research.stop_model_sim import (
    PathBar,
    simulate_fixed_stop,
    simulate_time_invalidation,
)

T0 = datetime(2024, 1, 1, tzinfo=UTC)


def _bars(rows: list[tuple[float, float, float]]) -> list[PathBar]:
    return [
        PathBar(timestamp=T0 + timedelta(minutes=15 * (i + 1)), high=h, low=lo, close=c)
        for i, (h, lo, c) in enumerate(rows)
    ]


def test_baseline_stop_hits_at_minus_one():
    # entry 100, stop 99 (risk 1). bar1 dips to 99.0 -> -1R stop.
    out = simulate_fixed_stop(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=_bars([(100.2, 99.0, 99.1)]), stop_r=1.0,
    )
    assert out.status == "OK" and out.exit_kind == "stop"
    assert out.outcome_r == -1.0 and out.exit_bar == 0


def test_tighter_stop_triggers_where_baseline_would_not():
    # bar dips to -0.8R only. baseline (-1.0) survives; 0.75R stop triggers.
    bars = _bars([(100.1, 99.2, 100.0), (100.5, 100.1, 100.4)])
    base = simulate_fixed_stop(side="long", entry_price=100.0, initial_stop_price=99.0,
                               bars=bars, stop_r=1.0)
    tight = simulate_fixed_stop(side="long", entry_price=100.0, initial_stop_price=99.0,
                                bars=bars, stop_r=0.75)
    assert base.exit_kind == "time"  # never hit -1R, exits at horizon close
    assert tight.exit_kind == "stop" and tight.outcome_r == -0.75


def test_wider_stop_lets_trade_run_to_time():
    # bar1 dips to -1.1R (would stop baseline) but a 1.5R stop survives; later recovers.
    bars = _bars([(100.2, 98.9, 99.9), (101.0, 100.0, 100.8)])
    base = simulate_fixed_stop(side="long", entry_price=100.0, initial_stop_price=99.0,
                               bars=bars, stop_r=1.0)
    wide = simulate_fixed_stop(side="long", entry_price=100.0, initial_stop_price=99.0,
                               bars=bars, stop_r=1.5)
    assert base.exit_kind == "stop" and base.outcome_r == -1.0
    assert wide.exit_kind == "time"
    assert abs(wide.outcome_r - 0.8) < 1e-9  # close 100.8 -> +0.8R


def test_time_stop_uses_close_of_last_bar():
    bars = _bars([(100.3, 99.8, 100.1), (100.6, 100.0, 100.5)])
    out = simulate_fixed_stop(side="long", entry_price=100.0, initial_stop_price=99.0,
                              bars=bars, stop_r=1.0, max_bars=32)
    assert out.exit_kind == "time"
    assert abs(out.outcome_r - 0.5) < 1e-9  # last close 100.5


def test_short_side_outcome():
    # short entry 100 stop 101 (risk 1). price falls to close 99.0 -> +1R at time.
    bars = _bars([(100.2, 99.5, 99.6), (99.8, 99.0, 99.0)])
    out = simulate_fixed_stop(side="short", entry_price=100.0, initial_stop_price=101.0,
                              bars=bars, stop_r=1.0)
    assert out.exit_kind == "time" and out.outcome_r == 1.0


def test_max_bars_truncates_horizon():
    bars = _bars([(100.1, 99.9, 100.0)] * 40)
    out = simulate_fixed_stop(side="long", entry_price=100.0, initial_stop_price=99.0,
                              bars=bars, stop_r=1.0, max_bars=32)
    assert out.exit_bar == 31  # only first 32 bars considered


def test_time_invalidation_exits_when_no_progress():
    # never reaches +0.5R by bar 2 -> invalidation exit at bar 1 close.
    bars = _bars([(100.1, 99.8, 100.0), (100.2, 99.9, 100.05), (101.0, 100.5, 100.9)])
    out = simulate_time_invalidation(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=bars, threshold_r=0.5, n_bars=2,
    )
    assert out.exit_kind == "invalidation"
    assert out.exit_bar == 1
    assert abs(out.outcome_r - 0.05) < 1e-9


def test_time_invalidation_holds_when_progress_made():
    # reaches +0.5R by bar 2 -> not invalidated; runs to time stop.
    bars = _bars([(100.6, 99.9, 100.5), (100.7, 100.2, 100.6), (100.9, 100.4, 100.8)])
    out = simulate_time_invalidation(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=bars, threshold_r=0.5, n_bars=2,
    )
    assert out.exit_kind == "time"
    assert abs(out.outcome_r - 0.8) < 1e-9


def test_invalidation_respects_baseline_stop_first():
    # stop hit at bar 1 before the invalidation check at bar 2.
    bars = _bars([(100.1, 98.9, 99.0), (100.2, 100.0, 100.1)])
    out = simulate_time_invalidation(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=bars, threshold_r=0.5, n_bars=2,
    )
    assert out.exit_kind == "stop" and out.outcome_r == -1.0


def test_bad_side_and_zero_risk_and_no_bars():
    assert simulate_fixed_stop(side="x", entry_price=100, initial_stop_price=99,
                               bars=_bars([(100, 99, 99)]), stop_r=1.0).status == "BAD_SIDE"
    assert simulate_fixed_stop(side="long", entry_price=100, initial_stop_price=100,
                               bars=_bars([(100, 99, 99)]), stop_r=1.0).status == "ZERO_RISK"
    assert simulate_fixed_stop(side="long", entry_price=100, initial_stop_price=99,
                               bars=[], stop_r=1.0).status == "NO_BARS"
