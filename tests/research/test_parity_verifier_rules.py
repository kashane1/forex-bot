"""Fixture-level tests for the verifier's independent strategy rules.

Tests the CAMPAIGN_002 H4 ``trend_following 0.1.0`` rule evaluation
on tiny, deterministic inputs — no full backtest required. Each
fixture exercises one rule branch (entry, no-entry, initial stop,
trailing ratchet, exit precedence, …) so that a divergence found
later by the event loop can be localized.
"""

from __future__ import annotations

from math import nan

import pytest
from research.parity_verifier.models import Side, TradeExitReason
from research.parity_verifier.rules import (
    evaluate_entry,
    evaluate_exit,
    fill_entry_price,
    initial_stop_price,
    ratchet_trailing_stop,
    size_position,
    trade_pnl,
)

# ---------- evaluate_entry ----------


def test_no_entry_when_in_position() -> None:
    out = evaluate_entry(
        ema_fast=1.1,
        ema_slow=1.0,
        close=1.15,
        donchian_high_val=1.10,
        donchian_low_val=1.05,
        atr_value=0.005,
        atr_floor_pips=None,
        pip_size=0.0001,
        in_position=True,
    )
    assert out.is_entry is False
    assert out.side is Side.FLAT


def test_no_entry_with_nan_indicators() -> None:
    out = evaluate_entry(
        ema_fast=nan,
        ema_slow=1.0,
        close=1.15,
        donchian_high_val=1.10,
        donchian_low_val=1.05,
        atr_value=0.005,
        atr_floor_pips=None,
        pip_size=0.0001,
        in_position=False,
    )
    assert out.is_entry is False


def test_long_entry_on_breakout_above_donchian_high() -> None:
    out = evaluate_entry(
        ema_fast=1.10,
        ema_slow=1.05,
        close=1.1500,
        donchian_high_val=1.1450,
        donchian_low_val=1.0900,
        atr_value=0.005,
        atr_floor_pips=None,
        pip_size=0.0001,
        in_position=False,
    )
    assert out.is_entry is True
    assert out.side is Side.LONG


def test_short_entry_on_breakdown_below_donchian_low() -> None:
    out = evaluate_entry(
        ema_fast=1.05,
        ema_slow=1.10,
        close=1.0800,
        donchian_high_val=1.1100,
        donchian_low_val=1.0900,
        atr_value=0.005,
        atr_floor_pips=None,
        pip_size=0.0001,
        in_position=False,
    )
    assert out.is_entry is True
    assert out.side is Side.SHORT


def test_no_entry_when_close_does_not_break_band() -> None:
    out = evaluate_entry(
        ema_fast=1.10,
        ema_slow=1.05,
        close=1.1400,
        donchian_high_val=1.1450,
        donchian_low_val=1.0900,
        atr_value=0.005,
        atr_floor_pips=None,
        pip_size=0.0001,
        in_position=False,
    )
    assert out.is_entry is False


def test_no_entry_blocked_by_trend_filter() -> None:
    """Close breaks the high but EMA fast < EMA slow — long not allowed."""

    out = evaluate_entry(
        ema_fast=1.05,
        ema_slow=1.10,
        close=1.1500,
        donchian_high_val=1.1450,
        donchian_low_val=1.0900,
        atr_value=0.005,
        atr_floor_pips=None,
        pip_size=0.0001,
        in_position=False,
    )
    assert out.is_entry is False


def test_no_entry_below_atr_floor() -> None:
    """If ``atr_floor_pips`` is set and ATR is below it, no entry. The
    floor is documented as empty `{}` for CAMPAIGN_002, but the verifier
    must still honour it correctly if a future re-run sets one."""

    out = evaluate_entry(
        ema_fast=1.10,
        ema_slow=1.05,
        close=1.1500,
        donchian_high_val=1.1450,
        donchian_low_val=1.0900,
        atr_value=0.0001,  # 1.0 pips of ATR
        atr_floor_pips=5.0,
        pip_size=0.0001,
        in_position=False,
    )
    assert out.is_entry is False


# ---------- initial_stop_price ----------


def test_initial_stop_long_subtracts_atr_x_multiple_from_close() -> None:
    stop = initial_stop_price(
        side=Side.LONG, close_price=1.1500, atr_value=0.005, atr_stop_multiple=2.0
    )
    assert stop == pytest.approx(1.1500 - 0.010)


def test_initial_stop_short_adds_atr_x_multiple_to_close() -> None:
    stop = initial_stop_price(
        side=Side.SHORT, close_price=1.0800, atr_value=0.005, atr_stop_multiple=2.0
    )
    assert stop == pytest.approx(1.0800 + 0.010)


def test_initial_stop_rejects_flat() -> None:
    with pytest.raises(ValueError):
        initial_stop_price(
            side=Side.FLAT, close_price=1.0, atr_value=0.005, atr_stop_multiple=2.0
        )


def test_initial_stop_uses_close_not_post_slippage_entry() -> None:
    """Regression: the verifier originally passed ``entry_price`` (post-
    slippage ask + slip for long) as the base. The bespoke strategy
    anchors the stop at the bar's mid close. For a long with close=1.1500,
    ATR=0.005, multiple=2.0, slip=1 pip (0.0001):

      bespoke stop (correct)  = 1.1500 - 0.010 = 1.1400
      buggy verifier stop     = 1.1501 - 0.010 = 1.1401  (1 pip too high)

    A 1-pip stop offset accumulates into a systematic per-trade R
    difference. Pin the close-based behaviour here.
    """

    close = 1.1500
    bug_entry = 1.1501  # ask_close + slip for a long
    correct_stop = initial_stop_price(
        side=Side.LONG, close_price=close, atr_value=0.005, atr_stop_multiple=2.0
    )
    assert correct_stop == pytest.approx(1.1400)
    # Sanity: had we passed entry_price=bug_entry, we'd get a different
    # (higher) stop — but the function no longer accepts ``entry_price``,
    # so this construct cannot happen by accident.
    assert correct_stop != pytest.approx(bug_entry - 0.010)


# ---------- ratchet_trailing_stop ----------


def test_trailing_stop_long_ratchets_up_only() -> None:
    """A new long stop above the current stop replaces it; a lower
    candidate does not."""

    new_stop, moved = ratchet_trailing_stop(
        side=Side.LONG,
        current_stop=1.1400,
        bid_close=1.1600,
        ask_close=1.1605,
        atr_value=0.005,
        trailing_stop_atr_multiple=2.0,
    )
    # candidate = 1.16 - 0.01 = 1.15 > 1.14 -> ratchets
    assert moved is True
    assert new_stop == pytest.approx(1.15)

    new_stop2, moved2 = ratchet_trailing_stop(
        side=Side.LONG,
        current_stop=1.15,
        bid_close=1.1500,  # 1.15 - 0.01 = 1.14 < 1.15 -> no move
        ask_close=1.1505,
        atr_value=0.005,
        trailing_stop_atr_multiple=2.0,
    )
    assert moved2 is False
    assert new_stop2 == pytest.approx(1.15)


def test_trailing_stop_short_ratchets_down_only() -> None:
    new_stop, moved = ratchet_trailing_stop(
        side=Side.SHORT,
        current_stop=1.1000,
        bid_close=1.0790,
        ask_close=1.0795,
        atr_value=0.005,
        trailing_stop_atr_multiple=2.0,
    )
    # short candidate = 1.0795 + 0.01 = 1.0895 < 1.10 -> ratchets
    assert moved is True
    assert new_stop == pytest.approx(1.0895)

    new_stop2, moved2 = ratchet_trailing_stop(
        side=Side.SHORT,
        current_stop=1.0895,
        bid_close=1.0890,
        ask_close=1.0895,  # candidate = 1.0895 + 0.01 = 1.0995 > 1.0895 -> no move
        atr_value=0.005,
        trailing_stop_atr_multiple=2.0,
    )
    assert moved2 is False
    assert new_stop2 == pytest.approx(1.0895)


# ---------- evaluate_exit ----------


def test_exit_long_at_initial_stop_when_bid_low_breaks_it() -> None:
    out = evaluate_exit(
        side=Side.LONG,
        bid_high=1.0,
        bid_low=0.9,
        bid_close=0.95,
        ask_high=1.0,
        ask_low=0.9,
        ask_close=0.95,
        stop_price=0.92,
        has_trailed=False,
        bars_held=10,
        max_bars_in_trade=240,
        is_last_bar=False,
    )
    assert out.exit_now is True
    assert out.exit_price == pytest.approx(0.92)
    assert out.exit_reason is TradeExitReason.STOP


def test_exit_long_at_trailed_stop_uses_trailing_label() -> None:
    out = evaluate_exit(
        side=Side.LONG,
        bid_high=1.0,
        bid_low=0.9,
        bid_close=0.95,
        ask_high=1.0,
        ask_low=0.9,
        ask_close=0.95,
        stop_price=0.92,
        has_trailed=True,
        bars_held=10,
        max_bars_in_trade=240,
        is_last_bar=False,
    )
    assert out.exit_now is True
    assert out.exit_reason is TradeExitReason.TRAILING_STOP


def test_exit_short_at_stop_when_ask_high_pierces() -> None:
    out = evaluate_exit(
        side=Side.SHORT,
        bid_high=1.05,
        bid_low=1.0,
        bid_close=1.04,
        ask_high=1.06,
        ask_low=1.0,
        ask_close=1.05,
        stop_price=1.055,
        has_trailed=False,
        bars_held=5,
        max_bars_in_trade=240,
        is_last_bar=False,
    )
    assert out.exit_now is True
    assert out.exit_price == pytest.approx(1.055)
    assert out.exit_reason is TradeExitReason.STOP


def test_time_stop_fires_when_bars_held_reaches_max() -> None:
    out = evaluate_exit(
        side=Side.LONG,
        bid_high=1.0,
        bid_low=0.99,
        bid_close=0.995,
        ask_high=1.001,
        ask_low=0.991,
        ask_close=0.996,
        stop_price=0.50,  # safely below low — no stop trigger
        has_trailed=False,
        bars_held=240,
        max_bars_in_trade=240,
        is_last_bar=False,
    )
    assert out.exit_now is True
    assert out.exit_reason is TradeExitReason.TIME
    assert out.exit_price == pytest.approx(0.995)  # bid_close (long exits on bid)


def test_eod_exit_at_last_bar_when_no_other_trigger() -> None:
    out = evaluate_exit(
        side=Side.SHORT,
        bid_high=1.0,
        bid_low=0.99,
        bid_close=0.995,
        ask_high=1.001,
        ask_low=0.991,
        ask_close=0.996,
        stop_price=2.0,  # well above ask high
        has_trailed=False,
        bars_held=5,
        max_bars_in_trade=240,
        is_last_bar=True,
    )
    assert out.exit_now is True
    assert out.exit_reason is TradeExitReason.EOD
    assert out.exit_price == pytest.approx(0.996)  # ask_close (short exits on ask)


def test_no_exit_when_nothing_triggers() -> None:
    out = evaluate_exit(
        side=Side.LONG,
        bid_high=1.0,
        bid_low=0.99,
        bid_close=0.995,
        ask_high=1.001,
        ask_low=0.991,
        ask_close=0.996,
        stop_price=0.5,  # well below low
        has_trailed=False,
        bars_held=10,
        max_bars_in_trade=240,
        is_last_bar=False,
    )
    assert out.exit_now is False


def test_exit_precedence_stop_before_time() -> None:
    """If the stop AND the time stop both fire on the same bar, the
    spec says adverse stop wins."""

    out = evaluate_exit(
        side=Side.LONG,
        bid_high=1.0,
        bid_low=0.9,
        bid_close=0.95,
        ask_high=1.0,
        ask_low=0.9,
        ask_close=0.95,
        stop_price=0.92,  # bid_low (0.9) <= 0.92 -> stop fires
        has_trailed=False,
        bars_held=240,  # also at max
        max_bars_in_trade=240,
        is_last_bar=True,  # and last bar
    )
    assert out.exit_now is True
    assert out.exit_reason is TradeExitReason.STOP


# ---------- fill_entry_price ----------


def test_fill_entry_uses_ask_for_long_with_slippage() -> None:
    price = fill_entry_price(
        side=Side.LONG,
        bid_close=1.0999,
        ask_close=1.1001,
        spread_slippage_multiplier=0.5,
        fixed_slippage_pips=0.2,
        pip_size=0.0001,
    )
    # spread_pips = (1.1001 - 1.0999) / 0.0001 = 2.0
    # slip_pips = max(0.2, 2.0 * 0.5) = 1.0
    # long entry = ask + slip * pip = 1.1001 + 0.0001 = 1.1002
    assert price == pytest.approx(1.1002)


def test_fill_entry_short_subtracts_slippage_from_bid() -> None:
    price = fill_entry_price(
        side=Side.SHORT,
        bid_close=1.0999,
        ask_close=1.1001,
        spread_slippage_multiplier=0.5,
        fixed_slippage_pips=0.2,
        pip_size=0.0001,
    )
    # short entry = bid - slip * pip = 1.0999 - 0.0001 = 1.0998
    assert price == pytest.approx(1.0998)


def test_fill_entry_uses_fixed_floor_when_spread_is_tiny() -> None:
    price = fill_entry_price(
        side=Side.LONG,
        bid_close=1.0999,
        ask_close=1.0999,  # zero spread
        spread_slippage_multiplier=0.5,
        fixed_slippage_pips=0.2,
        pip_size=0.0001,
    )
    # slip_pips = max(0.2, 0 * 0.5) = 0.2
    # long = ask + 0.2 * pip = 1.0999 + 0.00002 = 1.09992
    assert price == pytest.approx(1.09992)


# ---------- size_position ----------


def test_size_position_eur_usd_basic() -> None:
    units = size_position(
        nav=500.0,
        risk_per_trade_pct=0.25,
        entry_price=1.1500,
        stop_price=1.1450,
        pip_size=0.0001,
        quote_currency="USD",
        base_currency="EUR",
        mid_price=1.1500,
    )
    # risk_amount = 500 * 0.0025 = 1.25
    # stop_distance_pips = 0.005 / 0.0001 = 50
    # pip_value_home = 0.0001 (USD-quoted)
    # raw = 1.25 / (50 * 0.0001) = 250
    assert units == 250


def test_size_position_usd_jpy_uses_pip_size_over_mid() -> None:
    units = size_position(
        nav=500.0,
        risk_per_trade_pct=0.25,
        entry_price=150.00,
        stop_price=149.50,
        pip_size=0.01,
        quote_currency="JPY",
        base_currency="USD",
        mid_price=150.00,
    )
    # risk_amount = 1.25
    # stop_distance_pips = 0.5 / 0.01 = 50
    # pip_value_home = 0.01 / 150.0 = 6.666...e-5
    # raw = 1.25 / (50 * 6.666e-5) = 375.0
    assert units == 375


def test_size_position_floors_to_whole_units() -> None:
    units = size_position(
        nav=500.0,
        risk_per_trade_pct=0.25,
        entry_price=1.1500,
        stop_price=1.1462,
        pip_size=0.0001,
        quote_currency="USD",
        base_currency="EUR",
        mid_price=1.1500,
    )
    # risk_amount = 1.25
    # stop_distance_pips = 0.0038 / 0.0001 = 38
    # raw = 1.25 / (38 * 0.0001) = 328.947... -> floor 328
    assert units == 328


def test_size_position_returns_zero_when_stop_distance_is_zero() -> None:
    units = size_position(
        nav=500.0,
        risk_per_trade_pct=0.25,
        entry_price=1.0,
        stop_price=1.0,
        pip_size=0.0001,
        quote_currency="USD",
        base_currency="EUR",
        mid_price=1.0,
    )
    assert units == 0


def test_size_position_rejects_unsupported_currency_pair() -> None:
    with pytest.raises(ValueError):
        size_position(
            nav=500.0,
            risk_per_trade_pct=0.25,
            entry_price=1.0,
            stop_price=0.99,
            pip_size=0.0001,
            quote_currency="EUR",
            base_currency="GBP",
            mid_price=1.0,
        )


# ---------- trade_pnl ----------


def test_trade_pnl_long_eur_usd() -> None:
    pnl = trade_pnl(
        side=Side.LONG,
        entry_price=1.1500,
        exit_price=1.1550,
        units=250,
        quote_currency="USD",
        base_currency="EUR",
    )
    # diff = 0.005 * 250 = 1.25
    assert pnl == pytest.approx(1.25)


def test_trade_pnl_short_eur_usd_negative_when_price_rises() -> None:
    pnl = trade_pnl(
        side=Side.SHORT,
        entry_price=1.1500,
        exit_price=1.1550,
        units=250,
        quote_currency="USD",
        base_currency="EUR",
    )
    assert pnl == pytest.approx(-1.25)


def test_trade_pnl_usd_jpy_converts_through_exit_price() -> None:
    pnl = trade_pnl(
        side=Side.LONG,
        entry_price=150.00,
        exit_price=151.00,
        units=375,
        quote_currency="JPY",
        base_currency="USD",
    )
    # gross_quote = 1.0 * 375 = 375 JPY
    # gross_home = 375 / 151 = 2.4834...
    assert pnl == pytest.approx(375 / 151)


def test_trade_pnl_rejects_unsupported_currency_pair() -> None:
    with pytest.raises(ValueError):
        trade_pnl(
            side=Side.LONG,
            entry_price=1.0,
            exit_price=1.01,
            units=100,
            quote_currency="EUR",
            base_currency="GBP",
        )
