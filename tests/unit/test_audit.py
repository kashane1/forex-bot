"""Tests for the data-quality gap classifier in forex_bot.backtesting.audit
(added in Phase 5, oanda-practice-readonly-001)."""

from __future__ import annotations

from datetime import UTC, datetime

from forex_bot.backtesting.audit import AuditReport, GapClassification, classify_gaps


def _report(*, missing=None, weekend=None) -> AuditReport:
    return AuditReport(
        instrument="EUR_USD",
        granularity="H4",
        requested_from=None,
        requested_to=None,
        first_ts=None,
        last_ts=None,
        candle_count=0,
        completed_count=0,
        incomplete_count=0,
        bid_available_count=0,
        ask_available_count=0,
        missing_intervals=missing or [],
        weekend_gaps=weekend or [],
    )


def _gap(start: tuple, end: tuple, bars: int):
    return (datetime(*start, tzinfo=UTC), datetime(*end, tzinfo=UTC), bars)


def test_weekend_gaps_pass_through_as_expected():
    wk = _gap((2024, 3, 1, 21), (2024, 3, 3, 21), 11)
    g = classify_gaps(_report(weekend=[wk]))
    assert g.weekend == [wk]
    assert g.expected_count == 1
    assert g.concerning_count == 0


def test_year_end_gap_is_classified_as_holiday():
    holiday = _gap((2023, 12, 25, 0), (2023, 12, 27, 0), 11)
    g = classify_gaps(_report(missing=[holiday]))
    assert g.year_end_holiday == [holiday]
    assert g.outage_like == []
    assert g.expected_count == 1
    assert g.concerning_count == 0


def test_new_year_gap_is_classified_as_holiday():
    holiday = _gap((2024, 1, 1, 0), (2024, 1, 2, 0), 5)
    g = classify_gaps(_report(missing=[holiday]))
    assert g.year_end_holiday == [holiday]


def test_midweek_multibar_gap_is_outage_like():
    outage = _gap((2024, 3, 13, 0), (2024, 3, 14, 12), 8)
    g = classify_gaps(_report(missing=[outage]))
    assert g.outage_like == [outage]
    assert g.concerning_count == 1


def test_midweek_short_gap_is_suspicious():
    short = _gap((2024, 3, 13, 0), (2024, 3, 13, 8), 1)
    g = classify_gaps(_report(missing=[short]))
    assert g.suspicious_short == [short]
    assert g.concerning_count == 1


def test_two_bar_gap_is_suspicious_three_bar_is_outage():
    two = _gap((2024, 6, 12, 0), (2024, 6, 12, 12), 2)
    three = _gap((2024, 7, 10, 0), (2024, 7, 10, 16), 3)
    g = classify_gaps(_report(missing=[two, three]))
    assert g.suspicious_short == [two]
    assert g.outage_like == [three]


def test_empty_report_has_no_gaps():
    g = classify_gaps(_report())
    assert isinstance(g, GapClassification)
    assert g.expected_count == 0
    assert g.concerning_count == 0
