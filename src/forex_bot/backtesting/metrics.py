"""Backtest metrics. All metrics are derived from the trade list and
equity curve. Sharpe/Sortino use simple daily aggregation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal

import numpy as np
import pandas as pd


@dataclass
class TradeRecord:
    instrument: str
    side: str
    units: Decimal
    entry_time: datetime
    exit_time: datetime
    entry_price: Decimal
    exit_price: Decimal
    stop_price: Decimal
    pnl: Decimal
    r_multiple: Decimal
    bars_held: int
    spread_paid_pips: Decimal
    exit_reason: str
    # Which bar the entry filled against — see forex_bot.backtesting.fills.
    fill_timing: str = "signal_bar_close"

    def to_dict(self) -> dict[str, str | int]:
        d = {k: str(v) for k, v in asdict(self).items() if not isinstance(v, int)}
        d["bars_held"] = self.bars_held
        return d


@dataclass
class BacktestMetrics:
    total_return_pct: float
    final_equity: float
    starting_equity: float
    max_drawdown_pct: float
    max_drawdown_duration_bars: int
    sharpe: float
    sortino: float
    profit_factor: float
    expectancy_r: float
    average_r: float
    median_r: float
    win_rate: float
    average_win: float
    average_loss: float
    trade_count: int
    largest_single_loss: float
    average_spread_paid_pips: float
    exposure_pct: float = 0.0

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass
class _EquityBar:
    time: datetime
    equity: float


def compute_metrics(
    trades: list[TradeRecord],
    equity_curve: list[_EquityBar],
    starting_equity: float,
) -> BacktestMetrics:
    if not trades:
        return BacktestMetrics(
            total_return_pct=0.0,
            final_equity=starting_equity,
            starting_equity=starting_equity,
            max_drawdown_pct=0.0,
            max_drawdown_duration_bars=0,
            sharpe=0.0,
            sortino=0.0,
            profit_factor=0.0,
            expectancy_r=0.0,
            average_r=0.0,
            median_r=0.0,
            win_rate=0.0,
            average_win=0.0,
            average_loss=0.0,
            trade_count=0,
            largest_single_loss=0.0,
            average_spread_paid_pips=0.0,
        )

    pnls = np.array([float(t.pnl) for t in trades])
    r_values = np.array([float(t.r_multiple) for t in trades])
    spreads = np.array([float(t.spread_paid_pips) for t in trades])
    wins = pnls[pnls > 0]
    losses = pnls[pnls < 0]

    equity_series = pd.Series(
        [b.equity for b in equity_curve],
        index=pd.to_datetime([b.time for b in equity_curve], utc=True),
    ).sort_index()
    if equity_series.empty:
        equity_series = pd.Series([starting_equity])

    running_max = equity_series.cummax()
    drawdown = (equity_series - running_max) / running_max
    max_dd = float(drawdown.min()) if not drawdown.empty else 0.0

    # Drawdown duration in bars (count consecutive non-new-highs).
    duration = 0
    max_duration = 0
    for value in drawdown.tolist():
        if value < 0:
            duration += 1
            max_duration = max(max_duration, duration)
        else:
            duration = 0

    daily = equity_series.resample("D").last().dropna().pct_change().dropna()
    if len(daily) > 1 and daily.std(ddof=0) > 0:
        sharpe = float(daily.mean() / daily.std(ddof=0) * np.sqrt(252))
        downside = daily[daily < 0]
        sortino = (
            float(daily.mean() / downside.std(ddof=0) * np.sqrt(252))
            if len(downside) > 1 and downside.std(ddof=0) > 0
            else 0.0
        )
    else:
        sharpe = 0.0
        sortino = 0.0

    profit_sum = float(wins.sum())
    loss_sum = float(-losses.sum())
    profit_factor = profit_sum / loss_sum if loss_sum > 0 else float("inf") if profit_sum > 0 else 0.0

    return BacktestMetrics(
        total_return_pct=float((equity_series.iloc[-1] / starting_equity - 1) * 100),
        final_equity=float(equity_series.iloc[-1]),
        starting_equity=starting_equity,
        max_drawdown_pct=float(max_dd * 100),
        max_drawdown_duration_bars=max_duration,
        sharpe=sharpe,
        sortino=sortino,
        profit_factor=profit_factor,
        expectancy_r=float(r_values.mean()),
        average_r=float(r_values.mean()),
        median_r=float(np.median(r_values)),
        win_rate=float(len(wins) / len(pnls)),
        average_win=float(wins.mean()) if len(wins) else 0.0,
        average_loss=float(losses.mean()) if len(losses) else 0.0,
        trade_count=len(trades),
        largest_single_loss=float(losses.min()) if len(losses) else 0.0,
        average_spread_paid_pips=float(spreads.mean()) if len(spreads) else 0.0,
    )


__all__ = ["BacktestMetrics", "TradeRecord", "_EquityBar", "compute_metrics"]
