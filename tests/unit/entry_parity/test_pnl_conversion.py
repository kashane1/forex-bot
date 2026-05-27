"""PnL home-currency conversion for non-USD-quote pairs."""

from __future__ import annotations

from decimal import Decimal

from research.backtrader_exit_parity.exit_logic import OpenTrade
from research.backtrader_exit_parity.pnl import pnl_home_currency

from forex_bot.domain.instruments import Instrument


def _trade(side: str, entry: str, units: int) -> OpenTrade:
    import pandas as pd

    return OpenTrade(
        side=side,
        units=units,
        entry_price=Decimal(entry),
        entry_time=pd.Timestamp("2020-01-01T00:00:00Z"),
        stop_price=Decimal("1.0"),
        initial_stop_price=Decimal("1.0"),
        spread_pips_at_entry=Decimal("1.0"),
    )


def test_usd_jpy_pnl_converts_quote_to_usd():
    inst = Instrument(
        name="USD_JPY",
        type="CURRENCY",
        display_precision=3,
        pip_location=-2,
        trade_units_precision=0,
    )
    trade = _trade("long", "150.000", 1000)
    pnl = pnl_home_currency(trade, Decimal("149.000"), inst)
    expected = float(Decimal("-1000") / Decimal("149.000"))
    assert abs(float(pnl) - expected) < 0.001
