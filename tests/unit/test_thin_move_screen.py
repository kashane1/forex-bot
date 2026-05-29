"""Unit tests for the H03 thin-move screen helpers (diagnostic-only)."""

from __future__ import annotations

import pytest

from forex_bot.research.thin_move_screen import (
    PARTICIPATION_BUCKETS,
    bucket_stats,
    fade_returns,
    low_tail_threshold,
    participation_label,
    tertile_edges,
)


def test_participation_buckets_order():
    assert PARTICIPATION_BUCKETS == ("low", "medium", "high")


def test_tertile_edges_and_participation_label():
    vals = [float(v) for v in range(1, 101)]  # 1..100
    edges = tertile_edges(vals)
    p33, p67 = edges
    assert p33 < p67
    # low volume -> thin -> "low"; high volume -> "high"
    assert participation_label(1.0, edges) == "low"
    assert participation_label(50.0, edges) == "medium"
    assert participation_label(100.0, edges) == "high"
    # boundary: value exactly at p33 is "low" (<=), just above p67 is "high"
    assert participation_label(p33, edges) == "low"
    assert participation_label(p67 + 0.01, edges) == "high"


def test_tertile_edges_validation():
    with pytest.raises(ValueError):
        tertile_edges([1.0])


def test_low_tail_threshold_picks_bottom_decile():
    vals = [float(v) for v in range(1, 101)]  # 1..100
    thr = low_tail_threshold(vals, frac=0.10)
    # bottom 10% of 1..100 -> ~1..10; upper edge ~10
    assert thr <= 11.0
    # everything <= thr is "ultra thin": should be roughly a tenth of the sample
    n_tail = sum(1 for v in vals if v <= thr)
    assert 8 <= n_tail <= 12


def test_low_tail_threshold_validation():
    with pytest.raises(ValueError):
        low_tail_threshold([], frac=0.10)
    with pytest.raises(ValueError):
        low_tail_threshold([1.0], frac=0.0)


def test_low_tail_is_low_side_mirror():
    # The low tail must select SMALL values, unlike the H16 top tail which selects large.
    vals = [float(v) for v in range(1, 101)]
    thr = low_tail_threshold(vals, frac=0.10)
    tail = [v for v in vals if v <= thr]
    assert max(tail) < 20.0  # genuinely the thin end


def test_reused_primitives_are_wired():
    # Smoke test that the re-exported generic helpers work through this module.
    f1 = fade_returns([100.0, 100.10], [-1, -1], 0.01, 1)
    assert f1[0] == pytest.approx(10.0)  # down-completion + rise => reversion
    s = bucket_stats([1.0, -1.0, 3.0, -1.0])
    assert s.reversion_rate == pytest.approx(0.5)
