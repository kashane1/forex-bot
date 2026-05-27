"""Home-currency PnL conversion for the Backtrader exit-parity lane.

Mirrors ``BacktestEngine._pnl`` (``src/forex_bot/backtesting/engine.py``):

* USD-quote pairs (EUR_USD, GBP_USD, …): gross PnL is already in USD.
* USD-base pairs (USD_JPY, USD_CAD, USD_CHF): quote-currency gross PnL is
  divided by the exit price to convert JPY/CAD/CHF → USD.

Unsupported crosses (neither leg is account currency) raise ``ValueError``.

Commission is not applied here; campaign configs use ``commission_per_unit: 0``.
"""

from __future__ import annotations

from decimal import Decimal

from forex_bot.domain.instruments import Instrument
from research.backtrader_exit_parity.exit_logic import OpenTrade

DEFAULT_ACCOUNT_CURRENCY = "USD"


def gross_pnl_quote(
    trade: OpenTrade,
    exit_price: Decimal,
) -> Decimal:
    """Gross PnL in the instrument's quote currency (before home conversion)."""
    diff = (
        (exit_price - trade.entry_price)
        if trade.side == "long"
        else (trade.entry_price - exit_price)
    )
    return diff * trade.units


def pnl_home_currency(
    trade: OpenTrade,
    exit_price: Decimal,
    instrument: Instrument,
    *,
    account_currency: str = DEFAULT_ACCOUNT_CURRENCY,
    commission_per_unit: Decimal = Decimal("0"),
) -> Decimal:
    """Convert quote-currency gross PnL to account (home) currency."""
    home = account_currency.upper()
    gross_quote = gross_pnl_quote(trade, exit_price)

    if instrument.quote_currency == home:
        gross_home = gross_quote
    elif instrument.base_currency == home:
        gross_home = gross_quote / exit_price
    else:
        raise ValueError(
            f"Unsupported cross pair {instrument.name} for account_currency={home}; "
            "no conversion quote available"
        )

    return gross_home - commission_per_unit * trade.units
