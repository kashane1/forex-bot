#!/usr/bin/env python3
"""Infrastructure: signal_bar_close vs next_bar_open on CAMPAIGN_019 reference.

Local SQLite only. No broker. No strategy approval. No test lockbox.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.fill_timing_comparison.metrics import (
    compare_exit_reason_shares,
    count_next_bar_open_unavailable,
    entry_price_delta_pips,
    exit_reason_shares,
    fill_timing_delta,
    metrics_from_runs,
    pair_fold_delta_rows,
)

from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.fills import FillModel, FillTiming
from forex_bot.config import load_settings
from forex_bot.data.candle_dedupe import DEDUPE_POLICY
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo, InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.mean_reversion_thesis_invalidation import (
    MeanReversionThesisInvalidationStrategy,
    c008_entry_params,
)

CONFIG_PATH = ROOT / "configs/campaign_019_mean_reversion_thesis_invalidation.yaml"
C008_CONFIG = ROOT / "configs/campaign_008_range_mean_reversion.yaml"
OUT_DIR = ROOT / "research/fill_timing_reference_comparison"
LOCAL_TRADES = OUT_DIR / "local_trades"

SPLITS = ("train", "validation")
FILL_TIMINGS: tuple[FillTiming, ...] = ("signal_bar_close", "next_bar_open")
COST_BASE = {"name": "base", "spread_multiplier": 0.5, "fixed_slippage_pips": 0.2}
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


def _split_window(split: str) -> tuple[datetime, datetime]:
    windows = {
        "train": ("2020-01-01", "2022-12-31"),
        "validation": ("2023-01-01", "2024-12-31"),
    }
    frm, to = windows[split]
    return _parse(frm), _parse(to)


def validate_frozen_config(settings) -> None:
    sc = settings.strategy
    if sc.enabled != ["mean_reversion_thesis_invalidation"]:
        raise SystemExit("config must enable only mean_reversion_thesis_invalidation")
    c019 = sc.mean_reversion_thesis_invalidation.model_dump()
    c008 = load_settings(C008_CONFIG).strategy.mean_reversion.model_dump()
    if c008_entry_params(c019) != c008_entry_params(c008):
        raise SystemExit("C019 entry params diverge from C008")


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
class PairRun:
    instrument: str
    split: str
    fill_timing: str
    metrics: dict[str, Any]
    data_request_hash: str
    config_hash: str
    trades: pd.DataFrame
    rejections: pd.DataFrame


def run_one(
    *,
    settings,
    instr_repo: InstrumentRepo,
    candles: CandleRepo,
    ds: DataSourceRepo,
    risk_engine: RiskEngine,
    strategy_cfg: dict[str, Any],
    thesis_long_z: float,
    thesis_short_z: float,
    thesis_z_len: int,
    instrument: str,
    split: str,
    fill_timing: FillTiming,
    write_local_trades: bool,
) -> PairRun:
    meta = instr_repo.get(instrument)
    if meta is None:
        raise SystemExit(f"missing instrument {instrument}")
    from_dt, to_dt = _split_window(split)
    rows, _ = candles.list_with_dedupe_stats(
        instrument,
        settings.market.granularity,
        completed_only=True,
        from_time=from_dt,
        to_time=to_dt,
    )
    if not rows:
        raise SystemExit(f"no candles for {instrument} {split}")
    frame = CandleFrame.from_candles(instrument, settings.market.granularity, rows)
    source = (ds.latest_for(instrument, settings.market.granularity) or {}).get(
        "source", "unknown"
    )
    if source != REQUIRED_DATA_SOURCE:
        raise SystemExit(f"bad data source {source!r} for {instrument}")
    data_hash = compute_data_request_hash(
        instrument=instrument,
        granularity=settings.market.granularity,
        from_time=from_dt.isoformat(),
        to_time=to_dt.isoformat(),
        source=source,
        candle_count=len(rows),
    )
    engine = BacktestEngine(
        instrument=meta,
        strategy=MeanReversionThesisInvalidationStrategy(version=strategy_cfg["version"]),
        strategy_config=strategy_cfg,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(COST_BASE["fixed_slippage_pips"])),
            spread_slippage_multiplier=Decimal(str(COST_BASE["spread_multiplier"])),
        ),
        fill_timing=fill_timing,
        starting_equity=Decimal(str(settings.backtest.starting_equity_usd)),
        account_currency=settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(strategy_cfg.get("max_bars_in_trade", 40)),
        commission_per_unit=Decimal(str(settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=strategy_cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(strategy_cfg.get("atr_lookback", 14)),
        risk_engine=risk_engine,
        settings=settings,
        thesis_invalidation_enabled=True,
        thesis_invalidation_long_z=thesis_long_z,
        thesis_invalidation_short_z=thesis_short_z,
        thesis_invalidation_zscore_lookback=thesis_z_len,
    )
    result = engine.run(frame, data_request_hash=data_hash)
    trades = pd.DataFrame(
        [
            {
                "instrument": t.instrument,
                "side": t.side,
                "entry_time": t.entry_time.isoformat(),
                "exit_time": t.exit_time.isoformat(),
                "entry_price": float(t.entry_price),
                "exit_price": float(t.exit_price),
                "exit_reason": t.exit_reason,
                "r_multiple": float(t.r_multiple),
                "bars_held": t.bars_held,
                "fill_timing": t.fill_timing,
            }
            for t in result.trades
        ]
    )
    rej_rows: list[dict[str, str]] = []
    for r in result.rejected_signals:
        for code, msg in zip(
            r.rejection_codes,
            r.rejection_messages or [""] * len(r.rejection_codes),
            strict=False,
        ):
            rej_rows.append(
                {
                    "timestamp": r.timestamp.isoformat(),
                    "code": code,
                    "reason": msg,
                }
            )
    rejections = pd.DataFrame(rej_rows)
    if write_local_trades:
        LOCAL_TRADES.mkdir(parents=True, exist_ok=True)
        path = LOCAL_TRADES / f"{instrument}_{split}_{fill_timing}_trades.csv"
        trades.to_csv(path, index=False)
        rej_path = LOCAL_TRADES / f"{instrument}_{split}_{fill_timing}_rejections.csv"
        rejections.to_csv(rej_path, index=False)
    return PairRun(
        instrument=instrument,
        split=split,
        fill_timing=fill_timing,
        metrics=_metrics_to_dict(result.metrics),
        data_request_hash=data_hash,
        config_hash=result.config_hash,
        trades=trades,
        rejections=rejections,
    )


def aggregate_runs(runs: list[PairRun], split: str, fill_timing: str) -> dict[str, Any]:
    subset = [r for r in runs if r.split == split and r.fill_timing == fill_timing]
    per_pair = {r.instrument: r.metrics for r in subset}
    return metrics_from_runs(per_pair)


def build_payload(runs: list[PairRun]) -> dict[str, Any]:
    close_train = aggregate_runs(runs, "train", "signal_bar_close")
    open_train = aggregate_runs(runs, "train", "next_bar_open")
    close_val = aggregate_runs(runs, "validation", "signal_bar_close")
    open_val = aggregate_runs(runs, "validation", "next_bar_open")

    close_trades = pd.concat(
        [r.trades for r in runs if r.fill_timing == "signal_bar_close"],
        ignore_index=True,
    )
    open_trades = pd.concat(
        [r.trades for r in runs if r.fill_timing == "next_bar_open"],
        ignore_index=True,
    )
    train_close_trades = pd.concat(
        [r.trades for r in runs if r.split == "train" and r.fill_timing == "signal_bar_close"],
        ignore_index=True,
    )
    train_open_trades = pd.concat(
        [r.trades for r in runs if r.split == "train" and r.fill_timing == "next_bar_open"],
        ignore_index=True,
    )

    all_rej_open = pd.concat(
        [r.rejections for r in runs if r.fill_timing == "next_bar_open"],
        ignore_index=True,
    )

    hashes = {r.data_request_hash for r in runs}
    config_hashes = {r.config_hash for r in runs}

    return {
        "manifest": {
            "reference_campaign": "CAMPAIGN_019",
            "strategy_name": "mean_reversion_thesis_invalidation",
            "strategy_version": "0.1.0-c019",
            "strategy_evidence": False,
            "not_approved": True,
            "test_lockbox_opened": False,
            "splits": list(SPLITS),
            "cost_regime": "base",
            "dedupe_policy": DEDUPE_POLICY,
            "data_path": str(CONFIG_PATH.relative_to(ROOT)),
            "database_path": "data/campaign_002.sqlite3",
            "git_commit": _git("rev-parse", "HEAD"),
            "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "data_request_hashes_unique": sorted(hashes),
            "config_hashes_unique": sorted(config_hashes),
            "note": (
                "Only fill_timing differs between runs; C019 committed artifacts "
                "used signal_bar_close"
            ),
        },
        "signal_bar_close_metrics": {
            "train": close_train,
            "validation": close_val,
        },
        "next_bar_open_metrics": {
            "train": open_train,
            "validation": open_val,
        },
        "fill_timing_delta": {
            "train": fill_timing_delta(close_train, open_train),
            "validation": fill_timing_delta(close_val, open_val),
        },
        "exit_reason_delta": {
            "train": compare_exit_reason_shares(
                exit_reason_shares(train_close_trades),
                exit_reason_shares(train_open_trades),
            ),
            "all": compare_exit_reason_shares(
                exit_reason_shares(close_trades),
                exit_reason_shares(open_trades),
            ),
        },
        "pair_fold_delta": {
            "train": pair_fold_delta_rows(
                close_train.get("per_pair", {}),
                open_train.get("per_pair", {}),
                split="train",
            ),
            "validation": pair_fold_delta_rows(
                close_val.get("per_pair", {}),
                open_val.get("per_pair", {}),
                split="validation",
            ),
        },
        "entry_price_delta_train": entry_price_delta_pips(train_close_trades, train_open_trades),
        "next_bar_open_unavailable_rejections": count_next_bar_open_unavailable(all_rej_open),
        "c019_committed_baseline": {
            "train_expectancy_r": -0.072,
            "validation_expectancy_r": 0.0962,
            "source": "research/campaign_019/train_metrics.json",
        },
    }


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "run_manifest.json").write_text(
        json.dumps(payload["manifest"], indent=2, default=str),
        encoding="utf-8",
    )
    (OUT_DIR / "signal_bar_close_metrics.json").write_text(
        json.dumps(payload["signal_bar_close_metrics"], indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "next_bar_open_metrics.json").write_text(
        json.dumps(payload["next_bar_open_metrics"], indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "fill_timing_delta.json").write_text(
        json.dumps(payload["fill_timing_delta"], indent=2),
        encoding="utf-8",
    )
    pd.DataFrame(payload["exit_reason_delta"]["train"]).to_csv(
        OUT_DIR / "exit_reason_delta.csv", index=False
    )
    pd.DataFrame(
        payload["pair_fold_delta"]["train"] + payload["pair_fold_delta"]["validation"]
    ).to_csv(OUT_DIR / "pair_fold_delta.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill timing reference comparison")
    parser.add_argument(
        "--write-local-trades",
        action="store_true",
        help="Write per-run trade CSVs to gitignored local_trades/",
    )
    args = parser.parse_args()

    settings = load_settings(CONFIG_PATH)
    validate_frozen_config(settings)
    raw = settings.strategy.mean_reversion_thesis_invalidation.model_dump()
    strategy_cfg = {k: v for k, v in raw.items() if k != "thesis_invalidation"}
    ti = raw["thesis_invalidation"]
    db = Database(settings.app.database_path)
    instr = InstrumentRepo(db)
    candles = CandleRepo(db)
    ds = DataSourceRepo(db)
    risk_engine = RiskEngine(settings, mode="backtest")

    runs: list[PairRun] = []
    for fill_timing in FILL_TIMINGS:
        for split in SPLITS:
            for instrument in settings.market.instruments:
                print(f"Running {instrument} {split} {fill_timing}...")
                runs.append(
                    run_one(
                        settings=settings,
                        instr_repo=instr,
                        candles=candles,
                        ds=ds,
                        risk_engine=risk_engine,
                        strategy_cfg=strategy_cfg,
                        thesis_long_z=float(ti["long_exit_zscore"]),
                        thesis_short_z=float(ti["short_exit_zscore"]),
                        thesis_z_len=int(ti["zscore_lookback"]),
                        instrument=instrument,
                        split=split,
                        fill_timing=fill_timing,
                        write_local_trades=args.write_local_trades,
                    )
                )

    payload = build_payload(runs)
    write_artifacts(payload)
    print(f"Wrote compact artifacts to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
