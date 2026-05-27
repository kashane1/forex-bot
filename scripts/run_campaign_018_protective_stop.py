#!/usr/bin/env python3
"""CAMPAIGN_018 — mean_reversion_protective_stop execution runner.

Precommitted research run only. not_approved: true.
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

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.exporters import write_all
from forex_bot.backtesting.fills import FillModel
from forex_bot.config import load_settings
from forex_bot.data.candle_dedupe import DEDUPE_POLICY
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo, InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.mean_reversion_protective_stop import (
    MeanReversionProtectiveStopStrategy,
    c008_entry_params,
)

CONFIG_PATH = ROOT / "configs/campaign_018_mean_reversion_protective_stop.yaml"
C008_CONFIG = ROOT / "configs/campaign_008_range_mean_reversion.yaml"
OUT_BT = ROOT / "backtests/CAMPAIGN_018_mean_reversion_protective_stop"
OUT_RESEARCH = ROOT / "research/campaign_018"
DEDUPED_C008 = ROOT / "research/deduped_c008_c009_rerun/metrics_summary.json"
DEDUPED_C009 = ROOT / "research/deduped_c008_c009_rerun/metrics_summary.json"
C011_NULL = ROOT / "research/null_baselines/campaign_011_deduped_null_baseline.json"

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2020-01-01", "2022-12-31"),
    "validation": ("2023-01-01", "2024-12-31"),
    "test": ("2025-01-01", "2026-05-20"),
    "full": ("2020-01-01", "2026-05-20"),
}

COST_BASE = {"name": "base", "spread_multiplier": 0.5, "fixed_slippage_pips": 0.2}
COST_STRESS_2X = {"name": "stress_2x", "spread_multiplier": 2.0, "fixed_slippage_pips": 0.5}
COST_STRESS_15X = {"name": "stress_15x", "spread_multiplier": 1.5, "fixed_slippage_pips": 0.3}

C011_NULL_EXP_R = -0.0029
BEAT_NULL_MARGIN = 0.010
REQUIRED_DATA_SOURCE = "oanda-practice"


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


def validate_frozen_config(settings) -> float:
    sc = settings.strategy
    if sc.enabled != ["mean_reversion_protective_stop"]:
        raise SystemExit("CAMPAIGN_018 config must enable only mean_reversion_protective_stop")
    if sc.mean_reversion_protective_stop is None:
        raise SystemExit("missing mean_reversion_protective_stop config")
    c018 = sc.mean_reversion_protective_stop.model_dump()
    c008 = load_settings(C008_CONFIG).strategy.mean_reversion.model_dump()
    if c008_entry_params(c018) != c008_entry_params(c008):
        raise SystemExit("C018 entry params diverge from C008 frozen config")
    ps = c018["protective_stop"]
    if ps["favorable_excursion_r_threshold"] != 1.0 or ps["ratchet"] is not False:
        raise SystemExit("protective_stop params not precommitted")
    return float(ps["favorable_excursion_r_threshold"])


@dataclass
class RunRecord:
    split: str
    cost_regime: str
    instrument: str
    metrics: dict[str, Any]
    trades_path: str


@dataclass
class CampaignCtx:
    settings: Any
    db: Database
    instr: InstrumentRepo
    candles: CandleRepo
    ds: DataSourceRepo
    risk_engine: RiskEngine
    strategy_cfg: dict[str, Any]
    protective_stop_after_r: float
    granularity: str
    runs: list[RunRecord] = field(default_factory=list)
    all_trades: list[pd.DataFrame] = field(default_factory=list)


def load_ctx() -> CampaignCtx:
    settings = load_settings(CONFIG_PATH)
    threshold = validate_frozen_config(settings)
    raw = settings.strategy.mean_reversion_protective_stop.model_dump()
    strategy_cfg = {k: v for k, v in raw.items() if k != "protective_stop"}
    db = Database(settings.app.database_path)
    return CampaignCtx(
        settings=settings,
        db=db,
        instr=InstrumentRepo(db),
        candles=CandleRepo(db),
        ds=DataSourceRepo(db),
        risk_engine=RiskEngine(settings, mode="backtest"),
        strategy_cfg=strategy_cfg,
        protective_stop_after_r=threshold,
        granularity=settings.market.granularity,
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
    rows, dedupe_stats = ctx.candles.list_with_dedupe_stats(
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
        strategy=MeanReversionProtectiveStopStrategy(version=ctx.strategy_cfg["version"]),
        strategy_config=ctx.strategy_cfg,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(regime["fixed_slippage_pips"])),
            spread_slippage_multiplier=Decimal(str(regime["spread_multiplier"])),
        ),
        starting_equity=Decimal(str(ctx.settings.backtest.starting_equity_usd)),
        account_currency=ctx.settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(ctx.settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(ctx.strategy_cfg.get("max_bars_in_trade", 40)),
        commission_per_unit=Decimal(str(ctx.settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=ctx.strategy_cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(ctx.strategy_cfg.get("atr_lookback", 14)),
        risk_engine=ctx.risk_engine,
        settings=ctx.settings,
        protective_stop_after_r=ctx.protective_stop_after_r,
    )
    result = engine.run(frame, data_request_hash=data_hash)
    regime_name = str(regime["name"])
    sub = OUT_BT / split / regime_name
    label = f"c018_{instrument}_{split}_{regime_name}"
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
    pairs_pos = sum(1 for r in subset if r.metrics["total_return_pct"] > 0)
    return {
        "trade_count": total,
        "expectancy_r": round(wexp, 4),
        "profit_factor": round(statistics.mean(pfs), 4) if pfs else None,
        "pairs_positive": pairs_pos,
        "pairs_total": len(subset),
        "per_pair": {r.instrument: r.metrics for r in subset},
    }


def mechanism_diagnostics(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty:
        return {"total_trades": 0}
    armed = trades["protective_stop_armed"].astype(bool) if "protective_stop_armed" in trades else pd.Series([False] * len(trades))
    prot_exit = trades["protective_stop_exit"].astype(bool) if "protective_stop_exit" in trades else pd.Series([False] * len(trades))
    target_exits = (trades["exit_reason"] == "target").sum() if "exit_reason" in trades else 0
    by_reason = trades.groupby("exit_reason").size().to_dict() if "exit_reason" in trades else {}
    return {
        "total_trades": len(trades),
        "protective_stop_armed_count": int(armed.sum()),
        "protective_stop_armed_rate_pct": round(100.0 * armed.sum() / len(trades), 2),
        "protective_stop_exit_count": int(prot_exit.sum()),
        "protective_stop_exit_rate_pct": round(100.0 * prot_exit.sum() / len(trades), 2),
        "target_exit_count": int(target_exits),
        "exit_reason_counts": {str(k): int(v) for k, v in by_reason.items()},
        "median_r": round(float(trades["r_multiple"].median()), 4) if "r_multiple" in trades else None,
    }


def evaluate_gates(agg: dict[str, Any], mech: dict[str, Any]) -> dict[str, Any]:
    train = agg.get("train", {})
    val = agg.get("validation", {})
    val2x = agg.get("validation_stress_2x", {})
    full15 = agg.get("full_stress_15x", {})
    val_exp = val.get("expectancy_r") or -999.0
    beat_null_threshold = C011_NULL_EXP_R + BEAT_NULL_MARGIN
    checks = {
        "train_expectancy_gte_zero": (train.get("expectancy_r") or -999) >= 0,
        "validation_expectancy_gt_zero": val_exp > 0,
        "validation_pf_gte_1_05": (val.get("profit_factor") or 0) >= 1.05,
        "validation_pairs_positive_gte_2": val.get("pairs_positive", 0) >= 2,
        "validation_trade_count_gte_30": val.get("trade_count", 0) >= 30,
        "validation_stress_2x_expectancy_gte_zero": (val2x.get("expectancy_r") or -999) >= 0,
        "beat_null_vs_c011": val_exp > beat_null_threshold,
        "protective_mechanism_active": mech.get("protective_stop_armed_rate_pct", 0) >= 10.0,
        "zero_target_exits": mech.get("target_exit_count", 0) == 0,
        "full_stress_15x_expectancy_gte_zero": (full15.get("expectancy_r") or -999) >= 0,
    }
    passed = all(checks.values())
    failed = [k for k, v in checks.items() if not v]
    within_null = abs(val_exp - C011_NULL_EXP_R) < 0.005
    return {
        "screening_pass": passed,
        "checks": checks,
        "failed_gates": failed,
        "within_null": within_null,
        "beat_null_threshold": beat_null_threshold,
        "test_window_opened": False,
        "verdict": "REJECT" if not passed else "SCREENING_PASS",
    }


def evaluate_test_gates(agg: dict[str, Any]) -> dict[str, Any]:
    test = agg.get("test", {})
    checks = {
        "test_expectancy_gte_zero": (test.get("expectancy_r") or -999) >= 0,
        "test_pf_gte_1_0": (test.get("profit_factor") or 0) >= 1.0,
        "test_trade_count_gte_20": test.get("trade_count", 0) >= 20,
    }
    passed = all(checks.values())
    train = agg.get("train", {})
    val = agg.get("validation", {})
    combined_exp = None
    total = (train.get("trade_count") or 0) + (val.get("trade_count") or 0) + (test.get("trade_count") or 0)
    if total:
        combined_exp = (
            (train.get("expectancy_r") or 0) * (train.get("trade_count") or 0)
            + (val.get("expectancy_r") or 0) * (val.get("trade_count") or 0)
            + (test.get("expectancy_r") or 0) * (test.get("trade_count") or 0)
        ) / total
    checks["combined_train_val_test_exp_gte_zero"] = (combined_exp or -999) >= 0
    passed = passed and checks["combined_train_val_test_exp_gte_zero"]
    return {
        "test_pass": passed,
        "checks": checks,
        "failed_gates": [k for k, v in checks.items() if not v],
        "verdict": "RESEARCH_PASS_PROMOTION_REVIEW_REQUIRED" if passed else "REJECT",
    }


def load_baseline_comparison() -> dict[str, Any]:
    out: dict[str, Any] = {}
    if DEDUPED_C008.exists():
        out["c008_deduped"] = json.loads(DEDUPED_C008.read_text())["CAMPAIGN_008"]
    if DEDUPED_C009.exists():
        out["c009_deduped"] = json.loads(DEDUPED_C009.read_text())["CAMPAIGN_009"]
    if C011_NULL.exists():
        null = json.loads(C011_NULL.read_text())
        out["c011_null"] = {
            "aggregate_expectancy_r": null.get("aggregate_expectancy_r", C011_NULL_EXP_R),
            "total_trades": null.get("total_trades"),
        }
    return out


def run_train_validation(ctx: CampaignCtx) -> dict[str, Any]:
    pairs = ctx.settings.market.instruments
    for split in ("train", "validation"):
        for pair in pairs:
            run_pair_split(ctx, instrument=pair, split=split, regime=COST_BASE)
    for pair in pairs:
        run_pair_split(ctx, instrument=pair, split="validation", regime=COST_STRESS_2X)
    for pair in pairs:
        run_pair_split(ctx, instrument=pair, split="full", regime=COST_STRESS_15X)
    agg = {
        "train": aggregate(ctx.runs, "train", "base"),
        "validation": aggregate(ctx.runs, "validation", "base"),
        "validation_stress_2x": aggregate(ctx.runs, "validation", "stress_2x"),
        "full_stress_15x": aggregate(ctx.runs, "full", "stress_15x"),
    }
    trades = pd.concat(ctx.all_trades, ignore_index=True) if ctx.all_trades else pd.DataFrame()
    mech = mechanism_diagnostics(trades)
    gates = evaluate_gates(agg, mech)
    return {"aggregate": agg, "mechanism": mech, "gates": gates}


def run_test(ctx: CampaignCtx) -> dict[str, Any]:
    pairs = ctx.settings.market.instruments
    for pair in pairs:
        run_pair_split(ctx, instrument=pair, split="test", regime=COST_BASE)
    return {"test": aggregate(ctx.runs, "test", "base")}


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
    for name, key in [
        ("run_manifest.json", "manifest"),
        ("train_metrics.json", "aggregate"),
        ("validation_metrics.json", "aggregate"),
        ("gate_result.json", "gates"),
        ("mechanism_diagnostics.json", "mechanism"),
        ("cost_stress_2x.json", "aggregate"),
        ("comparison_to_c008_c009_deduped.json", "comparison"),
        ("comparison_to_c011_null.json", "comparison"),
    ]:
        pass
    (OUT_RESEARCH / "run_manifest.json").write_text(
        json.dumps(payload.get("manifest", {}), indent=2, default=str),
        encoding="utf-8",
    )
    agg = payload.get("aggregate", {})
    (OUT_RESEARCH / "train_metrics.json").write_text(json.dumps(agg.get("train", {}), indent=2), encoding="utf-8")
    (OUT_RESEARCH / "validation_metrics.json").write_text(
        json.dumps(agg.get("validation", {}), indent=2), encoding="utf-8"
    )
    (OUT_RESEARCH / "gate_result.json").write_text(
        json.dumps(payload.get("gates", {}), indent=2, default=str), encoding="utf-8"
    )
    (OUT_RESEARCH / "mechanism_diagnostics.json").write_text(
        json.dumps(payload.get("mechanism", {}), indent=2), encoding="utf-8"
    )
    (OUT_RESEARCH / "cost_stress_2x.json").write_text(
        json.dumps(agg.get("validation_stress_2x", {}), indent=2), encoding="utf-8"
    )
    comp = payload.get("comparison", {})
    (OUT_RESEARCH / "comparison_to_c008_c009_deduped.json").write_text(
        json.dumps(
            {k: comp[k] for k in ("c018", "c008_deduped", "c009_deduped") if k in comp},
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    (OUT_RESEARCH / "comparison_to_c011_null.json").write_text(
        json.dumps(
            {k: comp[k] for k in ("c018_validation", "c011_null", "beat_null_threshold") if k in comp},
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    (OUT_RESEARCH / "metrics_summary.json").write_text(
        json.dumps(payload.get("metrics_summary", {}), indent=2, default=str),
        encoding="utf-8",
    )
    (OUT_RESEARCH / "evidence_status.json").write_text(
        json.dumps(payload.get("evidence_status", {}), indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="CAMPAIGN_018 runner")
    parser.add_argument(
        "command",
        choices=["train-validation", "test", "full"],
        help="train-validation only, conditional test, or both if gates pass",
    )
    args = parser.parse_args()
    t0 = time.time()
    ctx = load_ctx()
    baseline = load_baseline_comparison()
    manifest = {
        "campaign_id": "CAMPAIGN_018",
        "strategy_name": "mean_reversion_protective_stop",
        "strategy_version": "0.1.0-c018",
        "hypothesis": "delayed_reversion_protective_stop_after_1R",
        "config_path": str(CONFIG_PATH.relative_to(ROOT)),
        "dedupe_policy": DEDUPE_POLICY,
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "started_at_utc": datetime.now(UTC).isoformat(),
    }
    payload: dict[str, Any] = {"manifest": manifest, "comparison": baseline}

    if args.command in ("train-validation", "full"):
        tv = run_train_validation(ctx)
        payload.update(tv)
        agg = tv["aggregate"]
        payload["comparison"] = {
            **baseline,
            "c018": agg,
            "c018_validation": agg.get("validation"),
            "beat_null_threshold": C011_NULL_EXP_R + BEAT_NULL_MARGIN,
        }
        payload["metrics_summary"] = agg
        payload["evidence_status"] = {
            "campaign_id": "CAMPAIGN_018",
            "strategy_evidence": True,
            "not_approved": True,
            "paper_demo_live_enabled": False,
            "test_window_opened": False,
        }
        write_artifacts(payload)
        print(f"Screening pass: {tv['gates']['screening_pass']} verdict={tv['gates']['verdict']}")
        if args.command == "full" and tv["gates"]["screening_pass"]:
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
            print("Test lockbox NOT opened — screening failed")
    elif args.command == "test":
        raise SystemExit("Run train-validation first; test only if screening passes")

    manifest["elapsed_seconds"] = round(time.time() - t0, 1)
    write_artifacts(payload)
    print(f"Done in {manifest['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
