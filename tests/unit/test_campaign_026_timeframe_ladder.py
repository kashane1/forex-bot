"""CAMPAIGN_026 timeframe-ladder simulator — deterministic exit/gate/cost tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from forex_bot.research import campaign_026_timeframe_ladder as tl


def _candidate(exit_model="time_stop_only", *, execution_tf="M15", **over):
    c = {
        "candidate_id": "C026_TF_TEST",
        "execution_timeframe": execution_tf,
        "donchian_length": 20,
        "atr_stop_multiple": 2.0,
        "exit_model": exit_model,
        "target_r_multiple": None,
        "breakeven_trigger_r": None,
        "trail_activation_r": None,
        "trail_atr_multiple": None,
        "channel_exit_length": None,
        "time_stop_bars": 48,
        "context_mode": "standard",
        "local_setup_mode": "pullback_or_compression",
    }
    if exit_model == "fixed_2r_target":
        c["target_r_multiple"] = 2.0
    elif exit_model == "fixed_3r_target":
        c["target_r_multiple"] = 3.0
    elif exit_model == "breakeven_then_atr_trail":
        c.update(breakeven_trigger_r=1.0, trail_activation_r=1.5, trail_atr_multiple=1.5)
    elif exit_model == "donchian_channel_exit":
        c["channel_exit_length"] = 20
    c.update(over)
    return c


def _feat(n=80, *, execution_tf="M15", close=1.0, atr=0.0010, pip=0.0001, h1_available=True):
    idx = pd.DatetimeIndex([datetime(2022, 1, 3, tzinfo=UTC) + timedelta(minutes=15 * i) for i in range(n)])
    def arr(v):
        return np.full(n, float(v))
    dc = {ln: np.full(n, np.nan) for ln in tl.DONCHIAN_LENGTHS}
    return tl.PairFeatures026(
        instrument="EUR_USD",
        execution_tf=execution_tf,
        index=idx,
        open=arr(close),
        high=arr(close),
        low=arr(close),
        close=arr(close),
        atr=arr(atr),
        spread_pips=arr(0.0),
        pip_size=pip,
        dc_high=dict(dc),
        dc_low={ln: np.full(n, close - 0.0001) for ln in tl.DONCHIAN_LENGTHS},
        h4_trend=np.ones(n, dtype=int),
        h1_standard=np.ones(n, dtype=int),
        h1_strict=np.ones(n, dtype=int),
        h1_available=h1_available,
        d1_not_bearish=np.ones(n, dtype=bool),
        d1_not_bullish=np.ones(n, dtype=bool),
        local_pullback_long=np.ones(n, dtype=bool),
        local_pullback_short=np.ones(n, dtype=bool),
        local_compression=np.ones(n, dtype=bool),
        warm_mask=np.ones(n, dtype=bool),
    )


def test_next_bar_open_entry_is_after_signal() -> None:
    feat = _feat()
    tr = tl._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate())
    assert tr is not None
    assert tr.entry_time == feat.index[31].to_pydatetime()
    assert tr.entry_time > feat.index[30].to_pydatetime()


def test_fixed_target_emits_correct_r_and_net() -> None:
    feat = _feat()
    feat.high[33] = 1.0040  # +2R = 1.0 + 2*0.0020
    tr = tl._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("fixed_2r_target"))
    assert tr.exit_reason == "fixed_target_2r"
    assert tr.gross_r_multiple == pytest.approx(2.0, abs=1e-9)
    # zero spread, COST_BASE 0.2-pip fixed slippage/side -> 0.4 pip RT = 0.02R -> 1.98
    assert tr.net_r(tl.COST_BASE) == pytest.approx(1.98, abs=1e-9)


def test_same_bar_stop_and_target_resolves_adverse_first() -> None:
    feat = _feat()
    feat.high[33] = 1.0040
    feat.low[33] = 0.9980
    tr = tl._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("fixed_2r_target"))
    assert tr.exit_reason == "hard_stop"
    assert tr.gross_r_multiple == pytest.approx(-1.0, abs=1e-9)


def test_time_stop_fires_at_exact_bar_count() -> None:
    feat = _feat(n=120)
    tr = tl._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("time_stop_only", time_stop_bars=48))
    assert tr.exit_reason == "time_stop"
    assert tr.hold_bars == 49


def test_channel_exit_uses_prior_completed_channel() -> None:
    feat = _feat(n=120)
    feat.dc_low[20][34] = 1.0001
    feat.close[34] = 1.0000
    feat.open[35] = 1.0000
    tr = tl._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("donchian_channel_exit"))
    assert tr.exit_reason == "donchian_channel_exit"
    assert tr.exit_time == feat.index[35].to_pydatetime()


def test_cost_stress_reduces_net_r_deterministically() -> None:
    feat = _feat()
    feat.spread_pips[:] = 1.0
    feat.high[33] = 1.0040
    tr = tl._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("fixed_2r_target"))
    base = tr.net_r(tl.COST_BASE)
    stress = tr.net_r(tl.COST_STRESS_2X)
    assert stress < base < tr.gross_r_multiple
    assert tr.net_r(tl.COST_STRESS_2X) == stress


def test_m30_has_no_h1_trend_gate() -> None:
    # When H1 is not in the ladder's trend set (M30), signals do not require H1 align.
    feat = _feat(execution_tf="M30", h1_available=False)
    feat.h1_standard[:] = -1  # opposing H1; must be ignored for M30
    feat.close[40] = 1.05
    feat.dc_high[20][40] = 1.00  # breakout long at bar 40
    direction = tl.compute_signal_direction(feat, _candidate(execution_tf="M30"))
    assert direction[40] == 1  # long fires despite opposing H1


def test_m15_requires_h1_trend_gate() -> None:
    feat = _feat(execution_tf="M15", h1_available=True)
    feat.h1_standard[:] = -1  # opposing H1 must block longs
    feat.close[40] = 1.05
    feat.dc_high[20][40] = 1.00
    direction = tl.compute_signal_direction(feat, _candidate(execution_tf="M15"))
    assert direction[40] == 0  # blocked by H1


def test_train_filters_are_timeframe_aware() -> None:
    good = {
        "trade_count": 100, "expectancy_r": 0.05, "profit_factor": 1.10,
        "pairs_nonneg": 4, "top_pair_positive_r_concentration": 0.3,
    }
    # 100 trades passes M15/M30 (>=80) but FAILS M3 (>=150)
    assert tl.apply_train_filters(good, 0.0, execution_tf="M15")["eligible"] is True
    assert tl.apply_train_filters(good, 0.0, execution_tf="M30")["eligible"] is True
    assert tl.apply_train_filters(good, 0.0, execution_tf="M3")["eligible"] is False
    assert tl.TRAIN_MIN_TRADES_BY_TF == {"M3": 150, "M15": 80, "M30": 80}


def test_rank_and_select_ignores_validation_and_rejects_when_none() -> None:
    import inspect

    assert list(inspect.signature(tl.rank_and_select).parameters) == ["evaluations"]
    base = {"trade_count": 30, "expectancy_r": -0.1, "profit_factor": 0.8, "pairs_nonneg": 1,
            "top_pair_positive_r_concentration": 0.9, "avg_spread_atr_ratio": 0.4}
    ev = {
        "candidate_id": "C026_TF_001", "execution_timeframe": "M15", "candidate": {"candidate_id": "C026_TF_001"},
        "base": base, "stress_2x": {"expectancy_r": -0.2},
        "filters": tl.apply_train_filters(base, -0.2, execution_tf="M15"),
    }
    sel = tl.rank_and_select([ev])
    assert sel["selection_uses_validation"] is False
    assert sel["champion_candidate_id"] is None
    assert sel["classification"] == "REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE"


def test_cost_diagnostic_for_frame_is_deterministic() -> None:
    n = 200
    idx = pd.DatetimeIndex([datetime(2022, 1, 3, tzinfo=UTC) + timedelta(minutes=15 * i) for i in range(n)])
    rng = np.linspace(1.0, 1.02, n)
    df = pd.DataFrame(
        {
            "open": rng, "high": rng + 0.001, "low": rng - 0.001, "close": rng,
            "bid_close": rng - 0.00005, "ask_close": rng + 0.00005,
        },
        index=idx,
    )
    a = tl.cost_diagnostic_for_frame(df, 0.0001)
    b = tl.cost_diagnostic_for_frame(df, 0.0001)
    assert a == b
    assert a["status"] == "OK"
    assert a["median_spread_atr"] > 0
    assert a["median_spread_pips"] == pytest.approx(1.0, abs=1e-6)  # 0.0001 spread / 0.0001 pip
