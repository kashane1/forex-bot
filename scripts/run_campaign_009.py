#!/usr/bin/env python3
"""CAMPAIGN_009 runner — mean-reversion + midline exit.

Human-authorized focused follow-up to CAMPAIGN_008 (NOT a marathon
campaign). Implements the CAMPAIGN_009 pre-commit discipline exactly
(`docs/research/CAMPAIGN_009_PRECOMMIT.md`):

  --phase screen : runs train + validation ONLY, each under all three
                   cost regimes (base / stress_15x / stress_2x). The
                   2025-2026 reported test window and the 2020-2026 full
                   descriptive window are NOT touched.
  --phase test   : runs the reported test window (2025-2026) under all
                   three cost regimes, plus the full descriptive window
                   at base cost. Run ONLY after every screening gate in
                   the pre-commit has passed.

RiskEngine is wired in for every run (mode="backtest"); per-signal
risk_rejections CSVs are always exported. Real OANDA practice candles
only — the runner aborts on any other data source (no synthetic
fallback).
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
from forex_bot.strategies.mean_reversion import MeanReversionStrategy

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2020-01-01", "2022-12-31"),
    "validation": ("2023-01-01", "2024-12-31"),
    "test_untouched": ("2025-01-01", "2026-05-20"),
    "full": ("2020-01-01", "2026-05-20"),
}

# Screening touches train + validation only — the test/full windows stay
# sealed until every screening gate passes.
SCREEN_SPLITS = ["train", "validation"]

COST_REGIMES: list[dict[str, object]] = [
    {"name": "base", "spread_multiplier": 0.5, "fixed_slippage_pips": 0.2},
    {"name": "stress_15x", "spread_multiplier": 1.5, "fixed_slippage_pips": 0.3},
    {"name": "stress_2x", "spread_multiplier": 2.0, "fixed_slippage_pips": 0.5},
]

REQUIRED_DATA_SOURCE = "oanda-practice"


def _parse(d: str) -> datetime:
    return datetime.fromisoformat(d).replace(tzinfo=UTC)


def _git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        return ""
    return r.stdout.strip()


@dataclass
class RunRecord:
    label: str
    instrument: str
    granularity: str
    split: str
    cost_regime: str
    config_hash: str
    data_request_hash: str
    data_source: str
    strategy_version: str
    metrics: dict
    rejection_counts: dict
    rejected_signal_count: int
    risk_engine_used: bool
    summary_path: str


@dataclass
class Ctx:
    settings: object
    db: Database
    instr: InstrumentRepo
    candles: CandleRepo
    ds: DataSourceRepo
    out_root: Path
    risk_engine: RiskEngine
    strategy_cfg: dict
    granularity: str
    runs: list[RunRecord] = field(default_factory=list)


def load_ctx(config_path: Path, out_root: Path) -> Ctx:
    settings = load_settings(config_path)
    sc = settings.strategy
    if sc.enabled != ["mean_reversion"] or sc.mean_reversion is None:
        raise SystemExit("CAMPAIGN_009 config must enable only mean_reversion")
    cfg = sc.mean_reversion.model_dump()
    if not cfg.get("midline_exit"):
        raise SystemExit(
            "CAMPAIGN_009 requires mean_reversion.midline_exit: true "
            "(the single predeclared rule change)"
        )
    db = Database(settings.app.database_path)
    out_root.mkdir(parents=True, exist_ok=True)
    return Ctx(
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


def run_single(
    ctx: Ctx,
    *,
    instrument: str,
    split: str,
    regime: dict[str, object],
) -> RunRecord | None:
    meta = ctx.instr.get(instrument)
    if meta is None:
        raise SystemExit(f"instrument metadata missing for {instrument}")
    frm, to = SPLITS[split]
    from_dt, to_dt = _parse(frm), _parse(to)
    rows = ctx.candles.list(
        instrument, ctx.granularity, completed_only=True,
        from_time=from_dt, to_time=to_dt,  # type: ignore[arg-type]
    )
    if not rows:
        raise SystemExit(f"no candles for {instrument} {ctx.granularity} {split}")
    frame = CandleFrame.from_candles(instrument, ctx.granularity, rows)  # type: ignore[arg-type]
    source = (ctx.ds.latest_for(instrument, ctx.granularity) or {}).get(
        "source", "unknown"
    )
    # Provenance guard — real OANDA practice data only, no synthetic fallback.
    if source != REQUIRED_DATA_SOURCE:
        raise SystemExit(
            f"data source for {instrument} {ctx.granularity} is '{source}', "
            f"expected '{REQUIRED_DATA_SOURCE}'. CAMPAIGN_009 aborts — no "
            "synthetic fallback."
        )
    data_hash = compute_data_request_hash(
        instrument=instrument, granularity=ctx.granularity,
        from_time=from_dt.isoformat(), to_time=to_dt.isoformat(),
        source=source, candle_count=len(rows),
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
    label = f"{split}_{regime_name}_{instrument}_{ctx.granularity}"
    sub_dir = f"{split}/{regime_name}"
    paths = write_all(result, ctx.out_root / sub_dir, label, split=split)
    summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
    summary.update(
        strategy_params={k: v for k, v in cfg.items() if k != "min_atr_pips"},
        split=split, cost_regime=regime_name, label=label, data_source=source,
        risk_engine_used=result.risk_engine_used,
        rejection_counts=result.rejection_counts,
        rejected_signal_count=len(result.rejected_signals),
    )
    paths["summary_json"].write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )
    rec = RunRecord(
        label=label, instrument=instrument, granularity=ctx.granularity,
        split=split, cost_regime=regime_name, config_hash=result.config_hash,
        data_request_hash=data_hash, data_source=source,
        strategy_version=cfg["version"],
        metrics=_metrics_to_dict(result.metrics),
        rejection_counts=result.rejection_counts,
        rejected_signal_count=len(result.rejected_signals),
        risk_engine_used=result.risk_engine_used,
        summary_path=str(paths["summary_json"].relative_to(ctx.out_root)),
    )
    ctx.runs.append(rec)
    return rec


def run_phase(ctx: Ctx, phase: str) -> None:
    pairs = ctx.settings.market.instruments
    if phase == "screen":
        for split in SCREEN_SPLITS:
            for regime in COST_REGIMES:
                for pair in pairs:
                    run_single(ctx, instrument=pair, split=split, regime=regime)
                    print(f"  screen {split}/{regime['name']} {pair}: done")
    elif phase == "test":
        for regime in COST_REGIMES:
            for pair in pairs:
                run_single(
                    ctx, instrument=pair, split="test_untouched", regime=regime
                )
                print(f"  TEST test_untouched/{regime['name']} {pair}: done")
        base = COST_REGIMES[0]
        for pair in pairs:
            run_single(ctx, instrument=pair, split="full", regime=base)
            print(f"  full/base {pair}: done")
    else:
        raise SystemExit(f"unknown phase '{phase}'")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--phase", required=True, choices=["screen", "test"])
    ap.add_argument("--clean", action="store_true")
    args = ap.parse_args()

    out_root = Path(args.out)
    if args.clean and args.phase == "screen" and out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    ctx = load_ctx(Path(args.config), out_root)
    t0 = time.time()
    print(f"=== CAMPAIGN_009 phase={args.phase} {datetime.now(UTC).isoformat()} ===")
    run_phase(ctx, args.phase)
    dt = time.time() - t0

    index_path = out_root / "_index.json"
    existing: list[dict] = []
    meta: dict = {}
    if index_path.exists():
        try:
            prev = json.loads(index_path.read_text())
            existing = prev.get("runs", [])
            meta = prev
        except Exception:
            pass
    new_labels = {r.label for r in ctx.runs}
    merged = [r for r in existing if r.get("label") not in new_labels]
    merged += [dataclasses.asdict(r) for r in ctx.runs]
    index = {
        "campaign_id": "CAMPAIGN_009",
        "generated_at": datetime.now(UTC).isoformat(),
        "git_commit": _git("rev-parse", "HEAD") or "unknown",
        "git_commit_short": (_git("rev-parse", "HEAD") or "unknown")[:12],
        "git_dirty": bool(_git("status", "--porcelain")),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD") or "unknown",
        "config_path": args.config,
        "config_hash": ctx.settings.config_hash,
        "strategy": "mean_reversion",
        "strategy_version": ctx.strategy_cfg["version"],
        "granularity": ctx.granularity,
        "data_source": REQUIRED_DATA_SOURCE,
        "risk_engine_mode": "backtest",
        "phases_run": sorted(set(meta.get("phases_run", [])) | {args.phase}),
        "total_runs": len(merged),
        "elapsed_seconds": float(meta.get("elapsed_seconds", 0.0)) + dt,
        "runs": merged,
    }
    index_path.write_text(json.dumps(index, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {index_path}")
    print(f"phase {args.phase}: {len(ctx.runs)} runs in {dt:.1f}s "
          f"(total {len(merged)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
