"""Indicator tests with a focus on no-lookahead in Donchian."""

from __future__ import annotations

import pandas as pd
import pytest

from forex_bot.strategies.indicators import atr, donchian_high, donchian_low, ema


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
