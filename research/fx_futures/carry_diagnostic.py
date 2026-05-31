"""FX-futures carry diagnostic — runs the FROZEN carry factor on futures returns.

Reuses ``research.carry.carry_factor`` functions UNMODIFIED (hml weights, forward
return, NW t-stat, cell stats, nulls, Holm). The ONLY change versus the spot
study is the return series: the per-currency USD level matrix comes from CME FX
futures instead of spot mids.

Venue identity (FX_FUTURES_COST_MODEL.md §4): in futures the carry differential
is embedded in the basis and realized via convergence INTO the futures price, so
the **futures total return = futures price return**. There is NO separate accrual
leg added (financing = 0). The spot-style FRED accrual is computed separately and
reported only as the benefit futures gives up — never added to the futures total.

No trades, no entry/exit, no optimization, no threshold changes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.carry import carry_factor as CF

HORIZONS = (1, 3, 6, 12)
PRIMARY_H = 3
K = 3
SCHEME = "hml"


def _futures_portfolio_price_return(weights: pd.DataFrame, ln_levels: pd.DataFrame, h: int) -> pd.Series:
    """Futures total = price-only forward return (NO accrual added)."""
    return CF.forward_spot_return(weights, ln_levels, h)


def run_diagnostic(signal: pd.DataFrame, usd_levels: pd.DataFrame,
                   yield_signal: pd.DataFrame | None, *, seed: int = CF.SEED,
                   n_draws: int = 2000, run_nulls: bool = True) -> dict:
    """Evaluate the frozen carry factor on futures levels.

    ``signal``       : month×currency carry signal (FRED rate, lag-1) — FROZEN.
    ``usd_levels``   : month×currency USD-per-currency futures levels.
    ``yield_signal`` : month×currency annualized carry yield (for the *reference*
                       spot-style accrual only); may be None to skip that report.
    """
    ln_levels = np.log(usd_levels)
    # align signal to the level index
    common = signal.index.intersection(usd_levels.index)
    signal = signal.reindex(common)
    ln_levels = ln_levels.reindex(common)

    weights = CF.build_weights(signal, SCHEME, K)
    rng = np.random.default_rng(seed)

    cells: dict[str, dict] = {}
    for h in HORIZONS:
        price = _futures_portfolio_price_return(weights, ln_levels, h)
        st = CF.cell_stats(price, h)
        cell = {
            "n": st.n, "n_independent": st.n_independent, "mean": st.mean,
            "std": st.std, "ann_ratio": st.ann_ratio,
            "sign_consistency": st.sign_consistency, "nw_t": st.nw_t,
        }
        # reference-only: the spot-style accrual futures does NOT hand out
        if yield_signal is not None:
            acc = CF.carry_accrual(weights, yield_signal.reindex(common), h).reindex(price.index)
            cell["reference_spot_accrual_mean"] = float(acc.mean())
            cell["futures_minus_spotaccrual_note"] = (
                "futures total = price return only; accrual shown is what spot booked, "
                "not added to futures total"
            )
        cells[f"h{h}"] = cell

    out: dict = {
        "seed": seed, "scheme": SCHEME, "k": K, "primary_h": PRIMARY_H,
        "n_months": int(len(common)),
        "window_first": str(common.min().date()) if len(common) else None,
        "window_last": str(common.max().date()) if len(common) else None,
        "currencies": list(signal.columns),
        "rank_stability": CF.rank_stability(signal),
        "cells": cells,
        "venue_identity": "futures_total = futures_price_return; financing=0; no accrual leg",
    }

    if run_nulls:
        out["nulls"] = _run_nulls(signal, ln_levels, h=PRIMARY_H, weights=weights,
                                  n_draws=n_draws, rng=rng)
    return out


def _futures_total_for_weights(weights, ln_levels, h):
    return CF.forward_spot_return(weights, ln_levels, h)


def _run_nulls(signal: pd.DataFrame, ln_levels: pd.DataFrame, *, h: int,
               weights: pd.DataFrame, n_draws: int, rng) -> dict:
    """Null battery, price-only (consistent with the futures total identity).

    Re-implemented here (not calling carry_factor's _portfolio_total, which adds
    accrual) so the nulls match the futures price-only total. carry_factor's
    generic helpers (build_weights, hml, matched_z) are reused unmodified.
    """
    observed = _futures_total_for_weights(weights, ln_levels, h).mean()
    cols = signal.columns.to_list()

    # 1) randomized ranks: permute asset->signal each month
    rr = np.empty(n_draws)
    base = signal.to_numpy()
    for d in range(n_draws):
        vals = base.copy()
        for i in range(vals.shape[0]):
            row = vals[i]
            mask = ~np.isnan(row)
            src = np.where(mask)[0]
            row[src] = row[rng.permutation(src)]
            vals[i] = row
        w = CF.build_weights(pd.DataFrame(vals, index=signal.index, columns=cols), SCHEME, K)
        rr[d] = _futures_total_for_weights(w, ln_levels, h).mean()

    # 2) shuffled-timestamp: permute signal months
    st = np.empty(n_draws)
    for d in range(n_draws):
        perm = rng.permutation(len(signal.index))
        w = CF.build_weights(pd.DataFrame(signal.to_numpy()[perm], index=signal.index, columns=cols), SCHEME, K)
        st[d] = _futures_total_for_weights(w, ln_levels, h).mean()

    # 3) matched-random baskets (shuffled contracts): random long/short k each month
    mr = np.empty(n_draws)
    valid = {m: row.dropna().index.to_list() for m, row in signal.iterrows()}
    for d in range(n_draws):
        rows = {}
        for m, assets in valid.items():
            w = pd.Series(0.0, index=signal.columns)
            if len(assets) >= 2 * K:
                pick = rng.permutation(assets)
                for a in pick[:K]:
                    w[a] = 1.0 / K
                for a in pick[K:2 * K]:
                    w[a] = -1.0 / K
            rows[m] = w
        wmat = pd.DataFrame(rows).T.reindex(columns=signal.columns)
        mr[d] = _futures_total_for_weights(wmat, ln_levels, h).mean()

    # 4) unconditional baseline: equal-weight long all currencies vs USD
    ew = pd.DataFrame(0.0, index=signal.index, columns=signal.columns)
    nonusd = [c for c in signal.columns if c != "USD"]
    for c in nonusd:
        ew[c] = 1.0 / len(nonusd)
    uncond = float(_futures_total_for_weights(ew, ln_levels, h).mean())

    nulls = {
        "observed_mean": float(observed),
        "randomized_ranks": CF.matched_z(observed, rr),
        "shuffled_timestamp": CF.matched_z(observed, st),
        "matched_random": CF.matched_z(observed, mr),
        "unconditional_baseline_mean": uncond,
        "n_draws": n_draws,
    }
    pvals = {
        "randomized_ranks": nulls["randomized_ranks"]["p_one_sided"],
        "shuffled_timestamp": nulls["shuffled_timestamp"]["p_one_sided"],
        "matched_random": nulls["matched_random"]["p_one_sided"],
    }
    nulls["holm_bonferroni"] = CF.holm_bonferroni(pvals)
    return nulls


def drop_one_currency(signal: pd.DataFrame, usd_levels: pd.DataFrame, h: int = PRIMARY_H) -> dict:
    """Leave-one-currency-out means at horizon h (price-only futures total)."""
    ln_levels = np.log(usd_levels)
    common = signal.index.intersection(usd_levels.index)
    signal = signal.reindex(common)
    ln_levels = ln_levels.reindex(common)
    out = {}
    for drop in [c for c in signal.columns if c != "USD"]:
        sub = signal.drop(columns=[drop])
        w = CF.build_weights(sub, SCHEME, K)
        # weights need full column set for the level multiply
        w = w.reindex(columns=signal.columns).fillna(0.0)
        out[f"drop_{drop}"] = float(CF.forward_spot_return(w, ln_levels, h).mean())
    full = CF.build_weights(signal, SCHEME, K)
    out["full"] = float(CF.forward_spot_return(full, ln_levels, h).mean())
    return out
