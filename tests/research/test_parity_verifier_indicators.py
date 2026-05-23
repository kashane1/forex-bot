"""Fixture-level tests for the verifier's independent indicators.

Expected values are hand-computed from the canonical definitions in
``docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md`` §3 — never copied
from the bespoke engine. NaN handling, warmup length, and the
prior-bar Donchian convention are all explicitly pinned.
"""

from __future__ import annotations

from math import isnan

import pytest
from research.parity_verifier.indicators import atr, donchian_high, donchian_low, ema


def test_ema_rejects_zero_length() -> None:
    with pytest.raises(ValueError):
        ema([1.0, 2.0, 3.0], 0)


def test_ema_warmup_is_nan_until_length_samples() -> None:
    values = [1.0, 1.0, 1.0, 1.0, 1.0]
    out = ema(values, 3)
    assert isnan(out[0])
    assert isnan(out[1])
    assert out[2] == pytest.approx(1.0)
    assert out[3] == pytest.approx(1.0)
    assert out[4] == pytest.approx(1.0)


def test_ema_constant_series_returns_constant() -> None:
    out = ema([7.0] * 10, 4)
    for value in out[3:]:
        assert value == pytest.approx(7.0)


def test_ema_known_values_length_three() -> None:
    """Hand-derived EMA(3) with alpha = 2/(L+1) = 0.5.

    seed at index 2: avg(values[:3]) is *not* used by the
    ``ewm(adjust=False)`` convention — instead the recursion is seeded
    at the third sample's value (pandas behaviour). After that:

        ema[3] = 0.5 * 4 + 0.5 * 3 = 3.5
        ema[4] = 0.5 * 5 + 0.5 * 3.5 = 4.25
        ema[5] = 0.5 * 6 + 0.5 * 4.25 = 5.125
    """

    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    out = ema(values, 3)
    assert isnan(out[0]) and isnan(out[1])
    assert out[2] == pytest.approx(3.0)
    assert out[3] == pytest.approx(3.5)
    assert out[4] == pytest.approx(4.25)
    assert out[5] == pytest.approx(5.125)


def test_ema_alpha_is_two_over_l_plus_one() -> None:
    """A long series of zeros followed by a single ``1`` exposes alpha
    directly: after the shock, the next sample is alpha × 1 + (1-alpha) × 0."""

    length = 9  # alpha = 0.2
    values = [0.0] * length + [1.0, 0.0, 0.0]
    out = ema(values, length)
    # ema[length-1] is the seed at the last zero, so still 0.
    assert out[length - 1] == pytest.approx(0.0)
    # ema[length] = 0.2 * 1 + 0.8 * 0 = 0.2
    assert out[length] == pytest.approx(0.2)
    # ema[length+1] = 0.2 * 0 + 0.8 * 0.2 = 0.16
    assert out[length + 1] == pytest.approx(0.16)


def test_atr_rejects_zero_length() -> None:
    with pytest.raises(ValueError):
        atr([1.0], [1.0], [1.0], 0)


def test_atr_rejects_mismatched_inputs() -> None:
    with pytest.raises(ValueError):
        atr([1.0, 2.0], [1.0], [1.0], 14)


def test_atr_warmup_is_nan() -> None:
    highs = [1.0] * 5
    lows = [0.5] * 5
    closes = [0.75] * 5
    out = atr(highs, lows, closes, 3)
    assert isnan(out[0]) and isnan(out[1])
    assert out[2] == pytest.approx((1.0 - 0.5 + 1.0 - 0.5 + 1.0 - 0.5) / 3)


def test_atr_first_tr_uses_high_minus_low_when_no_prev_close() -> None:
    out = atr([2.0], [1.0], [1.5], 1)
    assert out[0] == pytest.approx(1.0)


def test_atr_handles_gap_correctly() -> None:
    """A gap between close[i-1] and high[i]/low[i] should make TR larger
    than (high-low). Choose values so the gap dominates."""

    highs = [10.0, 12.0, 12.5]
    lows = [9.5, 11.8, 11.9]
    closes = [9.6, 11.9, 12.0]
    # TR[0] = 10 - 9.5 = 0.5
    # TR[1] = max(12 - 11.8, |12 - 9.6|, |11.8 - 9.6|) = max(0.2, 2.4, 2.2) = 2.4
    # TR[2] = max(12.5 - 11.9, |12.5 - 11.9|, |11.9 - 11.9|) = max(0.6, 0.6, 0.0) = 0.6
    # ATR(3) seed at index 2 = mean(0.5, 2.4, 0.6) = 1.1666...
    out = atr(highs, lows, closes, 3)
    assert out[2] == pytest.approx((0.5 + 2.4 + 0.6) / 3)


def test_atr_wilder_recursion() -> None:
    """Construct a fixture where TR is constant for the seed window and
    then receives a single shock — exposes the Wilder alpha = 1/L."""

    length = 4
    # Constant H-L=1.0 for the first `length` bars, then a shock bar.
    highs = [1.0, 2.0, 3.0, 4.0, 6.0]
    lows = [0.0, 1.0, 2.0, 3.0, 4.0]
    closes = [0.5, 1.5, 2.5, 3.5, 5.0]
    # TR_0 = high - low = 1.0
    # TR_1 = max(1.0, |2.0-0.5|, |1.0-0.5|) = 1.5
    # TR_2 = max(1.0, |3.0-1.5|, |2.0-1.5|) = 1.5
    # TR_3 = max(1.0, |4.0-2.5|, |3.0-2.5|) = 1.5
    # seed at index 3 = (1.0 + 1.5 + 1.5 + 1.5) / 4 = 1.375
    # TR_4 = max(6-4, |6-3.5|, |4-3.5|) = max(2.0, 2.5, 0.5) = 2.5
    # ATR_4 = (1/4) * 2.5 + (3/4) * 1.375 = 0.625 + 1.03125 = 1.65625
    out = atr(highs, lows, closes, length)
    assert out[3] == pytest.approx(1.375)
    assert out[4] == pytest.approx(1.65625)


def test_donchian_high_uses_prior_bars_only() -> None:
    """Spec: ``donchian_high[t] = max(high[t-L..t-1])`` — *not* including
    the current bar. A fixture where high[t] is higher than every prior
    high must still produce the prior maximum."""

    highs = [1.0, 2.0, 3.0, 4.0, 5.0, 100.0]
    out = donchian_high(highs, 3)
    # i < 3: NaN
    assert isnan(out[0]) and isnan(out[1]) and isnan(out[2])
    # i=3: max(high[0..2]) = max(1, 2, 3) = 3
    assert out[3] == pytest.approx(3.0)
    # i=4: max(high[1..3]) = max(2, 3, 4) = 4
    assert out[4] == pytest.approx(4.0)
    # i=5: max(high[2..4]) = max(3, 4, 5) = 5 — the 100 does NOT enter
    assert out[5] == pytest.approx(5.0)


def test_donchian_low_uses_prior_bars_only() -> None:
    lows = [5.0, 4.0, 3.0, 2.0, 1.0, 0.5]
    out = donchian_low(lows, 3)
    assert isnan(out[0]) and isnan(out[1]) and isnan(out[2])
    assert out[3] == pytest.approx(3.0)
    assert out[4] == pytest.approx(2.0)
    assert out[5] == pytest.approx(1.0)  # 0.5 not included


def test_donchian_breakout_against_prior_high() -> None:
    """Make sure the spec convention is correct: a close at the high of
    bar t must be *strictly above* donchian_high[t] (which equals the
    max of the prior L bars) to be a breakout."""

    highs = [1.0, 1.0, 1.0, 1.0, 1.5]
    closes = [1.0, 1.0, 1.0, 1.0, 1.5]
    dh = donchian_high(highs, 3)
    # at i=4: donchian = max(high[1..3]) = 1.0; close[4] = 1.5; breakout because 1.5 > 1.0.
    assert dh[4] == pytest.approx(1.0)
    assert closes[4] > dh[4]


def test_donchian_rejects_zero_length() -> None:
    with pytest.raises(ValueError):
        donchian_high([1.0, 2.0], 0)
    with pytest.raises(ValueError):
        donchian_low([1.0, 2.0], 0)


def test_indicators_handle_short_input_gracefully() -> None:
    out = ema([1.0, 2.0], 5)
    assert all(isnan(x) for x in out)
    out_atr = atr([1.0], [0.5], [0.75], 3)
    assert all(isnan(x) for x in out_atr)
    out_dch = donchian_high([1.0, 2.0], 3)
    assert all(isnan(x) for x in out_dch)
