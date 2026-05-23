"""Per-day rollover-event calculator.

Pure functions over local inputs. Given a ``PositionInterval``, a
``FinancingRateSource``, and a ``FinancingCalculatorConfig``,
``calculate_position`` returns a ``PositionFinancingSummary``.
``calculate_run`` aggregates many positions into a
``FinancingRunReport``.

No I/O, no network, no clock reads (except an injectable ``now``
on ``calculate_run`` defaulting to the protocol's deterministic
default).

See ``docs/research/FINANCING_MODEL_PROTOCOL.md`` for the
convention.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

from research.financing.models import (
    DailyFinancingEvent,
    FinancingCalculatorConfig,
    FinancingRunReport,
    FinancingTreatment,
    MissingRatePolicy,
    PositionFinancingSummary,
    PositionInterval,
    RatePair,
)
from research.financing.rates import FinancingRateSource

_DAYS_PER_YEAR = 365


class MissingFinancingRateError(Exception):
    """Raised by ``calculate_position`` when the rate source returns
    None and ``missing_rate_policy == ERROR``."""


def _rollover_dates(
    interval: PositionInterval,
    config: FinancingCalculatorConfig,
) -> list[date]:
    """Every UTC date ``d`` such that the rollover moment of ``d``
    falls strictly inside ``(open_time, close_time)``, after the
    weekend-skip filter."""

    rollover_t = time(hour=config.rollover_hour_utc, tzinfo=UTC)
    dates: list[date] = []
    # Start from open_time's date; iterate while the rollover
    # candidate has not passed close_time.
    cur = interval.open_time.date()
    end = interval.close_time.date()
    while cur <= end:
        candidate = datetime.combine(cur, rollover_t)
        if interval.open_time < candidate < interval.close_time:
            if not (config.skip_weekends and cur.weekday() >= 5):
                dates.append(cur)
        cur += timedelta(days=1)
    return dates


def _notional_home(interval: PositionInterval) -> tuple[float, list[str]]:
    """Position notional in home currency, plus per-event notes
    if a cross-pair fallback fires.

    v1 supports:
    * home == quote → notional = units * entry_price
    * home == base  → notional = units (already home-denominated)
    * cross-pair    → conservative fallback, notional = units (a
                      stand-in that lets the conservative debit
                      still fire); flagged via the returned note
                      list and consumed by the caller.
    """
    notes: list[str] = []
    home = interval.home_currency
    if interval.quote_currency == home:
        notional = float(interval.units * interval.entry_price)
    elif interval.base_currency == home:
        notional = float(interval.units)
    else:
        notional = float(interval.units)
        notes.append(
            f"cross-pair conversion deferred — using units as notional "
            f"({interval.instrument} home={home})"
        )
    return notional, notes


def _applied_rate(
    pair: RatePair,
    side: str,
) -> float:
    """Pick the rate (annual bp) for the position's own side."""
    return pair.long_annual_bp if side == "long" else pair.short_annual_bp


def _build_event(
    *,
    interval: PositionInterval,
    date_utc: date,
    rate_pair: RatePair | None,
    multiplier: int,
    config: FinancingCalculatorConfig,
    rate_source_name: str,
    extra_notes: list[str],
) -> DailyFinancingEvent:
    notes = list(extra_notes)
    notional, notional_notes = _notional_home(interval)
    notes.extend(notional_notes)

    rate_was_missing = False
    long_bp: float | None = None
    short_bp: float | None = None

    if rate_pair is None:
        rate_was_missing = True
        if config.missing_rate_policy == MissingRatePolicy.ERROR:
            # Caller already gated this — should not reach here.
            raise MissingFinancingRateError(
                f"no rate for {interval.instrument} on {date_utc}"
            )
        fallback_bp_per_day = config.conservative_fallback_bp_per_day
        # Both sides debit, mirroring ConservativeStressRateSource.
        applied_bp_per_day = -fallback_bp_per_day
        notes.append(
            f"missing rate — conservative fallback bp/day={fallback_bp_per_day}"
        )
    else:
        long_bp = rate_pair.long_annual_bp
        short_bp = rate_pair.short_annual_bp
        applied_annual_bp = _applied_rate(rate_pair, interval.side)
        applied_bp_per_day = applied_annual_bp / _DAYS_PER_YEAR

    if multiplier > 1:
        notes.append(f"triple-swap day (multiplier={multiplier})")

    cashflow_home = (applied_bp_per_day / 10_000.0) * multiplier * notional
    cashflow_home_stress = min(cashflow_home, 0.0)

    return DailyFinancingEvent(
        position_id=interval.position_id,
        instrument=interval.instrument,
        date_utc=date_utc,
        weekday=date_utc.weekday(),
        rollover_multiplier=multiplier,
        rate_long_annual_bp=long_bp,
        rate_short_annual_bp=short_bp,
        applied_side=interval.side,
        applied_rate_bp_per_day=applied_bp_per_day,
        notional_home=notional,
        cashflow_home=cashflow_home,
        cashflow_home_stress=cashflow_home_stress,
        rate_source_name=rate_source_name,
        rate_was_missing=rate_was_missing,
        notes=notes,
    )


def calculate_position(
    interval: PositionInterval,
    rate_source: FinancingRateSource,
    config: FinancingCalculatorConfig | None = None,
) -> PositionFinancingSummary:
    """Compute one position's per-day financing events.

    Raises ``MissingFinancingRateError`` if the rate source returns
    None and ``config.missing_rate_policy == ERROR``.
    """
    cfg = config or FinancingCalculatorConfig()
    if interval.home_currency != cfg.home_currency:
        # The interval's own home_currency dominates the protocol
        # — but the config's home_currency is authoritative for the
        # report. Surface the mismatch via a stand-alone note on
        # every event rather than raising; the caller chose to mix.
        prefix_notes = [
            f"position.home_currency={interval.home_currency} differs "
            f"from config.home_currency={cfg.home_currency}; "
            f"using position.home_currency for notional conversion"
        ]
    else:
        prefix_notes = []

    events: list[DailyFinancingEvent] = []
    rate_was_missing_any = False

    for d in _rollover_dates(interval, cfg):
        rate_pair = rate_source.rate_for(d, interval.instrument)
        if (
            rate_pair is None
            and cfg.missing_rate_policy == MissingRatePolicy.SKIP
        ):
            rate_was_missing_any = True
            continue
        if (
            rate_pair is None
            and cfg.missing_rate_policy == MissingRatePolicy.ERROR
        ):
            raise MissingFinancingRateError(
                f"no rate for {interval.instrument} on {d} "
                f"(position_id={interval.position_id})"
            )

        multiplier = 1
        if (
            cfg.triple_swap_weekday is not None
            and d.weekday() == cfg.triple_swap_weekday
        ):
            multiplier = 3

        event = _build_event(
            interval=interval,
            date_utc=d,
            rate_pair=rate_pair,
            multiplier=multiplier,
            config=cfg,
            rate_source_name=rate_source.name,
            extra_notes=prefix_notes,
        )
        events.append(event)
        if event.rate_was_missing:
            rate_was_missing_any = True

    cashflow_total = sum(e.cashflow_home for e in events)
    stress_total = sum(e.cashflow_home_stress for e in events)

    return PositionFinancingSummary(
        position_id=interval.position_id,
        instrument=interval.instrument,
        side=interval.side,
        events=events,
        rollovers=len(events),
        cashflow_home_total=float(cashflow_total),
        cashflow_home_stress_total=float(stress_total),
        rate_was_missing_any=rate_was_missing_any,
    )


def calculate_run(
    intervals: list[PositionInterval],
    rate_source: FinancingRateSource,
    config: FinancingCalculatorConfig | None = None,
    *,
    now: datetime | None = None,
) -> FinancingRunReport:
    """Aggregate financing for many positions into one report.

    ``now`` is the only clock-read seam — injectable for
    reproducible tests. Defaults to ``datetime.now(UTC).replace(microsecond=0)``.
    """
    cfg = config or FinancingCalculatorConfig()
    summaries = [calculate_position(i, rate_source, cfg) for i in intervals]

    event_count = sum(s.rollovers for s in summaries)
    cashflow_total = sum(s.cashflow_home_total for s in summaries)
    stress_total = sum(s.cashflow_home_stress_total for s in summaries)
    missing_count = sum(
        1
        for s in summaries
        for e in s.events
        if e.rate_was_missing
    )

    if rate_source.treatment == FinancingTreatment.MODELED:
        raise ValueError(
            "rate_source.treatment must not be MODELED — research/financing "
            "never produces MODELED financing"
        )

    return FinancingRunReport(
        config=cfg,
        rate_source_name=rate_source.name,
        rate_source_treatment=rate_source.treatment,
        home_currency=cfg.home_currency,
        positions=summaries,
        event_count=event_count,
        cashflow_home_total=float(cashflow_total),
        cashflow_home_stress_total=float(stress_total),
        missing_rate_event_count=missing_count,
        financing_treatment=rate_source.treatment,
        generated_at_utc=now or datetime.now(UTC).replace(microsecond=0),
    )


# Re-export Decimal so callers can build PositionInterval without
# importing decimal themselves. Pure convenience.
__all__ = [
    "Decimal",
    "MissingFinancingRateError",
    "calculate_position",
    "calculate_run",
]
