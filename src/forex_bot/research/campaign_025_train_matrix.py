"""CAMPAIGN_025 train-matrix simulator — vectorized M5 backtest for the candidate
matrix (scaffold-evidence lane, no test lockbox, no approval).

This is an isolated research simulator. It does NOT modify the shared
``forex_bot.backtesting`` engine, the executor, or any broker code. It precomputes
indicators once per pair and simulates each candidate's trades with candidate-
specific exit models (time-stop-only, fixed 2R/3R, breakeven-then-ATR-trail,
Donchian channel exit). Fills are ``next_bar_open`` only; same-bar stop/target
ambiguity resolves adverse-first; HTF context is the last completed bar (no
lookahead). See docs/research/CAMPAIGN_025_TRAIN_MATRIX_SPEC.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from forex_bot.research.campaign_025_loader import C025Frames
from forex_bot.strategies.indicators import atr, donchian_high, donchian_low, ema

# C011 deduped null baseline (per-R) and the beat-by margin (frozen).
C011_NULL_EXP_R = -0.0029154071495408797
BEAT_NULL_MARGIN = 0.010

# Cost regimes (frozen; mirror the C021 lane).
COST_BASE = {"name": "base", "fixed_slippage_pips": 0.2, "spread_multiplier": 0.5}
COST_STRESS_2X = {"name": "stress_2x", "fixed_slippage_pips": 0.5, "spread_multiplier": 2.0}

# Frozen base parameters shared by all candidates.
ATR_LOOKBACK = 14
M15_EMA_FAST = 20
M15_PULLBACK_LOOKBACK = 8
M15_COMPRESSION_DONCHIAN = 12
M15_COMPRESSION_ATR = 14
M15_COMPRESSION_WIDTH_ATR_MAX = 3.0
H1_EMA_FAST, H1_EMA_SLOW, H1_SLOPE_BARS = 20, 50, 3
H4_EMA_FAST, H4_EMA_SLOW = 20, 50
D1_EMA_FAST, D1_EMA_SLOW, D1_SLOPE_BARS = 20, 50, 3
DONCHIAN_LENGTHS = (12, 20, 30)

# Train-only selection filters (frozen — see spec §"Train-only selection filters").
TRAIN_MIN_TRADES = 100
TRAIN_MIN_PF = 1.03
TRAIN_MIN_PAIRS_NONNEG = 3
TRAIN_STRESS_MIN_EXP = -0.005
SINGLE_PAIR_CONCENTRATION_MAX = 0.50

EXIT_REASONS = (
    "hard_stop",
    "fixed_target_2r",
    "fixed_target_3r",
    "breakeven_stop",
    "atr_trailing_stop",
    "donchian_channel_exit",
    "time_stop",
    "end_of_data",
)


def _pip_size(instrument_name: str) -> float:
    return 0.01 if instrument_name.endswith("JPY") else 0.0001


def _htf_trend_frame(frame, *, ema_fast: int, ema_slow: int) -> pd.DataFrame:
    df = frame.completed_only().df
    if df.empty:
        return pd.DataFrame(columns=["time", "close", "ema_fast", "ema_slow"])
    close = df["close"].astype(float).reset_index(drop=True)
    out = pd.DataFrame(
        {
            "time": pd.to_datetime(df.index, utc=True),
            "close": close.to_numpy(),
            "ema_fast": ema(close, ema_fast).to_numpy(),
            "ema_slow": ema(close, ema_slow).to_numpy(),
        }
    )
    return out


def _slope(series: pd.Series, bars: int) -> pd.Series:
    return series - series.shift(bars)


@dataclass
class PairFeatures:
    instrument: str
    index: pd.DatetimeIndex
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    atr: np.ndarray
    spread_pips: np.ndarray
    pip_size: float
    dc_high: dict[int, np.ndarray]
    dc_low: dict[int, np.ndarray]
    # aligned HTF/M15 features (last completed bar, no lookahead)
    h4_trend: np.ndarray  # +1 bull / -1 bear / 0
    h1_standard: np.ndarray
    h1_strict: np.ndarray
    d1_not_bearish: np.ndarray  # bool
    d1_not_bullish: np.ndarray
    m15_pullback_long: np.ndarray
    m15_pullback_short: np.ndarray
    m15_compression: np.ndarray
    warm_mask: np.ndarray  # bars with all indicators/context defined


def _merge_asof_to_m5(m5_index: pd.DatetimeIndex, htf: pd.DataFrame, cols: list[str]) -> dict[str, np.ndarray]:
    """Map last-completed HTF values onto the M5 index (backward, exact ok)."""
    base = pd.DataFrame({"time": m5_index})
    if htf.empty:
        return {c: np.full(len(m5_index), np.nan) for c in cols}
    merged = pd.merge_asof(
        base, htf[["time", *cols]].sort_values("time"), on="time", direction="backward", allow_exact_matches=True
    )
    return {c: merged[c].to_numpy() for c in cols}


def load_features_for_window(
    store: Any, pairs: list[str], *, window_start: datetime, window_end: datetime, warmup_days: int = 60
) -> dict[str, PairFeatures]:
    """Load each pair once (with a warmup buffer) and precompute features.

    Warmup bars before window_start are used only for indicator/context warmup;
    they never produce counted trades (the simulate functions gate on the window).
    """
    from datetime import timedelta

    from forex_bot.research.campaign_025_loader import load_c025_frames

    load_from = window_start - timedelta(days=warmup_days)
    feats: dict[str, PairFeatures] = {}
    for pair in pairs:
        frames = load_c025_frames(store, pair, from_dt=load_from, to_dt=window_end)
        feats[pair] = precompute_pair_features(frames)
    return feats


def precompute_pair_features(frames: C025Frames) -> PairFeatures:
    m5 = frames.m5.completed_only().df
    idx = m5.index
    high = m5["high"].astype(float)
    low = m5["low"].astype(float)
    close = m5["close"].astype(float)
    open_ = m5["open"].astype(float)
    atr_m5 = atr(high, low, close, ATR_LOOKBACK)
    pip = _pip_size(frames.instrument)
    if {"bid_close", "ask_close"}.issubset(m5.columns):
        spread_pips = ((m5["ask_close"].astype(float) - m5["bid_close"].astype(float)) / pip).clip(lower=0.0)
    else:
        spread_pips = pd.Series(np.full(len(m5), 1.0), index=m5.index)
    dc_high = {n: donchian_high(high, n).to_numpy() for n in DONCHIAN_LENGTHS}
    dc_low = {n: donchian_low(low, n).to_numpy() for n in DONCHIAN_LENGTHS}

    # ---- M15 features (per M15 bar) ----
    m15 = frames.m15.completed_only().df
    m15_close = m15["close"].astype(float)
    m15_ema = ema(m15_close, M15_EMA_FAST)
    pull_long_bar = (m15["low"].astype(float).to_numpy() <= m15_ema.to_numpy())
    pull_short_bar = (m15["high"].astype(float).to_numpy() >= m15_ema.to_numpy())
    # rolling OR over last pullback_lookback bars
    pl = pd.Series(pull_long_bar).rolling(M15_PULLBACK_LOOKBACK, min_periods=1).max().fillna(0).astype(bool)
    ps = pd.Series(pull_short_bar).rolling(M15_PULLBACK_LOOKBACK, min_periods=1).max().fillna(0).astype(bool)
    m15_dc_w = donchian_high(m15["high"].astype(float), M15_COMPRESSION_DONCHIAN) - donchian_low(
        m15["low"].astype(float), M15_COMPRESSION_DONCHIAN
    )
    m15_atr = atr(m15["high"].astype(float), m15["low"].astype(float), m15_close, M15_COMPRESSION_ATR)
    comp = (m15_dc_w / m15_atr) <= M15_COMPRESSION_WIDTH_ATR_MAX
    m15_feat = pd.DataFrame(
        {
            "time": pd.to_datetime(m15.index, utc=True),
            "pull_long": pl.to_numpy(),
            "pull_short": ps.to_numpy(),
            "compression": comp.fillna(False).to_numpy(),
        }
    )

    # ---- H1 ----
    h1 = _htf_trend_frame(frames.h1, ema_fast=H1_EMA_FAST, ema_slow=H1_EMA_SLOW)
    if not h1.empty:
        h1_slope = _slope(pd.Series(h1["ema_fast"]), H1_SLOPE_BARS)
        ef, es, cl = h1["ema_fast"], h1["ema_slow"], h1["close"]
        std = np.where((ef > es) & (h1_slope >= 0), 1, np.where((ef < es) & (h1_slope <= 0), -1, 0))
        strict = np.where(
            (ef > es) & (h1_slope >= 0) & (cl > es), 1,
            np.where((ef < es) & (h1_slope <= 0) & (cl < es), -1, 0),
        )
        h1["std"] = std
        h1["strict"] = strict

    # ---- H4 (H4M1) ----
    h4 = _htf_trend_frame(frames.h4, ema_fast=H4_EMA_FAST, ema_slow=H4_EMA_SLOW)
    if not h4.empty:
        ef, es, cl = h4["ema_fast"], h4["ema_slow"], h4["close"]
        h4["trend"] = np.where((cl > es) & (ef >= es), 1, np.where((cl < es) & (ef <= es), -1, 0))

    # ---- D1AGG ----
    d1 = _htf_trend_frame(frames.d1agg, ema_fast=D1_EMA_FAST, ema_slow=D1_EMA_SLOW)
    if not d1.empty:
        d1_slope = _slope(pd.Series(d1["ema_fast"]), D1_SLOPE_BARS)
        cl, es = d1["close"], d1["ema_slow"]
        d1["not_bearish"] = ((cl >= es) | (d1_slope >= 0)).astype(float)
        d1["not_bullish"] = ((cl <= es) | (d1_slope <= 0)).astype(float)

    a_h4 = _merge_asof_to_m5(idx, h4, ["trend"]) if not h4.empty else {"trend": np.full(len(idx), np.nan)}
    a_h1 = _merge_asof_to_m5(idx, h1, ["std", "strict"]) if not h1.empty else {"std": np.full(len(idx), np.nan), "strict": np.full(len(idx), np.nan)}
    a_d1 = _merge_asof_to_m5(idx, d1, ["not_bearish", "not_bullish"]) if not d1.empty else {"not_bearish": np.full(len(idx), np.nan), "not_bullish": np.full(len(idx), np.nan)}
    a_m15 = _merge_asof_to_m5(idx, m15_feat, ["pull_long", "pull_short", "compression"])

    h4_trend = np.nan_to_num(a_h4["trend"], nan=0.0).astype(int)
    h1_std = np.nan_to_num(a_h1["std"], nan=0.0).astype(int)
    h1_strict = np.nan_to_num(a_h1["strict"], nan=0.0).astype(int)
    d1_nb = np.nan_to_num(a_d1["not_bearish"], nan=0.0).astype(bool)
    d1_nbu = np.nan_to_num(a_d1["not_bullish"], nan=0.0).astype(bool)
    m15_pl = np.nan_to_num(a_m15["pull_long"], nan=0.0).astype(bool)
    m15_ps = np.nan_to_num(a_m15["pull_short"], nan=0.0).astype(bool)
    m15_comp = np.nan_to_num(a_m15["compression"], nan=0.0).astype(bool)

    # warmup: ATR + largest Donchian defined, and HTF context present
    warm = (
        ~np.isnan(atr_m5.to_numpy())
        & ~np.isnan(dc_high[max(DONCHIAN_LENGTHS)])
        & ~np.isnan(a_h4["trend"])
        & ~np.isnan(a_h1["std"])
        & ~np.isnan(a_d1["not_bearish"])
    )

    return PairFeatures(
        instrument=frames.instrument,
        index=idx,
        open=open_.to_numpy(),
        high=high.to_numpy(),
        low=low.to_numpy(),
        close=close.to_numpy(),
        atr=atr_m5.to_numpy(),
        spread_pips=spread_pips.to_numpy(),
        pip_size=pip,
        dc_high=dc_high,
        dc_low=dc_low,
        h4_trend=h4_trend,
        h1_standard=h1_std,
        h1_strict=h1_strict,
        d1_not_bearish=d1_nb,
        d1_not_bullish=d1_nbu,
        m15_pullback_long=m15_pl,
        m15_pullback_short=m15_ps,
        m15_compression=m15_comp,
        warm_mask=warm,
    )


def _m15_setup(mode: str, pull: np.ndarray, comp: np.ndarray) -> np.ndarray:
    if mode == "pullback_only":
        return pull
    if mode == "compression_only":
        return comp
    return pull | comp  # pullback_or_compression


def compute_signal_direction(feat: PairFeatures, candidate: dict) -> np.ndarray:
    """Return +1 (long) / -1 (short) / 0 per M5 bar for the candidate's gates."""
    n = candidate["m5_donchian_length"]
    h1 = feat.h1_strict if candidate["h1_trend_mode"] == "strict" else feat.h1_standard
    setup_long = _m15_setup(candidate["m15_setup_mode"], feat.m15_pullback_long, feat.m15_compression)
    setup_short = _m15_setup(candidate["m15_setup_mode"], feat.m15_pullback_short, feat.m15_compression)
    breakout_long = feat.close > feat.dc_high[n]
    breakout_short = feat.close < feat.dc_low[n]
    long_sig = (
        feat.warm_mask & breakout_long & (feat.h4_trend == 1) & (h1 == 1) & feat.d1_not_bearish & setup_long
    )
    short_sig = (
        feat.warm_mask & breakout_short & (feat.h4_trend == -1) & (h1 == -1) & feat.d1_not_bullish & setup_short
    )
    out = np.zeros(len(feat.close), dtype=int)
    out[long_sig] = 1
    out[short_sig] = -1  # breakout_long & breakout_short are mutually exclusive
    return out


@dataclass
class Trade:
    instrument: str
    side: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    initial_stop: float
    risk: float
    gross_r_multiple: float
    exit_reason: str
    hold_bars: int
    spread_pips_entry: float
    spread_pips_exit: float
    atr_at_entry_pips: float
    pip_size: float

    def net_r(self, cost: dict[str, Any]) -> float:
        """Net R after round-trip cost (fixed slippage + spread multiplier), per side."""
        fixed = cost["fixed_slippage_pips"]
        mult = cost["spread_multiplier"]
        cost_pips = (fixed + mult * self.spread_pips_entry) + (fixed + mult * self.spread_pips_exit)
        cost_price = cost_pips * self.pip_size
        return self.gross_r_multiple - (cost_price / self.risk if self.risk > 0 else 0.0)


def _initial_stop_and_risk(feat: PairFeatures, i: int, candidate: dict, side: int) -> tuple[float, float, float]:
    """At signal bar i: stop anchored at signal close; risk = |entry_open - stop|.

    entry_open is bar i+1's open. ATR uses the prior completed bar (i-1) to match
    the scaffold convention; structure = opposite prior Donchian channel side.
    """
    n = candidate["m5_donchian_length"]
    mult = candidate["atr_stop_multiple"]
    prior_atr = feat.atr[i - 1]
    sig_close = feat.close[i]
    if side == 1:
        structure = feat.dc_low[n][i]
    else:
        structure = feat.dc_high[n][i]
    d_atr = mult * prior_atr
    d_struct = abs(sig_close - structure)
    stop_dist = max(d_atr, d_struct)
    stop_price = sig_close - stop_dist if side == 1 else sig_close + stop_dist
    entry_price = feat.open[i + 1]
    risk = abs(entry_price - stop_price)
    return stop_price, risk, entry_price


def _simulate_trade(feat: PairFeatures, sig_i: int, side: int, candidate: dict) -> Trade | None:
    """Simulate one trade entered at sig_i+1 open. Returns None if not viable."""
    n_bars = len(feat.close)
    entry_i = sig_i + 1
    if entry_i >= n_bars:
        return None
    stop_price, risk, entry_price = _initial_stop_and_risk(feat, sig_i, candidate, side)
    if not np.isfinite(risk) or risk <= 0:
        return None
    exit_model = candidate["exit_model"]
    time_stop = candidate["time_stop_m5_bars"]
    target_r = candidate["target_r_multiple"]
    be_r = candidate["breakeven_trigger_r"]
    trail_act_r = candidate["trail_activation_r"]
    trail_mult = candidate["trail_atr_multiple"]
    chan_len = candidate["channel_exit_length"]

    target_price = None
    if target_r is not None:
        target_price = entry_price + target_r * risk if side == 1 else entry_price - target_r * risk

    cur_stop = stop_price
    stop_reason = "hard_stop"  # becomes breakeven_stop / atr_trailing_stop if moved
    be_done = False
    trail_on = False
    last = min(entry_i + time_stop, n_bars - 1)

    for k in range(entry_i, last + 1):
        hi, lo, cl = feat.high[k], feat.low[k], feat.close[k]
        # favorable excursion in R (intrabar)
        if side == 1:
            fav_r = (hi - entry_price) / risk
        else:
            fav_r = (entry_price - lo) / risk
        # --- adverse-first: hard/active stop checked before target ---
        stop_hit = (lo <= cur_stop) if side == 1 else (hi >= cur_stop)
        target_hit = target_price is not None and ((hi >= target_price) if side == 1 else (lo <= target_price))
        if stop_hit:
            return _mk_trade(feat, entry_i, k, side, candidate, entry_price, cur_stop, stop_price, risk, stop_reason)
        if target_hit:
            reason = "fixed_target_2r" if target_r == 2.0 else "fixed_target_3r"
            return _mk_trade(feat, entry_i, k, side, candidate, entry_price, target_price, stop_price, risk, reason)
        # --- breakeven / trailing management (after this bar's close) ---
        if exit_model == "breakeven_then_atr_trail":
            if not be_done and fav_r >= be_r:
                cur_stop = entry_price  # breakeven, same for long/short
                stop_reason = "breakeven_stop"
                be_done = True
            if fav_r >= trail_act_r:
                trail_on = True
            if trail_on and np.isfinite(feat.atr[k]):
                if side == 1:
                    new_stop = cl - trail_mult * feat.atr[k]
                    if new_stop > cur_stop:
                        cur_stop, stop_reason = new_stop, "atr_trailing_stop"
                else:
                    new_stop = cl + trail_mult * feat.atr[k]
                    if new_stop < cur_stop:
                        cur_stop, stop_reason = new_stop, "atr_trailing_stop"
        # --- donchian channel exit on completed close (fill next open) ---
        if exit_model == "donchian_channel_exit" and chan_len is not None:
            if side == 1 and np.isfinite(feat.dc_low[chan_len][k]) and cl < feat.dc_low[chan_len][k]:
                xi = min(k + 1, n_bars - 1)
                return _mk_trade(feat, entry_i, xi, side, candidate, entry_price, feat.open[xi], stop_price, risk, "donchian_channel_exit")
            if side == -1 and np.isfinite(feat.dc_high[chan_len][k]) and cl > feat.dc_high[chan_len][k]:
                xi = min(k + 1, n_bars - 1)
                return _mk_trade(feat, entry_i, xi, side, candidate, entry_price, feat.open[xi], stop_price, risk, "donchian_channel_exit")
        # --- time stop ---
        if k - entry_i >= time_stop:
            xi = min(k + 1, n_bars - 1)
            return _mk_trade(feat, entry_i, xi, side, candidate, entry_price, feat.open[xi], stop_price, risk, "time_stop")
    # ran out of data
    xi = last
    return _mk_trade(feat, entry_i, xi, side, candidate, entry_price, feat.close[xi], stop_price, risk, "end_of_data")


def _mk_trade(feat, entry_i, exit_i, side, candidate, entry_price, exit_price, initial_stop, risk, reason) -> Trade:
    gross = (exit_price - entry_price) if side == 1 else (entry_price - exit_price)
    r = gross / risk
    return Trade(
        instrument=feat.instrument,
        side="long" if side == 1 else "short",
        entry_time=feat.index[entry_i].to_pydatetime(),
        exit_time=feat.index[exit_i].to_pydatetime(),
        entry_price=float(entry_price),
        exit_price=float(exit_price),
        initial_stop=float(initial_stop),
        risk=float(risk),
        gross_r_multiple=float(r),
        exit_reason=reason,
        hold_bars=int(exit_i - entry_i),
        spread_pips_entry=float(feat.spread_pips[entry_i]),
        spread_pips_exit=float(feat.spread_pips[exit_i]),
        atr_at_entry_pips=float(feat.atr[entry_i] / feat.pip_size) if np.isfinite(feat.atr[entry_i]) else float("nan"),
        pip_size=feat.pip_size,
    )


def simulate_candidate_pair(
    feat: PairFeatures, candidate: dict, *, window_start: datetime, window_end: datetime
) -> tuple[list[Trade], dict[str, int]]:
    """Simulate all trades for one candidate/pair within [window_start, window_end].

    Only trades whose SIGNAL bar falls inside the window are kept (warmup bars
    before window_start are used for indicators but never produce counted trades).
    One position at a time; re-entry only after the prior trade exits.
    """
    direction = compute_signal_direction(feat, candidate)
    times = feat.index
    in_window = np.asarray((times >= pd.Timestamp(window_start)) & (times <= pd.Timestamp(window_end)))
    sig_idx = np.flatnonzero((direction != 0) & in_window)
    funnel = {"signals_in_window": int(sig_idx.size), "entries": 0}
    trades: list[Trade] = []
    pos = 0
    for i in sig_idx:
        if i < pos:
            continue  # still in a prior trade
        side = int(direction[i])
        tr = _simulate_trade(feat, int(i), side, candidate)
        if tr is None:
            continue
        trades.append(tr)
        funnel["entries"] += 1
        # find exit bar index to block re-entry until after exit
        exit_pos = int(np.searchsorted(times, pd.Timestamp(tr.exit_time)))
        pos = max(exit_pos + 1, int(i) + 1)
    return trades, funnel


def funnel_counts(feat: PairFeatures, candidate: dict, *, window_start: datetime, window_end: datetime) -> dict[str, int]:
    """Signal-funnel diagnostics (stage pass counts) within the window."""
    n = candidate["m5_donchian_length"]
    times = feat.index
    w = np.asarray((times >= pd.Timestamp(window_start)) & (times <= pd.Timestamp(window_end)))
    h1 = feat.h1_strict if candidate["h1_trend_mode"] == "strict" else feat.h1_standard
    setup_long = _m15_setup(candidate["m15_setup_mode"], feat.m15_pullback_long, feat.m15_compression)
    setup_short = _m15_setup(candidate["m15_setup_mode"], feat.m15_pullback_short, feat.m15_compression)
    breakout = (feat.close > feat.dc_high[n]) | (feat.close < feat.dc_low[n])
    base = w & feat.warm_mask
    return {
        "m5_bars_examined": int(np.count_nonzero(base)),
        "h4_context_pass": int(np.count_nonzero(base & (feat.h4_trend != 0))),
        "h1_context_pass": int(np.count_nonzero(base & (h1 != 0))),
        "d1agg_context_pass": int(np.count_nonzero(base & (feat.d1_not_bearish | feat.d1_not_bullish))),
        "m15_setup_pass": int(np.count_nonzero(base & (setup_long | setup_short))),
        "m5_breakout_pass": int(np.count_nonzero(base & breakout)),
    }


# --------------------------------------------------------------------------- #
# metrics
# --------------------------------------------------------------------------- #
def _expectancy(rs: list[float]) -> float | None:
    return float(np.mean(rs)) if rs else None


def _profit_factor(pnls: list[float]) -> float | None:
    gains = sum(p for p in pnls if p > 0)
    losses = -sum(p for p in pnls if p < 0)
    if losses == 0:
        return float("inf") if gains > 0 else None
    return float(gains / losses)


def aggregate_candidate_metrics(
    trades_by_pair: dict[str, list[Trade]], *, cost: dict[str, Any] = COST_BASE
) -> dict[str, Any]:
    all_trades = [t for ts in trades_by_pair.values() for t in ts]
    rs = [t.net_r(cost) for t in all_trades]
    pair_exp = {p: _expectancy([t.net_r(cost) for t in ts]) for p, ts in trades_by_pair.items()}
    pairs_nonneg = sum(1 for v in pair_exp.values() if v is not None and v >= 0)
    pos_r_by_pair = {p: sum(max(t.net_r(cost), 0.0) for t in ts) for p, ts in trades_by_pair.items()}
    total_pos = sum(pos_r_by_pair.values())
    top_conc = (max(pos_r_by_pair.values()) / total_pos) if total_pos > 0 else 0.0
    longs = [t.net_r(cost) for t in all_trades if t.side == "long"]
    shorts = [t.net_r(cost) for t in all_trades if t.side == "short"]
    exit_counts = {r: 0 for r in EXIT_REASONS}
    for t in all_trades:
        exit_counts[t.exit_reason] = exit_counts.get(t.exit_reason, 0) + 1
    holds = [t.hold_bars for t in all_trades]
    spreads = [t.spread_pips_entry for t in all_trades]
    atrs = [t.atr_at_entry_pips for t in all_trades if np.isfinite(t.atr_at_entry_pips)]
    spread_atr = (
        float(np.mean([s / a for s, a in zip(spreads, atrs, strict=False) if a > 0])) if atrs else None
    )
    exp = _expectancy(rs)
    return {
        "cost_regime": cost["name"],
        "trade_count": len(all_trades),
        "expectancy_r": exp,
        "profit_factor": _profit_factor(rs),
        "pairs_nonneg": pairs_nonneg,
        "pairs_total": len(trades_by_pair),
        "per_pair_expectancy_r": {p: (round(v, 5) if v is not None else None) for p, v in pair_exp.items()},
        "per_pair_trade_count": {p: len(ts) for p, ts in trades_by_pair.items()},
        "top_pair_positive_r_concentration": round(top_conc, 4),
        "long_count": len(longs),
        "short_count": len(shorts),
        "long_expectancy_r": _expectancy(longs),
        "short_expectancy_r": _expectancy(shorts),
        "exit_reason_counts": exit_counts,
        "avg_hold_bars": float(np.mean(holds)) if holds else 0.0,
        "median_hold_bars": float(np.median(holds)) if holds else 0.0,
        "avg_spread_atr_ratio": spread_atr,
        "beat_c011_null_by": (round(exp - C011_NULL_EXP_R, 5) if exp is not None else None),
    }


def simulate_all_pairs(
    feats: dict[str, PairFeatures], candidate: dict, *, window_start: datetime, window_end: datetime
) -> tuple[dict[str, list[Trade]], dict[str, dict[str, int]]]:
    trades_by_pair: dict[str, list[Trade]] = {}
    funnel_by_pair: dict[str, dict[str, int]] = {}
    for pair, feat in feats.items():
        trades, fn = simulate_candidate_pair(feat, candidate, window_start=window_start, window_end=window_end)
        trades_by_pair[pair] = trades
        stage = funnel_counts(feat, candidate, window_start=window_start, window_end=window_end)
        stage.update(fn)
        funnel_by_pair[pair] = stage
    return trades_by_pair, funnel_by_pair


def evaluate_candidate(
    feats: dict[str, PairFeatures], candidate: dict, *, window_start: datetime, window_end: datetime
) -> dict[str, Any]:
    trades_by_pair, funnel_by_pair = simulate_all_pairs(
        feats, candidate, window_start=window_start, window_end=window_end
    )
    base = aggregate_candidate_metrics(trades_by_pair, cost=COST_BASE)
    stress = aggregate_candidate_metrics(trades_by_pair, cost=COST_STRESS_2X)
    filters = apply_train_filters(base, stress["expectancy_r"])
    # aggregate funnel across pairs
    funnel_total: dict[str, int] = {}
    for fn in funnel_by_pair.values():
        for k, v in fn.items():
            funnel_total[k] = funnel_total.get(k, 0) + v
    return {
        "candidate_id": candidate["candidate_id"],
        "archetype": candidate.get("archetype"),
        "candidate": candidate,
        "base": base,
        "stress_2x": stress,
        "filters": filters,
        "funnel_total": funnel_total,
        "funnel_by_pair": funnel_by_pair,
        "trades_by_pair": trades_by_pair,
    }


def _cost_stress_adjusted_exp(ev: dict[str, Any]) -> float:
    b = ev["base"]["expectancy_r"]
    s = ev["stress_2x"]["expectancy_r"]
    if b is None:
        return -999.0
    if s is None:
        return b
    return 0.5 * (b + s)


def rank_and_select(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply train filters + ranking; select at most one champion (train only).

    Validation metrics are NEVER consulted here.
    """
    any_reached_100 = any(ev["base"]["trade_count"] >= TRAIN_MIN_TRADES for ev in evaluations)
    if not any_reached_100:
        return {
            "champion_candidate_id": None,
            "classification": "BLOCKED_MATRIX_TOO_SPARSE",
            "reason": "no candidate reached 100 train trades",
            "selection_uses_validation": False,
            "eligible_candidates": [],
            "single_pair_review_flags": [
                ev["candidate_id"] for ev in evaluations if ev["filters"].get("single_pair_review_flag")
            ],
        }
    eligible = [ev for ev in evaluations if ev["filters"]["eligible"]]
    spr_flags = [ev["candidate_id"] for ev in evaluations if ev["filters"].get("single_pair_review_flag")]
    if not eligible:
        classification = "REJECT_MATRIX_NO_TRAIN_CANDIDATE"
        if spr_flags:
            classification = "SINGLE_PAIR_REVIEW_ONLY_CANDIDATE"
        return {
            "champion_candidate_id": None,
            "classification": classification,
            "reason": "no candidate passed all train filters",
            "selection_uses_validation": False,
            "eligible_candidates": [],
            "single_pair_review_flags": spr_flags,
        }

    def sort_key(ev: dict[str, Any]) -> tuple:
        b = ev["base"]
        return (
            -_cost_stress_adjusted_exp(ev),          # 1. cost-stress-adjusted expectancy (desc)
            -b["pairs_nonneg"],                       # 2. non-negative pairs (desc)
            b["top_pair_positive_r_concentration"],   # 3. concentration (asc)
            -(b["profit_factor"] or 0),               # 5. PF (desc)
            b["trade_count"],                          # 6. lower turnover (asc)
            ev["candidate"]["candidate_id"],           # 7. stable / base-like tiebreak
        )

    ranked = sorted(eligible, key=sort_key)
    champ = ranked[0]
    return {
        "champion_candidate_id": champ["candidate_id"],
        "classification": "CHAMPION_SELECTED_TRAIN",
        "reason": "passed train filters; top of cost-stress-adjusted ranking",
        "selection_uses_validation": False,
        "eligible_candidates": [ev["candidate_id"] for ev in ranked],
        "ranking": [
            {
                "candidate_id": ev["candidate_id"],
                "cost_stress_adjusted_exp": round(_cost_stress_adjusted_exp(ev), 5),
                "base_expectancy_r": ev["base"]["expectancy_r"],
                "stress_2x_expectancy_r": ev["stress_2x"]["expectancy_r"],
                "pairs_nonneg": ev["base"]["pairs_nonneg"],
                "profit_factor": ev["base"]["profit_factor"],
                "trade_count": ev["base"]["trade_count"],
            }
            for ev in ranked
        ],
        "single_pair_review_flags": spr_flags,
        "champion_parameters": champ["candidate"],
    }


def apply_train_filters(base: dict[str, Any], stress_exp: float | None) -> dict[str, Any]:
    exp = base["expectancy_r"]
    pf = base["profit_factor"]
    checks = {
        "trades_gte_100": base["trade_count"] >= TRAIN_MIN_TRADES,
        "expectancy_gte_0": exp is not None and exp >= 0,
        "pf_gte_1_03": pf is not None and pf >= TRAIN_MIN_PF,
        "pairs_nonneg_gte_3": base["pairs_nonneg"] >= TRAIN_MIN_PAIRS_NONNEG,
        "stress_2x_exp_gte_neg_0_005": stress_exp is not None and stress_exp >= TRAIN_STRESS_MIN_EXP,
        "single_pair_concentration_ok": base["top_pair_positive_r_concentration"] <= SINGLE_PAIR_CONCENTRATION_MAX,
    }
    return {
        "eligible": all(checks.values()),
        "checks": checks,
        "failed": [k for k, v in checks.items() if not v],
        "single_pair_review_flag": (
            not checks["single_pair_concentration_ok"] or not checks["pairs_nonneg_gte_3"]
        )
        and (exp is not None and exp > 0),
    }
