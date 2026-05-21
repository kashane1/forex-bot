"""Shared fixtures."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import Quote

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def paper_config_path() -> Path:
    return REPO_ROOT / "configs" / "paper.yaml"


@pytest.fixture
def practice_config_path() -> Path:
    return REPO_ROOT / "configs" / "practice.yaml"


@pytest.fixture
def live_example_config_path() -> Path:
    return REPO_ROOT / "configs" / "live.example.yaml"


@pytest.fixture
def paper_settings(paper_config_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "test-account-id")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "test-token")
    return load_settings(paper_config_path)


@pytest.fixture
def temp_db(tmp_path: Path) -> Database:
    return Database(tmp_path / "test.sqlite3")


@pytest.fixture
def eur_usd() -> Instrument:
    return Instrument(
        name="EUR_USD",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        maximum_order_units=Decimal("100000000"),
        margin_rate=Decimal("0.02"),
    )


@pytest.fixture
def usd_jpy() -> Instrument:
    return Instrument(
        name="USD_JPY",
        type="CURRENCY",
        display_precision=3,
        pip_location=-2,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        maximum_order_units=Decimal("100000000"),
        margin_rate=Decimal("0.04"),
    )


@pytest.fixture
def gbp_jpy() -> Instrument:
    return Instrument(
        name="GBP_JPY",
        type="CURRENCY",
        display_precision=3,
        pip_location=-2,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        maximum_order_units=Decimal("100000000"),
        margin_rate=Decimal("0.04"),
    )


@pytest.fixture
def quote_eur_usd() -> Quote:
    return Quote(
        instrument="EUR_USD",
        time=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
        bid=Decimal("1.07990"),
        ask=Decimal("1.08010"),
    )


@pytest.fixture
def quote_usd_jpy() -> Quote:
    return Quote(
        instrument="USD_JPY",
        time=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
        bid=Decimal("154.950"),
        ask=Decimal("154.970"),
    )


@pytest.fixture
def quote_gbp_jpy() -> Quote:
    return Quote(
        instrument="GBP_JPY",
        time=datetime(2026, 5, 21, 12, 0, tzinfo=UTC),
        bid=Decimal("192.000"),
        ask=Decimal("192.030"),
    )
