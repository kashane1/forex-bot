"""Forward-return windows for the edge-discovery lab.

Given a candle frame and a set of signal timestamps (e.g. event
release times, condition-met bar closes), compute the per-signal
forward return ``ln(close_{t+w} / close_{t})`` over a fixed window of
``w`` bars, signed by ``side`` (LONG = +1, SHORT = -1, NEUTRAL = +1
treated as long, used only when the side itself is the unknown).

Entry reference is the **close of the signal bar** — never the open of
that same bar — to mirror the existing backtester's default
``signal_bar_close`` fill model and prevent subtle look-ahead. A study
that wants a "next-bar open" entry should advance the signal time by
one bar before calling this.

Returns are reported in raw log-return units; downstream code converts
to R or applies cost overlays.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import pandas as pd


class Side(Enum):
    LONG = 1
    SHORT = -1
    NEUTRAL = 1  # use when the side itself is what's being measured


@dataclass(frozen=True)
class ForwardReturns:
    """Per-signal forward returns.

    ``per_signal`` columns:
      - ``signal_time`` — UTC timestamp of the signal bar close
      - ``entry_idx`` — integer index of the entry bar (signal bar)
      - ``exit_idx`` — integer index of the exit bar (signal + window)
      - ``entry_price`` — mid close at entry
      - ``exit_price`` — mid close at exit
      - ``log_return`` — ln(exit / entry), signed by side
      - ``bars_held`` — fixed at ``window_bars`` (kept for cost calcs)
      - ``side`` — +1 for LONG, -1 for SHORT
      - ``label`` — optional caller-supplied label (e.g. event class)

    Trailing signals that don't have ``window_bars`` of forward data
    are dropped and reported in ``dropped_trailing``.
    """

    per_signal: pd.DataFrame
    window_bars: int
    side: Side
    n_signals: int
    dropped_trailing: int
    dropped_missing: int = 0
    extras: dict[str, object] = field(default_factory=dict)


def _bar_index_of(frame_times: pd.Index, when: pd.Timestamp) -> int | None:
    """Index of the bar whose close timestamp is ``when``, or the next
    bar after ``when`` if there's no exact match. Returns None if
    ``when`` is past the end."""
    pos = frame_times.searchsorted(when, side="left")
    if pos >= len(frame_times):
        return None
    return int(pos)


def compute_forward_returns(
    frame: pd.DataFrame,
    signal_times: Iterable[pd.Timestamp],
    *,
    window_bars: int,
    side: Side = Side.LONG,
    labels: Iterable[object] | None = None,
) -> ForwardReturns:
    """Compute signed log-returns over a fixed forward window.

    The frame is the ``CandleSample.frame`` produced by ``load_candles_csv``
    — UTC-indexed, with a ``close`` column.

    Each signal timestamp is mapped to the bar whose close is at or
    after the signal time (so a signal released *during* a bar is paired
    with that bar's close, not a still-incomplete bar — caller is
    responsible for passing already-closed timestamps in if they don't
    want this behavior).
    """
    if "close" not in frame.columns:
        raise ValueError("frame must have a 'close' column — use load_candles_csv()")
    if window_bars < 1:
        raise ValueError(f"window_bars must be >= 1, got {window_bars}")

    times = frame.index
    closes = frame["close"].to_numpy(dtype=float)
    n = len(closes)

    sig_list = list(signal_times)
    label_list = list(labels) if labels is not None else [None] * len(sig_list)
    if len(label_list) != len(sig_list):
        raise ValueError("labels length must match signal_times length")

    sign = float(side.value)
    rows = []
    dropped_trailing = 0
    dropped_missing = 0
    for sig, lab in zip(sig_list, label_list, strict=True):
        when = pd.Timestamp(sig).tz_convert("UTC") if pd.Timestamp(sig).tzinfo else pd.Timestamp(sig).tz_localize("UTC")
        entry = _bar_index_of(times, when)
        if entry is None:
            dropped_missing += 1
            continue
        exit_idx = entry + window_bars
        if exit_idx >= n:
            dropped_trailing += 1
            continue
        ep = closes[entry]
        xp = closes[exit_idx]
        if not (ep > 0 and xp > 0):
            dropped_missing += 1
            continue
        log_ret = float(np.log(xp / ep)) * sign
        rows.append(
            {
                "signal_time": times[entry],
                "entry_idx": entry,
                "exit_idx": exit_idx,
                "entry_price": ep,
                "exit_price": xp,
                "log_return": log_ret,
                "bars_held": window_bars,
                "side": int(sign),
                "label": lab,
            }
        )

    per_signal = pd.DataFrame(rows)
    return ForwardReturns(
        per_signal=per_signal,
        window_bars=window_bars,
        side=side,
        n_signals=len(rows),
        dropped_trailing=dropped_trailing,
        dropped_missing=dropped_missing,
    )
