"""Non-time-bar feasibility analyzer (diagnostic-only, research).

Pure economics + classification layer for the
``research-range-volatility-bar-feasibility-001`` sprint. Given **compact** bar
diagnostics (cadence/geometry, produced by reusing the tested
``forex_bot.data.non_time_bars`` builders) plus a per-pair spread estimate, this
module computes the transaction-cost economics that decide whether a
(pair, bar_type, threshold) cell is even worth strategy effort after CAMPAIGN_029.

It is **diagnostic-only**: it computes no signals, no PnL, no labelled returns, and
approves nothing. The only "strategy-like" arithmetic is the inherited C029 cost
model — half-spread + slippage per side — applied as *geometry* to candidate stop
sizes, never to a trade. The decision labels are hypotheses about where it is worth
looking, **not** gate passes.

All functions here are pure and deterministic so they can be unit-tested without a
database. The impure DB streaming + bar folding lives in the driver script
``scripts/analyze_non_time_bar_feasibility.py``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

from forex_bot.data.non_time_bars import pip_size

# --------------------------------------------------------------------------- #
# Constants — analyst-set, documented in
# docs/research/RANGE_VOLATILITY_BAR_FEASIBILITY_PROTOCOL.md §4.1.
# These are diagnostic thresholds, NOT gates.
# --------------------------------------------------------------------------- #

DEFAULT_SLIPPAGE_PIPS_PER_SIDE = 0.2  # matches CAMPAIGN_029's conservative cost model

# Cost-to-risk feasibility bands (evaluated at the baseline stop multiple).
FEASIBLE_COST_TO_RISK = 0.05  # a modest, historically-plausible gross edge can survive
MARGINAL_COST_TO_RISK = 0.10  # C029 lived here (0.095) and died

# Cadence bands, bars per year.
MIN_BARS_PER_YEAR = 200.0
MAX_BARS_PER_YEAR = 20_000.0

# Noise: fraction of bars whose forming M1 candle crossed the threshold > once.
MAX_MULTI_THRESHOLD_RATE = 0.10

# Minimum completed bars for any economics to be meaningful.
MIN_BAR_COUNT = 30

# Nominal stop multiples (× threshold). See protocol §3.
RANGE_BASELINE_STOP_MULT = 2.0
RANGE_WIDE_STOP_MULT = 4.0
VOL_BASELINE_STOP_MULT = 1.0
VOL_WIDE_STOP_MULT = 2.0

DAYS_PER_YEAR = 365.25
DAYS_PER_MONTH = DAYS_PER_YEAR / 12.0

# CAMPAIGN_029 anchor (USD_JPY 10-pip range bars, train window).
C029_COST_PIPS = 2.29
C029_AVG_RISK_PIPS = 24.05
C029_COST_TO_RISK = 0.095  # = 2.29 / 24.05, rounded as reported
C029_GROSS_EDGE_R = 0.0839
C029_NET_EDGE_R = -0.0188
# Best gross edge this lab has observed; used as the "achievable" benchmark.
LAB_ACHIEVABLE_GROSS_EDGE_R = 0.08

FeasibilityLabel = Literal[
    "FEASIBLE_FOR_STRATEGY_RESEARCH",
    "FEASIBLE_ONLY_WITH_LARGER_STOPS",
    "COST_DOMINATED",
    "TOO_SPARSE",
    "TOO_NOISY",
    "INCONCLUSIVE",
]

CadenceClass = Literal["too_sparse", "sane", "very_high"]


# --------------------------------------------------------------------------- #
# Cost economics
# --------------------------------------------------------------------------- #


def round_trip_cost_pips(
    spread_pips: float, *, slippage_pips_per_side: float = DEFAULT_SLIPPAGE_PIPS_PER_SIDE
) -> float:
    """Estimated round-trip transaction cost in pips.

    Matches the CAMPAIGN_029 cost model: a half-spread is paid at the entry fill and
    a half-spread at the exit fill (≈ one full spread round-trip), plus adverse
    slippage on each side. So ``cost = spread + 2 * slippage``.
    """
    if spread_pips < 0:
        raise ValueError("spread_pips must be non-negative")
    if slippage_pips_per_side < 0:
        raise ValueError("slippage_pips_per_side must be non-negative")
    return spread_pips + 2.0 * slippage_pips_per_side


def nominal_stop_pips(threshold_pips: float, stop_multiple: float) -> float:
    """Nominal stop distance in pips = ``stop_multiple × threshold`` (protocol §3)."""
    if threshold_pips <= 0:
        raise ValueError("threshold_pips must be positive")
    if stop_multiple <= 0:
        raise ValueError("stop_multiple must be positive")
    return threshold_pips * stop_multiple


def cost_to_threshold_ratio(round_trip_cost: float, threshold_pips: float) -> float:
    """Round-trip cost as a fraction of the bar threshold."""
    if threshold_pips <= 0:
        raise ValueError("threshold_pips must be positive")
    return round_trip_cost / threshold_pips


def cost_to_risk_ratio(round_trip_cost: float, stop_pips: float) -> float:
    """Round-trip cost as a fraction of nominal stop risk.

    This equals the **minimum gross expectancy (per-R)** a strategy must clear just
    to break even on cost: net_R ≈ gross_R − cost_to_risk.
    """
    if stop_pips <= 0:
        raise ValueError("stop_pips must be positive")
    return round_trip_cost / stop_pips


def min_gross_expectancy_to_survive(cost_to_risk: float) -> float:
    """Break-even gross expectancy per unit R (alias of the cost-to-risk ratio)."""
    return cost_to_risk


def baseline_stop_multiple(bar_type: str) -> float:
    """Baseline nominal-stop multiple for a bar type (protocol §3)."""
    return RANGE_BASELINE_STOP_MULT if bar_type == "range" else VOL_BASELINE_STOP_MULT


def wide_stop_multiple(bar_type: str) -> float:
    """Wider-stop scenario multiple for a bar type (protocol §3)."""
    return RANGE_WIDE_STOP_MULT if bar_type == "range" else VOL_WIDE_STOP_MULT


# --------------------------------------------------------------------------- #
# Cadence
# --------------------------------------------------------------------------- #


def bars_per_year(bar_count: int, window_days: float) -> float:
    """Window-normalised bar cadence, bars per 365.25 days."""
    if window_days <= 0:
        raise ValueError("window_days must be positive")
    return bar_count / (window_days / DAYS_PER_YEAR)


def bars_per_day(bar_count: int, window_days: float) -> float:
    if window_days <= 0:
        raise ValueError("window_days must be positive")
    return bar_count / window_days


def bars_per_month(bar_count: int, window_days: float) -> float:
    if window_days <= 0:
        raise ValueError("window_days must be positive")
    return bar_count / (window_days / DAYS_PER_MONTH)


def classify_cadence(per_year: float) -> CadenceClass:
    """Classify cadence into too_sparse / sane / very_high (protocol §4.1)."""
    if per_year < MIN_BARS_PER_YEAR:
        return "too_sparse"
    if per_year > MAX_BARS_PER_YEAR:
        return "very_high"
    return "sane"


def is_too_noisy(multi_threshold_rate: float, per_year: float) -> bool:
    """A cell is geometry-noisy if the threshold is small relative to an M1 candle's
    range (many bars cross the threshold more than once in one candle) or cadence is
    so high that cost is paid on a torrent of bars (protocol §4.1)."""
    return multi_threshold_rate > MAX_MULTI_THRESHOLD_RATE or per_year > MAX_BARS_PER_YEAR


# --------------------------------------------------------------------------- #
# Cell classification
# --------------------------------------------------------------------------- #


def classify_cell(
    *,
    bar_count: int,
    per_year: float,
    multi_threshold_rate: float,
    cost_to_risk_baseline: float,
    cost_to_risk_wide: float,
) -> FeasibilityLabel:
    """Assign one diagnostic label to a (pair, bar_type, threshold) cell.

    Priority order (first match wins), per protocol §4.2:
      1. insufficient data         -> INCONCLUSIVE
      2. too few bars/year         -> TOO_SPARSE
      3. noisy (multi-thresh/high) -> TOO_NOISY
      4. cheap at baseline stop    -> FEASIBLE_FOR_STRATEGY_RESEARCH
      5. cheap only at wide stop   -> FEASIBLE_ONLY_WITH_LARGER_STOPS
      6. otherwise                 -> COST_DOMINATED
    """
    if bar_count < MIN_BAR_COUNT:
        return "INCONCLUSIVE"
    if per_year < MIN_BARS_PER_YEAR:
        return "TOO_SPARSE"
    if is_too_noisy(multi_threshold_rate, per_year):
        return "TOO_NOISY"
    if cost_to_risk_baseline <= FEASIBLE_COST_TO_RISK:
        return "FEASIBLE_FOR_STRATEGY_RESEARCH"
    if cost_to_risk_wide <= FEASIBLE_COST_TO_RISK:
        return "FEASIBLE_ONLY_WITH_LARGER_STOPS"
    return "COST_DOMINATED"


# --------------------------------------------------------------------------- #
# Cell record
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class FeasibilityCell:
    """One (pair, bar_type, threshold) feasibility record (compact, serialisable)."""

    instrument: str
    bar_type: str  # "range" | "volatility"
    method: str | None  # None for range; "true_range" | "abs_close" for volatility
    threshold_pips: float
    bar_count: int
    window_days: float
    spread_pips: float
    slippage_pips_per_side: float

    # derived (filled by build_cell)
    per_year: float = 0.0
    per_month: float = 0.0
    per_day: float = 0.0
    median_minutes_per_bar: float | None = None
    avg_m1_rows_per_bar: float | None = None
    avg_overshoot_pips: float | None = None
    multi_threshold_rate: float = 0.0
    round_trip_cost_pips: float = 0.0
    cost_to_threshold: float = 0.0
    baseline_stop_pips: float = 0.0
    wide_stop_pips: float = 0.0
    cost_to_risk_baseline: float = 0.0
    cost_to_risk_wide: float = 0.0
    min_gross_edge_baseline_r: float = 0.0
    cadence_class: str = "sane"
    label: str = "INCONCLUSIVE"

    def as_dict(self) -> dict:
        return asdict(self)


def build_cell(
    *,
    instrument: str,
    bar_type: str,
    method: str | None,
    threshold_pips: float,
    bar_count: int,
    window_days: float,
    spread_pips: float,
    slippage_pips_per_side: float = DEFAULT_SLIPPAGE_PIPS_PER_SIDE,
    multi_threshold_rate: float = 0.0,
    median_minutes_per_bar: float | None = None,
    avg_m1_rows_per_bar: float | None = None,
    avg_overshoot_pips: float | None = None,
) -> FeasibilityCell:
    """Compute every derived field and the diagnostic label for one cell (pure)."""
    cost = round_trip_cost_pips(spread_pips, slippage_pips_per_side=slippage_pips_per_side)
    base_mult = baseline_stop_multiple(bar_type)
    wide_mult = wide_stop_multiple(bar_type)
    base_stop = nominal_stop_pips(threshold_pips, base_mult)
    wide_stop = nominal_stop_pips(threshold_pips, wide_mult)

    if window_days > 0:
        py = bars_per_year(bar_count, window_days)
        pm = bars_per_month(bar_count, window_days)
        pd = bars_per_day(bar_count, window_days)
    else:
        py = pm = pd = 0.0

    ctr_base = cost_to_risk_ratio(cost, base_stop)
    ctr_wide = cost_to_risk_ratio(cost, wide_stop)

    label = classify_cell(
        bar_count=bar_count,
        per_year=py,
        multi_threshold_rate=multi_threshold_rate,
        cost_to_risk_baseline=ctr_base,
        cost_to_risk_wide=ctr_wide,
    )

    return FeasibilityCell(
        instrument=instrument,
        bar_type=bar_type,
        method=method,
        threshold_pips=threshold_pips,
        bar_count=bar_count,
        window_days=round(window_days, 3),
        spread_pips=round(spread_pips, 4),
        slippage_pips_per_side=slippage_pips_per_side,
        per_year=round(py, 2),
        per_month=round(pm, 2),
        per_day=round(pd, 3),
        median_minutes_per_bar=median_minutes_per_bar,
        avg_m1_rows_per_bar=avg_m1_rows_per_bar,
        avg_overshoot_pips=avg_overshoot_pips,
        multi_threshold_rate=round(multi_threshold_rate, 4),
        round_trip_cost_pips=round(cost, 4),
        cost_to_threshold=round(cost_to_threshold_ratio(cost, threshold_pips), 4),
        baseline_stop_pips=round(base_stop, 3),
        wide_stop_pips=round(wide_stop, 3),
        cost_to_risk_baseline=round(ctr_base, 4),
        cost_to_risk_wide=round(ctr_wide, 4),
        min_gross_edge_baseline_r=round(min_gross_expectancy_to_survive(ctr_base), 4),
        cadence_class=classify_cadence(py),
        label=label,
    )


# --------------------------------------------------------------------------- #
# Spread / cost helpers
# --------------------------------------------------------------------------- #


def spread_price_to_pips(spread_price: float, instrument: str) -> float:
    """Convert a price-space spread (ask − bid) to pips for the instrument."""
    if spread_price < 0:
        raise ValueError("spread_price must be non-negative")
    return spread_price / float(pip_size(instrument))


# --------------------------------------------------------------------------- #
# Comparisons + deterministic summary
# --------------------------------------------------------------------------- #


def _sorted_cells(cells: list[FeasibilityCell]) -> list[FeasibilityCell]:
    """Deterministic ordering: instrument, bar_type, method, threshold."""
    return sorted(
        cells,
        key=lambda c: (c.instrument, c.bar_type, c.method or "", c.threshold_pips),
    )


def label_counts(cells: list[FeasibilityCell]) -> dict[str, int]:
    """Count cells by label, in a stable label order."""
    order: list[FeasibilityLabel] = [
        "FEASIBLE_FOR_STRATEGY_RESEARCH",
        "FEASIBLE_ONLY_WITH_LARGER_STOPS",
        "COST_DOMINATED",
        "TOO_SPARSE",
        "TOO_NOISY",
        "INCONCLUSIVE",
    ]
    counts = {label: 0 for label in order}
    for c in cells:
        counts[c.label] = counts.get(c.label, 0) + 1
    return counts


def compare_range_vs_volatility(cells: list[FeasibilityCell]) -> dict:
    """Compare range vs volatility cells on cost-to-risk and feasibility share."""
    out: dict[str, dict] = {}
    for bar_type in ("range", "volatility"):
        group = [c for c in cells if c.bar_type == bar_type]
        if not group:
            out[bar_type] = {"n_cells": 0}
            continue
        feasible = [
            c
            for c in group
            if c.label
            in ("FEASIBLE_FOR_STRATEGY_RESEARCH", "FEASIBLE_ONLY_WITH_LARGER_STOPS")
        ]
        ctrs = sorted(c.cost_to_risk_baseline for c in group)
        out[bar_type] = {
            "n_cells": len(group),
            "n_feasible": len(feasible),
            "feasible_share": round(len(feasible) / len(group), 4),
            "median_cost_to_risk_baseline": ctrs[len(ctrs) // 2],
            "min_cost_to_risk_baseline": ctrs[0],
        }
    return out


def compare_pair_vs_others(cells: list[FeasibilityCell], focus: str) -> dict:
    """Compare one pair's cost economics against the pooled others."""
    focus_cells = [c for c in cells if c.instrument == focus]
    other_cells = [c for c in cells if c.instrument != focus]

    def _agg(group: list[FeasibilityCell]) -> dict:
        if not group:
            return {"n_cells": 0}
        ctrs = sorted(c.cost_to_risk_baseline for c in group)
        feasible = sum(
            1
            for c in group
            if c.label
            in ("FEASIBLE_FOR_STRATEGY_RESEARCH", "FEASIBLE_ONLY_WITH_LARGER_STOPS")
        )
        return {
            "n_cells": len(group),
            "median_cost_to_risk_baseline": ctrs[len(ctrs) // 2],
            "min_cost_to_risk_baseline": ctrs[0],
            "feasible_share": round(feasible / len(group), 4),
            "mean_spread_pips": round(sum(c.spread_pips for c in group) / len(group), 4),
        }

    return {focus: _agg(focus_cells), "others_pooled": _agg(other_cells)}


def summarize_feasibility(cells: list[FeasibilityCell]) -> dict:
    """Deterministic top-level summary (stable ordering, ready to serialise)."""
    ordered = _sorted_cells(cells)
    pairs = sorted({c.instrument for c in ordered})
    return {
        "n_cells": len(ordered),
        "pairs": pairs,
        "label_counts": label_counts(ordered),
        "range_vs_volatility": compare_range_vs_volatility(ordered),
        "cells": [c.as_dict() for c in ordered],
    }


@dataclass
class CostFloorRow:
    """C029-anchored cost-floor comparison for one cell."""

    instrument: str
    bar_type: str
    method: str | None
    threshold_pips: float
    round_trip_cost_pips: float
    baseline_stop_pips: float
    cost_to_risk_baseline: float
    min_gross_edge_baseline_r: float
    beats_c029_cost_floor: bool = field(default=False)
    survivable_by_lab_edge: bool = field(default=False)

    def as_dict(self) -> dict:
        return asdict(self)


def cost_floor_row(cell: FeasibilityCell) -> CostFloorRow:
    """Build the C029-anchored cost-floor comparison for a cell.

    ``beats_c029_cost_floor`` = this cell's break-even gross edge is below C029's
    (i.e. cost is less punishing than the 10-pip USD_JPY case). ``survivable_by_lab``
    = the break-even gross edge is below the best gross edge this lab has observed
    (~0.08R), i.e. a known-achievable edge could in principle clear cost here.
    """
    return CostFloorRow(
        instrument=cell.instrument,
        bar_type=cell.bar_type,
        method=cell.method,
        threshold_pips=cell.threshold_pips,
        round_trip_cost_pips=cell.round_trip_cost_pips,
        baseline_stop_pips=cell.baseline_stop_pips,
        cost_to_risk_baseline=cell.cost_to_risk_baseline,
        min_gross_edge_baseline_r=cell.min_gross_edge_baseline_r,
        beats_c029_cost_floor=cell.cost_to_risk_baseline < C029_COST_TO_RISK,
        survivable_by_lab_edge=cell.cost_to_risk_baseline <= LAB_ACHIEVABLE_GROSS_EDGE_R,
    )
