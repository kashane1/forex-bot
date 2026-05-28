#!/usr/bin/env python3
"""CAMPAIGN_021 — LTF MTF confluence entry evidence runner (gate-disciplined)."""

from __future__ import annotations

import argparse
import csv
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
from forex_bot.data.candle_dedupe import DEDUPE_POLICY
from forex_bot.data.m1_timeframe_materialization import MATERIALIZED_SOURCE
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.campaign_021_gates import (
    C011_NULL_EXP_R,
    apply_parity_to_gates,
    evaluate_test_gates,
    evaluate_train_gates,
    evaluate_validation_gates,
)
from forex_bot.research.campaign_021_loader import (
    build_data_feature_preflight,
    check_materialized_coverage,
    instrument_for,
    live_aggregation_enabled,
    load_c021_frames,
)
from forex_bot.research.execution_realism import (
    ExecutionRealism,
    FillTiming,
    parse_research_metadata,
)
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.lower_timeframe_mtf_confluence_entry import (
    D1AGG_SOURCE_M1,
    D1AGG_SOURCE_NATIVE,
    LowerTimeframeMtfConfluenceEntryStrategy,
    validate_c021_data_provenance,
)

CONFIG_PATH = ROOT / "configs/campaign_021_ltf_mtf_confluence.yaml"
APPROVED_PATH = ROOT / "configs/approved_strategies.yaml"
OUT_BT = ROOT / "backtests/CAMPAIGN_021_ltf_mtf_confluence"
OUT_RESEARCH = ROOT / "research/campaign_021"
OUT_RAW = OUT_RESEARCH / "raw"
C011_NULL = ROOT / "research/null_baselines/campaign_011_deduped_null_baseline.json"
C020_SUMMARY = ROOT / "research/campaign_020/metrics_summary.json"
EXPECTED_STRATEGY = "lower_timeframe_mtf_confluence_entry"
GATE_STATE_PATH = OUT_RESEARCH / "gate_state.json"

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2020-01-01", "2022-12-31"),
    "validation": ("2023-01-01", "2024-12-31"),
    "test": ("2025-01-01", "2026-05-20"),
}

COST_BASE = {"name": "base", "spread_multiplier": 0.5, "fixed_slippage_pips": 0.2}
COST_STRESS_2X = {"name": "stress_2x", "spread_multiplier": 2.0, "fixed_slippage_pips": 0.5}


def _parse(d: str) -> datetime:
    return datetime.fromisoformat(d).replace(tzinfo=UTC)


def _parse_end(d: str) -> datetime:
    return datetime.fromisoformat(d).replace(hour=23, minute=59, second=59, tzinfo=UTC)


def _git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True,
            text=True,
            check=False,
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


def load_settings() -> tuple[Settings, dict[str, Any]]:
    raw = _load_raw()
    return Settings.model_validate(_strip_for_settings(raw)), raw


def assert_registry_empty() -> None:
    approved = yaml.safe_load(APPROVED_PATH.read_text(encoding="utf-8")) or {}
    if approved.get("approved"):
        raise SystemExit("approved_strategies.yaml must remain empty for CAMPAIGN_021")


def assert_execution_metadata(raw: dict[str, Any]) -> None:
    meta = parse_research_metadata(raw.get("research_metadata"))
    if meta is None:
        raise SystemExit("research_metadata required")
    if meta.fill_timing != FillTiming.NEXT_BAR_OPEN:
        raise SystemExit("fill_timing must be next_bar_open")
    if meta.fill_timing == FillTiming.SIGNAL_BAR_CLOSE:
        raise SystemExit("signal_bar_close forbidden for CAMPAIGN_021")
    if meta.execution_realism != ExecutionRealism.CONSERVATIVE:
        raise SystemExit("execution_realism must be conservative")
    provenance = raw.get("data_provenance") or {}
    validate_c021_data_provenance(provenance)
    if provenance.get("d1agg_context") == D1AGG_SOURCE_M1:
        raise SystemExit("m1_derived_d1agg forbidden")


def validate_frozen_config(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    assert_registry_empty()
    assert_execution_metadata(raw)
    if settings.strategy.enabled != [EXPECTED_STRATEGY]:
        raise SystemExit(f"config must enable only {EXPECTED_STRATEGY}")
    cfg = settings.strategy.lower_timeframe_mtf_confluence_entry
    if cfg is None:
        raise SystemExit("missing lower_timeframe_mtf_confluence_entry config")
    if cfg.version != "0.1.0-c021" or cfg.timeframe != "M15":
        raise SystemExit("frozen identity diverged")
    if cfg.max_bars_in_trade != 32 or cfg.atr_stop_multiple != 2.0:
        raise SystemExit("precommitted risk parameters diverged")
    return cfg.model_dump()


def load_gate_state() -> dict[str, Any]:
    if GATE_STATE_PATH.is_file():
        return json.loads(GATE_STATE_PATH.read_text(encoding="utf-8"))
    return {}


def save_gate_state(state: dict[str, Any]) -> None:
    OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
    GATE_STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_train_pass_for_validation() -> dict[str, Any]:
    state = load_gate_state()
    if not state.get("train_gate_pass"):
        raise SystemExit(
            "BLOCKED: validation requires train_gate_pass in gate_state.json "
            "(run train-only first)"
        )
    return state


def require_lockbox_allowed() -> dict[str, Any]:
    state = load_gate_state()
    if not state.get("test_lockbox_allowed"):
        raise SystemExit(
            "BLOCKED: test lockbox requires train+validation+parity gates "
            f"(gate_state={state})"
        )
    return state


def _metrics_to_dict(m) -> dict[str, Any]:
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
    strategy_cfg: dict[str, Any]
    provenance: dict[str, Any]
    store: PostgresCandleStore
    risk_engine: RiskEngine
    fill_timing: str
    runs: list[RunRecord] = field(default_factory=list)
    all_trades: list[pd.DataFrame] = field(default_factory=list)
    frame_cache: dict[tuple[str, str], Any] = field(default_factory=dict)


def load_ctx() -> CampaignCtx:
    if live_aggregation_enabled():
        raise SystemExit(
            "FOREX_BOT_ALLOW_LIVE_M1_AGGREGATION is set; "
            "live M1 aggregation is forbidden for CAMPAIGN_021 evidence runs"
        )
    settings, raw = load_settings()
    strategy_cfg = validate_frozen_config(settings, raw)
    provenance = raw.get("data_provenance") or {}
    environ = bootstrap_environ(None)
    db_cfg = get_research_database_config(environ=environ, require=True)
    store = PostgresCandleStore(db_cfg)
    meta = parse_research_metadata(raw["research_metadata"])
    return CampaignCtx(
        settings=settings,
        raw=raw,
        strategy_cfg=strategy_cfg,
        provenance=provenance,
        store=store,
        risk_engine=RiskEngine(settings, mode="backtest"),
        fill_timing=meta.fill_timing.value if meta and meta.fill_timing else "next_bar_open",
    )


def _split_bounds(split: str) -> tuple[datetime, datetime]:
    frm, to = SPLITS[split]
    return _parse(frm), _parse_end(to)


def _frames_for(ctx: CampaignCtx, instrument: str, split: str):
    key = (instrument, split)
    if key not in ctx.frame_cache:
        from_dt, to_dt = _split_bounds(split)
        ctx.frame_cache[key] = load_c021_frames(
            ctx.store, instrument, from_dt=from_dt, to_dt=to_dt
        )
    return ctx.frame_cache[key]


def run_pair_split(
    ctx: CampaignCtx,
    *,
    instrument: str,
    split: str,
    regime: dict[str, object],
) -> RunRecord:
    frames = _frames_for(ctx, instrument, split)
    m15_frame = frames.m15.completed_only()
    if len(m15_frame.df) < 150:
        raise SystemExit(f"insufficient M15 bars: {instrument} {split}")
    meta = instrument_for(instrument)
    from_dt, to_dt = _split_bounds(split)
    cfg = {
        **ctx.strategy_cfg,
        "data_provenance": ctx.provenance,
        "context_frames": {
            "H1": frames.h1,
            "H4": frames.h4,
            "D1AGG": frames.d1agg,
        },
    }
    data_hash = compute_data_request_hash(
        instrument=instrument,
        granularity="M15",
        from_time=from_dt.isoformat(),
        to_time=to_dt.isoformat(),
        source="postgres_m1_materialized|d1agg=native_h4",
        candle_count=len(m15_frame.df),
    )
    engine = BacktestEngine(
        instrument=meta,
        strategy=LowerTimeframeMtfConfluenceEntryStrategy(version=cfg["version"]),
        strategy_config=cfg,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(regime["fixed_slippage_pips"])),
            spread_slippage_multiplier=Decimal(str(regime["spread_multiplier"])),
        ),
        starting_equity=Decimal(str(ctx.settings.backtest.starting_equity_usd)),
        account_currency=ctx.settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(ctx.settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(cfg.get("max_bars_in_trade", 32)),
        commission_per_unit=Decimal(str(ctx.settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=None,
        atr_lookback=int(cfg.get("atr_lookback", 14)),
        risk_engine=ctx.risk_engine,
        settings=ctx.settings,
        fill_timing=ctx.fill_timing,
    )
    result = engine.run(m15_frame, data_request_hash=data_hash)
    regime_name = str(regime["name"])
    sub = OUT_BT / split / regime_name
    label = f"c021_{instrument}_{split}_{regime_name}"
    paths = write_all(result, sub, label, split=split)
    trades_df = pd.read_csv(paths["trades_csv"])
    raw_path = OUT_RAW / split / regime_name / f"{instrument}_trades.csv"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    trades_df.to_csv(raw_path, index=False)
    ctx.all_trades.append(trades_df)
    rec = RunRecord(
        split=split,
        cost_regime=regime_name,
        instrument=instrument,
        metrics=_metrics_to_dict(result.metrics),
        trades_path=str(raw_path.relative_to(ROOT)),
    )
    ctx.runs.append(rec)
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
    pairs_pos = sum(1 for r in subset if (r.metrics.get("expectancy_r") or 0) > 0)
    return {
        "trade_count": total,
        "expectancy_r": round(wexp, 4),
        "profit_factor": round(statistics.mean(pfs), 4) if pfs else None,
        "pairs_positive": pairs_pos,
        "pairs_total": len(subset),
        "per_pair": {r.instrument: r.metrics for r in subset},
    }


def hold_diagnostics(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty or "entry_time" not in trades.columns:
        return {"total_trades": 0, "avg_hold_calendar_days": 0.0, "avg_hold_m15_bars": 0.0}
    entry = pd.to_datetime(trades["entry_time"], utc=True)
    exit_ = pd.to_datetime(trades["exit_time"], utc=True)
    days = (exit_ - entry).dt.total_seconds() / 86400.0
    bars = (exit_ - entry).dt.total_seconds() / 900.0
    return {
        "total_trades": len(trades),
        "avg_hold_calendar_days": round(float(days.mean()), 3),
        "median_hold_calendar_days": round(float(days.median()), 3),
        "avg_hold_m15_bars": round(float(bars.mean()), 2),
        "pct_holds_gt_1_day": round(float((days > 1.0).mean() * 100), 2),
    }


def financing_overlay_sensitivity(trades: pd.DataFrame, runs: list[RunRecord]) -> dict[str, Any]:
    holds = hold_diagnostics(trades)
    if holds.get("avg_hold_calendar_days", 0) <= 1.0:
        return {"applied": False, "reason": "avg_hold_calendar_days <= 1", "hold_diagnostics": holds}
    return {
        "applied": False,
        "reason": "financing_mode none — overlay deferred to dedicated lane",
        "hold_diagnostics": holds,
        "note": "precommit requires overlay when avg hold > 1 day; document in validation result",
    }


def load_c011_null() -> dict[str, Any]:
    if C011_NULL.exists():
        return json.loads(C011_NULL.read_text(encoding="utf-8"))
    return {"aggregate_expectancy_r": C011_NULL_EXP_R}


def load_c020_baseline() -> dict[str, Any]:
    if C020_SUMMARY.exists():
        return json.loads(C020_SUMMARY.read_text(encoding="utf-8"))
    return {}


def run_train(ctx: CampaignCtx) -> dict[str, Any]:
    pairs = ctx.settings.market.instruments
    for pair in pairs:
        run_pair_split(ctx, instrument=pair, split="train", regime=COST_BASE)
    train = aggregate(ctx.runs, "train", "base")
    train["provenance_ok"] = ctx.provenance.get("d1agg_context") == D1AGG_SOURCE_NATIVE
    trades = pd.concat(ctx.all_trades, ignore_index=True) if ctx.all_trades else pd.DataFrame()
    gates = evaluate_train_gates(train)
    return {
        "aggregate": {"train": train},
        "hold_diagnostics": hold_diagnostics(trades),
        "train_gates": gates,
        "trades": trades,
    }


def run_validation(ctx: CampaignCtx) -> dict[str, Any]:
    pairs = ctx.settings.market.instruments
    ctx.all_trades = []
    for pair in pairs:
        run_pair_split(ctx, instrument=pair, split="validation", regime=COST_BASE)
    for pair in pairs:
        run_pair_split(ctx, instrument=pair, split="validation", regime=COST_STRESS_2X)
    train = aggregate(ctx.runs, "train", "base")
    val = aggregate(ctx.runs, "validation", "base")
    val2x = aggregate(ctx.runs, "validation", "stress_2x")
    trades = pd.concat(ctx.all_trades, ignore_index=True) if ctx.all_trades else pd.DataFrame()
    null_baseline = load_c011_null()
    comparison = {
        "c011_null": {"aggregate_expectancy_r": null_baseline.get("aggregate_expectancy_r", C011_NULL_EXP_R)},
        "c021_validation": val,
        "c020_baseline": load_c020_baseline(),
        "beat_null_threshold": C011_NULL_EXP_R + 0.010,
        "beat_null": bool((val.get("expectancy_r") or -999) > C011_NULL_EXP_R + 0.010),
    }
    gates = evaluate_validation_gates(
        {"train": train, "validation": val, "validation_stress_2x": val2x},
        comparison=comparison,
    )
    return {
        "aggregate": {"train": train, "validation": val, "validation_stress_2x": val2x},
        "hold_diagnostics": hold_diagnostics(trades),
        "financing_overlay": financing_overlay_sensitivity(trades, ctx.runs),
        "gates": gates,
        "comparison": comparison,
    }


def run_test(ctx: CampaignCtx) -> dict[str, Any]:
    for pair in ctx.settings.market.instruments:
        run_pair_split(ctx, instrument=pair, split="test", regime=COST_BASE)
    return {"test": aggregate(ctx.runs, "test", "base")}


def run_backtrader_parity(_ctx: CampaignCtx) -> dict[str, Any]:
    return {
        "status": "NOT_RUN",
        "parity_pass": False,
        "reason": "No Backtrader adapter for lower_timeframe_mtf_confluence_entry yet",
        "campaign_id": "CAMPAIGN_021",
    }


def write_train_artifacts(payload: dict[str, Any]) -> None:
    OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
    agg = payload.get("aggregate", {})
    train = agg.get("train", {})
    (OUT_RESEARCH / "train_metrics.json").write_text(json.dumps(train, indent=2) + "\n", encoding="utf-8")
    (OUT_RESEARCH / "train_gate_result.json").write_text(
        json.dumps(payload.get("train_gates", {}), indent=2) + "\n", encoding="utf-8"
    )
    (OUT_RESEARCH / "train_runtime_manifest.json").write_text(
        json.dumps(payload.get("manifest", {}), indent=2, default=str) + "\n", encoding="utf-8"
    )
    (OUT_RESEARCH / "train_provenance_manifest.json").write_text(
        json.dumps(
            {
                "data_provenance": payload.get("provenance"),
                "d1agg_source": D1AGG_SOURCE_NATIVE,
                "fill_timing": "next_bar_open",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    per_pair = train.get("per_pair", {})
    if per_pair:
        path = OUT_RESEARCH / "train_pair_metrics.csv"
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=["instrument", "trade_count", "expectancy_r", "profit_factor", "win_rate"],
            )
            writer.writeheader()
            for inst, m in per_pair.items():
                writer.writerow(
                    {
                        "instrument": inst,
                        "trade_count": m.get("trade_count"),
                        "expectancy_r": m.get("expectancy_r"),
                        "profit_factor": m.get("profit_factor"),
                        "win_rate": m.get("win_rate"),
                    }
                )
    trades = payload.get("trades")
    if isinstance(trades, pd.DataFrame) and not trades.empty:
        summary = {
            "trade_count": len(trades),
            "by_exit_reason": trades["exit_reason"].value_counts().to_dict()
            if "exit_reason" in trades.columns
            else {},
        }
        (OUT_RESEARCH / "train_trades_summary.json").write_text(
            json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8"
        )


def write_validation_artifacts(payload: dict[str, Any]) -> None:
    agg = payload.get("aggregate", {})
    for name in ("validation", "validation_stress_2x"):
        if name in agg:
            (OUT_RESEARCH / f"{name}_metrics.json").write_text(
                json.dumps(agg[name], indent=2) + "\n", encoding="utf-8"
            )
    (OUT_RESEARCH / "gate_result.json").write_text(
        json.dumps(payload.get("gates", {}), indent=2) + "\n", encoding="utf-8"
    )
    (OUT_RESEARCH / "cost_stress_2x.json").write_text(
        json.dumps(agg.get("validation_stress_2x", {}), indent=2) + "\n", encoding="utf-8"
    )
    (OUT_RESEARCH / "comparison_to_c011_null.json").write_text(
        json.dumps(payload.get("comparison", {}), indent=2, default=str) + "\n", encoding="utf-8"
    )
    (OUT_RESEARCH / "comparison_to_c020.json").write_text(
        json.dumps({"c020_metrics_summary": load_c020_baseline()}, indent=2) + "\n", encoding="utf-8"
    )
    val = agg.get("validation", {})
    per_pair = val.get("per_pair", {})
    if per_pair:
        with (OUT_RESEARCH / "validation_pair_metrics.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=["instrument", "trade_count", "expectancy_r", "profit_factor"],
            )
            writer.writeheader()
            for inst, m in per_pair.items():
                writer.writerow(
                    {
                        "instrument": inst,
                        "trade_count": m.get("trade_count"),
                        "expectancy_r": m.get("expectancy_r"),
                        "profit_factor": m.get("profit_factor"),
                    }
                )


def preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    from forex_bot.data.m1_corpus_validation import inventory_sql

    strategy = LowerTimeframeMtfConfluenceEntryStrategy()
    blocked: list[str] = []
    result: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_021",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c021",
        "not_approved": True,
        "strategy_evidence": False,
        "fill_timing": "next_bar_open",
        "data_provenance": raw.get("data_provenance"),
        "warmup_bars_required": strategy.warmup_bars_required(),
        "pairs": list(settings.market.instruments),
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "blocked_reasons": blocked,
    }
    try:
        assert_execution_metadata(raw)
        assert_registry_empty()
    except SystemExit as exc:
        blocked.append(str(exc))
    try:
        environ = bootstrap_environ(None)
        cfg = get_research_database_config(environ=environ, require=True)
        store = PostgresCandleStore(cfg)
        inv = inventory_sql(store)
        result["m1_corpus"] = inv
        if inv.get("missing_pairs"):
            blocked.append(f"missing M1 pairs: {inv['missing_pairs']}")
        with store.connection() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT COUNT(*) FROM {cfg.schema}.candles
                WHERE granularity = 'H4'
                """
            )
            h4_total = int(cur.fetchone()[0])
            cur.execute(
                f"""
                SELECT COUNT(DISTINCT instrument) FROM {cfg.schema}.candles
                WHERE granularity = 'D1AGG'
                """
            )
            d1agg_pairs = int(cur.fetchone()[0])
        result["native_h4_rows"] = h4_total
        result["d1agg_pairs_in_store"] = d1agg_pairs
        if h4_total < 1000:
            blocked.append("insufficient native H4 rows for D1AGG derivation")
        materialized: dict[str, Any] = {"source": MATERIALIZED_SOURCE, "pairs": {}}
        train_from, train_to = SPLITS["train"]
        from_dt = datetime.fromisoformat(train_from).replace(tzinfo=UTC)
        to_dt = datetime.fromisoformat(train_to).replace(hour=23, minute=59, tzinfo=UTC)
        missing_materialized: list[str] = []
        for pair in settings.market.instruments:
            cov = check_materialized_coverage(
                store, pair, from_dt=from_dt, to_dt=to_dt
            )
            materialized["pairs"][pair] = cov
            if cov["status"] != "PASS":
                missing_materialized.append(pair)
        result["materialized_coverage"] = materialized
        if missing_materialized:
            blocked.append(
                "missing materialized M5/M15/H1/H4 for: "
                + ", ".join(missing_materialized)
                + " — run scripts/materialize_m1_derived_timeframes.py --all-majors"
            )
        if live_aggregation_enabled():
            blocked.append(
                "FOREX_BOT_ALLOW_LIVE_M1_AGGREGATION must not be set for CAMPAIGN_021"
            )
    except Exception as exc:
        blocked.append(f"postgres: {exc}")
    result["blocked_reasons"] = blocked
    result["preflight_ok"] = not blocked
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="CAMPAIGN_021 runner")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--data-feature-preflight", action="store_true")
    parser.add_argument("--emit-plan", action="store_true")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["train-only", "train-validation", "validation", "test", "full"],
    )
    args = parser.parse_args()
    settings, raw = load_settings()

    if args.preflight_only:
        pf = preflight(settings, raw)
        (OUT_RESEARCH / "preflight_result.json").write_text(
            json.dumps(pf, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(pf, indent=2, sort_keys=True))
        return 0 if pf["preflight_ok"] else 1

    if args.data_feature_preflight:
        assert_execution_metadata(raw)
        environ = bootstrap_environ(None)
        store = PostgresCandleStore(get_research_database_config(environ=environ, require=True))
        report = build_data_feature_preflight(
            store, splits=SPLITS, pairs=list(settings.market.instruments)
        )
        (OUT_RESEARCH / "data_feature_preflight.json").write_text(
            json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, indent=2))
        return 0 if report["preflight_ok"] else 1

    if args.validate_config or args.emit_plan:
        validate_frozen_config(settings, raw)
        print(f"[CAMPAIGN_021] config OK — {EXPECTED_STRATEGY} 0.1.0-c021")
        return 0

    if not args.command:
        parser.print_help()
        return 0

    assert_registry_empty()
    t0 = time.time()
    ctx = load_ctx()
    manifest = {
        "campaign_id": "CAMPAIGN_021",
        "command": args.command,
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "started_at_utc": datetime.now(UTC).isoformat(),
        "splits": SPLITS,
        "dedupe_policy": DEDUPE_POLICY,
        "data_provenance": ctx.provenance,
        "d1agg_source": D1AGG_SOURCE_NATIVE,
        "fill_timing": "next_bar_open",
    }

    if args.command == "validation":
        require_train_pass_for_validation()
        val_payload = run_validation(ctx)
        val_payload["manifest"] = manifest
        write_validation_artifacts(val_payload)
        gates = val_payload["gates"]
        save_gate_state(
            {
                "train_gate_pass": gates["train_gate_pass"],
                "validation_gate_pass": gates["validation_gate_pass"],
                "validation_allowed": True,
                "test_lockbox_allowed": False,
                "verdict": gates["verdict"],
            }
        )
        print(f"Validation verdict: {gates['verdict']}")
        return 0

    if args.command == "test":
        require_lockbox_allowed()
        test_payload = run_test(ctx)
        (OUT_RESEARCH / "test_metrics.json").write_text(
            json.dumps(test_payload["test"], indent=2) + "\n", encoding="utf-8"
        )
        tg = evaluate_test_gates(test_payload["test"])
        (OUT_RESEARCH / "test_gate_result.json").write_text(
            json.dumps(tg, indent=2) + "\n", encoding="utf-8"
        )
        return 0

    if args.command in ("train-only", "train-validation", "full"):
        train_payload = run_train(ctx)
        train_payload["manifest"] = manifest
        train_payload["provenance"] = ctx.provenance
        write_train_artifacts(train_payload)
        tg = train_payload["train_gates"]
        save_gate_state(
            {
                "train_gate_pass": tg["train_gate_pass"],
                "validation_allowed": tg["validation_allowed"],
                "validation_gate_pass": False,
                "parity_pass": False,
                "test_lockbox_allowed": False,
                "verdict": tg["verdict"],
            }
        )
        print(f"Train gate pass: {tg['train_gate_pass']} | verdict: {tg['verdict']}")
        if not tg["train_gate_pass"]:
            print("STOP: train failed — no validation rescue, no test lockbox")
            manifest["elapsed_seconds"] = round(time.time() - t0, 1)
            (OUT_RESEARCH / "train_runtime_manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
            return 0

        if args.command == "train-only":
            manifest["elapsed_seconds"] = round(time.time() - t0, 1)
            return 0

    if args.command in ("train-validation", "full"):
        val_payload = run_validation(ctx)
        val_payload["manifest"] = manifest
        write_validation_artifacts(val_payload)
        gates = val_payload["gates"]
        parity = run_backtrader_parity(ctx)
        (OUT_RESEARCH / "backtrader_parity_result.json").write_text(
            json.dumps(parity, indent=2) + "\n", encoding="utf-8"
        )
        gates = apply_parity_to_gates(gates, parity_pass=parity["parity_pass"])
        (OUT_RESEARCH / "gate_result.json").write_text(
            json.dumps(gates, indent=2) + "\n", encoding="utf-8"
        )
        save_gate_state(
            {
                "train_gate_pass": gates["train_gate_pass"],
                "validation_gate_pass": gates["validation_gate_pass"],
                "parity_pass": parity["parity_pass"],
                "test_lockbox_allowed": gates["test_lockbox_allowed"],
                "verdict": gates["verdict"],
            }
        )
        print(f"Screening: {gates['screening_pass']} | parity: {parity['parity_pass']}")
        if not gates["validation_gate_pass"]:
            print("STOP: validation failed — no test lockbox")
            return 0
        if not parity["parity_pass"]:
            print("STOP: Backtrader parity not pass — no test lockbox")
            return 0

        if args.command == "full":
            test_payload = run_test(ctx)
            (OUT_RESEARCH / "test_metrics.json").write_text(
                json.dumps(test_payload["test"], indent=2) + "\n", encoding="utf-8"
            )
            print("Test lockbox opened and executed once")

    manifest["elapsed_seconds"] = round(time.time() - t0, 1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
