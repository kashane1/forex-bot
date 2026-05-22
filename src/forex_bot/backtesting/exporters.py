"""Exporters: trades CSV, equity curve CSV, metrics JSON+MD, summary JSON,
and per-signal risk rejections CSV.

All artifacts include the config_hash + data_request_hash so that any
downstream consumer can verify reproducibility. The risk-rejections
export is permanent infrastructure (added for CAMPAIGN_003): every
backtest run that wires in the RiskEngine emits one row per
(rejected signal, rejection code) so future reports can analyze
rejections by pair / timeframe / split / hour / day / code.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import UTC
from pathlib import Path
from typing import Any

from forex_bot.backtesting.engine import BacktestResult

_DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _session_label(hour_utc: int) -> str:
    if hour_utc >= 21 or hour_utc < 6:
        return "Asia/late"
    if hour_utc < 12:
        return "London"
    if hour_utc < 16:
        return "London/NY overlap"
    return "NY"


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
        "fill_timing",
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
                    "fill_timing": t.fill_timing,
                }
            )


def write_risk_rejections_csv(
    result: BacktestResult, path: Path, *, split: str | None = None
) -> None:
    """One row per (rejected signal, rejection code).

    Columns are deliberately analysis-ready: pair / timeframe / split /
    strategy version / side / code / reason / spread / ATR / hour / day /
    session. No credentials, account IDs, or tokens are written — the
    only free-text field is the RiskEngine's own rejection reason string,
    which never contains secrets.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "timestamp",
        "instrument",
        "granularity",
        "split",
        "strategy_version",
        "side",
        "rejection_code",
        "rejection_reason",
        "spread_pips",
        "atr_pips",
        "stop_distance_pips",
        "hour_utc",
        "day_of_week",
        "session",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for rej in result.rejected_signals:
            ts = rej.timestamp.astimezone(UTC)
            # Pair each code with its message positionally; fall back to "".
            codes = rej.rejection_codes or [""]
            for idx, code in enumerate(codes):
                reason = (
                    rej.rejection_messages[idx]
                    if idx < len(rej.rejection_messages)
                    else ""
                )
                writer.writerow(
                    {
                        "timestamp": rej.timestamp.isoformat(),
                        "instrument": rej.instrument,
                        "granularity": rej.granularity,
                        "split": split or "",
                        "strategy_version": result.strategy_version,
                        "side": rej.side,
                        "rejection_code": code,
                        "rejection_reason": reason,
                        "spread_pips": "" if rej.spread_pips is None else str(rej.spread_pips),
                        "atr_pips": "" if rej.atr_pips is None else str(rej.atr_pips),
                        "stop_distance_pips": (
                            "" if rej.stop_distance_pips is None
                            else str(rej.stop_distance_pips)
                        ),
                        "hour_utc": ts.hour,
                        "day_of_week": _DOW[ts.weekday()],
                        "session": _session_label(ts.hour),
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
        "fill_timing": result.fill_timing,
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
        f"- Fill timing: `{result.fill_timing}`",
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
        "fill_timing": result.fill_timing,
        "metrics": asdict(result.metrics),
        **extras,
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def write_all(
    result: BacktestResult,
    export_dir: Path,
    prefix: str,
    *,
    split: str | None = None,
) -> dict[str, Path]:
    export_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "trades_csv": export_dir / f"{prefix}_trades.csv",
        "equity_csv": export_dir / f"{prefix}_equity.csv",
        "metrics_json": export_dir / f"{prefix}_metrics.json",
        "metrics_md": export_dir / f"{prefix}_metrics.md",
        "summary_json": export_dir / f"{prefix}_summary.json",
        "risk_rejections_csv": export_dir / f"{prefix}_risk_rejections.csv",
    }
    write_trades_csv(result, paths["trades_csv"])
    write_equity_curve_csv(result, paths["equity_csv"])
    write_metrics_json(result, paths["metrics_json"])
    write_metrics_markdown(result, paths["metrics_md"])
    write_summary_json(result, paths["summary_json"])
    # Risk rejections are always emitted (empty file with header if the run
    # used no RiskEngine), so downstream tooling can rely on the path.
    write_risk_rejections_csv(result, paths["risk_rejections_csv"], split=split)
    return paths


def _fmt_pf(value: float) -> str:
    if value == float("inf"):
        return "inf"
    return f"{value:.2f}"
