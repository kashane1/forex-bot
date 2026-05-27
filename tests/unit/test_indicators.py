"""Indicator tests with a focus on no-lookahead in Donchian."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from forex_bot.strategies.indicators import adx, atr, donchian_high, donchian_low, ema, rsi, zscore


def _series(values: list[float]) -> pd.Series:
    return pd.Series(values)


def test_ema_known_values():
    s = _series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    e = ema(s, 3)
    assert pd.notna(e.iloc[-1])
    # EMA with span=3 → alpha=2/(3+1)=0.5
    # iterative: start=1 → 1.5 → 2.25 → 3.125 → 4.0625 → ... rises monotonically
    assert e.iloc[-1] > e.iloc[-2]


def test_atr_positive():
    high = _series([1.05, 1.06, 1.04, 1.05, 1.07, 1.06, 1.05, 1.04, 1.06, 1.08, 1.09, 1.07, 1.08, 1.10])
    low = _series([1.03, 1.04, 1.02, 1.03, 1.05, 1.04, 1.03, 1.02, 1.04, 1.06, 1.07, 1.05, 1.06, 1.08])
    close = _series([1.04, 1.05, 1.03, 1.04, 1.06, 1.05, 1.04, 1.03, 1.05, 1.07, 1.08, 1.06, 1.07, 1.09])
    a = atr(high, low, close, length=5)
    assert pd.notna(a.iloc[-1])
    assert float(a.iloc[-1]) > 0


def test_donchian_excludes_current_bar():
    """Critical no-lookahead property: Donchian(N) at bar t equals max over
    bars t-N..t-1 (NOT including bar t)."""
    high = _series([1.0, 2.0, 3.0, 1.5, 1.2])
    low = _series([0.5, 1.0, 1.5, 0.8, 0.7])

    dh = donchian_high(high, length=3)
    # At index 3: window is bars 0..2 → max=3.0. The current high (1.5) must NOT influence.
    assert dh.iloc[3] == 3.0
    # At index 4: window is bars 1..3 → max(2.0, 3.0, 1.5) = 3.0
    assert dh.iloc[4] == 3.0

    dl = donchian_low(low, length=3)
    assert dl.iloc[3] == 0.5
    assert dl.iloc[4] == 0.8


def test_donchian_breakout_uses_prior_only():
    """If the current bar makes a new high, that should NOT prevent a breakout
    detection — the prior-bar Donchian must be lower than the current close."""
    high = _series([1.0, 1.0, 1.0, 2.0])
    low = _series([0.5, 0.5, 0.5, 1.5])
    close = _series([0.9, 0.9, 0.9, 1.9])
    dh = donchian_high(high, length=3)
    # At index 3: window=0..2 → max=1.0. Close=1.9 > 1.0 → breakout, correctly.
    assert dh.iloc[3] == 1.0
    assert close.iloc[3] > dh.iloc[3]


def test_indicator_invalid_length():
    s = _series([1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        ema(s, 0)
    with pytest.raises(ValueError):
        donchian_high(s, 0)
    with pytest.raises(ValueError):
        atr(s, s, s, 0)


def test_adx_strong_uptrend_is_high():
    """A clean monotone uptrend should drive ADX well above 25."""
    n = 80
    high = _series([1.0 + 0.01 * i for i in range(n)])
    low = _series([0.99 + 0.01 * i for i in range(n)])
    close = _series([0.995 + 0.01 * i for i in range(n)])
    a = adx(high, low, close, length=14)
    assert pd.notna(a.iloc[-1])
    assert float(a.iloc[-1]) > 25.0


def test_adx_flat_chop_is_low():
    """A noisy, directionless market should keep ADX low (no trend)."""
    rng = np.random.default_rng(42)
    n = 200
    # Mean-reverting noise around 1.00 — no sustained direction.
    close_vals = 1.00 + rng.normal(0, 0.002, n)
    close = _series(close_vals.tolist())
    high = _series((close_vals + np.abs(rng.normal(0, 0.001, n))).tolist())
    low = _series((close_vals - np.abs(rng.normal(0, 0.001, n))).tolist())
    a = adx(high, low, close, length=14)
    assert pd.notna(a.iloc[-1])
    assert float(a.iloc[-1]) < 25.0


def test_adx_bounded_0_100():
    rng = np.random.default_rng(7)
    n = 200
    close = _series((100 + rng.normal(0, 1, n).cumsum()).tolist())
    high = close + 0.5
    low = close - 0.5
    a = adx(high, low, close, length=14).dropna()
    assert (a >= 0).all()
    assert (a <= 100).all()


def test_adx_no_lookahead():
    """ADX at bar t must not change when future bars are appended."""
    n = 100
    high = _series([1.0 + 0.01 * i for i in range(n)])
    low = _series([0.99 + 0.01 * i for i in range(n)])
    close = _series([0.995 + 0.01 * i for i in range(n)])
    full = adx(high, low, close, length=14)
    truncated = adx(high.iloc[:60], low.iloc[:60], close.iloc[:60], length=14)
    # The value at index 59 must be identical whether or not bars 60..99 exist.
    assert abs(float(full.iloc[59]) - float(truncated.iloc[59])) < 1e-9


def test_adx_invalid_length():
    s = _series([1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        adx(s, s, s, 0)


def test_zscore_warmup_is_nan_not_zero():
    s = _series([1.0, 2.0, 3.0, 4.0, 5.0])
    z = zscore(s, length=3)
    assert pd.isna(z.iloc[0])
    assert pd.isna(z.iloc[1])
    assert pd.notna(z.iloc[2])


def test_zscore_no_lookahead():
    s = _series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    full = zscore(s, length=3)
    trunc = zscore(s.iloc[:5], length=3)
    assert abs(float(full.iloc[4]) - float(trunc.iloc[4])) < 1e-9


def test_rsi_early_bars_filled_to_50_not_nan():
    """RSI uses fillna(50.0) during warmup — strategies must gate on bar count."""
    s = _series([1.0, 1.1, 1.0, 1.2, 1.1, 1.3, 1.2, 1.4, 1.3, 1.5, 1.4, 1.6, 1.5, 1.7, 1.6])
    r = rsi(s, length=14)
    assert r.iloc[0] == 50.0
    assert r.iloc[-1] != 50.0 or len(s) > 20
