"""Cost-overlay tests.

Pin the pip-value rule, the round-trip cost arithmetic, the financing
stress arithmetic (against the CONSERVATIVE_BP_PER_DAY table), and
the turnover-cost-burden composition.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from research.edge_discovery.costs import (
    apply_cost_overlay,
    cost_fraction,
    financing_stress_fraction,
    pip_value_for,
    turnover_cost_burden,
)
from research.edge_discovery.loaders import load_candles_csv
from research.edge_discovery.windows import Side, compute_forward_returns

from forex_bot.financing import CONSERVATIVE_BP_PER_DAY

REPO_ROOT = Path(__file__).resolve().parents[3]
H4_FIXTURE = REPO_ROOT / "research" / "edge_discovery" / "sample_fixtures" / "synthetic_EUR_USD_H4.csv"


def test_pip_value_jpy_vs_others() -> None:
    assert pip_value_for("USD_JPY") == 0.01
    assert pip_value_for("EUR_USD") == 0.0001
    assert pip_value_for("GBP_USD") == 0.0001


def test_cost_fraction_matches_formula() -> None:
    # round trip: spread + 2 * slip pips
    f = cost_fraction("EUR_USD", entry_price=1.1, spread_pips=1.5, slip_pips=0.2)
    expected = (1.5 + 2 * 0.2) * 0.0001 / 1.1
    assert abs(f - expected) < 1e-15


def test_cost_fraction_rejects_zero_price() -> None:
    with pytest.raises(ValueError):
        cost_fraction("EUR_USD", entry_price=0.0, spread_pips=1.0, slip_pips=0.1)


def test_financing_stress_uses_conservative_table() -> None:
    bp = CONSERVATIVE_BP_PER_DAY["EUR_USD"]
    # 24 hours = 1 day
    f = financing_stress_fraction("EUR_USD", bars_held=6, hours_per_bar=4.0)
    expected = (bp / 10000.0) * 1.0
    assert abs(f - expected) < 1e-15


def test_financing_stress_defaults_to_max_for_unknown_pair() -> None:
    f_known = financing_stress_fraction("USD_JPY", bars_held=6)
    f_unknown = financing_stress_fraction("XAU_USD", bars_held=6)
    assert f_unknown >= f_known  # conservative default >= every known value


def test_apply_cost_overlay_subtracts_costs_and_financing() -> None:
    sample = load_candles_csv(H4_FIXTURE)
    sigs = [sample.frame.index[i] for i in (5, 25, 55)]
    fr = compute_forward_returns(sample.frame, sigs, window_bars=4, side=Side.LONG)
    out = apply_cost_overlay(fr.per_signal, "EUR_USD", spread_pips=1.5, slip_pips=0.2)
    assert "log_return_post_cost" in out.columns
    for _, row in out.iterrows():
        expected = row["log_return"] - row["cost_fraction"] - row["financing_fraction"]
        assert abs(row["log_return_post_cost"] - expected) < 1e-12


def test_apply_cost_overlay_without_financing() -> None:
    sample = load_candles_csv(H4_FIXTURE)
    sigs = [sample.frame.index[10]]
    fr = compute_forward_returns(sample.frame, sigs, window_bars=4)
    out = apply_cost_overlay(fr.per_signal, "EUR_USD", apply_financing=False)
    expected = out["log_return"].iloc[0] - out["cost_fraction"].iloc[0]
    assert abs(out["log_return_post_cost"].iloc[0] - expected) < 1e-12


def test_apply_cost_overlay_empty_frame_returns_empty_with_cols() -> None:
    empty = pd.DataFrame(columns=["entry_price", "log_return", "bars_held"])
    out = apply_cost_overlay(empty, "EUR_USD")
    assert "log_return_post_cost" in out.columns
    assert out.empty


def test_apply_cost_overlay_requires_log_return_column() -> None:
    df = pd.DataFrame({"entry_price": [1.1], "bars_held": [4]})
    with pytest.raises(ValueError, match="must come from compute_forward_returns"):
        apply_cost_overlay(df, "EUR_USD")


def test_turnover_cost_burden_share_is_correct() -> None:
    r = turnover_cost_burden(pre_cost_mean=0.0010, n_trades=100, cost_per_trade_fraction=0.00015)
    # share = |100 * 0.00015 / (0.0010 * 100)| = 0.15
    assert abs(r["cost_share_of_mean"] - 0.15) < 1e-9
    assert r["cost_total"] == pytest.approx(0.015)


def test_turnover_cost_burden_zero_pre_cost_is_inf() -> None:
    r = turnover_cost_burden(pre_cost_mean=0.0, n_trades=100, cost_per_trade_fraction=0.00015)
    assert r["cost_share_of_mean"] == float("inf")
