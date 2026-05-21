"""Exporters: trades CSV, equity curve CSV, metrics JSON+MD, summary JSON.

All artifacts include the config_hash + data_request_hash so that any
downstream consumer can verify reproducibility.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from forex_bot.backtesting.engine import BacktestResult


def write_trades_csv(result: BacktestResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "instrument",
        "side",
        "units",
        "entry_time",
        "exit_time",
        "entry_price",
        "exit_price",
        "stop_price",
        "pnl",
        "r_multiple",
        "bars_held",
        "spread_paid_pips",
        "exit_reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for t in result.trades:
            writer.writerow(
                {
                    "instrument": t.instrument,
                    "side": t.side,
                    "units": str(t.units),
                    "entry_time": t.entry_time.isoformat(),
                    "exit_time": t.exit_time.isoformat(),
                    "entry_price": str(t.entry_price),
                    "exit_price": str(t.exit_price),
                    "stop_price": str(t.stop_price),
                    "pnl": str(t.pnl),
                    "r_multiple": str(t.r_multiple),
                    "bars_held": t.bars_held,
                    "spread_paid_pips": str(t.spread_paid_pips),
                    "exit_reason": t.exit_reason,
                }
            )


def write_equity_curve_csv(result: BacktestResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "equity"])
        for bar in result.equity_curve:
            writer.writerow([bar.time.isoformat(), bar.equity])


def write_metrics_json(result: BacktestResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "instrument": result.instrument,
        "strategy_name": result.strategy_name,
        "strategy_version": result.strategy_version,
        "granularity": result.granularity,
        "from_time": result.from_time,
        "to_time": result.to_time,
        "fill_model": result.fill_model_repr,
        "config_hash": result.config_hash,
        "data_request_hash": result.data_request_hash,
        "metrics": asdict(result.metrics),
        "notes": result.notes,
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def write_metrics_markdown(result: BacktestResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    m = result.metrics
    lines = [
        f"# Backtest: {result.instrument} {result.granularity} {result.strategy_name} v{result.strategy_version}",
        "",
        f"- Window: `{result.from_time}` → `{result.to_time}`",
        f"- Config hash: `{result.config_hash}`",
        f"- Data request hash: `{result.data_request_hash}`",
        f"- Fill model: `{result.fill_model_repr}`",
        "",
        "## Metrics",
        "",
        f"- Trades: **{m.trade_count}**",
        f"- Total return: **{m.total_return_pct:.2f}%**",
        f"- Final equity: **{m.final_equity:.2f}** (start {m.starting_equity:.2f})",
        f"- Max drawdown: **{m.max_drawdown_pct:.2f}%** "
        f"({m.max_drawdown_duration_bars} bars)",
        f"- Sharpe: **{m.sharpe:.2f}**, Sortino: **{m.sortino:.2f}**",
        f"- Profit factor: **{_fmt_pf(m.profit_factor)}**",
        f"- Expectancy R: **{m.expectancy_r:.3f}**",
        f"- Average R: **{m.average_r:.3f}**, Median R: **{m.median_r:.3f}**",
        f"- Win rate: **{m.win_rate * 100:.1f}%**",
        f"- Average win: **{m.average_win:.4f}**, Average loss: **{m.average_loss:.4f}**",
        f"- Largest single loss: **{m.largest_single_loss:.4f}**",
        f"- Average spread paid: **{m.average_spread_paid_pips:.2f} pips**",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary_json(result: BacktestResult, path: Path, **extras: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "instrument": result.instrument,
        "strategy_name": result.strategy_name,
        "strategy_version": result.strategy_version,
        "granularity": result.granularity,
        "from_time": result.from_time,
        "to_time": result.to_time,
        "config_hash": result.config_hash,
        "data_request_hash": result.data_request_hash,
        "fill_model": result.fill_model_repr,
        "metrics": asdict(result.metrics),
        **extras,
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def write_all(result: BacktestResult, export_dir: Path, prefix: str) -> dict[str, Path]:
    export_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "trades_csv": export_dir / f"{prefix}_trades.csv",
        "equity_csv": export_dir / f"{prefix}_equity.csv",
        "metrics_json": export_dir / f"{prefix}_metrics.json",
        "metrics_md": export_dir / f"{prefix}_metrics.md",
        "summary_json": export_dir / f"{prefix}_summary.json",
    }
    write_trades_csv(result, paths["trades_csv"])
    write_equity_curve_csv(result, paths["equity_csv"])
    write_metrics_json(result, paths["metrics_json"])
    write_metrics_markdown(result, paths["metrics_md"])
    write_summary_json(result, paths["summary_json"])
    return paths


def _fmt_pf(value: float) -> str:
    if value == float("inf"):
        return "inf"
    return f"{value:.2f}"
