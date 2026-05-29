"""Cost-feasibility flagging for the edge-discovery lab.

The lab already *computes* spread/ATR and cost overlays (``costs.py`` and the
``research/cost_atlas`` builder). What was missing is a cheap **gate** layer
that turns those numbers into a pre-campaign feasibility verdict so a timeframe
/ session / pair that is structurally cost-hostile gets rejected *before* a
campaign is built — the exact lesson of C025 (M5 spread/ATR ≈ 0.45) and C026
(the M3→M30 cost ladder).

This module does NOT recompute spread or ATR; it consumes a spread/ATR ratio
(bid-ask spread as a fraction of per-bar ATR) plus optional pip-level spread and
returns descriptive flags, the minimum target-R needed to overcome the cost
drag, and an opportunity score. Pure and deterministic. Descriptive only.

Flags:
  * ``COST_FEASIBLE``            — spread/ATR below the hostile threshold
  * ``COST_HOSTILE``            — spread/ATR at/above the hostile threshold
  * ``TIMEFRAME_TOO_FAST``      — a timeframe whose median spread/ATR is hostile
  * ``SESSION_HOSTILE``         — a session whose spread/ATR is hostile
  * ``PAIR_COST_ADVANTAGED``    — pair spread/ATR materially below the universe median
  * ``PAIR_COST_DISADVANTAGED`` — pair spread/ATR materially above the universe median

Import-isolated: numpy / pandas only.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import pandas as pd

# Default hostile threshold. C025/C026 evidence: M3≈0.59 / M5≈0.45 were
# cost-defeated; M15≈0.23 / M30≈0.15 were not cost-bound (though still no edge).
# 0.25 sits between the cost-bound and not-cost-bound regimes.
DEFAULT_HOSTILE_RATIO = 0.25
# A pair is "advantaged"/"disadvantaged" when it deviates from the universe
# median spread/ATR by more than this fraction.
DEFAULT_PAIR_DEVIATION = 0.20

COST_FLAGS = (
    "COST_FEASIBLE",
    "COST_HOSTILE",
    "TIMEFRAME_TOO_FAST",
    "SESSION_HOSTILE",
    "PAIR_COST_ADVANTAGED",
    "PAIR_COST_DISADVANTAGED",
)


def round_trip_cost_pips(spread_pips: float, *, slip_pips: float = 0.2) -> float:
    """Round-trip transaction cost in pips (entry + exit), matching the
    ``costs.cost_fraction`` convention: ``spread + 2 * slip``."""
    return float(spread_pips) + 2.0 * float(slip_pips)


def min_target_r_to_overcome(round_trip_pips: float, stop_pips: float) -> float:
    """Minimum target (in R) just to break even against the round-trip cost,
    given a stop distance in pips. ``cost_in_R = round_trip_pips / stop_pips``."""
    if stop_pips <= 0:
        raise ValueError(f"stop_pips must be positive, got {stop_pips}")
    return round_trip_pips / float(stop_pips)


def opportunity_score(spread_atr_ratio: float, *, hostile_ratio: float = DEFAULT_HOSTILE_RATIO) -> float:
    """A 0..1 score: 1.0 when cost is negligible, 0.0 at/above the hostile
    threshold. Linear in the ratio, clipped."""
    if hostile_ratio <= 0:
        raise ValueError("hostile_ratio must be positive")
    return float(max(0.0, min(1.0, 1.0 - spread_atr_ratio / hostile_ratio)))


@dataclass(frozen=True)
class CostFeasibilityCell:
    """Feasibility verdict for one pair/timeframe/session cell."""

    label: str
    spread_atr_ratio: float
    opportunity_score: float
    min_target_r: float | None
    flags: list[str]
    extras: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "spread_atr_ratio": self.spread_atr_ratio,
            "opportunity_score": self.opportunity_score,
            "min_target_r": self.min_target_r,
            "flags": list(self.flags),
            "extras": dict(self.extras),
        }


def classify_cost_feasibility(
    label: str,
    spread_atr_ratio: float,
    *,
    hostile_ratio: float = DEFAULT_HOSTILE_RATIO,
    spread_pips: float | None = None,
    stop_pips: float | None = None,
    slip_pips: float = 0.2,
    kind: str | None = None,
    universe_median_ratio: float | None = None,
    pair_deviation: float = DEFAULT_PAIR_DEVIATION,
) -> CostFeasibilityCell:
    """Classify a single cost cell.

    ``kind`` (``"timeframe"`` / ``"session"`` / ``"pair"`` / ``None``) controls
    which structural flag a hostile cell also receives. When
    ``universe_median_ratio`` is supplied, a pair cell is additionally flagged
    advantaged/disadvantaged relative to it.
    """
    flags: list[str] = []
    hostile = spread_atr_ratio >= hostile_ratio
    flags.append("COST_HOSTILE" if hostile else "COST_FEASIBLE")
    if hostile and kind == "timeframe":
        flags.append("TIMEFRAME_TOO_FAST")
    if hostile and kind == "session":
        flags.append("SESSION_HOSTILE")
    if kind == "pair" and universe_median_ratio is not None and universe_median_ratio > 0:
        rel = (spread_atr_ratio - universe_median_ratio) / universe_median_ratio
        if rel <= -pair_deviation:
            flags.append("PAIR_COST_ADVANTAGED")
        elif rel >= pair_deviation:
            flags.append("PAIR_COST_DISADVANTAGED")

    min_target = None
    if spread_pips is not None and stop_pips is not None:
        min_target = min_target_r_to_overcome(
            round_trip_cost_pips(spread_pips, slip_pips=slip_pips), stop_pips
        )

    extras: dict[str, object] = {"hostile_ratio": hostile_ratio}
    if spread_pips is not None:
        extras["spread_pips"] = float(spread_pips)
    return CostFeasibilityCell(
        label=label,
        spread_atr_ratio=float(spread_atr_ratio),
        opportunity_score=opportunity_score(spread_atr_ratio, hostile_ratio=hostile_ratio),
        min_target_r=min_target,
        flags=flags,
        extras=extras,
    )


def cost_feasibility_table(
    cells: Mapping[str, float],
    *,
    kind: str | None = None,
    hostile_ratio: float = DEFAULT_HOSTILE_RATIO,
    flag_pairs_vs_median: bool = False,
    pair_deviation: float = DEFAULT_PAIR_DEVIATION,
) -> pd.DataFrame:
    """Classify many cells (``{label: spread_atr_ratio}``) into a tidy frame.

    With ``flag_pairs_vs_median`` the universe median ratio is computed across
    the supplied cells and each is flagged advantaged/disadvantaged.
    """
    if not cells:
        raise ValueError("cells is empty")
    median_ratio = None
    if flag_pairs_vs_median:
        median_ratio = float(pd.Series(list(cells.values())).median())
    rows = []
    for label in sorted(cells):
        cell = classify_cost_feasibility(
            label, float(cells[label]),
            hostile_ratio=hostile_ratio, kind=kind,
            universe_median_ratio=median_ratio, pair_deviation=pair_deviation,
        )
        d = cell.to_dict()
        d["flags"] = ";".join(d["flags"])
        d.pop("extras", None)
        rows.append(d)
    return pd.DataFrame(rows)
