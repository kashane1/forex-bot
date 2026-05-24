"""Null-baseline tests.

Pin determinism (same seed → same per-seed mean), the descriptive band
output, and the cost-overlay integration.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from research.edge_discovery.costs import apply_cost_overlay
from research.edge_discovery.loaders import load_candles_csv
from research.edge_discovery.null import NullBaseline, compare_to_null, random_null_baseline

REPO_ROOT = Path(__file__).resolve().parents[3]
H4_FIXTURE = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_EUR_USD_H4.csv"


def _sample():
    return load_candles_csv(H4_FIXTURE)


def test_seeded_null_is_deterministic() -> None:
    sample = _sample()
    a = random_null_baseline(sample.frame, n_trades=50, window_bars=6, seeds=range(5))
    b = random_null_baseline(sample.frame, n_trades=50, window_bars=6, seeds=range(5))
    # Series-level equality of the per-seed means.
    assert list(a.per_seed_means) == list(b.per_seed_means)
    assert a.mean_of_means == b.mean_of_means


def test_null_with_cost_overlay_is_more_negative_than_pre_cost() -> None:
    sample = _sample()
    pre = random_null_baseline(sample.frame, n_trades=80, window_bars=6, seeds=range(10))
    post = random_null_baseline(
        sample.frame,
        n_trades=80,
        window_bars=6,
        seeds=range(10),
        apply_cost_overlay_fn=apply_cost_overlay,
        instrument="EUR_USD",
    )
    # Costs only subtract; per-seed and aggregate means must shift down.
    assert post.mean_of_means <= pre.mean_of_means


def test_null_requires_minimum_frame_length() -> None:
    sample = _sample()
    # Trim to fewer bars than window + 2
    tiny = sample.frame.iloc[:3]
    with pytest.raises(ValueError, match="need at least window_bars"):
        random_null_baseline(tiny, n_trades=5, window_bars=4)


def test_compare_to_null_band_within() -> None:
    null = NullBaseline(
        per_seed_means=__import__("pandas").Series([0.0001, -0.0001, 0.0, 0.0002, -0.0002]),
        mean_of_means=0.0,
        std_of_means=0.0002,
        n_trades_per_seed=10,
        window_bars=5,
        seeds_used=(0, 1, 2, 3, 4),
    )
    r = compare_to_null(0.0001, null)
    assert r["band"] == "within_null"


def test_compare_to_null_band_materially_above() -> None:
    null = NullBaseline(
        per_seed_means=__import__("pandas").Series([0.0001, 0.0, -0.0001, 0.0001, 0.0]),
        mean_of_means=0.0,
        std_of_means=0.0001,
        n_trades_per_seed=10,
        window_bars=5,
        seeds_used=(0, 1, 2, 3, 4),
    )
    r = compare_to_null(0.001, null)  # 10 null stds above
    assert r["band"] == "materially_above_null"


def test_compare_to_null_collapsed_std() -> None:
    import pandas as pd
    null = NullBaseline(
        per_seed_means=pd.Series([0.0]),
        mean_of_means=0.0,
        std_of_means=0.0,
        n_trades_per_seed=10,
        window_bars=5,
        seeds_used=(0,),
    )
    r = compare_to_null(0.001, null)
    assert r["band"] == "null_collapsed"
