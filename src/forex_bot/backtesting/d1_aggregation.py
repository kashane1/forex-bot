"""H4 -> D1 candle aggregation for valid daily-timeframe research.

CAMPAIGN_006 established that native OANDA D1 candles cannot be validly
backtested by this engine: a D1 candle closes at the 17:00 NY rollover,
so its timestamp lands inside the session-filter blackout and its close
spread is the (abnormally wide) rollover spread. A whole timeframe was
therefore untestable.

This module builds *synthetic* daily candles by aggregating real,
already-validated OANDA H4 bid/ask candles. The key idea: the synthetic
daily bar covers a 20-hour "research day" — the first five H4 candles of
an OANDA trading day (17:00 -> 13:00 NY) — and is timestamped at its
close (13:00 NY). It deliberately excludes the sixth, rollover-adjacent
H4 candle (13:00 -> 17:00 NY). The result is a daily bar whose timestamp
and close spread both sit in liquid hours, well clear of the rollover
blackout.

The aggregated granularity is tagged ``D1AGG`` so it can never be
confused with native OANDA ``D``. Future daily-timeframe research MUST
use this aggregate source, not raw OANDA D1.

This module runs no strategy logic and produces no trading result.
See docs/research/D1_AGGREGATION_DESIGN.md.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from forex_bot.domain.candles import Candle

AGG_GRANULARITY = "D1AGG"
_H4_PER_TRADING_DAY = 6  # a well-formed OANDA trading day
_RESEARCH_CANDLES = 5  # the first five: 17:00 -> 13:00 NY
_BLACKOUT_START = time(16, 45)  # NY — the session-filter `rollover` window
_BLACKOUT_END = time(17, 15)


@dataclass(frozen=True)
class D1DayReport:
    """Classification of one OANDA trading day seen in the input.

    status is one of:
      * "aggregated" — a clean D1AGG candle was produced;
      * "incomplete" — fewer than 6 complete H4 candles (holiday, data
        gap, or a partial day at the range boundary); no candle emitted;
      * "ambiguous"  — 6 candles present but their slots / bid-ask data
        are not well-formed; no candle emitted.
    """

    trading_day: date
    status: str
    h4_complete_count: int
    note: str


@dataclass(frozen=True)
class D1AggregationResult:
    instrument: str
    alignment_hour: int
    alignment_tz: str
    candles: list[Candle]  # clean D1AGG candles (one per "aggregated" day)
    day_reports: list[D1DayReport]  # every trading-day group, classified
    missing_weekdays: list[date]  # weekdays in span with NO H4 data at all
    source_h4_count: int
    source_hash: str

    @property
    def aggregated_count(self) -> int:
        return sum(1 for r in self.day_reports if r.status == "aggregated")

    @property
    def incomplete_count(self) -> int:
        return sum(1 for r in self.day_reports if r.status == "incomplete")

    @property
    def ambiguous_count(self) -> int:
        return sum(1 for r in self.day_reports if r.status == "ambiguous")


def rollover_safe(
    dt: datetime,
    *,
    alignment_tz: str = "America/New_York",
    blackout_start: time = _BLACKOUT_START,
    blackout_end: time = _BLACKOUT_END,
) -> bool:
    """True if ``dt`` does not fall inside the NY rollover blackout window.

    A synthetic daily candle is only validly backtestable if its
    timestamp clears this window — the exact contamination that made
    native OANDA D1 untestable in CAMPAIGN_006.
    """
    ny = dt.astimezone(ZoneInfo(alignment_tz)).time()
    return not (blackout_start <= ny <= blackout_end)


def aggregate_h4_to_d1(
    h4_candles: list[Candle],
    *,
    alignment_hour: int = 17,
    alignment_tz: str = "America/New_York",
    instrument: str | None = None,
) -> D1AggregationResult:
    """Aggregate completed H4 candles into D1AGG research candles.

    Only complete H4 candles are used. A trading day yields a D1AGG
    candle only if it has all six well-formed H4 candles; otherwise it is
    classified (incomplete / ambiguous) and recorded but not emitted.
    Weekend gaps are simply absent (no trading day); weekday gaps are
    reported in ``missing_weekdays``.
    """
    for c in h4_candles:
        if c.granularity != "H4":
            raise ValueError(
                "aggregate_h4_to_d1 accepts only H4 candles; got "
                f"granularity={c.granularity!r}"
            )
    data_instruments = {c.instrument for c in h4_candles}
    if len(data_instruments) > 1:
        raise ValueError(f"mixed instruments in input: {sorted(data_instruments)}")
    inst = instrument or (next(iter(data_instruments)) if data_instruments else "")

    source_hash = _hash_h4(h4_candles)

    # Group complete H4 candles by OANDA trading day (alignment_hour NY).
    by_day: dict[date, list[Candle]] = defaultdict(list)
    for c in h4_candles:
        if not c.complete:
            continue
        ny = c.time.astimezone(ZoneInfo(alignment_tz))
        trading_day = (
            ny.date() + timedelta(days=1) if ny.hour >= alignment_hour else ny.date()
        )
        by_day[trading_day].append(c)

    candles: list[Candle] = []
    reports: list[D1DayReport] = []
    for trading_day in sorted(by_day):
        group = sorted(by_day[trading_day], key=lambda c: c.time)
        report, d1 = _aggregate_day(
            trading_day, group, inst, alignment_hour, alignment_tz
        )
        reports.append(report)
        if d1 is not None:
            candles.append(d1)

    return D1AggregationResult(
        instrument=inst,
        alignment_hour=alignment_hour,
        alignment_tz=alignment_tz,
        candles=candles,
        day_reports=reports,
        missing_weekdays=_missing_weekdays(sorted(by_day)),
        source_h4_count=len(h4_candles),
        source_hash=source_hash,
    )


def _aggregate_day(
    trading_day: date,
    group: list[Candle],
    instrument: str,
    alignment_hour: int,
    alignment_tz: str,
) -> tuple[D1DayReport, Candle | None]:
    n = len(group)
    if n != _H4_PER_TRADING_DAY:
        status = "incomplete" if n < _H4_PER_TRADING_DAY else "ambiguous"
        return (
            D1DayReport(
                trading_day, status, n,
                f"expected {_H4_PER_TRADING_DAY} complete H4 candles, found {n}",
            ),
            None,
        )

    tz = ZoneInfo(alignment_tz)
    ny_hours = [c.time.astimezone(tz).hour for c in group]
    expected = [(alignment_hour + 4 * k) % 24 for k in range(_H4_PER_TRADING_DAY)]
    if ny_hours != expected:
        return (
            D1DayReport(
                trading_day, "ambiguous", n,
                f"H4 slot hours {ny_hours} != expected {expected}",
            ),
            None,
        )

    research = group[:_RESEARCH_CANDLES]
    # group[_RESEARCH_CANDLES] is the rollover-adjacent H4 candle (13:00 ->
    # 17:00 NY). It is excluded from OHLC; only its open time is used, as
    # the research day's close timestamp (13:00 NY).
    rollover_candle = group[_RESEARCH_CANDLES]
    if any(_missing_bid_ask(c) for c in research):
        return (
            D1DayReport(
                trading_day, "ambiguous", n,
                "an H4 candle is missing bid/ask OHLC",
            ),
            None,
        )

    d1 = _build_d1(rollover_candle.time, research, instrument)
    if not rollover_safe(d1.time, alignment_tz=alignment_tz):
        # Defensive — by construction this cannot happen, but never emit a
        # candle whose timestamp would re-introduce the CAMPAIGN_006 bug.
        return (
            D1DayReport(
                trading_day, "ambiguous", n,
                "aggregated timestamp fell inside the rollover blackout",
            ),
            None,
        )
    return D1DayReport(trading_day, "aggregated", n, "ok"), d1


def _build_d1(
    close_time: datetime, research: list[Candle], instrument: str
) -> Candle:
    """Build one D1AGG candle from the five research H4 candles.

    All five are guaranteed (by the caller) to carry full bid/ask OHLC.
    """
    bid_h = [c.bid_h for c in research if c.bid_h is not None]
    bid_l = [c.bid_l for c in research if c.bid_l is not None]
    ask_h = [c.ask_h for c in research if c.ask_h is not None]
    ask_l = [c.ask_l for c in research if c.ask_l is not None]
    return Candle(
        instrument=instrument,
        granularity=AGG_GRANULARITY,
        time=close_time,
        complete=True,
        volume=sum(c.volume for c in research),
        bid_o=research[0].bid_o,
        bid_h=max(bid_h),
        bid_l=min(bid_l),
        bid_c=research[-1].bid_c,
        ask_o=research[0].ask_o,
        ask_h=max(ask_h),
        ask_l=min(ask_l),
        ask_c=research[-1].ask_c,
    )


def _missing_bid_ask(c: Candle) -> bool:
    return None in (
        c.bid_o, c.bid_h, c.bid_l, c.bid_c,
        c.ask_o, c.ask_h, c.ask_l, c.ask_c,
    )


def _missing_weekdays(days: list[date]) -> list[date]:
    """Weekdays inside the spanned range that have no trading day at all —
    holidays or data gaps. Weekends are never expected and never flagged."""
    if not days:
        return []
    present = set(days)
    out: list[date] = []
    cursor = days[0]
    while cursor <= days[-1]:
        if cursor.weekday() < 5 and cursor not in present:
            out.append(cursor)
        cursor += timedelta(days=1)
    return out


def _hash_h4(candles: list[Candle]) -> str:
    """Deterministic provenance hash over the input H4 candles."""
    hasher = hashlib.sha256()
    for c in sorted(candles, key=lambda c: c.time):
        hasher.update(
            "|".join(
                str(x) for x in (
                    c.instrument, c.granularity, c.time.isoformat(), c.complete,
                    c.volume, c.bid_o, c.bid_h, c.bid_l, c.bid_c,
                    c.ask_o, c.ask_h, c.ask_l, c.ask_c,
                )
            ).encode("utf-8")
        )
    return hasher.hexdigest()
