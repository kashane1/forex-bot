#!/usr/bin/env python3
"""CAMPAIGN_020 — MTF confluence pullback evidence runner."""

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
from forex_bot.data.candle_dedupe import DEDUPE_POLICY
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo, InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.research.execution_realism import FillTiming, parse_research_metadata
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.multi_timeframe_confluence_pullback import (
    MultiTimeframeConfluencePullbackStrategy,
)

CONFIG_PATH = ROOT / "configs/campaign_020_mtf_confluence_pullback.yaml"
OUT_BT = ROOT / "backtests/CAMPAIGN_020_mtf_confluence_pullback"
OUT_RESEARCH = ROOT / "research/campaign_020"
C011_NULL = ROOT / "research/null_baselines/campaign_011_deduped_null_baseline.json"
EXPECTED_STRATEGY = "multi_timeframe_confluence_pullback"

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2020-01-01", "2022-12-31"),
    "validation": ("2023-01-01", "2024-12-31"),
    "test": ("2025-01-01", "2026-05-20"),
}

COST_BASE = {"name": "base", "spread_multiplier": 0.5, "fixed_slippage_pips": 0.2}
COST_STRESS_2X = {"name": "stress_2x", "spread_multiplier": 2.0, "fixed_slippage_pips": 0.5}

C011_NULL_EXP_R = -0.0029154071495408797
BEAT_NULL_MARGIN = 0.010
REQUIRED_DATA_SOURCE = "oanda-practice"
MIN_VALIDATION_TRADES = 80
MIN_VALIDATION_PAIRS_POSITIVE = 2


def _parse(d: str) -> datetime:
    return datetime.fromisoformat(d).replace(tzinfo=UTC)


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


def _load_campaign_yaml() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def _strip_for_settings(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)
    for key in ("campaign", "research_metadata", "financing"):
        data.pop(key, None)
    text = CONFIG_PATH.read_text(encoding="utf-8")
    data.setdefault("config_hash", compute_config_hash(text))
    data.setdefault("config_source_path", str(CONFIG_PATH))
    return data


def load_settings_from_campaign() -> tuple[Settings, dict[str, Any]]:
    raw = _load_campaign_yaml()
    return Settings.model_validate(_strip_for_settings(raw)), raw


def validate_frozen_config(settings: Settings) -> dict[str, Any]:
    sc = settings.strategy
    if sc.enabled != [EXPECTED_STRATEGY]:
        raise SystemExit(f"config must enable only {EXPECTED_STRATEGY}")
    if sc.multi_timeframe_confluence_pullback is None:
        raise SystemExit("missing multi_timeframe_confluence_pullback config")
    c020 = sc.multi_timeframe_confluence_pullback
    if c020.version != "0.1.0-c020":
        raise SystemExit("version must be 0.1.0-c020")
    if c020.d1_ema_slow != 50 or c020.h4_ema_context != 50:
        raise SystemExit("precommitted EMA parameters diverged")
    return c020.model_dump()


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
    db: Database
    instr: InstrumentRepo
    candles: CandleRepo
    ds: DataSourceRepo
    risk_engine: RiskEngine
    strategy_cfg: dict[str, Any]
    granularity: str
    fill_timing: str
    runs: list[RunRecord] = field(default_factory=list)
    all_trades: list[pd.DataFrame] = field(default_factory=list)


def load_ctx() -> CampaignCtx:
    settings, raw = load_settings_from_campaign()
    strategy_cfg = validate_frozen_config(settings)
    meta = parse_research_metadata(raw.get("research_metadata"))
    if meta is None or meta.fill_timing != FillTiming.NEXT_BAR_OPEN:
        raise SystemExit("CAMPAIGN_020 requires research_metadata.fill_timing=next_bar_open")
    db = Database(settings.app.database_path)
    return CampaignCtx(
        settings=settings,
        db=db,
        instr=InstrumentRepo(db),
        candles=CandleRepo(db),
        ds=DataSourceRepo(db),
        risk_engine=RiskEngine(settings, mode="backtest"),
        strategy_cfg=strategy_cfg,
        granularity=settings.market.granularity,
        fill_timing="next_bar_open",
    )


def run_pair_split(
    ctx: CampaignCtx,
    *,
    instrument: str,
    split: str,
    regime: dict[str, object],
) -> RunRecord:
    meta = ctx.instr.get(instrument)
    if meta is None:
        raise SystemExit(f"missing instrument: {instrument}")
    frm, to = SPLITS[split]
    from_dt, to_dt = _parse(frm), _parse(to)
    rows, _dedupe_stats = ctx.candles.list_with_dedupe_stats(
        instrument,
        ctx.granularity,
        completed_only=True,
        from_time=from_dt,
        to_time=to_dt,
    )
    if not rows:
        raise SystemExit(f"no candles: {instrument} {split}")
    frame = CandleFrame.from_candles(instrument, ctx.granularity, rows)
    source = (ctx.ds.latest_for(instrument, ctx.granularity) or {}).get("source", "unknown")
    if source != REQUIRED_DATA_SOURCE:
        raise SystemExit(f"bad source {source} for {instrument}")
    data_hash = compute_data_request_hash(
        instrument=instrument,
        granularity=ctx.granularity,
        from_time=from_dt.isoformat(),
        to_time=to_dt.isoformat(),
        source=source,
        candle_count=len(rows),
    )
    engine = BacktestEngine(
        instrument=meta,
        strategy=MultiTimeframeConfluencePullbackStrategy(version=ctx.strategy_cfg["version"]),
        strategy_config=ctx.strategy_cfg,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(regime["fixed_slippage_pips"])),
            spread_slippage_multiplier=Decimal(str(regime["spread_multiplier"])),
        ),
        starting_equity=Decimal(str(ctx.settings.backtest.starting_equity_usd)),
        account_currency=ctx.settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(ctx.settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(ctx.strategy_cfg.get("max_bars_in_trade", 24)),
        commission_per_unit=Decimal(str(ctx.settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=ctx.strategy_cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(ctx.strategy_cfg.get("atr_lookback", 14)),
        risk_engine=ctx.risk_engine,
        settings=ctx.settings,
        fill_timing=ctx.fill_timing,
    )
    result = engine.run(frame, data_request_hash=data_hash)
    regime_name = str(regime["name"])
    sub = OUT_BT / split / regime_name
    label = f"c020_{instrument}_{split}_{regime_name}"
    paths = write_all(result, sub, label, split=split)
    trades_df = pd.read_csv(paths["trades_csv"])
    ctx.all_trades.append(trades_df)
    rec = RunRecord(
        split=split,
        cost_regime=regime_name,
        instrument=instrument,
        metrics=_metrics_to_dict(result.metrics),
        trades_path=str(paths["trades_csv"].relative_to(ROOT)),
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
    if trades.empty or "entry_time" not in trades.columns or "exit_time" not in trades.columns:
        return {"total_trades": 0, "avg_hold_calendar_days": 0.0}
    entry = pd.to_datetime(trades["entry_time"], utc=True)
    exit_ = pd.to_datetime(trades["exit_time"], utc=True)
    days = (exit_ - entry).dt.total_seconds() / 86400.0
    return {
        "total_trades": len(trades),
        "avg_hold_calendar_days": round(float(days.mean()), 3),
        "median_hold_calendar_days": round(float(days.median()), 3),
        "pct_holds_gt_1_day": round(float((days > 1.0).mean() * 100), 2),
    }


def financing_overlay_sensitivity(
    trades: pd.DataFrame, runs: list[RunRecord]
) -> dict[str, Any]:
    if trades.empty:
        return {"applied": False, "reason": "no_trades"}
    holds = hold_diagnostics(trades)
    if holds.get("avg_hold_calendar_days", 0) <= 1.0:
        return {
            "applied": False,
            "reason": "avg_hold_calendar_days <= 1",
            "hold_diagnostics": holds,
        }
    try:
        from research.financing.overlay import apply_financing_overlay, load_trades_from_csv
        from research.financing.rates import default_stress_rate_source

        ledger: list = []
        for rec in runs:
            if rec.cost_regime != "base":
                continue
            ledger.extend(load_trades_from_csv(ROOT / rec.trades_path))
        if not ledger:
            return {"applied": False, "reason": "no_trade_csvs", "hold_diagnostics": holds}
        result = apply_financing_overlay(ledger, rate_source=default_stress_rate_source())
        agg = result.get("aggregate", {})
        return {
            "applied": True,
            "diagnostic_label": result.get("diagnostic_label"),
            "hold_diagnostics": holds,
            "gross_expectancy_r": agg.get("gross_expectancy_r"),
            "net_expectancy_r": agg.get("net_expectancy_r"),
            "financing_drag_r": agg.get("financing_drag_r"),
            "note": "SYNTHETIC stress overlay only — not observed financing",
        }
    except Exception as exc:
        return {"applied": False, "reason": str(exc), "hold_diagnostics": holds}


def evaluate_gates(agg: dict[str, Any]) -> dict[str, Any]:
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
        "validation_trade_count_gte_80": bool(val.get("trade_count", 0) >= MIN_VALIDATION_TRADES),
        "validation_pairs_positive_gte_2": bool(
            val.get("pairs_positive", 0) >= MIN_VALIDATION_PAIRS_POSITIVE
        ),
        "validation_stress_2x_expectancy_gte_zero": bool(
            (val2x.get("expectancy_r") if val2x.get("expectancy_r") is not None else -999) >= 0
        ),
        "beat_null_vs_c011": bool(
            (val_exp if val_exp is not None else -999) > beat_null_threshold
        ),
        "backtrader_parity_pass": False,
    }
    train_pass = checks["train_expectancy_gte_zero"]
    screening_pass = train_pass and all(
        checks[k] for k in checks if k not in ("backtrader_parity_pass",)
    )
    failed = [k for k, v in checks.items() if not v]
    within_null = bool(
        val_exp is not None and abs(float(val_exp) - C011_NULL_EXP_R) < 0.005
    )
    verdict = "REJECT"
    if not train_pass:
        verdict = "REJECT"
    elif screening_pass:
        verdict = "SCREENING_PASS"
    else:
        verdict = "REJECT"
    return {
        "screening_pass": screening_pass,
        "train_gate_pass": train_pass,
        "checks": checks,
        "failed_gates": failed,
        "within_null": within_null,
        "beat_null_threshold": beat_null_threshold,
        "test_window_opened": False,
        "verdict": verdict,
        "fill_timing": "next_bar_open",
    }


def evaluate_test_gates(agg: dict[str, Any]) -> dict[str, Any]:
    test = agg.get("test", {})
    checks = {
        "test_expectancy_gte_zero": bool((test.get("expectancy_r") or -999) >= 0),
        "test_pf_gte_1_0": bool((test.get("profit_factor") or 0) >= 1.0),
        "test_trade_count_gte_20": bool(test.get("trade_count", 0) >= 20),
    }
    passed = all(checks.values())
    return {
        "test_pass": passed,
        "checks": checks,
        "failed_gates": [k for k, v in checks.items() if not v],
        "verdict": "RESEARCH_PASS_PROMOTION_REVIEW_REQUIRED" if passed else "REJECT",
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
    financing = financing_overlay_sensitivity(all_trades, ctx.runs)
    gates = evaluate_gates(agg)
    gates["checks"]["backtrader_parity_pass"] = False
    if "backtrader_parity_pass" not in gates["failed_gates"]:
        gates["failed_gates"] = [*gates["failed_gates"], "backtrader_parity_pass"]
    if not gates["checks"]["backtrader_parity_pass"]:
        gates["screening_pass"] = False
        gates["verdict"] = "REJECT"
    return {
        "aggregate": agg,
        "hold_diagnostics": holds,
        "financing_overlay": financing,
        "gates": gates,
    }


def run_test(ctx: CampaignCtx) -> dict[str, Any]:
    for pair in ctx.settings.market.instruments:
        run_pair_split(ctx, instrument=pair, split="test", regime=COST_BASE)
    return {"test": aggregate(ctx.runs, "test", "base")}


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
    agg = payload.get("aggregate", {})
    (OUT_RESEARCH / "run_manifest.json").write_text(
        json.dumps(payload.get("manifest", {}), indent=2, default=str), encoding="utf-8"
    )
    (OUT_RESEARCH / "train_metrics.json").write_text(
        json.dumps(agg.get("train", {}), indent=2), encoding="utf-8"
    )
    (OUT_RESEARCH / "validation_metrics.json").write_text(
        json.dumps(agg.get("validation", {}), indent=2), encoding="utf-8"
    )
    (OUT_RESEARCH / "gate_result.json").write_text(
        json.dumps(payload.get("gates", {}), indent=2), encoding="utf-8"
    )
    (OUT_RESEARCH / "hold_diagnostics.json").write_text(
        json.dumps(payload.get("hold_diagnostics", {}), indent=2), encoding="utf-8"
    )
    (OUT_RESEARCH / "financing_overlay_sensitivity.json").write_text(
        json.dumps(payload.get("financing_overlay", {}), indent=2), encoding="utf-8"
    )
    (OUT_RESEARCH / "cost_stress_2x.json").write_text(
        json.dumps(agg.get("validation_stress_2x", {}), indent=2), encoding="utf-8"
    )
    (OUT_RESEARCH / "comparison_to_c011_null.json").write_text(
        json.dumps(payload.get("comparison", {}), indent=2, default=str), encoding="utf-8"
    )
    (OUT_RESEARCH / "metrics_summary.json").write_text(
        json.dumps(payload.get("metrics_summary", agg), indent=2, default=str),
        encoding="utf-8",
    )
    (OUT_RESEARCH / "evidence_status.json").write_text(
        json.dumps(payload.get("evidence_status", {}), indent=2), encoding="utf-8"
    )


def preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    db = Path(settings.app.database_path)
    meta = parse_research_metadata(raw.get("research_metadata"))
    strategy = MultiTimeframeConfluencePullbackStrategy()
    result: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_020",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c020",
        "not_approved": True,
        "strategy_evidence": False,
        "test_lockbox_opened": False,
        "database_path": str(db),
        "database_exists": db.is_file(),
        "fill_timing": meta.fill_timing.value if meta and meta.fill_timing else None,
        "warmup_bars_required": strategy.warmup_bars_required(),
        "pairs": list(settings.market.instruments),
        "blocked_reasons": [],
    }
    if meta is None or meta.fill_timing != FillTiming.NEXT_BAR_OPEN:
        result["blocked_reasons"].append("fill_timing must be next_bar_open")
    if not db.is_file():
        result["blocked_reasons"].append(f"missing database: {db}")
    if settings.app.trading_enabled or settings.app.allow_order_submission:
        result["blocked_reasons"].append("order submission must stay disabled")
    result["preflight_ok"] = not result["blocked_reasons"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="CAMPAIGN_020 runner")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--emit-plan", action="store_true")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["train-validation", "test", "full"],
        help="Evidence execution (requires clean DB)",
    )
    args = parser.parse_args()

    settings, raw = load_settings_from_campaign()
    if args.preflight_only or args.dry_run:
        pf = preflight(settings, raw)
        OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
        (OUT_RESEARCH / "preflight.json").write_text(
            json.dumps(pf, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(pf, indent=2))
        return 0 if pf["preflight_ok"] else 1

    if args.validate_config or args.emit_plan:
        validate_frozen_config(settings)
        print(f"[CAMPAIGN_020] config OK — {EXPECTED_STRATEGY} 0.1.0-c020")
        if args.emit_plan:
            (OUT_RESEARCH / "execution_plan.json").write_text(
                json.dumps(
                    {
                        "campaign_id": "CAMPAIGN_020",
                        "fill_timing": "next_bar_open",
                        "splits": SPLITS,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        return 0

    if not args.command:
        parser.print_help()
        return 0

    t0 = time.time()
    ctx = load_ctx()
    null_baseline = load_c011_null()
    manifest = {
        "campaign_id": "CAMPAIGN_020",
        "strategy_name": EXPECTED_STRATEGY,
        "strategy_version": "0.1.0-c020",
        "fill_timing": "next_bar_open",
        "execution_realism": "conservative",
        "config_path": str(CONFIG_PATH.relative_to(ROOT)),
        "dedupe_policy": DEDUPE_POLICY,
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
            "c011_null": {
                "aggregate_expectancy_r": null_baseline.get("aggregate_expectancy_r", C011_NULL_EXP_R),
            },
            "c020_validation": agg.get("validation"),
            "beat_null_threshold": C011_NULL_EXP_R + BEAT_NULL_MARGIN,
            "beat_null": bool(
                val_exp is not None and val_exp > C011_NULL_EXP_R + BEAT_NULL_MARGIN
            ),
        }
        payload["metrics_summary"] = agg
        payload["evidence_status"] = {
            "campaign_id": "CAMPAIGN_020",
            "strategy_evidence": True,
            "not_approved": True,
            "paper_demo_live_enabled": False,
            "test_window_opened": False,
            "scaffold_only": False,
        }
        write_artifacts(payload)
        gates = tv["gates"]
        print(
            f"Train gate: {gates['train_gate_pass']} | Screening: {gates['screening_pass']} "
            f"| Verdict: {gates['verdict']}"
        )
        if not gates["train_gate_pass"]:
            print("STOP: train gate failed — no validation rescue, no test lockbox")
            manifest["elapsed_seconds"] = round(time.time() - t0, 1)
            write_artifacts(payload)
            return 0

        if args.command == "full" and gates["screening_pass"]:
            test_agg = run_test(ctx)
            payload["aggregate"]["test"] = test_agg["test"]
            test_gates = evaluate_test_gates(payload["aggregate"])
            payload["gates"]["test_window_opened"] = True
            payload["gates"]["test_gates"] = test_gates
            payload["gates"]["verdict"] = test_gates["verdict"]
            payload["evidence_status"]["test_window_opened"] = True
            write_artifacts(payload)
            print(f"Test verdict: {test_gates['verdict']}")
        elif args.command == "full":
            print("Test lockbox NOT opened — screening or parity failed")

    manifest["elapsed_seconds"] = round(time.time() - t0, 1)
    write_artifacts(payload)
    print(f"Done in {manifest['elapsed_seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
