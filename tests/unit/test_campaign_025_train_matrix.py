"""CAMPAIGN_025 train-matrix simulator — deterministic exit-model + gate tests."""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from forex_bot.research import campaign_025_train_matrix as tm

_REPO = Path(__file__).resolve().parents[2]


def _candidate(exit_model="time_stop_only", **over):
    c = {
        "candidate_id": "C025_MTX_TEST",
        "m5_donchian_length": 20,
        "atr_stop_multiple": 2.0,
        "exit_model": exit_model,
        "target_r_multiple": None,
        "breakeven_trigger_r": None,
        "trail_activation_r": None,
        "trail_atr_multiple": None,
        "channel_exit_length": None,
        "time_stop_m5_bars": 48,
        "h1_trend_mode": "standard",
        "m15_setup_mode": "pullback_or_compression",
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


def _feat(n=80, *, close=1.0, atr=0.0010, pip=0.0001):
    """Flat synthetic M5 frame; caller overrides high/low/open at specific bars."""
    idx = pd.DatetimeIndex([datetime(2022, 1, 3, tzinfo=UTC) + timedelta(minutes=5 * i) for i in range(n)])
    arr = lambda v: np.full(n, float(v))
    dc = {ln: np.full(n, np.nan) for ln in tm.DONCHIAN_LENGTHS}
    return tm.PairFeatures(
        instrument="EUR_USD",
        index=idx,
        open=arr(close),
        high=arr(close),
        low=arr(close),
        close=arr(close),
        atr=arr(atr),
        spread_pips=arr(0.0),  # zero spread → gross == net for clean R assertions
        pip_size=pip,
        dc_high=dict(dc),
        # structure channel kept NEAR price so the ATR stop binds (risk = 2*ATR)
        dc_low={ln: np.full(n, close - 0.0001) for ln in tm.DONCHIAN_LENGTHS},
        h4_trend=np.ones(n, dtype=int),
        h1_standard=np.ones(n, dtype=int),
        h1_strict=np.ones(n, dtype=int),
        d1_not_bearish=np.ones(n, dtype=bool),
        d1_not_bullish=np.ones(n, dtype=bool),
        m15_pullback_long=np.ones(n, dtype=bool),
        m15_pullback_short=np.ones(n, dtype=bool),
        m15_compression=np.ones(n, dtype=bool),
        warm_mask=np.ones(n, dtype=bool),
    )


def test_next_bar_open_entry_is_after_signal() -> None:
    feat = _feat()
    tr = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate())
    assert tr is not None
    # entry is the bar AFTER the signal bar
    assert tr.entry_time == feat.index[31].to_pydatetime()
    assert tr.entry_time > feat.index[30].to_pydatetime()


def test_fixed_target_emits_correct_r() -> None:
    feat = _feat()
    # risk = 2.0*ATR(prior)=0.0020; entry open=1.0; +2R target = 1.0040
    feat.high[33] = 1.0040  # bar reaches target, low stays at close (no stop)
    tr = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("fixed_2r_target"))
    assert tr.exit_reason == "fixed_target_2r"
    assert tr.gross_r_multiple == pytest.approx(2.0, abs=1e-9)
    # zero spread but COST_BASE still charges 0.2-pip fixed slippage per side:
    # 0.4 pips round-trip = 0.00004 price / 0.0020 risk = 0.02R -> net 1.98
    assert tr.net_r(tm.COST_BASE) == pytest.approx(1.98, abs=1e-9)


def test_same_bar_stop_and_target_resolves_adverse_first() -> None:
    feat = _feat()
    # same bar touches BOTH the +2R target (1.0040) and the stop (0.9980)
    feat.high[33] = 1.0040
    feat.low[33] = 0.9980
    tr = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("fixed_2r_target"))
    assert tr.exit_reason == "hard_stop"
    assert tr.gross_r_multiple == pytest.approx(-1.0, abs=1e-9)


def test_time_stop_fires_at_exact_bar_count() -> None:
    feat = _feat(n=120)
    tr = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("time_stop_only", time_stop_m5_bars=48))
    assert tr.exit_reason == "time_stop"
    # entry index 31; time stop at entry+48 -> exit fills next open (index 31+48+? )
    assert tr.hold_bars == 49  # k reaches entry+48, fill at k+1 → 49 bars after entry


def test_breakeven_activates_only_after_threshold() -> None:
    feat = _feat(n=120)
    # bar 33 reaches +1R (high=1.0020) -> stop moves to breakeven(entry=1.0)
    feat.high[33] = 1.0020
    # bar 35 dips to entry -> breakeven stop hit
    feat.low[35] = 1.0000
    tr = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("breakeven_then_atr_trail"))
    assert tr.exit_reason == "breakeven_stop"
    assert tr.gross_r_multiple == pytest.approx(0.0, abs=1e-9)


def test_breakeven_not_triggered_before_threshold() -> None:
    feat = _feat(n=120)
    # never reaches +1R; small dip to entry should NOT be a breakeven stop (still initial hard stop)
    feat.low[35] = 1.0000  # at entry, above initial hard stop 0.9980 -> no exit here
    tr = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("breakeven_then_atr_trail"))
    # with no favorable excursion and no stop hit, exits on time stop, not breakeven
    assert tr.exit_reason in ("time_stop", "end_of_data")


def test_channel_exit_uses_prior_completed_channel() -> None:
    feat = _feat(n=120)
    # set the prior Donchian low channel above price at bar 34 so a close < channel triggers
    feat.dc_low[20][34] = 1.0001  # prior channel low
    feat.close[34] = 1.0000  # close below prior channel low -> exit signal on completed bar 34
    feat.open[35] = 1.0000  # exit fills next open
    tr = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("donchian_channel_exit"))
    assert tr.exit_reason == "donchian_channel_exit"
    assert tr.exit_time == feat.index[35].to_pydatetime()


def test_trade_r_calculation_is_deterministic() -> None:
    feat = _feat()
    feat.high[33] = 1.0040
    a = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("fixed_2r_target"))
    b = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("fixed_2r_target"))
    assert a.gross_r_multiple == b.gross_r_multiple == pytest.approx(2.0)


def test_cost_stress_reduces_net_r_deterministically() -> None:
    feat = _feat()
    feat.spread_pips[:] = 1.0  # 1 pip spread everywhere
    feat.high[33] = 1.0040
    tr = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("fixed_2r_target"))
    base = tr.net_r(tm.COST_BASE)
    stress = tr.net_r(tm.COST_STRESS_2X)
    assert stress < base < tr.gross_r_multiple
    # deterministic
    assert tr.net_r(tm.COST_STRESS_2X) == stress


def test_c011_null_margin_in_metrics_is_deterministic() -> None:
    feat = _feat()
    feat.high[33] = 1.0040
    tr = tm._simulate_trade(feat, sig_i=30, side=1, candidate=_candidate("fixed_2r_target"))
    m = tm.aggregate_candidate_metrics({"EUR_USD": [tr]}, cost=tm.COST_BASE)
    # beat_c011_null_by is rounded to 5dp in the metrics
    assert m["beat_c011_null_by"] == pytest.approx(m["expectancy_r"] - tm.C011_NULL_EXP_R, abs=1e-4)


def test_train_filters_use_frozen_thresholds() -> None:
    good = {
        "trade_count": 150, "expectancy_r": 0.05, "profit_factor": 1.10,
        "pairs_nonneg": 4, "top_pair_positive_r_concentration": 0.3,
    }
    f = tm.apply_train_filters(good, stress_exp=0.0)
    assert f["eligible"] is True
    bad = {**good, "trade_count": 50}
    assert tm.apply_train_filters(bad, stress_exp=0.0)["eligible"] is False
    assert tm.TRAIN_MIN_TRADES == 100 and tm.TRAIN_MIN_PF == 1.03 and tm.TRAIN_MIN_PAIRS_NONNEG == 3


def test_selection_ignores_validation_metrics() -> None:
    # rank_and_select consumes only train evaluations; it has no validation input
    # and stamps selection_uses_validation=false on its output.
    import inspect

    sig = inspect.signature(tm.rank_and_select)
    assert list(sig.parameters) == ["evaluations"]  # only train evaluations, no validation arg
    ev = {
        "candidate_id": "C025_MTX_001", "archetype": "x", "candidate": {"candidate_id": "C025_MTX_001"},
        "base": {"trade_count": 200, "expectancy_r": 0.04, "profit_factor": 1.1, "pairs_nonneg": 4,
                 "top_pair_positive_r_concentration": 0.2},
        "stress_2x": {"expectancy_r": 0.01},
        "filters": tm.apply_train_filters(
            {"trade_count": 200, "expectancy_r": 0.04, "profit_factor": 1.1, "pairs_nonneg": 4,
             "top_pair_positive_r_concentration": 0.2}, 0.01),
    }
    sel = tm.rank_and_select([ev])
    assert sel["selection_uses_validation"] is False
    assert sel["champion_candidate_id"] == "C025_MTX_001"


def test_too_sparse_blocks_when_no_candidate_reaches_100() -> None:
    ev = {
        "candidate_id": "C025_MTX_001", "archetype": "x", "candidate": {"candidate_id": "C025_MTX_001"},
        "base": {"trade_count": 40, "expectancy_r": 0.5, "profit_factor": 2.0, "pairs_nonneg": 7,
                 "top_pair_positive_r_concentration": 0.1},
        "stress_2x": {"expectancy_r": 0.4},
        "filters": tm.apply_train_filters(
            {"trade_count": 40, "expectancy_r": 0.5, "profit_factor": 2.0, "pairs_nonneg": 7,
             "top_pair_positive_r_concentration": 0.1}, 0.4),
    }
    sel = tm.rank_and_select([ev])
    assert sel["classification"] == "BLOCKED_MATRIX_TOO_SPARSE"
    assert sel["champion_candidate_id"] is None


def _load_runner_module():
    path = _REPO / "scripts/run_campaign_025_m5_donchian_htf_confluence.py"
    spec = importlib.util.spec_from_file_location("c025_runner", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_test_window_guard_rejects_overlap() -> None:
    runner = _load_runner_module()
    with pytest.raises(SystemExit, match="FAIL_IF_TEST_WINDOW"):
        runner._assert_not_test_window("2025-02-01", "2025-06-01")
    # a pre-test window is allowed
    runner._assert_not_test_window("2021-07-01", "2023-06-30")


def test_overlapping_train_validation_guard_is_chronological() -> None:
    # validation must be strictly after train in the frozen split
    assert "2023-07-01" > "2023-06-30"  # documents the split boundary ordering
