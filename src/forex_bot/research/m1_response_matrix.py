"""M1 / HTF confluence response matrix (research-only).

Factor-discovery and response-analysis ONLY. Given a higher-timeframe (HTF)
confluence *state*, this module measures what 1-minute (M1) price does afterward.

It deliberately contains **no** trade mechanics: no positions, no entries/exits,
no stops, no targets, no sizing, no PnL, no optimization, no approval, and no
network / OANDA / credentials. Spread is *recorded and reported* for
spread-awareness, but never gates or closes anything.

The public surface is split so the analysis core is testable on synthetic data:

* primitives / features      -> ``htf_features``
* lookahead-safe alignment   -> ``align_asof`` / ``build_confluence_frame``
* state definitions          -> ``confluence_states`` (see also STATE doc)
* event sampling             -> ``extract_events`` (rising-edge + cooldown)
* forward response           -> ``forward_response`` (5/10/15/30/60 min)
* aggregation                -> ``summarize``
* null sampling              -> ``sample_random_events`` / ``sample_matched_null``

See ``docs/research/M1_HTF_CONFLUENCE_STATE_DEFINITIONS.md`` for the locked
definitions this module implements.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from forex_bot.strategies import indicators as ind

# --------------------------------------------------------------------------- #
# Locked parameters (mirror the state-definitions doc).
# --------------------------------------------------------------------------- #

HORIZONS_MIN: tuple[int, ...] = (5, 10, 15, 30, 60)

EMA_FAST = 20
EMA_SLOW = 50
SLOPE_LOOKBACK = 3
DONCHIAN = 20
ATR_LEN = 14
COMPRESSION_WINDOW = 100
COMPRESSION_Q = 0.33
COOLDOWN_MIN = 60
GAP_TOL_MIN = 5

# Timeframe bar lengths in minutes (completion offset for lookahead-safety).
TF_MINUTES: dict[str, int] = {"M1": 1, "M5": 5, "M15": 15, "H1": 60, "H4": 240}

# Per-family timeframe roles: (structure_tf, trend_tfs, vol_tf).
FAMILY_TFS: dict[str, tuple[str, tuple[str, ...], str]] = {
    "A": ("M5", ("M15",), "M15"),
    "B": ("M15", ("H1",), "H1"),
    "C": ("M15", ("H1", "H4"), "H4"),
}

_PIP = {
    "USD_JPY": 0.01,
    "EUR_USD": 0.0001,
    "GBP_USD": 0.0001,
    "AUD_USD": 0.0001,
    "NZD_USD": 0.0001,
    "USD_CAD": 0.0001,
    "USD_CHF": 0.0001,
}


def pip_size(pair: str) -> float:
    """Pip size for a pair; JPY-quoted pairs use 0.01, others 0.0001."""
    if pair in _PIP:
        return _PIP[pair]
    return 0.01 if pair.endswith("_JPY") else 0.0001


# --------------------------------------------------------------------------- #
# Sessions.
# --------------------------------------------------------------------------- #


def sessions_of(index: pd.DatetimeIndex) -> pd.Series:
    """Map a UTC DatetimeIndex to session labels (tokyo/london/ny/offhours)."""
    hour = index.hour
    out = np.full(len(index), "offhours", dtype=object)
    out[(hour >= 0) & (hour < 7)] = "tokyo"
    out[(hour >= 7) & (hour < 12)] = "london"
    out[(hour >= 12) & (hour < 21)] = "ny"
    return pd.Series(out, index=index, name="session")


# --------------------------------------------------------------------------- #
# HTF primitives / features.
# --------------------------------------------------------------------------- #


def htf_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the locked primitives on an HTF OHLC frame.

    ``df`` must be indexed by (UTC, ascending) bar time with ``open/high/low/
    close`` columns. Returns a new frame of numeric features and boolean
    primitives. Everything is computed from the bar's own completed values;
    lookahead-safety across timeframes is handled later by :func:`align_asof`.
    """
    close = df["close"]
    high = df["high"]
    low = df["low"]

    ema_fast = ind.ema(close, EMA_FAST)
    ema_slow = ind.ema(close, EMA_SLOW)
    # EMA50 slope: change in EMA50 over SLOPE_LOOKBACK completed bars.
    slope = ema_slow - ema_slow.shift(SLOPE_LOOKBACK)
    atr = ind.atr(high, low, close, ATR_LEN)
    don_hi_prev = ind.donchian_high(high, DONCHIAN).shift(1)
    don_lo_prev = ind.donchian_low(low, DONCHIAN).shift(1)
    atr_q = atr.rolling(COMPRESSION_WINDOW, min_periods=EMA_SLOW).quantile(COMPRESSION_Q)

    out = pd.DataFrame(index=df.index)
    out["atr"] = atr
    out["trend_up"] = (close > ema_slow) & (slope > 0)
    out["trend_down"] = (close < ema_slow) & (slope < 0)
    out["aligned_up"] = close > ema_slow
    out["aligned_down"] = close < ema_slow
    out["pullback_up"] = (close > ema_slow) & (close < ema_fast)
    out["pullback_down"] = (close < ema_slow) & (close > ema_fast)
    out["breakout_up"] = close > don_hi_prev
    out["breakout_down"] = close < don_lo_prev
    out["compression"] = atr <= atr_q
    # Boolean columns: NaN-driven comparisons already resolve to False.
    bool_cols = [c for c in out.columns if c != "atr"]
    out[bool_cols] = out[bool_cols].fillna(False).astype(bool)
    return out


# --------------------------------------------------------------------------- #
# Lookahead-safe alignment.
# --------------------------------------------------------------------------- #


def align_asof(
    m1_index: pd.DatetimeIndex,
    htf_features_df: pd.DataFrame,
    *,
    tf_minutes: int,
    prefix: str,
) -> pd.DataFrame:
    """As-of merge HTF features onto M1 timestamps, lookahead-safe.

    An HTF bar stamped at time ``T`` only *completes* at ``T + tf_minutes``, so
    it may inform an M1 bar only at or after that completion time. We therefore
    key the merge on the HTF completion time, not the bar-open time.
    """
    if not m1_index.is_monotonic_increasing:
        raise ValueError("m1_index must be sorted ascending")
    htf = htf_features_df.sort_index()
    right = htf.reset_index()
    time_col = right.columns[0]
    # HTF bar at time T completes at T + tf_minutes; key the merge on completion
    # time so a bar can only inform M1 bars at/after it has closed (tz preserved).
    right["_avail"] = (right[time_col] + pd.Timedelta(minutes=tf_minutes)).dt.as_unit("ns")
    right = right.drop(columns=[time_col]).sort_values("_avail")

    left = pd.DataFrame({"_m1": pd.DatetimeIndex(m1_index).as_unit("ns")})
    merged = pd.merge_asof(
        left,
        right,
        left_on="_m1",
        right_on="_avail",
        direction="backward",
    )
    merged = merged.drop(columns=["_m1", "_avail"])
    merged.index = m1_index
    merged.columns = [f"{prefix}_{c}" for c in merged.columns]
    return merged


def build_confluence_frame(
    m1_df: pd.DataFrame,
    htf_frames: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Join M1 price/spread columns with lookahead-safe HTF primitives.

    ``m1_df``: UTC-indexed M1 frame with at least ``mid_c`` and ``spread_close``.
    ``htf_frames``: ``{tf_label: ohlc_df}`` for the TFs referenced by the states
    (e.g. ``M5``, ``M15``, ``H1``, ``H4``). Returns the M1 frame augmented with
    ``{TF}_*`` primitive columns and ``{TF}_atr``.
    """
    pieces = [m1_df]
    for tf, ohlc in htf_frames.items():
        feats = htf_features(ohlc)
        aligned = align_asof(
            m1_df.index, feats, tf_minutes=TF_MINUTES[tf], prefix=tf
        )
        pieces.append(aligned)
    return pd.concat(pieces, axis=1)


# --------------------------------------------------------------------------- #
# State definitions (signed context series).
# --------------------------------------------------------------------------- #


def _state_conditions(frame: pd.DataFrame) -> dict[str, pd.Series]:
    """Map archetype name -> (long_condition, short_condition) booleans."""
    f = frame
    specs: dict[str, tuple[pd.Series, pd.Series]] = {
        # Family A: M5 structure + M15 trend
        "A1_trend_cont": (
            f["M15_trend_up"] & f["M5_aligned_up"],
            f["M15_trend_down"] & f["M5_aligned_down"],
        ),
        "A2_pullback": (
            f["M15_trend_up"] & f["M5_pullback_up"],
            f["M15_trend_down"] & f["M5_pullback_down"],
        ),
        "A3_breakout": (
            f["M15_trend_up"] & f["M5_breakout_up"],
            f["M15_trend_down"] & f["M5_breakout_down"],
        ),
        "A4_compression": (
            f["M15_trend_up"] & f["M5_compression"],
            f["M15_trend_down"] & f["M5_compression"],
        ),
        # Family B: M15 structure + H1 trend
        "B1_trend_cont": (
            f["H1_trend_up"] & f["M15_aligned_up"],
            f["H1_trend_down"] & f["M15_aligned_down"],
        ),
        "B2_pullback": (
            f["H1_trend_up"] & f["M15_pullback_up"],
            f["H1_trend_down"] & f["M15_pullback_down"],
        ),
        "B3_breakout": (
            f["H1_trend_up"] & f["M15_breakout_up"],
            f["H1_trend_down"] & f["M15_breakout_down"],
        ),
        # Family C: M15 structure + H1 trend + H4 trend
        "C1_trend_cont": (
            f["H4_trend_up"] & f["H1_trend_up"] & f["M15_aligned_up"],
            f["H4_trend_down"] & f["H1_trend_down"] & f["M15_aligned_down"],
        ),
        "C2_pullback": (
            f["H4_trend_up"] & f["H1_trend_up"] & f["M15_pullback_up"],
            f["H4_trend_down"] & f["H1_trend_down"] & f["M15_pullback_down"],
        ),
    }
    return specs  # type: ignore[return-value]


def state_family(state_name: str) -> str:
    """Family letter (A/B/C) for an archetype or signed-state name."""
    return state_name[0]


def confluence_states(frame: pd.DataFrame) -> dict[str, pd.Series]:
    """Return signed context series in {-1, 0, +1} per signed state name.

    For each archetype, a ``*_long`` (direction +1) and ``*_short`` (direction
    −1) series are produced. The value is the direction where the context holds,
    else 0.
    """
    out: dict[str, pd.Series] = {}
    for arch, (long_cond, short_cond) in _state_conditions(frame).items():
        out[f"{arch}_long"] = pd.Series(
            np.where(long_cond.to_numpy(), 1, 0), index=frame.index, name=f"{arch}_long"
        )
        out[f"{arch}_short"] = pd.Series(
            np.where(short_cond.to_numpy(), -1, 0),
            index=frame.index,
            name=f"{arch}_short",
        )
    return out


# --------------------------------------------------------------------------- #
# Event sampling.
# --------------------------------------------------------------------------- #


def extract_events(
    signed: pd.Series,
    frame: pd.DataFrame,
    *,
    pair: str,
    state: str,
    vol_col: str | None = None,
    cooldown_min: int = COOLDOWN_MIN,
) -> pd.DataFrame:
    """Rising-edge + cooldown event sampling for one signed state series.

    Returns one row per event with ``timestamp, pair, state, direction,
    session, spread`` (pips) and ``volatility`` (pips, from ``vol_col`` if
    given) — the recorded fields from the definitions doc.
    """
    active = signed != 0
    prev = active.shift(1, fill_value=False)
    rising = active & ~prev
    rising_idx = frame.index[rising.to_numpy()]

    pip = pip_size(pair)
    cooldown = pd.Timedelta(minutes=cooldown_min)
    kept: list[pd.Timestamp] = []
    last: pd.Timestamp | None = None
    for ts in rising_idx:
        if last is None or (ts - last) >= cooldown:
            kept.append(ts)
            last = ts
    if not kept:
        return _empty_events()

    sub = frame.loc[kept]
    directions = signed.loc[kept].astype(int).to_numpy()
    spreads = (sub["spread_close"].to_numpy() / pip) if "spread_close" in sub else np.full(len(kept), np.nan)
    if vol_col is not None and vol_col in sub:
        vol = sub[vol_col].to_numpy() / pip
    else:
        vol = np.full(len(kept), np.nan)
    return pd.DataFrame(
        {
            "timestamp": pd.DatetimeIndex(kept),
            "pair": pair,
            "state": state,
            "direction": directions,
            "session": sessions_of(pd.DatetimeIndex(kept)).to_numpy(),
            "spread": spreads,
            "volatility": vol,
        }
    )


def _empty_events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.DatetimeIndex([], tz="UTC"),
            "pair": pd.Series([], dtype=object),
            "state": pd.Series([], dtype=object),
            "direction": pd.Series([], dtype=int),
            "session": pd.Series([], dtype=object),
            "spread": pd.Series([], dtype=float),
            "volatility": pd.Series([], dtype=float),
        }
    )


# --------------------------------------------------------------------------- #
# Forward response.
# --------------------------------------------------------------------------- #


def forward_response(
    m1_df: pd.DataFrame,
    events: pd.DataFrame,
    *,
    pair: str,
    horizons_min: tuple[int, ...] = HORIZONS_MIN,
    gap_tol_min: int = GAP_TOL_MIN,
    price_col: str = "mid_c",
) -> pd.DataFrame:
    """Measure signed forward response per event over each horizon.

    Adds, per horizon ``h``: ``ret_{h}`` (signed forward return, pips),
    ``mfe_{h}`` (max favorable excursion, pips), ``mae_{h}`` (max adverse
    excursion magnitude, pips). NaN where a data/weekend gap means the horizon
    endpoint is unavailable within ``gap_tol_min``. No PnL, no positions.
    """
    out = events.copy().reset_index(drop=True)
    if out.empty:
        for h in horizons_min:
            out[f"ret_{h}"] = pd.Series(dtype=float)
            out[f"mfe_{h}"] = pd.Series(dtype=float)
            out[f"mae_{h}"] = pd.Series(dtype=float)
        return out

    pip = pip_size(pair)
    # Use datetime64/timedelta64 throughout so the result is independent of the
    # index's time resolution (ns vs us) — avoids unit-mismatch bugs.
    times = m1_df.index.to_numpy()  # datetime64, UTC, ascending
    mids = m1_df[price_col].to_numpy(dtype=float)
    n = len(times)
    tol = np.timedelta64(int(gap_tol_min) * 60, "s")

    ev_times = pd.DatetimeIndex(out["timestamp"]).to_numpy()
    directions = out["direction"].to_numpy(dtype=float)
    pos0 = np.searchsorted(times, ev_times, side="left")

    results = {h: {"ret": [], "mfe": [], "mae": []} for h in horizons_min}
    for i in range(len(out)):
        p0 = pos0[i]
        # Event timestamp must land exactly on an M1 bar.
        if p0 >= n or times[p0] != ev_times[i]:
            for h in horizons_min:
                results[h]["ret"].append(np.nan)
                results[h]["mfe"].append(np.nan)
                results[h]["mae"].append(np.nan)
            continue
        entry = mids[p0]
        d = directions[i]
        for h in horizons_min:
            target = ev_times[i] + np.timedelta64(h * 60, "s")
            end = np.searchsorted(times, target, side="left")
            if end >= n or (times[end] - target) > tol or end <= p0:
                results[h]["ret"].append(np.nan)
                results[h]["mfe"].append(np.nan)
                results[h]["mae"].append(np.nan)
                continue
            window = mids[p0 + 1 : end + 1]
            dd = d * (window - entry) / pip
            results[h]["ret"].append(d * (mids[end] - entry) / pip)
            results[h]["mfe"].append(float(max(dd.max(), 0.0)))
            results[h]["mae"].append(float(max(-dd.min(), 0.0)))

    for h in horizons_min:
        out[f"ret_{h}"] = results[h]["ret"]
        out[f"mfe_{h}"] = results[h]["mfe"]
        out[f"mae_{h}"] = results[h]["mae"]
    return out


# --------------------------------------------------------------------------- #
# Aggregation.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ResponseCell:
    """Aggregate response for one (state, horizon)."""

    state: str
    horizon_min: int
    n: int
    mean_ret: float
    median_ret: float
    std_ret: float
    t_stat: float
    hit_rate: float
    p_pos: float
    p_neg: float
    mean_mfe: float
    mean_mae: float
    mfe_mae: float
    mean_spread: float
    mean_vol: float


def summarize(
    response_df: pd.DataFrame,
    *,
    horizons_min: tuple[int, ...] = HORIZONS_MIN,
) -> pd.DataFrame:
    """Aggregate per-event response into one row per (state, horizon)."""
    rows: list[ResponseCell] = []
    if response_df.empty:
        return pd.DataFrame([c.__dict__ for c in rows])
    for state, grp in response_df.groupby("state", sort=True):
        mean_spread = float(np.nanmean(grp["spread"])) if "spread" in grp else float("nan")
        mean_vol = float(np.nanmean(grp["volatility"])) if "volatility" in grp else float("nan")
        for h in horizons_min:
            r = grp[f"ret_{h}"].to_numpy(dtype=float)
            r = r[~np.isnan(r)]
            nobs = int(r.size)
            if nobs == 0:
                continue
            mean = float(np.mean(r))
            std = float(np.std(r, ddof=1)) if nobs > 1 else float("nan")
            t = mean / (std / np.sqrt(nobs)) if (std and std > 0 and nobs > 1) else float("nan")
            mfe = float(np.nanmean(grp[f"mfe_{h}"]))
            mae = float(np.nanmean(grp[f"mae_{h}"]))
            rows.append(
                ResponseCell(
                    state=str(state),
                    horizon_min=h,
                    n=nobs,
                    mean_ret=mean,
                    median_ret=float(np.median(r)),
                    std_ret=std,
                    t_stat=t,
                    hit_rate=float(np.mean(r > 0)),
                    p_pos=float(np.mean(r > 0)),
                    p_neg=float(np.mean(r < 0)),
                    mean_mfe=mfe,
                    mean_mae=mae,
                    mfe_mae=(mfe / mae) if mae > 0 else float("nan"),
                    mean_spread=mean_spread,
                    mean_vol=mean_vol,
                )
            )
    return pd.DataFrame([c.__dict__ for c in rows])


# --------------------------------------------------------------------------- #
# Null sampling (for the Phase-5 comparison).
# --------------------------------------------------------------------------- #


def sample_random_events(
    m1_df: pd.DataFrame,
    *,
    pair: str,
    n: int,
    direction: int,
    seed: int,
    sessions: pd.Series | None = None,
    allowed_sessions: list[str] | None = None,
    label: str = "_null_random",
) -> pd.DataFrame:
    """Draw ``n`` random M1 timestamps as a null event set (fixed direction).

    ``allowed_sessions`` restricts the candidate pool to those session labels
    (used for session-matched nulls). Sampling is without replacement when
    possible and deterministic under ``seed``.
    """
    if sessions is None:
        sessions = sessions_of(m1_df.index)
    if allowed_sessions is not None:
        mask = sessions.isin(allowed_sessions).to_numpy()
        candidates = m1_df.index[mask]
    else:
        candidates = m1_df.index
    if len(candidates) == 0:
        return _empty_events()
    rng = np.random.default_rng(seed)
    replace = n > len(candidates)
    picks = rng.choice(len(candidates), size=n, replace=replace)
    ts = pd.DatetimeIndex(candidates[np.sort(picks)])
    return pd.DataFrame(
        {
            "timestamp": ts,
            "pair": pair,
            "state": label,
            "direction": int(direction),
            "session": sessions_of(ts).to_numpy(),
            "spread": np.nan,
            "volatility": np.nan,
        }
    )


def sample_matched_null(
    m1_df: pd.DataFrame,
    reference_events: pd.DataFrame,
    *,
    pair: str,
    seed: int,
    label: str = "_null_matched",
) -> pd.DataFrame:
    """Session- and direction-matched null: one random M1 bar per reference
    event, drawn from the same session and given the same direction."""
    if reference_events.empty:
        return _empty_events()
    sessions = sessions_of(m1_df.index)
    rng = np.random.default_rng(seed)
    by_session: dict[str, np.ndarray] = {}
    for sess in reference_events["session"].unique():
        by_session[sess] = np.flatnonzero((sessions == sess).to_numpy())

    ts_list: list[pd.Timestamp] = []
    dirs: list[int] = []
    for _, ev in reference_events.iterrows():
        pool = by_session.get(ev["session"])
        if pool is None or pool.size == 0:
            continue
        pick = pool[rng.integers(0, pool.size)]
        ts_list.append(m1_df.index[pick])
        dirs.append(int(ev["direction"]))
    if not ts_list:
        return _empty_events()
    ts = pd.DatetimeIndex(ts_list)
    order = np.argsort(ts.asi8)
    ts = ts[order]
    dirs_arr = np.asarray(dirs)[order]
    return pd.DataFrame(
        {
            "timestamp": ts,
            "pair": pair,
            "state": label,
            "direction": dirs_arr,
            "session": sessions_of(ts).to_numpy(),
            "spread": np.nan,
            "volatility": np.nan,
        }
    )
