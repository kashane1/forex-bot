"""Single-pair probe robustness — pressure-test the EUR_USD /
CAMPAIGN_012 +0.0950 R cell.

Phase 2 of the research-edge-discovery-lab-single-pair-probe-001
sprint. Runs every anti-overfit check defined in §3 of
SINGLE_PAIR_PROBE_001_PLAN.md and classifies the cell per §4. Reads
the Phase 1 extraction JSON plus the committed campaign artifacts.

Outputs:
- research/edge_discovery/studies/outputs/real/
  probe_robustness_eur_usd_c012.{json,md}

Exploratory lab output. Not strategy evidence. CAMPAIGN_012 remains
REJECT.
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
    fold_pair_summaries_to_frame,
    load_campaign_fold_pair_summaries,
    load_campaign_trades,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs" / "real"

PAIR = "EUR_USD"
CANDIDATE = "CAMPAIGN_012_regime_switcher_atr_percentile"
NULL = "CAMPAIGN_011_random_entry_anchor"
OTHER_CANDIDATES = (
    "CAMPAIGN_010_session_breakout",
    "CAMPAIGN_013_cross_pair_currency_strength_rotation",
    "CAMPAIGN_014_calendar_event_window_anomaly",
)
PHASE1_INPUT = OUTPUTS / "probe_single_pair_eur_usd_c012.json"
MATERIAL_GAP_R = 0.05

# 2x cost stress assumption: each spread_paid_pips contributes a
# per-trade cost in R units approximately equal to (2 * spread_pips /
# stop_distance_in_pips). We don't have stop distances in the
# committed schema, but average_spread_paid_pips × a typical EUR_USD
# stop of ~50 pips gives a per-trade cost ratio. For the
# 2× stress we subtract (extra_spread / avg_stop_pips) R per trade,
# where extra_spread = average_spread_paid_pips × 1.0 (the doubling)
# and avg_stop_pips is a conservative 50.
ASSUMED_EUR_USD_STOP_PIPS = 50.0


def _load_per_fold_for_pair(campaign_name: str, pair: str) -> pd.DataFrame:
    summaries = load_campaign_fold_pair_summaries(REPO_ROOT / "backtests" / campaign_name)
    df = fold_pair_summaries_to_frame(summaries)
    return df[df["instrument"] == pair].sort_values("fold_index").reset_index(drop=True)


def _per_fold_gap(cand: pd.DataFrame, null: pd.DataFrame) -> pd.DataFrame:
    merged = pd.merge(
        cand[["fold_index", "metric_expectancy_r", "metric_trade_count",
              "metric_average_spread_paid_pips"]],
        null[["fold_index", "metric_expectancy_r"]].rename(
            columns={"metric_expectancy_r": "null_metric_expectancy_r"}
        ),
        on="fold_index", how="outer",
    ).sort_values("fold_index").reset_index(drop=True)
    merged["per_fold_gap_r"] = merged["metric_expectancy_r"] - merged["null_metric_expectancy_r"]
    return merged


def _check_loo(merged: pd.DataFrame) -> dict[str, object]:
    """Leave-one-fold-out resamples. For each fold k, drop fold k
    from the candidate and from the null, then recompute the mean
    gap. Returns a list of per-LOO means, the LOO range, and the
    sign-stability count."""
    gaps = merged["per_fold_gap_r"].to_numpy(dtype=float)
    n = len(gaps)
    loo_means: list[dict[str, float | int]] = []
    above_floor = 0
    below_zero = 0
    for k in range(n):
        mask = np.ones(n, dtype=bool)
        mask[k] = False
        m = float(gaps[mask].mean())
        loo_means.append({"dropped_fold": int(merged.iloc[k]["fold_index"]), "mean_gap_r": m})
        if m >= MATERIAL_GAP_R:
            above_floor += 1
        if m < 0:
            below_zero += 1
    return {
        "per_loo": loo_means,
        "min_loo_mean_gap": float(min(d["mean_gap_r"] for d in loo_means)),
        "max_loo_mean_gap": float(max(d["mean_gap_r"] for d in loo_means)),
        "n_loo_above_material_floor": int(above_floor),
        "n_loo_below_zero": int(below_zero),
        "all_loo_above_floor": bool(above_floor == n),
    }


def _check_cost_stress_2x(merged: pd.DataFrame, trades: pd.DataFrame) -> dict[str, float]:
    """2× cost stress on the candidate per-fold mean R. We compute
    per-trade extra cost = (avg_spread_pips × 1.0) / 50 (the assumed
    stop distance) and subtract that from each trade's r_multiple.
    Then we recompute per-fold candidate mean R, the new mean, and
    the new gap to the (unchanged) null."""
    trades = trades.copy()
    trades["spread_paid_pips"] = trades["spread_paid_pips"].astype(float)
    trades["r_stress_2x"] = trades["r_multiple"].astype(float) - (
        trades["spread_paid_pips"] / ASSUMED_EUR_USD_STOP_PIPS
    )
    per_fold_stress = (
        trades.groupby("fold_index")["r_stress_2x"].mean().reset_index()
        .rename(columns={"r_stress_2x": "stress_mean_r", "fold_index": "fold_index"})
    )
    m2 = pd.merge(merged, per_fold_stress, on="fold_index", how="left")
    m2["stress_gap_r"] = m2["stress_mean_r"] - m2["null_metric_expectancy_r"]
    return {
        "assumed_stop_pips": ASSUMED_EUR_USD_STOP_PIPS,
        "per_trade_extra_cost_r_avg": float(
            (trades["spread_paid_pips"] / ASSUMED_EUR_USD_STOP_PIPS).mean()
        ),
        "candidate_stress_mean_r": float(m2["stress_mean_r"].mean()),
        "stress_mean_gap_r": float(m2["stress_gap_r"].mean()),
        "stress_median_gap_r": float(m2["stress_gap_r"].median()),
        "stress_n_folds_positive_gap": int((m2["stress_gap_r"] > 0).sum()),
    }


def _check_neighboring_pairs(null_eur: pd.DataFrame) -> list[dict[str, object]]:
    """For each non-EUR pair, compute the same C012 vs C011 gap and
    report it. EUR_USD's status is appended too for the side-by-side."""
    cand_summaries = load_campaign_fold_pair_summaries(REPO_ROOT / "backtests" / CANDIDATE)
    null_summaries = load_campaign_fold_pair_summaries(REPO_ROOT / "backtests" / NULL)
    cand_df = fold_pair_summaries_to_frame(cand_summaries)
    null_df = fold_pair_summaries_to_frame(null_summaries)
    rows: list[dict[str, object]] = []
    for pair in SEVEN_MAJORS:
        cand_pair = cand_df[cand_df["instrument"] == pair].sort_values("fold_index")
        null_pair = null_df[null_df["instrument"] == pair].sort_values("fold_index")
        cand_mean = float(cand_pair["metric_expectancy_r"].mean())
        null_mean = float(null_pair["metric_expectancy_r"].mean())
        gap = cand_mean - null_mean
        cand_median = float(cand_pair["metric_expectancy_r"].median())
        rows.append({
            "pair": pair,
            "candidate_mean_r": cand_mean,
            "candidate_median_r": cand_median,
            "null_mean_r": null_mean,
            "mean_gap_r": gap,
            "above_material_floor": bool(gap >= MATERIAL_GAP_R),
            "candidate_n_folds_positive": int((cand_pair["metric_expectancy_r"] > 0).sum()),
            "candidate_total_trades": int(cand_pair["metric_trade_count"].sum()),
        })
    return rows


def _check_neighboring_candidates(pair: str) -> list[dict[str, object]]:
    """For each candidate in (C012, C010, C013, C014), compute the
    EUR_USD gap vs C011 EUR_USD null and report."""
    null_summaries = load_campaign_fold_pair_summaries(REPO_ROOT / "backtests" / NULL)
    null_df = fold_pair_summaries_to_frame(null_summaries)
    null_pair = null_df[null_df["instrument"] == pair].sort_values("fold_index")
    null_mean = float(null_pair["metric_expectancy_r"].mean())
    rows: list[dict[str, object]] = []
    for c in (CANDIDATE,) + OTHER_CANDIDATES:
        cand_summaries = load_campaign_fold_pair_summaries(REPO_ROOT / "backtests" / c)
        cand_df = fold_pair_summaries_to_frame(cand_summaries)
        cand_pair = cand_df[cand_df["instrument"] == pair].sort_values("fold_index")
        cand_mean = float(cand_pair["metric_expectancy_r"].mean())
        cand_median = float(cand_pair["metric_expectancy_r"].median())
        gap = cand_mean - null_mean
        rows.append({
            "candidate": c,
            "candidate_mean_r": cand_mean,
            "candidate_median_r": cand_median,
            "null_mean_r": null_mean,
            "mean_gap_r": gap,
            "above_material_floor": bool(gap >= MATERIAL_GAP_R),
            "candidate_n_folds_positive": int((cand_pair["metric_expectancy_r"] > 0).sum()),
            "candidate_total_trades": int(cand_pair["metric_trade_count"].sum()),
        })
    return rows


def _classify(
    phase1: dict[str, object],
    loo: dict[str, object],
    cost: dict[str, float],
    neighbor_pairs: list[dict[str, object]],
    neighbor_cands: list[dict[str, object]],
) -> dict[str, object]:
    """Apply the plan's §4 classification rules."""
    gap = phase1["gap"]
    cand = phase1["candidate"]
    n_folds_positive = int(cand["n_folds_positive_expectancy"])
    median_per_fold = float(cand["median_expectancy_r"])
    mean_gap = float(gap["mean_gap_r"])
    se_mean_gap = float(gap["se_mean_gap"])
    n_folds_pos_gap = int(gap["n_folds_with_positive_gap"])

    # Single-fold dominance: signed share. The Phase 1 report's
    # top_fold_share_of_abs_total uses |total| as the denominator,
    # which goes to >100 % when total is negative. The cleaner check
    # is: how much of the absolute sum of per-fold cumulative R
    # comes from the single best fold?
    dom = phase1["candidate_dominance"]
    fold_cum_r = {int(k): float(v) for k, v in dom["fold_cum_r"].items()}
    abs_total = sum(abs(v) for v in fold_cum_r.values()) or 1e-12
    top_fold_share_abs = (
        max(abs(v) for v in fold_cum_r.values()) / abs_total
    )
    top_fold_signed_share = float(dom["top_fold_share_of_abs_total"])

    # 2× cost stress
    stress_mean_gap = float(cost["stress_mean_gap_r"])
    stress_n_pos = int(cost["stress_n_folds_positive_gap"])

    # Neighbor pair coherence: how many of the 7 majors have C012
    # above the material floor?
    n_neighbor_pairs_above = sum(
        1 for r in neighbor_pairs if r["above_material_floor"]
    )

    # Neighbor candidate coherence: how many candidates (out of 4)
    # have EUR_USD above the material floor?
    n_neighbor_cands_above = sum(
        1 for r in neighbor_cands if r["above_material_floor"]
    )

    # Apply §4 rules.
    failures: list[str] = []
    if loo["min_loo_mean_gap"] < MATERIAL_GAP_R:
        failures.append("LOO_drops_below_floor")
    if n_folds_positive <= 4:
        failures.append("at_most_4_of_8_folds_positive")
    if median_per_fold < 0:
        failures.append("median_per_fold_expectancy_negative")
    if top_fold_share_abs > 0.40:
        failures.append("top_fold_share_above_40pct")
    if se_mean_gap >= mean_gap:
        failures.append("SE_gap_exceeds_mean_gap")
    if stress_mean_gap < MATERIAL_GAP_R:
        failures.append("2x_cost_stress_drops_below_floor")

    robust_criteria = []
    if loo["all_loo_above_floor"]:
        robust_criteria.append("LOO_all_above_floor")
    if n_folds_pos_gap >= 5:
        robust_criteria.append("at_least_5_folds_positive_gap")
    if stress_mean_gap >= MATERIAL_GAP_R:
        robust_criteria.append("2x_cost_stress_above_floor")
    if top_fold_share_abs <= 0.40:
        robust_criteria.append("top_fold_share_at_or_below_40pct")
    if se_mean_gap > 0 and (mean_gap / se_mean_gap) >= 2.0:
        robust_criteria.append("gap_at_least_2_SE_above_zero")

    if failures:
        classification = "SELECTED_CELL_ARTIFACT" if any(f in failures for f in (
            "median_per_fold_expectancy_negative",
            "LOO_drops_below_floor",
            "top_fold_share_above_40pct",
            "SE_gap_exceeds_mean_gap",
            "at_most_4_of_8_folds_positive",
        )) else "WEAK_UNSTABLE_SIGNAL"
    elif len(robust_criteria) == 5:
        classification = "ROBUST_EXPLORATORY_SIGNAL"
    else:
        classification = "WEAK_UNSTABLE_SIGNAL"

    return {
        "classification": classification,
        "failures": failures,
        "robust_criteria_met": robust_criteria,
        "summary": {
            "n_folds_positive": n_folds_positive,
            "median_per_fold_expectancy_r": median_per_fold,
            "mean_gap_r": mean_gap,
            "se_mean_gap": se_mean_gap,
            "t_stat_approx": float(mean_gap / se_mean_gap) if se_mean_gap else float("nan"),
            "loo_min_gap_r": float(loo["min_loo_mean_gap"]),
            "loo_max_gap_r": float(loo["max_loo_mean_gap"]),
            "loo_n_below_zero": int(loo["n_loo_below_zero"]),
            "top_fold_share_of_abs_sum": float(top_fold_share_abs),
            "top_fold_signed_share_of_total": float(top_fold_signed_share),
            "stress_mean_gap_r": stress_mean_gap,
            "stress_n_folds_positive_gap": stress_n_pos,
            "n_neighbor_pairs_above_floor": int(n_neighbor_pairs_above),
            "n_neighbor_candidates_above_floor_on_eur_usd": int(n_neighbor_cands_above),
        },
    }


def run() -> Path:
    if not PHASE1_INPUT.is_file():
        raise FileNotFoundError(
            f"Phase 1 extraction JSON not found: {PHASE1_INPUT}. "
            "Run probe_single_pair_eur_usd_c012.py first."
        )
    with PHASE1_INPUT.open(encoding="utf-8") as fh:
        phase1 = json.load(fh)

    cand_per_fold = _load_per_fold_for_pair(CANDIDATE, PAIR)
    null_per_fold = _load_per_fold_for_pair(NULL, PAIR)
    merged = _per_fold_gap(cand_per_fold, null_per_fold)
    cand_trades = load_campaign_trades(REPO_ROOT / "backtests" / CANDIDATE, instruments=[PAIR])

    loo = _check_loo(merged)
    cost = _check_cost_stress_2x(merged, cand_trades)
    neighbor_pairs = _check_neighboring_pairs(null_per_fold)
    neighbor_cands = _check_neighboring_candidates(PAIR)
    cls = _classify(phase1, loo, cost, neighbor_pairs, neighbor_cands)

    prov = StudyProvenance(
        data_kind="real",
        inputs=[
            StudyInput(
                kind="probe_phase1_extraction",
                path=str(PHASE1_INPUT.relative_to(REPO_ROOT)),
                sha256="(consumed verbatim; see Phase 1 inputs for upstream sha256s)",
                rows=int(phase1["candidate"]["total_trades"]),
                extra={"pair": PAIR},
            ),
            StudyInput(
                kind="campaign_fold_summaries",
                path=f"backtests/{CANDIDATE}/folds",
                sha256="(56 per-fold per-pair JSON bundle)",
                rows=56,
                extra={"campaign_name": CANDIDATE, "role": "candidate"},
            ),
            StudyInput(
                kind="campaign_fold_summaries",
                path=f"backtests/{NULL}/folds",
                sha256="(56 per-fold per-pair JSON bundle)",
                rows=56,
                extra={"campaign_name": NULL, "role": "null"},
            ),
        ] + [
            StudyInput(
                kind="campaign_fold_summaries",
                path=f"backtests/{c}/folds",
                sha256="(56 per-fold per-pair JSON bundle)",
                rows=56,
                extra={"campaign_name": c, "role": "neighbor_candidate"},
            )
            for c in OTHER_CANDIDATES
        ],
        date_coverage=phase1["provenance"]["date_coverage"],
        pair_universe=list(SEVEN_MAJORS),
        limitations=[
            "2× cost stress assumes a notional EUR_USD stop distance "
            f"of {ASSUMED_EUR_USD_STOP_PIPS} pips and doubles the observed "
            "spread; this is a coarse stress, not the full lab cost overlay.",
            "Leave-one-fold-out gives 8 paired-difference resamples; "
            "with only 8 folds the LOO distribution is itself noisy.",
            "Classification rules are deterministic per the plan's §4; "
            "they do not weight individual checks by confidence.",
            "No campaign verdict is changed by this study. CAMPAIGN_012 "
            "remains REJECT.",
        ],
        exploratory_only=True,
    )
    assert_real_data_kind(prov)

    payload = {
        "study_label": "probe_robustness_eur_usd_c012",
        "pair": PAIR,
        "candidate_campaign": CANDIDATE,
        "null_campaign": NULL,
        "material_gap_floor_r": MATERIAL_GAP_R,
        "loo": loo,
        "cost_stress_2x": cost,
        "neighboring_pairs": neighbor_pairs,
        "neighboring_candidates": neighbor_cands,
        "classification_block": cls,
        "provenance": prov.to_dict(),
        "verdict_word_ban_acknowledged": True,
        "notes": [
            "Classification is per SINGLE_PAIR_PROBE_001_PLAN.md §4.",
            "A classification of SELECTED_CELL_ARTIFACT means the cell "
            "does not survive the lab's anti-overfit screens and should "
            "NOT be promoted to further study.",
            "Lab output. Does not approve any strategy or change any "
            "campaign verdict.",
        ],
    }
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUTS / "probe_robustness_eur_usd_c012.json"
    md_path = OUTPUTS / "probe_robustness_eur_usd_c012.md"
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    _write_markdown(md_path, payload)
    return md_path


def _write_markdown(md_path: Path, p: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append(f"# Single-pair probe (Phase 2 robustness) — {p['study_label']}")
    lines.append("")
    lines.append("> Exploratory lab output. Not a strategy verdict; does not approve,")
    lines.append("> promote, or change any campaign status. CAMPAIGN_012 remains REJECT;")
    lines.append("> CAMPAIGN_011 remains the null model.")
    lines.append("")
    cls = p["classification_block"]
    lines.append("## Classification")
    lines.append("")
    lines.append(f"- **Result:** `{cls['classification']}`")
    lines.append(f"- Material-gap floor: `+{p['material_gap_floor_r']}` R")
    if cls["failures"]:
        lines.append("- Failed criteria:")
        for f in cls["failures"]:
            lines.append(f"  - `{f}`")
    else:
        lines.append("- Failed criteria: *(none)*")
    lines.append("- Robust criteria met:")
    for c in cls["robust_criteria_met"]:
        lines.append(f"  - `{c}`")
    if not cls["robust_criteria_met"]:
        lines.append("  - *(none)*")
    lines.append("")
    summary = cls["summary"]
    lines.append("### Headline numbers")
    lines.append("")
    lines.append(f"- n folds positive (candidate expectancy R > 0): **{summary['n_folds_positive']} / 8**")
    lines.append(f"- median per-fold candidate expectancy R: **`{summary['median_per_fold_expectancy_r']:+.4f}`**")
    lines.append(f"- mean gap R: **`{summary['mean_gap_r']:+.4f}`**, SE: `{summary['se_mean_gap']:.4f}`, t-stat: `{summary['t_stat_approx']:.3f}`")
    lines.append(f"- LOO mean gap range: `[{summary['loo_min_gap_r']:+.4f}, {summary['loo_max_gap_r']:+.4f}]`; {summary['loo_n_below_zero']} of 8 LOO means below zero")
    lines.append(f"- top fold share of |sum-of-absolute fold R|: **`{summary['top_fold_share_of_abs_sum']:.3f}`**")
    lines.append(f"- top fold signed share of total R: `{summary['top_fold_signed_share_of_total']:+.3f}`")
    lines.append(f"- 2× cost-stress mean gap R: **`{summary['stress_mean_gap_r']:+.4f}`** ({summary['stress_n_folds_positive_gap']} / 8 folds positive)")
    lines.append(f"- neighbor pairs above floor (C012 vs C011, other 6 pairs): **{summary['n_neighbor_pairs_above_floor']} / 7**")
    lines.append(f"- neighbor candidates above floor on EUR_USD (C010/12/13/14 vs C011): **{summary['n_neighbor_candidates_above_floor_on_eur_usd']} / 4**")
    lines.append("")
    lines.append("## Leave-one-fold-out resamples")
    lines.append("")
    lines.append("| dropped fold | LOO mean gap R |")
    lines.append("|---:|---:|")
    for d in p["loo"]["per_loo"]:
        lines.append(f"| {int(d['dropped_fold'])} | `{float(d['mean_gap_r']):+.4f}` |")
    lines.append("")
    cost = p["cost_stress_2x"]
    lines.append("## 2× cost-stress")
    lines.append("")
    lines.append(f"- assumed EUR_USD stop pips: `{cost['assumed_stop_pips']}`")
    lines.append(f"- average per-trade extra cost (R units): `{cost['per_trade_extra_cost_r_avg']:.5f}`")
    lines.append(f"- candidate stress mean R: `{cost['candidate_stress_mean_r']:+.4f}`")
    lines.append(f"- stress mean gap R: **`{cost['stress_mean_gap_r']:+.4f}`** ({cost['stress_n_folds_positive_gap']} / 8 folds positive gap)")
    lines.append(f"- stress median gap R: `{cost['stress_median_gap_r']:+.4f}`")
    lines.append("")
    lines.append("## Neighboring pairs (same candidate / same null)")
    lines.append("")
    lines.append("| pair | C012 mean R | C012 median R | C011 null R | gap R | above floor? | n folds positive | total trades |")
    lines.append("|---|---:|---:|---:|---:|:---:|---:|---:|")
    for row in p["neighboring_pairs"]:
        flag = "✓" if row["above_material_floor"] else " "
        lines.append(
            f"| {row['pair']} | {row['candidate_mean_r']:+.4f} | {row['candidate_median_r']:+.4f} | "
            f"{row['null_mean_r']:+.4f} | **{row['mean_gap_r']:+.4f}** | {flag} | "
            f"{int(row['candidate_n_folds_positive'])} | {int(row['candidate_total_trades'])} |"
        )
    lines.append("")
    lines.append("## Neighboring candidates (same EUR_USD pair / same null)")
    lines.append("")
    lines.append("| candidate | mean R | median R | null R | gap R | above floor? | n folds positive | total trades |")
    lines.append("|---|---:|---:|---:|---:|:---:|---:|---:|")
    for row in p["neighboring_candidates"]:
        flag = "✓" if row["above_material_floor"] else " "
        lines.append(
            f"| {row['candidate']} | {row['candidate_mean_r']:+.4f} | {row['candidate_median_r']:+.4f} | "
            f"{row['null_mean_r']:+.4f} | **{row['mean_gap_r']:+.4f}** | {flag} | "
            f"{int(row['candidate_n_folds_positive'])} | {int(row['candidate_total_trades'])} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for n in p["notes"]:
        lines.append(f"- {n}")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    out = run()
    print(f"wrote {out}")
