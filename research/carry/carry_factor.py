"""Carry factor — research-only construction & gross factor-validation study.

Implements the FROZEN protocol in ``docs/research/CARRY_FACTOR_PROTOCOL.md``.
Builds carry-sorted *factor exposures* and measures their *gross* forward-return
response, cross-sectional consistency, null separation, and robustness.

Builds **NO** trades, NO entry/exit, NO PnL ledger, NO cost model, NO approval.
Returns are gross spot mid + accrued *interbank* carry (the economic signal),
never net of broker spread / OANDA financing — that is a separate, later gate.

Import-isolated: no ``forex_bot.broker`` / ``loops`` / ``approval`` / ``execution``.
The only first-party import is the unmodified carry-dataset construction code
``research.carry.carry_rates`` (rate panel → monthly matrix), reused as-is.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from research.carry.carry_rates import CURRENCIES, INSTRUMENTS, legs

# Frozen seed (protocol §6/§8/§10).
SEED = 20260531
# Majors that pin each currency's USD value (protocol §1-§2).
MAJORS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF"]


# --------------------------------------------------------------------------- #
# §2  Monthly spot panel  →  per-currency USD-value levels
# --------------------------------------------------------------------------- #
def currency_usd_levels(month_end_mid: pd.DataFrame) -> pd.DataFrame:
    """USD value of one unit of each currency, per month (cols = 8 currencies).

    ``month_end_mid`` is indexed by month-start (MS) with one column per major
    (the month-end H1 mid). For a base-major (EUR_USD) the price already *is* USD
    per base; for a quote-major (USD_JPY) USD-per-quote is ``1/price``. USD ≡ 1.
    """
    lvl = pd.DataFrame(index=month_end_mid.index)
    lvl["USD"] = 1.0
    for pair in MAJORS:
        b, q = legs(pair)
        p = month_end_mid[pair]
        if q == "USD":  # base-major: price = USD per base
            lvl[b] = p
        else:  # quote-major (USD_xxx): USD per quote = 1/price
            lvl[q] = 1.0 / p
    return lvl.reindex(columns=CURRENCIES)


def currency_log_returns(usd_levels: pd.DataFrame) -> pd.DataFrame:
    """Monthly log return vs USD per currency (USD column ≡ 0)."""
    r = np.log(usd_levels).diff()
    r["USD"] = 0.0
    return r


def instrument_log_levels(usd_levels: pd.DataFrame) -> pd.DataFrame:
    """ln(mid price) for all 15 instruments, by no-arbitrage from USD levels.

    price(B_Q) = (USD per B) / (USD per Q) = Q per B  ⇒  ln = lnL_B − lnL_Q.
    """
    lnl = np.log(usd_levels)
    out = {}
    for inst in INSTRUMENTS:
        b, q = legs(inst)
        out[inst] = lnl[b] - lnl[q]
    return pd.DataFrame(out, index=usd_levels.index)


# --------------------------------------------------------------------------- #
# §3  Carry signal  →  per-currency rate & yield, instrument carry
# --------------------------------------------------------------------------- #
def lag_matrix(mat: pd.DataFrame, lag: int) -> pd.DataFrame:
    """Shift a month-indexed signal matrix forward by ``lag`` months."""
    return mat.shift(lag)


def currency_yields(rate_matrix: pd.DataFrame) -> pd.DataFrame:
    """Annualized carry yield (decimal) of holding each ccy funded in USD."""
    y = (rate_matrix.sub(rate_matrix["USD"], axis=0)) / 100.0
    return y.reindex(columns=CURRENCIES)


def instrument_carry(rate_matrix: pd.DataFrame) -> pd.DataFrame:
    """carry(B_Q) = rate_B − rate_Q (annualized %) for the 15 instruments."""
    out = {}
    for inst in INSTRUMENTS:
        b, q = legs(inst)
        out[inst] = rate_matrix[b] - rate_matrix[q]
    return pd.DataFrame(out, index=rate_matrix.index)


# --------------------------------------------------------------------------- #
# §4  Factor construction — exposures only (no forward returns here)
# --------------------------------------------------------------------------- #
def hml_weights(signal_row: pd.Series, k: int) -> pd.Series:
    """Long top-k / short bottom-k equal-weight, dollar-neutral (Σ|w| = 2)."""
    s = signal_row.dropna()
    if len(s) < 2 * k:
        return pd.Series(0.0, index=signal_row.index)
    order = s.sort_values(ascending=False)
    longs = order.index[:k]
    shorts = order.index[-k:]
    w = pd.Series(0.0, index=signal_row.index)
    w[longs] = 1.0 / k
    w[shorts] = -1.0 / k
    return w


def rank_weights(signal_row: pd.Series) -> pd.Series:
    """Rank-centered, dollar-neutral continuous weights (Σ|w| = 2)."""
    s = signal_row.dropna()
    if len(s) < 2:
        return pd.Series(0.0, index=signal_row.index)
    ranks = s.rank()
    centered = ranks - ranks.mean()
    denom = centered.abs().sum()
    w = pd.Series(0.0, index=signal_row.index)
    if denom > 0:
        w[s.index] = 2.0 * centered / denom
    return w


def build_weights(signal: pd.DataFrame, scheme: str, k: int = 3) -> pd.DataFrame:
    """Per-month weight matrix from a month×asset signal matrix."""
    rows = {}
    for month, row in signal.iterrows():
        rows[month] = hml_weights(row, k) if scheme == "hml" else rank_weights(row)
    return pd.DataFrame(rows).T.reindex(columns=signal.columns)


# --------------------------------------------------------------------------- #
# §5  Forward-return response
# --------------------------------------------------------------------------- #
def forward_spot_return(weights: pd.DataFrame, ln_levels: pd.DataFrame, h: int) -> pd.Series:
    """Σ_i w_i(t) · (lnL_i(t+h) − lnL_i(t)), aligned on rebalance months."""
    fwd = ln_levels.shift(-h) - ln_levels
    common = weights.index.intersection(fwd.index)
    w = weights.reindex(common).reindex(columns=ln_levels.columns).fillna(0.0)
    f = fwd.reindex(common)
    out = (w * f).sum(axis=1, min_count=1)
    # drop rebalances whose +h window runs off the end (NaN forward level)
    valid = f.notna().all(axis=1) & (w.abs().sum(axis=1) > 0)
    return out[valid]


def carry_accrual(weights: pd.DataFrame, yield_signal: pd.DataFrame, h: int) -> pd.Series:
    """Σ_i w_i(t) · yield_i(t) · h/12 — interbank carry earned over the hold."""
    common = weights.index.intersection(yield_signal.index)
    w = weights.reindex(common).reindex(columns=yield_signal.columns).fillna(0.0)
    y = yield_signal.reindex(common).reindex(columns=yield_signal.columns)
    return (w * y).sum(axis=1, min_count=1) * (h / 12.0)


@dataclass(frozen=True)
class CellStats:
    n: int
    n_independent: int
    mean: float
    std: float
    ann_ratio: float
    sign_consistency: float
    nw_t: float


def nw_tstat(x: np.ndarray, lag: int) -> float:
    """Newey–West HAC t-stat of the mean (Bartlett kernel, given lag)."""
    x = np.asarray(x, float)
    n = len(x)
    if n < 3:
        return float("nan")
    xc = x - x.mean()
    gamma0 = (xc @ xc) / n
    var = gamma0
    for ell in range(1, min(lag, n - 1) + 1):
        w = 1.0 - ell / (lag + 1)
        cov = (xc[ell:] @ xc[:-ell]) / n
        var += 2 * w * cov
    se = np.sqrt(max(var, 1e-30) / n)
    return float(x.mean() / se)


def cell_stats(returns: pd.Series, h: int) -> CellStats:
    x = returns.dropna().to_numpy()
    n = len(x)
    if n == 0:
        return CellStats(0, 0, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))
    mean, std = float(x.mean()), float(x.std(ddof=1)) if n > 1 else float("nan")
    ann = float(mean * (12.0 / h) / (std * np.sqrt(12.0 / h))) if std and std > 0 else float("nan")
    sign = float((x > 0).mean())
    return CellStats(n, max(1, n // h), mean, std, ann, sign, nw_tstat(x, h))


def rank_stability(signal: pd.DataFrame) -> float:
    """Mean month-over-month Spearman correlation of the asset ranking."""
    cors = []
    prev = None
    for _, row in signal.iterrows():
        r = row.dropna().rank()
        if prev is not None:
            common = r.index.intersection(prev.index)
            if len(common) >= 3:
                cors.append(r[common].corr(prev[common], method="spearman"))
        prev = r
    return float(np.nanmean(cors)) if cors else float("nan")


# --------------------------------------------------------------------------- #
# §8  Nulls  →  matched-Z
# --------------------------------------------------------------------------- #
def _portfolio_total(weights, ln_levels, yield_signal, h):
    spot = forward_spot_return(weights, ln_levels, h)
    acc = carry_accrual(weights, yield_signal, h).reindex(spot.index)
    return (spot + acc)


def null_randomized_ranks(signal, ln_levels, yield_signal, h, scheme, k, n_draws, rng):
    """Permute the asset→signal-value assignment each month, recompute HML mean."""
    means = np.empty(n_draws)
    cols = signal.columns.to_list()
    for d in range(n_draws):
        shuffled = signal.copy()
        vals = signal.to_numpy().copy()
        for i in range(vals.shape[0]):
            row = vals[i]
            mask = ~np.isnan(row)
            perm = rng.permutation(np.where(mask)[0])
            src = np.where(mask)[0]
            row[src] = row[perm]
            vals[i] = row
        shuffled = pd.DataFrame(vals, index=signal.index, columns=cols)
        w = build_weights(shuffled, scheme, k)
        means[d] = _portfolio_total(w, ln_levels, yield_signal, h).mean()
    return means


def null_shuffled_timestamp(signal, ln_levels, yield_signal, h, scheme, k, n_draws, rng):
    """Permute the *months* of the signal (detach signal from forward window)."""
    means = np.empty(n_draws)
    idx = signal.index
    for d in range(n_draws):
        perm = rng.permutation(len(idx))
        shuffled = pd.DataFrame(signal.to_numpy()[perm], index=idx, columns=signal.columns)
        w = build_weights(shuffled, scheme, k)
        means[d] = _portfolio_total(w, ln_levels, yield_signal, h).mean()
    return means


def null_matched_random(signal, ln_levels, yield_signal, h, k, n_draws, rng):
    """Random long/short baskets of size k each month, ignoring carry."""
    means = np.empty(n_draws)
    valid_assets = {m: row.dropna().index.to_list() for m, row in signal.iterrows()}
    for d in range(n_draws):
        rows = {}
        for m, assets in valid_assets.items():
            w = pd.Series(0.0, index=signal.columns)
            if len(assets) >= 2 * k:
                pick = rng.permutation(assets)
                for a in pick[:k]:
                    w[a] = 1.0 / k
                for a in pick[k : 2 * k]:
                    w[a] = -1.0 / k
            rows[m] = w
        wmat = pd.DataFrame(rows).T.reindex(columns=signal.columns)
        means[d] = _portfolio_total(wmat, ln_levels, yield_signal, h).mean()
    return means


def matched_z(observed_mean: float, null_means: np.ndarray) -> dict:
    mu, sd = float(np.nanmean(null_means)), float(np.nanstd(null_means, ddof=1))
    z = (observed_mean - mu) / sd if sd > 0 else float("nan")
    # one-sided empirical p (observed ≥ null)
    p = float((null_means >= observed_mean).mean())
    return {"null_mean": mu, "null_std": sd, "z": float(z), "p_one_sided": p}


def holm_bonferroni(pvals: dict[str, float], alpha: float = 0.05) -> dict[str, dict]:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out = {}
    for rank, (key, p) in enumerate(items):
        thresh = alpha / (m - rank)
        out[key] = {"p": float(p), "holm_threshold": float(thresh), "reject_null": bool(p < thresh)}
    return out
