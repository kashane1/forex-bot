"""Unit tests for the H16 overshoot-exhaustion screen helpers (diagnostic-only)."""

from __future__ import annotations

import pytest

from forex_bot.research.overshoot_exhaustion_screen import (
    autocorr_lag1,
    bucket_label,
    bucket_stats,
    conditional_followon_rate,
    fade_returns,
    permutation_null_group_mean,
    quantile_edges,
    to_pips,
    top_tail_threshold,
)


def test_to_pips():
    assert to_pips(0.30, 0.01) == pytest.approx(30.0)  # JPY
    assert to_pips(0.0003, 0.0001) == pytest.approx(3.0)  # non-JPY
    with pytest.raises(ValueError):
        to_pips(0.1, 0.0)


def test_fade_returns_sign_convention():
    # closes rising; an up-completion (dir +1) that keeps rising => continuation => fade<0.
    closes = [100.0, 100.10, 100.30]  # pip_size 0.01
    dirs = [1, 1, 1]
    f1 = fade_returns(closes, dirs, 0.01, 1)
    # bar0: -1*(100.10-100.00)/0.01 = -10 pips (continuation)
    assert f1[0] == pytest.approx(-10.0)
    assert f1[2] is None  # runs off the end
    # a down-completion (dir -1) followed by a rise => reversion => fade>0
    f1b = fade_returns([100.0, 100.10], [-1, -1], 0.01, 1)
    assert f1b[0] == pytest.approx(10.0)


def test_fade_returns_validation():
    with pytest.raises(ValueError):
        fade_returns([1.0, 2.0], [1, 1], 0.01, 0)
    with pytest.raises(ValueError):
        fade_returns([1.0, 2.0], [1], 0.01, 1)


def test_quantile_edges_and_bucket_label():
    vals = list(range(1, 101))  # 1..100
    edges = quantile_edges([float(v) for v in vals])
    assert bucket_label(1.0, edges) == "small"
    assert bucket_label(40.0, edges) == "medium"
    assert bucket_label(60.0, edges) == "large"
    assert bucket_label(100.0, edges) == "extreme"


def test_top_tail_threshold():
    vals = [float(v) for v in range(1, 101)]
    thr = top_tail_threshold(vals, frac=0.05)
    # top 5% of 1..100 -> ~96..100; lower edge ~96
    assert thr >= 95.0
    with pytest.raises(ValueError):
        top_tail_threshold([], frac=0.05)
    with pytest.raises(ValueError):
        top_tail_threshold([1.0], frac=1.5)


def test_bucket_stats_empty_and_basic():
    empty = bucket_stats([])
    assert empty.n == 0 and empty.mean is None
    s = bucket_stats([1.0, -1.0, 3.0, -1.0])
    assert s.n == 4
    assert s.mean == pytest.approx(0.5)
    assert s.reversion_rate == pytest.approx(0.5)  # 2 of 4 > 0


def test_autocorr_lag1():
    # perfectly increasing -> strong positive autocorr
    inc = [1.0, 2.0, 3.0, 4.0, 5.0]
    ac = autocorr_lag1(inc)
    assert ac is not None and ac > 0.3
    assert autocorr_lag1([1.0, 1.0]) is None  # too short
    assert autocorr_lag1([2.0, 2.0, 2.0]) is None  # zero variance


def test_conditional_followon_rate_clustering():
    # large-overshoot bars clustered together -> conditional rate > base rate (lift>1)
    labels = ["extreme", "extreme", "extreme", "small", "small", "small", "small", "small"]
    out = conditional_followon_rate(labels, target=("extreme",))
    assert out["base_rate"] == pytest.approx(3 / 8)
    # of the 3 'extreme' at positions with a successor (idx 0,1,2): successors are
    # extreme,extreme,small -> 2/3
    assert out["conditional_rate"] == pytest.approx(2 / 3, abs=1e-3)
    assert out["lift"] > 1.0


def test_permutation_null_is_deterministic_and_centered():
    # fades unrelated to group membership -> observed near null center, p not extreme.
    fades = [float(i % 5 - 2) for i in range(200)]  # repeating -2..2, mean 0
    in_group = [i < 50 for i in range(200)]  # arbitrary group, no relation to value
    a = permutation_null_group_mean(fades, in_group, draws=500, seed=7)
    b = permutation_null_group_mean(fades, in_group, draws=500, seed=7)
    assert a.as_dict() == b.as_dict()  # deterministic given seed
    assert a.n_group == 50
    # null mean ~ overall mean ~ 0
    assert abs(a.null_mean) < 0.5


def test_permutation_null_detects_real_group_signal():
    # group bars have systematically higher fade -> observed should sit high in null.
    fades = [5.0] * 30 + [0.0] * 170
    in_group = [True] * 30 + [False] * 170
    res = permutation_null_group_mean(fades, in_group, draws=500, seed=1)
    assert res.observed_mean == pytest.approx(5.0)
    assert res.one_sided_p_ge < 0.01  # observed far above null
    assert res.pct_rank > 0.99


def test_permutation_null_rejects_trivial_group():
    with pytest.raises(ValueError):
        permutation_null_group_mean([1.0, 2.0], [True, True], draws=10, seed=1)
