"""Unit tests for the read-only volatility-compression → expansion taxonomy.

Synthetic M15 frames are constructed to exercise:
  * compression detection (true / false) for each feature,
  * expansion magnitude + breakout / follow-through / false-breakout labels,
  * the no-lookahead guarantee: truncating the frame at bar ``i`` must not change any
    compression feature value at ``i`` (expansion labels, by contrast, *do* depend on
    future bars).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from forex_bot.research.volatility_compression_expansion import (
    COMPRESSION_FEATURES,
    CompressionExpansionParams,
    breakout_followthrough,
    breakout_labels,
    compute_compression_features,
    compute_expansion_labels,
    false_breakout,
    forward_range_pips,
    inside_bar_count,
    session_bucket,
)

PIP = 0.01
PARAMS = CompressionExpansionParams()


def _frame(highs, lows, closes, *, start="2023-01-03T00:00:00+00:00") -> pd.DataFrame:
    n = len(closes)
    t0 = datetime.fromisoformat(start)
    idx = pd.DatetimeIndex([t0 + timedelta(minutes=15 * k) for k in range(n)])
    opens = [closes[0]] + list(closes[:-1])
    return pd.DataFrame(
        {"mid_o": opens, "mid_h": highs, "mid_l": lows, "mid_c": closes}, index=idx
    )


def _synthetic_compressed_then_expand(n_calm=200, n_expand=40, n_recalm=60):
    """Calm (tiny ranges) → expansion (large ranges) → calm again.

    The trailing-window percentile is only discriminating across a *mix* of regimes:
    an expansion bar reads HIGH vs its (mostly calm) trailing window, and a post-
    expansion calm bar reads LOW vs its (expansion-containing) trailing window.
    """
    rng = np.random.default_rng(0)
    highs, lows, closes = [], [], []
    price = 150.0

    def push(half_range, drift_sd):
        nonlocal price
        price += rng.normal(0, drift_sd)
        highs.append(price + half_range)
        lows.append(price - half_range)
        closes.append(price)

    for _ in range(n_calm):
        push(0.02, 0.01)
    for _ in range(n_expand):
        push(0.40, 0.30)
    for _ in range(n_recalm):
        push(0.02, 0.01)
    return _frame(highs, lows, closes)


# --------------------------------------------------------------------------- #
# Compression
# --------------------------------------------------------------------------- #
def test_compression_features_present_and_aligned():
    f = _synthetic_compressed_then_expand()
    feats = compute_compression_features(f, PARAMS)
    assert set(feats.columns) == set(COMPRESSION_FEATURES)
    assert len(feats) == len(f)
    assert feats.index.equals(f.index)


def test_calm_regime_reads_as_compressed_percentile():
    """An expansion bar reads HIGH percentile vs its trailing (mostly calm) window; a
    post-expansion calm bar reads LOW vs its (expansion-containing) trailing window."""
    f = _synthetic_compressed_then_expand(n_calm=200, n_expand=40, n_recalm=60)
    feats = compute_compression_features(f, PARAMS)
    expand_idx = 210  # inside the expansion block
    recalm_idx = len(f) - 1  # calm again, trailing window still holds expansion bars
    assert feats["range_pct"].iloc[expand_idx] > 0.8
    assert feats["atr_pct"].iloc[expand_idx] > 0.8
    assert feats["range_pct"].iloc[recalm_idx] < 0.4
    assert feats["atr_pct"].iloc[recalm_idx] < feats["atr_pct"].iloc[expand_idx]


def test_inside_bar_count_detects_contraction():
    # bar0 wide; bars 1..3 progressively inside; bar4 breaks out (not inside)
    highs = [151.0, 150.8, 150.6, 150.5, 152.0]
    lows = [149.0, 149.2, 149.4, 149.5, 148.0]
    closes = [150.0, 150.0, 150.0, 150.0, 151.0]
    f = _frame(highs, lows, closes)
    ib = inside_bar_count(f, PARAMS)
    assert ib.iloc[0] == 0
    assert ib.iloc[3] == 3  # three consecutive inside bars
    assert ib.iloc[4] == 0  # break resets


# --------------------------------------------------------------------------- #
# Expansion
# --------------------------------------------------------------------------- #
def test_forward_range_pips_magnitude():
    # flat then a big move 4 bars ahead
    highs = [150.1, 150.1, 150.1, 150.1, 151.0, 150.1]
    lows = [149.9, 149.9, 149.9, 149.9, 149.0, 149.9]
    closes = [150.0, 150.0, 150.0, 150.0, 150.5, 150.0]
    f = _frame(highs, lows, closes)
    fr = forward_range_pips(f, 4)
    # from bar 1, the window bars 2..5 includes the wide bar 4 (high 151.0, low 149.0)
    assert fr.iloc[1] >= (151.0 - 149.0) / PIP - 1e-6


def test_breakout_up_and_followthrough():
    p = CompressionExpansionParams(range_lookback=4, atr_len=3, followthrough_atr_frac=0.1)
    # tight prior range ~[149.9,150.1], then a strong up-break that holds
    highs = [150.1, 150.1, 150.1, 150.1, 150.1, 150.6, 151.2, 151.5]
    lows = [149.9, 149.9, 149.9, 149.9, 149.9, 150.0, 150.4, 150.8]
    closes = [150.0, 150.0, 150.0, 150.0, 150.0, 150.5, 151.1, 151.4]
    f = _frame(highs, lows, closes)
    bl = breakout_labels(f, 3, p)
    ft = breakout_followthrough(f, 3, p)
    # decision bar 4: prior range over bars0..3, future bars 5..7 break up and hold
    assert bool(bl["breakout_up"].iloc[4])
    assert bool(ft.iloc[4])


def test_false_breakout_returns_inside():
    p = CompressionExpansionParams(range_lookback=4, atr_len=3, followthrough_atr_frac=0.1)
    # break up on the next bar then close back well inside the prior range by horizon end
    highs = [150.1, 150.1, 150.1, 150.1, 150.1, 150.6, 150.15, 150.05]
    lows = [149.9, 149.9, 149.9, 149.9, 149.9, 150.0, 149.95, 149.90]
    closes = [150.0, 150.0, 150.0, 150.0, 150.0, 150.5, 150.0, 149.95]
    f = _frame(highs, lows, closes)
    fb = false_breakout(f, 3, p)
    assert bool(fb.iloc[4])


# --------------------------------------------------------------------------- #
# No-lookahead causality
# --------------------------------------------------------------------------- #
def test_compression_features_have_no_lookahead():
    """Truncating the frame at bar i must not change any compression value at i."""
    f = _synthetic_compressed_then_expand()
    full = compute_compression_features(f, PARAMS)
    for i in (120, 160, 199, 220):
        trunc = compute_compression_features(f.iloc[: i + 1], PARAMS)
        for col in full.columns:
            a, b = full[col].iloc[i], trunc[col].iloc[i]
            if pd.isna(a) and pd.isna(b):
                continue
            assert a == b or abs(a - b) < 1e-9, f"lookahead in {col} at i={i}: {a} vs {b}"


def test_expansion_labels_do_depend_on_future():
    """Sanity: expansion labels SHOULD change when future bars are withheld (they are
    forward-looking by design)."""
    f = _synthetic_compressed_then_expand()
    h = 8
    full = compute_expansion_labels(f, PARAMS)
    i = 150
    # withholding everything after i makes the forward window unavailable -> NaN
    trunc = compute_expansion_labels(f.iloc[: i + 1], PARAMS)
    assert not pd.isna(full[f"fwd_range_pips_h{h}"].iloc[i])
    assert pd.isna(trunc[f"fwd_range_pips_h{h}"].iloc[i])


# --------------------------------------------------------------------------- #
# Session classifier
# --------------------------------------------------------------------------- #
def test_session_bucket_known_instants():
    # 13:00 UTC in January = 08:00 ET (NY open, also London active) -> overlap
    assert session_bucket(datetime(2023, 1, 10, 13, 0, tzinfo=UTC)) == "london_ny_overlap"
    # 22:00 UTC = 17:00 ET -> rollover
    assert session_bucket(datetime(2023, 1, 10, 22, 0, tzinfo=UTC)) == "rollover"
    # 02:00 UTC = 11:00 JST (Tokyo active), London/NY closed -> tokyo
    assert session_bucket(datetime(2023, 1, 10, 2, 0, tzinfo=UTC)) == "tokyo"


def test_session_bucket_requires_tzaware():
    import pytest

    with pytest.raises(ValueError):
        session_bucket(datetime(2023, 1, 10, 13, 0))
