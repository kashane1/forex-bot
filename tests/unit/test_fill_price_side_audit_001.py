"""Phase 5 audit: explicit bid/ask fill sides and single slippage application."""

from __future__ import annotations

from decimal import Decimal

from forex_bot.backtesting.fills import FillModel


def test_fill_model_long_entry_ask_exit_bid_zero_slip():
    fm = FillModel(fixed_slippage_pips=Decimal("0"), spread_slippage_multiplier=Decimal("0"))
    bid = Decimal("1.1000")
    ask = Decimal("1.1002")
    pip = Decimal("0.0001")
    assert fm.entry_price(side="long", bid=bid, ask=ask, pip_size=pip) == ask
    assert fm.exit_price(side="long", bid=bid, ask=ask, pip_size=pip) == bid


def test_fill_model_short_entry_bid_exit_ask_zero_slip():
    fm = FillModel(fixed_slippage_pips=Decimal("0"), spread_slippage_multiplier=Decimal("0"))
    bid = Decimal("1.1000")
    ask = Decimal("1.1002")
    pip = Decimal("0.0001")
    assert fm.entry_price(side="short", bid=bid, ask=ask, pip_size=pip) == bid
    assert fm.exit_price(side="short", bid=bid, ask=ask, pip_size=pip) == ask


def test_slippage_applied_once_adverse_direction():
    fm = FillModel(fixed_slippage_pips=Decimal("1"), spread_slippage_multiplier=Decimal("0"))
    bid = Decimal("1.1000")
    ask = Decimal("1.1002")
    pip = Decimal("0.0001")
    entry_long = fm.entry_price(side="long", bid=bid, ask=ask, pip_size=pip)
    assert entry_long == ask + Decimal("0.0001")
    exit_long = fm.exit_price(side="long", bid=bid, ask=ask, pip_size=pip)
    assert exit_long == bid - Decimal("0.0001")
