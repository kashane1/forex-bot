"""CAMPAIGN_027 train/validation engine + runner guardrails.

Deterministic synthetic-frame tests of the frozen-rule simulation (no DB):
short-only, long diagnostic-only, next_bar_open entry, 12-bar time stop, 3xATR
protective stop, same-bar adverse-first tie, R-multiple / conservative-cost /
2x-stress determinism, artifact-contract fields. Plus runner guardrails: windows
cannot overlap, the test lockbox cannot be touched, no approval flags, no broker
import.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest
from research.campaign_027 import engine as eng

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts/run_campaign_027_h4_filtered_zscore_reversion.py"


@pytest.fixture(scope="module")
def runner():
    spec = importlib.util.spec_from_file_location("run_c027_tv", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _mk_feat(rows: list[dict]) -> pd.DataFrame:
    """Build a feature frame (4h UTC index) with explicit per-bar control. Each
    row: open, high, atr14, zscore, f_low_vol, f_quiet_session, session_bucket."""
    idx = pd.date_range("2021-01-04 00:00", periods=len(rows), freq="4h", tz="UTC")
    df = pd.DataFrame(index=idx)
    df["open"] = [r["open"] for r in rows]
    df["high"] = [r["high"] for r in rows]
    df["close"] = [r.get("close", r["open"]) for r in rows]
    df["spread_open"] = [r.get("spread_open", 0.0001) for r in rows]
    df["atr14"] = [r["atr14"] for r in rows]
    df["zscore"] = [r["zscore"] for r in rows]
    df["atr_percentile"] = [r.get("atr_percentile", 0.1) for r in rows]
    df["session_bucket"] = [r.get("session_bucket", "asia") for r in rows]
    df["f_strong_extension"] = df["zscore"].abs() >= 2.5
    df["f_low_vol"] = [r.get("f_low_vol", True) for r in rows]
    df["f_quiet_session"] = [r.get("f_quiet_session", True) for r in rows]
    df["base_trigger"] = df["zscore"].abs() >= 2.0
    df["raw_side"] = ["short" if r["zscore"] > 0 else "long" for r in rows]
    return df


def _quiet_short_series(n=16, *, trigger_at=0, atr=0.01, entry_px=1.0, highs=None):
    rows = []
    for i in range(n):
        z = 3.0 if i == trigger_at else 0.0  # only one short trigger
        hi = (highs[i] if highs is not None else entry_px)  # default: never hits stop
        rows.append({"open": entry_px, "high": hi, "atr14": atr, "zscore": z,
                     "session_bucket": "asia"})
    return _mk_feat(rows)


P = eng.FrozenParams()
WS = pd.Timestamp("2021-01-01", tz="UTC")
WE = pd.Timestamp("2021-12-31 23:59", tz="UTC")


# ---- short-only + entry mechanics ------------------------------------------

def test_only_short_entries_and_next_bar_open():
    feat = _quiet_short_series()
    trades, dropped = eng.simulate_trades(feat, "EUR_USD", window_start=WS, window_end=WE,
                                        split="train", p=P)
    assert len(trades) == 1
    t = trades[0]
    assert t["side"] == "short"
    assert t["fill_timing"] == "next_bar_open"
    # entry at the open of bar t+1 (trigger at index 0 → entry bar index 1)
    assert t["entry_time"] == feat.index[1].isoformat()
    assert t["entry_price"] == pytest.approx(1.0)


def test_long_signal_is_diagnostic_only_never_entered():
    rows = [{"open": 1.0, "high": 1.0, "atr14": 0.01,
             "zscore": (-3.0 if i == 0 else 0.0), "session_bucket": "asia"} for i in range(16)]
    feat = _mk_feat(rows)
    trades, _ = eng.simulate_trades(feat, "EUR_USD", window_start=WS, window_end=WE,
                                  split="train", p=P)
    assert trades == []  # long never entered
    sig = eng.build_signal_rows(feat, "EUR_USD", window_start=WS, window_end=WE, split="train", p=P)
    longs = [s for s in sig if s["side"] == "long"]
    assert longs and all(s["entered"] is False for s in longs)


def test_time_stop_is_12_bars():
    feat = _quiet_short_series()  # highs never reach the stop → time stop
    trades, _ = eng.simulate_trades(feat, "EUR_USD", window_start=WS, window_end=WE,
                                  split="train", p=P)
    t = trades[0]
    assert t["exit_reason"] == "time_stop"
    assert t["bars_held"] == 12
    # exit at open of entry_bar (1) + 12 = bar 13
    assert t["exit_time"] == feat.index[13].isoformat()


def test_protective_atr_stop_3x_and_bars_held():
    atr = 0.01
    stop = 1.0 + 3.0 * atr  # 1.03
    highs = [1.0] * 16
    highs[4] = 1.05  # bar 4 spikes above stop → protective stop fills (entry bar=1)
    feat = _quiet_short_series(atr=atr, highs=highs)
    trades, _ = eng.simulate_trades(feat, "EUR_USD", window_start=WS, window_end=WE,
                                  split="train", p=P)
    t = trades[0]
    assert t["exit_reason"] == "protective_atr_stop"
    assert t["stop_price"] == pytest.approx(stop)
    assert t["exit_price"] == pytest.approx(stop)
    assert t["bars_held"] == 3  # bar 4 - entry bar 1


def test_same_bar_adverse_first_tie():
    atr = 0.01
    stop = 1.0 + 3.0 * atr
    highs = [1.0] * 16
    highs[3] = stop  # high exactly equals the stop → adverse stop wins the tie
    feat = _quiet_short_series(atr=atr, highs=highs)
    trades, _ = eng.simulate_trades(feat, "EUR_USD", window_start=WS, window_end=WE,
                                  split="train", p=P)
    assert trades[0]["exit_reason"] == "protective_atr_stop"


# ---- determinism: R-multiple, conservative cost, 2x stress -----------------

def test_r_multiple_and_conservative_cost_deterministic():
    # time-stop trade with a known favourable exit price for a short.
    atr = 0.01
    rows = [{"open": 1.0, "high": 1.0, "atr14": atr, "zscore": (3.0 if i == 0 else 0.0),
             "close": 1.0, "session_bucket": "asia"} for i in range(16)]
    rows[13]["open"] = 0.99  # exit (open of bar 13) below entry → profit for a short
    feat = _mk_feat(rows)
    trades, _ = eng.simulate_trades(feat, "EUR_USD", window_start=WS, window_end=WE,
                                  split="train", p=P)
    t = trades[0]
    import math
    signed = -math.log(0.99 / 1.0)
    risk_frac = 3.0 * atr / 1.0
    assert t["r_multiple"] == pytest.approx(round(signed / risk_frac, 6))
    pip = 0.0001
    cost_cons = (1.5 * pip + 2 * 0.2 * pip) / 1.0 + eng.financing_stress_fraction(
        "EUR_USD", bars_held=12, hours_per_bar=4.0)
    assert t["pnl"] == pytest.approx(round(signed - cost_cons, 8))
    # run twice → identical
    again, _ = eng.simulate_trades(feat, "EUR_USD", window_start=WS, window_end=WE,
                                 split="train", p=P)
    assert again[0] == t


def test_cost_stress_2x_deterministic_and_more_negative():
    feat = _quiet_short_series()
    trades, _ = eng.simulate_trades(feat, "EUR_USD", window_start=WS, window_end=WE,
                                  split="train", p=P)
    s1 = eng.cost_stress_2x(trades)
    s2 = eng.cost_stress_2x(trades)
    assert s1 == s2
    base = eng.trade_metrics(trades)["expectancy_conservative"]
    assert s1["expectancy_conservative_2x"] <= base  # doubled cost cannot improve


# ---- features parity with the frozen strategy module -----------------------

def test_features_match_frozen_strategy_module():
    import numpy as np

    from forex_bot.strategies.h4_filtered_zscore_reversion import compute_decision
    rng = np.random.default_rng(7)
    n = 400
    idx = pd.date_range("2020-06-01", periods=n, freq="4h", tz="UTC")
    close = 1.10 + np.cumsum(rng.normal(0, 0.0008, n))
    df = pd.DataFrame(index=idx)
    df["open"] = close
    df["high"] = close + 0.0010
    df["low"] = close - 0.0010
    df["close"] = close
    df["spread_open"] = 0.0001
    df["spread_close"] = 0.0001
    feat = eng.compute_features(df, P)
    cfg = {"zscore_lookback": 20, "strong_extension_abs_z": 2.5, "atr_lookback": 14,
           "atr_percentile_window": 250, "atr_percentile_max": 0.33,
           "quiet_sessions": ("asia", "london"), "zscore_std_ddof": 1}
    for k in (300, 350, 399):
        dec = compute_decision(df.iloc[: k + 1], cfg)
        assert dec is not None
        assert feat["zscore"].iloc[k] == pytest.approx(dec.zscore, rel=1e-9)
        assert feat["atr14"].iloc[k] == pytest.approx(dec.atr14, rel=1e-9)
        assert feat["atr_percentile"].iloc[k] == pytest.approx(dec.atr_percentile, rel=1e-9)


# ---- runner guardrails -----------------------------------------------------

def test_runner_refuses_bare_evidence_flags(runner):
    for flag in ("--train", "--validation", "--test", "--backtest", "--execute"):
        with pytest.raises(SystemExit) as exc:
            runner.main([flag])
        assert "REFUSED" in str(exc.value)


def test_train_validation_windows_cannot_overlap(runner):
    settings, raw = runner.load_settings()
    with pytest.raises(SystemExit) as exc:
        runner.run_train_validation(
            settings, raw, train_start="2020-01-01", train_end="2022-12-31",
            valid_start="2022-06-01", valid_end="2023-12-31", out_dir=Path("/tmp/c027x"),
            fail_if_test_window=True, no_test_lockbox=True, matched_null_seeds=5)
    assert "OVERLAP" in str(exc.value)


def test_train_validation_refuses_test_lockbox(runner):
    settings, raw = runner.load_settings()
    with pytest.raises(SystemExit) as exc:
        runner.run_train_validation(
            settings, raw, train_start="2025-01-01", train_end="2025-12-31",
            valid_start="2026-01-01", valid_end="2026-05-20", out_dir=Path("/tmp/c027y"),
            fail_if_test_window=True, no_test_lockbox=True, matched_null_seeds=5)
    assert "FAIL_IF_TEST_WINDOW" in str(exc.value)


def test_manifest_and_registry_carry_no_approval(runner):
    m = runner._tv_manifest("train-validation", {})
    assert m["approved"] is False
    assert m["promotion_eligible"] is False
    assert m["paper_demo_live_enabled"] is False
    assert m["test_lockbox_opened"] is False
    reg = runner._candidate_registry()
    assert reg["single_candidate"] is True
    assert len(reg["candidates"]) == 1


def test_required_artifact_fields_declared(runner):
    # signal/trade/funnel required fields per the artifact contract
    assert set(runner.SIGNAL_LEDGER_FIELDS) >= {
        "instrument", "signal_time_utc", "side", "timeframe", "zscore", "atr14",
        "atr_percentile", "session_bucket", "f_low_vol", "f_strong_extension",
        "f_quiet_session", "entered"}
    assert set(runner.TRADE_LEDGER_FIELDS) >= {
        "instrument", "side", "units", "entry_time", "exit_time", "entry_price",
        "exit_price", "stop_price", "pnl", "r_multiple", "bars_held",
        "spread_paid_pips", "exit_reason", "fill_timing"}


def test_engine_has_no_broker_or_executor_import():
    src = (ROOT / "research/campaign_027/engine.py").read_text(encoding="utf-8")
    for forbidden in ("forex_bot.broker", "forex_bot.loops", "forex_bot.execution",
                      "forex_bot.approval", "import oanda"):
        assert forbidden not in src
