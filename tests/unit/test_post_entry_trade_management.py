"""Unit tests for read-only post-entry trade-management diagnostic events.

Synthetic post-entry M15 windows for long and short trades, plus a no-lookahead test:
horizon-N features must not change when bars after N are mutated.
"""

from __future__ import annotations

import math

from forex_bot.research.post_entry_trade_management import (
    EVENT_LIVENESS,
    PostEntryParams,
    compute_post_entry_events,
    excursion_path,
    liveness_of,
)

PARAMS = PostEntryParams()


def _events(side, entry, stop, highs, lows, closes, emas, atrs):
    return compute_post_entry_events(
        side=side, entry_price=entry, stop_price=stop,
        post_high=highs, post_low=lows, post_close=closes,
        post_ema=emas, post_atr=atrs, params=PARAMS,
    )


# --------------------------------------------------------------------------
# excursion_path
# --------------------------------------------------------------------------


def test_excursion_path_long_basic():
    # entry 100, stop 99 (risk=1). Bars rise to +0.5R then +1.0R.
    highs = [100.3, 100.6, 101.0]
    lows = [99.9, 100.1, 100.4]
    p = excursion_path("long", 100.0, 99.0, highs, lows)
    assert p is not None
    assert p.cum_fav[-1] == 1.0
    assert p.first_fav_bar[0.5] == 2
    assert p.first_fav_bar[1.0] == 3


def test_excursion_path_short_basic():
    # short entry 100, stop 101 (risk=1). Price falls → favorable.
    highs = [100.1, 100.0, 99.8]
    lows = [99.7, 99.4, 99.0]
    p = excursion_path("short", 100.0, 101.0, highs, lows)
    assert p is not None
    assert p.cum_fav[-1] == 1.0  # entry-low = 100-99 = 1R
    assert p.first_fav_bar[0.25] == 1


def test_excursion_zero_risk_returns_none():
    assert excursion_path("long", 100.0, 100.0, [100.5], [99.5]) is None


# --------------------------------------------------------------------------
# horizon events
# --------------------------------------------------------------------------


def test_reached_and_mae_by_horizon_long():
    # 5 post bars; reaches +0.25R by bar 2, dips to -0.4R by bar 1.
    highs = [100.1, 100.4, 100.5, 100.6, 100.7]
    lows = [99.6, 99.9, 100.0, 100.1, 100.2]
    closes = [100.0, 100.3, 100.4, 100.5, 100.6]
    emas = [99.5] * 5
    atrs = [0.5] * 5
    f = _events("long", 100.0, 99.0, highs, lows, closes, emas, atrs)
    assert f["reached_plus_025_h2"] is True
    assert f["reached_plus_025_h4"] is True
    assert f["mae_by_h2"] <= -0.3  # dipped to ~-0.4R on bar 1
    assert f["no_continuation_h2"] is False
    assert f["bars_to_exit"] == 5
    assert f["open_at_h2"] is True
    assert f["open_at_h8"] is False  # only 5 bars


def test_no_continuation_when_flat():
    highs = [100.05] * 4
    lows = [99.95] * 4
    closes = [100.0] * 4
    emas = [99.5] * 4
    atrs = [0.5] * 4
    f = _events("long", 100.0, 99.0, highs, lows, closes, emas, atrs)
    assert f["no_continuation_h2"] is True
    assert f["reached_plus_025_h4"] is False


def test_early_reclaim_failure_and_trap_long():
    # Closes immediately back below EMA → reclaim failure + trap (within 2 bars).
    highs = [100.1, 100.0, 99.9, 99.8]
    lows = [99.4, 99.2, 99.0, 98.8]
    closes = [99.3, 99.1, 98.9, 98.7]  # all below ema=99.5
    emas = [99.5] * 4
    atrs = [0.5] * 4
    f = _events("long", 100.0, 98.0, highs, lows, closes, emas, atrs)
    assert f["early_reclaim_failure_h2"] is True
    assert f["trap_or_failed_breakout"] is True


def test_retest_hold_long():
    # Bar dips toward EMA (low touches ema+tol) but closes back above EMA.
    emas = [100.0, 100.0, 100.0, 100.0]
    atrs = [0.4, 0.4, 0.4, 0.4]
    highs = [100.6, 100.7, 100.8, 100.9]
    lows = [100.05, 100.1, 100.2, 100.3]  # bar1 low ~ema+0.05 <= ema+tol*atr(=0.1)
    closes = [100.5, 100.6, 100.7, 100.8]  # closes above ema
    f = _events("long", 100.2, 99.2, highs, lows, closes, emas, atrs)
    assert f["early_retest_hold_h2"] is True


def test_early_adverse_expansion_before_favorable():
    # Goes adverse to -0.5R on bar 1, only later reaches +0.25R.
    highs = [100.1, 100.1, 100.4]
    lows = [99.5, 99.7, 100.0]   # bar1 low=99.5 → adv=-0.5R
    closes = [99.6, 99.9, 100.3]
    emas = [99.0] * 3
    atrs = [0.5] * 3
    f = _events("long", 100.0, 99.0, highs, lows, closes, emas, atrs)
    assert f["early_adverse_expansion_h2"] is True


# --------------------------------------------------------------------------
# no lookahead beyond declared horizon
# --------------------------------------------------------------------------


def test_no_lookahead_beyond_horizon():
    highs = [100.1, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9, 101.0, 101.1, 101.2]
    lows = [99.8, 99.9, 100.0, 100.1, 100.2, 100.3, 100.4, 100.5, 100.6, 100.7]
    closes = [100.0, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9, 101.0, 101.1]
    emas = [99.5] * 10
    atrs = [0.5] * 10
    base = _events("long", 100.0, 99.0, highs, lows, closes, emas, atrs)

    # Mutate bars after horizon 4 wildly.
    h2 = highs.copy()
    l2 = lows.copy()
    c2 = closes.copy()
    for k in range(4, 10):
        h2[k], l2[k], c2[k] = 200.0, 10.0, 150.0
    mut = _events("long", 100.0, 99.0, h2, l2, c2, emas, atrs)

    for base_name in ("reached_plus_025", "reached_plus_05", "no_continuation",
                      "early_adverse_expansion", "early_favorable_displacement",
                      "early_retest_hold", "early_reclaim_failure",
                      "range_compression_after_entry", "mae_by"):
        assert base[f"{base_name}_h2"] == mut[f"{base_name}_h2"], base_name
        assert base[f"{base_name}_h4"] == mut[f"{base_name}_h4"], base_name


def test_empty_path_yields_none_features():
    f = _events("long", 100.0, 99.0, [], [], [], [], [])
    assert f["bars_to_exit"] == 0
    assert f["reached_plus_025_h2"] is None
    assert f["open_at_h2"] is False


# --------------------------------------------------------------------------
# liveness labelling
# --------------------------------------------------------------------------


def test_liveness_classification():
    assert liveness_of("early_retest_hold_h4") == "live_manageable"
    assert liveness_of("no_continuation_h8") == "live_manageable"
    assert liveness_of("reached_plus_025_h2") == "live_manageable"
    assert liveness_of("time_to_first_plus_05") == "hindsight_only"
    assert liveness_of("bars_to_exit") == "descriptive"
    assert liveness_of("open_at_h16") == "descriptive"
    # every declared base has a class
    assert all(v in {"live_manageable", "hindsight_only", "descriptive"}
               for v in EVENT_LIVENESS.values())


def test_finite_mae_values():
    highs = [100.4, 100.6]
    lows = [99.7, 99.8]
    closes = [100.2, 100.4]
    emas = [99.5, 99.5]
    atrs = [0.5, 0.5]
    f = _events("long", 100.0, 99.0, highs, lows, closes, emas, atrs)
    assert isinstance(f["mae_by_h2"], float) and math.isfinite(f["mae_by_h2"])
