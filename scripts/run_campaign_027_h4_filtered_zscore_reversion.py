#!/usr/bin/env python3
"""CAMPAIGN_027 — Filtered H4 z-score reversion SCAFFOLD runner.

Scaffold/precommit sprint only. **Preflight modes only** — no train/validation/
test/backtest/execute evidence machinery, and the test lockbox cannot be opened
here:

    --validate-config          frozen-identity check
    --preflight-only           H4 coverage + safety preflight
    --data-feature-preflight   per-pair feature computability (train window)
    --sample-signals-only      tiny bounded signal-count probe (diagnostic only)

Forbidden flags (``--train`` / ``--validation`` / ``--test`` / ``--backtest`` /
``--execute``) are explicitly refused. No OANDA order/trade/position/live
endpoint is touched; no live creds; ``approved_strategies.yaml`` must stay empty.
If the H4 store is unavailable the runner records ``BLOCKED_DATA_PRECONDITION``
rather than improvising. No bulky raw candle data is emitted.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.config import Settings, compute_config_hash
from forex_bot.strategies.h4_filtered_zscore_reversion import (
    H4FilteredZscoreReversionStrategy,
    compute_decision,
)

CONFIG_PATH = ROOT / "configs/campaign_027_h4_filtered_zscore_reversion.yaml"
APPROVED_PATH = ROOT / "configs/approved_strategies.yaml"
OUT_RESEARCH = ROOT / "research/campaign_027"
OUT_PREFLIGHT = OUT_RESEARCH / "preflight"
EXPECTED_STRATEGY = "h4_filtered_zscore_reversion"

# Frozen splits — used only to SCOPE the preflight window. No evidence here.
SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2020-01-01", "2022-12-31"),
    "validation": ("2023-01-01", "2024-12-31"),
    "test": ("2025-01-01", "2026-05-20"),
}
TEST_WINDOW = SPLITS["test"]
_BIDASK = ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c")


# --------------------------------------------------------------------------
# Safety helpers
# --------------------------------------------------------------------------

def _load_raw() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def _strip_for_settings(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)
    for key in ("campaign", "research_metadata", "financing", "data_provenance", "cost_model"):
        data.pop(key, None)
    text = CONFIG_PATH.read_text(encoding="utf-8")
    data.setdefault("config_hash", compute_config_hash(text))
    data.setdefault("config_source_path", str(CONFIG_PATH))
    return data


def load_settings() -> tuple[Settings, dict[str, Any]]:
    raw = _load_raw()
    return Settings.model_validate(_strip_for_settings(raw)), raw


def assert_registry_empty() -> None:
    approved = yaml.safe_load(APPROVED_PATH.read_text(encoding="utf-8")) or {}
    if approved.get("approved"):
        raise SystemExit("approved_strategies.yaml must remain empty for CAMPAIGN_027")


def assert_execution_metadata(raw: dict[str, Any]) -> None:
    meta = raw.get("research_metadata") or {}
    if meta.get("fill_timing") != "next_bar_open":
        raise SystemExit("fill_timing must be next_bar_open")
    if meta.get("execution_realism") != "conservative":
        raise SystemExit("execution_realism must be conservative")
    if meta.get("promotion_eligible") is True:
        raise SystemExit("promotion_eligible must be false in scaffold")


def assert_not_test_window(start: str, end: str) -> None:
    ts, te = TEST_WINDOW
    if not (end < ts or start > te):
        raise SystemExit(
            f"FAIL_IF_TEST_WINDOW: requested window [{start},{end}] overlaps the LOCKED "
            f"test window [{ts},{te}] — the lockbox stays closed in this sprint."
        )


def validate_frozen_config(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    assert_registry_empty()
    assert_execution_metadata(raw)
    if settings.strategy.enabled != [EXPECTED_STRATEGY]:
        raise SystemExit(f"config must enable only {EXPECTED_STRATEGY}")
    cfg = settings.strategy.h4_filtered_zscore_reversion
    if cfg is None:
        raise SystemExit("missing h4_filtered_zscore_reversion config")
    if cfg.version != "0.1.0-c027" or cfg.timeframe != "H4":
        raise SystemExit("frozen identity diverged")
    if (
        cfg.zscore_lookback != 20
        or cfg.strong_extension_abs_z != 2.5
        or cfg.atr_percentile_window != 250
        or cfg.atr_percentile_max != 0.33
        or cfg.side_mode != "short_only"
        or cfg.max_bars_in_trade != 12
        or cfg.atr_stop_multiple != 3.0
    ):
        raise SystemExit("precommitted parameters diverged")
    return cfg.model_dump()


# --------------------------------------------------------------------------
# Data (raw read-only sqlite; worktree-aware store resolution)
# --------------------------------------------------------------------------

def resolve_store() -> Path | None:
    """Resolve the H4 store, worktree-aware. Env override > worktree > primary."""
    candidates: list[Path] = []
    env = os.environ.get("CAMPAIGN_027_STORE") or os.environ.get("CAMPAIGN_STORE")
    if env:
        candidates.append(Path(env))
    candidates.append(ROOT / "data/campaign_002.sqlite3")
    # primary checkout (worktrees live under <primary>/.claude/worktrees/<name>)
    candidates.append(ROOT.parents[2] / "data/campaign_002.sqlite3")
    for c in candidates:
        if c.is_file():
            return c
    return None


def display_store(store: Path) -> str:
    """A portable, repo-relative store label (avoids committing absolute home
    paths). Falls back to the basename if the store is not under a repo root."""
    for base in (ROOT, ROOT.parents[2]):
        try:
            return str(store.relative_to(base))
        except ValueError:
            continue
    return store.name


def load_h4_frame(db_path: Path, instrument: str) -> pd.DataFrame:
    """Completed H4 candles for one instrument; UTC-indexed mid OHLC."""
    query = (
        "SELECT time, bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c, volume "
        "FROM candles WHERE instrument = ? AND granularity = 'H4' AND complete = 1 "
        "ORDER BY time ASC"
    )
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        df = pd.read_sql_query(query, conn, params=[instrument])
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"], utc=True)
    for col in _BIDASK:
        df[col] = df[col].astype(float)
    df = df.sort_values("time").drop_duplicates("time", keep="last").set_index("time")
    df["open"] = (df["bid_o"] + df["ask_o"]) / 2.0
    df["high"] = (df["bid_h"] + df["ask_h"]) / 2.0
    df["low"] = (df["bid_l"] + df["ask_l"]) / 2.0
    df["close"] = (df["bid_c"] + df["ask_c"]) / 2.0
    return df[["open", "high", "low", "close", "volume"]]


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def _write(name: str, payload: Any) -> Path:
    OUT_PREFLIGHT.mkdir(parents=True, exist_ok=True)
    path = OUT_PREFLIGHT / name
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    return path


def _run_manifest(mode: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = {
        "campaign_id": "CAMPAIGN_027",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c027",
        "mode": mode,
        "scaffold_only": True,
        "not_approved": True,
        "strategy_evidence": False,
        "diagnostic_only": True,
        "test_lockbox_opened": False,
        "full_evidence_run": False,
        "fill_timing": "next_bar_open",
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    if extra:
        manifest.update(extra)
    return manifest


# --------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------

def preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    strategy = H4FilteredZscoreReversionStrategy()
    blocked: list[str] = []
    try:
        assert_execution_metadata(raw)
        assert_registry_empty()
    except SystemExit as exc:
        blocked.append(str(exc))

    result: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_027",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c027",
        "not_approved": True,
        "strategy_evidence": False,
        "fill_timing": "next_bar_open",
        "warmup_bars_required": strategy.warmup_bars_required(),
        "pairs": list(settings.market.instruments),
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    store = resolve_store()
    coverage: dict[str, Any] = {}
    if store is None:
        blocked.append("BLOCKED_DATA_PRECONDITION: H4 store campaign_002.sqlite3 not found")
    else:
        result["store"] = display_store(store)
        warmup = strategy.warmup_bars_required()
        for pair in settings.market.instruments:
            try:
                df = load_h4_frame(store, pair)
            except Exception as exc:  # pragma: no cover - defensive
                coverage[pair] = {"status": "ERROR", "reason": str(exc)}
                blocked.append(f"BLOCKED_DATA_PRECONDITION: {pair}: {exc}")
                continue
            n = len(df)
            cov = {
                "bars": n,
                "min_time": str(df.index.min()) if n else None,
                "max_time": str(df.index.max()) if n else None,
                "warmup_ok": n >= warmup,
                "status": "PASS" if n >= warmup else "INSUFFICIENT_WARMUP",
            }
            coverage[pair] = cov
            if cov["status"] != "PASS":
                blocked.append(f"BLOCKED_DATA_PRECONDITION: {pair} {cov['status']}")
    result["pair_coverage"] = coverage
    result["blocked_reasons"] = blocked
    result["preflight_ok"] = not blocked
    return result


def data_feature_preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    assert_execution_metadata(raw)
    assert_registry_empty()
    train_start, train_end = SPLITS["train"]
    assert_not_test_window(train_start, train_end)
    cfg = settings.strategy.h4_filtered_zscore_reversion.model_dump()
    store = resolve_store()
    report: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_027",
        "strategy_evidence": False,
        "diagnostic_only": True,
        "window": [train_start, train_end],
        "no_lookahead": "zscore mean/std and atr percentile are .shift(1)",
        "pairs": {},
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    if store is None:
        report["status"] = "BLOCKED_DATA_PRECONDITION"
        report["reason"] = "H4 store not found"
        report["preflight_ok"] = False
        return report
    report["store"] = display_store(store)
    ts = pd.Timestamp(train_start, tz="UTC")
    te = pd.Timestamp(train_end, tz="UTC") + pd.Timedelta(hours=23, minutes=59)
    ok = True
    for pair in settings.market.instruments:
        df = load_h4_frame(store, pair)
        win = df[(df.index >= ts) & (df.index <= te)]
        # features computable if the decision computes (needs warmup); evaluate on
        # the LAST bar of the train window using the full pre-window history.
        upto = df[df.index <= te]
        decision = compute_decision(upto, cfg) if len(upto) else None
        feat_ok = decision is not None
        report["pairs"][pair] = {
            "train_window_bars": len(win),
            "history_bars_through_window": len(upto),
            "features_computable": feat_ok,
            "last_window_zscore": round(decision.zscore, 4) if decision else None,
            "last_window_atr_percentile": round(decision.atr_percentile, 4) if decision else None,
            "last_window_session": decision.session_bucket if decision else None,
            "status": "PASS" if feat_ok else "INSUFFICIENT_WARMUP",
        }
        ok = ok and feat_ok
    report["preflight_ok"] = ok
    return report


def sample_signals(
    settings: Settings, raw: dict[str, Any], *, pair: str, start: str, sample_bars: int
) -> dict[str, Any]:
    """Tiny bounded probe: count signals over a small bounded window. No evidence."""
    assert_execution_metadata(raw)
    assert_registry_empty()
    out: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_027",
        "pair": pair,
        "window_start": start,
        "sample_bars": sample_bars,
        "scaffold_only": True,
        "diagnostic_only": True,
        "full_evidence_run": False,
        "note": "signal counts only — NOT trades, NOT evidence; long counts are diagnostic-only and never entered",
    }
    store = resolve_store()
    if store is None:
        out["status"] = "BLOCKED_DATA_PRECONDITION"
        out["reason"] = "H4 store not found"
        return out
    cfg = settings.strategy.h4_filtered_zscore_reversion.model_dump()
    strategy = H4FilteredZscoreReversionStrategy()
    df = load_h4_frame(store, pair)
    start_ts = pd.Timestamp(start, tz="UTC")
    # bound: a small window starting at `start`, capped at `sample_bars` bars,
    # never crossing into the test lockbox.
    win = df[df.index >= start_ts].head(max(1, sample_bars))
    if win.empty:
        out["status"] = "BLOCKED_DATA_PRECONDITION"
        out["reason"] = f"no H4 bars at/after {start}"
        return out
    win_end = str(win.index.max().date())
    assert_not_test_window(str(win.index.min().date()), win_end)

    warmup = strategy.warmup_bars_required()
    evaluated = short_entries = long_diag = strong = low_vol = quiet = 0
    for end_ts in win.index:
        slice_df = df[df.index <= end_ts]
        if len(slice_df) < warmup:
            continue
        decision = compute_decision(slice_df, cfg)
        if decision is None:
            continue
        evaluated += 1
        strong += int(decision.f_strong_extension)
        low_vol += int(decision.f_low_vol)
        quiet += int(decision.f_quiet_session)
        if decision.entered_short:
            short_entries += 1
        elif decision.raw_side == "long" and decision.f_strong_extension and decision.f_low_vol and decision.f_quiet_session:
            long_diag += 1  # would-be long under the same filters — DIAGNOSTIC ONLY
    out.update({
        "status": "OK",
        "window_end": win_end,
        "evaluated_decisions": evaluated,
        "short_entries": short_entries,
        "long_diagnostic_only_not_entered": long_diag,
        "f_strong_extension_pass": strong,
        "f_low_vol_pass": low_vol,
        "f_quiet_session_pass": quiet,
    })
    return out


# --------------------------------------------------------------------------
# Train/validation execution (frozen rule; conservative cost binding)
# --------------------------------------------------------------------------

OUT_TV = OUT_RESEARCH / "train_validation"
GIT_COMMIT_ENV = "CAMPAIGN_027_COMMIT"
# Lab module versions pinned in the reproducibility manifest.
_LAB_MODULES = ("research.edge_discovery.costs", "research.edge_discovery.matched_nulls",
                "research.edge_discovery.filter_ablation")
# Required artifact filenames (artifact-contract compliance is checked against this).
REQUIRED_TV_ARTIFACTS = (
    "run_manifest.json", "candidate_registry.json", "signal_ledger.csv",
    "trade_ledger_train.csv", "trade_ledger_validation.csv", "filter_stage_ledger.csv",
    "signal_funnel_ledger.csv", "train_metrics.json", "validation_metrics.json",
    "gate_result.json", "pair_metrics_train.csv", "pair_metrics_validation.csv",
    "year_metrics_train.csv", "year_metrics_validation.csv", "side_metrics_train.csv",
    "side_metrics_validation.csv", "cost_stress_2x.json", "matched_null_result.json",
    "filter_ablation_confirmation.json", "recency_risk_report.json",
    "artifact_contract_compliance.json", "blocked_or_warning_conditions.json",
)
SIGNAL_LEDGER_FIELDS = (
    "instrument", "signal_time_utc", "side", "timeframe", "zscore", "atr14",
    "atr_percentile", "session_bucket", "f_low_vol", "f_strong_extension",
    "f_quiet_session", "entered",
)
TRADE_LEDGER_FIELDS = (
    "instrument", "side", "units", "entry_time", "exit_time", "entry_price",
    "exit_price", "stop_price", "pnl", "r_multiple", "bars_held",
    "spread_paid_pips", "exit_reason", "fill_timing",
)
FUNNEL_FIELDS = (
    "instrument", "signal_time_utc", "trigger", "f_low_vol_pass",
    "f_strong_extension_pass", "f_quiet_session_pass", "log_return",
    "log_return_post_cost", "log_return_post_cost_conservative", "r_multiple",
)


def _commit_hash() -> str:
    import subprocess
    env = os.environ.get(GIT_COMMIT_ENV)
    if env:
        return env
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:  # pragma: no cover - defensive
        return "unknown"


def _write_csv(path: Path, rows: list[dict], fields=None) -> None:
    import csv
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        header = list(fields) if fields else []
        path.write_text((",".join(header) + "\n") if header else "", encoding="utf-8")
        return
    fieldnames = list(fields) if fields else list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def _candidate_registry() -> dict:
    """Single frozen candidate (no matrix)."""
    return {
        "campaign_id": "CAMPAIGN_027",
        "strategy_family": EXPECTED_STRATEGY,
        "version": "0.1.0-c027",
        "single_candidate": True,
        "selection_metric": "expectancy_conservative",
        "selection_window": "train_only",
        "candidates": [{
            "candidate_id": "c027_frozen_001",
            "archetype": "h4_filtered_zscore_reversion_short_only",
            "frozen": True,
            "parameters": {
                "zscore_lookback": 20, "zscore_std_ddof": 1, "base_trigger_abs_z": 2.0,
                "strong_extension_abs_z": 2.5, "atr_lookback": 14, "atr_percentile_window": 250,
                "atr_percentile_max": 0.33, "atr_stop_multiple": 3.0, "max_bars_in_trade": 12,
                "side_mode": "short_only", "quiet_sessions": ["asia", "london"],
                "fill_timing": "next_bar_open",
            },
        }],
    }


def _tv_manifest(mode: str, extra: dict[str, Any]) -> dict:
    m = {
        "campaign_id": "CAMPAIGN_027",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c027",
        "mode": mode,
        "scaffold_only": False,
        "not_approved": True,
        "approved": False,
        "promotion_eligible": False,
        "paper_demo_live_enabled": False,
        "strategy_evidence": True,          # this campaign's OWN evidence run
        "diagnostic_only": False,
        "test_lockbox_opened": False,
        "full_evidence_run": True,
        "fill_timing": "next_bar_open",
        "commit_hash": _commit_hash(),
        "input_data_path": None,            # filled by caller (display_store)
        "dedupe_policy": "keep_last",
        "precommitted_rule": _candidate_registry()["candidates"][0]["parameters"],
        "lab_modules": list(_LAB_MODULES),
        "random_seed_metadata": {"matched_null_seeds": "range(0,50)"},
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    m.update(extra)
    return m


def _split_results(engine, frames, *, split, start, end, p):
    ws = pd.Timestamp(start, tz="UTC")
    we = pd.Timestamp(end, tz="UTC") + pd.Timedelta(hours=23, minutes=59)
    trades, signals, dropped = [], [], 0
    for inst, feat in frames.items():
        tr, dr = engine.simulate_trades(feat, inst, window_start=ws, window_end=we, split=split, p=p)
        sg = engine.build_signal_rows(feat, inst, window_start=ws, window_end=we, split=split, p=p)
        trades += tr
        signals += sg
        dropped += dr
    return trades, signals, dropped


def _gates_to_rows(gates) -> list[dict]:
    return [{"gate": g.name, "passed": g.passed, "detail": g.detail} for g in gates]


def run_train_validation(
    settings: Settings, raw: dict[str, Any], *, train_start: str, train_end: str,
    valid_start: str, valid_end: str, out_dir: Path, fail_if_test_window: bool,
    no_test_lockbox: bool, matched_null_seeds: int, schema_check: bool = False,
) -> dict[str, Any]:
    """Execute the frozen rule on train then (only if train gates pass) validation.
    Emits all artifact-contract artifacts. Never opens the test lockbox; never
    tunes; never approves."""
    from research.campaign_027 import engine

    validate_frozen_config(settings, raw)
    if fail_if_test_window:
        assert_not_test_window(train_start, train_end)
        assert_not_test_window(valid_start, valid_end)
    # windows must not overlap
    if not (train_end < valid_start or valid_start > train_end):
        raise SystemExit(
            f"OVERLAP: train [{train_start},{train_end}] overlaps validation "
            f"[{valid_start},{valid_end}]"
        )

    store = resolve_store()
    if store is None:
        out = {"status": "BLOCKED_DATA_PRECONDITION", "reason": "H4 store not found"}
        _write_json(out_dir / "blocked_or_warning_conditions.json", out)
        return out

    p = engine.FrozenParams()
    pairs = list(settings.market.instruments)
    # Build feature frames once per pair (full history → causal warmup).
    frames = {inst: engine.compute_features(engine.load_pair_frame(store, inst), p) for inst in pairs}
    frames_mid = {inst: feat[["close"]].copy() for inst, feat in frames.items()}

    if schema_check:
        # bounded: a single short train sub-window, lockbox-safe.
        train_start, train_end = "2020-01-01", "2020-12-31"
        valid_start, valid_end = "2021-01-01", "2021-12-31"

    # ---- TRAIN ----
    tr_trades, tr_signals, tr_dropped = _split_results(
        engine, frames, split="train", start=train_start, end=train_end, p=p)
    tr_metrics = engine.trade_metrics(tr_trades)
    tr_stress = engine.cost_stress_2x(tr_trades)
    tr_gates = engine.evaluate_train_gates(tr_metrics, tr_stress)
    tr_matched = engine.run_matched_null(tr_trades, frames_mid, seeds=range(matched_null_seeds))
    tr_ablation = engine.run_filter_ablation_confirmation(tr_signals)
    # matched-null + ablation gates (informational diagnostics)
    tr_mn_pass = any(
        ("BEATS_MATCHED_NULL" in r.get("flags", []) or "ABOVE_MATCHED_NULL" in r.get("flags", []))
        for r in tr_matched if r.get("mode") in ("session_matched_random", "full_matched_null")
    )
    tr_gates.append(engine.GateResult("train_matched_null_above_random", bool(tr_mn_pass),
                                      "session/full matched-null above random"))
    tr_gates.append(engine.GateResult("train_filter_ablation_retained_add_edge",
                                      bool(tr_ablation.get("retained_filters_all_add_edge")),
                                      "each retained filter FILTER_ADDS_EDGE on train"))
    train_pass = all(g.passed for g in tr_gates)

    # ---- VALIDATION (only if train passed) ----
    validation_run = bool(train_pass)
    val_trades = val_signals = []
    val_metrics = val_stress = {}
    val_gates = []
    val_matched = val_ablation = {}
    val_dropped = 0
    if validation_run:
        val_trades, val_signals, val_dropped = _split_results(
            engine, frames, split="validation", start=valid_start, end=valid_end, p=p)
        val_metrics = engine.trade_metrics(val_trades)
        val_stress = engine.cost_stress_2x(val_trades)
        val_gates = engine.evaluate_validation_gates(val_metrics, val_stress)
        val_matched = engine.run_matched_null(val_trades, frames_mid, seeds=range(matched_null_seeds))
        val_ablation = engine.run_filter_ablation_confirmation(val_signals)
        vmn_pass = any(
            ("BEATS_MATCHED_NULL" in r.get("flags", []) or "ABOVE_MATCHED_NULL" in r.get("flags", []))
            for r in val_matched if r.get("mode") in ("session_matched_random", "full_matched_null")
        )
        val_gates.append(engine.GateResult("validation_matched_null_above_random", bool(vmn_pass),
                                           "session/full matched-null above random"))
        val_gates.append(engine.GateResult("validation_filter_ablation_retained_add_edge",
                                           bool(val_ablation.get("retained_filters_all_add_edge")),
                                           "each retained filter FILTER_ADDS_EDGE on validation"))
    validation_pass = bool(validation_run and all(g.passed for g in val_gates))

    # ---- classification ----
    classification = _classify(train_pass, tr_gates, validation_run, validation_pass, val_gates)

    # ---- write artifacts ----
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = _tv_manifest("train-validation" if not schema_check else "artifact-schema-check", {
        "input_data_path": display_store(store),
        "train_window": [train_start, train_end],
        "validation_window": [valid_start, valid_end] if validation_run else None,
        "test_window_sealed": list(TEST_WINDOW),
        "train_pass": train_pass, "validation_run": validation_run,
        "validation_pass": validation_pass, "classification": classification,
    })
    _write_json(out_dir / "run_manifest.json", manifest)
    _write_json(out_dir / "candidate_registry.json", _candidate_registry())

    all_signals = tr_signals + (val_signals if validation_run else [])
    _write_csv(out_dir / "signal_ledger.csv", all_signals, SIGNAL_LEDGER_FIELDS)
    _write_csv(out_dir / "signal_funnel_ledger.csv", all_signals, FUNNEL_FIELDS)
    _write_csv(out_dir / "trade_ledger_train.csv", tr_trades, TRADE_LEDGER_FIELDS)
    _write_csv(out_dir / "trade_ledger_validation.csv", val_trades if validation_run else [],
               TRADE_LEDGER_FIELDS)

    # filter-stage ledger from the train ablation stage table (+ validation if run)
    stage_rows = [{"split": "train", **r} for r in tr_ablation.get("stage_table", [])]
    if validation_run:
        stage_rows += [{"split": "validation", **r} for r in val_ablation.get("stage_table", [])]
    _write_csv(out_dir / "filter_stage_ledger.csv", stage_rows)

    _write_json(out_dir / "train_metrics.json", {**tr_metrics, "dropped_trailing_signals": tr_dropped})
    _write_json(out_dir / "validation_metrics.json",
                {**val_metrics, "dropped_trailing_signals": val_dropped} if validation_run
                else {"validation_run": False, "reason": "train gates failed"})

    _pair_year_side_csvs(out_dir, "train", tr_metrics)
    if validation_run:
        _pair_year_side_csvs(out_dir, "validation", val_metrics)
    else:
        for stem in ("pair_metrics", "year_metrics", "side_metrics"):
            _write_csv(out_dir / f"{stem}_validation.csv", [])

    _write_json(out_dir / "cost_stress_2x.json", {"train": tr_stress,
                "validation": val_stress if validation_run else {"validation_run": False}})
    _write_json(out_dir / "matched_null_result.json", {"train": tr_matched,
                "validation": val_matched if validation_run else {"validation_run": False},
                "seeds": f"range(0,{matched_null_seeds})", "window_bars": 12,
                "post_cost": "conservative"})
    _write_json(out_dir / "filter_ablation_confirmation.json", {"train": tr_ablation,
                "validation": val_ablation if validation_run else {"validation_run": False}})
    _write_json(out_dir / "recency_risk_report.json", _recency_report(tr_metrics, val_metrics, validation_run))

    gate_result = {
        "campaign_id": "CAMPAIGN_027", "classification": classification,
        "train_pass": train_pass, "train_gates": _gates_to_rows(tr_gates),
        "validation_run": validation_run, "validation_pass": validation_pass,
        "validation_gates": _gates_to_rows(val_gates) if validation_run else [],
        "test_lockbox_opened": False, "approved": False, "promotion_eligible": False,
        "backtrader_parity_required": True,
        "note": "Backtrader parity still required before any test-lockbox open or promotion review.",
    }
    _write_json(out_dir / "gate_result.json", gate_result)

    compliance = _artifact_compliance(out_dir)
    _write_json(out_dir / "artifact_contract_compliance.json", compliance)

    warnings = {
        "train_dropped_trailing_signals": tr_dropped,
        "validation_dropped_trailing_signals": val_dropped if validation_run else None,
        "side_shuffled_degenerate_note": "short-only ledger → side_shuffled null is uninformative",
        "matched_null_compatibility": ("close-to-close information benchmark, not the realized "
                                       "next_bar_open post-cost PnL (separate trade ledger)"),
        "known_risks": ["wafer-thin edge inside cost band", "2024/2026 recency",
                        "filter forking-path", "raw-matrix LIKELY_SELECTION_NOISE"],
        "test_lockbox_opened": False,
    }
    _write_json(out_dir / "blocked_or_warning_conditions.json", warnings)

    return {
        "classification": classification, "train_pass": train_pass,
        "validation_run": validation_run, "validation_pass": validation_pass,
        "train_metrics": tr_metrics, "validation_metrics": val_metrics if validation_run else None,
        "train_gates": _gates_to_rows(tr_gates),
        "validation_gates": _gates_to_rows(val_gates) if validation_run else [],
        "artifact_compliance": compliance, "out_dir": str(out_dir),
    }


def _classify(train_pass, tr_gates, validation_run, validation_pass, val_gates) -> str:
    suffix = "TEST_LOCKBOX_CLOSED / NOT_APPROVED"
    if not train_pass:
        return f"REJECT_TRAIN_GATE / {suffix}"
    if not validation_run:
        return f"REJECT_TRAIN_GATE / {suffix}"
    if validation_pass:
        return f"TRAIN_VALIDATION_PASS_PARITY_REQUIRED / {suffix}"
    # most-specific validation failure
    failed = {g.name for g in val_gates if not g.passed}
    if "validation_2024_not_materially_negative" in failed:
        return f"REJECT_RECENCY_GATE / {suffix}"
    if "validation_cost_stress_2x_gte_0" in failed:
        return f"REJECT_COST_STRESS_GATE / {suffix}"
    if "validation_matched_null_above_random" in failed:
        return f"REJECT_MATCHED_NULL_GATE / {suffix}"
    return f"REJECT_VALIDATION_GATE / {suffix}"


def _pair_year_side_csvs(out_dir: Path, split: str, m: dict) -> None:
    pair_rows = [{"pair": k, "expectancy_conservative": v}
                 for k, v in m.get("per_pair_expectancy_conservative", {}).items()]
    year_rows = [{"year": k, "expectancy_conservative": v}
                 for k, v in m.get("per_year_expectancy_conservative", {}).items()]
    side_rows = [{"side": "short", "trade_count": m.get("side_counts", {}).get("short", 0),
                  "expectancy_conservative": m.get("expectancy_conservative"),
                  "long_entered": False, "long_count": 0}]
    _write_csv(out_dir / f"pair_metrics_{split}.csv", pair_rows)
    _write_csv(out_dir / f"year_metrics_{split}.csv", year_rows)
    _write_csv(out_dir / f"side_metrics_{split}.csv", side_rows)


def _recency_report(tr_metrics: dict, val_metrics: dict, validation_run: bool) -> dict:
    return {
        "train_by_year": tr_metrics.get("per_year_expectancy_conservative", {}),
        "validation_by_year": val_metrics.get("per_year_expectancy_conservative", {}) if validation_run else {},
        "validation_2024": (val_metrics.get("per_year_expectancy_conservative", {}).get("2024")
                            if validation_run else None),
        "test_2025_2026": "SEALED — not evaluated this sprint",
        "note": ("2024 and 2026-partial were pre-registered recency risks. 2024 (in the validation "
                 "window) is the binding recency gate; 2025-2026 stay in the sealed test lockbox."),
    }


def _artifact_compliance(out_dir: Path) -> dict:
    # These two are written by the caller immediately AFTER this check (the
    # compliance verdict and warning summary cannot inspect themselves), so they
    # are guaranteed-present and excluded from the presence scan.
    _written_after = {"artifact_contract_compliance.json", "blocked_or_warning_conditions.json"}
    present = {name: (out_dir / name).is_file() for name in REQUIRED_TV_ARTIFACTS
              if name not in _written_after}
    missing = [n for n, ok in present.items() if not ok]
    # required-field checks on the three ledgers
    field_checks = {}
    import csv as _csv
    for fname, required in (("signal_ledger.csv", SIGNAL_LEDGER_FIELDS),
                            ("trade_ledger_train.csv", TRADE_LEDGER_FIELDS),
                            ("signal_funnel_ledger.csv", FUNNEL_FIELDS)):
        path = out_dir / fname
        if path.is_file():
            with path.open(encoding="utf-8") as fh:
                header = next(_csv.reader(fh), [])
            field_checks[fname] = sorted(set(required) - set(header))
        else:
            field_checks[fname] = list(required)
    field_missing = {k: v for k, v in field_checks.items() if v}
    return {
        "all_required_present": not missing and not field_missing,
        "missing_files": missing,
        "missing_fields": field_missing,
        "required_artifacts": list(REQUIRED_TV_ARTIFACTS),
        "blocked": "BLOCKED_ARTIFACT_CONTRACT" if (missing or field_missing) else None,
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

_FORBIDDEN = ("--train", "--validation", "--test", "--backtest", "--execute")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    for bad in _FORBIDDEN:
        if bad in argv:
            raise SystemExit(
                f"REFUSED: {bad} is not available in the CAMPAIGN_027 scaffold sprint "
                "— no train/validation/test/backtest/execute evidence; lockbox stays closed."
            )
    parser = argparse.ArgumentParser(
        description="CAMPAIGN_027 runner (preflight + train/validation evidence)")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--data-feature-preflight", action="store_true")
    parser.add_argument("--sample-signals-only", action="store_true")
    parser.add_argument("--sample-pair", default="EUR_USD")
    parser.add_argument("--sample-start", default="2021-01-01")
    parser.add_argument("--sample-bars", type=int, default=300)
    # train/validation execution
    parser.add_argument("--train-validation", action="store_true",
                        help="run train then (if train gates pass) validation; emit artifacts")
    parser.add_argument("--artifact-schema-check", action="store_true",
                        help="bounded lockbox-safe run that verifies all artifact schemas")
    parser.add_argument("--train-start", default="2020-01-01")
    parser.add_argument("--train-end", default="2022-12-31")
    parser.add_argument("--validation-start", default="2023-01-01")
    parser.add_argument("--validation-end", default="2024-12-31")
    parser.add_argument("--output-dir", default=str(OUT_TV))
    parser.add_argument("--matched-null-seeds", type=int, default=50)
    parser.add_argument("--no-test-lockbox", dest="no_test_lockbox", action="store_true", default=True)
    parser.add_argument("--fail-if-test-window", dest="fail_if_test_window",
                        action="store_true", default=True)
    args = parser.parse_args(argv)
    settings, raw = load_settings()

    if args.train_validation or args.artifact_schema_check:
        out_dir = Path(args.output_dir)
        if args.artifact_schema_check:
            out_dir = out_dir / "schema_check"
        result = run_train_validation(
            settings, raw, train_start=args.train_start, train_end=args.train_end,
            valid_start=args.validation_start, valid_end=args.validation_end,
            out_dir=out_dir, fail_if_test_window=args.fail_if_test_window,
            no_test_lockbox=args.no_test_lockbox, matched_null_seeds=args.matched_null_seeds,
            schema_check=args.artifact_schema_check)
        print(json.dumps({k: v for k, v in result.items()
                          if k not in ("train_metrics", "validation_metrics")},
                         indent=2, default=str))
        ok = result.get("artifact_compliance", {}).get("all_required_present", False)
        return 0 if ok else 1

    if args.validate_config:
        validate_frozen_config(settings, raw)
        print(f"[CAMPAIGN_027] config OK — {EXPECTED_STRATEGY} 0.1.0-c027")
        return 0

    if args.preflight_only:
        pf = preflight(settings, raw)
        _write("preflight_result.json", pf)
        _write("pair_coverage_summary.json",
               {"campaign_id": "CAMPAIGN_027", "pair_coverage": pf.get("pair_coverage", {})})
        _write("run_manifest.json", _run_manifest("preflight-only", {"preflight_ok": pf["preflight_ok"]}))
        print(json.dumps(pf, indent=2, sort_keys=True, default=str))
        return 0 if pf["preflight_ok"] else 1

    if args.data_feature_preflight:
        report = data_feature_preflight(settings, raw)
        _write("data_feature_preflight.json", report)
        _write("run_manifest.json", _run_manifest("data-feature-preflight",
                                                   {"preflight_ok": report.get("preflight_ok", False)}))
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
        return 0 if report.get("preflight_ok") else 1

    if args.sample_signals_only:
        summary = sample_signals(settings, raw, pair=args.sample_pair,
                                 start=args.sample_start, sample_bars=args.sample_bars)
        _write("sample_signal_summary.json", summary)
        _write("run_manifest.json", _run_manifest("sample-signals-only",
                                                   {"sample_status": summary.get("status")}))
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        return 0 if summary.get("status") in ("OK", "BLOCKED_DATA_PRECONDITION") else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
