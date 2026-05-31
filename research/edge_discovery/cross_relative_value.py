"""Cross relative-value factor — research-only construction & study.

Implements the FROZEN protocol in
``docs/research/CROSS_RELATIVE_VALUE_PROTOCOL.md`` (Phase 1). Constructs
triangular no-arbitrage consistency residuals (synthetic-vs-observed) for the 8
crosses and measures whether their **deviations revert**. Builds NO trades, NO
signals, NO entry/exit, NO PnL, NO approval. Import-isolated research code.

A triangular residual is
    resid_c(t) = ln(observed cross)(t) - implied(t),
where implied is the no-arbitrage value from the two USD legs. It should be small
and stationary; the factor question is whether *deviations* (rolling-z stretched)
revert toward zero over 5-240 min, beyond a matched null and beyond a trivial
non-synchronous-quote / no-arb-band artifact.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.edge_discovery.relative_value_spread import ar1_half_life, rolling_z

# --------------------------------------------------------------------------- #
# Frozen universe + triangle definitions (protocol §1, §2)
# --------------------------------------------------------------------------- #
MAJORS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF"]
CROSSES = ["EUR_GBP", "EUR_JPY", "GBP_JPY", "AUD_JPY", "NZD_JPY", "EUR_CHF", "GBP_CHF", "EUR_AUD"]
INSTRUMENTS = MAJORS + CROSSES

# implied( cross ) = sum( coeff * ln(major) ); residual = ln(cross) - implied
TRIANGLES: dict[str, dict[str, int]] = {
    "EUR_GBP": {"EUR_USD": +1, "GBP_USD": -1},
    "EUR_JPY": {"EUR_USD": +1, "USD_JPY": +1},
    "GBP_JPY": {"GBP_USD": +1, "USD_JPY": +1},
    "AUD_JPY": {"AUD_USD": +1, "USD_JPY": +1},
    "NZD_JPY": {"NZD_USD": +1, "USD_JPY": +1},
    "EUR_CHF": {"EUR_USD": +1, "USD_CHF": +1},
    "GBP_CHF": {"GBP_USD": +1, "USD_CHF": +1},
    "EUR_AUD": {"EUR_USD": +1, "AUD_USD": -1},
}

# Frozen analysis constants (protocol §3-§5, §8)
PRIMARY_L = 48          # 4h rolling-z look-back in M5 bars
SAMPLE_EVERY = 12       # hourly event decimation
HORIZONS_BARS = {5: 1, 15: 3, 30: 6, 60: 12, 240: 48}
Z_STRETCH = 2.0
Z_EXTREME = 3.0
Z_COMPRESS = 0.5


def build_logprice_panel(price_by_instrument: dict[str, pd.Series]) -> pd.DataFrame:
    df = pd.DataFrame(price_by_instrument).sort_index()
    df = df[INSTRUMENTS].dropna(how="any")
    return np.log(df)


def build_residuals(logpx: pd.DataFrame, triangles=TRIANGLES) -> pd.DataFrame:
    """8 triangular residuals: resid_c = ln(cross) - sum(coeff*ln(major))."""
    cols = {}
    for cross, legs in triangles.items():
        implied = sum(coeff * logpx[m] for m, coeff in legs.items())
        cols[cross] = logpx[cross] - implied
    return pd.DataFrame(cols, index=logpx.index)[list(triangles.keys())]


def zscore_residuals(resid: pd.DataFrame, lookback: int = PRIMARY_L) -> pd.DataFrame:
    return pd.DataFrame(
        {c: rolling_z(resid[c], lookback) for c in resid.columns}, index=resid.index
    )


def event_positions(n: int, every: int = SAMPLE_EVERY, warmup: int = PRIMARY_L) -> np.ndarray:
    return np.arange(warmup + 1, n, every)


# --------------------------------------------------------------------------- #
# Deviation-response study (protocol §5-§7) — research-only measurement
# --------------------------------------------------------------------------- #
BUCKETS = {
    "stretched": (Z_STRETCH, np.inf),
    "extreme": (Z_EXTREME, np.inf),
    "compressed": (0.0, Z_COMPRESS),
}


def response_for_relationship(
    resid: pd.Series, z: pd.Series, ev: np.ndarray, horizons=HORIZONS_BARS
) -> pd.DataFrame:
    """Signed reversion / fraction-closed / P(reverts) per bucket x horizon (bp)."""
    r = resid.to_numpy()
    zz = z.to_numpy()
    n = len(r)
    rows = []
    for bucket, (lo, hi) in BUCKETS.items():
        absz = np.abs(zz[ev])
        in_b = (absz >= lo) & (absz < hi) & ~np.isnan(zz[ev])
        ev_b = ev[in_b]
        for mins, hb in horizons.items():
            fut = ev_b + hb
            ok = fut < n
            e = ev_b[ok]
            f = fut[ok]
            sgn = np.sign(zz[e])
            d_resid = r[f] - r[e]
            rev = -sgn * d_resid  # + = reverts toward zero
            with np.errstate(divide="ignore", invalid="ignore"):
                frac = -np.sign(r[e]) * d_resid / np.abs(r[e])
            valid = ~np.isnan(rev)
            rows.append({
                "bucket": bucket, "horizon_min": mins, "n": int(valid.sum()),
                "mean_rev_bp": float(np.nanmean(rev[valid]) / 1e-4) if valid.any() else np.nan,
                "p_revert": float((rev[valid] > 0).mean()) if valid.any() else np.nan,
                "mean_frac_closed": float(np.nanmean(frac[valid])) if valid.any() else np.nan,
            })
    return pd.DataFrame(rows)


def relationship_diagnostics(resid: pd.Series) -> dict:
    s = resid.dropna().to_numpy()
    hl = ar1_half_life(s)
    autocorr1 = float(pd.Series(s).autocorr(lag=1)) if len(s) > 2 else np.nan
    return {
        "resid_std_bp": float(np.nanstd(s) / 1e-4),
        "ar1_phi": hl["ar1_phi"],
        "half_life_bars": hl["half_life_bars"],
        "autocorr_lag1": autocorr1,
    }


def _session_codes(index: pd.DatetimeIndex) -> np.ndarray:
    h = index.hour.to_numpy()
    code = np.full(len(h), 4)
    code = np.where((h >= 0) & (h < 7), 0, code)
    code = np.where((h >= 7) & (h < 12), 1, code)
    code = np.where((h >= 12) & (h < 16), 2, code)
    code = np.where((h >= 16) & (h < 21), 3, code)
    return code


# --------------------------------------------------------------------------- #
# Null comparison (protocol §9) — research-only
# --------------------------------------------------------------------------- #
def _derangement(rng, k):
    """A permutation of range(k) with no fixed point (wrong-relationship map)."""
    while True:
        p = rng.permutation(k)
        if not np.any(p == np.arange(k)):
            return p


def rolling_robust_z(s: pd.Series, lookback: int) -> pd.Series:
    """Median/MAD rolling z (robust normalization variant), look-ahead-safe."""
    med = s.rolling(lookback).median().shift(1)
    mad = (s - med).abs().rolling(lookback).median().shift(1)
    return (s - med) / (1.4826 * mad)


def null_comparison(
    logpx: pd.DataFrame, ev: np.ndarray, lookback: int = PRIMARY_L,
    horizons=HORIZONS_BARS, seeds: int = 200, triangles=TRIANGLES,
    z_stretch: float = Z_STRETCH, robust: bool = False,
) -> pd.DataFrame:
    """Pooled stretched-bucket reversion vs four nulls -> matched_z per horizon.

    Pre-builds residuals/z for all (cross, template) combinations so the
    randomized-relationship null (off-diagonal templates) is cheap.
    """
    crosses = list(triangles.keys())
    templates = list(triangles.values())
    k = len(crosses)
    n = len(logpx)
    # resid[i][j] = ln(cross_i) - implied(template_j); z likewise. Diagonal = true.
    resid = np.full((k, k, n), np.nan)
    zarr = np.full((k, k, n), np.nan)
    lp = logpx
    for i, cross in enumerate(crosses):
        lc = lp[cross]
        for j, tmpl in enumerate(templates):
            implied = sum(coeff * lp[m] for m, coeff in tmpl.items())
            rs = (lc - implied)
            resid[i, j] = rs.to_numpy()
            zfun = rolling_robust_z if robust else rolling_z
            zarr[i, j] = zfun(rs, lookback).to_numpy()
    sess = _session_codes(logpx.index)[ev]
    rng_pools = {c: np.where(sess == c)[0] for c in range(5)}

    rows = []
    for mins, hb in horizons.items():
        fut = ev + hb
        ok = fut < n
        evh, futh = ev[ok], fut[ok]
        sess_h = sess[ok]

        def rev_for(i, j, positions, futs):
            z = zarr[i, j, positions]
            d = resid[i, j, futs] - resid[i, j, positions]
            return -np.sign(z) * d

        # observed: true diagonal, stretched events
        obs_vals = []
        for i in range(k):
            z = zarr[i, i, evh]
            mask = np.abs(z) >= z_stretch
            obs_vals.append(rev_for(i, i, evh[mask], futh[mask]))
        obs = float(np.nanmean(np.concatenate(obs_vals)) / 1e-4)

        for null_type in ("randomized_relationships", "shuffled_timestamps", "matched", "unconditional"):
            means = np.empty(seeds)
            for s in range(seeds):
                rng = np.random.default_rng(s + 1000 * mins)
                vals = []
                if null_type == "randomized_relationships":
                    perm = _derangement(rng, k)
                    for i in range(k):
                        j = perm[i]
                        z = zarr[i, j, evh]
                        mask = np.abs(z) >= z_stretch
                        vals.append(rev_for(i, j, evh[mask], futh[mask]))
                elif null_type == "shuffled_timestamps":
                    for i in range(k):
                        z = zarr[i, i, evh]
                        mask = np.abs(z) >= z_stretch
                        pe = evh[mask]
                        # forward change drawn from a random event's forward window
                        rsrc = rng.integers(0, len(evh), size=len(pe))
                        d = resid[i, i, futh[rsrc]] - resid[i, i, evh[rsrc]]
                        vals.append(-np.sign(z[mask]) * d)
                elif null_type == "matched":
                    for i in range(k):
                        z = zarr[i, i, evh]
                        mask = np.abs(z) >= z_stretch
                        m_sess = sess_h[mask]
                        pick = np.empty(mask.sum(), dtype=int)
                        for si, code in enumerate(m_sess):
                            pool = rng_pools[code]
                            pick[si] = pool[rng.integers(0, len(pool))]
                        pf = pick + hb
                        valp = pf < n
                        zz = zarr[i, i, pick[valp]]
                        d = resid[i, i, pf[valp]] - resid[i, i, pick[valp]]
                        vals.append(-np.sign(zz) * d)
                else:  # unconditional: all events (any |z|), true relationship
                    for i in range(k):
                        rsrc = rng.integers(0, len(evh), size=len(evh))
                        z = zarr[i, i, evh[rsrc]]
                        d = resid[i, i, futh[rsrc]] - resid[i, i, evh[rsrc]]
                        vals.append(-np.sign(z) * d)
                allv = np.concatenate(vals)
                means[s] = np.nanmean(allv) / 1e-4
            mu, sd = float(np.nanmean(means)), float(np.nanstd(means))
            rows.append({
                "horizon_min": mins, "null": null_type, "obs_bp": obs,
                "null_mean_bp": mu, "null_std_bp": sd,
                "z": (obs - mu) / sd if sd > 0 else float("nan"),
            })
    return pd.DataFrame(rows)
