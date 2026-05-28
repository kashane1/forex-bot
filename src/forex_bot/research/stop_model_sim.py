"""Diagnostic stop-model simulation on FIXED entries (research-only).

Given a trade's entry/side/risk and the fixed-horizon post-entry candle path
(entry → entry + max_bars), simulate the outcome R under alternative exit rules:
candidate hard-stop distances and time-to-invalidation early exits. Entries are
**never** changed — only the exit rule — so this is an exit *sensitivity*
diagnostic, not a re-tuning of the strategy and not an edge.

R convention: R = entry→initial-stop distance (= the campaign's 2×ATR). A
candidate stop at k×ATR therefore sits at (k/2)·R; e.g. 1.5×ATR → 0.75R,
3.0×ATR → 1.5R. Outcomes are price-based and pair-agnostic.

Intrabar ties resolve **adverse-first** (a bar that touches both the candidate
stop and a favorable level is assumed to stop first) — conservative: never
overstates a hypothetical improvement.

Caveats (must accompany any reported aggregate): mid OHLC only, no spread/
slippage, no next-bar-open fill timing — so a simulated baseline approximates,
not reproduces, the realized fill-model expectancy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

__all__ = ["PathBar", "StopOutcome", "simulate_fixed_stop", "simulate_time_invalidation"]

_LONG = {"long", "buy"}
_SHORT = {"short", "sell"}


@dataclass(frozen=True)
class PathBar:
    timestamp: datetime
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class StopOutcome:
    status: str  # "OK" | "NO_BARS" | "ZERO_RISK" | "BAD_SIDE"
    outcome_r: float | None
    exit_kind: str | None  # "stop" | "time" | "invalidation"
    exit_bar: int | None


def _dir(side: str) -> int | None:
    s = side.strip().lower()
    if s in _LONG:
        return 1
    if s in _SHORT:
        return -1
    return None


def _fav_adv(sign: int, entry: float, risk: float, bar: PathBar) -> tuple[float, float]:
    if sign == 1:
        return (bar.high - entry) / risk, (bar.low - entry) / risk
    return (entry - bar.low) / risk, (entry - bar.high) / risk


def _close_r(sign: int, entry: float, risk: float, bar: PathBar) -> float:
    return (bar.close - entry) / risk if sign == 1 else (entry - bar.close) / risk


def _prep(side: str, entry: float, stop: float, bars: list[PathBar], max_bars: int):
    sign = _dir(side)
    if sign is None:
        return None, None, StopOutcome("BAD_SIDE", None, None, None)
    risk = abs(entry - stop)
    if risk == 0:
        return None, None, StopOutcome("ZERO_RISK", None, None, None)
    window = bars[:max_bars]
    if not window:
        return None, None, StopOutcome("NO_BARS", None, None, None)
    return sign, risk, window


def simulate_fixed_stop(
    *,
    side: str,
    entry_price: float,
    initial_stop_price: float,
    bars: list[PathBar],
    stop_r: float,
    max_bars: int = 32,
) -> StopOutcome:
    """Outcome R if the hard stop sat at ``-stop_r`` R; else exit at the time-stop
    (close of the last in-horizon bar). ``bars`` must already be the post-entry
    path in order."""
    sign, risk, prepared = _prep(side, entry_price, initial_stop_price, bars, max_bars)
    if isinstance(prepared, StopOutcome):
        return prepared
    window = prepared
    for i, b in enumerate(window):
        _fav, adv = _fav_adv(sign, entry_price, risk, b)
        if adv <= -stop_r:
            return StopOutcome("OK", -stop_r, "stop", i)
    return StopOutcome("OK", _close_r(sign, entry_price, risk, window[-1]), "time", len(window) - 1)


def simulate_time_invalidation(
    *,
    side: str,
    entry_price: float,
    initial_stop_price: float,
    bars: list[PathBar],
    threshold_r: float,
    n_bars: int,
    baseline_stop_r: float = 1.0,
    max_bars: int = 32,
) -> StopOutcome:
    """Early-invalidation rule: if the trade has not reached ``+threshold_r`` MFE
    by bar ``n_bars``, exit at that bar's close. The baseline stop (``-baseline_stop_r``)
    still applies throughout; the time-stop applies at ``max_bars``."""
    sign, risk, prepared = _prep(side, entry_price, initial_stop_price, bars, max_bars)
    if isinstance(prepared, StopOutcome):
        return prepared
    window = prepared
    mfe = float("-inf")
    for i, b in enumerate(window):
        fav, adv = _fav_adv(sign, entry_price, risk, b)
        if adv <= -baseline_stop_r:
            return StopOutcome("OK", -baseline_stop_r, "stop", i)
        mfe = max(mfe, fav)
        if i + 1 == n_bars:
            if mfe < threshold_r:
                return StopOutcome("OK", _close_r(sign, entry_price, risk, b), "invalidation", i)
    return StopOutcome("OK", _close_r(sign, entry_price, risk, window[-1]), "time", len(window) - 1)
