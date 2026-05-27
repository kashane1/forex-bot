"""Lower-timeframe execution to completed HTF context alignment."""

from __future__ import annotations

import pandas as pd

from forex_bot.features.htf_align import align_last_completed

DEFAULT_EXECUTION_TIMEFRAME = "M15"
SUPPORTED_EXECUTION_TIMEFRAMES = {"M5", "M15"}
SUPPORTED_CONTEXT_TIMEFRAMES = {"H1", "H4", "D1AGG"}


def align_ltf_execution_context(
    decision_times: pd.DatetimeIndex | pd.Series,
    *,
    execution_timeframe: str = DEFAULT_EXECUTION_TIMEFRAME,
    h1_frame: pd.DataFrame | None = None,
    h4_frame: pd.DataFrame | None = None,
    d1agg_frame: pd.DataFrame | None = None,
    value_columns: list[str] | None = None,
    max_staleness: pd.Timedelta | None = None,
) -> pd.DataFrame:
    """Align completed H1/H4/D1AGG features to M5/M15 decisions."""
    if execution_timeframe not in SUPPORTED_EXECUTION_TIMEFRAMES:
        raise ValueError(f"unsupported execution timeframe: {execution_timeframe}")
    columns = value_columns or ["value"]
    decision_index = pd.DatetimeIndex(decision_times)
    if decision_index.tz is None:
        decision_index = decision_index.tz_localize("UTC")
    else:
        decision_index = decision_index.tz_convert("UTC")
    out = pd.DataFrame(index=decision_index)
    out["execution_timeframe"] = execution_timeframe
    out["available_data_cutoff"] = decision_index
    for prefix, frame in (("h1", h1_frame), ("h4", h4_frame), ("d1agg", d1agg_frame)):
        if frame is None:
            continue
        frame = _completed_only(frame)
        aligned = align_last_completed(
            decision_index,
            frame,
            columns,
            max_staleness=max_staleness,
            prefix=prefix,
        )
        out = out.join(aligned)
        time_col = f"{prefix}_{columns[0]}_time"
        if time_col in out.columns:
            out[f"{prefix}_feature_time"] = out[time_col]
    return out


def _completed_only(frame: pd.DataFrame) -> pd.DataFrame:
    if "complete" not in frame.columns:
        return frame
    return frame.loc[frame["complete"].astype(bool)].copy()
