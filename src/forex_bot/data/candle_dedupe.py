"""Canonical candle deduplication at the repository load boundary.

The local H4 store may contain two rows per bar when an earlier fetch
stored a local-offset ISO timestamp and a later refresh stored the same
bar at UTC. Backtrader CSV exports dedupe by UTC timestamp with
keep='last'; bespoke loads must match.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from forex_bot.domain.candles import Candle, Granularity

DEDUPE_POLICY = "keep_last"


@dataclass(frozen=True)
class CandleDedupeStats:
    raw_count: int
    deduped_count: int
    duplicates_detected: int
    duplicates_dropped: int
    dedupe_policy: str = DEDUPE_POLICY

    @classmethod
    def empty(cls) -> CandleDedupeStats:
        return cls(
            raw_count=0,
            deduped_count=0,
            duplicates_detected=0,
            duplicates_dropped=0,
        )


def candle_utc_time(candle: Candle) -> datetime:
    if candle.time.tzinfo is None:
        return candle.time.replace(tzinfo=UTC)
    return candle.time.astimezone(UTC)


def dedupe_candles(candles: list[Candle]) -> tuple[list[Candle], CandleDedupeStats]:
    """Return unique candles keyed by instrument + granularity + UTC time.

    Last row in input order wins (keep='last'). Output is monotonic by
    UTC timestamp.
    """
    if not candles:
        return [], CandleDedupeStats.empty()

    raw_count = len(candles)
    by_key: dict[tuple[str, Granularity, datetime], Candle] = {}
    for candle in candles:
        key = (candle.instrument, candle.granularity, candle_utc_time(candle))
        by_key[key] = candle

    deduped = sorted(by_key.values(), key=candle_utc_time)
    deduped_count = len(deduped)
    dropped = raw_count - deduped_count
    return deduped, CandleDedupeStats(
        raw_count=raw_count,
        deduped_count=deduped_count,
        duplicates_detected=dropped,
        duplicates_dropped=dropped,
    )
