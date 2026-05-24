"""Forward-window tests.

Pin the entry-bar mapping (signal close = entry, no look-ahead), the
side-signing convention (LONG = +, SHORT = -), the trailing-drop
semantics, and the label-passthrough behavior.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from research.edge_discovery.loaders import load_candles_csv
from research.edge_discovery.windows import Side, compute_forward_returns

REPO_ROOT = Path(__file__).resolve().parents[3]
H4_FIXTURE = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_EUR_USD_H4.csv"


def _sample():
    return load_candles_csv(H4_FIXTURE)


def test_long_window_matches_manual_log_return() -> None:
    sample = _sample()
    times = sample.frame.index
    sig = times[10]
    fr = compute_forward_returns(sample.frame, [sig], window_bars=5, side=Side.LONG)
    assert fr.n_signals == 1
    ep = sample.frame["close"].iloc[10]
    xp = sample.frame["close"].iloc[15]
    expected = np.log(xp / ep)
    assert abs(fr.per_signal["log_return"].iloc[0] - expected) < 1e-12


def test_short_window_flips_sign() -> None:
    sample = _sample()
    sig = sample.frame.index[20]
    long_fr = compute_forward_returns(sample.frame, [sig], window_bars=6, side=Side.LONG)
    short_fr = compute_forward_returns(sample.frame, [sig], window_bars=6, side=Side.SHORT)
    assert abs(long_fr.per_signal["log_return"].iloc[0] + short_fr.per_signal["log_return"].iloc[0]) < 1e-12


def test_trailing_signal_is_dropped_with_count() -> None:
    sample = _sample()
    times = sample.frame.index
    # First signal: 10 bars from end (window 5 fits — kept)
    # Second signal: last bar (no forward window — dropped)
    sig1 = times[-11]
    sig2 = times[-1]
    fr = compute_forward_returns(sample.frame, [sig1, sig2], window_bars=5)
    assert fr.n_signals == 1
    assert fr.dropped_trailing == 1


def test_missing_signal_after_frame_end_is_dropped_missing() -> None:
    sample = _sample()
    future = sample.frame.index[-1] + pd.Timedelta(hours=8)
    fr = compute_forward_returns(sample.frame, [future], window_bars=2)
    assert fr.n_signals == 0
    assert fr.dropped_missing == 1


def test_window_zero_raises() -> None:
    sample = _sample()
    with pytest.raises(ValueError, match="window_bars must be >= 1"):
        compute_forward_returns(sample.frame, [sample.frame.index[5]], window_bars=0)


def test_labels_are_threaded_through() -> None:
    sample = _sample()
    sigs = [sample.frame.index[i] for i in (10, 20, 30)]
    labels = ["NFP", "FOMC", "CPI"]
    fr = compute_forward_returns(sample.frame, sigs, window_bars=4, labels=labels)
    assert list(fr.per_signal["label"]) == labels


def test_labels_length_mismatch_raises() -> None:
    sample = _sample()
    sigs = [sample.frame.index[10]]
    with pytest.raises(ValueError, match="labels length must match"):
        compute_forward_returns(sample.frame, sigs, window_bars=3, labels=["A", "B"])


def test_frame_without_close_raises() -> None:
    bare = pd.DataFrame({"open": [1.0, 1.1]}, index=pd.to_datetime(["2024-01-01", "2024-01-02"], utc=True))
    with pytest.raises(ValueError, match="must have a 'close' column"):
        compute_forward_returns(bare, [bare.index[0]], window_bars=1)


def test_no_signals_returns_empty_frame() -> None:
    sample = _sample()
    fr = compute_forward_returns(sample.frame, [], window_bars=3)
    assert fr.n_signals == 0
    assert fr.per_signal.empty


def test_signal_in_middle_of_bar_snaps_to_next_close() -> None:
    """A signal whose timestamp falls *between* two bar closes pairs
    with the next bar's close, not the previous one — preventing
    accidental look-ahead onto a still-incomplete bar."""
    sample = _sample()
    closes = sample.frame.index
    in_between = closes[10] - pd.Timedelta(hours=2)
    fr = compute_forward_returns(sample.frame, [in_between], window_bars=3)
    assert fr.n_signals == 1
    # The entry bar should be closes[10] — the next close at or after the signal.
    assert fr.per_signal["signal_time"].iloc[0] == closes[10]
