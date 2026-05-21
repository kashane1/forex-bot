"""Sizing tests covering EUR_USD (quote=home), USD_JPY (base=home),
and GBP_JPY cross conversion."""

from __future__ import annotations

from decimal import Decimal

from forex_bot.risk.sizing import compute_pip_value_home, size_position


def test_pip_value_quote_equals_home_eur_usd(eur_usd):
    pip = compute_pip_value_home(eur_usd, "USD", {})
    assert pip == Decimal("0.0001")


def test_pip_value_base_equals_home_usd_jpy(usd_jpy, quote_usd_jpy):
    pip = compute_pip_value_home(usd_jpy, "USD", {"USD_JPY": quote_usd_jpy})
    # 0.01 / mid(154.96) ≈ 0.00006453
    assert pip < Decimal("0.0001")
    assert pip > Decimal("0.00006")


def test_pip_value_cross_uses_inverse(gbp_jpy, quote_usd_jpy):
    pip = compute_pip_value_home(gbp_jpy, "USD", {"USD_JPY": quote_usd_jpy})
    # 0.01 / 154.96 (same magnitude as USD_JPY pip)
    assert pip is not None
    assert pip > Decimal("0.00005")


def test_pip_value_missing_returns_none(gbp_jpy):
    assert compute_pip_value_home(gbp_jpy, "EUR", {}) is None


def test_size_position_eur_usd_basic(eur_usd, quote_eur_usd):
    result = size_position(
        instrument=eur_usd,
        account_currency="USD",
        nav_home=Decimal("500"),
        risk_per_trade_pct=Decimal("0.25"),
        entry_price=Decimal("1.08010"),
        stop_price=Decimal("1.07810"),  # 20 pip stop
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    assert result is not None
    # risk = 500 * 0.25/100 = 1.25 USD
    # stop = 20 pips, pip value = 0.0001 USD/EUR
    # raw_units = 1.25 / (20 * 0.0001) = 625 EUR
    assert result.units == Decimal("625")


def test_size_position_rounds_down(eur_usd, quote_eur_usd):
    result = size_position(
        instrument=eur_usd,
        account_currency="USD",
        nav_home=Decimal("500"),
        risk_per_trade_pct=Decimal("0.10"),
        entry_price=Decimal("1.08010"),
        stop_price=Decimal("1.07810"),
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    assert result is not None
    # 0.10% of 500 = 0.50 / (20 * 0.0001) = 250
    assert result.units == Decimal("250")


def test_size_position_usd_jpy(usd_jpy, quote_usd_jpy):
    result = size_position(
        instrument=usd_jpy,
        account_currency="USD",
        nav_home=Decimal("500"),
        risk_per_trade_pct=Decimal("0.25"),
        entry_price=Decimal("154.970"),
        stop_price=Decimal("154.770"),  # 20 pip stop
        quotes_by_instrument={"USD_JPY": quote_usd_jpy},
    )
    assert result is not None
    # risk = 1.25 USD; pip value ~0.0000645 USD/USD; stop = 20 pips
    # raw_units = 1.25 / (20 * 0.0000645) ≈ 968
    assert result.units > Decimal("900")
    assert result.units < Decimal("1100")


def test_size_position_zero_stop_returns_none(eur_usd, quote_eur_usd):
    result = size_position(
        instrument=eur_usd,
        account_currency="USD",
        nav_home=Decimal("500"),
        risk_per_trade_pct=Decimal("0.25"),
        entry_price=Decimal("1.08010"),
        stop_price=Decimal("1.08010"),
        quotes_by_instrument={"EUR_USD": quote_eur_usd},
    )
    assert result is None


def test_size_position_no_pip_value_returns_none(gbp_jpy):
    """Cross with no conversion available."""
    result = size_position(
        instrument=gbp_jpy,
        account_currency="EUR",
        nav_home=Decimal("500"),
        risk_per_trade_pct=Decimal("0.25"),
        entry_price=Decimal("192.030"),
        stop_price=Decimal("191.730"),
        quotes_by_instrument={},
    )
    assert result is None
