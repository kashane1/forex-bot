"""Tests for FinancingSourceType and manual CSV rate loader."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from research.financing.manual_csv import (
    ManualCsvValidationError,
    load_manual_csv_rate_schedule,
)
from research.financing.models import FinancingSourceType, FinancingTreatment
from research.financing.rates import ConservativeStressRateSource, default_stress_rate_source


def test_stress_source_has_synthetic_fixture_source_type() -> None:
    src = default_stress_rate_source()
    assert src.source_type == FinancingSourceType.SYNTHETIC_FIXTURE


def test_conservative_stress_source_type_on_class() -> None:
    assert ConservativeStressRateSource.source_type == FinancingSourceType.SYNTHETIC_FIXTURE


def test_load_manual_csv_rate_schedule(tmp_path: Path) -> None:
    csv_path = tmp_path / "rates.csv"
    csv_path.write_text(
        "date,instrument,long_annual_bp,short_annual_bp\n"
        "2020-07-06,EUR_USD,-219.0,-180.0\n"
        "2020-07-07,EUR_USD,-219.0,-180.0\n",
        encoding="utf-8",
    )
    src = load_manual_csv_rate_schedule(csv_path)
    assert src.source_type == FinancingSourceType.MANUAL_CSV
    assert src.treatment == FinancingTreatment.ESTIMATED
    pair = src.rate_for(date(2020, 7, 6), "EUR_USD")
    assert pair is not None
    assert pair.long_annual_bp == -219.0
    assert pair.short_annual_bp == -180.0


def test_manual_csv_refuses_modeled_treatment(tmp_path: Path) -> None:
    csv_path = tmp_path / "rates.csv"
    csv_path.write_text(
        "date,instrument,long_annual_bp,short_annual_bp\n"
        "2020-07-06,EUR_USD,-219.0,-180.0\n",
        encoding="utf-8",
    )
    with pytest.raises(ManualCsvValidationError, match="MODELED"):
        load_manual_csv_rate_schedule(csv_path, treatment=FinancingTreatment.MODELED)


def test_manual_csv_rejects_duplicate_keys(tmp_path: Path) -> None:
    csv_path = tmp_path / "rates.csv"
    csv_path.write_text(
        "date,instrument,long_annual_bp,short_annual_bp\n"
        "2020-07-06,EUR_USD,-219.0,-180.0\n"
        "2020-07-06,EUR_USD,-100.0,-100.0\n",
        encoding="utf-8",
    )
    with pytest.raises(ManualCsvValidationError, match="duplicate"):
        load_manual_csv_rate_schedule(csv_path)
