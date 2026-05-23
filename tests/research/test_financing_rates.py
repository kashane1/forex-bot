"""Tests for ``FinancingRateSource`` and its v1 implementations."""

from __future__ import annotations

from datetime import date

import pytest
from research.financing.models import FinancingTreatment, RatePair
from research.financing.rates import (
    CONSERVATIVE_BP_PER_DAY,
    ConservativeStressRateSource,
    TableRateSource,
    default_stress_rate_source,
)

_DAYS_PER_YEAR = 365


def test_conservative_table_mirrors_existing_overlay() -> None:
    """The bp/day numbers must mirror src/forex_bot/financing.py
    so the new module's stress mode matches the existing one."""
    expected = {
        "EUR_USD": 0.6,
        "GBP_USD": 0.7,
        "USD_JPY": 1.2,
        "AUD_USD": 0.7,
        "USD_CAD": 0.5,
        "USD_CHF": 0.9,
        "NZD_USD": 0.7,
    }
    assert expected == CONSERVATIVE_BP_PER_DAY


def test_default_stress_source_treatment_is_estimated() -> None:
    src = default_stress_rate_source()
    assert src.treatment == FinancingTreatment.ESTIMATED
    assert src.name == "conservative_stress"


def test_stress_source_returns_debit_on_both_sides() -> None:
    src = ConservativeStressRateSource()
    pair = src.rate_for(date(2026, 5, 18), "EUR_USD")
    assert pair is not None
    # Annual bp = bp_per_day * 365, with negative sign (debit)
    expected_annual = -0.6 * _DAYS_PER_YEAR
    assert pair.long_annual_bp == expected_annual
    assert pair.short_annual_bp == expected_annual
    assert pair.long_annual_bp < 0
    assert pair.short_annual_bp < 0


def test_stress_source_uses_default_for_unknown_pair() -> None:
    src = ConservativeStressRateSource()
    pair = src.rate_for(date(2026, 5, 18), "ZZZ_QQQ")
    assert pair is not None
    expected_annual = -1.2 * _DAYS_PER_YEAR  # _DEFAULT_BP_PER_DAY
    assert pair.long_annual_bp == expected_annual
    assert pair.short_annual_bp == expected_annual


def test_stress_source_accepts_custom_table_and_default() -> None:
    src = ConservativeStressRateSource(
        bp_per_day_table={"EUR_USD": 2.0},
        default_bp_per_day=5.0,
        name="custom-stress",
    )
    assert src.name == "custom-stress"
    pair = src.rate_for(date(2026, 5, 18), "EUR_USD")
    assert pair is not None
    assert pair.long_annual_bp == -2.0 * _DAYS_PER_YEAR
    other = src.rate_for(date(2026, 5, 18), "ZZZ_QQQ")
    assert other is not None
    assert other.long_annual_bp == -5.0 * _DAYS_PER_YEAR


def test_stress_source_is_date_independent() -> None:
    src = ConservativeStressRateSource()
    a = src.rate_for(date(2020, 1, 1), "EUR_USD")
    b = src.rate_for(date(2030, 12, 31), "EUR_USD")
    assert a == b


def test_table_rate_source_returns_none_for_missing() -> None:
    src = TableRateSource({})
    assert src.rate_for(date(2026, 5, 18), "EUR_USD") is None


def test_table_rate_source_returns_stored_value() -> None:
    pair = RatePair(long_annual_bp=-12.0, short_annual_bp=8.0)
    src = TableRateSource(
        {(date(2026, 5, 19), "EUR_USD"): pair},
        name="fix",
    )
    assert src.name == "fix"
    assert src.rate_for(date(2026, 5, 19), "EUR_USD") == pair
    assert src.rate_for(date(2026, 5, 20), "EUR_USD") is None
    assert src.rate_for(date(2026, 5, 19), "USD_JPY") is None


def test_table_rate_source_rejects_modeled_treatment() -> None:
    with pytest.raises(ValueError, match="MODELED"):
        TableRateSource({}, treatment=FinancingTreatment.MODELED)


def test_table_rate_source_accepts_unmodeled_treatment() -> None:
    src = TableRateSource({}, treatment=FinancingTreatment.UNMODELED)
    assert src.treatment == FinancingTreatment.UNMODELED


def test_table_rate_source_default_treatment_is_estimated() -> None:
    src = TableRateSource({})
    assert src.treatment == FinancingTreatment.ESTIMATED


def test_table_rate_source_copies_input_table() -> None:
    """Mutating the original dict after construction must not affect the source."""
    pair = RatePair(long_annual_bp=-1.0, short_annual_bp=1.0)
    table = {(date(2026, 5, 19), "EUR_USD"): pair}
    src = TableRateSource(table)
    table.pop((date(2026, 5, 19), "EUR_USD"))
    assert src.rate_for(date(2026, 5, 19), "EUR_USD") == pair
