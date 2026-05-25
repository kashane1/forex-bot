"""CAMPAIGN_015 anti-overfit diagnostic classifier.

Pure function. Consumes a small structured input describing the
CAMPAIGN_015 aggregate metrics and the matched CAMPAIGN_011 null
baseline, and emits exactly one of the binding labels from
``docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md`` §11:

* ``ROBUST_ABOVE_NULL``
* ``ABOVE_NULL_BUT_FRAGILE``
* ``SELECTED_CELL_ARTIFACT``
* ``WITHIN_NULL``
* ``WORSE_THAN_NULL``
* ``BLOCKED``

The classifier never modifies any registry or artifact; it never
imports broker / OANDA / LEAN. It cannot approve a strategy.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field

CAMPAIGN_015_CLASSIFIER_LABELS = (
    "ROBUST_ABOVE_NULL",
    "ABOVE_NULL_BUT_FRAGILE",
    "SELECTED_CELL_ARTIFACT",
    "WITHIN_NULL",
    "WORSE_THAN_NULL",
    "BLOCKED",
)

# Anti-overfit thresholds (binding per pre-commit §9).
LOO_MIN_MEAN_GAP_R_MIN = 0.05
PER_FOLD_T_STAT_MIN = 2.0
MEDIAN_PER_FOLD_EXPECTANCY_R_MIN = 0.0
TRADE_LEVEL_CUMULATIVE_R_MIN = 0.0
PAIR_CONCENTRATION_MAX = 0.70  # top pair > 70% of gross positive R
FOLD_CONCENTRATION_MAX = 0.60  # top fold > 60% of gross positive R
COST_DOMINANCE_MAX = 0.50

# Aggregate gates (Phase 0 §8.1; for the "above null" determination).
AGG_EXPECTANCY_R_MIN_BASE = 0.03
AGG_PROFIT_FACTOR_MIN_BASE = 1.05

# Indistinguishability bands for the WITHIN_NULL label.
WITHIN_NULL_PF_BAND = (0.95, 1.05)
WITHIN_NULL_RETURN_PCT_BAND_HALF = 2.0  # |ret_pct| <= |null_ret_pct| + 2.0
WITHIN_NULL_PAIRS_POSITIVE_BAND = 1


@dataclass
class DiagnosticInputs:
    """All inputs needed to classify CAMPAIGN_015 vs the CAMPAIGN_011
    matched null. Numeric fields default to NaN so a partially-filled
    record short-circuits to BLOCKED."""

    blocked: bool = False
    blocked_reasons: list[str] = field(default_factory=list)

    # Campaign aggregate
    campaign_expectancy_r: float = math.nan
    campaign_return_pct: float = math.nan
    campaign_profit_factor: float | None = None
    campaign_pairs_positive: int = -1
    campaign_total_trades: int = 0
    # Per-fold expectancy in R, campaign
    campaign_per_fold_expectancy_r: list[float] = field(default_factory=list)
    # Per-pair gross positive R (sum of positive per-trade R per pair)
    campaign_pair_gross_positive_r: dict[str, float] = field(default_factory=dict)
    # Per-fold gross positive R (sum of positive per-trade R per fold)
    campaign_fold_gross_positive_r: list[float] = field(default_factory=list)
    # All per-trade R values, in order
    campaign_trade_r_series: list[float] = field(default_factory=list)
    # Estimated total cost in R (commissions + slippage * trades)
    campaign_total_cost_r: float = 0.0

    # Null aggregate (CAMPAIGN_011, matched sample)
    null_expectancy_r: float = math.nan
    null_return_pct: float = math.nan
    null_profit_factor: float | None = None
    null_pairs_positive: int = -1
    null_per_fold_expectancy_r: list[float] = field(default_factory=list)


def classify_campaign_015(inputs: DiagnosticInputs) -> dict[str, object]:
    """Return a dict with `label` and per-axis diagnostics.

    Output shape:
      {
        "label": one of CAMPAIGN_015_CLASSIFIER_LABELS,
        "anti_overfit_gates": dict[str, bool],
        "metrics": dict[str, float | None],
        "reasons": list[str],
      }
    """
    if inputs.blocked:
        return _blocked(inputs.blocked_reasons or ["blocked by upstream"])

    fold_count = len(inputs.campaign_per_fold_expectancy_r)
    null_fold_count = len(inputs.null_per_fold_expectancy_r)

    if fold_count < 3 or null_fold_count != fold_count:
        return _blocked(
            [
                f"insufficient folds: campaign={fold_count}, "
                f"null={null_fold_count}; classifier needs >= 3 folds "
                "and matching null"
            ]
        )

    # Per-fold gap series.
    fold_gap = [
        inputs.campaign_per_fold_expectancy_r[i] - inputs.null_per_fold_expectancy_r[i]
        for i in range(fold_count)
    ]

    # LOO min mean gap (drop fold k; recompute mean gap on the
    # remaining N-1; take the minimum across k).
    loo_means = []
    for k in range(fold_count):
        remaining = [g for j, g in enumerate(fold_gap) if j != k]
        loo_means.append(statistics.mean(remaining))
    loo_min_mean_gap = min(loo_means) if loo_means else math.nan

    # Per-fold t-stat: mean / (stdev / sqrt(N)).
    if fold_count >= 2:
        gap_mean = statistics.mean(fold_gap)
        gap_std = statistics.stdev(fold_gap)
        if gap_std == 0:
            t_stat = math.inf if gap_mean > 0 else (-math.inf if gap_mean < 0 else 0.0)
        else:
            t_stat = gap_mean / (gap_std / math.sqrt(fold_count))
    else:
        gap_mean = math.nan
        t_stat = math.nan

    median_per_fold = statistics.median(inputs.campaign_per_fold_expectancy_r)
    trade_level_cumulative_r = sum(inputs.campaign_trade_r_series)

    # Pair concentration: max pair share of total gross positive R.
    pair_gross_total = sum(inputs.campaign_pair_gross_positive_r.values())
    if pair_gross_total > 0:
        pair_concentration = (
            max(inputs.campaign_pair_gross_positive_r.values()) / pair_gross_total
        )
    else:
        pair_concentration = 0.0

    # Fold concentration: max fold share of total gross positive R.
    fold_gross_total = sum(inputs.campaign_fold_gross_positive_r)
    if fold_gross_total > 0:
        fold_concentration = max(inputs.campaign_fold_gross_positive_r) / fold_gross_total
    else:
        fold_concentration = 0.0

    # Cost dominance.
    abs_total_r = sum(abs(r) for r in inputs.campaign_trade_r_series)
    cost_dominance = (
        inputs.campaign_total_cost_r / abs_total_r if abs_total_r > 0 else 0.0
    )

    # "Above-null" precondition for ROBUST / FRAGILE: the campaign's
    # aggregate expectancy AND PF must meet the Phase 0 §8.1 floors.
    above_aggregate_floor = (
        inputs.campaign_expectancy_r >= AGG_EXPECTANCY_R_MIN_BASE
        and inputs.campaign_profit_factor is not None
        and inputs.campaign_profit_factor >= AGG_PROFIT_FACTOR_MIN_BASE
    )

    # The anti-overfit gates.
    gates = {
        "loo_min_mean_gap_ge_0p05": loo_min_mean_gap >= LOO_MIN_MEAN_GAP_R_MIN,
        "per_fold_t_stat_ge_2p0": t_stat >= PER_FOLD_T_STAT_MIN,
        "median_per_fold_expectancy_ge_0": (
            median_per_fold >= MEDIAN_PER_FOLD_EXPECTANCY_R_MIN
        ),
        "trade_level_cumulative_r_gt_0": (
            trade_level_cumulative_r > TRADE_LEVEL_CUMULATIVE_R_MIN
        ),
        "pair_concentration_le_70pct": pair_concentration <= PAIR_CONCENTRATION_MAX,
        "fold_concentration_le_60pct": fold_concentration <= FOLD_CONCENTRATION_MAX,
        "cost_dominance_le_50pct": cost_dominance <= COST_DOMINANCE_MAX,
    }
    all_gates_pass = all(gates.values())

    # WITHIN_NULL detection: campaign aggregates sit inside null bands.
    pf_band_low, pf_band_high = WITHIN_NULL_PF_BAND
    inside_pf_band = (
        inputs.campaign_profit_factor is not None
        and pf_band_low <= inputs.campaign_profit_factor <= pf_band_high
    )
    within_null = (
        inside_pf_band
        and not math.isnan(inputs.null_return_pct)
        and abs(inputs.campaign_return_pct - inputs.null_return_pct)
        <= WITHIN_NULL_RETURN_PCT_BAND_HALF
        and abs(inputs.campaign_pairs_positive - inputs.null_pairs_positive)
        <= WITHIN_NULL_PAIRS_POSITIVE_BAND
        and abs(gap_mean) < 0.02
    )

    # WORSE_THAN_NULL detection: every binding axis is meaningfully worse.
    worse_than_null = (
        inputs.campaign_expectancy_r < inputs.null_expectancy_r
        and (inputs.campaign_profit_factor or 0.0) < (inputs.null_profit_factor or 0.0)
        and inputs.campaign_return_pct < inputs.null_return_pct
        and inputs.campaign_pairs_positive <= inputs.null_pairs_positive
        and gap_mean < -0.05
    )

    # SELECTED_CELL_ARTIFACT detection: one pair or one fold drives the
    # entire positive R, AND removing it would collapse the campaign
    # below the matched null.
    top_pair_drives_all = pair_concentration > PAIR_CONCENTRATION_MAX
    top_fold_drives_all = fold_concentration > FOLD_CONCENTRATION_MAX
    selected_cell_artifact = top_pair_drives_all or top_fold_drives_all

    metrics = {
        "loo_min_mean_gap_r": loo_min_mean_gap,
        "per_fold_t_stat": t_stat,
        "gap_mean_r": gap_mean,
        "median_per_fold_expectancy_r": median_per_fold,
        "trade_level_cumulative_r": trade_level_cumulative_r,
        "pair_concentration": pair_concentration,
        "fold_concentration": fold_concentration,
        "cost_dominance": cost_dominance,
        "aggregate_floor_pass": above_aggregate_floor,
        "within_null_pf_band_match": inside_pf_band,
        "worse_than_null": worse_than_null,
        "selected_cell_artifact_geometry": selected_cell_artifact,
    }
    reasons: list[str] = []

    # Decision logic (precedence: WORSE -> WITHIN -> SELECTED_CELL ->
    # ROBUST -> ABOVE-NULL FRAGILE).
    if worse_than_null:
        label = "WORSE_THAN_NULL"
        reasons.append("campaign aggregate metrics materially worse than matched null")
    elif within_null:
        label = "WITHIN_NULL"
        reasons.append("campaign aggregate metrics sit inside CAMPAIGN_011 null band")
    elif above_aggregate_floor and selected_cell_artifact:
        # Above the aggregate floor but driven by one cell -- artifact.
        label = "SELECTED_CELL_ARTIFACT"
        if top_pair_drives_all:
            reasons.append(
                f"top pair drives {pair_concentration:.1%} of gross positive R "
                f"(threshold > {PAIR_CONCENTRATION_MAX:.0%})"
            )
        if top_fold_drives_all:
            reasons.append(
                f"top fold drives {fold_concentration:.1%} of gross positive R "
                f"(threshold > {FOLD_CONCENTRATION_MAX:.0%})"
            )
    elif above_aggregate_floor and all_gates_pass:
        label = "ROBUST_ABOVE_NULL"
        reasons.append("all aggregate + anti-overfit gates pass; not driven by a single cell")
    elif above_aggregate_floor:
        label = "ABOVE_NULL_BUT_FRAGILE"
        failed = [name for name, ok in gates.items() if not ok]
        reasons.append(f"aggregate floor pass but anti-overfit gates fail: {failed}")
    else:
        # Aggregate floor not met but neither WORSE nor WITHIN — borderline.
        # Default to WITHIN_NULL as the most conservative non-positive
        # label (the strategy did not demonstrably beat null, but also
        # not catastrophically worse on every axis).
        label = "WITHIN_NULL"
        reasons.append(
            "aggregate floor not met and neither worse-than-null nor "
            "selected-cell-artifact criteria fully tripped; defaulting "
            "to WITHIN_NULL"
        )

    return {
        "label": label,
        "anti_overfit_gates": gates,
        "metrics": metrics,
        "reasons": reasons,
    }


def _blocked(reasons: list[str]) -> dict[str, object]:
    return {
        "label": "BLOCKED",
        "anti_overfit_gates": {},
        "metrics": {},
        "reasons": list(reasons),
    }
