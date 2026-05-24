"""Cross-campaign exit-asymmetry — robustness + null comparison (Phase 3).

Sprint: ``research-exit-asymmetry-cross-campaign-001``.

Consumes the Phase 1+2 output
``research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.json``
and the same five trade ledgers, then runs the anti-overfit screens
the single-pair-probe sprint installed
(``EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md``) against every
(campaign × instrument) cell that cleared the +0.05 R floor on
``mean_R_given_time`` or ``mean_R_overall`` vs CAMPAIGN_011 — plus
some descriptive per-cell dispersion tables that don't pivot on any
single candidate.

The four probe-addendum screens, restated:
  * §A.2 LOO: leave-one-fold-out mean gap must stay ≥ +0.05 R when
    any single fold is dropped.
  * §A.3 t-stat ≥ 2: ``mean_gap / SE_mean_gap`` on the 8 paired
    fold gaps.
  * §A.4 median ≥ 0: median per-fold candidate metric ≥ 0.
  * §A.5 R-9: ``mean_of_fold_means > 0`` AND ``total_cumulative_R <
    0`` is a small-n averaging artifact — fires a red flag.

Plus three structural screens we add here:
  * Stop-rate-driven gap: per-fold gap correlates strongly with the
    candidate cell's stop-rate. If correlation |r| ≥ 0.5 the
    "positive gap" is being driven by stop-rate dispersion rather
    than by genuine exit-shape edge.
  * Time-only-positive overall-negative: ``mean_R_given_time`` is
    above-floor vs C011 but ``mean_R_overall`` is below-floor → the
    cell is exactly the small-n masking pattern.
  * Neighbour-pair / neighbour-campaign isolation: how many cells in
    the cell's row or column also clear the floor?

Output:
  * ``research/edge_discovery/studies/outputs/real/exit_asymmetry_robustness.{json,md}``

Exploratory lab output. No strategy approved. No campaign verdict
changed. ``configs/approved_strategies.yaml`` remains
``approved: []``.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.edge_discovery.real_data import (
    SEVEN_MAJORS,
    StudyInput,
    StudyProvenance,
    assert_real_data_kind,
    load_campaign_trades,
    load_campaign_walk_forward_result,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"
PHASE12_JSON = OUTPUTS / "exit_asymmetry_cross_campaign.json"

CAMPAIGNS: tuple[str, ...] = (
    "CAMPAIGN_010_session_breakout",
    "CAMPAIGN_011_random_entry_anchor",
    "CAMPAIGN_012_regime_switcher_atr_percentile",
    "CAMPAIGN_013_cross_pair_currency_strength_rotation",
    "CAMPAIGN_014_calendar_event_window_anomaly",
)
NULL_CAMPAIGN = "CAMPAIGN_011_random_entry_anchor"

MATERIAL_GAP_R = 0.05
T_STAT_THRESHOLD = 2.0
MAJORITY_FRACTION = 5 / 8  # probe-addendum standard
MIN_PAIRED_FOLDS_FOR_SCREEN = 6  # below this the screens are too noisy


# ---------------------------------------------------------------------------
# Per-cell, per-fold metric extraction
# ---------------------------------------------------------------------------


def _load_all_trades() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for name in CAMPAIGNS:
        df = load_campaign_trades(REPO_ROOT / "backtests" / name)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def _per_fold_cell_metrics(
    df: pd.DataFrame, campaign: str, instrument: str
) -> pd.DataFrame:
    """One row per fold for a given (campaign, instrument), with the
    metrics we screen on: mean_r_overall, mean_r_given_time,
    mean_r_given_stop, stop_rate, time_rate, n_trades."""
    sub = df[(df["campaign_name"] == campaign) & (df["instrument"] == instrument)]
    rows: list[dict[str, object]] = []
    for fold_idx, g in sub.groupby("fold_index", sort=True, observed=True):
        n = len(g)
        if n == 0:
            continue
        n_stop = int((g["exit_reason"] == "stop").sum())
        n_time = int((g["exit_reason"] == "time").sum())
        stop_r = g.loc[g["exit_reason"] == "stop", "r_multiple"]
        time_r = g.loc[g["exit_reason"] == "time", "r_multiple"]
        rows.append({
            "fold_index": int(fold_idx),
            "n_trades": n,
            "n_stop": n_stop,
            "n_time": n_time,
            "stop_rate": n_stop / n,
            "time_rate": n_time / n,
            "mean_r_overall": float(g["r_multiple"].mean()),
            "sum_r_overall": float(g["r_multiple"].sum()),
            "mean_r_given_stop": float(stop_r.mean()) if not stop_r.empty else float("nan"),
            "mean_r_given_time": float(time_r.mean()) if not time_r.empty else float("nan"),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Probe-addendum screens
# ---------------------------------------------------------------------------


def _screen_above_floor_cell(
    df: pd.DataFrame,
    *,
    campaign: str,
    instrument: str,
    metric: str,
) -> dict[str, object]:
    """Apply the probe-addendum §A.2/A.3/A.4/A.5 screens to one
    (campaign, instrument, metric) cell.

    ``metric`` is one of ``mean_r_overall`` or ``mean_r_given_time``.
    The null cell is always CAMPAIGN_011 × the same instrument.
    Per-fold gaps are computed against the matched fold of the null.
    """
    cand_fold = _per_fold_cell_metrics(df, campaign, instrument)
    null_fold = _per_fold_cell_metrics(df, NULL_CAMPAIGN, instrument)
    merged = cand_fold.merge(
        null_fold,
        on="fold_index",
        suffixes=("_cand", "_null"),
        how="inner",
    )
    gap = merged[f"{metric}_cand"] - merged[f"{metric}_null"]
    gap_valid = gap.dropna()
    n_folds = len(gap_valid)
    mean_gap = float(gap_valid.mean()) if n_folds else float("nan")
    median_gap = float(gap_valid.median()) if n_folds else float("nan")
    std_gap = float(gap_valid.std(ddof=1)) if n_folds > 1 else float("nan")
    se_mean = std_gap / np.sqrt(n_folds) if n_folds > 1 else float("nan")
    t_stat = mean_gap / se_mean if se_mean and not np.isnan(se_mean) and se_mean > 0 else float("nan")

    # §A.2 LOO
    loo_values: list[float] = []
    for drop_idx in gap_valid.index:
        loo = gap_valid.drop(drop_idx)
        loo_values.append(float(loo.mean()))
    min_loo = float(np.min(loo_values)) if loo_values else float("nan")
    max_loo = float(np.max(loo_values)) if loo_values else float("nan")

    # §A.4 median candidate per-fold ≥ 0
    median_cand = float(merged[f"{metric}_cand"].median())
    median_cand_pos = bool(median_cand >= 0)
    folds_positive_on_metric = int((merged[f"{metric}_cand"] > 0).sum())
    folds_positive_gap = int((gap_valid > 0).sum())

    # §A.5 R-9 (mean-of-means positive while cumulative-R negative)
    # For exit-time-specific R-9, evaluate the candidate's mean-of-
    # fold-means of `mean_r_overall` vs the candidate's `sum_r_overall`.
    cand_full = df[(df["campaign_name"] == campaign) & (df["instrument"] == instrument)]
    mean_of_means_overall = float(cand_fold["mean_r_overall"].mean()) if not cand_fold.empty else float("nan")
    cumulative_r_overall = float(cand_full["r_multiple"].sum())
    r9_fires = mean_of_means_overall > 0 and cumulative_r_overall < 0

    # Stop-rate-driven gap correlation
    stop_rate_corr = float("nan")
    if n_folds > 1:
        stop_rate_series = merged["stop_rate_cand"]
        if stop_rate_series.std(ddof=0) > 0 and gap_valid.std(ddof=0) > 0:
            stop_rate_corr = float(stop_rate_series.corr(gap))

    # Probe-addendum's 5/8 majority threshold scales with paired-fold
    # count: ``ceil(5/8 * n_folds_paired)``. For n_folds_paired = 8 this
    # is the original 5 / 8. For smaller paired counts (some folds lack
    # the exit-reason class in the null or candidate) the threshold
    # tightens proportionally.
    majority_threshold = max(1, int(np.ceil(MAJORITY_FRACTION * n_folds))) if n_folds > 0 else 1
    enough_paired_folds = n_folds >= MIN_PAIRED_FOLDS_FOR_SCREEN

    screens = {
        "enough_paired_folds_for_screen": bool(enough_paired_folds),
        "loo_min_above_floor": bool(min_loo >= MATERIAL_GAP_R) if not np.isnan(min_loo) else False,
        "t_stat_at_or_above_2": bool(t_stat >= T_STAT_THRESHOLD) if not np.isnan(t_stat) else False,
        "median_per_fold_cand_non_negative": median_cand_pos,
        "r9_does_not_fire": bool(not r9_fires),
        "majority_folds_positive_on_metric": bool(folds_positive_on_metric >= majority_threshold),
        "majority_folds_positive_gap": bool(folds_positive_gap >= majority_threshold),
        "stop_rate_driven_corr_below_0_5": bool(abs(stop_rate_corr) < 0.5) if not np.isnan(stop_rate_corr) else False,
    }
    failures = [name for name, ok in screens.items() if not ok]
    if not enough_paired_folds:
        # Too few paired folds to fire the §A.2 / §A.3 screens
        # reliably — record as INSUFFICIENT_DATA per Phase 0 plan §8.
        classification = "INSUFFICIENT_DATA"
    elif failures:
        classification = (
            "ISOLATED_SELECTED_CELL_ARTIFACT"
            if len(failures) >= 2
            else "PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL"
        )
    else:
        classification = "PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL"

    return {
        "campaign": campaign,
        "instrument": instrument,
        "metric": metric,
        "n_folds_paired": n_folds,
        "mean_gap_r": mean_gap,
        "median_gap_r": median_gap,
        "std_gap_r": std_gap,
        "se_mean_gap_r": se_mean,
        "t_stat": t_stat,
        "min_loo_mean_gap_r": min_loo,
        "max_loo_mean_gap_r": max_loo,
        "loo_values_by_dropped_fold": [float(v) for v in loo_values],
        "median_cand_per_fold": median_cand,
        "folds_positive_on_metric": folds_positive_on_metric,
        "folds_positive_gap": folds_positive_gap,
        "mean_of_fold_means_overall": mean_of_means_overall,
        "cumulative_r_overall": cumulative_r_overall,
        "r9_fires": bool(r9_fires),
        "stop_rate_gap_correlation": stop_rate_corr,
        "majority_threshold_at_n_folds": majority_threshold,
        "screens": screens,
        "failures": failures,
        "classification": classification,
    }


# ---------------------------------------------------------------------------
# Aggregate dispersion + R-9 sweep (descriptive, no classification)
# ---------------------------------------------------------------------------


def _per_campaign_r9_sweep(df: pd.DataFrame) -> list[dict[str, object]]:
    """For each campaign × pair: compute mean-of-fold-means and
    cumulative-R; mark R-9 fires when mean>0 and cumulative<0."""
    rows: list[dict[str, object]] = []
    for campaign in CAMPAIGNS:
        for pair in SEVEN_MAJORS:
            cell_fold = _per_fold_cell_metrics(df, campaign, pair)
            if cell_fold.empty:
                continue
            cell_full = df[(df["campaign_name"] == campaign) & (df["instrument"] == pair)]
            mean_of_means = float(cell_fold["mean_r_overall"].mean())
            cum = float(cell_full["r_multiple"].sum())
            rows.append({
                "campaign": campaign,
                "instrument": pair,
                "n_folds_with_trades": len(cell_fold),
                "mean_of_fold_means_overall": mean_of_means,
                "cumulative_r_overall": cum,
                "r9_fires": bool(mean_of_means > 0 and cum < 0),
                "median_per_fold_mean_r_overall": float(cell_fold["mean_r_overall"].median()),
                "stop_rate_min": float(cell_fold["stop_rate"].min()),
                "stop_rate_max": float(cell_fold["stop_rate"].max()),
                "stop_rate_std": float(cell_fold["stop_rate"].std(ddof=0)),
            })
    return rows


def _per_campaign_fold_dispersion(df: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for campaign in CAMPAIGNS:
        for pair in SEVEN_MAJORS:
            cell_fold = _per_fold_cell_metrics(df, campaign, pair)
            if cell_fold.empty:
                continue
            mean_r_std = float(cell_fold["mean_r_overall"].std(ddof=0))
            stop_rate_std = float(cell_fold["stop_rate"].std(ddof=0))
            rows.append({
                "campaign": campaign,
                "instrument": pair,
                "n_folds_with_trades": len(cell_fold),
                "mean_r_overall_std": mean_r_std,
                "stop_rate_std": stop_rate_std,
            })
    return rows


# ---------------------------------------------------------------------------
# Bucket counters
# ---------------------------------------------------------------------------


def _classify_grid_cells(r9_sweep: list[dict[str, object]]) -> dict[str, int]:
    counters: dict[str, int] = {
        "r9_fires_count": 0,
        "median_per_fold_mean_r_overall_negative": 0,
        "cumulative_negative": 0,
        "mean_of_means_positive_cells": 0,
        "total_cells": 0,
    }
    for row in r9_sweep:
        counters["total_cells"] += 1
        if row["r9_fires"]:
            counters["r9_fires_count"] += 1
        if float(row["median_per_fold_mean_r_overall"]) < 0:
            counters["median_per_fold_mean_r_overall_negative"] += 1
        if float(row["cumulative_r_overall"]) < 0:
            counters["cumulative_negative"] += 1
        if float(row["mean_of_fold_means_overall"]) > 0:
            counters["mean_of_means_positive_cells"] += 1
    return counters


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def _build_provenance() -> StudyProvenance:
    inputs: list[StudyInput] = []
    earliest: pd.Timestamp | None = None
    latest: pd.Timestamp | None = None
    for name in CAMPAIGNS:
        result = load_campaign_walk_forward_result(REPO_ROOT / "backtests" / name)
        inputs.append(
            StudyInput(
                kind="campaign_walk_forward_results",
                path=result.source_path,
                sha256=result.source_sha256,
                rows=len(result.fold_metrics),
                extra={
                    "overall_verdict": result.overall_verdict,
                    "strategy_evidence": result.strategy_evidence,
                },
            )
        )
        plan = result.plan
        if isinstance(plan, dict):
            for top_key in ("universe_start", "universe_end"):
                val = plan.get(top_key)
                if val:
                    ts = pd.Timestamp(val, tz="UTC")
                    if top_key == "universe_start":
                        earliest = ts if earliest is None or ts < earliest else earliest
                    else:
                        latest = ts if latest is None or ts > latest else latest
    # Add the Phase 1+2 JSON as an input (the file we're consuming).
    if PHASE12_JSON.is_file():
        import hashlib
        sha = hashlib.sha256(PHASE12_JSON.read_bytes()).hexdigest()
        inputs.append(
            StudyInput(
                kind="phase12_extraction_json",
                path=str(PHASE12_JSON),
                sha256=sha,
                rows=None,
            )
        )
    prov = StudyProvenance(
        data_kind="real",
        inputs=inputs,
        date_coverage={
            "start_utc": str(earliest) if earliest is not None else "",
            "end_utc": str(latest) if latest is not None else "",
        },
        pair_universe=list(SEVEN_MAJORS),
        limitations=[
            "Robustness screens consume per-fold means; per-fold n is small",
            "(≤ 100 trades typical) so screens that depend on per-fold",
            "std (t-stat, LOO) are intrinsically noisy.",
            "Any 'PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL' classification",
            "explicitly does NOT promote a candidate. It records an",
            "observation; the prior single-pair-probe addendum §A.1 makes",
            "explicit that a future proposal must show ≥ 2 above-floor",
            "cells in a multi-cell grid OR ≥ 1 LOO-stable cell - the",
            "lab is not staffing follow-ups on partial-signal observations.",
        ],
        exploratory_only=True,
    )
    assert_real_data_kind(prov)
    return prov


# ---------------------------------------------------------------------------
# Output rendering
# ---------------------------------------------------------------------------


def _build_markdown(payload: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("# Cross-Campaign Exit-Asymmetry — Phase 3 Robustness")
    lines.append("")
    lines.append("**Sprint:** `research-exit-asymmetry-cross-campaign-001`")
    lines.append("**Phase:** 3 (robustness + null comparison)")
    lines.append("**Date:** 2026-05-24")
    lines.append("")
    lines.append("> Exploratory lab output. **No strategy approved.** **No campaign**")
    lines.append("> **verdict changed.** Paper / demo / live remain blocked.")
    lines.append("> CAMPAIGN_010 - CAMPAIGN_014 remain REJECT-anchored.")
    lines.append("")
    lines.append("## R-9 sweep across the 5 × 7 = 35 (campaign, pair) grid")
    lines.append("")
    bc = payload["bucket_counters"]
    lines.append(f"- Total (campaign, pair) cells evaluated: **{bc['total_cells']}**")
    lines.append(f"- Cells with `mean_of_fold_means_overall > 0`: **{bc['mean_of_means_positive_cells']}**")
    lines.append(f"- Cells with `cumulative_r_overall < 0`: **{bc['cumulative_negative']}**")
    lines.append(f"- **R-9 fires** (mean>0 AND cumulative<0): **{bc['r9_fires_count']}** out of {bc['total_cells']}")
    lines.append(f"- Cells with negative median per-fold mean_R: **{bc['median_per_fold_mean_r_overall_negative']}**")
    lines.append("")
    lines.append("R-9 fires on **the cells whose mean-of-fold-means looked positive while their**")
    lines.append("**trade-level cumulative R was negative** — by construction these are small-n")
    lines.append("averaging artifacts. They are surfaced for the lab's reading and are **not**")
    lines.append("proposed as candidate strategies.")
    lines.append("")
    lines.append("### Cells where R-9 fires")
    lines.append("")
    r9_fires = [r for r in payload["r9_sweep"] if r["r9_fires"]]
    if r9_fires:
        lines.append("| campaign | instrument | mean_of_fold_means_overall | cumulative_r_overall | median_per_fold_R | stop_rate σ |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for r in r9_fires:
            lines.append(
                f"| {r['campaign']} | {r['instrument']} "
                f"| {r['mean_of_fold_means_overall']:+.4f} "
                f"| {r['cumulative_r_overall']:+.3f} "
                f"| {r['median_per_fold_mean_r_overall']:+.4f} "
                f"| {r['stop_rate_std']:.4f} |"
            )
    else:
        lines.append("None.")
    lines.append("")
    lines.append("## Per-(campaign × pair) fold dispersion of stop_rate and mean_R_overall")
    lines.append("")
    lines.append("(Selected highlights only; full table in JSON.)")
    lines.append("")
    disp = payload["per_campaign_fold_dispersion"]
    # Sort by stop_rate_std descending and show top-10
    disp_sorted = sorted(disp, key=lambda r: r["stop_rate_std"], reverse=True)[:10]
    lines.append("| campaign | instrument | stop_rate σ | mean_R_overall σ |")
    lines.append("|---|---|---:|---:|")
    for r in disp_sorted:
        lines.append(
            f"| {r['campaign']} | {r['instrument']} "
            f"| {r['stop_rate_std']:.4f} | {r['mean_r_overall_std']:.4f} |"
        )
    lines.append("")
    lines.append("## Above-floor-cell screens")
    lines.append("")
    screened = payload["screened_cells"]
    if not screened:
        lines.append("No cells cleared the +0.05 R floor on `mean_R_overall`; no cells were")
        lines.append("screened for that metric. See `mean_R_given_time` screens below for the")
        lines.append("one cell that cleared the floor on that metric (CAMPAIGN_013 × EUR_USD).")
        lines.append("")
    for cell in screened:
        lines.append(f"### {cell['campaign']} × {cell['instrument']} on `{cell['metric']}`")
        lines.append("")
        lines.append(f"**Classification:** `{cell['classification']}`")
        lines.append("")
        lines.append(f"- n_folds_paired: {cell['n_folds_paired']}")
        lines.append(f"- mean_gap_r: **{cell['mean_gap_r']:+.4f}** R")
        lines.append(f"- median_gap_r: {cell['median_gap_r']:+.4f} R")
        lines.append(f"- se_mean_gap_r: {cell['se_mean_gap_r']:.4f} R")
        lines.append(f"- t_stat: **{cell['t_stat']:.3f}**")
        lines.append(f"- min_loo_mean_gap_r: **{cell['min_loo_mean_gap_r']:+.4f}** R")
        lines.append(f"- max_loo_mean_gap_r: {cell['max_loo_mean_gap_r']:+.4f} R")
        lines.append(f"- median per-fold candidate metric: {cell['median_cand_per_fold']:+.4f}")
        lines.append(f"- folds positive on metric (≥ 5/8): {cell['folds_positive_on_metric']}")
        lines.append(f"- folds with positive gap (≥ 5/8): {cell['folds_positive_gap']}")
        lines.append(f"- mean_of_fold_means_overall: {cell['mean_of_fold_means_overall']:+.4f}")
        lines.append(f"- cumulative_r_overall: {cell['cumulative_r_overall']:+.3f}")
        lines.append(f"- R-9 fires: **{cell['r9_fires']}**")
        lines.append(f"- stop_rate-gap correlation: {cell['stop_rate_gap_correlation']:.3f}")
        lines.append("")
        lines.append("Screens:")
        for name, ok in cell["screens"].items():
            lines.append(f"  - `{name}`: {'PASS' if ok else 'NOT MET'}")
        if cell["failures"]:
            lines.append("")
            lines.append(f"**Failures ({len(cell['failures'])}):** {cell['failures']}")
        lines.append("")
        lines.append("LOO values by dropped fold:")
        for i, v in enumerate(cell["loo_values_by_dropped_fold"]):
            lines.append(f"  - dropping fold-paired index {i}: {v:+.4f}")
        lines.append("")
    lines.append("## Provenance")
    lines.append("")
    prov = payload["provenance"]
    lines.append(f"- data_kind: `{prov['data_kind']}`")
    lines.append(f"- pair_universe: `{prov['pair_universe']}`")
    lines.append(f"- date_coverage: {prov['date_coverage']['start_utc']} → {prov['date_coverage']['end_utc']}")
    lines.append(f"- inputs ({len(prov['inputs'])}):")
    for inp in prov["inputs"]:
        lines.append(f"  - {inp['kind']} · {inp['path']} · sha256 `{inp['sha256'][:12]}...`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("This output **does not approve** any strategy and **does not change**")
    lines.append("any campaign verdict. `PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL` is a")
    lines.append("descriptive record of the partial-signal pattern the single-pair-probe")
    lines.append("sprint already required ≥ 2 above-floor cells (or LOO stability) to override.")
    return "\n".join(lines) + "\n"


def main() -> dict[str, object]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    prov = _build_provenance()
    trades = _load_all_trades()

    # Load the Phase 1+2 above-floor list.
    phase12 = json.loads(PHASE12_JSON.read_text(encoding="utf-8"))
    above = phase12.get("above_floor_cells_vs_null", [])

    screened: list[dict[str, object]] = []
    for cell in above:
        for metric_field, metric_name in (
            ("above_floor_on_overall", "mean_r_overall"),
            ("above_floor_on_time_only", "mean_r_given_time"),
        ):
            if cell.get(metric_field):
                screened.append(_screen_above_floor_cell(
                    trades,
                    campaign=cell["campaign_name"],
                    instrument=cell["instrument"],
                    metric=metric_name,
                ))

    r9_sweep = _per_campaign_r9_sweep(trades)
    fold_dispersion = _per_campaign_fold_dispersion(trades)
    bucket = _classify_grid_cells(r9_sweep)

    payload: dict[str, object] = {
        "verdict_word_ban_acknowledged": True,
        "sprint_id": "research-exit-asymmetry-cross-campaign-001",
        "phase": "3",
        "screened_cells": screened,
        "r9_sweep": r9_sweep,
        "per_campaign_fold_dispersion": fold_dispersion,
        "bucket_counters": bucket,
        "provenance": prov.to_dict(),
        "refusals": {
            "approves_strategy": False,
            "changes_campaign_verdict": False,
            "proposes_parameter_tune": False,
            "writes_to_approved_strategies_yaml": False,
        },
    }
    out_json = OUTPUTS / "exit_asymmetry_robustness.json"
    out_md = OUTPUTS / "exit_asymmetry_robustness.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
    out_md.write_text(_build_markdown(payload), encoding="utf-8")
    return payload


if __name__ == "__main__":
    main()
