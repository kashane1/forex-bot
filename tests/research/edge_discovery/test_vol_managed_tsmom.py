"""Unit tests for the CAMPAIGN_031 vol-managed TSMOM front-gate screen.

Synthetic-only. Pins the screen's mechanics (D1AGG aggregation, no-lookahead
sign-blend signal, EWMA vol, portfolio scaling to a vol target, cost/financing
subtraction, determinism) and two boundary behaviours: a constructed persistent
trend yields a positive pre-cost Sharpe, while costs+financing only ever reduce
the net series below the pre-cost series.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.edge_discovery import vol_managed_tsmom as vm


def _h4_trending(n_days: int = 60, drift: float = 0.0005) -> pd.DataFrame:
    """Build 17:00-NY-aligned H4 bars (6 per day) with a steady up-drift."""
    start = pd.Timestamp("2020-01-01 22:00", tz="UTC")  # 17:00 NY
    idx = pd.date_range(start, periods=n_days * 6, freq="4h")
    price = 1.10 * np.exp(np.cumsum(np.full(len(idx), drift / 6.0)))
    return pd.DataFrame({"mid_c": price}, index=idx)


def test_d1agg_drops_partial_days_and_keeps_5th_bar() -> None:
    h4 = _h4_trending(n_days=10)
    d1 = vm.aggregate_h4_to_d1agg(h4)
    # 6 H4 bars per day, full -> 10 daily bars
    assert len(d1) == 10
    assert "mid_close" in d1.columns
    # daily close = mid of the 5th bar of the day (index 4), not the 6th
    first_day_5th = float(h4["mid_c"].iloc[4])
    assert abs(float(d1["mid_close"].iloc[0]) - first_day_5th) < 1e-12


def test_d1agg_partial_final_day_dropped() -> None:
    h4 = _h4_trending(n_days=5)
    h4 = h4.iloc[:-3]  # last day now has only 3 bars (<5) -> dropped
    d1 = vm.aggregate_h4_to_d1agg(h4)
    assert len(d1) == 4


def test_sign_blend_is_lookahead_free_and_bounded() -> None:
    prices = pd.Series(np.linspace(1.0, 2.0, 400))
    sig = vm.sign_blend_signal(prices, lookbacks=(63, 126, 252))
    assert set(np.unique(sig.dropna())) <= {-1.0, 0.0, 1.0}
    # first max_k bars must be flat (no lookback available)
    assert (sig.iloc[:252] == 0.0).all()
    # a monotonic uptrend -> +1 once warmed up
    assert sig.iloc[-1] == 1.0


def test_ewma_vol_positive_and_annualized() -> None:
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0, 0.01, 500))
    v = vm.ewma_vol(r, com=60).dropna()
    assert (v > 0).all()
    # annualized daily 1% vol ~ 0.01*sqrt(252) ~ 0.16
    assert 0.10 < v.iloc[-1] < 0.25


def test_portfolio_scale_hits_target_naive() -> None:
    # two active legs, sigma 0.10 each, raw_w = +/-1/0.10 -> vol_contrib = +/-1
    raw_w = np.array([10.0, -10.0])
    sigma = np.array([0.10, 0.10])
    c = vm._portfolio_scale(raw_w, sigma, None, target_vol=0.10)
    # naive port vol = sqrt(1^2+1^2)=sqrt(2); c = 0.10/sqrt(2)
    assert abs(c - 0.10 / np.sqrt(2)) < 1e-9


def test_costs_only_reduce_net_below_pre_cost() -> None:
    prices = {
        "EUR_USD": pd.Series(1.10 * np.exp(np.cumsum(np.full(500, 0.0004)))),
        "USD_JPY": pd.Series(110.0 * np.exp(np.cumsum(np.full(500, -0.0003)))),
    }
    book = vm.build_book(prices, mm_overlay=False, use_full_sigma=False)
    assert (book.daily_turnover_cost >= -1e-12).all()
    assert (book.daily_financing >= -1e-12).all()
    # net = pre - turnover - financing, pointwise
    recon = book.daily_pre_cost - book.daily_turnover_cost - book.daily_financing
    assert np.allclose(recon.to_numpy(), book.daily_net.to_numpy())


def test_trend_has_positive_pre_cost_sharpe() -> None:
    # a persistent trend should be detectable pre-cost by sign-blend TSMOM
    prices = {
        "EUR_USD": pd.Series(1.10 * np.exp(np.cumsum(np.full(600, 0.0006)))),
        "GBP_USD": pd.Series(1.30 * np.exp(np.cumsum(np.full(600, 0.0006)))),
    }
    book = vm.build_book(prices, mm_overlay=False, use_full_sigma=False)
    assert vm.sharpe(book.daily_pre_cost) > 0.0


def test_build_book_is_deterministic() -> None:
    prices = {
        "EUR_USD": pd.Series(1.10 * np.exp(np.cumsum(np.full(400, 0.0003)))),
        "AUD_USD": pd.Series(0.70 * np.exp(np.cumsum(np.full(400, -0.0002)))),
    }
    a = vm.build_book(prices)
    b = vm.build_book(prices)
    assert np.allclose(a.daily_net.to_numpy(), b.daily_net.to_numpy())


def test_block_bootstrap_ci_brackets_point_estimate() -> None:
    rng = np.random.default_rng(1)
    daily = pd.Series(rng.normal(0.0003, 0.006, 600))
    ci = vm.block_bootstrap_sharpe_ci(daily, n=500)
    assert ci["lo"] <= ci["sharpe"] <= ci["hi"]
