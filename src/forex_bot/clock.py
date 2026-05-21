"""Time utilities. Centralised so tests can freeze and inject a clock."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

UTC_TZ = UTC

Clock = Callable[[], datetime]


def utcnow() -> datetime:
    return datetime.now(UTC_TZ)


def to_zone(dt: datetime, tz_name: str) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    return dt.astimezone(ZoneInfo(tz_name))


def parse_rfc3339(value: str) -> datetime:
    """Parse OANDA RFC3339 timestamps. OANDA may suffix nanoseconds; trim."""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    if "." in value:
        head, dot, tail = value.partition(".")
        frac, sep, tz = tail.partition("+")
        if not sep:
            frac, sep, tz = tail.partition("-")
            if sep:
                sep = "-"
        frac = frac[:6]
        if sep:
            value = f"{head}.{frac}{sep}{tz}"
        else:
            value = f"{head}.{frac}"
    return datetime.fromisoformat(value)
