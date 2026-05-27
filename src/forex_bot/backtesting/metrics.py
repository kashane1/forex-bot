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
    # Trailing default-with-safety fields — must remain last. Added by
    # sprint infra-exit-fidelity-001; see
    # docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md.
    # ambiguous_exit: this trade exited via an adverse stop on a bar where
    # the take-profit was ALSO in range. The engine's stop-precedence
    # tie-break (CAMPAIGN_009_PRECOMMIT.md §59) won; the flag merely
    # records that ambiguity for audit.
    ambiguous_exit: bool = False
    # gap_fill: this trade's exit was filled at the bar's open instead of
    # at the stop/tp level — only possible when gap_fill_policy ==
    # "gap_through" and the bar opened past the level.
    gap_fill: bool = False
    # gap_fill_distance_pips: absolute distance from the stop/tp level to
    # the filled bar-open, in pips. Always None when gap_fill is False.
    gap_fill_distance_pips: Decimal | None = None
    # CAMPAIGN_018 protective stop (research backtest only).
    protective_stop_armed: bool = False
    protective_stop_arm_time: datetime | None = None
    protective_stop_arm_mfe_r: float | None = None
    protective_stop_exit: bool = False
    # CAMPAIGN_019 thesis invalidation (research backtest only).
    thesis_invalidation_exit: bool = False
    zscore_at_exit: float | None = None

    def to_dict(self) -> dict[str, str | int | bool | float | None]:
        # Explicit per-field serialization. Bools and Optional[Decimal] do
        # not survive the prior `isinstance(v, int)` filter (Python: True
        # is an int) — list every field by hand so additions are visible.
        return {
            "instrument": self.instrument,
            "side": self.side,
            "units": str(self.units),
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat(),
            "entry_price": str(self.entry_price),
            "exit_price": str(self.exit_price),
            "stop_price": str(self.stop_price),
            "pnl": str(self.pnl),
            "r_multiple": str(self.r_multiple),
            "bars_held": self.bars_held,
            "spread_paid_pips": str(self.spread_paid_pips),
            "exit_reason": self.exit_reason,
            "fill_timing": self.fill_timing,
            "ambiguous_exit": self.ambiguous_exit,
            "gap_fill": self.gap_fill,
            "gap_fill_distance_pips": (
                str(self.gap_fill_distance_pips)
                if self.gap_fill_distance_pips is not None
                else None
            ),
            "protective_stop_armed": self.protective_stop_armed,
            "protective_stop_arm_time": (
                self.protective_stop_arm_time.isoformat()
                if self.protective_stop_arm_time is not None
                else None
            ),
            "protective_stop_arm_mfe_r": self.protective_stop_arm_mfe_r,
            "protective_stop_exit": self.protective_stop_exit,
            "thesis_invalidation_exit": self.thesis_invalidation_exit,
            "zscore_at_exit": self.zscore_at_exit,
        }


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
    # Trailing default-with-safety fields — must remain last. Added by
    # sprint infra-exit-fidelity-001. ambiguous_exit_count counts trades
    # where stop-precedence hid a TP that was provably in range on the
    # same bar; gap_fill_exit_count counts trades whose exit filled at
    # bar-open under gap_fill_policy="gap_through". Both default to 0
    # so prior consumers (and trades-empty backtests) keep working.
    ambiguous_exit_count: int = 0
    gap_fill_exit_count: int = 0

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
            # Trailing default fields stay at their defaults explicitly so
            # the empty-trades branch matches the populated branch's shape.
            ambiguous_exit_count=0,
            gap_fill_exit_count=0,
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
        ambiguous_exit_count=sum(1 for t in trades if t.ambiguous_exit),
        gap_fill_exit_count=sum(1 for t in trades if t.gap_fill),
    )


__all__ = ["BacktestMetrics", "TradeRecord", "_EquityBar", "compute_metrics"]
