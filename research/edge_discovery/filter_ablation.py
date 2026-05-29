"""Filter-ablation diagnostics for the edge-discovery lab.

A recurring failure mode in strategy search is adding filters that *look*
helpful because the surviving sample has a higher mean — but the filter only
shrank the sample (selection variance), it did not add edge. This module
decomposes a staged signal table so a filter has to earn its place:

  * ``trigger_only``      — every triggered signal, no filter
  * ``filter:<name>``     — trigger + exactly one filter (marginal view)
  * ``cumulative:<k>``    — trigger + the first k filters AND-combined
  * ``leave_out:<name>``  — all filters except one (how much it contributes)
  * ``all_filters``       — every filter AND-combined

For each stage it reports pass count, the sample-reduction ratio versus
trigger-only, the expectancy proxy (mean of the value column), the hit rate,
an optional post-cost expectancy, and pair/side coverage. Per filter it then
derives a contribution score and a descriptive flag:

  * ``FILTER_ADDS_EDGE``          — raises expectancy beyond a tolerance
  * ``FILTER_ONLY_REDUCES_SAMPLE``— shrinks the sample without changing edge
  * ``FILTER_HURTS_EDGE``         — lowers expectancy beyond a tolerance
  * ``FILTER_TOO_SPARSE``         — one-filter sample below ``min_sample``
  * ``FILTER_PAIR_SPECIFIC_ONLY`` — surviving sample concentrated on one pair

The value column is whatever forward-return / expectancy proxy the caller
supplies (e.g. ``log_return`` from ``windows.compute_forward_returns``); the
module is metric-agnostic and does no randomization, so it is deterministic by
construction. Descriptive only — never a verdict.

Import-isolated: numpy / pandas only.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import pandas as pd

FILTER_FLAGS = (
    "FILTER_ADDS_EDGE",
    "FILTER_ONLY_REDUCES_SAMPLE",
    "FILTER_HURTS_EDGE",
    "FILTER_TOO_SPARSE",
    "FILTER_PAIR_SPECIFIC_ONLY",
)


@dataclass(frozen=True)
class StageMetrics:
    """Metrics for one ablation stage."""

    stage: str
    filters_applied: tuple[str, ...]
    n: int
    reduction_ratio: float
    expectancy: float
    expectancy_se: float
    hit_rate: float
    post_cost_expectancy: float | None
    pair_coverage: int
    side_coverage: int
    top_pair_concentration: float

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "filters_applied": list(self.filters_applied),
            "n": self.n,
            "reduction_ratio": self.reduction_ratio,
            "expectancy": self.expectancy,
            "expectancy_se": self.expectancy_se,
            "hit_rate": self.hit_rate,
            "post_cost_expectancy": self.post_cost_expectancy,
            "pair_coverage": self.pair_coverage,
            "side_coverage": self.side_coverage,
            "top_pair_concentration": self.top_pair_concentration,
        }


@dataclass(frozen=True)
class FilterContribution:
    """How much one filter contributes, marginally and at leave-one-out."""

    filter: str
    marginal_expectancy_gain: float
    leave_out_delta: float
    reduction_ratio: float
    edge_per_unit_reduction: float | None
    flags: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "filter": self.filter,
            "marginal_expectancy_gain": self.marginal_expectancy_gain,
            "leave_out_delta": self.leave_out_delta,
            "reduction_ratio": self.reduction_ratio,
            "edge_per_unit_reduction": self.edge_per_unit_reduction,
            "flags": list(self.flags),
        }


@dataclass(frozen=True)
class FilterAblationResult:
    trigger_only: StageMetrics
    all_filters: StageMetrics
    single_filter: list[StageMetrics]
    cumulative: list[StageMetrics]
    leave_one_out: list[StageMetrics]
    contributions: list[FilterContribution]
    value_col: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "value_col": self.value_col,
            "trigger_only": self.trigger_only.to_dict(),
            "all_filters": self.all_filters.to_dict(),
            "single_filter": [s.to_dict() for s in self.single_filter],
            "cumulative": [s.to_dict() for s in self.cumulative],
            "leave_one_out": [s.to_dict() for s in self.leave_one_out],
            "contributions": [c.to_dict() for c in self.contributions],
            "notes": list(self.notes),
        }


def _stage_metrics(
    sub: pd.DataFrame,
    *,
    stage: str,
    filters_applied: Sequence[str],
    baseline_n: int,
    value_col: str,
    post_cost_col: str | None,
    pair_col: str | None,
    side_col: str | None,
) -> StageMetrics:
    n = len(sub)
    reduction = 1.0 - (n / baseline_n) if baseline_n > 0 else 0.0
    if n == 0:
        return StageMetrics(
            stage=stage,
            filters_applied=tuple(filters_applied),
            n=0,
            reduction_ratio=reduction,
            expectancy=0.0,
            expectancy_se=0.0,
            hit_rate=0.0,
            post_cost_expectancy=None,
            pair_coverage=0,
            side_coverage=0,
            top_pair_concentration=0.0,
        )
    vals = sub[value_col].astype(float)
    expectancy = float(vals.mean())
    std = float(vals.std(ddof=1)) if n > 1 else 0.0
    se = std / (n ** 0.5) if n > 0 else 0.0
    hit_rate = float((vals > 0).mean())
    post = None
    if post_cost_col is not None and post_cost_col in sub.columns:
        post = float(sub[post_cost_col].astype(float).mean())
    pair_cov = int(sub[pair_col].nunique()) if pair_col and pair_col in sub.columns else 0
    side_cov = int(sub[side_col].nunique()) if side_col and side_col in sub.columns else 0
    if pair_col and pair_col in sub.columns and n > 0:
        top_conc = float(sub[pair_col].value_counts(normalize=True).iloc[0])
    else:
        top_conc = 0.0
    return StageMetrics(
        stage=stage,
        filters_applied=tuple(filters_applied),
        n=n,
        reduction_ratio=reduction,
        expectancy=expectancy,
        expectancy_se=se,
        hit_rate=hit_rate,
        post_cost_expectancy=post,
        pair_coverage=pair_cov,
        side_coverage=side_cov,
        top_pair_concentration=top_conc,
    )


def _mask_for(signals: pd.DataFrame, cols: Sequence[str]) -> pd.Series:
    """AND-combine the boolean filter columns (empty → all True)."""
    if not cols:
        return pd.Series(True, index=signals.index)
    mask = pd.Series(True, index=signals.index)
    for c in cols:
        mask &= signals[c].astype(bool)
    return mask


def filter_ablation(
    signals: pd.DataFrame,
    *,
    filter_cols: Sequence[str],
    value_col: str = "log_return",
    post_cost_col: str | None = "log_return_post_cost",
    pair_col: str | None = "instrument",
    side_col: str | None = "side",
    cumulative_order: Sequence[str] | None = None,
    min_sample: int = 20,
    edge_tolerance: float = 1e-4,
    noise_multiple: float = 1.0,
    pair_specific_threshold: float = 0.8,
) -> FilterAblationResult:
    """Decompose a staged signal table into filter-ablation diagnostics.

    ``signals`` rows are the *triggered* signals; ``filter_cols`` are boolean
    (or 0/1) columns, one per filter; ``value_col`` is the per-signal expectancy
    proxy. ``cumulative_order`` defaults to ``filter_cols`` order.

    The "adds edge / hurts edge / only reduces sample" decision is **noise
    aware**: a filter is only credited (or blamed) when its marginal expectancy
    change exceeds ``max(edge_tolerance, noise_multiple * SE)``, where ``SE`` is
    the standard error of the one-filter subset mean. Otherwise the change is
    treated as sampling noise and, if the sample shrank, flagged
    ``FILTER_ONLY_REDUCES_SAMPLE``. A filter is "pair specific" when the
    surviving one-filter sample's top pair exceeds ``pair_specific_threshold``.
    """
    if signals is None or signals.empty:
        raise ValueError("signals is empty; nothing to ablate")
    if value_col not in signals.columns:
        raise ValueError(f"signals missing value_col {value_col!r}")
    missing = [c for c in filter_cols if c not in signals.columns]
    if missing:
        raise ValueError(f"signals missing filter columns: {missing}")
    if not filter_cols:
        raise ValueError("filter_cols must be non-empty")

    order = list(cumulative_order) if cumulative_order is not None else list(filter_cols)
    bad_order = [c for c in order if c not in filter_cols]
    if bad_order:
        raise ValueError(f"cumulative_order has unknown filters: {bad_order}")

    baseline_n = len(signals)
    common = dict(
        baseline_n=baseline_n,
        value_col=value_col,
        post_cost_col=post_cost_col,
        pair_col=pair_col,
        side_col=side_col,
    )

    trigger_only = _stage_metrics(
        signals, stage="trigger_only", filters_applied=(), **common
    )

    single: list[StageMetrics] = []
    for f in filter_cols:
        sub = signals[_mask_for(signals, [f])]
        single.append(_stage_metrics(sub, stage=f"filter:{f}", filters_applied=(f,), **common))

    cumulative: list[StageMetrics] = []
    for k in range(1, len(order) + 1):
        cols = order[:k]
        sub = signals[_mask_for(signals, cols)]
        cumulative.append(
            _stage_metrics(sub, stage=f"cumulative:{k}", filters_applied=tuple(cols), **common)
        )

    leave_out: list[StageMetrics] = []
    for f in filter_cols:
        cols = [c for c in filter_cols if c != f]
        sub = signals[_mask_for(signals, cols)]
        leave_out.append(
            _stage_metrics(sub, stage=f"leave_out:{f}", filters_applied=tuple(cols), **common)
        )

    all_filters = _stage_metrics(
        signals[_mask_for(signals, list(filter_cols))],
        stage="all_filters",
        filters_applied=tuple(filter_cols),
        **common,
    )

    contributions = _contributions(
        filter_cols=filter_cols,
        trigger_only=trigger_only,
        single=single,
        leave_out=leave_out,
        all_filters=all_filters,
        min_sample=min_sample,
        edge_tolerance=edge_tolerance,
        noise_multiple=noise_multiple,
        pair_specific_threshold=pair_specific_threshold,
    )

    notes: list[str] = []
    if all_filters.n < min_sample:
        notes.append(
            f"all-filters sample is {all_filters.n} (< min_sample {min_sample}); "
            "edge estimates are high-variance"
        )

    return FilterAblationResult(
        trigger_only=trigger_only,
        all_filters=all_filters,
        single_filter=single,
        cumulative=cumulative,
        leave_one_out=leave_out,
        contributions=contributions,
        value_col=value_col,
        notes=notes,
    )


def _contributions(
    *,
    filter_cols: Sequence[str],
    trigger_only: StageMetrics,
    single: list[StageMetrics],
    leave_out: list[StageMetrics],
    all_filters: StageMetrics,
    min_sample: int,
    edge_tolerance: float,
    noise_multiple: float,
    pair_specific_threshold: float,
) -> list[FilterContribution]:
    single_by_f = {s.filters_applied[0]: s for s in single}
    leave_by_f = {lo.filters_applied: lo for lo in leave_out}
    out: list[FilterContribution] = []
    for f in filter_cols:
        s = single_by_f[f]
        marginal = s.expectancy - trigger_only.expectancy
        lo_cols = tuple(c for c in filter_cols if c != f)
        lo = leave_by_f.get(lo_cols)
        # leave_out_delta: how much expectancy the full stack loses if you drop f.
        leave_delta = (all_filters.expectancy - lo.expectancy) if lo is not None else 0.0
        edge_per_red = None if s.reduction_ratio <= 0 else marginal / s.reduction_ratio

        threshold = max(edge_tolerance, noise_multiple * s.expectancy_se)
        flags: list[str] = []
        if s.n < min_sample:
            flags.append("FILTER_TOO_SPARSE")
        if marginal > threshold:
            flags.append("FILTER_ADDS_EDGE")
        elif marginal < -threshold:
            flags.append("FILTER_HURTS_EDGE")
        elif s.reduction_ratio > 0.05:
            flags.append("FILTER_ONLY_REDUCES_SAMPLE")
        if s.top_pair_concentration >= pair_specific_threshold or s.pair_coverage == 1:
            flags.append("FILTER_PAIR_SPECIFIC_ONLY")

        out.append(
            FilterContribution(
                filter=f,
                marginal_expectancy_gain=marginal,
                leave_out_delta=leave_delta,
                reduction_ratio=s.reduction_ratio,
                edge_per_unit_reduction=edge_per_red,
                flags=flags,
            )
        )
    return out
