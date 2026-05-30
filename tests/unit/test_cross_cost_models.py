"""Phase 4 — non-USD cross cost models (spread + two-legged carry)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from forex_bot.research.cost_models import (
    CrossCarryModel,
    CrossSpreadCostModel,
    SpreadStats,
    cross_cost_profile,
)
from forex_bot.research.cost_models.carry import CrossCarryTreatment

# --- spread model ---------------------------------------------------------

def test_spread_model_uses_registry_band_by_default():
    m = CrossSpreadCostModel("GBP_JPY")  # wide band (2.5, 4.0)
    assert m.source == "registry_estimate"
    assert m.spread_pips(level="low") == 2.5
    assert m.spread_pips(level="high") == 4.0
    assert m.spread_pips(level="typical") == pytest.approx(3.25)


def test_spread_price_uses_cross_pip_size():
    # JPY cross: pip = 0.01, so 3.25 pips => 0.0325 price units.
    m = CrossSpreadCostModel("GBP_JPY")
    assert m.spread_price(level="typical") == Decimal("3.25") * Decimal("0.01")
    # non-JPY cross: pip = 0.0001
    m2 = CrossSpreadCostModel("EUR_GBP")
    assert m2.spread_price(level="low") == Decimal("1.0") * Decimal("0.0001")


def test_spread_cost_r_round_trip_is_two_legs():
    m = CrossSpreadCostModel("EUR_GBP")  # band (1,2) → typical 1.5
    # risk 30 pips, round trip → 2*1.5/30 = 0.10 R
    assert m.spread_cost_r(30.0, level="typical", round_trip=True) == pytest.approx(0.10)
    assert m.spread_cost_r(30.0, level="typical", round_trip=False) == pytest.approx(0.05)


def test_spread_cost_r_rejects_nonpositive_risk():
    m = CrossSpreadCostModel("EUR_GBP")
    with pytest.raises(ValueError):
        m.spread_cost_r(0.0)


def test_measured_spread_overrides_estimate():
    stats = SpreadStats.from_bid_ask(
        "EUR_JPY",
        bids=[160.00, 160.01, 160.02, 160.03, 160.04],
        asks=[160.02, 160.03, 160.05, 160.06, 160.10],  # spreads 2,2,3,3,6 pips
    )
    assert stats.source == "measured"
    assert stats.median_pips == pytest.approx(3.0)
    m = CrossSpreadCostModel("EUR_JPY", measured=stats)
    assert m.source == "measured"
    assert m.spread_pips(level="typical") == pytest.approx(3.0)
    assert m.spread_pips(level="high") == pytest.approx(stats.p90_pips)


def test_spread_model_rejects_non_cross():
    with pytest.raises(ValueError):
        CrossSpreadCostModel("USD_JPY")


# --- carry model (two-legged, quote-currency-cancelling) ------------------

def test_carry_model_uses_explicit_registry_bp_not_majors_fallback():
    m = CrossCarryModel("AUD_JPY")
    assert m.bp_per_day == 1.2  # explicit registry value for AUD_JPY
    assert m.carry_legs == ("AUD", "JPY")
    assert m.treatment == CrossCarryTreatment.ESTIMATED


def test_carry_debit_quote_is_nonnegative_and_scales_with_time():
    m = CrossCarryModel("EUR_JPY")  # bp 0.8
    d1 = m.debit_quote(Decimal("1000"), Decimal("160"), bars_held=6)   # 1 day
    d2 = m.debit_quote(Decimal("1000"), Decimal("160"), bars_held=60)  # 10 days
    assert d1 >= 0
    assert d2 == pytest.approx(d1 * 10)
    # 1 day: 0.8/10000 * (1000*160) = 12.8 JPY
    assert d1 == pytest.approx(0.8 / 10_000 * 1000 * 160)


def test_carry_debit_r_is_quote_currency_independent():
    # debit_r = days * bp/10000 * entry / |entry-stop|  (units & quote cancel)
    m = CrossCarryModel("GBP_JPY")  # bp 1.0
    r = m.debit_r(Decimal("1000"), Decimal("190.00"), Decimal("188.00"), bars_held=6)
    expected = (6 * 4 / 24) * (1.0 / 10_000) * 190.0 / 2.0
    assert r == pytest.approx(expected)
    # independent of units
    r2 = m.debit_r(Decimal("5000"), Decimal("190.00"), Decimal("188.00"), bars_held=6)
    assert r2 == pytest.approx(r)


def test_carry_debit_r_zero_for_degenerate_risk():
    m = CrossCarryModel("EUR_JPY")
    assert m.debit_r(Decimal("1000"), Decimal("160"), Decimal("160"), bars_held=6) == 0.0


def test_carry_metadata_is_honest_about_denomination_and_blocker():
    m = CrossCarryModel("AUD_JPY")
    md = m.metadata()
    assert md["carry_treatment"] == "estimated"
    assert md["financing_in_engine_pnl"] is False
    assert md["financing_is_live_blocker"] is True
    assert md["denomination"] == "quote_currency:JPY"
    assert md["carry_legs"] == ["AUD", "JPY"]


def test_carry_model_rejects_non_cross():
    with pytest.raises(ValueError):
        CrossCarryModel("USD_CAD")


# --- combined profile -----------------------------------------------------

def test_cross_cost_profile_is_diagnostic_and_complete():
    prof = cross_cost_profile("EUR_CHF")
    assert prof["strategy_evidence"] is False
    assert prof["diagnostic_only"] is True
    assert prof["quote_currency"] == "CHF"
    assert prof["spread"]["source"] == "registry_estimate"
    assert prof["carry"]["financing_is_live_blocker"] is True
    # EUR_CHF carries the 2015 SNB structural break
    assert any(b["date"] == "2015-01-15" for b in prof["structural_breaks"])


def test_profile_rejects_non_cross():
    with pytest.raises(ValueError):
        cross_cost_profile("EUR_USD")
