"""Tests for the non-USD FX cross registry (forex_bot.domain.cross_instruments)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from forex_bot.data.m1_corpus_validation import MAJOR_PAIRS, SUPPORTED_PAIRS
from forex_bot.domain.cross_instruments import (
    EXTENDED_CROSS_PAIRS,
    NONUSD_CROSS_PAIRS,
    PRIMARY_CROSS_PAIRS,
    CrossSpec,
    cross_display_precision,
    cross_instrument,
    cross_pip_location,
    cross_spec,
    is_nonusd_cross,
    registered_crosses,
)

REQUIRED_WAVE1 = ("EUR_GBP", "EUR_JPY", "GBP_JPY", "AUD_JPY")


def test_required_wave1_crosses_are_registered_as_primary():
    for name in REQUIRED_WAVE1:
        assert is_nonusd_cross(name), f"{name} must be registered"
        assert name in PRIMARY_CROSS_PAIRS


def test_registry_has_no_usd_legged_pairs():
    for name in registered_crosses():
        assert "USD" not in name.split("_"), f"{name} is not a non-USD cross"


def test_primary_and_extended_partition_the_registry():
    assert set(PRIMARY_CROSS_PAIRS).isdisjoint(EXTENDED_CROSS_PAIRS)
    assert set(PRIMARY_CROSS_PAIRS) | set(EXTENDED_CROSS_PAIRS) == set(NONUSD_CROSS_PAIRS)


def test_jpy_crosses_use_jpy_pip_conventions():
    for name in ("EUR_JPY", "GBP_JPY", "AUD_JPY", "NZD_JPY"):
        assert cross_pip_location(name) == -2
        assert cross_display_precision(name) == 3
        assert cross_spec(name).is_jpy_cross is True
        assert cross_spec(name).pip_size == Decimal("0.01")


def test_non_jpy_crosses_use_four_decimal_pip_conventions():
    for name in ("EUR_GBP", "EUR_CHF", "GBP_CHF", "EUR_AUD"):
        assert cross_pip_location(name) == -4
        assert cross_display_precision(name) == 5
        assert cross_spec(name).is_jpy_cross is False
        assert cross_spec(name).pip_size == Decimal("0.0001")


def test_base_and_quote_currency_parsing():
    spec = cross_spec("AUD_JPY")
    assert spec.base_currency == "AUD"
    assert spec.quote_currency == "JPY"
    assert spec.carry_legs == ("AUD", "JPY")


def test_cross_instrument_builds_a_valid_domain_instrument():
    inst = cross_instrument("GBP_JPY")
    assert inst.name == "GBP_JPY"
    assert inst.type == "CURRENCY"
    assert inst.pip_location == -2
    assert inst.display_precision == 3
    assert inst.pip_size == Decimal("0.01")
    # display/pip helpers from the existing Instrument model work unchanged
    assert inst.price_to_pips(Decimal("0.10")) == Decimal("10")


def test_cross_instrument_non_jpy_roundtrips_pips():
    inst = cross_instrument("EUR_GBP")
    assert inst.pip_size == Decimal("0.0001")
    assert inst.price_to_pips(Decimal("0.0010")) == Decimal("10")


def test_eur_chf_carries_the_2015_snb_structural_break():
    spec = cross_spec("EUR_CHF")
    breaks = dict(spec.structural_breaks)
    assert date(2015, 1, 15) in breaks


def test_carry_crosses_flagged():
    assert cross_spec("AUD_JPY").is_carry_cross is True
    assert cross_spec("EUR_GBP").is_carry_cross is False


def test_supported_pairs_is_majors_plus_crosses_and_majors_unchanged():
    # MAJOR_PAIRS must stay exactly the seven control-universe majors.
    assert MAJOR_PAIRS == (
        "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD",
    )
    assert SUPPORTED_PAIRS == MAJOR_PAIRS + NONUSD_CROSS_PAIRS
    # union, no overlap
    assert set(MAJOR_PAIRS).isdisjoint(NONUSD_CROSS_PAIRS)


def test_bad_cross_name_rejected():
    with pytest.raises(ValueError):
        CrossSpec(
            name="EURJPY", tier="primary", cost_band="near_major",
            est_spread_pips=(1.0, 2.0), conservative_bp_per_day=0.5, is_carry_cross=False,
        )


def test_usd_legged_pair_rejected_by_spec():
    with pytest.raises(ValueError, match="non-USD"):
        CrossSpec(
            name="EUR_USD", tier="primary", cost_band="near_major",
            est_spread_pips=(1.0, 2.0), conservative_bp_per_day=0.5, is_carry_cross=False,
        )


def test_unknown_cost_band_rejected():
    with pytest.raises(ValueError, match="cost band"):
        CrossSpec(
            name="EUR_GBP", tier="primary", cost_band="cheap",
            est_spread_pips=(1.0, 2.0), conservative_bp_per_day=0.5, is_carry_cross=False,
        )


def test_unknown_cross_lookups_raise():
    assert is_nonusd_cross("EUR_USD") is False
    with pytest.raises(KeyError):
        cross_spec("EUR_USD")
