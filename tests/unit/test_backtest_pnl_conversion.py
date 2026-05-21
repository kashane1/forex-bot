"""PnL accounting: non-USD-quote pairs (USD_JPY, USD_CAD, USD_CHF) must
convert quote-currency PnL back to account currency using the exit price."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd

from forex_bot.backtesting.engine import BacktestEngine, _OpenTrade
from forex_bot.backtesting.fills import FillModel
from forex_bot.domain.instruments import Instrument
from forex_bot.strategies.trend_following import TrendFollowingStrategy


def _engine(instrument: Instrument) -> BacktestEngine:
    return BacktestEngine(
        instrument=instrument,
        strategy=TrendFollowingStrategy(version="test"),
        strategy_config={},
        fill_model=FillModel(
            fixed_slippage_pips=Decimal("0"),
            spread_slippage_multiplier=Decimal("0"),
        ),
        starting_equity=Decimal("500"),
        account_currency="USD",
    )


def _trade(side: str, units: Decimal, entry: Decimal, stop: Decimal) -> _OpenTrade:
    return _OpenTrade(
        side=side,
        units=units,
        entry_price=entry,
        entry_time=pd.Timestamp("2026-05-21", tz="UTC"),
        stop_price=stop,
        initial_stop_price=stop,
        spread_pips_at_entry=Decimal("1.0"),
    )


def test_eur_usd_pnl_in_home_directly(eur_usd):
    eng = _engine(eur_usd)
    trade = _trade("long", Decimal("1000"), Decimal("1.0800"), Decimal("1.0750"))
    pnl = eng._pnl(trade, Decimal("1.0900"))
    # diff=0.0100 quote (USD), units=1000 EUR, gross_quote = 10 USD
    # quote==home → gross_home = 10 USD.
    assert pnl == Decimal("10.00")


def test_usd_jpy_pnl_converts_using_exit_price(usd_jpy):
    eng = _engine(usd_jpy)
    trade = _trade("long", Decimal("1000"), Decimal("140.00"), Decimal("139.00"))
    pnl = eng._pnl(trade, Decimal("142.00"))
    # diff=2 JPY, units=1000 USD, gross_quote = 2000 JPY
    # base==home (USD), so gross_home = 2000 / 142 ≈ 14.0845 USD.
    expected = Decimal("2000") / Decimal("142")
    assert abs(pnl - expected) < Decimal("0.0001")


def test_usd_jpy_short_pnl(usd_jpy):
    eng = _engine(usd_jpy)
    trade = _trade("short", Decimal("1000"), Decimal("142.00"), Decimal("143.00"))
    pnl = eng._pnl(trade, Decimal("140.00"))
    # short: diff_quote = entry - exit = 2 JPY
    # gross_quote = 2000 JPY, exit 140 → ≈ 14.286 USD
    expected = Decimal("2000") / Decimal("140")
    assert abs(pnl - expected) < Decimal("0.0001")


def test_usd_jpy_losing_trade_does_not_explode_equity(usd_jpy):
    """Regression: before the fix, a 200-pip loss on a $500 account became
    a multi-thousand-dollar 'loss' in the equity curve and could turn equity
    negative in a single trade."""
    eng = _engine(usd_jpy)
    # Size for risk = 1.25 USD over 200-pip stop:
    # pip_value_home = 0.01 / 142 ≈ 7.04e-5; raw_units = 1.25 / (200*7.04e-5) ≈ 88.7
    trade = _trade(
        side="long",
        units=Decimal("88"),
        entry=Decimal("142.00"),
        stop=Decimal("140.00"),
    )
    # Stop hit: loss is 88 USD × 2 JPY = 176 JPY ≈ $1.24 (close to the
    # intended risk).
    pnl = eng._pnl(trade, Decimal("140.00"))
    assert pnl < Decimal("0")
    assert pnl > Decimal("-2.00"), f"loss {pnl} should be ~$1.24, not multi-USD"
