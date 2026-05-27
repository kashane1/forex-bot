"""Preflight checks for lower-timeframe research backtests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from forex_bot.domain.candles import CandleFrame

SUPPORTED_LTF_EXECUTION_TIMEFRAMES = {"M5", "M15"}
DEFAULT_LTF_EXECUTION_TIMEFRAME = "M15"


@dataclass(frozen=True)
class LtfBacktestPreflightResult:
    ok: bool
    errors: list[str]
    execution_timeframe: str
    next_bar_open_time: datetime | None
    time_stop_bars: int | None


def run_ltf_backtest_preflight(
    execution_frame: CandleFrame,
    *,
    signal_time: datetime | None = None,
    context_frames: dict[str, CandleFrame] | None = None,
    time_stop_bars: int | None = None,
) -> LtfBacktestPreflightResult:
    errors: list[str] = []
    if execution_frame.granularity not in SUPPORTED_LTF_EXECUTION_TIMEFRAMES:
        errors.append(f"unsupported execution timeframe: {execution_frame.granularity}")
    if execution_frame.df.empty:
        errors.append("execution frame is empty")
    if time_stop_bars is not None and time_stop_bars <= 0:
        errors.append("time_stop_bars must be positive execution bars")
    next_time = None
    if signal_time is not None and not execution_frame.df.empty:
        next_time = next_bar_open_time(execution_frame, signal_time)
        if next_time is None:
            errors.append("NEXT_BAR_OPEN_UNAVAILABLE")
    for name, frame in (context_frames or {}).items():
        if name not in {"H1", "H4", "D1AGG"}:
            errors.append(f"unsupported context timeframe: {name}")
        if frame.df.empty:
            errors.append(f"context frame empty: {name}")
        elif "complete" in frame.df.columns and not frame.df["complete"].astype(bool).any():
            errors.append(f"context frame has no completed rows: {name}")
    return LtfBacktestPreflightResult(
        ok=not errors,
        errors=errors,
        execution_timeframe=execution_frame.granularity,
        next_bar_open_time=next_time.to_pydatetime() if next_time is not None else None,
        time_stop_bars=time_stop_bars,
    )


def next_bar_open_time(frame: CandleFrame, signal_time: datetime) -> pd.Timestamp | None:
    idx = pd.DatetimeIndex(frame.df.index)
    signal_ts = pd.Timestamp(signal_time)
    if signal_ts.tzinfo is None:
        signal_ts = signal_ts.tz_localize("UTC")
    else:
        signal_ts = signal_ts.tz_convert("UTC")
    future = idx[idx > signal_ts]
    if future.empty:
        return None
    return pd.Timestamp(future[0]).tz_convert("UTC")


def time_stop_exit_index(entry_index: int, *, time_stop_bars: int, frame_length: int) -> int | None:
    if time_stop_bars <= 0:
        raise ValueError("time_stop_bars must be positive")
    exit_index = entry_index + time_stop_bars
    return exit_index if exit_index < frame_length else None
