"""Oscillator divergence detection — filter/exit helper only."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from research.confluence.models import DivergenceFlag

DivergenceState = Literal["none", "bullish", "bearish", "conflicting"]


@dataclass(frozen=True)
class DivergenceResult:
    flag: DivergenceFlag
    price_pivot: str | None = None
    oscillator_pivot: str | None = None


def _last_two_pivots(series: pd.Series, *, kind: str) -> tuple[float, float] | None:
    """Return last two pivot values for lower_low / higher_high detection."""
    vals = series.dropna()
    if len(vals) < 10:
        return None
    window = vals.iloc[-20:]
    if kind == "low":
        idx = window.nsmallest(2).index
    else:
        idx = window.nlargest(2).index
    if len(idx) < 2:
        return None
    ordered = window.loc[sorted(idx)]
    return float(ordered.iloc[0]), float(ordered.iloc[1])


def detect_divergence(
    close: pd.Series,
    oscillator: pd.Series,
) -> DivergenceResult:
    """Detect bullish/bearish divergence on last ~20 bars."""
    price_lows = _last_two_pivots(close, kind="low")
    osc_lows = _last_two_pivots(oscillator, kind="low")
    price_highs = _last_two_pivots(close, kind="high")
    osc_highs = _last_two_pivots(oscillator, kind="high")

    bullish = (
        price_lows is not None
        and osc_lows is not None
        and price_lows[1] < price_lows[0]
        and osc_lows[1] > osc_lows[0]
    )
    bearish = (
        price_highs is not None
        and osc_highs is not None
        and price_highs[1] > price_highs[0]
        and osc_highs[1] < osc_highs[0]
    )
    if bullish and bearish:
        return DivergenceResult(flag="conflicting")
    if bullish:
        return DivergenceResult(flag="bullish", price_pivot="lower_low", oscillator_pivot="higher_low")
    if bearish:
        return DivergenceResult(flag="bearish", price_pivot="higher_high", oscillator_pivot="lower_high")
    return DivergenceResult(flag="none")
