"""Session and calendar bucketing for cost atlas."""

from __future__ import annotations

from datetime import datetime


def session_bucket(hour_utc: int) -> str:
    """UTC hour bucket aligned with campaign risk diagnostics."""
    if hour_utc >= 22 or hour_utc < 6:
        return "asian"
    if 6 <= hour_utc < 12:
        return "london"
    if 12 <= hour_utc < 16:
        return "london_ny_overlap"
    return "ny"


def weekday_name(ts: datetime) -> str:
    return ts.strftime("%A")


def is_rollover_adjacent(hour_utc: int, weekday: str) -> bool:
    """Flag bars near NY rollover (16:45–17:15 NY ≈ 21:45–22:15 UTC in EST)."""
    # H4 bar close hour heuristic: 20–23 UTC on weekdays often overlaps rollover window.
    return weekday not in ("Saturday", "Sunday") and hour_utc in (20, 21, 22, 23)


def is_weekend_adjacent(weekday: str) -> bool:
    return weekday in ("Friday", "Sunday", "Monday")
