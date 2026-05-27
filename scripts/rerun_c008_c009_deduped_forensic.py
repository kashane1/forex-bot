#!/usr/bin/env python3
"""Deduped forensic replay for CAMPAIGN_008 and CAMPAIGN_009.

Re-runs frozen mean-reversion configs on deduped candle inputs.
strategy_evidence: false. forensic_only: true. No test lockbox.
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

from research.cost_atlas.loader import load_deduped_h4_frame
from research.edge_discovery.real_data import resolve_h4_store_path

from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.exporters import write_all
from forex_bot.backtesting.fills import FillModel
from forex_bot.config import load_settings
from forex_bot.data.candle_dedupe import DEDUPE_POLICY
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo, InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.mean_reversion import MeanReversionStrategy

RESEARCH_OUT = ROOT / "research/deduped_c008_c009_rerun"
FROZEN_JSON = RESEARCH_OUT / "frozen_config_reconstruction.json"
C008_OUT = ROOT / "backtests/CAMPAIGN_008_mean_reversion_deduped_forensic"
C009_OUT = ROOT / "backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic"

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2020-01-01", "2022-12-31"),
    "validation": ("2023-01-01", "2024-12-31"),
    "test_untouched": ("2025-01-01", "2026-05-20"),
    "full": ("2020-01-01", "2026-05-20"),
}

COST_REGIMES: list[dict[str, object]] = [
    {"name": "base", "spread_multiplier": 0.5, "fixed_slippage_pips": 0.2},
    {"name": "stress_15x", "spread_multiplier": 1.5, "fixed_slippage_pips": 0.3},
    {"name": "stress_2x", "spread_multiplier": 2.0, "fixed_slippage_pips": 0.5},
]

C008_FROZEN = {
    "version": "0.1.0-c008",
    "midline_exit": False,
    "atr_lookback": 14,
    "zscore_lookback": 20,
    "zscore_long_threshold": -2.0,
    "zscore_short_threshold": 2.0,
    "rsi_lookback": 14,
    "regime_ema": 200,
    "adx_lookback": 14,
    "adx_max": 20.0,
    "atr_stop_multiple": 1.5,
    "max_bars_in_trade": 40,
}

C009_FROZEN = {**C008_FROZEN, "version": "0.2.0-c009", "midline_exit": True}

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


def validate_frozen_config(settings, campaign: str) -> None:
    sc = settings.strategy
    if sc.enabled != ["mean_reversion"] or sc.mean_reversion is None:
        raise SystemExit(f"{campaign}: config must enable only mean_reversion")
    cfg = sc.mean_reversion.model_dump()
    expected = C008_FROZEN if campaign == "CAMPAIGN_008" else C009_FROZEN
    for key, val in expected.items():
        got = cfg.get(key)
        if key == "midline_exit" and campaign == "CAMPAIGN_008":
            if got not in (False, None):
                raise SystemExit(f"C008 midline_exit must be false/absent, got {got}")
            continue
        if got != val:
            raise SystemExit(
                f"{campaign} frozen param mismatch: {key} expected {val!r}, got {got!r}"
            )


@dataclass
class RunRecord:
    label: str
    instrument: str
    split: str
    cost_regime: str
    strategy_version: str
    data_request_hash: str
    dedupe_stats: dict[str, int]
    metrics: dict[str, Any]
    summary_path: str
    trades_path: str


@dataclass
class ReplayCtx:
    campaign_id: str
    settings: Any
    db: Database
    instr: InstrumentRepo
    candles: CandleRepo
    ds: DataSourceRepo
    out_root: Path
    risk_engine: RiskEngine
    strategy_cfg: dict[str, Any]
    granularity: str
    runs: list[RunRecord] = field(default_factory=list)


def load_replay_ctx(config_path: Path, out_root: Path, campaign_id: str) -> ReplayCtx:
    settings = load_settings(config_path)
    validate_frozen_config(settings, campaign_id)
    cfg = settings.strategy.mean_reversion.model_dump()
    db = Database(settings.app.database_path)
    out_root.mkdir(parents=True, exist_ok=True)
    return ReplayCtx(
        campaign_id=campaign_id,
        settings=settings,
        db=db,
        instr=InstrumentRepo(db),
        candles=CandleRepo(db),
        ds=DataSourceRepo(db),
        out_root=out_root,
        risk_engine=RiskEngine(settings, mode="backtest"),
        strategy_cfg=cfg,
        granularity=settings.market.granularity,
    )


def data_preflight(db_path: Path, pairs: list[str], splits: list[str]) -> dict[str, Any]:
    reasons: list[str] = []
    if not db_path.exists():
        return {
            "blocked": True,
            "reason": "BLOCKED_DATA_STORE_MISSING",
            "messages": [f"database missing: {db_path}"],
        }
    details: dict[str, Any] = {
        "dedupe_policy": DEDUPE_POLICY,
        "input_classification": "DEDUPED_INPUT",
        "duplicate_rows_detected_total": 0,
        "duplicate_rows_dropped_total": 0,
        "per_pair": {},
    }
    db = Database(db_path)
    candle_repo = CandleRepo(db)
    ds_repo = DataSourceRepo(db)
    for pair in pairs:
        per_pair: dict[str, Any] = {"source": None, "splits": {}}
        src_row = ds_repo.latest_for(pair, "H4")
        source = (src_row or {}).get("source", "unknown")
        per_pair["source"] = source
        if source != REQUIRED_DATA_SOURCE:
            reasons.append(f"{pair}: source {source!r} != {REQUIRED_DATA_SOURCE}")
        for split in splits:
            frm_s, to_s = SPLITS[split]
            frm, to = _parse(frm_s), _parse(to_s)
            rows, stats = candle_repo.list_with_dedupe_stats(
                pair, "H4", completed_only=True,
                from_time=frm, to_time=to,  # type: ignore[arg-type]
            )
            per_pair["splits"][split] = {
                "deduped_count": stats.deduped_count,
                "raw_count": stats.raw_count,
                "duplicates_detected": stats.duplicates_detected,
                "duplicates_dropped": stats.duplicates_dropped,
            }
            details["duplicate_rows_detected_total"] += stats.duplicates_detected
            details["duplicate_rows_dropped_total"] += stats.duplicates_dropped
            if not rows:
                reasons.append(f"{pair} {split}: zero candles")
            frame = CandleFrame.from_candles(pair, "H4", rows)  # type: ignore[arg-type]
            if not frame.df.index.is_unique:
                reasons.append(f"{pair} {split}: non-unique index after dedupe")
        details["per_pair"][pair] = per_pair
    return {
        "blocked": bool(reasons),
        "reason": "BLOCKED_DATA_PREFLIGHT" if reasons else None,
        "messages": reasons,
        "details": details,
    }


def run_single(
    ctx: ReplayCtx,
    *,
    instrument: str,
    split: str,
    regime: dict[str, object],
    sub_dir: str,
    label_prefix: str,
) -> RunRecord:
    if split == "test_untouched":
        raise SystemExit("test lockbox must not be opened in forensic replay")
    meta = ctx.instr.get(instrument)
    if meta is None:
        raise SystemExit(f"missing instrument metadata: {instrument}")
    frm, to = SPLITS[split]
    from_dt, to_dt = _parse(frm), _parse(to)
    rows, dedupe_stats = ctx.candles.list_with_dedupe_stats(
        instrument, ctx.granularity, completed_only=True,
        from_time=from_dt, to_time=to_dt,  # type: ignore[arg-type]
    )
    if not rows:
        raise SystemExit(f"no candles: {instrument} {split}")
    frame = CandleFrame.from_candles(instrument, ctx.granularity, rows)  # type: ignore[arg-type]
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
    cfg = dict(ctx.strategy_cfg)
    regime_name = str(regime["name"])
    engine = BacktestEngine(
        instrument=meta,
        strategy=MeanReversionStrategy(version=cfg["version"]),
        strategy_config=cfg,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(regime["fixed_slippage_pips"])),
            spread_slippage_multiplier=Decimal(str(regime["spread_multiplier"])),
        ),
        starting_equity=Decimal(str(ctx.settings.backtest.starting_equity_usd)),
        account_currency=ctx.settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(ctx.settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(cfg.get("max_bars_in_trade", 40)),
        commission_per_unit=Decimal(str(ctx.settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(cfg.get("atr_lookback", 14)),
        risk_engine=ctx.risk_engine,
        settings=ctx.settings,
    )
    result = engine.run(frame, data_request_hash=data_hash)
    label = f"{label_prefix}_{instrument}_{ctx.granularity}_{split}"
    paths = write_all(result, ctx.out_root / sub_dir, label, split=split)
    summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
    summary.update(
        split=split,
        cost_regime=regime_name,
        forensic_only=True,
        strategy_evidence=False,
        dedupe_policy=DEDUPE_POLICY,
        dedupe_stats={
            "raw_count": dedupe_stats.raw_count,
            "deduped_count": dedupe_stats.deduped_count,
            "duplicates_dropped": dedupe_stats.duplicates_dropped,
        },
    )
    paths["summary_json"].write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    rec = RunRecord(
        label=label,
        instrument=instrument,
        split=split,
        cost_regime=regime_name,
        strategy_version=cfg["version"],
        data_request_hash=data_hash,
        dedupe_stats={
            "raw_count": dedupe_stats.raw_count,
            "deduped_count": dedupe_stats.deduped_count,
            "duplicates_dropped": dedupe_stats.duplicates_dropped,
        },
        metrics=_metrics_to_dict(result.metrics),
        summary_path=str(paths["summary_json"].relative_to(ctx.out_root)),
        trades_path=str(paths["trades_csv"].relative_to(ctx.out_root)),
    )
    ctx.runs.append(rec)
    return rec


def run_c008_forensic(ctx: ReplayCtx) -> None:
    pairs = ctx.settings.market.instruments
    base = COST_REGIMES[0]
    for split in ("train", "validation"):
        for pair in pairs:
            run_single(
                ctx, instrument=pair, split=split, regime=base,
                sub_dir=f"baseline/{split}", label_prefix="baseline",
            )
            print(f"  C008 deduped {split}/base {pair}: done")
    for regime in COST_REGIMES:
        for pair in pairs:
            run_single(
                ctx, instrument=pair, split="full", regime=regime,
                sub_dir=f"cost_stress/{regime['name']}",
                label_prefix=f"cost_{regime['name']}",
            )
            print(f"  C008 deduped full/{regime['name']} {pair}: done")


def run_c009_forensic(ctx: ReplayCtx) -> None:
    pairs = ctx.settings.market.instruments
    for split in ("train", "validation"):
        for regime in COST_REGIMES:
            for pair in pairs:
                run_single(
                    ctx, instrument=pair, split=split, regime=regime,
                    sub_dir=f"{split}/{regime['name']}", label_prefix=f"{split}_{regime['name']}",
                )
                print(f"  C009 deduped {split}/{regime['name']} {pair}: done")


def aggregate_split(runs: list[RunRecord], split: str, cost_regime: str = "base") -> dict[str, Any]:
    subset = [r for r in runs if r.split == split and r.cost_regime == cost_regime]
    if not subset:
        return {"trade_count": 0, "expectancy_r": None, "profit_factor": None, "pairs_positive": 0}
    total_trades = sum(r.metrics["trade_count"] for r in subset)
    weighted_exp = sum(
        r.metrics["expectancy_r"] * r.metrics["trade_count"] for r in subset
    ) / total_trades if total_trades else 0.0
    pfs = [r.metrics["profit_factor"] for r in subset if r.metrics["profit_factor"] is not None]
    pairs_pos = sum(1 for r in subset if r.metrics["total_return_pct"] > 0)
    return {
        "trade_count": total_trades,
        "expectancy_r": round(weighted_exp, 4),
        "profit_factor": round(statistics.mean(pfs), 4) if pfs else None,
        "pairs_positive": pairs_pos,
        "pairs_total": len(subset),
        "per_pair": {
            r.instrument: r.metrics for r in subset
        },
    }


def evaluate_c008_gates(agg: dict[str, Any]) -> dict[str, Any]:
    train = agg["train_base"]
    val = agg["validation_base"]
    stress15 = agg.get("full_stress_15x", {})
    checks = {
        "train_expectancy_gte_zero": (train.get("expectancy_r") or -999) >= 0,
        "validation_expectancy_gte_zero": (val.get("expectancy_r") or -999) >= 0,
        "validation_pf_gte_1_05": (val.get("profit_factor") or 0) >= 1.05,
        "validation_pairs_positive_gte_2": val.get("pairs_positive", 0) >= 2,
        "validation_trade_count_gte_30": val.get("trade_count", 0) >= 30,
        "full_stress_15x_expectancy_gte_zero": (stress15.get("expectancy_r") or -999) >= 0,
    }
    passed = all(checks.values())
    failed = [k for k, v in checks.items() if not v]
    return {
        "screening_pass": passed,
        "checks": checks,
        "failed_gates": failed,
        "test_window_opened": False,
        "verdict": "REJECT" if not passed else "SCREEN_PASS_NOT_OPENING_TEST",
    }


def evaluate_c009_gates(agg: dict[str, Any]) -> dict[str, Any]:
    train = agg["train_base"]
    val = agg["validation_base"]
    val2x = agg.get("validation_stress_2x", {})
    checks = {
        "train_expectancy_gte_zero": (train.get("expectancy_r") or -999) >= 0,
        "validation_expectancy_gt_zero": (val.get("expectancy_r") or -999) > 0,
        "validation_pf_gte_1_05": (val.get("profit_factor") or 0) >= 1.05,
        "validation_stress_2x_expectancy_gte_zero": (val2x.get("expectancy_r") or -999) >= 0,
        "validation_pairs_positive_gte_2": val.get("pairs_positive", 0) >= 2,
        "validation_trade_count_gte_30": val.get("trade_count", 0) >= 30,
    }
    passed = all(checks.values())
    failed = [k for k, v in checks.items() if not v]
    return {
        "screening_pass": passed,
        "checks": checks,
        "failed_gates": failed,
        "test_window_opened": False,
        "verdict": "REJECT" if not passed else "SCREEN_PASS_NOT_OPENING_TEST",
    }


def _load_trades_glob(pattern: str, campaign_id: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(ROOT.glob(pattern)):
        parts = path.parts
        split = "unknown"
        for p in parts:
            if p in ("train", "validation", "full"):
                split = p
                break
        df = pd.read_csv(path)
        df["campaign_id"] = campaign_id
        df["split"] = split
        df["source_artifact"] = str(path.relative_to(ROOT))
        if "entry_time" in df.columns:
            df["entry_time"] = pd.to_datetime(df["entry_time"], utc=True)
        if "exit_time" in df.columns:
            df["exit_time"] = pd.to_datetime(df["exit_time"], utc=True)
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _exit_breakdown(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty:
        return {}
    out: dict[str, Any] = {"total_trades": len(trades), "by_exit_reason": {}}
    for reason, grp in trades.groupby("exit_reason"):
        out["by_exit_reason"][str(reason)] = {
            "count": len(grp),
            "share_pct": round(100.0 * len(grp) / len(trades), 2),
            "expectancy_r": round(float(grp["r_multiple"].mean()), 4),
            "median_r": round(float(grp["r_multiple"].median()), 4),
            "avg_bars_held": round(float(grp["bars_held"].mean()), 2),
        }
    return out


def _stop_distance_pips(row: pd.Series) -> float | None:
    if pd.isna(row.get("entry_price")) or pd.isna(row.get("stop_price")):
        return None
    entry = float(row["entry_price"])
    stop = float(row["stop_price"])
    inst = str(row.get("instrument", ""))
    dist = abs(entry - stop)
    return dist * 100.0 if "JPY" in inst else dist * 10000.0


def compute_mae_mfe(trades: pd.DataFrame) -> dict[str, Any]:
    db_path = resolve_h4_store_path(ROOT)
    if db_path is None or trades.empty:
        return {"mae_mfe_computed": False, "reason": "no_db_or_trades"}
    records: list[dict[str, Any]] = []
    cache: dict[str, pd.DataFrame] = {}
    for _, trade in trades.iterrows():
        inst = str(trade["instrument"])
        if inst not in cache:
            frame, _ = load_deduped_h4_frame(ROOT, inst, db_path=db_path)
            cache[inst] = frame
        window = cache[inst][
            (cache[inst].index >= trade["entry_time"]) & (cache[inst].index <= trade["exit_time"])
        ]
        if window.empty:
            continue
        entry = float(trade["entry_price"])
        stop = float(trade["stop_price"]) if pd.notna(trade.get("stop_price")) else None
        side = str(trade["side"])
        if side == "long":
            mae = entry - float(window["low"].min())
            mfe = float(window["high"].max()) - entry
        else:
            mae = float(window["high"].max()) - entry
            mfe = entry - float(window["low"].min())
        stop_dist = abs(entry - stop) if stop is not None else None
        mae_r = mae / stop_dist if stop_dist and stop_dist > 0 else None
        mfe_r = mfe / stop_dist if stop_dist and stop_dist > 0 else None
        records.append(
            {
                "split": trade.get("split"),
                "exit_reason": trade.get("exit_reason"),
                "mae_r": mae_r,
                "mfe_r": mfe_r,
                "reached_1r_favorable": mfe_r is not None and mfe_r >= 1.0,
                "stop_distance_pips": _stop_distance_pips(trade),
            }
        )
    if not records:
        return {"mae_mfe_computed": False, "reason": "no_joinable_trades"}
    df = pd.DataFrame(records)
    stop = df[df["exit_reason"] == "stop"]
    time_df = df[df["exit_reason"] == "time"]
    target = df[df["exit_reason"] == "target"]
    return {
        "mae_mfe_computed": True,
        "trades_computed": len(df),
        "stop_trades": len(stop),
        "stop_pct_reached_1r_before_stop": round(100.0 * float(stop["reached_1r_favorable"].mean()), 2)
        if len(stop)
        else None,
        "stop_pct_never_1r_favorable": round(100.0 * float((~stop["reached_1r_favorable"]).mean()), 2)
        if len(stop)
        else None,
        "stop_median_mfe_r": round(float(stop["mfe_r"].median()), 4) if len(stop) else None,
        "time_median_mfe_r": round(float(time_df["mfe_r"].median()), 4) if len(time_df) else None,
        "target_median_mfe_r": round(float(target["mfe_r"].median()), 4) if len(target) else None,
        "median_stop_distance_pips": round(float(df["stop_distance_pips"].median()), 2),
    }


def load_original_headline(campaign: str) -> dict[str, Any]:
    if campaign == "CAMPAIGN_008":
        return {
            "train": {"trades": 216, "expectancy_r": -0.017, "profit_factor": 1.02},
            "validation": {"trades": 138, "expectancy_r": 0.172, "profit_factor": 1.29, "pairs_positive": 6},
            "full_stress_15x": {"expectancy_r": 0.04},
        }
    return {
        "train": {"trades": 252, "expectancy_r": -0.062, "profit_factor": 0.97},
        "validation": {"trades": 151, "expectancy_r": 0.17, "profit_factor": 1.37, "pairs_positive": 4},
    }


def classify_delta(old_val: float | None, new_val: float | None, tol: float = 0.02) -> str:
    if old_val is None or new_val is None:
        return "UNKNOWN"
    if abs(new_val - old_val) <= tol:
        return "CONFIRMED_DEDUP_SAFE"
    return "MATERIAL_CHANGE"


def build_comparison(c008_runs: list[RunRecord], c009_runs: list[RunRecord]) -> dict[str, Any]:
    c008_agg = {
        "train_base": aggregate_split(c008_runs, "train", "base"),
        "validation_base": aggregate_split(c008_runs, "validation", "base"),
        "full_stress_15x": aggregate_split(c008_runs, "full", "stress_15x"),
        "full_stress_2x": aggregate_split(c008_runs, "full", "stress_2x"),
    }
    c009_agg = {
        "train_base": aggregate_split(c009_runs, "train", "base"),
        "validation_base": aggregate_split(c009_runs, "validation", "base"),
        "validation_stress_2x": aggregate_split(c009_runs, "validation", "stress_2x"),
    }
    c008_orig = load_original_headline("CAMPAIGN_008")
    c009_orig = load_original_headline("CAMPAIGN_009")
    return {
        "strategy_evidence": False,
        "forensic_only": True,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "CAMPAIGN_008": {
            "deduped": c008_agg,
            "original_headline": c008_orig,
            "classification": {
                "train_expectancy_r": classify_delta(
                    c008_orig["train"]["expectancy_r"], c008_agg["train_base"]["expectancy_r"]
                ),
                "validation_expectancy_r": classify_delta(
                    c008_orig["validation"]["expectancy_r"],
                    c008_agg["validation_base"]["expectancy_r"],
                ),
                "train_fail_persists": (c008_agg["train_base"]["expectancy_r"] or 0) < 0,
                "validation_positive_persists": (c008_agg["validation_base"]["expectancy_r"] or 0) > 0,
            },
        },
        "CAMPAIGN_009": {
            "deduped": c009_agg,
            "original_headline": c009_orig,
            "classification": {
                "train_expectancy_r": classify_delta(
                    c009_orig["train"]["expectancy_r"], c009_agg["train_base"]["expectancy_r"]
                ),
                "validation_expectancy_r": classify_delta(
                    c009_orig["validation"]["expectancy_r"],
                    c009_agg["validation_base"]["expectancy_r"],
                ),
                "train_fail_persists": (c009_agg["train_base"]["expectancy_r"] or 0) < 0,
                "validation_positive_persists": (c009_agg["validation_base"]["expectancy_r"] or 0) > 0,
            },
        },
    }


def write_replay_artifacts(
    *,
    preflight: dict[str, Any],
    c008_ctx: ReplayCtx,
    c009_ctx: ReplayCtx,
    elapsed: float,
) -> None:
    RESEARCH_OUT.mkdir(parents=True, exist_ok=True)
    c008_agg = {
        "train_base": aggregate_split(c008_ctx.runs, "train", "base"),
        "validation_base": aggregate_split(c008_ctx.runs, "validation", "base"),
        "full_stress_15x": aggregate_split(c008_ctx.runs, "full", "stress_15x"),
        "full_stress_2x": aggregate_split(c008_ctx.runs, "full", "stress_2x"),
    }
    c009_agg = {
        "train_base": aggregate_split(c009_ctx.runs, "train", "base"),
        "validation_base": aggregate_split(c009_ctx.runs, "validation", "base"),
        "validation_stress_2x": aggregate_split(c009_ctx.runs, "validation", "stress_2x"),
    }
    gate_c008 = evaluate_c008_gates(c008_agg)
    gate_c009 = evaluate_c009_gates(c009_agg)
    stamp = datetime.now(UTC).isoformat()
    meta = {
        "strategy_evidence": False,
        "forensic_only": True,
        "not_approval": True,
        "test_window_opened": False,
    }
    (RESEARCH_OUT / "metrics_summary.json").write_text(
        json.dumps(
            {
                **meta,
                "generated_at_utc": stamp,
                "CAMPAIGN_008": c008_agg,
                "CAMPAIGN_009": c009_agg,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (RESEARCH_OUT / "gate_result.json").write_text(
        json.dumps({**meta, "generated_at_utc": stamp, "CAMPAIGN_008": gate_c008, "CAMPAIGN_009": gate_c009}, indent=2),
        encoding="utf-8",
    )
    (RESEARCH_OUT / "run_manifest.json").write_text(
        json.dumps(
            {
                **meta,
                "generated_at_utc": stamp,
                "git_commit": _git("rev-parse", "HEAD"),
                "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
                "preflight": preflight,
                "c008_runs": len(c008_ctx.runs),
                "c009_runs": len(c009_ctx.runs),
                "elapsed_seconds": round(elapsed, 2),
                "c008_out": str(C008_OUT.relative_to(ROOT)),
                "c009_out": str(C009_OUT.relative_to(ROOT)),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (RESEARCH_OUT / "evidence_status.json").write_text(
        json.dumps(
            {
                **meta,
                "generated_at_utc": stamp,
                "prior_integrity": "LIKELY_CONTAMINATED",
                "deduped_replay_status": "COMPLETE",
                "c008_verdict_unchanged": "REJECT",
                "c009_verdict_unchanged": "REJECT",
                "promotion_eligible": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def cmd_replay() -> int:
    t0 = time.time()
    db_path = ROOT / "data/campaign_002.sqlite3"
    settings = load_settings(ROOT / "configs/campaign_008_range_mean_reversion.yaml")
    pairs = settings.market.instruments
    splits_needed = ["train", "validation", "full"]
    preflight = data_preflight(db_path, pairs, splits_needed)
    if preflight["blocked"]:
        (RESEARCH_OUT / "evidence_status.json").write_text(
            json.dumps(
                {
                    "strategy_evidence": False,
                    "forensic_only": True,
                    "deduped_replay_status": preflight.get("reason", "BLOCKED"),
                    "messages": preflight.get("messages", []),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print("PREFLIGHT BLOCKED:", preflight.get("messages"))
        return 2

    c008_ctx = load_replay_ctx(
        ROOT / "configs/campaign_008_range_mean_reversion.yaml", C008_OUT, "CAMPAIGN_008"
    )
    c009_ctx = load_replay_ctx(
        ROOT / "configs/campaign_009_mean_reversion.yaml", C009_OUT, "CAMPAIGN_009"
    )
    print("=== C008 deduped forensic replay ===")
    run_c008_forensic(c008_ctx)
    print("=== C009 deduped forensic replay ===")
    run_c009_forensic(c009_ctx)
    elapsed = time.time() - t0
    write_replay_artifacts(preflight=preflight, c008_ctx=c008_ctx, c009_ctx=c009_ctx, elapsed=elapsed)
    comparison = build_comparison(c008_ctx.runs, c009_ctx.runs)
    (RESEARCH_OUT / "old_vs_deduped_metric_comparison.json").write_text(
        json.dumps(comparison, indent=2), encoding="utf-8"
    )
    c008_trades = _load_trades_glob("backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/baseline/*/*_trades.csv", "CAMPAIGN_008_DEDUPED")
    c009_trades = _load_trades_glob("backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic/*/*/*_trades.csv", "CAMPAIGN_009_DEDUPED")
    anatomy = {
        "strategy_evidence": False,
        "forensic_only": True,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "CAMPAIGN_008": _exit_breakdown(c008_trades),
        "CAMPAIGN_009": _exit_breakdown(c009_trades),
        "c008_train_validation": {
            "train": _exit_breakdown(c008_trades[c008_trades["split"] == "train"]),
            "validation": _exit_breakdown(c008_trades[c008_trades["split"] == "validation"]),
        },
        "c009_train_validation": {
            "train": _exit_breakdown(c009_trades[c009_trades["split"] == "train"]),
            "validation": _exit_breakdown(c009_trades[c009_trades["split"] == "validation"]),
        },
    }
    (RESEARCH_OUT / "deduped_exit_anatomy.json").write_text(json.dumps(anatomy, indent=2), encoding="utf-8")
    mae = {
        "strategy_evidence": False,
        "forensic_only": True,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "CAMPAIGN_008": compute_mae_mfe(c008_trades),
        "CAMPAIGN_009": compute_mae_mfe(c009_trades),
    }
    (RESEARCH_OUT / "deduped_mae_mfe.json").write_text(json.dumps(mae, indent=2), encoding="utf-8")
    print(f"\nForensic replay complete in {elapsed:.1f}s")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Deduped C008/C009 forensic replay")
    ap.add_argument(
        "command",
        nargs="?",
        default="replay",
        choices=["replay"],
        help="run deduped forensic replay",
    )
    return cmd_replay()


if __name__ == "__main__":
    raise SystemExit(main())
