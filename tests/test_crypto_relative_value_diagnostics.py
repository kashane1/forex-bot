"""Tests for Family B BTC/ETH relative-value diagnostics."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from research.crypto.diagnostics.loader import align_btc_eth_pair, rows_to_ohlcv
from research.crypto.diagnostics.relative_value import (
    NULL_SEED,
    paired_cost_report,
    rolling_beta,
    rolling_zscore,
)
from research.crypto.diagnostics.trend_persistence import null_distribution


def _synthetic_ohlcv(n: int, *, start: float = 100.0) -> dict:
    t0 = datetime(2021, 5, 31, 0, 0, tzinfo=UTC)
    times = np.array([t0.replace(minute=i % 60, hour=i // 60) for i in range(n)], dtype=object)
    close = start * np.exp(np.cumsum(np.random.default_rng(1).normal(0, 0.001, n)))
    return {
        "times": times,
        "open": close,
        "high": close * 1.001,
        "low": close * 0.999,
        "close": close,
    }


def test_align_intersection_no_forward_fill():
    btc = _synthetic_ohlcv(10)
    eth = _synthetic_ohlcv(10)
    eth["times"] = btc["times"][:8]
    aligned = align_btc_eth_pair(btc, eth)
    assert aligned["n_aligned"] == 8
    assert aligned["n_dropped_btc_only"] == 2
    assert len(aligned["btc_close"]) == 8


def test_unsupported_instrument_rejected():
    from research.crypto.registry import validate_instrument

    with pytest.raises(ValueError, match="unsupported"):
        validate_instrument("SOL_USD")


def test_paired_cost_all_in_m15():
    costs = paired_cost_report("M15")["all_in"]
    assert costs["paired_rt_bps"] == pytest.approx(10 + 4 + 120 + 16 + 4 + 120, rel=0.01)


def test_beta_uses_past_only():
    rng = np.random.default_rng(0)
    n = 200
    btc = rng.normal(0, 0.01, n)
    eth = 0.8 * btc + rng.normal(0, 0.005, n)
    beta = rolling_beta(eth, btc, 20)
    assert np.isnan(beta[19])
    assert np.isfinite(beta[50])


def test_null_reproducible():
    r = np.random.default_rng(2).normal(0, 0.01, 1000)
    a = null_distribution(r, lambda x: float(np.mean(x)), seed=NULL_SEED, n_trials=30, timeframe="D1")
    b = null_distribution(r, lambda x: float(np.mean(x)), seed=NULL_SEED, n_trials=30, timeframe="D1")
    assert a["shuffle"]["null_mean"] == b["shuffle"]["null_mean"]


def test_zscore_no_lookahead_on_first_window():
    s = np.arange(100, dtype=float)
    z = rolling_zscore(s, 10)
    assert np.isnan(z[9])
    assert np.isfinite(z[10])
