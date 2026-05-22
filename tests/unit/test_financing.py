"""Tests for the conservative financing stress model.

This is a STRESS model, not a real historical financing model — see the
module docstring. The tests pin the arithmetic and the conservative
properties (debit always >= 0, scales with holding time and notional).
"""

from __future__ import annotations

from decimal import Decimal

from forex_bot.financing import (
    CONSERVATIVE_BP_PER_DAY,
    bp_per_day,
    financing_debit_r,
    financing_debit_usd,
    holding_days,
    notional_usd,
)


def test_holding_days_from_h4_bars():
    # 6 H4 bars = 24 hours = 1 day
    assert holding_days(6, hours_per_bar=4) == 1.0
    assert holding_days(30, hours_per_bar=4) == 5.0


def test_notional_usd_quote_pair():
    # EUR_USD: units in EUR, notional = units * price
    assert notional_usd("EUR_USD", Decimal("1000"), Decimal("1.08")) == 1080.0


def test_notional_usd_base_pair():
    # USD_JPY: units already in USD
    assert notional_usd("USD_JPY", Decimal("1000"), Decimal("150.0")) == 1000.0


def test_financing_debit_usd_known_value():
    # EUR_USD, 1000 units @ 1.08, held 30 H4 bars (=5 days), bp/day 0.6.
    # notional = 1080 USD; debit = 5 * 0.6/10000 * 1080 = 0.324 USD
    debit = financing_debit_usd("EUR_USD", Decimal("1000"), Decimal("1.08"), 30)
    assert abs(debit - 0.324) < 1e-9


def test_financing_debit_is_never_negative():
    """The stress model is a cost, never a credit — even for the side
    that would carry positively in reality."""
    for inst in CONSERVATIVE_BP_PER_DAY:
        d = financing_debit_usd(inst, Decimal("500"), Decimal("1.20"), 12)
        assert d >= 0.0


def test_financing_debit_scales_with_holding_time():
    short_hold = financing_debit_usd("GBP_USD", Decimal("1000"), Decimal("1.27"), 6)
    long_hold = financing_debit_usd("GBP_USD", Decimal("1000"), Decimal("1.27"), 60)
    # 10x the bars -> 10x the debit
    assert abs(long_hold - 10 * short_hold) < 1e-9


def test_financing_debit_r_is_fraction_of_risk():
    # USD_JPY: 1000 units @ 150, stop 148 -> risk 2 JPY * 1000 / 150 = 13.33 USD
    # held 30 bars (5 days), notional 1000 USD, bp 1.2
    # debit = 5 * 1.2/10000 * 1000 = 0.6 USD
    # debit_r = 0.6 / 13.333... = 0.045
    r = financing_debit_r(
        "USD_JPY", Decimal("1000"), Decimal("150.0"), Decimal("148.0"), 30
    )
    assert abs(r - 0.045) < 1e-4


def test_financing_debit_r_zero_when_no_risk():
    # entry == stop -> degenerate, no risk -> 0 to avoid div-by-zero
    r = financing_debit_r(
        "EUR_USD", Decimal("1000"), Decimal("1.08"), Decimal("1.08"), 30
    )
    assert r == 0.0


def test_unknown_pair_uses_conservative_default():
    # An unlisted pair must fall back to the table maximum, not 0.
    assert bp_per_day("XAU_USD") == max(CONSERVATIVE_BP_PER_DAY.values())
