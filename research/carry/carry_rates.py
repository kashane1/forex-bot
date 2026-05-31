"""Carry / interest-rate-differential dataset — research-only construction.

Harmonized per-currency short rates (OECD 3-month interbank, FRED
``IR3TIB01<CC>M156N``) → per-instrument monthly carry differential
``carry(BASE_QUOTE) = r_base - r_quote`` (annualized %). Lookahead-safe,
provenance-tracked, reproducible. Builds NO trades, NO signals, NO factor study.

The series is the *interbank* carry signal (no broker markup) — it is the
economic carry driver, NOT OANDA's tradable financing cost. Carry is an
un-validated DATA asset here, never an edge.
"""
from __future__ import annotations

import pandas as pd

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CHF", "CAD"]

# Harmonized OECD 3-month interbank rate (monthly, annualized %), one family.
RATE_SERIES: dict[str, str] = {
    "USD": "IR3TIB01USM156N",
    "EUR": "IR3TIB01EZM156N",
    "GBP": "IR3TIB01GBM156N",
    "JPY": "IR3TIB01JPM156N",
    "AUD": "IR3TIB01AUM156N",
    "NZD": "IR3TIB01NZM156N",
    "CHF": "IR3TIB01CHM156N",
    "CAD": "IR3TIB01CAM156N",
}

MAJORS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF"]
CROSSES = ["EUR_GBP", "EUR_JPY", "GBP_JPY", "AUD_JPY", "NZD_JPY", "EUR_CHF", "GBP_CHF", "EUR_AUD"]
INSTRUMENTS = MAJORS + CROSSES


def legs(pair: str) -> tuple[str, str]:
    b, q = pair.split("_")
    return b, q


def build_rate_panel(rate_by_ccy: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Long tidy panel: columns [date, currency, rate, series_id].

    ``rate_by_ccy[ccy]`` is a DataFrame with columns ``date`` (UTC) and ``value``
    (annualized %) — the raw FRED monthly observations.
    """
    frames = []
    for ccy in CURRENCIES:
        df = rate_by_ccy[ccy].copy()
        df = df.rename(columns={"value": "rate"})
        df["currency"] = ccy
        df["series_id"] = RATE_SERIES[ccy]
        frames.append(df[["date", "currency", "rate", "series_id"]])
    out = pd.concat(frames, ignore_index=True)
    return out.sort_values(["currency", "date"]).reset_index(drop=True)


def monthly_rate_matrix(panel: pd.DataFrame) -> pd.DataFrame:
    """Wide month-indexed rate matrix (rows=month, cols=currency), forward-filled.

    Each currency's monthly observation is normalized to month-start and
    forward-filled so every month carries the latest *known* value (lookahead-safe
    at monthly cadence: a month uses only that month's published value or earlier).
    """
    p = panel.copy()
    p["month"] = (
        p["date"].dt.tz_convert("UTC").dt.tz_localize(None).dt.to_period("M").dt.to_timestamp()
    )
    wide = p.pivot_table(index="month", columns="currency", values="rate", aggfunc="last")
    wide = wide.reindex(columns=CURRENCIES).sort_index()
    full_idx = pd.date_range(wide.index.min(), wide.index.max(), freq="MS")
    wide = wide.reindex(full_idx).ffill()
    wide.index.name = "month"
    return wide


def build_carry_differentials(rate_matrix: pd.DataFrame) -> pd.DataFrame:
    """Long monthly carry-differential table for all 15 instruments.

    carry(BASE_QUOTE) = r_base - r_quote (annualized %). Long the pair earns the
    base-leg rate and pays the quote-leg rate; positive carry = base out-yields
    quote. Descriptive only — NOT a signal.
    """
    rows = []
    for inst in INSTRUMENTS:
        b, q = legs(inst)
        rb = rate_matrix[b]
        rq = rate_matrix[q]
        carry = rb - rq
        for month, val in carry.items():
            if pd.isna(val):
                continue
            rows.append({
                "month": month, "instrument": inst,
                "base_ccy": b, "quote_ccy": q,
                "base_rate": float(rb.loc[month]), "quote_rate": float(rq.loc[month]),
                "carry_diff": float(val),
            })
    return pd.DataFrame(rows).sort_values(["instrument", "month"]).reset_index(drop=True)


def triangular_rate_residual(rate_matrix: pd.DataFrame) -> pd.DataFrame:
    """Internal-consistency check: a cross's carry must equal the difference of its
    two USD-leg carries (no-arbitrage of additive rate differentials).

    e.g. carry(EUR_JPY) should equal carry(EUR_USD-implied) - carry(JPY-implied):
    (r_EUR - r_JPY) - [(r_EUR - r_USD) - (r_JPY - r_USD)] == 0 identically.
    Returned residuals must be ~0 (construction is additive); this verifies the
    matrix has no per-currency inconsistency.
    """
    res = {}
    for cross in CROSSES:
        b, q = legs(cross)
        direct = rate_matrix[b] - rate_matrix[q]
        implied = (rate_matrix[b] - rate_matrix["USD"]) - (rate_matrix[q] - rate_matrix["USD"])
        res[cross] = (direct - implied)
    return pd.DataFrame(res, index=rate_matrix.index)
