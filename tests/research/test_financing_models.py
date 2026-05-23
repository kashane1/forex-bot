"""Financing model + import-isolation tests.

Pins the data shapes the calculator emits, the
``strategy_evidence: false`` rail on ``FinancingRunReport``, and
grep-enforces that no file under ``research/financing/`` imports
from ``forex_bot``.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError
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

# ---------- PositionInterval ----------


def _utc(y: int, m: int, d: int, h: int = 12) -> datetime:
    return datetime(y, m, d, h, 0, tzinfo=UTC)


def test_position_interval_valid() -> None:
    p = PositionInterval(
        position_id="t1",
        instrument="EUR_USD",
        side="long",
        units=Decimal("10000"),
        entry_price=Decimal("1.0800"),
        open_time=_utc(2026, 5, 18),
        close_time=_utc(2026, 5, 22),
    )
    assert p.base_currency == "EUR"
    assert p.quote_currency == "USD"
    assert p.home_currency == "USD"


def test_position_interval_rejects_bad_instrument() -> None:
    with pytest.raises(ValidationError):
        PositionInterval(
            position_id="t1",
            instrument="EURUSD",  # missing underscore
            side="long",
            units=Decimal("1"),
            entry_price=Decimal("1"),
            open_time=_utc(2026, 5, 18),
            close_time=_utc(2026, 5, 19),
        )


def test_position_interval_rejects_bad_side() -> None:
    with pytest.raises(ValidationError):
        PositionInterval(
            position_id="t1",
            instrument="EUR_USD",
            side="LONG",  # case matters
            units=Decimal("1"),
            entry_price=Decimal("1"),
            open_time=_utc(2026, 5, 18),
            close_time=_utc(2026, 5, 19),
        )


def test_position_interval_rejects_zero_units_or_price() -> None:
    with pytest.raises(ValidationError):
        PositionInterval(
            position_id="t1",
            instrument="EUR_USD",
            side="long",
            units=Decimal("0"),
            entry_price=Decimal("1"),
            open_time=_utc(2026, 5, 18),
            close_time=_utc(2026, 5, 19),
        )
    with pytest.raises(ValidationError):
        PositionInterval(
            position_id="t1",
            instrument="EUR_USD",
            side="long",
            units=Decimal("1"),
            entry_price=Decimal("0"),
            open_time=_utc(2026, 5, 18),
            close_time=_utc(2026, 5, 19),
        )


def test_position_interval_rejects_close_before_open() -> None:
    with pytest.raises(ValidationError):
        PositionInterval(
            position_id="t1",
            instrument="EUR_USD",
            side="long",
            units=Decimal("1"),
            entry_price=Decimal("1"),
            open_time=_utc(2026, 5, 19),
            close_time=_utc(2026, 5, 18),
        )


def test_position_interval_rejects_naive_times() -> None:
    with pytest.raises(ValidationError):
        PositionInterval(
            position_id="t1",
            instrument="EUR_USD",
            side="long",
            units=Decimal("1"),
            entry_price=Decimal("1"),
            open_time=datetime(2026, 5, 18, 0, 0),  # naive
            close_time=_utc(2026, 5, 19),
        )


def test_position_interval_rejects_bad_home_currency() -> None:
    with pytest.raises(ValidationError):
        PositionInterval(
            position_id="t1",
            instrument="EUR_USD",
            side="long",
            units=Decimal("1"),
            entry_price=Decimal("1"),
            open_time=_utc(2026, 5, 18),
            close_time=_utc(2026, 5, 19),
            home_currency="usd",  # lower-case
        )


# ---------- FinancingCalculatorConfig ----------


def test_config_defaults_match_protocol() -> None:
    cfg = FinancingCalculatorConfig()
    assert cfg.rollover_hour_utc == 21
    assert cfg.triple_swap_weekday == 2
    assert cfg.skip_weekends is True
    assert cfg.missing_rate_policy == MissingRatePolicy.CONSERVATIVE
    assert cfg.home_currency == "USD"
    assert cfg.conservative_fallback_bp_per_day == 1.2


def test_config_triple_swap_can_be_disabled() -> None:
    cfg = FinancingCalculatorConfig(triple_swap_weekday=None)
    assert cfg.triple_swap_weekday is None


def test_config_rejects_invalid_rollover_hour() -> None:
    with pytest.raises(ValidationError):
        FinancingCalculatorConfig(rollover_hour_utc=24)
    with pytest.raises(ValidationError):
        FinancingCalculatorConfig(rollover_hour_utc=-1)


def test_config_rejects_invalid_triple_swap_weekday() -> None:
    with pytest.raises(ValidationError):
        FinancingCalculatorConfig(triple_swap_weekday=7)


# ---------- DailyFinancingEvent ----------


def test_event_rejects_positive_stress() -> None:
    with pytest.raises(ValidationError):
        DailyFinancingEvent(
            position_id="t1",
            instrument="EUR_USD",
            date_utc=date(2026, 5, 18),
            weekday=0,
            rollover_multiplier=1,
            rate_long_annual_bp=10.0,
            rate_short_annual_bp=-10.0,
            applied_side="long",
            applied_rate_bp_per_day=0.03,
            notional_home=10000.0,
            cashflow_home=0.5,
            cashflow_home_stress=0.5,  # positive — forbidden
            rate_source_name="x",
            rate_was_missing=False,
        )


def test_event_rejects_bad_applied_side() -> None:
    with pytest.raises(ValidationError):
        DailyFinancingEvent(
            position_id="t1",
            instrument="EUR_USD",
            date_utc=date(2026, 5, 18),
            weekday=0,
            rollover_multiplier=1,
            rate_long_annual_bp=None,
            rate_short_annual_bp=None,
            applied_side="LONG",
            applied_rate_bp_per_day=-0.03,
            notional_home=10000.0,
            cashflow_home=-1.0,
            cashflow_home_stress=-1.0,
            rate_source_name="x",
            rate_was_missing=True,
        )


# ---------- PositionFinancingSummary ----------


def test_summary_rejects_rollover_mismatch() -> None:
    with pytest.raises(ValidationError):
        PositionFinancingSummary(
            position_id="t1",
            instrument="EUR_USD",
            side="long",
            events=[],
            rollovers=3,  # mismatches len(events)==0
            cashflow_home_total=0.0,
            cashflow_home_stress_total=0.0,
            rate_was_missing_any=False,
        )


# ---------- FinancingRunReport rails ----------


def _empty_report(treatment: FinancingTreatment) -> FinancingRunReport:
    return FinancingRunReport(
        config=FinancingCalculatorConfig(),
        rate_source_name="src",
        rate_source_treatment=treatment,
        home_currency="USD",
        positions=[],
        event_count=0,
        cashflow_home_total=0.0,
        cashflow_home_stress_total=0.0,
        missing_rate_event_count=0,
        financing_treatment=treatment,
    )


def test_report_strategy_evidence_pin() -> None:
    with pytest.raises(ValidationError) as ex:
        FinancingRunReport(
            config=FinancingCalculatorConfig(),
            rate_source_name="src",
            rate_source_treatment=FinancingTreatment.ESTIMATED,
            home_currency="USD",
            positions=[],
            event_count=0,
            cashflow_home_total=0.0,
            cashflow_home_stress_total=0.0,
            missing_rate_event_count=0,
            strategy_evidence=True,  # forbidden
            financing_treatment=FinancingTreatment.ESTIMATED,
        )
    assert "strategy_evidence" in str(ex.value)


def test_report_engine_pnl_pin() -> None:
    with pytest.raises(ValidationError):
        FinancingRunReport(
            config=FinancingCalculatorConfig(),
            rate_source_name="src",
            rate_source_treatment=FinancingTreatment.ESTIMATED,
            home_currency="USD",
            positions=[],
            event_count=0,
            cashflow_home_total=0.0,
            cashflow_home_stress_total=0.0,
            missing_rate_event_count=0,
            financing_treatment=FinancingTreatment.ESTIMATED,
            financing_in_engine_pnl=True,  # forbidden
        )


def test_report_live_blocker_pin() -> None:
    with pytest.raises(ValidationError):
        FinancingRunReport(
            config=FinancingCalculatorConfig(),
            rate_source_name="src",
            rate_source_treatment=FinancingTreatment.ESTIMATED,
            home_currency="USD",
            positions=[],
            event_count=0,
            cashflow_home_total=0.0,
            cashflow_home_stress_total=0.0,
            missing_rate_event_count=0,
            financing_treatment=FinancingTreatment.ESTIMATED,
            financing_is_live_blocker=False,  # forbidden
        )


def test_report_rejects_modeled() -> None:
    with pytest.raises(ValidationError):
        _empty_report(FinancingTreatment.MODELED)


def test_report_accepts_estimated() -> None:
    r = _empty_report(FinancingTreatment.ESTIMATED)
    assert r.financing_treatment == FinancingTreatment.ESTIMATED


def test_report_accepts_unmodeled() -> None:
    r = _empty_report(FinancingTreatment.UNMODELED)
    assert r.financing_treatment == FinancingTreatment.UNMODELED


def test_report_rejects_treatment_mismatch() -> None:
    with pytest.raises(ValidationError):
        FinancingRunReport(
            config=FinancingCalculatorConfig(),
            rate_source_name="src",
            rate_source_treatment=FinancingTreatment.ESTIMATED,
            home_currency="USD",
            positions=[],
            event_count=0,
            cashflow_home_total=0.0,
            cashflow_home_stress_total=0.0,
            missing_rate_event_count=0,
            financing_treatment=FinancingTreatment.UNMODELED,  # mismatches source
        )


# ---------- RatePair ----------


def test_rate_pair_accepts_signed_values() -> None:
    p = RatePair(long_annual_bp=-12.5, short_annual_bp=8.25)
    assert p.long_annual_bp == -12.5
    assert p.short_annual_bp == 8.25


# ---------- Import-isolation rail ----------


def test_financing_package_does_not_import_forex_bot() -> None:
    """No file under research/financing/ may import the bespoke
    engine. A grep is sufficient — Python's import resolution
    fires only on the exact name."""
    pkg = Path(__file__).resolve().parents[2] / "research" / "financing"
    offenders: list[str] = []
    for path in pkg.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "forex_bot" in stripped and (
                stripped.startswith("import ") or stripped.startswith("from ")
            ):
                offenders.append(f"{path}:{line_no}: {stripped}")
    assert offenders == [], (
        "research/financing/ must not import forex_bot:\n"
        + "\n".join(offenders)
    )
