"""Backtesting. Uses the same risk sizing model as live; fills use
bid/ask-aware prices and configurable slippage. Never fills on incomplete
candles."""

from forex_bot.backtesting.audit import AuditReport, audit_instrument, render_audit_markdown
from forex_bot.backtesting.engine import (
    BacktestEngine,
    BacktestResult,
    RejectedSignalRecord,
    compute_data_request_hash,
)
from forex_bot.backtesting.exporters import write_all, write_risk_rejections_csv
from forex_bot.backtesting.fills import FillModel
from forex_bot.backtesting.metrics import BacktestMetrics, compute_metrics
from forex_bot.backtesting.walk_forward import WalkForwardSplit, walk_forward_splits

__all__ = [
    "AuditReport",
    "BacktestEngine",
    "BacktestMetrics",
    "BacktestResult",
    "FillModel",
    "RejectedSignalRecord",
    "WalkForwardSplit",
    "audit_instrument",
    "compute_data_request_hash",
    "compute_metrics",
    "render_audit_markdown",
    "walk_forward_splits",
    "write_all",
    "write_risk_rejections_csv",
]
