"""Per-trade MFE/MAE reconstruction from post-entry candles (read-only research).

Given a trade (side, entry price, initial stop) and the sequence of candles that
occurred *after entry and up to exit*, compute the maximum favorable excursion
(MFE) and maximum adverse excursion (MAE) in **R units** (R = the entry→stop
risk distance), plus whether the trade reached favorable R thresholds before the
stop was touched.

This module computes geometry only. It never reruns a strategy, never changes a
verdict, never tunes anything. Whether real candles are available to feed it is a
data-availability question handled by the reconstruction script (and is currently
BLOCKED_LOCAL_DATA in checkouts without the materialized M15 store).

Conventions:
  * R is positive for favorable moves, negative for adverse.
  * The stop sits at exactly −``stop_r`` R by construction (risk = |entry−stop|),
    so a hard-stop touch == adverse excursion reaching −``stop_r``.
  * **Intrabar assumption:** within a single bar both the high and the low are
    visited; we cannot know the order. The default ``intrabar="adverse_first"``
    is conservative — if a bar touches both the stop and a favorable threshold,
    the stop is assumed to have happened first. This biases "reached +X before
    stop" *downward* (never overstates a hypothetical edge).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

__all__ = ["Bar", "MfeMaeResult", "compute_mfe_mae"]

_LONG = {"long", "buy", "b", "1"}
_SHORT = {"short", "sell", "s", "-1"}

FAVORABLE_THRESHOLDS = (0.25, 0.5, 1.0)
ADVERSE_THRESHOLDS = (0.5, 0.9)


@dataclass(frozen=True)
class Bar:
    """A single post-entry candle. ``high``/``low`` are the prices used for
    excursion; supply bid/ask-adjusted values upstream if desired."""

    timestamp: datetime
    high: float
    low: float


@dataclass(frozen=True)
class MfeMaeResult:
    status: str  # "OK" | "NO_BARS" | "ZERO_RISK" | "BAD_SIDE"
    bars_used: int
    risk_per_unit: float | None
    mfe_r: float | None
    mae_r: float | None
    reached_plus_0_25r: bool
    reached_plus_0_5r: bool
    reached_plus_1_0r: bool
    touched_minus_0_5r: bool
    touched_minus_0_9r: bool
    stop_hit: bool
    stop_hit_bar_index: int | None
    first_plus_0_5r_bar_index: int | None
    reached_plus_0_25r_before_stop: bool
    reached_plus_0_5r_before_stop: bool
    reached_plus_1_0r_before_stop: bool


def _normalize_side(side: str) -> int | None:
    s = side.strip().lower()
    if s in _LONG:
        return 1
    if s in _SHORT:
        return -1
    return None


def _empty(status: str, risk: float | None = None) -> MfeMaeResult:
    return MfeMaeResult(
        status=status,
        bars_used=0,
        risk_per_unit=risk,
        mfe_r=None,
        mae_r=None,
        reached_plus_0_25r=False,
        reached_plus_0_5r=False,
        reached_plus_1_0r=False,
        touched_minus_0_5r=False,
        touched_minus_0_9r=False,
        stop_hit=False,
        stop_hit_bar_index=None,
        first_plus_0_5r_bar_index=None,
        reached_plus_0_25r_before_stop=False,
        reached_plus_0_5r_before_stop=False,
        reached_plus_1_0r_before_stop=False,
    )


def compute_mfe_mae(
    *,
    side: str,
    entry_price: float,
    initial_stop_price: float,
    bars: list[Bar],
    entry_time: datetime | None = None,
    exit_time: datetime | None = None,
    stop_r: float = 1.0,
    intrabar: str = "adverse_first",
) -> MfeMaeResult:
    """Compute MFE/MAE (R units) and threshold ordering for one trade.

    ``bars`` must be the candles *after* entry. ``entry_time``/``exit_time``, if
    given, defensively clip the window: bars at/before entry or strictly after
    exit are dropped (no lookahead past the realized exit).
    """
    sign = _normalize_side(side)
    if sign is None:
        return _empty("BAD_SIDE")

    risk = abs(entry_price - initial_stop_price)
    if risk == 0:
        return _empty("ZERO_RISK", risk=0.0)

    # Defensive windowing: only bars strictly after entry and up to exit.
    window = []
    for b in bars:
        if entry_time is not None and b.timestamp <= entry_time:
            continue
        if exit_time is not None and b.timestamp > exit_time:
            continue
        window.append(b)

    if not window:
        return _empty("NO_BARS", risk=risk)

    favorable_first = intrabar == "favorable_first"

    mfe_r = float("-inf")
    mae_r = float("inf")
    stop_idx: int | None = None
    first_thr_idx: dict[float, int | None] = {t: None for t in FAVORABLE_THRESHOLDS}

    for i, b in enumerate(window):
        if sign == 1:  # long
            fav = (b.high - entry_price) / risk
            adv = (b.low - entry_price) / risk
        else:  # short
            fav = (entry_price - b.low) / risk
            adv = (entry_price - b.high) / risk

        mfe_r = max(mfe_r, fav)
        mae_r = min(mae_r, adv)

        bar_stops = adv <= -stop_r
        if bar_stops and stop_idx is None:
            stop_idx = i

        for t in FAVORABLE_THRESHOLDS:
            if first_thr_idx[t] is None and fav >= t:
                first_thr_idx[t] = i

    def reached_before_stop(t: float) -> bool:
        ti = first_thr_idx[t]
        if ti is None:
            return False
        if stop_idx is None:
            return True
        if ti < stop_idx:
            return True
        if ti == stop_idx:
            # same bar touched both — order depends on intrabar assumption
            return favorable_first
        return False

    return MfeMaeResult(
        status="OK",
        bars_used=len(window),
        risk_per_unit=risk,
        mfe_r=round(mfe_r, 6),
        mae_r=round(mae_r, 6),
        reached_plus_0_25r=mfe_r >= 0.25,
        reached_plus_0_5r=mfe_r >= 0.5,
        reached_plus_1_0r=mfe_r >= 1.0,
        touched_minus_0_5r=mae_r <= -0.5,
        touched_minus_0_9r=mae_r <= -0.9,
        stop_hit=stop_idx is not None,
        stop_hit_bar_index=stop_idx,
        first_plus_0_5r_bar_index=first_thr_idx[0.5],
        reached_plus_0_25r_before_stop=reached_before_stop(0.25),
        reached_plus_0_5r_before_stop=reached_before_stop(0.5),
        reached_plus_1_0r_before_stop=reached_before_stop(1.0),
    )
