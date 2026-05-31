"""Tests for the gross carry factor-validation module (research-only).

Covers the construction identities the protocol relies on (no-arbitrage
instrument returns, dollar-neutral HML weights, USD-level inversion), the
statistics (NW t-stat, Holm-Bonferroni), and import-isolation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from research.carry.carry_rates import CURRENCIES, INSTRUMENTS

from research.carry import carry_factor as cf


@pytest.fixture
def toy_mid():
    idx = pd.date_range("2021-05-01", periods=8, freq="MS")
    rng = np.random.default_rng(1)
    cols = {}
    base = {"EUR_USD": 1.10, "GBP_USD": 1.30, "USD_JPY": 110.0, "AUD_USD": 0.75,
            "NZD_USD": 0.70, "USD_CAD": 1.25, "USD_CHF": 0.90}
    for pair, p0 in base.items():
        steps = rng.normal(0, 0.01, len(idx)).cumsum()
        cols[pair] = p0 * np.exp(steps)
    return pd.DataFrame(cols, index=idx)


def test_usd_levels_invert_quote_majors(toy_mid):
    lvl = cf.currency_usd_levels(toy_mid)
    assert list(lvl.columns) == CURRENCIES
    assert (lvl["USD"] == 1.0).all()
    # base-major: USD-per-EUR equals the EUR_USD price
    assert np.allclose(lvl["EUR"], toy_mid["EUR_USD"])
    # quote-major: USD-per-JPY equals 1/USD_JPY
    assert np.allclose(lvl["JPY"], 1.0 / toy_mid["USD_JPY"])


def test_instrument_return_is_sum_of_usd_legs(toy_mid):
    """No-arb identity: ln price(B_Q) = lnL_B - lnL_Q, so the cross's forward
    return equals the difference of its two USD legs' forward returns."""
    lvl = cf.currency_usd_levels(toy_mid)
    lnl_inst = cf.instrument_log_levels(lvl)
    # EUR_JPY forward 1-step return == EUR-leg fwd ret - JPY-leg fwd ret
    fwd_inst = lnl_inst["EUR_JPY"].shift(-1) - lnl_inst["EUR_JPY"]
    lnl_ccy = np.log(lvl)
    fwd_eur = lnl_ccy["EUR"].shift(-1) - lnl_ccy["EUR"]
    fwd_jpy = lnl_ccy["JPY"].shift(-1) - lnl_ccy["JPY"]
    pd.testing.assert_series_equal(fwd_inst, fwd_eur - fwd_jpy, check_names=False)


def test_all_15_instruments_present(toy_mid):
    lvl = cf.currency_usd_levels(toy_mid)
    lnl = cf.instrument_log_levels(lvl)
    assert list(lnl.columns) == INSTRUMENTS
    assert len(lnl.columns) == 15


def test_hml_weights_dollar_neutral_and_unit_gross():
    row = pd.Series(dict(zip(CURRENCIES, [5, 4, 3, 2, 1, 0, -1, -2], strict=True)))
    w = cf.hml_weights(row, k=3)
    assert w.sum() == pytest.approx(0.0)          # dollar-neutral
    assert w.abs().sum() == pytest.approx(2.0)    # gross exposure 2
    longs = set(w[w > 0].index)
    shorts = set(w[w < 0].index)
    assert longs == {"USD", "EUR", "GBP"}         # top-3 by signal
    assert shorts == {"NZD", "CHF", "CAD"}        # bottom-3 by signal


def test_hml_weights_insufficient_assets_returns_zero():
    row = pd.Series({"USD": 1.0, "EUR": np.nan})
    w = cf.hml_weights(row, k=3)
    assert (w == 0).all()


def test_rank_weights_dollar_neutral():
    row = pd.Series(dict(zip(CURRENCIES, range(8), strict=True)))
    w = cf.rank_weights(row)
    assert w.sum() == pytest.approx(0.0)
    assert w.abs().sum() == pytest.approx(2.0)


def test_carry_accrual_cancels_numeraire():
    """For a dollar-neutral book the USD rate term cancels in the accrual."""
    idx = pd.date_range("2021-05-01", periods=3, freq="MS")
    rate = pd.DataFrame({c: [v] * 3 for c, v in
                         zip(CURRENCIES, [3.0, 2.0, 3.0, 0.0, 3.0, 3.0, 0.0, 2.0], strict=True)}, index=idx)
    yld = cf.currency_yields(rate)
    sig = rate.reindex(columns=CURRENCIES)
    w = cf.build_weights(sig, "hml", 3)
    acc = cf.carry_accrual(w, yld, 12)  # 12m => full annual differential
    # long top-3 short bottom-3; accrual = (mean top - mean bottom)/100
    assert acc.iloc[0] > 0


def test_nw_tstat_matches_plain_t_at_zero_lag():
    rng = np.random.default_rng(0)
    x = rng.normal(0.5, 1.0, 200)
    plain = x.mean() / (x.std(ddof=0) / np.sqrt(len(x)))
    assert cf.nw_tstat(x, lag=0) == pytest.approx(plain, rel=1e-6)


def test_matched_z_and_holm():
    null = np.full(1000, 0.0)
    null[:1] = 0.0
    rng = np.random.default_rng(0)
    draws = rng.normal(0.0, 1.0, 5000)
    mz = cf.matched_z(2.0, draws)
    assert mz["z"] == pytest.approx(2.0, abs=0.1)
    holm = cf.holm_bonferroni({"a": 0.001, "b": 0.2, "c": 0.04})
    assert holm["a"]["reject_null"] is True
    assert holm["b"]["reject_null"] is False


def test_forward_spot_return_drops_tail(toy_mid):
    lvl = cf.currency_usd_levels(toy_mid)
    lnl = np.log(lvl)
    sig = pd.DataFrame(np.tile(np.arange(8.0), (len(toy_mid), 1)),
                       index=toy_mid.index, columns=CURRENCIES)
    w = cf.build_weights(sig, "hml", 3)
    r = cf.forward_spot_return(w, lnl, 3)
    # last 3 rebalances have no +3m forward level -> dropped
    assert r.index.max() <= toy_mid.index[-4]


def test_import_isolation():
    """The research module must not *import* broker/loops/approval/execution
    (AST import inspection — docstring mentions of those names are fine)."""
    import ast
    import sys

    src = sys.modules["research.carry.carry_factor"].__file__
    with open(src) as fh:
        tree = ast.parse(fh.read())
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = ("forex_bot.broker", "forex_bot.loops", "forex_bot.approval", "forex_bot.execution")
    assert not [m for m in imported if any(m.startswith(f) for f in forbidden)]
