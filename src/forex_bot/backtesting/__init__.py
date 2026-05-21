"""Backtesting. Uses the same risk sizing model as live; fills use
bid/ask-aware prices and configurable slippage. Never fills on incomplete
candles."""

from forex_bot.backtesting.engine import BacktestEngine, BacktestResult
from forex_bot.backtesting.fills import FillModel
from forex_bot.backtesting.metrics import BacktestMetrics, compute_metrics
from forex_bot.backtesting.walk_forward import WalkForwardSplit, walk_forward_splits

__all__ = [
    "BacktestEngine",
    "BacktestMetrics",
    "BacktestResult",
    "FillModel",
    "WalkForwardSplit",
    "compute_metrics",
    "walk_forward_splits",
]
