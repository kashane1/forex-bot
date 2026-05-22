#!/usr/bin/env python3
"""CAMPAIGN_004 runner — volatility-breakout (a different entry family).

ONE strategy: volatility_breakout 0.1.0-c004 (compression → expansion
breakout, no EMA filter). No optimizer, no robustness grid.

  - Baseline phase: 1 strategy × 6 pairs × 4 splits = 24 runs.
  - Cost stress:    1 strategy × 6 pairs × 3 regimes (full window) = 18 runs.
  - Total ~42 runs, H4 only.

Reuses real OANDA practice H4 candles from data/campaign_002.sqlite3.
RiskEngine wired in (mode="backtest"); every run exports a per-signal
risk_rejections CSV. Writes nothing into prior-campaign artifacts.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.exporters import write_all
from forex_bot.backtesting.fills import FillModel
from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo, InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.volatility_breakout import VolatilityBreakoutStrategy

PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF"]
GRANULARITY = "H4"
STRATEGY_VERSION = "0.1.0-c004"

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


@dataclass
class RunRecord:
    label: str
    instrument: str
    granularity: str
    split: str | None
    cost_regime: str
    config_hash: str
    data_request_hash: str
    strategy_version: str
    metrics: dict
    rejection_counts: dict
    rejected_signal_count: int
    summary_path: str


def _parse(d: str) -> datetime:
    return datetime.fromisoformat(d).replace(tzinfo=UTC)


def _git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        return "unknown"
    return r.stdout.strip() or "unknown"


def _git_dirty() -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        return False
    return bool(r.stdout.strip())


@dataclass
class CampaignContext:
    settings: object
    db: Database
    instr_repo: InstrumentRepo
    candle_repo: CandleRepo
    ds_repo: DataSourceRepo
    out_root: Path
    risk_engine: RiskEngine
    runs: list[RunRecord] = field(default_factory=list)


def load_context(config_path: Path, out_root: Path) -> CampaignContext:
    settings = load_settings(config_path)
    db = Database(settings.app.database_path)
    out_root.mkdir(parents=True, exist_ok=True)
    return CampaignContext(
        settings=settings,
        db=db,
        instr_repo=InstrumentRepo(db),
        candle_repo=CandleRepo(db),
        ds_repo=DataSourceRepo(db),
        out_root=out_root,
        risk_engine=RiskEngine(settings, mode="backtest"),
    )


def _strategy_cfg(settings) -> dict:
    cfg = settings.strategy.volatility_breakout.model_dump()
    cfg["version"] = STRATEGY_VERSION
    return cfg


def run_single(
    ctx: CampaignContext,
    *,
    instrument: str,
    from_dt: datetime,
    to_dt: datetime,
    spread_mult: float,
    fixed_slip: float,
    label: str,
    split: str,
    cost_regime: str,
    sub_dir: str,
) -> RunRecord | None:
    instrument_meta = ctx.instr_repo.get(instrument)
    if instrument_meta is None:
        return None
    rows = ctx.candle_repo.list(
        instrument, GRANULARITY, completed_only=True, from_time=from_dt, to_time=to_dt  # type: ignore[arg-type]
    )
    if not rows:
        return None
    frame = CandleFrame.from_candles(instrument, GRANULARITY, rows)  # type: ignore[arg-type]
    source = (ctx.ds_repo.latest_for(instrument, GRANULARITY) or {}).get(
        "source", "oanda-practice"
    )
    data_hash = compute_data_request_hash(
        instrument=instrument,
        granularity=GRANULARITY,
        from_time=from_dt.isoformat(),
        to_time=to_dt.isoformat(),
        source=source,
        candle_count=len(rows),
    )
    cfg = _strategy_cfg(ctx.settings)
    engine = BacktestEngine(
        instrument=instrument_meta,
        strategy=VolatilityBreakoutStrategy(version=cfg["version"]),
        strategy_config=cfg,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(fixed_slip)),
            spread_slippage_multiplier=Decimal(str(spread_mult)),
        ),
        starting_equity=Decimal(str(ctx.settings.backtest.starting_equity_usd)),
        account_currency=ctx.settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(ctx.settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(cfg.get("max_bars_in_trade", 120)),
        commission_per_unit=Decimal(str(ctx.settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(cfg.get("atr_lookback", 14)),
        risk_engine=ctx.risk_engine,
        settings=ctx.settings,
    )
    result = engine.run(frame, data_request_hash=data_hash)
    export_dir = ctx.out_root / sub_dir
    paths = write_all(result, export_dir, label, split=split)
    summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
    summary["strategy_params"] = {k: v for k, v in cfg.items() if k != "min_atr_pips"}
    summary["split"] = split
    summary["cost_regime"] = cost_regime
    summary["label"] = label
    summary["data_source"] = source
    summary["risk_engine_used"] = result.risk_engine_used
    summary["rejection_counts"] = result.rejection_counts
    summary["rejected_signal_count"] = len(result.rejected_signals)
    paths["summary_json"].write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )
    record = RunRecord(
        label=label,
        instrument=instrument,
        granularity=GRANULARITY,
        split=split,
        cost_regime=cost_regime,
        config_hash=result.config_hash,
        data_request_hash=data_hash,
        strategy_version=cfg["version"],
        metrics=_metrics_to_dict(result.metrics),
        rejection_counts=result.rejection_counts,
        rejected_signal_count=len(result.rejected_signals),
        summary_path=str(paths["summary_json"].relative_to(ctx.out_root)),
    )
    ctx.runs.append(record)
    return record


def _metrics_to_dict(m) -> dict:
    return {
        "trade_count": m.trade_count,
        "total_return_pct": float(m.total_return_pct),
        "final_equity": float(m.final_equity),
        "starting_equity": float(m.starting_equity),
        "max_drawdown_pct": float(m.max_drawdown_pct),
        "max_drawdown_duration_bars": m.max_drawdown_duration_bars,
        "sharpe": float(m.sharpe),
        "sortino": float(m.sortino),
        "profit_factor": (
            None if m.profit_factor == float("inf") else float(m.profit_factor)
        ),
        "expectancy_r": float(m.expectancy_r),
        "average_r": float(m.average_r),
        "median_r": float(m.median_r),
        "win_rate": float(m.win_rate),
        "average_win": float(m.average_win),
        "average_loss": float(m.average_loss),
        "largest_single_loss": float(m.largest_single_loss),
        "average_spread_paid_pips": float(m.average_spread_paid_pips),
    }


def run_baseline(ctx: CampaignContext) -> None:
    base_regime = COST_REGIMES[0]
    for split, (frm, to) in SPLITS.items():
        for pair in PAIRS:
            run_single(
                ctx,
                instrument=pair,
                from_dt=_parse(frm),
                to_dt=_parse(to),
                spread_mult=float(base_regime["spread_multiplier"]),
                fixed_slip=float(base_regime["fixed_slippage_pips"]),
                label=f"baseline_{pair}_{GRANULARITY}_{split}",
                split=split,
                cost_regime=str(base_regime["name"]),
                sub_dir=f"baseline/{split}",
            )
            print(f"  baseline {pair} {split}: done")


def run_cost_stress(ctx: CampaignContext) -> None:
    from_dt = _parse(SPLITS["full"][0])
    to_dt = _parse(SPLITS["full"][1])
    for regime in COST_REGIMES:
        for pair in PAIRS:
            run_single(
                ctx,
                instrument=pair,
                from_dt=from_dt,
                to_dt=to_dt,
                spread_mult=float(regime["spread_multiplier"]),
                fixed_slip=float(regime["fixed_slippage_pips"]),
                label=f"cost_{regime['name']}_{pair}_{GRANULARITY}",
                split="full",
                cost_regime=str(regime["name"]),
                sub_dir=f"cost_stress/{regime['name']}",
            )
            print(f"  cost {regime['name']} {pair}: done")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default=str(ROOT / "configs/campaign_004_volatility_breakout.yaml"),
    )
    parser.add_argument(
        "--out", default=str(ROOT / "backtests/campaign_004_volatility_breakout/runs")
    )
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    out_root = Path(args.out)
    if args.clean and out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    config_path = Path(args.config)
    ctx = load_context(config_path, out_root)

    t0 = time.time()
    print(f"=== CAMPAIGN_004 baseline {datetime.now(UTC).isoformat()} ===")
    run_baseline(ctx)
    print(f"=== CAMPAIGN_004 cost stress {datetime.now(UTC).isoformat()} ===")
    run_cost_stress(ctx)
    dt = time.time() - t0

    index = {
        "campaign_id": "CAMPAIGN_004",
        "generated_at": datetime.now(UTC).isoformat(),
        "git_commit": _git_commit(),
        "git_commit_short": _git_commit()[:12],
        "git_dirty": _git_dirty(),
        "config_path": str(config_path),
        "config_hash": ctx.settings.config_hash,
        "data_source": "oanda-practice (reused from data/campaign_002.sqlite3)",
        "strategy_version": STRATEGY_VERSION,
        "risk_engine_mode": "backtest",
        "total_runs": len(ctx.runs),
        "elapsed_seconds": dt,
        "runs": [dataclasses.asdict(r) for r in ctx.runs],
    }
    (out_root / "_index.json").write_text(
        json.dumps(index, indent=2, default=str), encoding="utf-8"
    )
    print(f"\nwrote {out_root / '_index.json'}")
    print(f"total runs: {len(ctx.runs)} in {dt:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
