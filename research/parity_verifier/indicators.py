"""Independent EMA / ATR / Donchian implementations.

These are written from the canonical mathematical definitions, not
copied from ``src/forex_bot/strategies/indicators.py``. The mapping
spec (``docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md`` §3) pins the
exact behavior:

- EMA: recursive with ``alpha = 2/(L+1)``, seeded at the first sample,
  emitting ``NaN`` until ``L`` samples have been seen.
- ATR: Wilder's smoothing with ``alpha = 1/L``; the true range uses
  the previous bar's close.
- Donchian: the high / low of the *prior* ``L`` bars, **excluding the
  current bar** — this is the spec's no-look-ahead convention.

All functions are pure: they return new lists / pandas Series; they
do not mutate inputs and do not depend on global state.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import nan


def ema(values: Sequence[float], length: int) -> list[float]:
    """Exponential moving average.

    Returns a list the same length as ``values``. Entries before the
    ``length``-th sample are ``NaN``; from that point on the value is
    the EMA seeded at ``values[length-1]`` (the standard pandas
    ``ewm(span, adjust=False, min_periods=length)`` behavior, re-derived
    here without pandas to keep the test fixtures self-contained).
    """

    if length <= 0:
        raise ValueError("ema length must be > 0")
    out: list[float] = [nan] * len(values)
    if len(values) < length:
        return out
    alpha = 2.0 / (length + 1.0)
    current = float(values[length - 1])
    out[length - 1] = current
    for i in range(length, len(values)):
        current = alpha * float(values[i]) + (1.0 - alpha) * current
        out[i] = current
    return out


def atr(
    high: Sequence[float],
    low: Sequence[float],
    close: Sequence[float],
    length: int = 14,
) -> list[float]:
    """Wilder's ATR.

    True range at bar ``i``:
    ``TR_i = max(high_i - low_i, |high_i - close_{i-1}|, |low_i - close_{i-1}|)``.
    The first sample (``i=0``) has no previous close, so ``TR_0 = high_0 - low_0``.

    ATR is the Wilder smoothing of TR with alpha = 1/length, seeded at
    the simple average of the first ``length`` TR values. Outputs are
    ``NaN`` until ``length`` TRs are available.
    """

    if length <= 0:
        raise ValueError("atr length must be > 0")
    n = len(high)
    if not (n == len(low) == len(close)):
        raise ValueError("high / low / close must have the same length")
    tr: list[float] = [nan] * n
    for i in range(n):
        if i == 0:
            tr[i] = float(high[i]) - float(low[i])
        else:
            prev_close = float(close[i - 1])
            tr[i] = max(
                float(high[i]) - float(low[i]),
                abs(float(high[i]) - prev_close),
                abs(float(low[i]) - prev_close),
            )
    out: list[float] = [nan] * n
    if n < length:
        return out
    seed = sum(tr[:length]) / length
    out[length - 1] = seed
    current = seed
    alpha = 1.0 / length
    for i in range(length, n):
        current = alpha * tr[i] + (1.0 - alpha) * current
        out[i] = current
    return out


def donchian_high(high: Sequence[float], length: int) -> list[float]:
    """Highest high of the *prior* ``length`` bars (excluding the
    current bar). The mapping spec calls out that this differs from
    Lean's built-in ``DonchianChannel``, which includes the forming
    bar."""

    if length <= 0:
        raise ValueError("donchian length must be > 0")
    n = len(high)
    out: list[float] = [nan] * n
    for i in range(n):
        if i < length:
            continue
        window = high[i - length : i]
        out[i] = max(float(x) for x in window)
    return out


def donchian_low(low: Sequence[float], length: int) -> list[float]:
    """Lowest low of the *prior* ``length`` bars (excluding the
    current bar)."""

    if length <= 0:
        raise ValueError("donchian length must be > 0")
    n = len(low)
    out: list[float] = [nan] * n
    for i in range(n):
        if i < length:
            continue
        window = low[i - length : i]
        out[i] = min(float(x) for x in window)
    return out
