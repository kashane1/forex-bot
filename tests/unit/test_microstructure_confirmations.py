"""Unit tests for the read-only M15 microstructure-confirmation detectors.

Synthetic M15 bars are constructed to trigger / not-trigger each detector, plus:
  * causality — appending future bars must not change a *live* detector's result;
  * the post-decision detectors are correctly flagged ``uses_post_decision=True``
    and *do* depend on bars after the decision index.
"""

from __future__ import annotations

import numpy as np

from forex_bot.research.microstructure_confirmations import (
    LIVE_DETECTORS,
    MicrostructureParams,
    build_context,
    detect_all,
    failed_reclaim_or_trap,
    liquidity_sweep_plus_displacement,
    range_expansion_after_compression,
    reclaim_distance_atr,
    reclaim_plus_impulse,
    reclaim_plus_micro_swing_break,
    reclaim_plus_retest_hold,
    session_bucket,
    volatility_context,
)

PARAMS = MicrostructureParams()


def _flat_bars(n: int, price: float = 100.0, rng: float = 0.2):
    """n identical small-range bars (open==close==price)."""
    o = np.full(n, price)
    c = np.full(n, price)
    h = np.full(n, price + rng / 2)
    low = np.full(n, price - rng / 2)
    return o, h, low, c


def _ctx(o, h, low, c):
    return build_context(o, h, low, c, PARAMS)


# --------------------------------------------------------------------------
# reclaim_plus_impulse
# --------------------------------------------------------------------------


def test_impulse_present_for_large_trend_body_long():
    o, h, low, c = _flat_bars(40)
    i = 39
    # Big bullish body at decision bar, ~3x typical range.
    o[i], c[i] = 100.0, 100.9
    h[i], low[i] = 100.95, 99.98
    res = reclaim_plus_impulse(_ctx(o, h, low, c), i, "long", PARAMS)
    assert res.available and res.present
    assert res.score > PARAMS.impulse_atr_mult
    assert res.uses_post_decision is False


def test_impulse_absent_for_doji():
    o, h, low, c = _flat_bars(40)
    res = reclaim_plus_impulse(_ctx(o, h, low, c), 39, "long", PARAMS)
    assert res.available and not res.present


def test_impulse_counter_trend_body_scores_negative_short():
    o, h, low, c = _flat_bars(40)
    i = 39
    # A bullish candle on a SHORT trade is counter-trend → negative score.
    o[i], c[i] = 100.0, 100.8
    res = reclaim_plus_impulse(_ctx(o, h, low, c), i, "short", PARAMS)
    assert res.score < 0 and not res.present


# --------------------------------------------------------------------------
# reclaim_plus_micro_swing_break
# --------------------------------------------------------------------------


def test_micro_swing_break_long():
    o, h, low, c = _flat_bars(20)
    i = 19
    c[i] = 101.0  # closes above prior 6-bar high band (~100.1)
    h[i] = 101.1
    res = reclaim_plus_micro_swing_break(_ctx(o, h, low, c), i, "long", PARAMS)
    assert res.present and res.score > 0


def test_micro_swing_break_absent_when_inside_range():
    o, h, low, c = _flat_bars(20)
    res = reclaim_plus_micro_swing_break(_ctx(o, h, low, c), 19, "long", PARAMS)
    assert not res.present


# --------------------------------------------------------------------------
# liquidity_sweep_plus_displacement
# --------------------------------------------------------------------------


def test_sweep_plus_displacement_long():
    o, h, low, c = _flat_bars(20)
    # Sweep: 2 bars before decision, a spike low below the local range.
    sweep = 17
    low[sweep] = 99.0
    h[sweep] = 100.05
    # Decision bar displaces up and closes above the sweep bar's high.
    i = 19
    o[i], c[i] = 100.0, 100.5
    h[i] = 100.6
    res = liquidity_sweep_plus_displacement(_ctx(o, h, low, c), i, "long", PARAMS)
    assert res.present and res.score > 0
    assert res.detail["sweep_bars_back"] == i - sweep


def test_sweep_absent_when_low_is_decision_bar():
    o, h, low, c = _flat_bars(20)
    i = 19
    low[i] = 99.0  # the lowest low is the decision bar itself → not a prior sweep
    c[i] = 99.1
    res = liquidity_sweep_plus_displacement(_ctx(o, h, low, c), i, "long", PARAMS)
    assert not res.present


# --------------------------------------------------------------------------
# range_expansion_after_compression
# --------------------------------------------------------------------------


def test_range_expansion_after_compression_long():
    # Long baseline of wider bars, then a compressed stretch, then expansion.
    o, h, low, c = _flat_bars(30, rng=1.0)
    # Compress the 6 bars before the decision bar.
    for k in range(23, 29):
        h[k], low[k] = 100.1, 99.9
    i = 29
    o[i], c[i] = 100.0, 100.8  # expansion bar, trend-direction body
    h[i], low[i] = 100.9, 99.95
    res = range_expansion_after_compression(_ctx(o, h, low, c), i, "long", PARAMS)
    assert res.present and res.score >= PARAMS.expansion_mult
    assert res.detail["compressed"] is True


def test_range_expansion_absent_without_compression():
    o, h, low, c = _flat_bars(30, rng=1.0)
    res = range_expansion_after_compression(_ctx(o, h, low, c), 29, "long", PARAMS)
    assert not res.present


# --------------------------------------------------------------------------
# Post-decision detectors + flagging
# --------------------------------------------------------------------------


def test_retest_hold_is_post_decision_and_detects_hold():
    o, h, low, c = _flat_bars(30)
    i = 20
    # After the decision bar, one bar dips to the EMA then closes back above it.
    k = 22
    low[k] = c[k] - 0.0  # dips toward ema
    # make ema ~ price (flat), low touches near ema, close holds above
    res = reclaim_plus_retest_hold(_ctx(o, h, low, c), i, "long", PARAMS)
    assert res.uses_post_decision is True
    assert res.available


def test_failed_reclaim_trap_post_decision():
    o, h, low, c = _flat_bars(30, price=100.0)
    i = 20
    # Drive closes below EMA after the decision bar → trap for a long.
    for k in range(i + 1, i + 1 + PARAMS.trap_horizon):
        c[k] = 95.0
        low[k] = 94.5
    res = failed_reclaim_or_trap(_ctx(o, h, low, c), i, "long", PARAMS)
    assert res.uses_post_decision is True
    assert res.present and res.score is not None


def test_failed_reclaim_absent_when_trend_holds():
    o, h, low, c = _flat_bars(30, price=100.0)
    i = 20
    for k in range(i + 1, i + 1 + PARAMS.trap_horizon):
        c[k] = 100.5  # stays above ema
    res = failed_reclaim_or_trap(_ctx(o, h, low, c), i, "long", PARAMS)
    assert not res.present and res.score is None


# --------------------------------------------------------------------------
# Causality: future bars must not change LIVE detectors
# --------------------------------------------------------------------------


def test_live_detectors_are_causal():
    o, h, low, c = _flat_bars(40)
    i = 30
    o[i], c[i] = 100.0, 100.9  # impulse at decision bar
    h[i] = 101.0
    base = _ctx(o, h, low, c)
    base_res = detect_all(base, i, "long", PARAMS)

    # Mutate bars strictly AFTER i with wild values.
    o2, h2, low2, c2 = o.copy(), h.copy(), low.copy(), c.copy()
    for k in range(i + 1, 40):
        o2[k], c2[k], h2[k], low2[k] = 50.0, 150.0, 200.0, 10.0
    mut = _ctx(o2, h2, low2, c2)
    mut_res = detect_all(mut, i, "long", PARAMS)

    for name in LIVE_DETECTORS:
        assert base_res[name].present == mut_res[name].present, name
        assert base_res[name].score == mut_res[name].score, name


def test_post_decision_detectors_do_depend_on_future():
    o, h, low, c = _flat_bars(30, price=100.0)
    i = 20
    held = failed_reclaim_or_trap(_ctx(o, h, low, c), i, "long", PARAMS)
    o2, h2, low2, c2 = o.copy(), h.copy(), low.copy(), c.copy()
    for k in range(i + 1, i + 1 + PARAMS.trap_horizon):
        c2[k] = 90.0
        low2[k] = 89.0
    trapped = failed_reclaim_or_trap(_ctx(o2, h2, low2, c2), i, "long", PARAMS)
    assert held.present is False and trapped.present is True


# --------------------------------------------------------------------------
# Context helpers
# --------------------------------------------------------------------------


def test_reclaim_distance_atr_sign():
    o, h, low, c = _flat_bars(40)
    i = 39
    c[i] = 100.5  # above flat ema
    ctx = _ctx(o, h, low, c)
    long_d = reclaim_distance_atr(ctx, i, "long", PARAMS)
    short_d = reclaim_distance_atr(ctx, i, "short", PARAMS)
    assert long_d is not None and long_d > 0
    assert short_d is not None and short_d < 0


def test_session_bucket_partitions_day():
    assert session_bucket(2) == "tokyo"
    assert session_bucket(8) == "london"
    assert session_bucket(13) == "london_ny_overlap"
    assert session_bucket(17) == "new_york"
    assert session_bucket(22) == "rollover_late"
    # exhaustive: every hour maps to a known bucket
    buckets = {session_bucket(h) for h in range(24)}
    assert buckets <= {"tokyo", "london", "london_ny_overlap", "new_york", "rollover_late"}


def test_volatility_context_percentile_in_unit_interval():
    rng = np.linspace(0.1, 2.0, 60)
    o = np.full(60, 100.0)
    c = np.full(60, 100.0)
    h = 100.0 + rng / 2
    low = 100.0 - rng / 2
    ctx = _ctx(o, h, low, c)
    vc = volatility_context(ctx, 59, lookback=60)
    assert vc["atr_at_entry"] is not None
    assert 0.0 <= vc["atr_percentile"] <= 1.0
