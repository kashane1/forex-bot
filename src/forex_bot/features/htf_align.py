"""Strict backward-looking higher-timeframe alignment."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

HTF_UNAVAILABLE = "HTF_UNAVAILABLE"
HTF_STALE = "HTF_STALE"


def align_last_completed(
    decision_times: pd.DatetimeIndex | pd.Series,
    htf_frame: pd.DataFrame,
    value_columns: list[str],
    *,
    htf_time_column: str = "time",
    complete_column: str | None = "complete",
    max_staleness: pd.Timedelta | None = None,
    prefix: str = "htf",
) -> pd.DataFrame:
    """Align HTF values to lower-timeframe decision times.

    For each decision time, use the max ``htf_time`` where ``htf_time <= decision_time``
    and (if present) ``complete`` is true. Never uses future or incomplete HTF rows.
    """
    decision_index = pd.DatetimeIndex(decision_times)
    if decision_index.tz is None:
        decision_index = decision_index.tz_localize("UTC")
    else:
        decision_index = decision_index.tz_convert("UTC")

    htf = htf_frame.copy()
    if htf_time_column not in htf.columns:
        raise ValueError(f"missing {htf_time_column!r} in htf_frame")
    htf_times = pd.to_datetime(htf[htf_time_column], utc=True)
    if complete_column and complete_column in htf.columns:
        htf = htf.loc[htf[complete_column].astype(bool)]
    htf = htf.assign(_htf_time=htf_times).sort_values("_htf_time")

    out = pd.DataFrame(index=decision_index)
    blocked: list[str | None] = []
    stale_flags: list[bool] = []

    for ts in decision_index:
        last_time = _last_htf_time(ts, htf["_htf_time"])
        reason: str | None = None
        is_stale = False
        if last_time is None:
            reason = HTF_UNAVAILABLE
        elif max_staleness is not None and (ts - last_time) > max_staleness:
            reason = HTF_STALE
            is_stale = True
        blocked.append(reason)
        stale_flags.append(is_stale)

        for col in value_columns:
            if col not in htf.columns:
                raise ValueError(f"missing value column {col!r}")
            if last_time is None:
                out.loc[ts, f"{prefix}_{col}"] = pd.NA
                out.loc[ts, f"{prefix}_{col}_time"] = pd.NaT
            else:
                row = htf.loc[htf["_htf_time"] == last_time].iloc[-1]
                out.loc[ts, f"{prefix}_{col}"] = row[col]
                out.loc[ts, f"{prefix}_{col}_time"] = last_time

    out[f"{prefix}_blocked_reason"] = blocked
    out[f"{prefix}_is_stale"] = stale_flags
    return out


def _last_htf_time(
    decision_time: pd.Timestamp, htf_times: pd.Series
) -> pd.Timestamp | None:
    prior = htf_times[htf_times <= decision_time]
    if prior.empty:
        return None
    return pd.Timestamp(prior.iloc[-1]).tz_convert("UTC")


def validate_htf_provenance(
    decision_time: datetime,
    htf_feature_times: dict[str, datetime] | None,
) -> list[str]:
    """Return errors if any HTF feature time is after decision_time."""
    if not htf_feature_times:
        return []
    errors: list[str] = []
    dt = pd.Timestamp(decision_time)
    if dt.tzinfo is None:
        dt = dt.tz_localize("UTC")
    for name, fts in htf_feature_times.items():
        ft = pd.Timestamp(fts)
        if ft.tzinfo is None:
            ft = ft.tz_localize("UTC")
        if ft > dt:
            errors.append(f"{name}: htf time {ft} after decision {dt}")
    return errors


def validate_signal_provenance(
    *,
    decision_time: datetime | None,
    available_data_cutoff: datetime | None,
    htf_feature_times: dict[str, datetime] | None,
) -> list[str]:
    """Validate optional signal provenance timestamps."""
    errors: list[str] = []
    if decision_time is not None and available_data_cutoff is not None:
        dt = pd.Timestamp(decision_time)
        cut = pd.Timestamp(available_data_cutoff)
        if dt.tzinfo is None:
            dt = dt.tz_localize("UTC")
        if cut.tzinfo is None:
            cut = cut.tz_localize("UTC")
        if dt > cut:
            errors.append("decision_time after available_data_cutoff")
    if decision_time is not None:
        errors.extend(validate_htf_provenance(decision_time, htf_feature_times))
    return errors
