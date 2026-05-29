"""Filter-ablation tests.

Pin cumulative / leave-one-out correctness, the sample-only-vs-adds-edge
distinction, sparsity flagging, pair-specific detection, and determinism.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from research.edge_discovery.filter_ablation import filter_ablation


def _signals() -> pd.DataFrame:
    """Construct a table where:
      - filter A genuinely raises expectancy (selects high-return rows),
      - filter B only shrinks the sample (random subset, same mean),
      - filter C hurts edge (selects low-return rows).
    """
    rng = np.random.default_rng(7)
    n = 600
    base = rng.normal(0.0, 1.0, size=n)
    pairs = rng.choice(["EUR_USD", "USD_JPY", "GBP_USD"], size=n)
    df = pd.DataFrame(
        {
            "instrument": pairs,
            "side": rng.choice(["long", "short"], size=n),
            "log_return": base,
        }
    )
    # Filter A: passes for the top-half of returns → raises mean.
    df["A"] = df["log_return"] > df["log_return"].median()
    # Filter B: random ~50% subset, independent of return → same mean.
    df["B"] = rng.random(n) < 0.5
    # Filter C: passes for the bottom third → lowers mean.
    df["C"] = df["log_return"] < df["log_return"].quantile(0.33)
    return df


def test_cumulative_and_leaveout_counts_are_correct() -> None:
    df = _signals()
    res = filter_ablation(df, filter_cols=["A", "B"], value_col="log_return", post_cost_col=None)
    # cumulative:1 == filter A subset count
    a_only = int(df["A"].sum())
    assert res.cumulative[0].n == a_only
    # cumulative:2 == A & B
    ab = int((df["A"] & df["B"]).sum())
    assert res.cumulative[1].n == ab
    # leave_out:A == subset where only B applies
    b_only = int(df["B"].sum())
    lo_a = next(s for s in res.leave_one_out if s.stage == "leave_out:A")
    assert lo_a.n == b_only


def test_adds_edge_vs_only_reduces_sample() -> None:
    df = _signals()
    res = filter_ablation(df, filter_cols=["A", "B", "C"], value_col="log_return", post_cost_col=None)
    by_f = {c.filter: c for c in res.contributions}
    assert "FILTER_ADDS_EDGE" in by_f["A"].flags
    assert "FILTER_ONLY_REDUCES_SAMPLE" in by_f["B"].flags
    assert "FILTER_HURTS_EDGE" in by_f["C"].flags
    # A's marginal gain should be clearly positive; C clearly negative.
    assert by_f["A"].marginal_expectancy_gain > 0
    assert by_f["C"].marginal_expectancy_gain < 0


def test_pair_specific_filter_flagged() -> None:
    rng = np.random.default_rng(3)
    n = 300
    df = pd.DataFrame(
        {
            "instrument": rng.choice(["EUR_USD", "USD_JPY"], size=n),
            "side": "long",
            "log_return": rng.normal(0.0, 1.0, size=n),
        }
    )
    # Filter P passes only on EUR_USD rows → single-pair survivor set.
    df["P"] = df["instrument"] == "EUR_USD"
    res = filter_ablation(df, filter_cols=["P"], value_col="log_return", post_cost_col=None)
    p = res.contributions[0]
    assert "FILTER_PAIR_SPECIFIC_ONLY" in p.flags


def test_sparse_filter_flagged() -> None:
    rng = np.random.default_rng(5)
    n = 200
    df = pd.DataFrame(
        {
            "instrument": rng.choice(["EUR_USD", "USD_JPY"], size=n),
            "side": "long",
            "log_return": rng.normal(0.0, 1.0, size=n),
        }
    )
    df["rare"] = False
    df.loc[df.index[:3], "rare"] = True  # only 3 pass
    res = filter_ablation(
        df, filter_cols=["rare"], value_col="log_return", post_cost_col=None, min_sample=20
    )
    assert "FILTER_TOO_SPARSE" in res.contributions[0].flags


def test_deterministic() -> None:
    df = _signals()
    a = filter_ablation(df, filter_cols=["A", "B", "C"], value_col="log_return", post_cost_col=None)
    b = filter_ablation(df, filter_cols=["A", "B", "C"], value_col="log_return", post_cost_col=None)
    assert a.to_dict() == b.to_dict()


def test_reduction_ratio_and_baseline() -> None:
    df = _signals()
    res = filter_ablation(df, filter_cols=["A"], value_col="log_return", post_cost_col=None)
    assert res.trigger_only.n == len(df)
    assert res.trigger_only.reduction_ratio == 0.0
    # all_filters == filter A here
    assert res.all_filters.n == int(df["A"].sum())
    assert 0.0 < res.all_filters.reduction_ratio < 1.0


def test_invalid_inputs_raise() -> None:
    df = _signals()
    with pytest.raises(ValueError, match="empty"):
        filter_ablation(pd.DataFrame(), filter_cols=["A"])
    with pytest.raises(ValueError, match="value_col"):
        filter_ablation(df, filter_cols=["A"], value_col="nope")
    with pytest.raises(ValueError, match="missing filter columns"):
        filter_ablation(df, filter_cols=["ZZZ"], value_col="log_return")
    with pytest.raises(ValueError, match="non-empty"):
        filter_ablation(df, filter_cols=[], value_col="log_return")


def test_post_cost_expectancy_populated() -> None:
    df = _signals()
    df["log_return_post_cost"] = df["log_return"] - 0.1
    res = filter_ablation(df, filter_cols=["A", "B"], value_col="log_return")
    assert res.trigger_only.post_cost_expectancy is not None
    assert res.trigger_only.post_cost_expectancy < res.trigger_only.expectancy
