"""MFE/MAE reconstruction tests with synthetic candles (no real data needed)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from forex_bot.research.mfe_mae import Bar, compute_mfe_mae

T0 = datetime(2024, 1, 1, tzinfo=UTC)


def _bars(rows: list[tuple[float, float]], start: datetime = T0, step_min: int = 15) -> list[Bar]:
    return [
        Bar(timestamp=start + timedelta(minutes=step_min * (i + 1)), high=h, low=lo)
        for i, (h, lo) in enumerate(rows)
    ]


def test_long_mfe_mae_basic():
    # entry 100, stop 99 -> risk 1.0 (1R == 1.0 price). Long.
    # bar1: high 100.5 (+0.5R), low 99.8 (-0.2R); bar2: high 101.2 (+1.2R), low 100.4
    res = compute_mfe_mae(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=_bars([(100.5, 99.8), (101.2, 100.4)]),
    )
    assert res.status == "OK"
    assert res.bars_used == 2
    assert abs(res.mfe_r - 1.2) < 1e-6
    assert abs(res.mae_r - (-0.2)) < 1e-6
    assert res.reached_plus_0_25r and res.reached_plus_0_5r and res.reached_plus_1_0r
    assert not res.touched_minus_0_5r
    assert not res.stop_hit


def test_short_mfe_mae_basic():
    # entry 100, stop 101 -> risk 1.0. Short: favorable = price falling.
    # bar1: high 100.3 (adv -0.3R), low 99.4 (fav +0.6R)
    res = compute_mfe_mae(
        side="short", entry_price=100.0, initial_stop_price=101.0,
        bars=_bars([(100.3, 99.4)]),
    )
    assert res.status == "OK"
    assert abs(res.mfe_r - 0.6) < 1e-6
    assert abs(res.mae_r - (-0.3)) < 1e-6
    assert res.reached_plus_0_5r
    assert not res.reached_plus_1_0r


def test_stop_before_profit_long():
    # bar1 dips to stop (low 99.0 -> -1R) AND never above +0.25; bar2 rallies.
    # With default adverse_first, stop on bar1; +0.5R on bar2 is AFTER stop.
    res = compute_mfe_mae(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=_bars([(100.1, 99.0), (100.8, 100.2)]),
    )
    assert res.stop_hit
    assert res.stop_hit_bar_index == 0
    assert res.reached_plus_0_5r  # MFE over whole path reached +0.5 (bar2)
    assert not res.reached_plus_0_5r_before_stop  # but only after the stop


def test_profit_before_drawdown_long():
    # bar1 reaches +0.5R with no stop; bar2 later dips to stop.
    res = compute_mfe_mae(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=_bars([(100.6, 100.1), (100.2, 99.0)]),
    )
    assert res.reached_plus_0_5r_before_stop
    assert res.first_plus_0_5r_bar_index == 0
    assert res.stop_hit
    assert res.stop_hit_bar_index == 1


def test_intrabar_same_bar_adverse_first_is_conservative():
    # One bar touches both +0.5R (high 100.5) and the stop (low 99.0).
    res_adv = compute_mfe_mae(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=_bars([(100.5, 99.0)]),
    )
    assert res_adv.stop_hit
    assert not res_adv.reached_plus_0_5r_before_stop  # adverse_first: stop wins
    res_fav = compute_mfe_mae(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=_bars([(100.5, 99.0)]), intrabar="favorable_first",
    )
    assert res_fav.reached_plus_0_5r_before_stop


def test_no_lookahead_past_exit():
    # bars after exit_time must be ignored: the +1R spike on bar3 is post-exit.
    start = T0
    bars = _bars([(100.3, 99.9), (100.4, 100.0), (102.0, 101.0)], start=start)
    exit_time = bars[1].timestamp  # exit at end of bar2
    res = compute_mfe_mae(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=bars, exit_time=exit_time,
    )
    assert res.bars_used == 2
    assert abs(res.mfe_r - 0.4) < 1e-6  # bar3's +2R excluded
    assert not res.reached_plus_1_0r


def test_drops_bars_at_or_before_entry():
    bars = _bars([(100.3, 99.9), (100.8, 100.1)], start=T0)
    # entry_time equal to the first bar timestamp -> that bar dropped
    res = compute_mfe_mae(
        side="long", entry_price=100.0, initial_stop_price=99.0,
        bars=bars, entry_time=bars[0].timestamp,
    )
    assert res.bars_used == 1
    assert abs(res.mfe_r - 0.8) < 1e-6


def test_no_bars_status():
    res = compute_mfe_mae(
        side="long", entry_price=100.0, initial_stop_price=99.0, bars=[],
    )
    assert res.status == "NO_BARS"
    assert res.mfe_r is None
    assert not res.stop_hit


def test_zero_risk_status():
    res = compute_mfe_mae(
        side="long", entry_price=100.0, initial_stop_price=100.0,
        bars=_bars([(100.5, 99.5)]),
    )
    assert res.status == "ZERO_RISK"


def test_bad_side_status():
    res = compute_mfe_mae(
        side="flat", entry_price=100.0, initial_stop_price=99.0,
        bars=_bars([(100.5, 99.5)]),
    )
    assert res.status == "BAD_SIDE"


def test_jpy_scale_risk_units():
    # JPY pair: entry 110.00, stop 110.20 (short), risk 0.20 price.
    # low 109.80 -> favorable (110.00-109.80)/0.20 = +1.0R
    res = compute_mfe_mae(
        side="short", entry_price=110.0, initial_stop_price=110.2,
        bars=_bars([(110.05, 109.8)]),
    )
    assert abs(res.mfe_r - 1.0) < 1e-6
    # adverse: (110.00-110.05)/0.20 = -0.25R
    assert abs(res.mae_r - (-0.25)) < 1e-6
