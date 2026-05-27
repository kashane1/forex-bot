"""RiskEngine window helpers — ported from ``BacktestEngine`` for parity."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pandas as pd

from forex_bot.clock import utcnow


def realized_windows(
    ts: pd.Timestamp,
    realized: list[tuple[datetime, Decimal]],
) -> tuple[Decimal, Decimal]:
    """Calendar day + Monday-week realized PnL windows (matches bespoke engine)."""
    if not realized:
        return Decimal("0"), Decimal("0")
    now = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else utcnow()
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = day_start - pd.Timedelta(days=day_start.weekday())
    today = sum((pnl for t, pnl in realized if t >= day_start), start=Decimal("0"))
    week = sum((pnl for t, pnl in realized if t >= week_start), start=Decimal("0"))
    return today, week


def drawdown_pct(equity_points: list[tuple[datetime, float]], current_equity: float) -> Decimal:
    """Peak-to-trough drawdown percent (matches bespoke engine)."""
    if not equity_points:
        return Decimal("0")
    peak = max(e for _, e in equity_points + [(datetime.now(UTC), current_equity)])
    if peak <= 0:
        return Decimal("0")
    dd = (peak - current_equity) / peak * 100
    return Decimal(str(round(dd, 4)))
