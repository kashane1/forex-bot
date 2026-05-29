"""Unit tests for the CAMPAIGN_028 relative-value spread reversion screen.

Synthetic-only. These pin the screen's mechanics (beta estimation, no-lookahead
z-score, half-life, two-leg cost, side handling, candidate enumeration) and its
two boundary behaviours: a constructed mean-reverting (cointegrated) spread shows
a finite half-life and a positive pre-cost fade, while two independent random
walks do not produce a robust above-null fade.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from research.edge_discovery.relative_value_spread import (
    ar1_half_life,
    candidate_pairs,
    estimate_beta,
    rolling_z,
    screen_one_spread,
)


def _frame(prices: np.ndarray, start: str = "2020-01-01") -> pd.DataFrame:
    idx = pd.date_range(start, periods=len(prices), freq="4h", tz="UTC")
    return pd.DataFrame({"close": prices.astype(float)}, index=idx)


def _ou(n: int, *, phi: float, sigma: float, seed: int) -> np.ndarray:
    """Stationary AR(1)/OU series with autocorrelation ``phi``."""
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + rng.normal(0.0, sigma)
    return x


def _random_walk(n: int, *, sigma: float, seed: int, drift: float = 0.0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.cumsum(rng.normal(drift, sigma, size=n))


# ---------------------------------------------------------------------------
# Mechanics
# ---------------------------------------------------------------------------


def test_candidate_pairs_count_for_seven_majors() -> None:
    majors = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"]
    pairs = candidate_pairs(majors)
    assert len(pairs) == 21
    # unordered, sorted, no self-pairs, no duplicates
    assert all(a < b for a, b in pairs)
    assert len(set(pairs)) == 21


def test_estimate_beta_recovers_known_slope() -> None:
    common = _random_walk(2000, sigma=0.01, seed=1)
    lp2 = common
    lp1 = 1.5 * common  # beta_true = 1.5 exactly
    aligned = pd.DataFrame({"p1": np.exp(lp1), "p2": np.exp(lp2)})
    beta = estimate_beta(aligned)
    assert abs(beta - 1.5) < 0.05


def test_rolling_z_has_no_lookahead() -> None:
    # z_t must use stats strictly prior to t (shift(1)); changing s_t must not
    # change the mean/std used at t, only the numerator.
    s = pd.Series(np.linspace(0.0, 1.0, 200))
    lookback = 20
    z = rolling_z(s, lookback)
    i = 100
    mu_prior = s.iloc[i - lookback:i].mean()
    sd_prior = s.iloc[i - lookback:i].std(ddof=1)
    expected = (s.iloc[i] - mu_prior) / sd_prior
    assert abs(z.iloc[i] - expected) < 1e-9


def test_ar1_half_life_finite_for_reverting_series() -> None:
    s = _ou(3000, phi=0.8, sigma=0.01, seed=7)
    out = ar1_half_life(s)
    assert out["ar1_phi"] is not None
    assert 0.0 < out["ar1_phi"] < 1.0
    assert out["half_life_bars"] is not None
    # phi≈0.8 → half-life ≈ -ln2/ln0.8 ≈ 3.1 bars
    assert 1.0 < out["half_life_bars"] < 8.0


def test_ar1_half_life_none_for_random_walk() -> None:
    s = _random_walk(3000, sigma=0.01, seed=9)
    out = ar1_half_life(s)
    # a unit-root series has phi≈1 → no finite reversion half-life
    assert out["half_life_bars"] is None or out["half_life_bars"] > 200


# ---------------------------------------------------------------------------
# Boundary behaviours
# ---------------------------------------------------------------------------


def test_cointegrated_spread_shows_reverting_fade() -> None:
    n = 3000
    common = _random_walk(n, sigma=0.001, seed=3)
    spread = _ou(n, phi=0.85, sigma=0.01, seed=4)  # stationary, half-life ~4 bars
    p2 = np.exp(common)
    p1 = np.exp(1.0 * common + spread)  # ln p1 - ln p2 = spread (stationary)
    res = screen_one_spread(
        _frame(p1), _frame(p2),
        instrument1="EUR_USD", instrument2="GBP_USD",
        lookback=30, threshold=1.5, window_bars=8, seeds=range(10),
    )
    assert res.half_life_bars is not None and res.half_life_bars < 30
    # fading z-extremes on a genuinely reverting spread is pre-cost positive
    assert res.pre_cost_mean > 0
    # and carries information vs random timing on the same spread
    assert res.null_band in ("slightly_above_null", "materially_above_null")


def test_random_walk_pair_has_no_genuine_short_half_life() -> None:
    # Two independent random walks → the spread is itself a unit-root process.
    # Its in-sample fade CAN look spuriously above-null (that is exactly the
    # hazard the basket-level selection test below exists to catch), so we
    # assert the honest *structural* property instead: no genuine short
    # mean-reversion half-life.
    n = 3000
    p1 = np.exp(_random_walk(n, sigma=0.002, seed=11))
    p2 = np.exp(_random_walk(n, sigma=0.002, seed=12))
    res = screen_one_spread(
        _frame(p1), _frame(p2),
        instrument1="EUR_USD", instrument2="USD_JPY",
        lookback=30, threshold=1.5, window_bars=8, seeds=range(10),
    )
    assert res.half_life_bars is None or res.half_life_bars > 100


def test_basket_of_random_walk_spreads_flags_selection_noise() -> None:
    # The gate that actually matters: across many non-cointegrated spreads, the
    # best post-cost expectancy must be indistinguishable from best-of-N noise.
    from research.edge_discovery.multiple_comparison import matrix_sanity

    means = []
    for k in range(12):
        p1 = np.exp(_random_walk(2500, sigma=0.002, seed=100 + 2 * k))
        p2 = np.exp(_random_walk(2500, sigma=0.002, seed=101 + 2 * k))
        res = screen_one_spread(
            _frame(p1), _frame(p2),
            instrument1="EUR_USD", instrument2="GBP_USD",
            lookback=30, threshold=1.5, window_bars=8, seeds=range(6),
        )
        means.append(res.post_cost_mean)
    table = pd.DataFrame({"label": [f"rw_{i}" for i in range(len(means))], "expectancy_r": means})
    ms = matrix_sanity(
        table, metric_col="expectancy_r", label_col="label",
        higher_is_better=True, null_reference=0.0, seed=1,
    )
    assert "ROBUST_MATRIX_SIGNAL" not in ms.flags


def test_two_leg_cost_reduces_expectancy() -> None:
    n = 2500
    common = _random_walk(n, sigma=0.001, seed=5)
    spread = _ou(n, phi=0.85, sigma=0.01, seed=6)
    p1 = np.exp(common + spread)
    p2 = np.exp(common)
    res = screen_one_spread(
        _frame(p1), _frame(p2),
        instrument1="EUR_USD", instrument2="GBP_USD",
        lookback=30, threshold=1.5, window_bars=8, seeds=range(8),
    )
    # cost is strictly subtractive on both legs
    assert res.post_cost_mean < res.pre_cost_mean
    assert res.two_leg_cost_fraction > 0
