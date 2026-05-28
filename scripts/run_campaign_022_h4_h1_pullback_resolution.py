#!/usr/bin/env python3
"""CAMPAIGN_022 — H4/H1 pullback resolution entry evidence runner.

Frozen 0.1.0-c022. M15 execution + H4/H1 materialized context (no D1). next_bar_open.
NOT approved; approved_strategies.yaml stays []. Local research Postgres only.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.exporters import write_all
from forex_bot.backtesting.fills import FillModel
from forex_bot.config import Settings, compute_config_hash
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.campaign_022_loader import (
    C022Frames,
    instrument_for,
    load_c022_frames,
)
from forex_bot.research.execution_realism import FillTiming, parse_research_metadata
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.h4_h1_pullback_resolution_entry import (
    H4H1PullbackResolutionEntryStrategy,
)

CONFIG_PATH = ROOT / "configs/campaign_022_h4_h1_pullback_resolution.yaml"
OUT_BT = ROOT / "backtests/CAMPAIGN_022_h4_h1_pullback_resolution"
OUT_RESEARCH = ROOT / "research/campaign_022"
C011_NULL = ROOT / "research/null_baselines/campaign_011_deduped_null_baseline.json"
EXPECTED_STRATEGY = "h4_h1_pullback_resolution_entry"
EXPECTED_VERSION = "0.1.0-c022"

# Frozen splits — fixed BEFORE any results were seen (see EXECUTION_001_PLAN).
SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2021-06-01", "2023-12-31"),
    "validation": ("2024-01-01", "2025-06-30"),
    "test": ("2025-07-01", "2026-05-20"),
}

COST_BASE = {"name": "base", "spread_multiplier": 0.5, "fixed_slippage_pips": 0.2}
COST_STRESS_2X = {"name": "stress_2x", "spread_multiplier": 2.0, "fixed_slippage_pips": 0.5}

C011_NULL_EXP_R = -0.0029154071495408797
BEAT_NULL_MARGIN = 0.010
MATERIALIZED_SOURCE = "m1_materialized"
MIN_VALIDATION_TRADES = 150
MIN_VALIDATION_PAIRS_POSITIVE = 4

# Performance (results-identical, verified trade-for-trade):
#  - SIGNAL_WINDOW_BARS bounds the per-bar M15 history handed to the strategy.
#    1500 >> the strategy's ~120-bar need, so recursive EMA/ADX seed influence
#    decays to ~0 and signals are unchanged.
#  - the HTF indicator frame builder is memoized per static context frame.
SIGNAL_WINDOW_BARS = 1500
OUT_CELLS = OUT_RESEARCH / "cells"


def _install_perf_shims() -> None:
    """Memoize the strategy's HTF indicator-frame builder per context frame.

    Identical output (same pure function, cached by frame identity) — only
    removes redundant per-bar recomputation of EMA/ADX/RSI over the *static*
    H1/H4 frames. Verified trade-for-trade equal vs the unmemoized strategy.
    """
    import forex_bot.strategies.h4_h1_pullback_resolution_entry as strat

    if getattr(strat._htf_indicator_frame, "_c022_memoized", False):
        return
    orig = strat._htf_indicator_frame
    cache: dict[tuple, Any] = {}

    def memo(frame, *, ema_fast_len, ema_slow_len, adx_len=None, rsi_len=None):
        key = (id(frame), ema_fast_len, ema_slow_len, adx_len, rsi_len)
        cached = cache.get(key)
        if cached is None:
            cached = orig(
                frame,
                ema_fast_len=ema_fast_len,
                ema_slow_len=ema_slow_len,
                adx_len=adx_len,
                rsi_len=rsi_len,
            )
            cache[key] = cached
        return cached

    memo._c022_memoized = True  # type: ignore[attr-defined]
    strat._htf_indicator_frame = memo


def _parse(d: str) -> datetime:
    return datetime.fromisoformat(d).replace(tzinfo=UTC)


def _git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        return ""
    return r.stdout.strip()


def _load_raw() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def _strip_for_settings(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)
    for key in ("campaign", "research_metadata", "financing", "data_provenance"):
        data.pop(key, None)
    text = CONFIG_PATH.read_text(encoding="utf-8")
    data.setdefault("config_hash", compute_config_hash(text))
    data.setdefault("config_source_path", str(CONFIG_PATH))
    return data


def load_settings_from_campaign() -> tuple[Settings, dict[str, Any]]:
    raw = _load_raw()
    return Settings.model_validate(_strip_for_settings(raw)), raw


def validate_frozen_config(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    sc = settings.strategy
    if sc.enabled != [EXPECTED_STRATEGY]:
        raise SystemExit(f"config must enable only {EXPECTED_STRATEGY}")
    c = sc.h4_h1_pullback_resolution_entry
    if c is None:
        raise SystemExit("missing h4_h1_pullback_resolution_entry config")
    if c.version != EXPECTED_VERSION:
        raise SystemExit(f"version must be {EXPECTED_VERSION}")
    # Frozen parameter assertions — no retuning.
    if c.h4_adx_min != 20.0:
        raise SystemExit("frozen h4_adx_min must be 20.0 (C023 ADX22 is a separate campaign)")
    if c.adx_min != 18.0:
        raise SystemExit("frozen M15 adx_min must be 18.0")
    if c.atr_stop_multiple != 2.0 or c.max_bars_in_trade != 32:
        raise SystemExit("frozen stop/time parameters diverged")
    prov = raw.get("data_provenance") or {}
    for forbidden in ("d1agg_context", "d1agg_source", "d1_context", "d1_source"):
        if prov.get(forbidden) is not None:
            raise SystemExit(f"CAMPAIGN_022 has no daily layer; unexpected {forbidden!r}")
    for key in ("execution_m15", "context_h1", "context_h4"):
        if prov.get(key) != "m1_derived":
            raise SystemExit(f"data_provenance.{key} must be m1_derived")
    return c.model_dump()


def _metrics_to_dict(m: Any) -> dict[str, Any]:
    return {
        "trade_count": m.trade_count,
        "total_return_pct": float(m.total_return_pct),
        "max_drawdown_pct": float(m.max_drawdown_pct),
        "profit_factor": None if m.profit_factor == float("inf") else float(m.profit_factor),
        "expectancy_r": float(m.expectancy_r),
        "win_rate": float(m.win_rate),
        "average_spread_paid_pips": float(m.average_spread_paid_pips),
    }


@dataclass
class RunRecord:
    split: str
    cost_regime: str
    instrument: str
    metrics: dict[str, Any]
    trades_path: str


@dataclass
class CampaignCtx:
    settings: Settings
    raw: dict[str, Any]
    store: PostgresCandleStore
    risk_engine: RiskEngine
    strategy_cfg: dict[str, Any]
    data_provenance: dict[str, Any]
    fill_timing: str = "next_bar_open"
    runs: list[RunRecord] = field(default_factory=list)
    all_trades: list[pd.DataFrame] = field(default_factory=list)
    _frame_cache: dict[tuple[str, str], C022Frames] = field(default_factory=dict)


def load_ctx() -> CampaignCtx:
    bootstrap_environ()  # load repo-root .env if present
    settings, raw = load_settings_from_campaign()
    strategy_cfg = validate_frozen_config(settings, raw)
    meta = parse_research_metadata(raw.get("research_metadata"))
    if meta is None or meta.fill_timing != FillTiming.NEXT_BAR_OPEN:
        raise SystemExit("CAMPAIGN_022 requires research_metadata.fill_timing=next_bar_open")
    store = PostgresCandleStore(get_research_database_config())
    _install_perf_shims()
    return CampaignCtx(
        settings=settings,
        raw=raw,
        store=store,
        risk_engine=RiskEngine(settings, mode="backtest"),
        strategy_cfg=strategy_cfg,
        data_provenance=dict(raw.get("data_provenance") or {}),
    )


def _frames_for(ctx: CampaignCtx, instrument: str, split: str) -> C022Frames:
    key = (instrument, split)
    if key not in ctx._frame_cache:
        frm, to = SPLITS[split]
        ctx._frame_cache[key] = load_c022_frames(
            ctx.store, instrument, from_dt=_parse(frm), to_dt=_parse(to)
        )
    return ctx._frame_cache[key]


def run_pair_split(
    ctx: CampaignCtx, *, instrument: str, split: str, regime: dict[str, object]
) -> RunRecord:
    instr = instrument_for(instrument)
    regime_name = str(regime["name"])
    frm, to = SPLITS[split]
    from_dt, to_dt = _parse(frm), _parse(to)

    # Resumable: a completed cell persists its metrics + trades path. On rerun we
    # reload it instead of recomputing, so a killed process loses at most one cell.
    cell_path = OUT_CELLS / f"{instrument}_{split}_{regime_name}.json"
    if cell_path.exists():
        cached = json.loads(cell_path.read_text(encoding="utf-8"))
        rec = RunRecord(
            split=split,
            cost_regime=regime_name,
            instrument=instrument,
            metrics=cached["metrics"],
            trades_path=cached["trades_path"],
        )
        ctx.runs.append(rec)
        tp = ROOT / cached["trades_path"]
        if tp.exists():
            tdf = pd.read_csv(tp)
            if not tdf.empty:
                ctx.all_trades.append(tdf)
        print(
            f"  [cached] {split}/{regime_name} {instrument}: "
            f"{rec.metrics['trade_count']} trades exp_r={rec.metrics['expectancy_r']:.4f}"
        )
        return rec

    frames = _frames_for(ctx, instrument, split)
    m15_frame = frames.m15
    rows = m15_frame.completed_only().df
    if rows.empty:
        raise SystemExit(f"no M15 candles: {instrument} {split}")

    strategy_cfg = dict(ctx.strategy_cfg)
    strategy_cfg["data_provenance"] = ctx.data_provenance
    strategy_cfg["context_frames"] = {"H4": frames.h4, "H1": frames.h1}

    data_hash = compute_data_request_hash(
        instrument=instrument,
        granularity="M15",
        from_time=from_dt.isoformat(),
        to_time=to_dt.isoformat(),
        source=MATERIALIZED_SOURCE,
        candle_count=len(rows),
    )
    engine = BacktestEngine(
        instrument=instr,
        strategy=H4H1PullbackResolutionEntryStrategy(version=ctx.strategy_cfg["version"]),
        strategy_config=strategy_cfg,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(regime["fixed_slippage_pips"])),
            spread_slippage_multiplier=Decimal(str(regime["spread_multiplier"])),
        ),
        starting_equity=Decimal(str(ctx.settings.backtest.starting_equity_usd)),
        account_currency=ctx.settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(ctx.settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(ctx.strategy_cfg.get("max_bars_in_trade", 32)),
        commission_per_unit=Decimal(str(ctx.settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=None,
        atr_lookback=int(ctx.strategy_cfg.get("atr_lookback", 14)),
        risk_engine=ctx.risk_engine,
        settings=ctx.settings,
        fill_timing=ctx.fill_timing,
        max_signal_window_bars=SIGNAL_WINDOW_BARS,
    )
    result = engine.run(m15_frame, data_request_hash=data_hash)
    sub = OUT_BT / split / regime_name
    label = f"c022_{instrument}_{split}_{regime_name}"
    paths = write_all(result, sub, label, split=split)
    trades_df = pd.read_csv(paths["trades_csv"]) if Path(paths["trades_csv"]).exists() else pd.DataFrame()
    if not trades_df.empty:
        ctx.all_trades.append(trades_df)
    rec = RunRecord(
        split=split,
        cost_regime=regime_name,
        instrument=instrument,
        metrics=_metrics_to_dict(result.metrics),
        trades_path=str(paths["trades_csv"].relative_to(ROOT)),
    )
    ctx.runs.append(rec)
    OUT_CELLS.mkdir(parents=True, exist_ok=True)
    cell_path.write_text(
        json.dumps({"metrics": rec.metrics, "trades_path": rec.trades_path}, indent=2),
        encoding="utf-8",
    )
    print(
        f"  {split}/{regime_name} {instrument}: "
        f"{rec.metrics['trade_count']} trades exp_r={rec.metrics['expectancy_r']:.4f}"
    )
    return rec


def aggregate(runs: list[RunRecord], split: str, cost: str = "base") -> dict[str, Any]:
    subset = [r for r in runs if r.split == split and r.cost_regime == cost]
    if not subset:
        return {"trade_count": 0, "expectancy_r": None, "profit_factor": None, "pairs_positive": 0}
    total = sum(r.metrics["trade_count"] for r in subset)
    wexp = (
        sum(r.metrics["expectancy_r"] * r.metrics["trade_count"] for r in subset) / total
        if total
        else 0.0
    )
    pfs = [r.metrics["profit_factor"] for r in subset if r.metrics["profit_factor"] is not None]
    pairs_pos = sum(1 for r in subset if r.metrics["trade_count"] > 0 and (r.metrics.get("expectancy_r") or 0) > 0)
    return {
        "trade_count": total,
        "expectancy_r": round(wexp, 4) if total else None,
        "profit_factor": round(statistics.mean(pfs), 4) if pfs else None,
        "pairs_positive": pairs_pos,
        "pairs_total": len(subset),
        "per_pair": {r.instrument: r.metrics for r in subset},
    }


def hold_diagnostics(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty or "entry_time" not in trades.columns or "exit_time" not in trades.columns:
        return {"total_trades": len(trades), "avg_hold_calendar_days": 0.0}
    entry = pd.to_datetime(trades["entry_time"], utc=True)
    exit_ = pd.to_datetime(trades["exit_time"], utc=True)
    days = (exit_ - entry).dt.total_seconds() / 86400.0
    out = {
        "total_trades": len(trades),
        "avg_hold_calendar_days": round(float(days.mean()), 3),
        "median_hold_calendar_days": round(float(days.median()), 3),
        "pct_holds_gt_1_day": round(float((days > 1.0).mean() * 100), 2),
    }
    if "exit_reason" in trades.columns:
        out["exit_reason_counts"] = {
            str(k): int(v) for k, v in trades["exit_reason"].value_counts().items()
        }
    if "bars_held" in trades.columns:
        bh = pd.to_numeric(trades["bars_held"], errors="coerce").dropna()
        if len(bh):
            out["avg_bars_held"] = round(float(bh.mean()), 2)
            out["median_bars_held"] = round(float(bh.median()), 2)
    return out


def evaluate_gates(agg: dict[str, Any], *, parity_pass: bool = False) -> dict[str, Any]:
    train = agg.get("train", {})
    val = agg.get("validation", {})
    val2x = agg.get("validation_stress_2x", {})
    train_exp = train.get("expectancy_r")
    val_exp = val.get("expectancy_r")
    beat_null_threshold = C011_NULL_EXP_R + BEAT_NULL_MARGIN
    checks = {
        "train_expectancy_gte_zero": bool((train_exp if train_exp is not None else -999) >= 0),
        "validation_expectancy_gt_zero": bool((val_exp if val_exp is not None else -999) > 0),
        "validation_pf_gte_1_05": bool((val.get("profit_factor") or 0) >= 1.05),
        "validation_trade_count_gte_min": bool(val.get("trade_count", 0) >= MIN_VALIDATION_TRADES),
        "validation_pairs_positive_gte_min": bool(
            val.get("pairs_positive", 0) >= MIN_VALIDATION_PAIRS_POSITIVE
        ),
        "validation_stress_2x_expectancy_gte_zero": bool(
            (val2x.get("expectancy_r") if val2x.get("expectancy_r") is not None else -999) >= 0
        ),
        "beat_null_vs_c011": bool((val_exp if val_exp is not None else -999) > beat_null_threshold),
        "backtrader_parity_pass": bool(parity_pass),
    }
    train_pass = checks["train_expectancy_gte_zero"]
    screening_pass = train_pass and all(checks.values())
    failed = [k for k, v in checks.items() if not v]
    verdict = "SCREENING_PASS" if screening_pass else "REJECT"
    return {
        "screening_pass": screening_pass,
        "train_gate_pass": train_pass,
        "checks": checks,
        "failed_gates": failed,
        "beat_null_threshold": beat_null_threshold,
        "min_validation_trades": MIN_VALIDATION_TRADES,
        "min_validation_pairs_positive": MIN_VALIDATION_PAIRS_POSITIVE,
        "test_window_opened": False,
        "verdict": verdict,
        "fill_timing": "next_bar_open",
    }


def load_c011_null() -> dict[str, Any]:
    if C011_NULL.exists():
        return json.loads(C011_NULL.read_text(encoding="utf-8"))
    return {"aggregate_expectancy_r": C011_NULL_EXP_R}


def run_train_validation(ctx: CampaignCtx) -> dict[str, Any]:
    pairs = ctx.settings.market.instruments
    for split in ("train", "validation"):
        for pair in pairs:
            run_pair_split(ctx, instrument=pair, split=split, regime=COST_BASE)
    for pair in pairs:
        run_pair_split(ctx, instrument=pair, split="validation", regime=COST_STRESS_2X)
    agg = {
        "train": aggregate(ctx.runs, "train", "base"),
        "validation": aggregate(ctx.runs, "validation", "base"),
        "validation_stress_2x": aggregate(ctx.runs, "validation", "stress_2x"),
    }
    all_trades = pd.concat(ctx.all_trades, ignore_index=True) if ctx.all_trades else pd.DataFrame()
    holds = hold_diagnostics(all_trades)
    gates = evaluate_gates(agg, parity_pass=False)  # parity runs in a later phase
    return {"aggregate": agg, "hold_diagnostics": holds, "gates": gates}


def run_test(ctx: CampaignCtx) -> dict[str, Any]:
    for pair in ctx.settings.market.instruments:
        run_pair_split(ctx, instrument=pair, split="test", regime=COST_BASE)
    return {"test": aggregate(ctx.runs, "test", "base")}


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
    agg = payload.get("aggregate", {})
    files = {
        "run_manifest.json": payload.get("manifest", {}),
        "train_metrics.json": agg.get("train", {}),
        "validation_metrics.json": agg.get("validation", {}),
        "cost_stress_2x.json": agg.get("validation_stress_2x", {}),
        "gate_result.json": payload.get("gates", {}),
        "hold_diagnostics.json": payload.get("hold_diagnostics", {}),
        "comparison_to_c011_null.json": payload.get("comparison", {}),
        "metrics_summary.json": payload.get("metrics_summary", agg),
        "evidence_status.json": payload.get("evidence_status", {}),
    }
    for name, obj in files.items():
        (OUT_RESEARCH / name).write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")


def preflight(ctx: CampaignCtx) -> dict[str, Any]:
    from forex_bot.strategies.h4_h1_pullback_resolution_entry import aligned_h4_bias
    pairs = ctx.settings.market.instruments
    by_pair: dict[str, Any] = {}
    blocked: list[str] = []
    for pair in pairs:
        frm, to = SPLITS["train"]
        frames = load_c022_frames(ctx.store, pair, from_dt=_parse(frm), to_dt=_parse(to))
        m15 = frames.m15.completed_only().df
        h1 = frames.h1.completed_only().df
        h4 = frames.h4.completed_only().df
        # Lookahead spot-check: aligned H4 feature time must be <= decision time.
        lookahead = 0
        if len(m15) >= 10:
            step = max(1, len(m15) // 200)
            for ts in m15.index[::step]:
                dt = ts.to_pydatetime()
                _b, ft, _r = aligned_h4_bias(
                    frames.h4, dt, ema_fast_len=20, ema_slow_len=50,
                    slope_bars=3, adx_len=14, adx_min=20.0,
                )
                if ft is not None and ft > dt:
                    lookahead += 1
        rep = {
            "instrument": pair,
            "m15_count": len(m15),
            "h1_count": len(h1),
            "h4_count": len(h4),
            "lookahead_violations": lookahead,
            "status": "PASS" if len(m15) >= 120 and len(h1) > 0 and len(h4) > 0 and lookahead == 0 else "FAIL",
        }
        by_pair[pair] = rep
        if rep["status"] != "PASS":
            blocked.append(pair)
    return {
        "campaign_id": "CAMPAIGN_022",
        "strategy_name": EXPECTED_STRATEGY,
        "version": EXPECTED_VERSION,
        "materialized_source": MATERIALIZED_SOURCE,
        "d1_layer": "absent",
        "pairs": by_pair,
        "blocked_pairs": blocked,
        "preflight_ok": not blocked,
        "not_approved": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="CAMPAIGN_022 runner")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument(
        "command", nargs="?", choices=["train-validation", "test", "full"],
    )
    args = parser.parse_args()

    if args.validate_config:
        bootstrap_environ()
        settings, raw = load_settings_from_campaign()
        validate_frozen_config(settings, raw)
        print(f"[CAMPAIGN_022] config OK — {EXPECTED_STRATEGY} {EXPECTED_VERSION}")
        return 0

    ctx = load_ctx()

    if args.preflight_only:
        pf = preflight(ctx)
        OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
        (OUT_RESEARCH / "preflight.json").write_text(json.dumps(pf, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(pf, indent=2))
        return 0 if pf["preflight_ok"] else 1

    if not args.command:
        parser.print_help()
        return 0

    t0 = time.time()
    null_baseline = load_c011_null()
    manifest = {
        "campaign_id": "CAMPAIGN_022",
        "strategy_name": EXPECTED_STRATEGY,
        "strategy_version": EXPECTED_VERSION,
        "fill_timing": "next_bar_open",
        "execution_realism": "conservative",
        "config_path": str(CONFIG_PATH.relative_to(ROOT)),
        "splits": SPLITS,
        "materialized_source": MATERIALIZED_SOURCE,
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "started_at_utc": datetime.now(UTC).isoformat(),
    }
    payload: dict[str, Any] = {"manifest": manifest}

    if args.command in ("train-validation", "full"):
        tv = run_train_validation(ctx)
        payload.update(tv)
        agg = tv["aggregate"]
        val_exp = agg.get("validation", {}).get("expectancy_r")
        payload["comparison"] = {
            "c011_null_aggregate_expectancy_r": null_baseline.get(
                "aggregate_expectancy_r", C011_NULL_EXP_R
            ),
            "c022_validation": agg.get("validation"),
            "beat_null_threshold": C011_NULL_EXP_R + BEAT_NULL_MARGIN,
            "beat_null": bool(val_exp is not None and val_exp > C011_NULL_EXP_R + BEAT_NULL_MARGIN),
            "c020_note": "C020 REJECT: train -0.035R, validation +0.053R (all-green H4)",
            "c021_note": "C021 scaffold only — no executed evidence exists",
        }
        payload["metrics_summary"] = agg
        payload["evidence_status"] = {
            "campaign_id": "CAMPAIGN_022",
            "strategy_evidence": True,
            "not_approved": True,
            "paper_demo_live_enabled": False,
            "test_window_opened": False,
        }
        write_artifacts(payload)
        gates = tv["gates"]
        print(
            f"Train gate: {gates['train_gate_pass']} | Screening: {gates['screening_pass']} "
            f"| Verdict: {gates['verdict']}"
        )
        if not gates["train_gate_pass"]:
            print("STOP: train gate failed — no validation rescue, no test lockbox")
        # Test lockbox stays CLOSED in this runner: opening requires Backtrader
        # parity PASS (a later phase). `full` still does not open it here.
        if args.command == "full":
            print("Test lockbox NOT opened — parity gate not yet satisfied in this phase.")

    manifest["elapsed_seconds"] = round(time.time() - t0, 1)
    write_artifacts(payload)
    print(f"Done in {manifest['elapsed_seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
