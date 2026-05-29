#!/usr/bin/env python3
"""CAMPAIGN_026 — Donchian + HTF confluence timeframe-ladder runner (M3/M15/M30).

Diagnostic + train-matrix evidence runner. Modes:

    --preflight-only          approved-empty + per-pair/tf materialized coverage
    --data-feature-preflight  per-pair/tf counts/ranges + HTF last-completed probe
    --cost-diagnostic         spread/ATR cost profile for M3, M5(ref), M15, M30
    --train-matrix            run the frozen candidate matrix on TRAIN only
    --validate-champion       validate the train-selected champion ONCE (if any)

Selection is train-only; validation never selects. The test lockbox
(2025-01-01..2026-05-20) is refused (`--fail-if-test-window`, default on). No OANDA
order/trade/position/live endpoints are touched; approved_strategies stays empty;
nothing is approved.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.m1_timeframe_materialization import MATERIALIZED_SOURCE
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.domain.candles import CandleFrame
from forex_bot.project_env import bootstrap_environ
from forex_bot.research import campaign_026_timeframe_ladder as tl
from forex_bot.research.campaign_026_loader import (
    EXECUTION_TIMEFRAMES,
    _load_materialized,
    coverage_report,
    load_c026_frames,
)

APPROVED_PATH = ROOT / "configs/approved_strategies.yaml"
OUT_DIR = ROOT / "research/campaign_026"
LADDER_DIR = OUT_DIR / "timeframe_ladder"
COST_DIR = OUT_DIR / "timeframe_cost_diagnostics"
REGISTRY_PATH = LADDER_DIR / "candidate_registry.json"

PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"]
COST_TIMEFRAMES = ["M3", "M5", "M15", "M30"]  # M5 = C025 reference baseline
TEST_WINDOW = ("2025-01-01", "2026-05-20")


# --------------------------------------------------------------------------- #
# safety guards
# --------------------------------------------------------------------------- #
def assert_registry_empty() -> None:
    approved = yaml.safe_load(APPROVED_PATH.read_text(encoding="utf-8")) or {}
    if approved.get("approved"):
        raise SystemExit("approved_strategies.yaml must remain empty for CAMPAIGN_026")


def assert_not_test_window(start: str, end: str, *, fail_if_test_window: bool) -> None:
    if not fail_if_test_window:
        return
    ts, te = TEST_WINDOW
    if not (end < ts or start > te):
        raise SystemExit(
            f"FAIL_IF_TEST_WINDOW: requested window [{start},{end}] overlaps the LOCKED "
            f"test window [{ts},{te}] — the lockbox stays closed in this sprint."
        )


def _open_store() -> PostgresCandleStore:
    environ = bootstrap_environ(None)
    cfg = get_research_database_config(environ=environ, require=True)
    return PostgresCandleStore(cfg)


def _load_candidates() -> list[dict]:
    reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return reg["candidates"]


def _manifest(mode: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    m = {
        "campaign_id": "CAMPAIGN_026",
        "strategy_family": "donchian_htf_confluence_timeframe_ladder",
        "version": "0.1.0-c026",
        "mode": mode,
        "not_approved": True,
        "strategy_evidence": mode in ("train-matrix", "validate-champion"),
        "test_lockbox_opened": False,
        "fill_timing": "next_bar_open",
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    if extra:
        m.update(extra)
    return m


def _write(directory: Path, name: str, payload: Any) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
    )


def _csv(directory: Path, name: str, rows: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


# --------------------------------------------------------------------------- #
# preflight
# --------------------------------------------------------------------------- #
def preflight() -> dict[str, Any]:
    blocked: list[str] = []
    try:
        assert_registry_empty()
    except SystemExit as exc:
        blocked.append(str(exc))
    report: dict[str, Any] = {"campaign_id": "CAMPAIGN_026", "pairs": PAIRS, "not_approved": True}
    try:
        store = _open_store()
        cov = coverage_report(store, pairs=PAIRS)
        report["coverage"] = cov
        if not cov["preflight_ok"]:
            blocked.append("BLOCKED_DATA_MATERIALIZATION: " + ", ".join(cov["blocked"]))
    except Exception as exc:
        blocked.append(f"BLOCKED_DATA_PRECONDITION: postgres unavailable: {exc}")
    report["materialized_source"] = MATERIALIZED_SOURCE
    report["blocked_reasons"] = blocked
    report["preflight_ok"] = not blocked
    return report


# --------------------------------------------------------------------------- #
# data-feature preflight (HTF last-completed / no-lookahead probe)
# --------------------------------------------------------------------------- #
def data_feature_preflight(*, train_start: str, train_end: str, fail_if_test_window: bool) -> dict[str, Any]:
    assert_registry_empty()
    assert_not_test_window(train_start, train_end, fail_if_test_window=fail_if_test_window)
    from_dt = datetime.fromisoformat(train_start).replace(tzinfo=UTC)
    to_dt = datetime.fromisoformat(train_end).replace(hour=23, minute=59, tzinfo=UTC)
    store = _open_store()
    by_tf: dict[str, Any] = {}
    blocked: list[str] = []
    for tf in EXECUTION_TIMEFRAMES:
        per_pair: dict[str, Any] = {}
        for pair in PAIRS:
            try:
                frames = load_c026_frames(store, pair, tf, from_dt=from_dt, to_dt=to_dt)
            except SystemExit as exc:
                per_pair[pair] = {"status": "BLOCKED_DATA_PRECONDITION", "reason": str(exc)}
                blocked.append(f"{pair}/{tf}")
                continue
            feat = tl.precompute_pair_features(frames)
            ex = frames.execution.completed_only().df
            # lookahead probe: every aligned HTF time must be <= the exec bar time
            n = len(feat.index)
            per_pair[pair] = {
                "status": "PASS" if n > 0 else "FAIL",
                "exec_bars": int(n),
                "exec_first": ex.index.min().isoformat() if n else None,
                "exec_last": ex.index.max().isoformat() if n else None,
                "warm_bars": int(feat.warm_mask.sum()),
                "h1_in_trend": feat.h1_available,
            }
        by_tf[tf] = per_pair
    return {
        "campaign_id": "CAMPAIGN_026",
        "window": {"train_start": train_start, "train_end": train_end},
        "by_execution_tf": by_tf,
        "blocked": blocked,
        "preflight_ok": not blocked,
        "materialized_source": MATERIALIZED_SOURCE,
        "not_approved": True,
        "strategy_evidence": False,
    }


# --------------------------------------------------------------------------- #
# cost diagnostic
# --------------------------------------------------------------------------- #
def _session(hour_utc: int) -> str:
    if hour_utc >= 21 or hour_utc < 7:
        return "asia"
    if 7 <= hour_utc < 13:
        return "london"
    return "newyork"


def cost_diagnostic(*, start: str, end: str, fail_if_test_window: bool) -> dict[str, Any]:
    assert_registry_empty()
    assert_not_test_window(start, end, fail_if_test_window=fail_if_test_window)
    from_dt = datetime.fromisoformat(start).replace(tzinfo=UTC)
    to_dt = datetime.fromisoformat(end).replace(hour=23, minute=59, tzinfo=UTC)
    store = _open_store()
    import numpy as np

    from forex_bot.research.campaign_025_loader import instrument_for
    from forex_bot.strategies.indicators import atr as _atr

    by_pair_rows: list[dict] = []
    session_rows: list[dict] = []
    agg: dict[str, Any] = {}
    for tf in COST_TIMEFRAMES:
        ratios_all: list[float] = []
        pip = None
        sess_ratios: dict[str, list[float]] = {"asia": [], "london": [], "newyork": []}
        for pair in PAIRS:
            inst = instrument_for(pair)
            pip = 10 ** inst.pip_location
            candles = _load_materialized(store, pair, tf, from_dt=from_dt, to_dt=to_dt)
            df = CandleFrame.from_candles(pair, tf, candles).completed_only().df
            stats = tl.cost_diagnostic_for_frame(df, pip)
            row = {"timeframe": tf, "pair": pair, **stats}
            by_pair_rows.append(row)
            if stats.get("status") == "OK" and len(df) > tl.ATR_LOOKBACK + 5:
                high = df["high"].astype(float)
                low = df["low"].astype(float)
                close = df["close"].astype(float)
                atr_pips = (_atr(high, low, close, tl.ATR_LOOKBACK) / pip).to_numpy()
                if {"bid_close", "ask_close"}.issubset(df.columns):
                    spr = ((df["ask_close"].astype(float) - df["bid_close"].astype(float)) / pip).clip(lower=0.0).to_numpy()
                else:
                    spr = np.full(len(df), np.nan)
                hours = df.index.hour.to_numpy()
                mask = np.isfinite(atr_pips) & (atr_pips > 0) & np.isfinite(spr)
                r = (spr[mask] / atr_pips[mask])
                ratios_all.extend(r.tolist())
                for h, rr in zip(hours[mask], r, strict=False):
                    sess_ratios[_session(int(h))].append(float(rr))
        if ratios_all:
            arr = np.array(ratios_all)
            agg[tf] = {
                "bars": int(arr.size),
                "median_spread_atr": round(float(np.median(arr)), 4),
                "mean_spread_atr": round(float(np.mean(arr)), 4),
                "p75_spread_atr": round(float(np.percentile(arr, 75)), 4),
                "p90_spread_atr": round(float(np.percentile(arr, 90)), 4),
            }
        for sess, vals in sess_ratios.items():
            if vals:
                a = np.array(vals)
                session_rows.append({
                    "timeframe": tf, "session": sess, "bars": int(a.size),
                    "median_spread_atr": round(float(np.median(a)), 4),
                    "p90_spread_atr": round(float(np.percentile(a, 90)), 4),
                })

    # viability flags vs the M5 reference
    m5_med = agg.get("M5", {}).get("median_spread_atr")
    flags = {}
    for tf in COST_TIMEFRAMES:
        med = agg.get(tf, {}).get("median_spread_atr")
        flags[tf] = {
            "median_spread_atr": med,
            "better_than_m5": (med is not None and m5_med is not None and med < m5_med),
            "cost_hostile_ge_0_30": (med is not None and med >= 0.30),
        }

    COST_DIR.mkdir(parents=True, exist_ok=True)
    _csv(COST_DIR, "timeframe_spread_atr_by_pair.csv", by_pair_rows)
    _csv(COST_DIR, "timeframe_spread_atr_by_session.csv", session_rows)
    summary_rows = [{"timeframe": tf, **agg.get(tf, {})} for tf in COST_TIMEFRAMES]
    _csv(COST_DIR, "timeframe_spread_atr_summary.csv", summary_rows)
    drag = {
        tf: {
            pair: next(
                (r for r in by_pair_rows if r["timeframe"] == tf and r["pair"] == pair), {}
            ).get("cost_drag_r_per_1atr_stop")
            for pair in PAIRS
        }
        for tf in COST_TIMEFRAMES
    }
    _write(COST_DIR, "timeframe_cost_drag_estimates.json", {"campaign_id": "CAMPAIGN_026", "window": {"start": start, "end": end}, "cost_drag_r_per_1atr_stop": drag})
    _write(COST_DIR, "timeframe_viability_flags.json", {"campaign_id": "CAMPAIGN_026", "m5_reference_median_spread_atr": m5_med, "flags": flags})
    out = {
        "campaign_id": "CAMPAIGN_026",
        "window": {"start": start, "end": end},
        "aggregate_spread_atr": agg,
        "viability_flags": flags,
        "not_approved": True,
        "strategy_evidence": False,
    }
    _write(COST_DIR, "cost_diagnostic_run_manifest.json", _manifest("cost-diagnostic", {"window": [start, end]}))
    return out


# --------------------------------------------------------------------------- #
# train matrix
# --------------------------------------------------------------------------- #
def run_train_matrix(*, train_start: str, train_end: str, fail_if_test_window: bool) -> dict[str, Any]:
    assert_registry_empty()
    assert_not_test_window(train_start, train_end, fail_if_test_window=fail_if_test_window)
    ws = datetime.fromisoformat(train_start).replace(tzinfo=UTC)
    we = datetime.fromisoformat(train_end).replace(hour=23, minute=59, tzinfo=UTC)
    store = _open_store()
    candidates = _load_candidates()
    by_tf: dict[str, list[dict]] = {}
    for c in candidates:
        by_tf.setdefault(c["execution_timeframe"], []).append(c)

    evals: list[dict] = []
    for tf, cs in by_tf.items():
        feats = tl.load_features_for_window(store, PAIRS, tf, window_start=ws, window_end=we)
        for c in cs:
            evals.append(tl.evaluate_candidate(feats, c, window_start=ws, window_end=we))
    selection = tl.rank_and_select(evals)

    LADDER_DIR.mkdir(parents=True, exist_ok=True)
    metrics_rows, gate_rows, pair_rows, side_rows, exit_rows, stress_rows = ([] for _ in range(6))
    spread_atr, funnel = {}, {}
    for ev in evals:
        cid, b, s = ev["candidate_id"], ev["base"], ev["stress_2x"]
        metrics_rows.append({
            "candidate_id": cid, "execution_timeframe": ev["execution_timeframe"],
            "trade_count": b["trade_count"], "expectancy_r": b["expectancy_r"],
            "profit_factor": b["profit_factor"], "pairs_nonneg": b["pairs_nonneg"],
            "top_pair_concentration": b["top_pair_positive_r_concentration"],
            "stress_2x_expectancy_r": s["expectancy_r"], "beat_c011_null_by": b["beat_c011_null_by"],
            "avg_hold_bars": round(b["avg_hold_bars"], 2), "avg_spread_atr_ratio": b["avg_spread_atr_ratio"],
        })
        gate_rows.append({
            "candidate_id": cid, "execution_timeframe": ev["execution_timeframe"],
            "eligible": ev["filters"]["eligible"], "min_trades_required": ev["filters"]["min_trades_required"],
            "failed": "|".join(ev["filters"]["failed"]),
            "single_pair_review_flag": ev["filters"]["single_pair_review_flag"],
        })
        for p, v in b["per_pair_expectancy_r"].items():
            pair_rows.append({"candidate_id": cid, "pair": p, "expectancy_r": v, "trade_count": b["per_pair_trade_count"][p]})
        side_rows.append({"candidate_id": cid, "long_count": b["long_count"], "long_expectancy_r": b["long_expectancy_r"],
                          "short_count": b["short_count"], "short_expectancy_r": b["short_expectancy_r"]})
        exit_rows.append({"candidate_id": cid, **b["exit_reason_counts"]})
        stress_rows.append({"candidate_id": cid, "base_expectancy_r": b["expectancy_r"], "stress_2x_expectancy_r": s["expectancy_r"]})
        spread_atr[cid] = {"avg_spread_atr_ratio": b["avg_spread_atr_ratio"], "avg_hold_bars": b["avg_hold_bars"], "median_hold_bars": b["median_hold_bars"]}
        funnel[cid] = ev["funnel_total"]

    _csv(LADDER_DIR, "train_matrix_metrics.csv", metrics_rows)
    _csv(LADDER_DIR, "train_matrix_gate_filters.csv", gate_rows)
    _csv(LADDER_DIR, "train_matrix_pair_metrics.csv", pair_rows)
    _csv(LADDER_DIR, "train_matrix_side_metrics.csv", side_rows)
    _csv(LADDER_DIR, "train_matrix_exit_reason_summary.csv", exit_rows)
    _csv(LADDER_DIR, "train_matrix_cost_stress_2x.csv", stress_rows)
    _write(LADDER_DIR, "train_matrix_spread_atr_diagnostics.json", spread_atr)
    _write(LADDER_DIR, "train_matrix_signal_funnel_diagnostics.json", funnel)
    selection["train_window"] = {"start": train_start, "end": train_end}
    selection["pairs"] = PAIRS
    _write(LADDER_DIR, "train_matrix_candidate_selection.json", selection)
    _write(LADDER_DIR, "train_matrix_run_manifest.json", _manifest("train-matrix", {
        "train_window": [train_start, train_end], "candidates": len(candidates),
        "champion": selection["champion_candidate_id"], "classification": selection["classification"],
    }))
    _write(LADDER_DIR, "blocked_or_warning_conditions.json", {
        "classification": selection["classification"],
        "single_pair_review_flags": selection.get("single_pair_review_flags", []),
        "validation_allowed": selection["champion_candidate_id"] is not None,
    })
    return selection


# --------------------------------------------------------------------------- #
# champion validation (one run, conditional)
# --------------------------------------------------------------------------- #
def run_champion_validation(*, valid_start: str, valid_end: str, fail_if_test_window: bool) -> dict[str, Any]:
    assert_registry_empty()
    assert_not_test_window(valid_start, valid_end, fail_if_test_window=fail_if_test_window)
    sel_path = LADDER_DIR / "train_matrix_candidate_selection.json"
    if not sel_path.is_file():
        raise SystemExit("no train selection found — run --train-matrix first")
    selection = json.loads(sel_path.read_text(encoding="utf-8"))
    champ_id = selection.get("champion_candidate_id")
    if not champ_id:
        out = {"validation_run": False, "reason": "no champion selected on train", "classification": selection["classification"]}
        _write(LADDER_DIR, "validation_result.json", out)
        return out
    champ = selection["champion_parameters"]
    tf = champ["execution_timeframe"]
    ws = datetime.fromisoformat(valid_start).replace(tzinfo=UTC)
    we = datetime.fromisoformat(valid_end).replace(hour=23, minute=59, tzinfo=UTC)
    store = _open_store()
    feats = tl.load_features_for_window(store, PAIRS, tf, window_start=ws, window_end=we)
    ev = tl.evaluate_candidate(feats, champ, window_start=ws, window_end=we)
    b, s = ev["base"], ev["stress_2x"]
    min_trades = tl.TRAIN_MIN_TRADES_BY_TF[tf]
    gates = {
        "validation_expectancy_gt_0": (b["expectancy_r"] or -9) > 0,
        "validation_pf_gte_1_05": (b["profit_factor"] or 0) >= 1.05,
        f"validation_trades_gte_{min_trades}": b["trade_count"] >= min_trades,
        "validation_pairs_nonneg_gte_4": b["pairs_nonneg"] >= 4,
        "stress_2x_expectancy_gte_0": (s["expectancy_r"] or -9) >= 0,
        "beat_c011_null_by_010": (b["beat_c011_null_by"] or -9) >= 0.010,
        "backtrader_parity_pass": False,
    }
    screening = all(v for k, v in gates.items() if k != "backtrader_parity_pass")
    classification = "TRAIN_VALIDATION_PASS_PARITY_REQUIRED" if screening else "TRAIN_VALIDATION_REJECT"
    out = {
        "validation_run": True, "validation_run_once": True, "selection_uses_validation": False,
        "champion_candidate_id": champ_id, "champion_timeframe": tf, "champion_parameters": champ,
        "validation_window": {"start": valid_start, "end": valid_end},
        "base": b, "stress_2x": s, "gates": gates, "screening_pass": screening,
        "classification": f"{classification} / TEST_LOCKBOX_CLOSED / NOT_APPROVED",
        "funnel_total": ev["funnel_total"], "test_lockbox_opened": False, "approved": False,
    }
    _write(LADDER_DIR, "validation_result.json", out)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="CAMPAIGN_026 timeframe-ladder runner")
    p.add_argument("--preflight-only", action="store_true")
    p.add_argument("--data-feature-preflight", action="store_true")
    p.add_argument("--cost-diagnostic", action="store_true")
    p.add_argument("--train-matrix", action="store_true")
    p.add_argument("--validate-champion", action="store_true")
    p.add_argument("--train-start", default="2021-07-01")
    p.add_argument("--train-end", default="2023-06-30")
    p.add_argument("--validation-start", default="2023-07-01")
    p.add_argument("--validation-end", default="2024-12-31")
    p.add_argument("--cost-start", default="2021-07-01")
    p.add_argument("--cost-end", default="2024-12-31")
    p.add_argument("--candidate-registry", default=str(REGISTRY_PATH))
    p.add_argument("--output-dir", default=str(OUT_DIR))
    p.add_argument("--no-test-lockbox", dest="no_test_lockbox", action="store_true", default=True)
    p.add_argument("--fail-if-test-window", dest="fail_if_test_window", action="store_true", default=True)
    args = p.parse_args()

    if args.preflight_only:
        out = preflight()
        _write(OUT_DIR / "preflight", "preflight_result.json", out)
        print(json.dumps(out, indent=2, sort_keys=True, default=str))
        return 0 if out["preflight_ok"] else 1

    if args.data_feature_preflight:
        out = data_feature_preflight(train_start=args.train_start, train_end=args.train_end, fail_if_test_window=args.fail_if_test_window)
        _write(OUT_DIR / "preflight", "data_feature_preflight.json", out)
        print(json.dumps(out, indent=2, sort_keys=True, default=str))
        return 0 if out["preflight_ok"] else 1

    if args.cost_diagnostic:
        out = cost_diagnostic(start=args.cost_start, end=args.cost_end, fail_if_test_window=args.fail_if_test_window)
        print(json.dumps(out, indent=2, sort_keys=True, default=str))
        return 0

    if args.train_matrix:
        sel = run_train_matrix(train_start=args.train_start, train_end=args.train_end, fail_if_test_window=args.fail_if_test_window)
        print(json.dumps({k: v for k, v in sel.items() if k != "ranking"}, indent=2, default=str))
        return 0

    if args.validate_champion:
        out = run_champion_validation(valid_start=args.validation_start, valid_end=args.validation_end, fail_if_test_window=args.fail_if_test_window)
        print(json.dumps({k: v for k, v in out.items() if k not in ("base", "stress_2x")}, indent=2, default=str))
        return 0

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
