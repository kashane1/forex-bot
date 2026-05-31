"""Raw futures EOD -> monthly month-end USD-per-currency level matrix.

The carry factor consumes a month-indexed (MS) matrix of USD-per-currency
levels. Each CME FX future already quotes USD-per-foreign-currency, so the
month-end close maps DIRECTLY to that currency's USD level — no inversion.
USD's own level is identically 1.0.

Lookahead-safe: a month's level is that month's *last observed* daily close
(month-end), nothing forward.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.fx_futures.registry import FUTURES_CURRENCIES


def month_end_levels(raw: dict[str, list[tuple[str, float]]]) -> pd.DataFrame:
    """currency -> [(date, close)] => month-start-indexed USD-per-currency matrix.

    Columns: USD + the seven futures currencies. USD ≡ 1.0. Index is month-start
    (MS) timestamps to match the carry factor's convention.
    """
    series = {}
    for ccy in FUTURES_CURRENCIES:
        rows = raw[ccy]
        idx = pd.to_datetime([d for d, _ in rows])
        s = pd.Series([c for _, c in rows], index=idx).sort_index()
        # month-end last observation, then stamp to month-start
        me = s.resample("ME").last()
        me.index = me.index.to_period("M").to_timestamp()  # -> MS
        series[ccy] = me
    lvl = pd.DataFrame(series)
    lvl.insert(0, "USD", 1.0)
    lvl.index.name = "month"
    # restrict to the common, fully-populated window across all contracts
    lvl = lvl.dropna(how="any")
    return lvl


def currency_log_returns(usd_levels: pd.DataFrame) -> pd.DataFrame:
    """Monthly log return vs USD per currency (USD column ≡ 0)."""
    r = np.log(usd_levels).diff()
    r["USD"] = 0.0
    return r


def instrument_log_levels_from_currency(usd_levels: pd.DataFrame, instruments: list[str]) -> pd.DataFrame:
    """ln(price) per instrument by no-arbitrage: ln P(B_Q) = lnL_B - lnL_Q."""
    lnl = np.log(usd_levels)
    out = {}
    for inst in instruments:
        b, q = inst.split("_")
        out[inst] = lnl[b] - lnl[q]
    return pd.DataFrame(out, index=usd_levels.index)


def coverage_report(usd_levels: pd.DataFrame) -> dict:
    """Continuity / coverage summary for the validation doc."""
    idx = usd_levels.index
    expected = pd.date_range(idx.min(), idx.max(), freq="MS")
    missing = expected.difference(idx)
    return {
        "n_months": len(idx),
        "first": str(idx.min().date()),
        "last": str(idx.max().date()),
        "expected_months": len(expected),
        "missing_months": len(missing),
        "currencies": list(usd_levels.columns),
    }
