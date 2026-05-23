"""Tests for the deterministic markdown + JSON renderers."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal

from research.financing.calculator import calculate_run
from research.financing.models import (
    FinancingCalculatorConfig,
    FinancingTreatment,
    PositionInterval,
    RatePair,
)
from research.financing.rates import TableRateSource, default_stress_rate_source
from research.financing.reporting import dump_events_json, render_summary_md


def _utc(y: int, m: int, d: int, h: int = 12) -> datetime:
    return datetime(y, m, d, h, 0, tzinfo=UTC)


def _stress_report():
    positions = [
        PositionInterval(
            position_id="t1",
            instrument="EUR_USD",
            side="long",
            units=Decimal("10000"),
            entry_price=Decimal("1.0800"),
            open_time=_utc(2026, 5, 18, 8),
            close_time=_utc(2026, 5, 22, 16),
        ),
    ]
    return calculate_run(
        positions,
        default_stress_rate_source(),
        now=_utc(2026, 5, 23),
    )


def test_dump_events_json_is_deterministic() -> None:
    a = dump_events_json(_stress_report())
    b = dump_events_json(_stress_report())
    assert a == b


def test_dump_events_json_parses_as_json() -> None:
    parsed = json.loads(dump_events_json(_stress_report()))
    assert parsed["strategy_evidence"] is False
    assert parsed["financing_in_engine_pnl"] is False
    assert parsed["financing_is_live_blocker"] is True
    assert parsed["financing_treatment"] == "estimated"
    assert parsed["event_count"] == 4
    assert len(parsed["positions"]) == 1
    assert parsed["positions"][0]["rollovers"] == 4


def test_dump_events_json_uses_iso_dates() -> None:
    parsed = json.loads(dump_events_json(_stress_report()))
    event = parsed["positions"][0]["events"][0]
    # YYYY-MM-DD is 10 characters; reject any other shape.
    assert isinstance(event["date_utc"], str)
    assert len(event["date_utc"]) == 10
    assert event["date_utc"][4] == "-" and event["date_utc"][7] == "-"


def test_dump_events_json_sorted_keys() -> None:
    text = dump_events_json(_stress_report())
    # ``"event_count"`` must appear before ``"financing_in_engine_pnl"``
    # alphabetically; this checks the sorted-keys invariant.
    ec = text.index('"event_count"')
    fi = text.index('"financing_in_engine_pnl"')
    assert ec < fi


def test_render_summary_md_is_deterministic() -> None:
    a = render_summary_md(_stress_report())
    b = render_summary_md(_stress_report())
    assert a == b


def test_render_summary_md_contains_expected_sections() -> None:
    text = render_summary_md(_stress_report())
    assert "# Financing Run Report" in text
    assert "## Run metadata" in text
    assert "## Aggregate" in text
    assert "## Positions" in text
    assert "strategy_evidence: false" in text
    assert "financing_treatment: estimated" in text
    assert "financing_is_live_blocker: true" in text


def test_render_summary_md_marks_triple_swap() -> None:
    text = render_summary_md(_stress_report())
    # Wednesday 2026-05-20 is the triple-swap day in this window.
    assert "triple-swap day (multiplier=3)" in text
    assert "x3" in text


def test_render_summary_md_empty_report() -> None:
    report = calculate_run(
        [], default_stress_rate_source(), now=_utc(2026, 5, 23),
    )
    text = render_summary_md(report)
    assert "_no positions_" in text
    assert "event_count: 0" in text


def test_render_summary_md_marks_missing_rate() -> None:
    src = TableRateSource({}, name="empty")
    positions = [
        PositionInterval(
            position_id="m1",
            instrument="EUR_USD",
            side="long",
            units=Decimal("10000"),
            entry_price=Decimal("1.08"),
            open_time=_utc(2026, 5, 19, 8),
            close_time=_utc(2026, 5, 20, 16),
        ),
    ]
    report = calculate_run(
        positions, src, now=_utc(2026, 5, 23),
    )
    text = render_summary_md(report)
    assert "**MISSING**" in text
    assert "**missing rates**" in text  # summary-level tag


def test_render_summary_md_marks_credit_path_when_table_credits() -> None:
    """A long position on a positive-long-rate pair must report a
    positive cashflow_home but a clamped-to-zero stress."""
    src = TableRateSource(
        {(date(2026, 5, 19), "EUR_USD"): RatePair(long_annual_bp=18.25, short_annual_bp=-9.125)},
    )
    positions = [
        PositionInterval(
            position_id="cred",
            instrument="EUR_USD",
            side="long",
            units=Decimal("10000"),
            entry_price=Decimal("1.0800"),
            open_time=_utc(2026, 5, 19, 8),
            close_time=_utc(2026, 5, 20, 16),
        ),
    ]
    report = calculate_run(positions, src, now=_utc(2026, 5, 23))
    text = render_summary_md(report)
    assert "cashflow=0.054000" in text
    assert "stress=0.000000" in text


def test_dump_events_json_round_trips_treatment_enum() -> None:
    """Pydantic enum dump must yield the lowercase string form
    (matches src/forex_bot/financing.FinancingTreatment)."""
    report = _stress_report()
    parsed = json.loads(dump_events_json(report))
    assert parsed["rate_source_treatment"] == FinancingTreatment.ESTIMATED.value


def test_render_summary_md_handles_triple_swap_disabled() -> None:
    cfg = FinancingCalculatorConfig(triple_swap_weekday=None)
    positions = [
        PositionInterval(
            position_id="nd",
            instrument="EUR_USD",
            side="long",
            units=Decimal("10000"),
            entry_price=Decimal("1.08"),
            open_time=_utc(2026, 5, 20, 8),
            close_time=_utc(2026, 5, 20, 23),
        ),
    ]
    report = calculate_run(
        positions, default_stress_rate_source(), cfg, now=_utc(2026, 5, 23),
    )
    text = render_summary_md(report)
    assert "triple_swap_weekday: disabled" in text
    assert "x1" in text
    # The triple-swap note must NOT appear when disabled.
    assert "triple-swap day" not in text
