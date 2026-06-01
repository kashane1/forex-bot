"""Tests for crypto Family C trend persistence diagnostics (research-only)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from research.crypto.diagnostics.loader import rows_to_ohlcv
from research.crypto.diagnostics.trend_persistence import (
    NULL_SEED,
    autocorr_at_lags,
    classify_synthesis,
    null_distribution,
    round_trip_cost_bps,
)
from research.crypto.registry import CANONICAL_INSTRUMENTS


def test_unsupported_instrument_rejected():
    import pytest

    with pytest.raises(ValueError, match="unsupported"):
        round_trip_cost_bps("SOL_USD", "H4", variant="all_in")


def test_only_canonical_instruments():
    assert CANONICAL_INSTRUMENTS == ("BTC_USD", "ETH_USD")


def test_round_trip_cost_frozen_btc_h4():
    assert round_trip_cost_bps("BTC_USD", "H4", variant="all_in") == 130.0


def test_round_trip_cost_frozen_eth_m15_spread():
    assert round_trip_cost_bps("ETH_USD", "M15", variant="spread_only") == 16.0


def test_null_reproducible_seed():
    rng_returns = np.random.default_rng(0).normal(0, 0.01, 500)
    a = null_distribution(rng_returns, lambda r: autocorr_at_lags(r)["ac1"], n_trials=50, seed=NULL_SEED)
    b = null_distribution(rng_returns, lambda r: autocorr_at_lags(r)["ac1"], n_trials=50, seed=NULL_SEED)
    assert a["shuffle"]["null_mean"] == b["shuffle"]["null_mean"]


def test_rows_to_ohlcv_empty():
    ohlcv = rows_to_ohlcv([])
    assert len(ohlcv["close"]) == 0


def test_classify_cost_defeated():
    payload = {
        "instruments": {
            "ETH_USD": {
                "timeframes": {
                    "M15": {
                        "autocorr": {"ac1": 0.02},
                        "null_ac1": {"shuffle": {"p_value_two_sided": 0.04}},
                        "momentum_proxy": {
                            "gross": {"sharpe": 1.0},
                            "spread_only": {"sharpe": -1.0},
                            "all_in": {"sharpe": -5.0},
                            "stress_2x": {"sharpe": -10.0},
                        },
                        "cost_edges_momentum_mean": {"spread_only_edge_bps": -10},
                    }
                }
            }
        }
    }
    c = classify_synthesis(payload)
    assert c["label"] == "STATISTICAL_ONLY_COST_DEFEATED"


def test_no_strategy_paths_in_repo_crypto_diagnostics():
    diag = ROOT / "research/crypto/diagnostics"
    for path in diag.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        assert "approved_strategies" not in text
        assert "campaign" not in text or "no campaign" in text or "campaign" not in text.split()
