"""Matched-null benchmark tests.

Pin: every mode runs, determinism under a seed, structure preservation
(trade/side counts), sparse-bucket handling, cost-overlay integration, input
validation, and the descriptive interpretation flags. No broker, no lockbox.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from research.edge_discovery.costs import apply_cost_overlay
from research.edge_discovery.matched_nulls import (
    MATCHED_NULL_MODES,
    interpret_matched_null,
    matched_null_baseline,
    session_bucket_utc,
    weekday_utc,
)


def _frame(seed: int, n: int = 1500, start: str = "2021-01-04 00:00") -> pd.DataFrame:
    """A positive random-walk H4 close series, UTC-indexed."""
    rng = np.random.default_rng(seed)
    steps = rng.normal(0.0, 0.0015, size=n)
    closes = 1.10 * np.exp(np.cumsum(steps))
    idx = pd.date_range(start=start, periods=n, freq="4h", tz="UTC")
    return pd.DataFrame({"close": closes}, index=idx)


def _frames() -> dict[str, pd.DataFrame]:
    return {"EUR_USD": _frame(1), "USD_JPY": _frame(2)}


def _ledger(frames: dict[str, pd.DataFrame], *, n_per_pair: int = 30) -> pd.DataFrame:
    """A small mixed-side ledger drawn from the frames' timestamps."""
    rows = []
    rng = np.random.default_rng(99)
    for pair, frame in frames.items():
        # Use mid-frame timestamps so there's always forward room.
        positions = rng.integers(50, len(frame) - 100, size=n_per_pair)
        for k, pos in enumerate(sorted(positions)):
            rows.append(
                {
                    "instrument": pair,
                    "side": "long" if k % 2 == 0 else "short",
                    "entry_time": frame.index[int(pos)],
                    "bars_held": int(6 + (k % 5) * 2),
                }
            )
    return pd.DataFrame(rows)


def test_session_and_weekday_helpers() -> None:
    assert session_bucket_utc(pd.Timestamp("2021-01-04 03:00", tz="UTC")) == "asia"
    assert session_bucket_utc(pd.Timestamp("2021-01-04 08:00", tz="UTC")) == "london"
    assert session_bucket_utc(pd.Timestamp("2021-01-04 13:00", tz="UTC")) == "london_ny_overlap"
    assert session_bucket_utc(pd.Timestamp("2021-01-04 18:00", tz="UTC")) == "new_york"
    assert session_bucket_utc(pd.Timestamp("2021-01-04 23:00", tz="UTC")) == "late"
    assert weekday_utc(pd.Timestamp("2021-01-04", tz="UTC")) == "Mon"


@pytest.mark.parametrize("mode", MATCHED_NULL_MODES)
def test_every_mode_runs_and_is_deterministic(mode: str) -> None:
    frames = _frames()
    ledger = _ledger(frames)
    a = matched_null_baseline(ledger, frames, mode=mode, window_bars=6, seeds=range(8), min_bucket=1)
    b = matched_null_baseline(ledger, frames, mode=mode, window_bars=6, seeds=range(8), min_bucket=1)
    assert list(a.per_seed_means) == list(b.per_seed_means)
    assert a.null_mean == b.null_mean
    assert a.n_trades > 0
    assert 0.0 <= a.prob_null_ge_strategy <= 1.0
    assert 0.0 <= a.strategy_percentile <= 100.0
    assert a.matched_keys  # non-empty


def test_trade_count_preserved_for_pair_matched() -> None:
    frames = _frames()
    ledger = _ledger(frames, n_per_pair=30)
    res = matched_null_baseline(
        ledger, frames, mode="pair_matched_random", window_bars=6, seeds=range(5), min_bucket=1
    )
    # All 60 trades have forward room, so all are used.
    assert res.n_trades == 60


def test_side_shuffled_keeps_entries_changes_signs() -> None:
    frames = _frames()
    ledger = _ledger(frames)
    res = matched_null_baseline(
        ledger, frames, mode="side_shuffled", window_bars=6, seeds=range(12), min_bucket=1
    )
    # No sparse buckets: side_shuffled never restricts a draw pool.
    assert res.sparse_buckets == []
    assert res.matched_keys == ("entry_bars_fixed", "side_counts")
    # The null is a distribution over sign permutations — std should be > 0.
    assert res.null_std > 0.0


def test_holding_period_mode_uses_hold_distribution() -> None:
    frames = _frames()
    ledger = _ledger(frames)
    res = matched_null_baseline(
        ledger, frames, mode="holding_period_matched_random", window_bars=6,
        seeds=range(6), min_bucket=1,
    )
    # Per-trade windows are sampled from the hold distribution → window_bars is
    # reported as None (variable), and a note is attached.
    assert res.window_bars is None
    assert any("hold-bar distribution" in n for n in res.notes)


def test_cost_overlay_shifts_null_down() -> None:
    frames = _frames()
    ledger = _ledger(frames)
    pre = matched_null_baseline(
        ledger, frames, mode="pair_matched_random", window_bars=6, seeds=range(10), min_bucket=1
    )
    post = matched_null_baseline(
        ledger, frames, mode="pair_matched_random", window_bars=6, seeds=range(10),
        min_bucket=1, apply_cost_overlay_fn=apply_cost_overlay,
    )
    assert post.metric.endswith("post_cost")
    assert post.null_mean <= pre.null_mean


def test_sparse_bucket_flagged_when_frame_too_short() -> None:
    frames = {"EUR_USD": _frame(1, n=20)}
    # Window larger than the frame can support for many entries.
    ledger = pd.DataFrame(
        {
            "instrument": ["EUR_USD"] * 5,
            "side": ["long"] * 5,
            "entry_time": [frames["EUR_USD"].index[i] for i in range(5)],
            "bars_held": [6] * 5,
        }
    )
    res = matched_null_baseline(
        ledger, frames, mode="pair_matched_random", window_bars=18, seeds=range(4), min_bucket=10
    )
    assert res.sparse_buckets  # flagged
    flags = interpret_matched_null(res)["flags"]
    assert "MATCHED_NULL_SPARSE" in flags


def test_interpret_flags_present() -> None:
    frames = _frames()
    ledger = _ledger(frames)
    res = matched_null_baseline(
        ledger, frames, mode="full_matched_null", window_bars=6, seeds=range(8), min_bucket=1
    )
    out = interpret_matched_null(res)
    assert out["mode"] == "full_matched_null"
    assert isinstance(out["flags"], list) and out["flags"]
    # Exactly one of the position bands is present.
    bands = {"BEATS_MATCHED_NULL", "ABOVE_MATCHED_NULL", "WITHIN_MATCHED_NULL", "BELOW_MATCHED_NULL"}
    assert len(bands.intersection(out["flags"])) == 1


def test_invalid_inputs_raise() -> None:
    frames = _frames()
    ledger = _ledger(frames)
    with pytest.raises(ValueError, match="unknown mode"):
        matched_null_baseline(ledger, frames, mode="nope", window_bars=6)
    with pytest.raises(ValueError, match="window_bars must be"):
        matched_null_baseline(ledger, frames, mode="side_shuffled", window_bars=0)
    with pytest.raises(ValueError, match="empty"):
        matched_null_baseline(pd.DataFrame(), frames, mode="side_shuffled", window_bars=6)
    with pytest.raises(ValueError, match="seeds must be non-empty"):
        matched_null_baseline(ledger, frames, mode="side_shuffled", window_bars=6, seeds=[])


def test_missing_required_column_raises() -> None:
    frames = _frames()
    bad = pd.DataFrame({"instrument": ["EUR_USD"], "entry_time": [frames["EUR_USD"].index[10]]})
    with pytest.raises(ValueError, match="missing required column"):
        matched_null_baseline(bad, frames, mode="pair_matched_random", window_bars=6)


def test_to_dict_is_json_friendly() -> None:
    frames = _frames()
    ledger = _ledger(frames)
    res = matched_null_baseline(
        ledger, frames, mode="timestamp_random_same_pair", window_bars=6, seeds=range(5), min_bucket=1
    )
    d = res.to_dict()
    assert set(d) >= {"mode", "metric", "n_trades", "null_distribution", "prob_null_ge_strategy"}
    assert d["null_distribution"]["n_seeds"] == 5
