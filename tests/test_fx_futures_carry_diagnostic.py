"""Unit tests for the FX-futures carry diagnostic infrastructure.

No network. Uses small synthetic fixtures to verify mechanics:
  - month-end resample + direct USD-per-currency mapping (no inversion)
  - HML weights are dollar-neutral
  - frozen carry_factor functions are reused unmodified
  - futures total = price-only (no accrual added)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from research.fx_futures import carry_diagnostic as DIAG  # noqa: N812
from research.fx_futures import continuous
from research.fx_futures.registry import CONTRACTS, FUTURES_CURRENCIES

from research.carry import carry_factor as CF  # noqa: N812


def _synthetic_raw():
    dates = pd.date_range("2020-01-01", "2021-12-31", freq="D")
    raw = {}
    for i, ccy in enumerate(FUTURES_CURRENCIES):
        # smooth drift per currency, daily
        vals = 1.0 + 0.0001 * (i + 1) * np.arange(len(dates))
        raw[ccy] = [(d.date().isoformat(), float(v)) for d, v in zip(dates, vals, strict=False)]
    return raw


def test_registry_quote_convention():
    # JPY/CHF/CAD are spot-inverted; others not.
    assert CONTRACTS["JPY"].spot_inverted is True
    assert CONTRACTS["CHF"].spot_inverted is True
    assert CONTRACTS["CAD"].spot_inverted is True
    assert CONTRACTS["EUR"].spot_inverted is False
    assert len(FUTURES_CURRENCIES) == 7


def test_month_end_levels_shape_and_usd():
    lvl = continuous.month_end_levels(_synthetic_raw())
    assert "USD" in lvl.columns
    assert (lvl["USD"] == 1.0).all()
    # 24 months, no missing
    cov = continuous.coverage_report(lvl)
    assert cov["missing_months"] == 0
    assert cov["n_months"] == 24


def test_direct_mapping_no_inversion():
    # the month-end level for a currency equals its raw month-end close directly
    raw = _synthetic_raw()
    lvl = continuous.month_end_levels(raw)
    # last EUR close of Jan 2020
    jan = [c for d, c in raw["EUR"] if d.startswith("2020-01")][-1]
    assert abs(lvl.loc["2020-01-01", "EUR"] - jan) < 1e-9


def test_hml_weights_dollar_neutral():
    sig = pd.Series({"EUR": 5.0, "GBP": 4.0, "JPY": 0.1, "AUD": 3.0,
                     "NZD": 3.5, "CHF": 0.2, "CAD": 2.0})
    w = CF.hml_weights(sig, k=3)
    assert abs(w.sum()) < 1e-12          # dollar neutral
    assert abs(w.abs().sum() - 2.0) < 1e-12  # gross exposure 2


def test_diagnostic_runs_and_is_price_only():
    raw = _synthetic_raw()
    lvl = continuous.month_end_levels(raw)
    # constant-rank signal: EUR..CAD descending
    months = lvl.index
    sig = pd.DataFrame({c: 7 - i for i, c in enumerate(FUTURES_CURRENCIES)},
                       index=months)
    res = DIAG.run_diagnostic(sig, lvl, yield_signal=None, run_nulls=False)
    assert res["venue_identity"].startswith("futures_total")
    assert "h3" in res["cells"]
    # price-only: with no accrual leg the mean equals forward_spot_return mean
    w = CF.build_weights(sig, "hml", 3)
    direct = CF.forward_spot_return(w, np.log(lvl), 3).mean()
    assert abs(res["cells"]["h3"]["mean"] - direct) < 1e-12


def test_drop_one_currency_keys():
    raw = _synthetic_raw()
    lvl = continuous.month_end_levels(raw)
    sig = pd.DataFrame({c: 7 - i for i, c in enumerate(FUTURES_CURRENCIES)},
                       index=lvl.index)
    d = DIAG.drop_one_currency(sig, lvl, h=3)
    assert "full" in d
    assert "drop_JPY" in d
