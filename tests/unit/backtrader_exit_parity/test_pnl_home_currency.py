"""Home-currency PnL conversion for the Backtrader exit-parity lane."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd
import pytest
from research.backtrader_exit_parity.exit_logic import OpenTrade
from research.backtrader_exit_parity.pnl import gross_pnl_quote, pnl_home_currency
from research.backtrader_exit_parity.risk_windows import drawdown_pct

from forex_bot.domain.instruments import Instrument


def _trade(side: str, entry: str, units: int) -> OpenTrade:
    return OpenTrade(
        side=side,
        units=units,
        entry_price=Decimal(entry),
        entry_time=pd.Timestamp("2020-01-01T00:00:00Z"),
        stop_price=Decimal("1.0"),
        initial_stop_price=Decimal("1.0"),
        spread_pips_at_entry=Decimal("1.0"),
    )


def _inst(name: str, pip_loc: int, prec: int) -> Instrument:
    return Instrument(
        name=name,
        type="CURRENCY",
        display_precision=prec,
        pip_location=pip_loc,
        trade_units_precision=0,
    )


def test_eur_usd_pnl_unchanged_in_usd_quote():
    inst = _inst("EUR_USD", -4, 5)
    trade = _trade("long", "1.0800", 1000)
    pnl = pnl_home_currency(trade, Decimal("1.0900"), inst)
    assert pnl == Decimal("10.00")


def test_usd_jpy_quote_to_usd_conversion(usd_jpy):
    trade = _trade("long", "150.000", 1000)
    pnl = pnl_home_currency(trade, Decimal("149.000"), usd_jpy)
    expected = Decimal("-1000") / Decimal("149.000")
    assert abs(pnl - expected) < Decimal("0.0001")


def test_usd_cad_quote_to_usd_conversion():
    inst = _inst("USD_CAD", -4, 5)
    trade = _trade("long", "1.3500", 1000)
    pnl = pnl_home_currency(trade, Decimal("1.3400"), inst)
    expected = Decimal("-10") / Decimal("1.3400")
    assert abs(pnl - expected) < Decimal("0.0001")


def test_usd_chf_quote_to_usd_conversion():
    inst = _inst("USD_CHF", -4, 5)
    trade = _trade("short", "0.9000", 2000)
    pnl = pnl_home_currency(trade, Decimal("0.8950"), inst)
    expected = Decimal("10") / Decimal("0.8950")
    assert abs(pnl - expected) < Decimal("0.0001")


def test_unsupported_cross_raises(gbp_jpy):
    trade = _trade("long", "192.000", 100)
    with pytest.raises(ValueError, match="Unsupported cross pair"):
        pnl_home_currency(trade, Decimal("193.000"), gbp_jpy)


def test_jpy_loss_without_conversion_would_inflate_drawdown(usd_jpy):
    """Regression: treating JPY PnL as USD inflated drawdown and blocked entries."""
    trade = _trade("long", "142.00", 88)
    exit_price = Decimal("140.00")
    wrong_usd = gross_pnl_quote(trade, exit_price)
    correct_usd = pnl_home_currency(trade, exit_price, usd_jpy)
    assert wrong_usd == Decimal("-176")
    assert correct_usd > Decimal("-2.00")
    assert abs(wrong_usd) > abs(correct_usd) * Decimal("50")


def test_correct_jpy_pnl_keeps_drawdown_below_limit(usd_jpy):
    starting = 10_000.0
    trade = _trade("long", "142.00", 88)
    pnl = float(pnl_home_currency(trade, Decimal("140.00"), usd_jpy))
    equity_bars = [(pd.Timestamp("2020-01-01").to_pydatetime(), starting)]
    dd = drawdown_pct(equity_bars, starting + pnl)
    assert dd < Decimal("1.0")
