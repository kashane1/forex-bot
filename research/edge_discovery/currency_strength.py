"""Cross-implied currency-strength factor — research-only construction & study.

Implements the FROZEN protocol in
``docs/research/CURRENCY_STRENGTH_FACTOR_PROTOCOL.md`` (Phase 1). This module
**constructs a factor and measures its forward response** — it builds NO trades,
NO signals, NO entry/exit logic, NO PnL, NO approval. It is import-isolated
research code under ``research/edge_discovery/``.

Core idea (average-of-pairs decomposition):
  Build a synthetic per-currency cumulative log-index ``CC_c(t)`` =
  mean over instruments containing ``c`` of ``sign_ci * logprice_i(t)`` where
  ``sign_ci = +1`` if ``c`` is the base leg, ``-1`` if the quote leg. Then
    strength_c(t)  = CC_c(t) - CC_c(t-L)          (L-bar look-back move)
    fwd_c(t,h)     = CC_c(t+h) - CC_c(t)          (forward h-bar move)
  Both are the protocol's signed average-of-pairs aggregations, since the
  instrument set and signs are fixed per currency.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Frozen universe (protocol §1)
# --------------------------------------------------------------------------- #
MAJORS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF"]
CROSSES = ["EUR_GBP", "EUR_JPY", "GBP_JPY", "AUD_JPY", "NZD_JPY", "EUR_CHF", "GBP_CHF", "EUR_AUD"]
INSTRUMENTS = MAJORS + CROSSES
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CHF", "CAD"]

# Frozen analysis constants (protocol §5,§6,§7)
PRIMARY_L = 48          # 4h look-back in M5 bars
DELTA_D = 12            # 1h change-in-strength window
SAMPLE_EVERY = 12       # hourly event decimation
HORIZONS_BARS = {5: 1, 15: 3, 30: 6, 60: 12, 240: 48}  # minutes -> M5 bars


def legs(pair: str) -> tuple[str, str]:
    b, q = pair.split("_")
    return b, q


def currency_sign_map() -> dict[str, dict[str, int]]:
    """For each currency, {instrument: +1 (base) or -1 (quote)}."""
    out: dict[str, dict[str, int]] = {c: {} for c in CURRENCIES}
    for inst in INSTRUMENTS:
        b, q = legs(inst)
        out[b][inst] = +1
        out[q][inst] = -1
    return out


# --------------------------------------------------------------------------- #
# Panel construction
# --------------------------------------------------------------------------- #
def build_logprice_panel(price_by_instrument: dict[str, pd.Series]) -> pd.DataFrame:
    """Inner-join M5 mid closes across all 15 instruments -> log-price panel.

    ``price_by_instrument[inst]`` is a float Series of mid closes indexed by UTC
    timestamp. Only timestamps present for ALL instruments are kept (protocol §2).
    """
    df = pd.DataFrame(price_by_instrument).sort_index()
    df = df[INSTRUMENTS].dropna(how="any")
    return np.log(df)


def build_currency_index(logpx: pd.DataFrame) -> pd.DataFrame:
    """Synthetic per-currency cumulative log-index CC_c(t) (average-of-pairs)."""
    sign_map = currency_sign_map()
    cols = {}
    for c in CURRENCIES:
        insts = list(sign_map[c].keys())
        signed = pd.DataFrame(
            {i: sign_map[c][i] * logpx[i] for i in insts}, index=logpx.index
        )
        cols[c] = signed.mean(axis=1)
    return pd.DataFrame(cols, index=logpx.index)[CURRENCIES]


def strength(cc: pd.DataFrame, lookback: int = PRIMARY_L) -> pd.DataFrame:
    """Look-back currency strength = CC(t) - CC(t-lookback)."""
    return cc - cc.shift(lookback)


def delta_strength(stren: pd.DataFrame, delta: int = DELTA_D) -> pd.DataFrame:
    return stren - stren.shift(delta)


def forward_return(cc: pd.DataFrame, h_bars: int) -> pd.DataFrame:
    """Forward h-bar currency return = CC(t+h) - CC(t)."""
    return cc.shift(-h_bars) - cc


def forward_mfe_mae(cc: pd.DataFrame, h_bars: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Max favourable / adverse excursion of the forward currency path [1..h]."""
    fav = pd.DataFrame(index=cc.index, columns=cc.columns, dtype=float)
    adv = pd.DataFrame(index=cc.index, columns=cc.columns, dtype=float)
    base = cc.to_numpy()
    n = len(cc)
    # path step k value = CC(t+k) - CC(t); running max/min over k=1..h
    run_max = np.full(base.shape, -np.inf)
    run_min = np.full(base.shape, np.inf)
    for k in range(1, h_bars + 1):
        shifted = np.full(base.shape, np.nan)
        if n - k > 0:
            shifted[: n - k] = base[k:]
        step = shifted - base
        run_max = np.fmax(run_max, step)
        run_min = np.fmin(run_min, step)
    fav.iloc[:, :] = run_max
    adv.iloc[:, :] = run_min
    return fav, adv


# --------------------------------------------------------------------------- #
# Ranking + event sampling
# --------------------------------------------------------------------------- #
def rank_panel(stren: pd.DataFrame) -> pd.DataFrame:
    """Rank 1 = strongest .. 8 = weakest, per bar (NaN rows -> NaN)."""
    return stren.rank(axis=1, ascending=False, method="first")


def event_index(logpx: pd.DataFrame, every: int = SAMPLE_EVERY, warmup: int = PRIMARY_L) -> np.ndarray:
    """Integer positions of sampled events (hourly decimation, after warm-up)."""
    return np.arange(warmup + DELTA_D, len(logpx), every)


@dataclass
class FactorPanels:
    logpx: pd.DataFrame
    cc: pd.DataFrame
    stren: pd.DataFrame
    dstren: pd.DataFrame
    ranks: pd.DataFrame
    dispersion: pd.Series
    spread: pd.Series


def build_panels(price_by_instrument: dict[str, pd.Series], lookback: int = PRIMARY_L) -> FactorPanels:
    logpx = build_logprice_panel(price_by_instrument)
    cc = build_currency_index(logpx)
    stren = strength(cc, lookback)
    dstren = delta_strength(stren, DELTA_D)
    ranks = rank_panel(stren)
    dispersion = stren.std(axis=1)
    spread = stren.max(axis=1) - stren.min(axis=1)
    return FactorPanels(logpx, cc, stren, dstren, ranks, dispersion, spread)


# --------------------------------------------------------------------------- #
# Response study (protocol §8, §9) — research-only measurement, no signals
# --------------------------------------------------------------------------- #
CONDITIONS = ("strongest", "weakest", "rapid_strengthen", "rapid_weaken")


def selected_currency_col(panels: FactorPanels, ev: np.ndarray) -> dict[str, np.ndarray]:
    """For each condition, the integer column-index of the selected currency per event."""
    ranks = panels.ranks.to_numpy()[ev]
    dstr = panels.dstren.to_numpy()[ev]
    out = {}
    out["strongest"] = np.nanargmin(np.where(np.isnan(ranks), np.inf, ranks), axis=1)
    # weakest = rank 8 (max rank)
    out["weakest"] = np.nanargmax(np.where(np.isnan(ranks), -np.inf, ranks), axis=1)
    out["rapid_strengthen"] = np.nanargmax(np.where(np.isnan(dstr), -np.inf, dstr), axis=1)
    out["rapid_weaken"] = np.nanargmin(np.where(np.isnan(dstr), np.inf, dstr), axis=1)
    return out


def gather_response(panels: FactorPanels, ev: np.ndarray, horizons=HORIZONS_BARS) -> pd.DataFrame:
    """Mean/P(pos)/P(neg)/MFE/MAE/rank-persistence per condition x horizon (bp)."""
    sel = selected_currency_col(panels, ev)
    ranks = panels.ranks.to_numpy()
    rows = []
    for mins, hb in horizons.items():
        fwd = forward_return(panels.cc, hb).to_numpy()
        mfe_df, mae_df = forward_mfe_mae(panels.cc, hb)
        mfe = mfe_df.to_numpy()
        mae = mae_df.to_numpy()
        fut_ranks = ranks  # rank at t+h
        for cond in CONDITIONS:
            col = sel[cond]
            vals = fwd[ev, col]
            fav = mfe[ev, col]
            adv = mae[ev, col]
            ok = ~np.isnan(vals)
            v = vals[ok]
            # rank persistence: selected currency still in same rank bucket at t+h
            evh = ev + hb
            valid_h = evh < len(ranks)
            persist = np.nan
            if cond in ("strongest", "weakest"):
                tgt = 1.0 if cond == "strongest" else float(len(CURRENCIES))
                evv = ev[valid_h]
                colv = col[valid_h]
                rk_future = fut_ranks[evv + hb, colv]
                persist = float(np.nanmean(rk_future == tgt))
            rows.append({
                "condition": cond, "horizon_min": mins, "n": int(ok.sum()),
                "mean_bp": float(np.nanmean(v) / 1e-4),
                "p_pos": float((v > 0).mean()), "p_neg": float((v < 0).mean()),
                "mfe_bp": float(np.nanmean(fav[ok]) / 1e-4),
                "mae_bp": float(np.nanmean(adv[ok]) / 1e-4),
                "rank_persist": persist,
            })
    return pd.DataFrame(rows)


def _session_codes(index: pd.DatetimeIndex) -> np.ndarray:
    h = index.hour.to_numpy()
    code = np.full(len(h), 4)  # late
    code = np.where((h >= 0) & (h < 7), 0, code)
    code = np.where((h >= 7) & (h < 12), 1, code)
    code = np.where((h >= 12) & (h < 16), 2, code)
    code = np.where((h >= 16) & (h < 21), 3, code)
    return code


def null_comparison(panels: FactorPanels, ev: np.ndarray, horizons=HORIZONS_BARS, seeds: int = 200) -> pd.DataFrame:
    """Four nulls vs observed conditional mean -> matched_z per condition x horizon x null."""
    sel = selected_currency_col(panels, ev)
    ncur = len(CURRENCIES)
    n_ev = len(ev)
    # Session-matched resampling pools (protocol §10): for each event, the pool of
    # event positions sharing its UTC session bucket. flat_pool is event positions
    # ordered by session so each session occupies a contiguous [start, start+len).
    sess = _session_codes(panels.cc.index)[ev]
    order = np.argsort(sess, kind="stable")
    flat_pool = order
    starts = np.zeros(5, dtype=int)
    lens = np.zeros(5, dtype=int)
    pos = 0
    for code in range(5):
        m = int((sess == code).sum())
        starts[code] = pos
        lens[code] = m
        pos += m
    ev_start = starts[sess]
    ev_len = np.maximum(lens[sess], 1)
    rows = []
    for mins, hb in horizons.items():
        fwd = forward_return(panels.cc, hb).to_numpy()
        fwd_ev = fwd[ev]  # (n_ev, ncur)
        for cond in CONDITIONS:
            col = sel[cond]
            obs_vals = fwd_ev[np.arange(n_ev), col]
            obs = float(np.nanmean(obs_vals))
            # unconditional baseline (all currency-bars at events)
            uncond = float(np.nanmean(fwd_ev))
            for null_type in ("randomized_ranks", "shuffled_currencies", "matched_timestamps", "unconditional"):
                means = np.empty(seeds)
                for s in range(seeds):
                    rng = np.random.default_rng(s + 1000 * mins + 7 * CONDITIONS.index(cond))
                    if null_type == "randomized_ranks":
                        rc = rng.integers(0, ncur, size=n_ev)
                        means[s] = np.nanmean(fwd_ev[np.arange(n_ev), rc])
                    elif null_type == "shuffled_currencies":
                        perm = rng.permutation(ncur)
                        means[s] = np.nanmean(fwd_ev[np.arange(n_ev), perm[col]])
                    elif null_type == "matched_timestamps":
                        # session-matched random events + random currency
                        rc = rng.integers(0, ncur, size=n_ev)
                        pick = flat_pool[ev_start + (rng.random(n_ev) * ev_len).astype(int)]
                        means[s] = np.nanmean(fwd_ev[pick, rc])
                    else:  # unconditional: bootstrap over all currency-bars
                        ridx = rng.integers(0, n_ev, size=n_ev)
                        rc = rng.integers(0, ncur, size=n_ev)
                        means[s] = np.nanmean(fwd_ev[ridx, rc])
                mu, sd = float(np.nanmean(means)), float(np.nanstd(means))
                z = (obs - mu) / sd if sd > 0 else float("nan")
                rows.append({
                    "condition": cond, "horizon_min": mins, "null": null_type,
                    "obs_bp": obs / 1e-4, "uncond_bp": uncond / 1e-4,
                    "null_mean_bp": mu / 1e-4, "null_std_bp": sd / 1e-4, "z": z,
                })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Robustness variants (protocol §13): nearby ranking + nearby aggregation
# --------------------------------------------------------------------------- #
def build_currency_index_volnorm(logpx: pd.DataFrame, vol_win: int = 288) -> pd.DataFrame:
    """Vol-normalized aggregation: weight each instrument leg by inverse rolling
    vol of its M5 log returns (nearby-aggregation robustness variant)."""
    sign_map = currency_sign_map()
    rets = logpx.diff()
    inv_vol = 1.0 / rets.rolling(vol_win, min_periods=vol_win // 2).std()
    # cumulative vol-weighted signed log-price proxy per instrument
    weighted_cumret = (rets * inv_vol).cumsum()
    cols = {}
    for c in CURRENCIES:
        insts = list(sign_map[c].keys())
        signed = pd.DataFrame(
            {i: sign_map[c][i] * weighted_cumret[i] for i in insts}, index=logpx.index
        )
        cols[c] = signed.mean(axis=1)
    return pd.DataFrame(cols, index=logpx.index)[CURRENCIES]


def gather_response_bucket(panels: FactorPanels, ev: np.ndarray, k: int, horizons=HORIZONS_BARS) -> pd.DataFrame:
    """Top-k / bottom-k bucket response (nearby-ranking robustness variant).

    'strongest' -> mean forward return over the k strongest currencies per event;
    'weakest'   -> mean over the k weakest. (k=1 reproduces the primary.)
    """
    ranks = panels.ranks.to_numpy()
    ncur = len(CURRENCIES)
    rows = []
    for mins, hb in horizons.items():
        fwd = forward_return(panels.cc, hb).to_numpy()
        fwd_ev = fwd[ev]
        rk_ev = ranks[ev]
        for cond, sel_mask in (
            ("strongest", rk_ev <= k),
            ("weakest", rk_ev >= (ncur - k + 1)),
        ):
            vals = np.where(sel_mask, fwd_ev, np.nan)
            m = np.nanmean(vals)
            rows.append({"condition": cond, "horizon_min": mins, "k": k,
                         "mean_bp": float(m / 1e-4)})
    return pd.DataFrame(rows)
