"""H03 thin-move fade — front-gate screen helpers (diagnostic-only).

Pure, DB-free functions that measure **conditional forward returns** after
non-time-bar completions, bucketed by completion **participation (tick-count
volume)**, for the `research-non-time-bar-thin-move-frontgate-001` screen. This is
a *conditional-distribution measurement*, not a strategy: there are no positions,
stops, sizing, PnL, equity, or signals here, and nothing is approved.

H03's claim: a move that completes on **unusually low participation** (low
tick-count volume) is more likely to **mean-revert** than one that completes on
normal/high participation. On range bars travel is ~fixed (threshold + overshoot),
so participation (volume) is the conditioning variable and the test is approximately
move-matched (the G4 point — see H03_THIN_MOVE_HYPOTHESIS.md §3).

The "fade return" convention is identical to the H16 screen so the two are directly
comparable: ``fade_k(i) = −completion_dir(i) × (mid_close[i+k] − mid_close[i])`` in
pips — **positive ⇒ price reverted** (the hypothesised behaviour for thin moves);
negative ⇒ continuation.

Generic statistics (`fade_returns`, `bucket_stats`, `permutation_null_group_mean`,
`autocorr_lag1`, `to_pips`) are reused from the H16 screen module to avoid
duplication; this module adds the H03-specific **participation bucketing** (per-pair
tertiles + a bottom-decile ultra-thin tail). All functions are deterministic (the
permutation null takes an explicit seed) so they are unit-testable without a database.
Impure DB streaming + bar building lives in ``scripts/screen_h03_thin_move.py``.
"""

from __future__ import annotations

import math
import statistics

# Reuse the generic, already-tested primitives from the H16 screen module.
from forex_bot.research.overshoot_exhaustion_screen import (  # noqa: F401  (re-exported)
    BucketStats,
    PermutationNull,
    autocorr_lag1,
    bucket_stats,
    fade_returns,
    permutation_null_group_mean,
    to_pips,
)

# Participation buckets, thin → high. "ultra_thin" is a disjoint sharp tail, handled
# separately (it overlaps "low"); the tertiles below partition all bars.
PARTICIPATION_BUCKETS = ("low", "medium", "high")
ULTRA_THIN_FRAC = 0.10


def tertile_edges(values: list[float]) -> tuple[float, float]:
    """Per-pair tertile edges (p33.3, p66.7) of a value list (>= 2 values).

    Bars with ``value <= edges[0]`` are ``low`` participation (thin), ``> edges[1]``
    are ``high``, the rest ``medium``.
    """
    if len(values) < 2:
        raise ValueError("need >= 2 values for tertile edges")
    q = statistics.quantiles(sorted(values), n=3)  # two cut points -> three groups
    return (q[0], q[1])


def participation_label(value: float, edges: tuple[float, float]) -> str:
    """Map a volume to low/medium/high participation by the tertile edges.

    Lower volume ⇒ thinner participation ⇒ ``low``.
    """
    p33, p67 = edges
    if value <= p33:
        return "low"
    if value <= p67:
        return "medium"
    return "high"


def low_tail_threshold(values: list[float], frac: float = ULTRA_THIN_FRAC) -> float:
    """Value at the ``frac`` quantile — the upper edge of the bottom ``frac`` tail.

    Bars with ``value <= low_tail_threshold`` are the ``ultra_thin`` group. This is the
    low-side mirror of the H16 screen's ``top_tail_threshold``.
    """
    if not 0.0 < frac < 1.0:
        raise ValueError("frac must be in (0, 1)")
    if not values:
        raise ValueError("values must be non-empty")
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil(frac * len(ordered)) - 1))
    return ordered[idx]
