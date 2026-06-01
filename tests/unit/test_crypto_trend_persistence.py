"""Tests for crypto Family C trend persistence diagnostics."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from research.crypto.trend_persistence import (
    autocorr_lag1,
    log_returns,
    round_trip_cost_bps,
    simulate_momentum_pnl,
)


def test_round_trip_cost_bps_btc_h4_all_in():
    assert round_trip_cost_bps("BTC_USD", "H4", variant="all_in") == 130.0


def test_round_trip_cost_bps_eth_m15_spread_only():
    assert round_trip_cost_bps("ETH_USD", "M15", variant="spread_only") == 16.0


def test_autocorr_positive_for_clustered_signs():
    rng = np.random.default_rng(0)
    rets = np.zeros(200)
    sign = 1.0
    for idx in range(len(rets)):
        rets[idx] = sign * abs(rng.normal(0.001, 0.0005))
        if rng.random() < 0.9:
            pass
        else:
            sign *= -1.0
    ac = autocorr_lag1(rets)
    assert ac is not None
    assert ac > 0


def test_gross_momentum_beats_stress_on_monotone_uptrend():
    closes = np.exp(np.linspace(0, 0.2, 200))
    rets = log_returns(closes)
    gross = simulate_momentum_pnl(
        rets, instrument="BTC_USD", timeframe="H4", lookback=4, variant="gross"
    )
    stress = simulate_momentum_pnl(
        rets, instrument="BTC_USD", timeframe="H4", lookback=4, variant="stress_2x"
    )
    assert gross["sharpe"] >= stress["sharpe"]
