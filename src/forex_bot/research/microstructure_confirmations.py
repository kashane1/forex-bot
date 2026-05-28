"""Read-only M15 microstructure-confirmation detectors (USD_JPY diagnostic).

These are **diagnostic detectors, not a strategy**. They never place a trade,
change a verdict, tune a parameter, or approve anything. Given an M15 OHLC window
and an evaluation index ``i`` (the C022 *decision bar* = the completed M15 bar that
produced the signal, one bar before the ``next_bar_open`` fill), each detector
reports whether a stronger microstructure-confirmation pattern was present, as a
boolean ``present`` plus a continuous ``score`` (the separation analysis uses the
continuous score's AUC; the boolean uses a fixed, *conventional* cut that is
documented as **not tuned**).

Lookahead policy — explicit per detector via ``uses_post_decision``:
  * **Live** detectors read only bars with index ``<= i`` (decision bar and earlier).
    They could in principle gate a live entry.
  * **Post-decision** detectors (retest-hold, failed-reclaim/trap) inspect bars
    *after* the decision bar (``i+1 .. i+horizon`` — i.e. post-entry under
    next-bar-open). They are flagged ``uses_post_decision=True`` and are
    **diagnostic-only**: they describe what happened after entry and cannot be used
    as a live entry feature.

Directional features are trend-aligned by ``sign`` (+1 long, −1 short) so long and
short trades are comparable; distances are normalized by same-bar ATR.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from forex_bot.strategies.indicators import atr as atr_indicator
from forex_bot.strategies.indicators import ema as ema_indicator

__all__ = [
    "LIVE_DETECTORS",
    "POST_DECISION_DETECTORS",
    "DetectorResult",
    "MicrostructureContext",
    "MicrostructureParams",
    "build_context",
    "detect_all",
    "failed_reclaim_or_trap",
    "liquidity_sweep_plus_displacement",
    "range_expansion_after_compression",
    "reclaim_distance_atr",
    "reclaim_plus_impulse",
    "reclaim_plus_micro_swing_break",
    "reclaim_plus_retest_hold",
    "session_bucket",
    "volatility_context",
]


@dataclass(frozen=True)
class MicrostructureParams:
    """Detector lengths and *conventional* (non-tuned) boolean cuts.

    The numeric cuts (``impulse_atr_mult`` etc.) exist only to derive a descriptive
    boolean; the diagnostic's separation scoring uses the continuous ``score`` and
    selects no threshold as a parameter.
    """

    ema_len: int = 20
    atr_len: int = 14
    swing_lookback: int = 6
    sweep_lookback: int = 6
    compression_lookback: int = 6
    compression_baseline: int = 20
    retest_horizon: int = 4
    trap_horizon: int = 4
    impulse_atr_mult: float = 1.0
    expansion_mult: float = 1.5
    retest_tol_atr: float = 0.25


@dataclass(frozen=True)
class DetectorResult:
    name: str
    available: bool
    present: bool | None
    score: float | None
    uses_post_decision: bool
    detail: dict = field(default_factory=dict)


@dataclass(frozen=True)
class MicrostructureContext:
    """Precomputed causal arrays for one instrument/window."""

    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    ema: np.ndarray
    atr: np.ndarray

    def __len__(self) -> int:
        return int(self.open.shape[0])


# Detector classification for the analysis step.
LIVE_DETECTORS = (
    "reclaim_plus_impulse",
    "reclaim_plus_micro_swing_break",
    "liquidity_sweep_plus_displacement",
    "range_expansion_after_compression",
)
POST_DECISION_DETECTORS = (
    "reclaim_plus_retest_hold",
    "failed_reclaim_or_trap",
)


def _sign(side: str | int | float) -> int:
    if isinstance(side, str):
        return 1 if side.strip().lower() in {"long", "buy", "b", "1"} else -1
    return 1 if float(side) >= 0 else -1


def _finite(x: object) -> float | None:
    try:
        v = float(x)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def build_context(
    open_: object,
    high: object,
    low: object,
    close: object,
    params: MicrostructureParams = MicrostructureParams(),
) -> MicrostructureContext:
    """Build a context with causal EMA(ema_len) and ATR(atr_len) over the window.

    EMA/ATR are causal (computed left-to-right); indexing the array at ``i`` uses
    only bars ``<= i`` for the live detectors. Inputs are array-likes of equal length.
    """
    o = np.asarray(open_, dtype=float)
    h = np.asarray(high, dtype=float)
    low_arr = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    if not (len(o) == len(h) == len(low_arr) == len(c)):
        raise ValueError("OHLC arrays must be equal length")
    cs = pd.Series(c)
    ema = ema_indicator(cs, params.ema_len).to_numpy()
    atr = atr_indicator(pd.Series(h), pd.Series(low_arr), cs, params.atr_len).to_numpy()
    return MicrostructureContext(open=o, high=h, low=low_arr, close=c, ema=ema, atr=atr)


def _at(arr: np.ndarray, i: int) -> float | None:
    if i < 0 or i >= arr.shape[0]:
        return None
    return _finite(arr[i])


# --------------------------------------------------------------------------
# Live detectors (lookback only; index <= i)
# --------------------------------------------------------------------------


def reclaim_distance_atr(
    ctx: MicrostructureContext, i: int, side, params: MicrostructureParams = MicrostructureParams()
) -> float | None:
    """The C022 baseline trigger: trend-signed close-vs-EMA20 distance in ATR units."""
    sign = _sign(side)
    c, e, a = _at(ctx.close, i), _at(ctx.ema, i), _at(ctx.atr, i)
    if c is None or e is None or a is None or a == 0:
        return None
    return sign * (c - e) / a


def reclaim_plus_impulse(
    ctx: MicrostructureContext, i: int, side, params: MicrostructureParams = MicrostructureParams()
) -> DetectorResult:
    """Decision bar is an impulse candle: trend-direction body large vs ATR."""
    sign = _sign(side)
    c, o, a = _at(ctx.close, i), _at(ctx.open, i), _at(ctx.atr, i)
    if c is None or o is None or a is None or a == 0:
        return DetectorResult("reclaim_plus_impulse", False, None, None, False)
    score = sign * (c - o) / a
    return DetectorResult(
        "reclaim_plus_impulse", True, bool(score >= params.impulse_atr_mult),
        round(score, 6), False, {"body_atr": round(score, 6)},
    )


def reclaim_plus_micro_swing_break(
    ctx: MicrostructureContext, i: int, side, params: MicrostructureParams = MicrostructureParams()
) -> DetectorResult:
    """Decision-bar close breaks the prior N-bar local extreme in trade direction."""
    sign = _sign(side)
    n = params.swing_lookback
    c, a = _at(ctx.close, i), _at(ctx.atr, i)
    if c is None or a is None or a == 0 or i - n < 0:
        return DetectorResult("reclaim_plus_micro_swing_break", False, None, None, False)
    if sign == 1:
        prior_extreme = float(np.max(ctx.high[i - n:i]))
        score = (c - prior_extreme) / a
    else:
        prior_extreme = float(np.min(ctx.low[i - n:i]))
        score = (prior_extreme - c) / a
    return DetectorResult(
        "reclaim_plus_micro_swing_break", True, bool(score > 0), round(score, 6), False,
        {"prior_extreme": round(prior_extreme, 6)},
    )


def liquidity_sweep_plus_displacement(
    ctx: MicrostructureContext, i: int, side, params: MicrostructureParams = MicrostructureParams()
) -> DetectorResult:
    """A recent opposite-side liquidity sweep followed by trend-direction displacement.

    Long: the lowest low in the last ``L+1`` bars was made *before* the decision bar
    (a sell-side stop-run), and the decision bar closes back above that sweep bar's
    high with a positive body — displacement up off swept liquidity. Short symmetric.
    Lookback only (indices ``i-L .. i``).
    """
    sign = _sign(side)
    lb = params.sweep_lookback
    c, o, a = _at(ctx.close, i), _at(ctx.open, i), _at(ctx.atr, i)
    if c is None or o is None or a is None or a == 0 or i - lb < 0:
        return DetectorResult("liquidity_sweep_plus_displacement", False, None, None, False)
    lo = i - lb
    if sign == 1:
        seg = ctx.low[lo:i + 1]
        rel = int(np.argmin(seg))
        sweep_idx = lo + rel
        swept_before = sweep_idx < i
        recovered = c > _finite(ctx.high[sweep_idx])
        directional = (c - o) > 0
        present = bool(swept_before and recovered and directional)
        score = (c - float(ctx.low[sweep_idx])) / a if present else 0.0
    else:
        seg = ctx.high[lo:i + 1]
        rel = int(np.argmax(seg))
        sweep_idx = lo + rel
        swept_before = sweep_idx < i
        recovered = c < _finite(ctx.low[sweep_idx])
        directional = (c - o) < 0
        present = bool(swept_before and recovered and directional)
        score = (float(ctx.high[sweep_idx]) - c) / a if present else 0.0
    return DetectorResult(
        "liquidity_sweep_plus_displacement", True, present, round(float(score), 6), False,
        {"sweep_bars_back": int(i - sweep_idx)},
    )


def range_expansion_after_compression(
    ctx: MicrostructureContext, i: int, side, params: MicrostructureParams = MicrostructureParams()
) -> DetectorResult:
    """Recent range compression then a trend-direction expansion bar at the decision bar."""
    sign = _sign(side)
    n, b = params.compression_lookback, params.compression_baseline
    c, o, a = _at(ctx.close, i), _at(ctx.open, i), _at(ctx.atr, i)
    if c is None or o is None or a is None or i - b < 0:
        return DetectorResult("range_expansion_after_compression", False, None, None, False)
    rng = ctx.high - ctx.low
    recent = float(np.mean(rng[i - n:i]))  # bars before decision bar
    baseline = float(np.mean(rng[i - b:i]))
    if not math.isfinite(recent) or not math.isfinite(baseline) or recent <= 0:
        return DetectorResult("range_expansion_after_compression", False, None, None, False)
    compressed = recent < baseline
    expansion_ratio = float(rng[i]) / recent
    directional = sign * (c - o) > 0
    present = bool(compressed and expansion_ratio >= params.expansion_mult and directional)
    return DetectorResult(
        "range_expansion_after_compression", True, present, round(expansion_ratio, 6), False,
        {"compressed": compressed, "recent_mean_range": round(recent, 6)},
    )


# --------------------------------------------------------------------------
# Post-decision detectors (inspect bars i+1 .. i+horizon) — diagnostic-only
# --------------------------------------------------------------------------


def reclaim_plus_retest_hold(
    ctx: MicrostructureContext, i: int, side, params: MicrostructureParams = MicrostructureParams()
) -> DetectorResult:
    """POST-DECISION: after entry, price retests the reclaimed EMA and *holds*.

    Long: some bar in ``i+1 .. i+M`` dips to within ``retest_tol_atr`` of the EMA
    (low <= ema + tol*ATR) yet closes back above the EMA — a held retest. Short
    symmetric. Uses post-entry bars → not a live entry feature.
    """
    sign = _sign(side)
    m, tol = params.retest_horizon, params.retest_tol_atr
    n = len(ctx)
    if i + 1 >= n:
        return DetectorResult("reclaim_plus_retest_hold", False, None, None, True)
    holds = 0
    for k in range(i + 1, min(i + m, n - 1) + 1):
        e, a = _at(ctx.ema, k), _at(ctx.atr, k)
        c = _at(ctx.close, k)
        if e is None or a is None or c is None:
            continue
        if sign == 1:
            retested = float(ctx.low[k]) <= e + tol * a
            held = c >= e
        else:
            retested = float(ctx.high[k]) >= e - tol * a
            held = c <= e
        if retested and held:
            holds += 1
    return DetectorResult(
        "reclaim_plus_retest_hold", True, bool(holds > 0), float(holds), True,
        {"hold_count": holds, "horizon": m},
    )


def failed_reclaim_or_trap(
    ctx: MicrostructureContext, i: int, side, params: MicrostructureParams = MicrostructureParams()
) -> DetectorResult:
    """POST-DECISION: after entry, the reclaim fails — close crosses back through the
    EMA against the trade direction within ``trap_horizon`` bars (a trap to avoid).

    ``present=True`` means the reclaim failed. ``score`` = bars until first failure
    (smaller = worse / earlier trap); ``None`` score when no trap. Uses post-entry bars.
    """
    sign = _sign(side)
    k_h = params.trap_horizon
    n = len(ctx)
    if i + 1 >= n:
        return DetectorResult("failed_reclaim_or_trap", False, None, None, True)
    for k in range(i + 1, min(i + k_h, n - 1) + 1):
        e, c = _at(ctx.ema, k), _at(ctx.close, k)
        if e is None or c is None:
            continue
        trapped = (c < e) if sign == 1 else (c > e)
        if trapped:
            return DetectorResult(
                "failed_reclaim_or_trap", True, True, float(k - i), True,
                {"bars_until_trap": int(k - i), "horizon": k_h},
            )
    return DetectorResult(
        "failed_reclaim_or_trap", True, False, None, True, {"horizon": k_h},
    )


# --------------------------------------------------------------------------
# Context helpers (categories 7 & 8)
# --------------------------------------------------------------------------


def session_bucket(hour: int) -> str:
    """USD_JPY session bucket by UTC hour (Tokyo / London / overlap / NY / rollover)."""
    h = int(hour) % 24
    if h >= 21:
        return "rollover_late"
    if h < 7:
        return "tokyo"
    if 7 <= h < 12:
        return "london"
    if 12 <= h < 16:
        return "london_ny_overlap"
    return "new_york"  # 16..21


def volatility_context(
    ctx: MicrostructureContext, i: int, lookback: int = 96
) -> dict[str, float | None]:
    """ATR-at-decision and its percentile rank within the trailing ``lookback`` bars.

    Percentile is causal (uses ATR values at indices ``<= i`` only). Returns ``None``
    fields when ATR is unavailable.
    """
    a = _at(ctx.atr, i)
    if a is None:
        return {"atr_at_entry": None, "atr_percentile": None}
    lo = max(0, i - lookback + 1)
    window = ctx.atr[lo:i + 1]
    window = window[np.isfinite(window)]
    pct = float((window <= a).mean()) if window.size else None
    return {"atr_at_entry": round(a, 6), "atr_percentile": None if pct is None else round(pct, 4)}


def detect_all(
    ctx: MicrostructureContext, i: int, side, params: MicrostructureParams = MicrostructureParams()
) -> dict[str, DetectorResult]:
    """Run every bar-pattern detector at index ``i`` for one trade."""
    fns = (
        reclaim_plus_impulse,
        reclaim_plus_micro_swing_break,
        liquidity_sweep_plus_displacement,
        range_expansion_after_compression,
        reclaim_plus_retest_hold,
        failed_reclaim_or_trap,
    )
    return {fn.__name__: fn(ctx, i, side, params) for fn in fns}
