"""Data audit. Reads stored candles for one instrument×granularity×window
and reports completeness/quality issues that would invalidate a backtest."""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from forex_bot.data.repositories import CandleRepo
from forex_bot.domain.candles import Granularity

GRANULARITY_SECONDS: dict[str, int] = {
    "M1": 60,
    "M5": 300,
    "M15": 900,
    "M30": 1800,
    "H1": 3600,
    "H4": 14400,
    "D": 86400,
}


@dataclass
class AuditReport:
    instrument: str
    granularity: str
    requested_from: datetime | None
    requested_to: datetime | None
    first_ts: datetime | None
    last_ts: datetime | None
    candle_count: int
    completed_count: int
    incomplete_count: int
    bid_available_count: int
    ask_available_count: int
    missing_intervals: list[tuple[datetime, datetime, int]] = field(default_factory=list)
    duplicate_timestamps: list[datetime] = field(default_factory=list)
    abnormal_spreads: list[tuple[datetime, float]] = field(default_factory=list)
    weekend_gaps: list[tuple[datetime, datetime, int]] = field(default_factory=list)
    median_spread_pips: float | None = None
    p95_spread_pips: float | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return (
            not self.missing_intervals
            and not self.duplicate_timestamps
            and not self.abnormal_spreads
            and self.incomplete_count == 0
            and self.candle_count > 0
            and self.bid_available_count == self.candle_count
            and self.ask_available_count == self.candle_count
        )


def audit_instrument(
    repo: CandleRepo,
    instrument: str,
    granularity: Granularity,
    *,
    requested_from: datetime | None = None,
    requested_to: datetime | None = None,
    pip_size: Decimal,
    abnormal_spread_multiplier: float = 5.0,
    weekend_gap_min_hours: int = 24,
) -> AuditReport:
    candles = repo.list(instrument, granularity, completed_only=False)
    if requested_from is not None:
        candles = [c for c in candles if c.time >= requested_from]
    if requested_to is not None:
        candles = [c for c in candles if c.time <= requested_to]

    report = AuditReport(
        instrument=instrument,
        granularity=granularity,
        requested_from=requested_from,
        requested_to=requested_to,
        first_ts=candles[0].time if candles else None,
        last_ts=candles[-1].time if candles else None,
        candle_count=len(candles),
        completed_count=sum(1 for c in candles if c.complete),
        incomplete_count=sum(1 for c in candles if not c.complete),
        bid_available_count=sum(
            1 for c in candles if c.bid_c is not None and c.bid_o is not None
        ),
        ask_available_count=sum(
            1 for c in candles if c.ask_c is not None and c.ask_o is not None
        ),
    )

    if not candles:
        report.notes.append("no candles in window")
        return report

    # ---- duplicates ----
    seen: set[datetime] = set()
    dups: list[datetime] = []
    for c in candles:
        if c.time in seen:
            dups.append(c.time)
        seen.add(c.time)
    report.duplicate_timestamps = dups

    # ---- missing intervals (gaps strictly larger than 1 granularity unit) ----
    step = timedelta(seconds=GRANULARITY_SECONDS.get(granularity, 0))
    if step > timedelta(0):
        sorted_candles = sorted(candles, key=lambda c: c.time)
        for prev, curr in zip(sorted_candles, sorted_candles[1:], strict=False):
            delta = curr.time - prev.time
            if delta > step * 1.5:
                expected_bars = int(delta / step) - 1
                if delta >= timedelta(hours=weekend_gap_min_hours) and _spans_weekend(
                    prev.time, curr.time
                ):
                    report.weekend_gaps.append((prev.time, curr.time, expected_bars))
                else:
                    report.missing_intervals.append((prev.time, curr.time, expected_bars))

    # ---- spread stats + abnormal ----
    spreads: list[float] = []
    for c in candles:
        if c.bid_c is not None and c.ask_c is not None:
            spread = float((c.ask_c - c.bid_c) / pip_size)
            spreads.append(spread)
    if spreads:
        report.median_spread_pips = statistics.median(spreads)
        report.p95_spread_pips = float(
            statistics.quantiles(spreads, n=20)[18]
            if len(spreads) > 20
            else max(spreads)
        )
        threshold = report.median_spread_pips * abnormal_spread_multiplier
        for c, s in zip(candles, spreads, strict=True):
            if s > threshold:
                report.abnormal_spreads.append((c.time, s))

    return report


def _spans_weekend(start: datetime, end: datetime) -> bool:
    """Treat gaps that include Saturday as weekend gaps."""
    cursor = start
    while cursor <= end:
        if cursor.weekday() == 5:  # Saturday
            return True
        cursor += timedelta(days=1)
    return False


def render_audit_markdown(report: AuditReport) -> str:
    def _trunc(items: list, limit: int = 8) -> tuple[list, str]:
        if len(items) <= limit:
            return items, ""
        return items[:limit], f"\n_(+{len(items) - limit} more)_"

    lines = [
        f"## Audit: {report.instrument} {report.granularity}",
        "",
        f"- Requested window: `{report.requested_from}` → `{report.requested_to}`",
        f"- First/last timestamp: `{report.first_ts}` → `{report.last_ts}`",
        f"- Candle count: **{report.candle_count}** "
        f"(complete={report.completed_count}, incomplete={report.incomplete_count})",
        f"- Bid availability: **{report.bid_available_count}/{report.candle_count}**",
        f"- Ask availability: **{report.ask_available_count}/{report.candle_count}**",
        f"- Median spread (pips): "
        f"{report.median_spread_pips:.2f}" if report.median_spread_pips is not None else "n/a",
        f"- p95 spread (pips): "
        f"{report.p95_spread_pips:.2f}" if report.p95_spread_pips is not None else "n/a",
        f"- Duplicate timestamps: **{len(report.duplicate_timestamps)}**",
        f"- Missing intervals (non-weekend): **{len(report.missing_intervals)}**",
        f"- Weekend gaps: **{len(report.weekend_gaps)}**",
        f"- Abnormal spreads (> {5}× median): **{len(report.abnormal_spreads)}**",
        f"- Clean: **{report.is_clean}**",
        "",
    ]
    if report.missing_intervals:
        shown, more = _trunc(report.missing_intervals)
        lines.append("### Missing intervals (sample)")
        for start, end, bars in shown:
            lines.append(f"- `{start.isoformat()}` → `{end.isoformat()}` ({bars} bars)")
        lines.append(more)
    if report.abnormal_spreads:
        shown, more = _trunc(report.abnormal_spreads)
        lines.append("\n### Abnormal spreads (sample)")
        for ts, spread in shown:
            lines.append(f"- `{ts.isoformat()}` — {spread:.2f} pips")
        lines.append(more)
    if report.notes:
        lines.append("\n### Notes")
        for n in report.notes:
            lines.append(f"- {n}")
    return "\n".join(lines)
