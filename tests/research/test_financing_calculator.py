"""Calculator tests covering long/short carry, missing-rate
policies, Wednesday triple swap, weekend skip, JPY precision,
same-day open/close, and currency conversion."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from research.financing.calculator import (
    MissingFinancingRateError,
    calculate_position,
    calculate_run,
)
from research.financing.models import (
    FinancingCalculatorConfig,
    FinancingTreatment,
    MissingRatePolicy,
    PositionInterval,
    RatePair,
)
from research.financing.rates import (
    ConservativeStressRateSource,
    TableRateSource,
    default_stress_rate_source,
)

_DAYS_PER_YEAR = 365


def _utc(y: int, m: int, d: int, h: int = 12, mn: int = 0) -> datetime:
    return datetime(y, m, d, h, mn, tzinfo=UTC)


def _position(
    *,
    side: str = "long",
    instrument: str = "EUR_USD",
    units: str = "10000",
    entry_price: str = "1.0800",
    open_time: datetime,
    close_time: datetime,
    position_id: str = "t1",
    home_currency: str = "USD",
) -> PositionInterval:
    return PositionInterval(
        position_id=position_id,
        instrument=instrument,
        side=side,
        units=Decimal(units),
        entry_price=Decimal(entry_price),
        open_time=open_time,
        close_time=close_time,
        home_currency=home_currency,
    )


# ---------- Long positive carry ----------


def test_long_positive_carry_credits() -> None:
    """A long position on a pair with positive long_rate credits
    the account (cashflow > 0). cashflow_home_stress stays <= 0.

    Window 5/19 08:00 → 5/20 16:00 crosses exactly one rollover
    (5/19 21:00 UTC, Tuesday — non-triple)."""
    src = TableRateSource(
        {(date(2026, 5, 19), "EUR_USD"): RatePair(long_annual_bp=18.25, short_annual_bp=-9.125)},
    )
    p = _position(
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    summary = calculate_position(p, src)
    assert summary.rollovers == 1
    e = summary.events[0]
    assert e.date_utc == date(2026, 5, 19)
    assert e.applied_side == "long"
    # bp/day = 18.25 / 365 = 0.05
    assert e.applied_rate_bp_per_day == pytest.approx(0.05, rel=1e-9)
    # notional = 10000 * 1.08 = 10800
    assert e.notional_home == pytest.approx(10800.0)
    # cashflow = +0.05 / 10000 * 10800 = +0.054
    assert e.cashflow_home == pytest.approx(0.054, rel=1e-9)
    # stress always <= 0 — a positive cashflow is capped at 0
    assert e.cashflow_home_stress == 0.0


# ---------- Long negative carry ----------


def test_long_negative_carry_debits() -> None:
    src = TableRateSource(
        {(date(2026, 5, 19), "EUR_USD"): RatePair(long_annual_bp=-18.25, short_annual_bp=9.125)},
    )
    p = _position(
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, src)
    assert s.rollovers == 1
    e = s.events[0]
    assert e.cashflow_home == pytest.approx(-0.054, rel=1e-9)
    assert e.cashflow_home_stress == pytest.approx(-0.054, rel=1e-9)


# ---------- Short positive carry ----------


def test_short_positive_carry_credits() -> None:
    src = TableRateSource(
        {(date(2026, 5, 19), "EUR_USD"): RatePair(long_annual_bp=-18.25, short_annual_bp=9.125)},
    )
    p = _position(
        side="short",
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, src)
    e = s.events[0]
    assert e.applied_side == "short"
    # bp/day = 9.125 / 365 = 0.025
    assert e.applied_rate_bp_per_day == pytest.approx(0.025, rel=1e-9)
    assert e.cashflow_home == pytest.approx(0.027, rel=1e-9)
    assert e.cashflow_home_stress == 0.0


# ---------- Short negative carry ----------


def test_short_negative_carry_debits() -> None:
    src = TableRateSource(
        {(date(2026, 5, 19), "EUR_USD"): RatePair(long_annual_bp=18.25, short_annual_bp=-9.125)},
    )
    p = _position(
        side="short",
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, src)
    e = s.events[0]
    assert e.cashflow_home == pytest.approx(-0.027, rel=1e-9)
    assert e.cashflow_home_stress == pytest.approx(-0.027, rel=1e-9)


# ---------- Zero-rate case ----------


def test_zero_rate_yields_zero_cashflow() -> None:
    src = TableRateSource(
        {(date(2026, 5, 19), "EUR_USD"): RatePair(long_annual_bp=0.0, short_annual_bp=0.0)},
    )
    p = _position(
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, src)
    assert s.rollovers == 1
    e = s.events[0]
    assert e.cashflow_home == 0.0
    assert e.cashflow_home_stress == 0.0
    assert e.rate_was_missing is False


# ---------- Multi-day holding period ----------


def test_multi_day_position_records_one_event_per_rollover() -> None:
    """4 daily rollovers, with Wednesday triple swap."""
    src = default_stress_rate_source()
    p = _position(
        open_time=_utc(2026, 5, 18, 8),  # Mon
        close_time=_utc(2026, 5, 22, 16),  # Fri
    )
    s = calculate_position(p, src)
    # Rollovers at 21:00 UTC on 5/18, 5/19, 5/20, 5/21 (Mon-Thu).
    # 5/22 21:00 is after the 16:00 close → skipped.
    assert s.rollovers == 4
    dates = [e.date_utc for e in s.events]
    assert dates == [
        date(2026, 5, 18),
        date(2026, 5, 19),
        date(2026, 5, 20),
        date(2026, 5, 21),
    ]
    # Wednesday is 5/20.
    multipliers = [e.rollover_multiplier for e in s.events]
    assert multipliers == [1, 1, 3, 1]
    # Each non-triple daily debit (EUR_USD bp/day 0.6, notional 10800):
    # 0.6/10000 * 10800 = 0.648.  Triple = 1.944.
    cashflows = [round(e.cashflow_home, 6) for e in s.events]
    assert cashflows == [-0.648, -0.648, -1.944, -0.648]
    assert round(s.cashflow_home_total, 6) == -3.888
    assert round(s.cashflow_home_stress_total, 6) == -3.888


# ---------- Same-day open + close ----------


def test_same_day_open_close_yields_zero_rollovers() -> None:
    """Open and close on the same UTC day, both before the 21:00
    rollover → no rollover boundary crossed → no events."""
    p = _position(
        open_time=_utc(2026, 5, 18, 8),
        close_time=_utc(2026, 5, 18, 16),
    )
    s = calculate_position(p, default_stress_rate_source())
    assert s.rollovers == 0
    assert s.events == []
    assert s.cashflow_home_total == 0.0


def test_intraday_position_crossing_rollover_does_record_event() -> None:
    """Open at 20:00 UTC, close at 22:00 UTC same day → rollover
    at 21:00 falls strictly inside → 1 event."""
    p = _position(
        open_time=_utc(2026, 5, 19, 20),  # Tuesday — non-triple
        close_time=_utc(2026, 5, 19, 22),
    )
    s = calculate_position(p, default_stress_rate_source())
    assert s.rollovers == 1
    assert s.events[0].rollover_multiplier == 1


# ---------- Wednesday / triple rollover ----------


def test_triple_rollover_on_wednesday() -> None:
    p = _position(
        open_time=_utc(2026, 5, 20, 8),  # Wed
        close_time=_utc(2026, 5, 20, 23),
    )
    s = calculate_position(p, default_stress_rate_source())
    assert s.rollovers == 1
    e = s.events[0]
    assert e.weekday == 2
    assert e.rollover_multiplier == 3
    # 0.6/10000 * 10800 * 3 = 1.944
    assert round(e.cashflow_home, 6) == -1.944
    assert any("triple-swap" in n for n in e.notes)


def test_triple_rollover_can_be_disabled() -> None:
    cfg = FinancingCalculatorConfig(triple_swap_weekday=None)
    p = _position(
        open_time=_utc(2026, 5, 20, 8),
        close_time=_utc(2026, 5, 20, 23),
    )
    s = calculate_position(p, default_stress_rate_source(), cfg)
    assert s.events[0].rollover_multiplier == 1
    assert round(s.events[0].cashflow_home, 6) == -0.648


def test_weekend_is_skipped_by_default() -> None:
    """Holding across Sat + Sun should record zero weekend
    events (Wednesday triple covers them). Open Fri before
    rollover, close Mon after rollover → events on Fri, Mon."""
    p = _position(
        open_time=_utc(2026, 5, 22, 8),  # Fri pre-rollover
        close_time=_utc(2026, 5, 25, 23),  # Mon post-rollover
    )
    s = calculate_position(p, default_stress_rate_source())
    dates = [e.date_utc for e in s.events]
    assert dates == [date(2026, 5, 22), date(2026, 5, 25)]


def test_weekend_skip_can_be_disabled() -> None:
    cfg = FinancingCalculatorConfig(skip_weekends=False, triple_swap_weekday=None)
    p = _position(
        open_time=_utc(2026, 5, 22, 8),  # Fri
        close_time=_utc(2026, 5, 25, 23),  # Mon
    )
    s = calculate_position(p, default_stress_rate_source(), cfg)
    dates = [e.date_utc for e in s.events]
    assert dates == [
        date(2026, 5, 22),  # Fri
        date(2026, 5, 23),  # Sat
        date(2026, 5, 24),  # Sun
        date(2026, 5, 25),  # Mon
    ]


# ---------- Missing-rate conservative fallback ----------


def test_missing_rate_uses_conservative_fallback_by_default() -> None:
    """No table entry → conservative fallback fires, marks event
    as missing, debits at conservative_fallback_bp_per_day."""
    src = TableRateSource({}, name="empty")
    p = _position(
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, src)
    assert s.rollovers == 1
    e = s.events[0]
    assert e.rate_was_missing is True
    assert e.rate_long_annual_bp is None
    assert e.rate_short_annual_bp is None
    # Default fallback 1.2 bp/day, debit.
    assert e.applied_rate_bp_per_day == pytest.approx(-1.2, rel=1e-9)
    # cashflow = -1.2/10000 * 10800 = -1.296
    assert e.cashflow_home == pytest.approx(-1.296, rel=1e-9)
    assert e.cashflow_home_stress == pytest.approx(-1.296, rel=1e-9)
    assert any("missing rate" in n for n in e.notes)


def test_missing_rate_skip_policy_drops_event() -> None:
    cfg = FinancingCalculatorConfig(missing_rate_policy=MissingRatePolicy.SKIP)
    src = TableRateSource({}, name="empty")
    p = _position(
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, src, cfg)
    assert s.rollovers == 0
    assert s.events == []
    assert s.rate_was_missing_any is True


def test_missing_rate_error_policy_raises() -> None:
    cfg = FinancingCalculatorConfig(missing_rate_policy=MissingRatePolicy.ERROR)
    src = TableRateSource({}, name="empty")
    p = _position(
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    with pytest.raises(MissingFinancingRateError):
        calculate_position(p, src, cfg)


def test_missing_rate_fallback_respects_custom_value() -> None:
    cfg = FinancingCalculatorConfig(conservative_fallback_bp_per_day=2.5)
    src = TableRateSource({}, name="empty")
    p = _position(
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, src, cfg)
    e = s.events[0]
    assert e.applied_rate_bp_per_day == pytest.approx(-2.5, rel=1e-9)


# ---------- USD-quote / USD-base / JPY precision ----------


def test_usd_quote_pair_notional_is_units_times_price() -> None:
    """EUR_USD with USD home: notional = units * entry_price."""
    p = _position(
        instrument="EUR_USD",
        units="25000",
        entry_price="1.0800",
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, default_stress_rate_source())
    assert s.events[0].notional_home == pytest.approx(27000.0)


def test_usd_base_pair_notional_is_units() -> None:
    """USD_JPY with USD home: notional = units (already USD)."""
    p = _position(
        instrument="USD_JPY",
        units="25000",
        entry_price="155.00",
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, default_stress_rate_source())
    assert s.events[0].notional_home == pytest.approx(25000.0)


def test_jpy_precision_with_explicit_table_rate() -> None:
    """JPY pair with a JPY-precision entry price. The bp/day is
    a fraction of notional in *home currency*, so JPY pip
    precision feeds in only via the entry price. The result
    must round to a non-trivial cents figure."""
    src = TableRateSource(
        {(date(2026, 5, 19), "USD_JPY"): RatePair(long_annual_bp=-18.25, short_annual_bp=9.125)},
    )
    p = _position(
        instrument="USD_JPY",
        units="10000",
        entry_price="155.123",
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, src)
    e = s.events[0]
    # USD-base: notional = units = 10000
    assert e.notional_home == pytest.approx(10000.0)
    # bp/day = -18.25/365 = -0.05 → cashflow = -0.05/10000 * 10000 = -0.05
    assert e.cashflow_home == pytest.approx(-0.05, rel=1e-9)


def test_cross_pair_triggers_conservative_fallback_note() -> None:
    """USD home, EUR_GBP → cross pair → conservative-fallback
    note appears even when a rate is found (notional path is
    the deferred-conversion fallback)."""
    src = TableRateSource(
        {(date(2026, 5, 19), "EUR_GBP"): RatePair(long_annual_bp=-10.0, short_annual_bp=10.0)},
    )
    p = _position(
        instrument="EUR_GBP",
        units="10000",
        entry_price="0.85",
        open_time=_utc(2026, 5, 19, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    s = calculate_position(p, src)
    e = s.events[0]
    assert any("cross-pair conversion deferred" in n for n in e.notes)
    # Notional fallback: units
    assert e.notional_home == pytest.approx(10000.0)


# ---------- calculate_run aggregate ----------


def test_calculate_run_aggregates_summaries() -> None:
    src = default_stress_rate_source()
    positions = [
        _position(
            position_id="a",
            open_time=_utc(2026, 5, 18, 8),
            close_time=_utc(2026, 5, 20, 16),
        ),
        _position(
            position_id="b",
            instrument="USD_JPY",
            units="20000",
            entry_price="155.00",
            open_time=_utc(2026, 5, 18, 8),
            close_time=_utc(2026, 5, 22, 16),
        ),
    ]
    report = calculate_run(positions, src, now=_utc(2026, 5, 23, 12))
    assert len(report.positions) == 2
    assert report.event_count == sum(s.rollovers for s in report.positions)
    assert report.rate_source_treatment == FinancingTreatment.ESTIMATED
    assert report.financing_treatment == FinancingTreatment.ESTIMATED
    assert report.financing_in_engine_pnl is False
    assert report.financing_is_live_blocker is True
    assert report.strategy_evidence is False
    assert report.generated_at_utc == _utc(2026, 5, 23, 12)


def test_calculate_run_handles_empty_position_list() -> None:
    report = calculate_run([], default_stress_rate_source(), now=_utc(2026, 5, 23, 12))
    assert report.positions == []
    assert report.event_count == 0
    assert report.cashflow_home_total == 0.0
    assert report.missing_rate_event_count == 0


def test_calculate_run_rejects_modeled_source() -> None:
    """A source that lies about being MODELED is rejected by
    calculate_run before any report is built."""

    class _FakeModeled(ConservativeStressRateSource):
        treatment = FinancingTreatment.MODELED

    src = _FakeModeled()
    with pytest.raises(ValueError, match="MODELED"):
        calculate_run([], src)


def test_calculate_run_counts_missing_events() -> None:
    src = TableRateSource({}, name="empty")
    positions = [
        _position(
            position_id="a",
            open_time=_utc(2026, 5, 18, 8),
            close_time=_utc(2026, 5, 22, 16),  # 4 rollovers
        ),
    ]
    report = calculate_run(positions, src, now=_utc(2026, 5, 23, 12))
    assert report.missing_rate_event_count == report.event_count == 4
