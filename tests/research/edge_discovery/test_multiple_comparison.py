"""Multiple-comparison / selection-noise tests.

Pin determinism, robust-vs-noise classification, too-many-variants flagging,
pair-holdout fragility, the below-null INCONCLUSIVE case, small matrices, and
input validation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from research.edge_discovery.multiple_comparison import (
    holdout_stability,
    matrix_sanity,
)


def _matrix(values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {"candidate_id": [f"C{i:03d}" for i in range(len(values))], "expectancy_r": values}
    )


def test_deterministic() -> None:
    tbl = _matrix(list(np.random.default_rng(0).normal(0, 0.02, 16)))
    a = matrix_sanity(tbl, metric_col="expectancy_r", label_col="candidate_id",
                      null_reference=0.0, null_std=0.02, seed=42)
    b = matrix_sanity(tbl, metric_col="expectancy_r", label_col="candidate_id",
                      null_reference=0.0, null_std=0.02, seed=42)
    assert a.prob_best_le_null_max == b.prob_best_le_null_max
    assert a.expected_max_under_null == b.expected_max_under_null
    assert a.to_dict() == b.to_dict()


def test_robust_outlier_identified() -> None:
    vals = list(np.random.default_rng(1).normal(0.0, 0.02, 15)) + [0.5]
    tbl = _matrix(vals)
    res = matrix_sanity(tbl, metric_col="expectancy_r", label_col="candidate_id",
                        null_reference=0.0, null_std=0.02, seed=0)
    assert res.best_value == 0.5
    assert res.best_vs_null > 0
    assert res.prob_best_le_null_max < 0.05
    assert "ROBUST_MATRIX_SIGNAL" in res.flags
    assert "LIKELY_SELECTION_NOISE" not in res.flags


def test_selection_noise_identified() -> None:
    # All variants are pure noise around the null; the best is just max-of-noise.
    vals = list(np.random.default_rng(2).normal(0.0, 0.02, 20))
    tbl = _matrix(vals)
    res = matrix_sanity(tbl, metric_col="expectancy_r", label_col="candidate_id",
                        null_reference=0.0, null_std=0.02, seed=0)
    assert "LIKELY_SELECTION_NOISE" in res.flags
    assert "ROBUST_MATRIX_SIGNAL" not in res.flags
    assert res.prob_best_le_null_max > 0.05


def test_below_null_is_inconclusive() -> None:
    # C025/C026-like: every candidate net-negative and below the null floor.
    vals = list(np.random.default_rng(3).normal(-0.14, 0.02, 16))
    tbl = _matrix(vals)
    res = matrix_sanity(tbl, metric_col="expectancy_r", label_col="candidate_id",
                        null_reference=-0.0029, null_std=0.02, seed=0)
    assert res.best_vs_null < 0
    assert "INCONCLUSIVE" in res.flags
    assert "LIKELY_SELECTION_NOISE" in res.flags
    assert "ROBUST_MATRIX_SIGNAL" not in res.flags


def test_too_many_variants_flagged() -> None:
    vals = list(np.random.default_rng(4).normal(0.0, 0.02, 60))
    tbl = _matrix(vals)
    res = matrix_sanity(tbl, metric_col="expectancy_r", label_col="candidate_id",
                        null_reference=0.0, null_std=0.02, seed=0, too_many_variants=50)
    assert "TOO_MANY_VARIANTS_FOR_EVIDENCE" in res.flags


def test_pair_holdout_fragility() -> None:
    vals = list(np.random.default_rng(5).normal(0.0, 0.02, 10)) + [0.3]
    tbl = _matrix(vals)
    # Best variant's edge comes entirely from one pair; dropping it flips sign.
    pair_values = {"EUR_USD": 1.0, "USD_JPY": -0.1, "GBP_USD": -0.1}
    res = matrix_sanity(
        tbl, metric_col="expectancy_r", label_col="candidate_id",
        null_reference=0.0, null_std=0.02, seed=0,
        best_group_values=pair_values,
    )
    assert res.pair_holdout is not None
    assert res.pair_holdout.sign_flips
    assert "FRAGILE_SINGLE_PAIR_RESULT" in res.flags
    assert res.fragility_score >= 0.75


def test_holdout_stability_weighted_mean() -> None:
    # Weighted leave-one-out: heavy pair dominates.
    values = {"A": 0.10, "B": -0.02, "C": -0.02}
    weights = {"A": 100, "B": 10, "C": 10}
    h = holdout_stability(values, kind="pair", weights=weights, higher_is_better=True)
    # Full weighted mean is positive (A dominates); dropping A flips it negative.
    assert h.full_value > 0
    assert h.leave_one_out["A"] < 0
    assert h.sign_flips
    assert h.dominant_group == "A"


def test_lower_is_better_path() -> None:
    # e.g. a cost metric where lower is better.
    vals = [0.5, 0.4, 0.05, 0.45]
    tbl = pd.DataFrame({"candidate_id": ["a", "b", "c", "d"], "cost": vals})
    res = matrix_sanity(tbl, metric_col="cost", label_col="candidate_id",
                        higher_is_better=False, null_reference=0.5, null_std=0.05, seed=0)
    assert res.best_label == "c"  # lowest cost
    assert res.best_value == 0.05
    assert res.best_vs_null > 0  # better than null in "lower is better" space


def test_small_matrix() -> None:
    res = matrix_sanity(_matrix([0.01, 0.02]), metric_col="expectancy_r",
                        label_col="candidate_id", null_reference=0.0, null_std=0.02, seed=0)
    assert res.n_variants == 2
    assert res.best_value == 0.02


def test_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError, match="empty"):
        matrix_sanity(pd.DataFrame(), metric_col="expectancy_r", label_col="candidate_id")
    with pytest.raises(ValueError, match="missing column"):
        matrix_sanity(_matrix([0.1]), metric_col="nope", label_col="candidate_id")
    with pytest.raises(ValueError, match="empty"):
        holdout_stability({}, kind="pair")
