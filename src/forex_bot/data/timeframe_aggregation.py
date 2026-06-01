"""Local M1 -> multi-timeframe candle aggregation for research."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Literal
from zoneinfo import ZoneInfo

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.domain.candles import Candle, Granularity

TargetGranularity = Literal["M3", "M5", "M15", "M30", "H1", "H4", "D1", "D1AGG"]
MissingPolicy = Literal["omit", "mark_incomplete"]

# M3/M30 are M1-derived research timeframes added for the CAMPAIGN_026 timeframe
# ladder. They use the identical fixed-minute bucketing rules as M5/M15/H1 (only
# the bucket size differs); see _bucket_start for the generic minute alignment.
_TARGET_MINUTES: dict[str, int] = {
    "M3": 3,
    "M5": 5,
    "M15": 15,
    "M30": 30,
    "H1": 60,
    "H4": 240,
    "D1": 1440,
}


@dataclass(frozen=True)
class AggregationCoverage:
    target_time: datetime
    expected_minutes: int
    observed_minutes: int
    complete_source_minutes: int
    missing_minutes: int


@dataclass(frozen=True)
class TimeframeAggregationResult:
    instrument: str
    source_granularity: str
    target_granularity: TargetGranularity
    candles: list[Candle]
    coverage: list[AggregationCoverage]
    omitted_incomplete_blocks: int


def aggregate_m1_candles(
    candles: Iterable[Candle],
    *,
    target: TargetGranularity,
    missing_policy: MissingPolicy = "omit",
    alignment_tz: str = "America/New_York",
    alignment_hour: int = 17,
) -> TimeframeAggregationResult:
    """Aggregate completed M1 candles into local research timeframes.

    Standard targets use bucket-start timestamps. ``D1AGG`` first creates
    strict completed H4 candles from M1 and then delegates to the existing
    H4 -> D1AGG research-day aggregator, preserving its timestamp convention.
    """
    rows = sorted(candles, key=lambda candle: candle.time)
    if not rows:
        return TimeframeAggregationResult("", "M1", target, [], [], 0)
    instruments = {candle.instrument for candle in rows}
    if len(instruments) != 1:
        raise ValueError(f"mixed instruments in input: {sorted(instruments)}")
    if any(candle.granularity != "M1" for candle in rows):
        raise ValueError("aggregate_m1_candles accepts only M1 source candles")
    if target == "D1AGG":
        h4 = aggregate_m1_candles(
            rows,
            target="H4",
            missing_policy="omit",
            alignment_tz=alignment_tz,
            alignment_hour=alignment_hour,
        )
        d1 = aggregate_h4_to_d1(
            h4.candles,
            instrument=next(iter(instruments)),
            alignment_hour=alignment_hour,
            alignment_tz=alignment_tz,
        )
        return TimeframeAggregationResult(
            instrument=d1.instrument,
            source_granularity="M1",
            target_granularity="D1AGG",
            candles=d1.candles,
            coverage=h4.coverage,
            omitted_incomplete_blocks=h4.omitted_incomplete_blocks + d1.incomplete_count + d1.ambiguous_count,
        )
    if target not in _TARGET_MINUTES:
        raise ValueError(f"unsupported target granularity: {target}")
    return _aggregate_fixed_minutes(
        rows,
        target=target,
        missing_policy=missing_policy,
        alignment_tz=alignment_tz,
        alignment_hour=alignment_hour,
    )


def _aggregate_fixed_minutes(
    rows: list[Candle],
    *,
    target: TargetGranularity,
    missing_policy: MissingPolicy,
    alignment_tz: str,
    alignment_hour: int,
) -> TimeframeAggregationResult:
    bucket_minutes = _TARGET_MINUTES[target]
    by_bucket: dict[datetime, list[Candle]] = defaultdict(list)
    for candle in rows:
        by_bucket[_bucket_start(candle.time, bucket_minutes, alignment_tz, alignment_hour)].append(candle)

    output: list[Candle] = []
    coverage: list[AggregationCoverage] = []
    omitted = 0
    for bucket_time in sorted(by_bucket):
        group = sorted(by_bucket[bucket_time], key=lambda candle: candle.time)
        expected = [bucket_time + timedelta(minutes=i) for i in range(bucket_minutes)]
        present = {candle.time for candle in group}
        complete_count = sum(1 for candle in group if candle.complete)
        missing_count = sum(1 for ts in expected if ts not in present)
        is_complete = (
            len(group) == bucket_minutes
            and missing_count == 0
            and complete_count == bucket_minutes
        )
        coverage.append(
            AggregationCoverage(
                target_time=bucket_time,
                expected_minutes=bucket_minutes,
                observed_minutes=len(group),
                complete_source_minutes=complete_count,
                missing_minutes=missing_count,
            )
        )
        if not is_complete and missing_policy == "omit":
            omitted += 1
            continue
        candle_granularity: Granularity = "D" if target == "D1" else target
        output.append(_build_candle(bucket_time, group, candle_granularity, complete=is_complete))

    return TimeframeAggregationResult(
        instrument=rows[0].instrument,
        source_granularity="M1",
        target_granularity=target,
        candles=output,
        coverage=coverage,
        omitted_incomplete_blocks=omitted,
    )


def _bucket_start(
    ts: datetime,
    bucket_minutes: int,
    alignment_tz: str,
    alignment_hour: int,
) -> datetime:
    if bucket_minutes == 240:
        return _aligned_h4_bucket_start(ts, alignment_tz, alignment_hour)
    utc = ts.astimezone(ZoneInfo("UTC"))
    minute_of_day = utc.hour * 60 + utc.minute
    bucket_minute = minute_of_day - (minute_of_day % bucket_minutes)
    return utc.replace(hour=bucket_minute // 60, minute=bucket_minute % 60, second=0, microsecond=0)


def _aligned_h4_bucket_start(ts: datetime, alignment_tz: str, alignment_hour: int) -> datetime:
    tz = ZoneInfo(alignment_tz)
    local = ts.astimezone(tz)
    anchor = local.replace(hour=alignment_hour, minute=0, second=0, microsecond=0)
    if local < anchor:
        anchor -= timedelta(days=1)
    elapsed_minutes = int((local - anchor).total_seconds() // 60)
    bucket_offset_hours = (elapsed_minutes // 240) * 4
    return (anchor + timedelta(hours=bucket_offset_hours)).astimezone(ZoneInfo("UTC"))


def _build_candle(
    bucket_time: datetime,
    group: list[Candle],
    granularity: Granularity,
    *,
    complete: bool,
) -> Candle:
    if not group:
        raise ValueError("cannot aggregate an empty candle group")
    return Candle(
        instrument=group[0].instrument,
        granularity=granularity,
        time=bucket_time,
        complete=complete,
        volume=sum(candle.volume for candle in group),
        bid_o=group[0].bid_o,
        bid_h=_max_decimal(candle.bid_h for candle in group),
        bid_l=_min_decimal(candle.bid_l for candle in group),
        bid_c=group[-1].bid_c,
        ask_o=group[0].ask_o,
        ask_h=_max_decimal(candle.ask_h for candle in group),
        ask_l=_min_decimal(candle.ask_l for candle in group),
        ask_c=group[-1].ask_c,
        mid_o=group[0].mid_o,
        mid_h=_max_decimal(candle.mid_h for candle in group),
        mid_l=_min_decimal(candle.mid_l for candle in group),
        mid_c=group[-1].mid_c,
    )


def _max_decimal(values: Iterable[Decimal | None]) -> Decimal | None:
    present = [value for value in values if value is not None]
    return max(present) if present else None


def _min_decimal(values: Iterable[Decimal | None]) -> Decimal | None:
    present = [value for value in values if value is not None]
    return min(present) if present else None
