"""C1 factor-validation analysis (research-only).

Given the one state that survived the M1/HTF confluence sampling matrix —
``C1_trend_cont_long`` (full H4+H1+M15 bullish alignment → M1 reverts down over
30–60 min) — this module supports the cross-pair / regime / USD-confound /
robustness / cost analyses needed to decide whether C1 is a genuine factor, a
USD-regime artifact, a sample-selection artifact, or a statistical mirage.

It is a thin layer over :mod:`forex_bot.research.m1_response_matrix`: it reuses
that module's locked, lookahead-safe HTF→M1 alignment, rising-edge + cooldown
event sampling, signed forward response, and null samplers. It adds only:

* a parametrised C1 builder (:class:`C1Spec`) so the factor can be re-derived
  under alternative — *not optimised* — specifications for robustness checks;
* a per-event **panel** carrying regime covariates (year/quarter/session, H4
  volatility, signed extension above EMA50 in ATR) for the regime / cost phases;
* currency-leg helpers for the USD-confound phase.

It contains **no** trade mechanics: no positions, entries/exits, stops, targets,
sizing, PnL, optimisation, approval, or network/OANDA/credential use. Spread is
recorded and reported only.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd

from forex_bot.research import m1_response_matrix as mrm
from forex_bot.strategies import indicators as ind

# --------------------------------------------------------------------------- #
# Currency-leg helpers (USD-confound phase).
# --------------------------------------------------------------------------- #


def currency_legs(pair: str) -> tuple[str, str]:
    """Return ``(base, quote)`` for a ``BASE_QUOTE`` pair name."""
    base, quote = pair.split("_")
    return base, quote


def usd_leg(pair: str) -> str:
    """Where USD sits in the pair: ``"base"``, ``"quote"``, or ``"none"``."""
    base, quote = currency_legs(pair)
    if base == "USD":
        return "base"
    if quote == "USD":
        return "quote"
    return "none"


# --------------------------------------------------------------------------- #
# Parametrised C1 specification (robustness phase).
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class C1Spec:
    """A C1 confluence specification.

    ``BASELINE`` reproduces the locked prior-sprint definition exactly. The
    other fields exist only so Phase 4 can perturb one knob at a time as a
    *robustness* check — never as optimisation.
    """

    name: str = "baseline"
    ema_fast: int = mrm.EMA_FAST
    ema_slow: int = mrm.EMA_SLOW
    slope_lookback: int = mrm.SLOPE_LOOKBACK
    trend_requires_slope: bool = True
    # Confluence timeframes (slowest first) and the rule each leg must satisfy
    # in the trend direction: "trend" (close vs ema_slow AND slope) or
    # "aligned" (close vs ema_slow only).
    legs: tuple[tuple[str, str], ...] = (
        ("H4", "trend"),
        ("H1", "trend"),
        ("M15", "aligned"),
    )

    @property
    def timeframes(self) -> tuple[str, ...]:
        return tuple(tf for tf, _ in self.legs)

    @property
    def vol_tf(self) -> str:
        """Slowest leg timeframe — used for the volatility / extension column."""
        return self.legs[0][0]


BASELINE = C1Spec()


def _safe_nanmean(x: np.ndarray | pd.Series) -> float:
    """``np.nanmean`` that returns NaN (no warning) for empty / all-NaN input."""
    arr = np.asarray(x, dtype=float)
    if arr.size == 0 or np.all(np.isnan(arr)):
        return float("nan")
    return float(np.nanmean(arr))


def _trend_frame(ohlc: pd.DataFrame, spec: C1Spec) -> pd.DataFrame:
    """Per-bar trend primitives + ATR + signed extension under ``spec``.

    Mirrors :func:`m1_response_matrix.htf_features` for the baseline spec but
    parametrised on EMA lengths / slope lookback / slope requirement, and adds
    ``ext_atr`` = ``(close − ema_slow) / atr`` (how far price is stretched beyond
    the slow EMA, in ATR units; positive above).
    """
    close = ohlc["close"]
    high = ohlc["high"]
    low = ohlc["low"]
    ema_fast = ind.ema(close, spec.ema_fast)
    ema_slow = ind.ema(close, spec.ema_slow)
    slope = ema_slow - ema_slow.shift(spec.slope_lookback)
    atr = ind.atr(high, low, close, mrm.ATR_LEN)

    out = pd.DataFrame(index=ohlc.index)
    out["atr"] = atr
    if spec.trend_requires_slope:
        out["trend_up"] = (close > ema_slow) & (slope > 0)
        out["trend_down"] = (close < ema_slow) & (slope < 0)
    else:
        out["trend_up"] = close > ema_slow
        out["trend_down"] = close < ema_slow
    out["aligned_up"] = close > ema_slow
    out["aligned_down"] = close < ema_slow
    with np.errstate(invalid="ignore", divide="ignore"):
        ext = (close - ema_slow) / atr
    out["ext_atr"] = ext
    bool_cols = ["trend_up", "trend_down", "aligned_up", "aligned_down"]
    out[bool_cols] = out[bool_cols].fillna(False).astype(bool)
    # ema_fast retained only to mirror the locked primitive set; unused by C1.
    _ = ema_fast
    return out


def build_combined_frame(
    m1_df: pd.DataFrame,
    raw_htf: dict[str, pd.DataFrame],
    spec: C1Spec = BASELINE,
) -> pd.DataFrame:
    """M1 price/spread + lookahead-safe per-leg trend primitives for ``spec``.

    ``raw_htf`` maps timeframe label (``"M5"/"M15"/"H1"/"H4"``) → OHLC frame.
    Only the timeframes named in ``spec.legs`` (plus the vol/extension leg) are
    aligned. Columns are prefixed by timeframe, e.g. ``H4_trend_up``,
    ``H4_atr``, ``H4_ext_atr``.
    """
    pieces = [m1_df]
    for tf in dict.fromkeys(spec.timeframes):  # preserve order, de-dup
        feats = _trend_frame(raw_htf[tf], spec)
        aligned = mrm.align_asof(
            m1_df.index, feats, tf_minutes=mrm.TF_MINUTES[tf], prefix=tf
        )
        pieces.append(aligned)
    return pd.concat(pieces, axis=1)


def c1_signed(frame: pd.DataFrame, spec: C1Spec = BASELINE) -> dict[str, pd.Series]:
    """Signed C1 long/short context series in {−1,0,+1} for ``spec``.

    A leg's long condition is ``{tf}_trend_up`` or ``{tf}_aligned_up`` per its
    rule; short mirrors with ``_down``. C1_long is the AND of all legs' long
    conditions (direction +1); C1_short the AND of all legs' short (−1).
    """
    long_cond = pd.Series(True, index=frame.index)
    short_cond = pd.Series(True, index=frame.index)
    for tf, rule in spec.legs:
        col = "trend" if rule == "trend" else "aligned"
        long_cond = long_cond & frame[f"{tf}_{col}_up"].astype(bool)
        short_cond = short_cond & frame[f"{tf}_{col}_down"].astype(bool)
    return {
        "C1_trend_cont_long": pd.Series(
            np.where(long_cond.to_numpy(), 1, 0), index=frame.index,
            name="C1_trend_cont_long",
        ),
        "C1_trend_cont_short": pd.Series(
            np.where(short_cond.to_numpy(), -1, 0), index=frame.index,
            name="C1_trend_cont_short",
        ),
    }


# --------------------------------------------------------------------------- #
# Per-event panel (regime / cost / cross-pair phases).
# --------------------------------------------------------------------------- #


def build_c1_panel(
    m1_df: pd.DataFrame,
    frame: pd.DataFrame,
    pair: str,
    spec: C1Spec = BASELINE,
) -> pd.DataFrame:
    """One row per C1_long / C1_short event with forward response + covariates.

    Columns: the recorded event fields (``timestamp, pair, state, direction,
    session, spread, volatility``), forward ``ret_/mfe_/mae_`` at each horizon,
    plus ``base_ccy, quote_ccy, usd_leg, year, quarter`` and ``ext_signed``
    (direction × slow-leg extension above EMA50 in ATR — how stretched the
    alignment is *in its own direction*).
    """
    vol_tf = spec.vol_tf
    vol_col = f"{vol_tf}_atr"
    ext_col = f"{vol_tf}_ext_atr"
    states = c1_signed(frame, spec)

    pieces = []
    for name, signed in states.items():
        ev = mrm.extract_events(signed, frame, pair=pair, state=name, vol_col=vol_col)
        if ev.empty:
            continue
        resp = mrm.forward_response(m1_df, ev, pair=pair)
        # signed extension at the event bar (lookahead-safe: from aligned frame).
        ext_at = frame[ext_col].reindex(pd.DatetimeIndex(resp["timestamp"])).to_numpy()
        resp["ext_signed"] = resp["direction"].to_numpy() * ext_at
        pieces.append(resp)

    if not pieces:
        return pd.DataFrame()
    panel = pd.concat(pieces, ignore_index=True)
    base, quote = currency_legs(pair)
    panel["base_ccy"] = base
    panel["quote_ccy"] = quote
    panel["usd_leg"] = usd_leg(pair)
    ts = pd.DatetimeIndex(panel["timestamp"])
    panel["year"] = ts.year
    # Quarter label built arithmetically to avoid tz-aware to_period() warnings.
    q = (ts.month - 1) // 3 + 1
    panel["quarter"] = [f"{y}Q{qq}" for y, qq in zip(ts.year, q, strict=True)]
    return panel


def _run_null_seeds(m1_df, ev, pair, sign, seeds, horizons_min, rand, matched):
    """Accumulate per-seed null mean returns into ``rand``/``matched`` dicts."""
    n = len(ev)
    for s in range(seeds):
        r_ev = mrm.sample_random_events(
            m1_df, pair=pair, n=n, direction=sign, seed=1000 + s
        )
        r_sum = mrm.summarize(
            mrm.forward_response(m1_df, r_ev, pair=pair), horizons_min=horizons_min
        ).set_index("horizon_min")
        m_ev = mrm.sample_matched_null(m1_df, ev, pair=pair, seed=5000 + s)
        m_sum = mrm.summarize(
            mrm.forward_response(m1_df, m_ev, pair=pair), horizons_min=horizons_min
        ).set_index("horizon_min")
        for h in horizons_min:
            if h in r_sum.index:
                rand[h].append(r_sum.loc[h, "mean_ret"])
            if h in m_sum.index:
                matched[h].append(m_sum.loc[h, "mean_ret"])


def c1_nulls(
    m1_df: pd.DataFrame,
    frame: pd.DataFrame,
    pair: str,
    *,
    seeds: int = 200,
    spec: C1Spec = BASELINE,
    horizons_min: tuple[int, ...] = mrm.HORIZONS_MIN,
) -> pd.DataFrame:
    """Random-timestamp and session-matched null comparison for C1 long/short.

    Same construction as the prior sprint's runner: hold event count (and, for
    the matched null, session mix + direction) fixed; report
    ``rand_z``/``matched_z`` per horizon. Pure descriptive statistics.
    """
    states = c1_signed(frame, spec)
    rows: list[dict] = []
    for name, signed in states.items():
        ev = mrm.extract_events(
            signed, frame, pair=pair, state=name, vol_col=f"{spec.vol_tf}_atr"
        )
        if ev.empty:
            continue
        sign = int(np.sign(signed.loc[signed != 0].iloc[0]))
        obs = mrm.summarize(
            mrm.forward_response(m1_df, ev, pair=pair), horizons_min=horizons_min
        ).set_index("horizon_min")
        n = len(ev)
        rand = {h: [] for h in horizons_min}
        matched = {h: [] for h in horizons_min}
        # Null event sets carry NaN spread/volatility by construction, so the
        # framework's per-group mean of those columns is an expected empty-slice;
        # silence only that warning (the return values are unaffected).
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "Mean of empty slice", RuntimeWarning)
            _run_null_seeds(
                m1_df, ev, pair, sign, seeds, horizons_min, rand, matched
            )
        for h in horizons_min:
            if h not in obs.index:
                continue
            o = float(obs.loc[h, "mean_ret"])
            r_arr = np.asarray(rand[h], dtype=float)
            m_arr = np.asarray(matched[h], dtype=float)
            r_std = float(r_arr.std(ddof=1)) if r_arr.size > 1 else float("nan")
            m_std = float(m_arr.std(ddof=1)) if m_arr.size > 1 else float("nan")
            rows.append(
                {
                    "pair": pair,
                    "state": name,
                    "horizon_min": h,
                    "n": n,
                    "obs_mean_ret": o,
                    "rand_null_mean": float(r_arr.mean()) if r_arr.size else float("nan"),
                    "rand_null_std": r_std,
                    "rand_z": (o - r_arr.mean()) / r_std if r_std and r_std > 0 else float("nan"),
                    "matched_null_mean": float(m_arr.mean()) if m_arr.size else float("nan"),
                    "matched_null_std": m_std,
                    "matched_z": (o - m_arr.mean()) / m_std if m_std and m_std > 0 else float("nan"),
                }
            )
    return pd.DataFrame(rows)


def grouped_summary(
    panel: pd.DataFrame,
    by: str | list[str],
    *,
    state: str = "C1_trend_cont_long",
    horizon: int = 60,
) -> pd.DataFrame:
    """Mean/median/t-stat of signed forward return by a covariate group.

    Descriptive only. ``by`` is a column (or list) in the panel; ``state`` and
    ``horizon`` pick which event type / forward window to summarise.
    """
    ret_col = f"ret_{horizon}"
    sub = panel[panel["state"] == state].copy()
    sub = sub[~sub[ret_col].isna()]
    if sub.empty:
        return pd.DataFrame()
    rows: list[dict] = []
    keys = [by] if isinstance(by, str) else by
    for key, grp in sub.groupby(by, sort=True):
        r = grp[ret_col].to_numpy(dtype=float)
        nobs = r.size
        mean = float(np.mean(r))
        std = float(np.std(r, ddof=1)) if nobs > 1 else float("nan")
        t = mean / (std / np.sqrt(nobs)) if (std and std > 0 and nobs > 1) else float("nan")
        row = {"state": state, "horizon_min": horizon, "n": nobs,
               "mean_ret": mean, "median_ret": float(np.median(r)),
               "t_stat": t, "p_neg": float(np.mean(r < 0)),
               "mean_spread": _safe_nanmean(grp["spread"]),
               "mean_vol": _safe_nanmean(grp["volatility"])}
        if len(keys) == 1:
            row[keys[0]] = key
        else:
            for k, v in zip(keys, key, strict=True):
                row[k] = v
        rows.append(row)
    out = pd.DataFrame(rows)
    front = keys + ["state", "horizon_min", "n", "mean_ret", "median_ret",
                    "t_stat", "p_neg", "mean_spread", "mean_vol"]
    return out[[c for c in front if c in out.columns]]
