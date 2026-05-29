"""CAMPAIGN_026 timeframe-ladder simulator — vectorized backtest for the Donchian +
HTF confluence family across variable execution timeframes (M3 / M15 / M30).

This is an isolated research simulator. It does NOT modify the shared
``forex_bot.backtesting`` engine, the executor, or any broker code. It is the C025
M5 simulator generalized to a configurable execution timeframe and context ladder:

  * execution frame: M3, M15, or M30 (materialized M1-derived bars)
  * local setup: M15 (for M3), internal M15 (for M15), H1 (for M30) — pullback or
    compression, same logic as C025
  * trend gates: H1 and/or H4M1 per the candidate's ``trend_timeframes``
  * regime: D1AGG (native-H4-derived), not-against the breakout direction

Fills are ``next_bar_open`` only; same-bar stop/target ambiguity resolves
adverse-first; HTF/local context is the last completed bar (no lookahead); Donchian
channels use prior completed bars only (``.shift(1)``). The trade model, cost model,
and metrics are imported unchanged from the C025 simulator. No test lockbox, no
approval. See docs/research/CAMPAIGN_026_TIMEFRAME_LADDER_SPEC.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

from forex_bot.research.campaign_025_train_matrix import (
    BEAT_NULL_MARGIN,  # noqa: F401  (re-exported for runner/tests)
    C011_NULL_EXP_R,
    COST_BASE,
    COST_STRESS_2X,
    Trade,
    _htf_trend_frame,
    _merge_asof_to_m5,
    _mk_trade,
    _pip_size,
    _slope,
    aggregate_candidate_metrics,
)
from forex_bot.research.campaign_026_loader import CONTEXT_LADDER, C026Frames
from forex_bot.strategies.indicators import atr, donchian_high, donchian_low, ema

# Frozen base parameters shared by all candidates (mirror C025).
ATR_LOOKBACK = 14
LOCAL_EMA_FAST = 20
LOCAL_PULLBACK_LOOKBACK = 8
LOCAL_COMPRESSION_DONCHIAN = 12
LOCAL_COMPRESSION_ATR = 14
LOCAL_COMPRESSION_WIDTH_ATR_MAX = 3.0
H1_EMA_FAST, H1_EMA_SLOW, H1_SLOPE_BARS = 20, 50, 3
H4_EMA_FAST, H4_EMA_SLOW = 20, 50
D1_EMA_FAST, D1_EMA_SLOW, D1_SLOPE_BARS = 20, 50, 3
DONCHIAN_LENGTHS = (12, 20, 30)

# Train-only selection filters (frozen — see spec). Trade floors are timeframe-aware:
# M3 trades faster so it must clear a higher count to be credible.
TRAIN_MIN_TRADES_BY_TF = {"M3": 150, "M15": 80, "M30": 80}
TRAIN_MIN_PF = 1.03
TRAIN_MIN_PAIRS_NONNEG = 3
TRAIN_STRESS_MIN_EXP = -0.005
SINGLE_PAIR_CONCENTRATION_MAX = 0.50


@dataclass
class PairFeatures026:
    instrument: str
    execution_tf: str
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
    h4_trend: np.ndarray
    h1_standard: np.ndarray
    h1_strict: np.ndarray
    h1_available: bool
    d1_not_bearish: np.ndarray
    d1_not_bullish: np.ndarray
    local_pullback_long: np.ndarray
    local_pullback_short: np.ndarray
    local_compression: np.ndarray
    warm_mask: np.ndarray


def _local_setup_frame(frames: C026Frames) -> pd.DataFrame:
    """Pullback/compression features on the local-setup frame (M15 or H1)."""
    local = frames.local.completed_only().df
    if local.empty:
        return pd.DataFrame(columns=["time", "pull_long", "pull_short", "compression"])
    close = local["close"].astype(float)
    high = local["high"].astype(float)
    low = local["low"].astype(float)
    ema_fast = ema(close, LOCAL_EMA_FAST)
    pull_long_bar = low.to_numpy() <= ema_fast.to_numpy()
    pull_short_bar = high.to_numpy() >= ema_fast.to_numpy()
    pl = pd.Series(pull_long_bar).rolling(LOCAL_PULLBACK_LOOKBACK, min_periods=1).max().fillna(0).astype(bool)
    ps = pd.Series(pull_short_bar).rolling(LOCAL_PULLBACK_LOOKBACK, min_periods=1).max().fillna(0).astype(bool)
    dc_w = donchian_high(high, LOCAL_COMPRESSION_DONCHIAN) - donchian_low(low, LOCAL_COMPRESSION_DONCHIAN)
    a = atr(high, low, close, LOCAL_COMPRESSION_ATR)
    comp = (dc_w / a) <= LOCAL_COMPRESSION_WIDTH_ATR_MAX
    return pd.DataFrame(
        {
            "time": pd.to_datetime(local.index, utc=True),
            "pull_long": pl.to_numpy(),
            "pull_short": ps.to_numpy(),
            "compression": comp.fillna(False).to_numpy(),
        }
    )


def precompute_pair_features(frames: C026Frames) -> PairFeatures026:
    execution_tf = frames.execution_tf
    ex = frames.execution.completed_only().df
    idx = ex.index
    high = ex["high"].astype(float)
    low = ex["low"].astype(float)
    close = ex["close"].astype(float)
    open_ = ex["open"].astype(float)
    atr_ex = atr(high, low, close, ATR_LOOKBACK)
    pip = _pip_size(frames.instrument)
    if {"bid_close", "ask_close"}.issubset(ex.columns):
        spread_pips = ((ex["ask_close"].astype(float) - ex["bid_close"].astype(float)) / pip).clip(lower=0.0)
    else:
        spread_pips = pd.Series(np.full(len(ex), 1.0), index=ex.index)
    dc_high = {n: donchian_high(high, n).to_numpy() for n in DONCHIAN_LENGTHS}
    dc_low = {n: donchian_low(low, n).to_numpy() for n in DONCHIAN_LENGTHS}

    trend_set = CONTEXT_LADDER[execution_tf]["trend"]
    h1_in_trend = "H1" in trend_set

    # ---- local setup ----
    local_feat = _local_setup_frame(frames)
    a_local = _merge_asof_to_m5(idx, local_feat, ["pull_long", "pull_short", "compression"])
    local_pl = np.nan_to_num(a_local["pull_long"], nan=0.0).astype(bool)
    local_ps = np.nan_to_num(a_local["pull_short"], nan=0.0).astype(bool)
    local_comp = np.nan_to_num(a_local["compression"], nan=0.0).astype(bool)

    # ---- H1 ----
    h1 = _htf_trend_frame(frames.h1, ema_fast=H1_EMA_FAST, ema_slow=H1_EMA_SLOW)
    if not h1.empty:
        h1_slope = _slope(pd.Series(h1["ema_fast"]), H1_SLOPE_BARS)
        ef, es, cl = h1["ema_fast"], h1["ema_slow"], h1["close"]
        h1["std"] = np.where((ef > es) & (h1_slope >= 0), 1, np.where((ef < es) & (h1_slope <= 0), -1, 0))
        h1["strict"] = np.where(
            (ef > es) & (h1_slope >= 0) & (cl > es), 1,
            np.where((ef < es) & (h1_slope <= 0) & (cl < es), -1, 0),
        )

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
    a_h1 = (
        _merge_asof_to_m5(idx, h1, ["std", "strict"])
        if not h1.empty
        else {"std": np.full(len(idx), np.nan), "strict": np.full(len(idx), np.nan)}
    )
    a_d1 = (
        _merge_asof_to_m5(idx, d1, ["not_bearish", "not_bullish"])
        if not d1.empty
        else {"not_bearish": np.full(len(idx), np.nan), "not_bullish": np.full(len(idx), np.nan)}
    )

    h4_trend = np.nan_to_num(a_h4["trend"], nan=0.0).astype(int)
    h1_std = np.nan_to_num(a_h1["std"], nan=0.0).astype(int)
    h1_strict = np.nan_to_num(a_h1["strict"], nan=0.0).astype(int)
    d1_nb = np.nan_to_num(a_d1["not_bearish"], nan=0.0).astype(bool)
    d1_nbu = np.nan_to_num(a_d1["not_bullish"], nan=0.0).astype(bool)

    warm = (
        ~np.isnan(atr_ex.to_numpy())
        & ~np.isnan(dc_high[max(DONCHIAN_LENGTHS)])
        & ~np.isnan(a_h4["trend"])
        & ~np.isnan(a_d1["not_bearish"])
    )
    if h1_in_trend:
        warm = warm & ~np.isnan(a_h1["std"])

    return PairFeatures026(
        instrument=frames.instrument,
        execution_tf=execution_tf,
        index=idx,
        open=open_.to_numpy(),
        high=high.to_numpy(),
        low=low.to_numpy(),
        close=close.to_numpy(),
        atr=atr_ex.to_numpy(),
        spread_pips=spread_pips.to_numpy(),
        pip_size=pip,
        dc_high=dc_high,
        dc_low=dc_low,
        h4_trend=h4_trend,
        h1_standard=h1_std,
        h1_strict=h1_strict,
        h1_available=h1_in_trend,
        d1_not_bearish=d1_nb,
        d1_not_bullish=d1_nbu,
        local_pullback_long=local_pl,
        local_pullback_short=local_ps,
        local_compression=local_comp,
        warm_mask=warm,
    )


def _local_setup(mode: str, pull: np.ndarray, comp: np.ndarray) -> np.ndarray:
    if mode == "pullback_only":
        return pull
    if mode == "compression_only":
        return comp
    return pull | comp  # pullback_or_compression


def compute_signal_direction(feat: PairFeatures026, candidate: dict) -> np.ndarray:
    """+1 (long) / -1 (short) / 0 per execution bar for the candidate's gates."""
    n = candidate["donchian_length"]
    h1 = feat.h1_strict if candidate["context_mode"] == "strict" else feat.h1_standard
    setup_mode = candidate.get("local_setup_mode", "pullback_or_compression")
    setup_long = _local_setup(setup_mode, feat.local_pullback_long, feat.local_compression)
    setup_short = _local_setup(setup_mode, feat.local_pullback_short, feat.local_compression)
    breakout_long = feat.close > feat.dc_high[n]
    breakout_short = feat.close < feat.dc_low[n]
    long_sig = feat.warm_mask & breakout_long & (feat.h4_trend == 1) & feat.d1_not_bearish & setup_long
    short_sig = feat.warm_mask & breakout_short & (feat.h4_trend == -1) & feat.d1_not_bullish & setup_short
    if feat.h1_available:  # H1 trend gate only when H1 is in the ladder's trend set
        long_sig = long_sig & (h1 == 1)
        short_sig = short_sig & (h1 == -1)
    out = np.zeros(len(feat.close), dtype=int)
    out[long_sig] = 1
    out[short_sig] = -1
    return out


def _initial_stop_and_risk(feat: PairFeatures026, i: int, candidate: dict, side: int) -> tuple[float, float, float]:
    n = candidate["donchian_length"]
    mult = candidate["atr_stop_multiple"]
    prior_atr = feat.atr[i - 1]
    sig_close = feat.close[i]
    structure = feat.dc_low[n][i] if side == 1 else feat.dc_high[n][i]
    d_atr = mult * prior_atr
    d_struct = abs(sig_close - structure)
    stop_dist = max(d_atr, d_struct)
    stop_price = sig_close - stop_dist if side == 1 else sig_close + stop_dist
    entry_price = feat.open[i + 1]
    risk = abs(entry_price - stop_price)
    return stop_price, risk, entry_price


def _simulate_trade(feat: PairFeatures026, sig_i: int, side: int, candidate: dict) -> Trade | None:
    n_bars = len(feat.close)
    entry_i = sig_i + 1
    if entry_i >= n_bars:
        return None
    stop_price, risk, entry_price = _initial_stop_and_risk(feat, sig_i, candidate, side)
    if not np.isfinite(risk) or risk <= 0:
        return None
    exit_model = candidate["exit_model"]
    time_stop = candidate["time_stop_bars"]
    target_r = candidate["target_r_multiple"]
    be_r = candidate["breakeven_trigger_r"]
    trail_act_r = candidate["trail_activation_r"]
    trail_mult = candidate["trail_atr_multiple"]
    chan_len = candidate["channel_exit_length"]

    target_price = None
    if target_r is not None:
        target_price = entry_price + target_r * risk if side == 1 else entry_price - target_r * risk

    cur_stop = stop_price
    stop_reason = "hard_stop"
    be_done = False
    trail_on = False
    last = min(entry_i + time_stop, n_bars - 1)

    for k in range(entry_i, last + 1):
        hi, lo, cl = feat.high[k], feat.low[k], feat.close[k]
        fav_r = (hi - entry_price) / risk if side == 1 else (entry_price - lo) / risk
        stop_hit = (lo <= cur_stop) if side == 1 else (hi >= cur_stop)
        target_hit = target_price is not None and ((hi >= target_price) if side == 1 else (lo <= target_price))
        if stop_hit:
            return _mk_trade(feat, entry_i, k, side, candidate, entry_price, cur_stop, stop_price, risk, stop_reason)
        if target_hit:
            reason = "fixed_target_2r" if target_r == 2.0 else "fixed_target_3r"
            return _mk_trade(feat, entry_i, k, side, candidate, entry_price, target_price, stop_price, risk, reason)
        if exit_model == "breakeven_then_atr_trail":
            if not be_done and fav_r >= be_r:
                cur_stop = entry_price
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
        if exit_model == "donchian_channel_exit" and chan_len is not None:
            if side == 1 and np.isfinite(feat.dc_low[chan_len][k]) and cl < feat.dc_low[chan_len][k]:
                xi = min(k + 1, n_bars - 1)
                return _mk_trade(feat, entry_i, xi, side, candidate, entry_price, feat.open[xi], stop_price, risk, "donchian_channel_exit")
            if side == -1 and np.isfinite(feat.dc_high[chan_len][k]) and cl > feat.dc_high[chan_len][k]:
                xi = min(k + 1, n_bars - 1)
                return _mk_trade(feat, entry_i, xi, side, candidate, entry_price, feat.open[xi], stop_price, risk, "donchian_channel_exit")
        if k - entry_i >= time_stop:
            xi = min(k + 1, n_bars - 1)
            return _mk_trade(feat, entry_i, xi, side, candidate, entry_price, feat.open[xi], stop_price, risk, "time_stop")
    xi = last
    return _mk_trade(feat, entry_i, xi, side, candidate, entry_price, feat.close[xi], stop_price, risk, "end_of_data")


def simulate_candidate_pair(
    feat: PairFeatures026, candidate: dict, *, window_start: datetime, window_end: datetime
) -> tuple[list[Trade], dict[str, int]]:
    direction = compute_signal_direction(feat, candidate)
    times = feat.index
    in_window = np.asarray((times >= pd.Timestamp(window_start)) & (times <= pd.Timestamp(window_end)))
    sig_idx = np.flatnonzero((direction != 0) & in_window)
    funnel = {"signals_in_window": int(sig_idx.size), "entries": 0}
    trades: list[Trade] = []
    pos = 0
    for i in sig_idx:
        if i < pos:
            continue
        side = int(direction[i])
        tr = _simulate_trade(feat, int(i), side, candidate)
        if tr is None:
            continue
        trades.append(tr)
        funnel["entries"] += 1
        exit_pos = int(np.searchsorted(times, pd.Timestamp(tr.exit_time)))
        pos = max(exit_pos + 1, int(i) + 1)
    return trades, funnel


def funnel_counts(feat: PairFeatures026, candidate: dict, *, window_start: datetime, window_end: datetime) -> dict[str, int]:
    n = candidate["donchian_length"]
    times = feat.index
    w = np.asarray((times >= pd.Timestamp(window_start)) & (times <= pd.Timestamp(window_end)))
    h1 = feat.h1_strict if candidate["context_mode"] == "strict" else feat.h1_standard
    setup_mode = candidate.get("local_setup_mode", "pullback_or_compression")
    setup_long = _local_setup(setup_mode, feat.local_pullback_long, feat.local_compression)
    setup_short = _local_setup(setup_mode, feat.local_pullback_short, feat.local_compression)
    breakout = (feat.close > feat.dc_high[n]) | (feat.close < feat.dc_low[n])
    base = w & feat.warm_mask
    return {
        "exec_bars_examined": int(np.count_nonzero(base)),
        "h4_context_pass": int(np.count_nonzero(base & (feat.h4_trend != 0))),
        "h1_context_pass": int(np.count_nonzero(base & (h1 != 0))) if feat.h1_available else -1,
        "d1agg_context_pass": int(np.count_nonzero(base & (feat.d1_not_bearish | feat.d1_not_bullish))),
        "local_setup_pass": int(np.count_nonzero(base & (setup_long | setup_short))),
        "breakout_pass": int(np.count_nonzero(base & breakout)),
    }


def simulate_all_pairs(
    feats: dict[str, PairFeatures026], candidate: dict, *, window_start: datetime, window_end: datetime
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


def apply_train_filters(base: dict[str, Any], stress_exp: float | None, *, execution_tf: str) -> dict[str, Any]:
    min_trades = TRAIN_MIN_TRADES_BY_TF[execution_tf]
    exp = base["expectancy_r"]
    pf = base["profit_factor"]
    checks = {
        f"trades_gte_{min_trades}": base["trade_count"] >= min_trades,
        "expectancy_gte_0": exp is not None and exp >= 0,
        "pf_gte_1_03": pf is not None and pf >= TRAIN_MIN_PF,
        "pairs_nonneg_gte_3": base["pairs_nonneg"] >= TRAIN_MIN_PAIRS_NONNEG,
        "stress_2x_exp_gte_neg_0_005": stress_exp is not None and stress_exp >= TRAIN_STRESS_MIN_EXP,
        "single_pair_concentration_ok": base["top_pair_positive_r_concentration"] <= SINGLE_PAIR_CONCENTRATION_MAX,
    }
    return {
        "eligible": all(checks.values()),
        "min_trades_required": min_trades,
        "checks": checks,
        "failed": [k for k, v in checks.items() if not v],
        "single_pair_review_flag": (
            not checks["single_pair_concentration_ok"] or not checks["pairs_nonneg_gte_3"]
        )
        and (exp is not None and exp > 0),
    }


def evaluate_candidate(
    feats: dict[str, PairFeatures026], candidate: dict, *, window_start: datetime, window_end: datetime
) -> dict[str, Any]:
    trades_by_pair, funnel_by_pair = simulate_all_pairs(
        feats, candidate, window_start=window_start, window_end=window_end
    )
    base = aggregate_candidate_metrics(trades_by_pair, cost=COST_BASE)
    stress = aggregate_candidate_metrics(trades_by_pair, cost=COST_STRESS_2X)
    filters = apply_train_filters(base, stress["expectancy_r"], execution_tf=candidate["execution_timeframe"])
    funnel_total: dict[str, int] = {}
    for fn in funnel_by_pair.values():
        for k, v in fn.items():
            if v < 0:
                continue
            funnel_total[k] = funnel_total.get(k, 0) + v
    return {
        "candidate_id": candidate["candidate_id"],
        "execution_timeframe": candidate["execution_timeframe"],
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
    eligible = [ev for ev in evaluations if ev["filters"]["eligible"]]
    spr_flags = [ev["candidate_id"] for ev in evaluations if ev["filters"].get("single_pair_review_flag")]
    if not eligible:
        classification = "REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE"
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
        # lower spread/ATR preferred (ties); None -> large sentinel
        spread_atr = b["avg_spread_atr_ratio"]
        spread_atr = spread_atr if spread_atr is not None else 9.0
        return (
            -_cost_stress_adjusted_exp(ev),         # 1. cost-stress-adjusted expectancy
            -b["pairs_nonneg"],                      # 2. non-negative pairs
            spread_atr,                              # 3. lower spread/ATR
            b["top_pair_positive_r_concentration"],  # 4. lower concentration
            -b["trade_count"],                       # 5. adequate trade count (more first)
            -(b["profit_factor"] or 0),              # 6. PF
            ev["candidate"]["candidate_id"],          # 8. stable tiebreak
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
                "execution_timeframe": ev["execution_timeframe"],
                "cost_stress_adjusted_exp": round(_cost_stress_adjusted_exp(ev), 5),
                "base_expectancy_r": ev["base"]["expectancy_r"],
                "stress_2x_expectancy_r": ev["stress_2x"]["expectancy_r"],
                "pairs_nonneg": ev["base"]["pairs_nonneg"],
                "profit_factor": ev["base"]["profit_factor"],
                "avg_spread_atr_ratio": ev["base"]["avg_spread_atr_ratio"],
                "trade_count": ev["base"]["trade_count"],
            }
            for ev in ranked
        ],
        "single_pair_review_flags": spr_flags,
        "champion_parameters": champ["candidate"],
    }


def cost_diagnostic_for_frame(df: pd.DataFrame, pip_size: float) -> dict[str, Any]:
    """Spread/ATR cost-profile stats for one execution-frame DataFrame.

    Pure/testable. ``df`` is a completed-bar frame with columns high/low/close and
    (ideally) bid_close/ask_close. ATR(14) is in price; spread/ATR ratio compares the
    bid/ask spread (pips) to per-bar ATR (pips). Cost-drag is the round-trip cost
    (2x spread, the COST_BASE multiplier on spread plus fixed slippage) expressed in R
    for a typical stop of 1.0x ATR.
    """
    n = len(df)
    out: dict[str, Any] = {"bars": n}
    if n < ATR_LOOKBACK + 5:
        out["status"] = "INSUFFICIENT"
        return out
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)
    atr_price = atr(high, low, close, ATR_LOOKBACK)
    atr_pips = (atr_price / pip_size).to_numpy()
    if {"bid_close", "ask_close"}.issubset(df.columns):
        spread_pips = ((df["ask_close"].astype(float) - df["bid_close"].astype(float)) / pip_size).clip(lower=0.0).to_numpy()
    else:
        spread_pips = np.full(n, np.nan)
    mask = np.isfinite(atr_pips) & (atr_pips > 0) & np.isfinite(spread_pips)
    atr_pips = atr_pips[mask]
    spread_pips = spread_pips[mask]
    if atr_pips.size == 0:
        out["status"] = "INSUFFICIENT"
        return out
    ratio = spread_pips / atr_pips
    fixed = COST_BASE["fixed_slippage_pips"]
    mult = COST_BASE["spread_multiplier"]
    median_spread = float(np.median(spread_pips))
    median_atr = float(np.median(atr_pips))
    # round-trip cost in pips at median spread (entry+exit), then R for a 1.0x-ATR stop
    rt_cost_pips = 2 * (fixed + mult * median_spread)
    cost_drag_r_1atr = rt_cost_pips / median_atr if median_atr > 0 else None
    out.update(
        {
            "status": "OK",
            "median_spread_atr": round(float(np.median(ratio)), 4),
            "mean_spread_atr": round(float(np.mean(ratio)), 4),
            "p75_spread_atr": round(float(np.percentile(ratio, 75)), 4),
            "p90_spread_atr": round(float(np.percentile(ratio, 90)), 4),
            "median_atr_pips": round(median_atr, 3),
            "median_spread_pips": round(median_spread, 4),
            "roundtrip_cost_pips_at_median": round(rt_cost_pips, 4),
            "cost_drag_r_per_1atr_stop": round(cost_drag_r_1atr, 4) if cost_drag_r_1atr is not None else None,
            "min_target_r_to_overcome_cost": round(cost_drag_r_1atr, 4) if cost_drag_r_1atr is not None else None,
        }
    )
    return out


def load_features_for_window(
    store: Any,
    pairs: list[str],
    execution_tf: str,
    *,
    window_start: datetime,
    window_end: datetime,
    warmup_days: int = 60,
) -> dict[str, PairFeatures026]:
    """Load each pair once (with a warmup buffer) and precompute features."""
    from forex_bot.research.campaign_026_loader import load_c026_frames

    load_from = window_start - timedelta(days=warmup_days)
    feats: dict[str, PairFeatures026] = {}
    for pair in pairs:
        frames = load_c026_frames(store, pair, execution_tf, from_dt=load_from, to_dt=window_end)
        feats[pair] = precompute_pair_features(frames)
    return feats


__all__ = [
    "C011_NULL_EXP_R",
    "DONCHIAN_LENGTHS",
    "TRAIN_MIN_TRADES_BY_TF",
    "PairFeatures026",
    "compute_signal_direction",
    "evaluate_candidate",
    "load_features_for_window",
    "precompute_pair_features",
    "rank_and_select",
    "simulate_candidate_pair",
]
