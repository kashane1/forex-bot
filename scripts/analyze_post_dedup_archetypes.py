#!/usr/bin/env python3
"""Post-dedup pair / fold / side / exit archetype analysis.

Exploratory meta-analysis across CAMPAIGN_015–017 deduped evidence.
Classifies whether any reliable archetype warrants a pair-specific,
side-specific, or regime-specific lab.

This is exploratory. It CANNOT approve a strategy or justify retuning.

Usage:
    python scripts/analyze_post_dedup_archetypes.py
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

NULL_BASELINE_PATH = REPO_ROOT / "research/null_baselines/campaign_011_deduped_null_baseline.json"
METRIC_MATRIX_PATH = REPO_ROOT / "research/post_dedup_meta/campaign_metric_matrix.json"

CAMPAIGN_BACKTESTS: dict[str, Path] = {
    "CAMPAIGN_015": REPO_ROOT / "backtests/CAMPAIGN_015_failed_breakout_reversal_deduped",
    "CAMPAIGN_016": REPO_ROOT / "backtests/CAMPAIGN_016_weekly_cross_sectional_momentum",
    "CAMPAIGN_017": REPO_ROOT / "backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout",
}

CANDIDATE_CAMPAIGNS = ("CAMPAIGN_015", "CAMPAIGN_016", "CAMPAIGN_017")
PAIRS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)

# Meaningful beat-null threshold: one null fold std band above centre.
MEANINGFUL_NULL_GAP_R = 0.05


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _find_trade_csvs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(root.glob("folds/base/fold_*/fold_*_*_trades.csv"))


def _read_trades(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.is_file():
        return []
    with csv_path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _trade_side_stats(trades: list[dict[str, str]]) -> dict[str, Any]:
    long_r: list[float] = []
    short_r: list[float] = []
    exit_reasons: Counter[str] = Counter()
    for t in trades:
        r = float(t.get("r_multiple", 0) or 0)
        side = (t.get("side") or "").lower()
        if side == "long":
            long_r.append(r)
        elif side == "short":
            short_r.append(r)
        exit_reasons[t.get("exit_reason", "unknown")] += 1

    def _exp(rs: list[float]) -> float | None:
        return sum(rs) / len(rs) if rs else None

    return {
        "long_trades": len(long_r),
        "short_trades": len(short_r),
        "long_exp_r": _exp(long_r),
        "short_exp_r": _exp(short_r),
        "exit_reason_counts": dict(exit_reasons),
    }


def _pair_campaign_matrix(matrix: dict[str, Any]) -> dict[str, dict[str, float]]:
    """pair -> campaign_id -> exp_r."""
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for row in matrix["campaigns"]:
        if row["role"] != "candidate":
            continue
        cid = row["campaign_id"]
        for p in row.get("per_pair", []):
            out[p["instrument"]][cid] = p["expectancy_r"]
    return dict(out)


def _fold_campaign_matrix(matrix: dict[str, Any]) -> dict[int, dict[str, float]]:
    out: dict[int, dict[str, float]] = defaultdict(dict)
    for row in matrix["campaigns"]:
        if row["role"] != "candidate":
            continue
        cid = row["campaign_id"]
        for f in row.get("per_fold", []):
            out[int(f["fold_index"])][cid] = float(f["expectancy_r"])
    return dict(out)


def _null_fold_map(null_baseline: dict[str, Any]) -> dict[int, float]:
    return {
        int(f["fold_index"]): float(f["expectancy_r"])
        for f in null_baseline.get("per_fold", [])
    }


def analyze_pair_archetypes(
    pair_matrix: dict[str, dict[str, float]],
    null_centre: float,
    null_std: float,
) -> dict[str, Any]:
    pair_scores: list[dict[str, Any]] = []
    for pair in PAIRS:
        by_camp = pair_matrix.get(pair, {})
        exp_values = [by_camp[c] for c in CANDIDATE_CAMPAIGNS if c in by_camp]
        if not exp_values:
            continue
        mean_exp = sum(exp_values) / len(exp_values)
        positive_count = sum(1 for v in exp_values if v > 0)
        beat_null_count = sum(1 for v in exp_values if v - null_centre > null_std)
        pair_scores.append(
            {
                "pair": pair,
                "mean_exp_r_across_campaigns": mean_exp,
                "campaign_exp_r": by_camp,
                "positive_campaign_count": positive_count,
                "beat_null_std_count": beat_null_count,
                "consistently_negative": all(v < 0 for v in exp_values),
                "consistently_positive": all(v > 0 for v in exp_values),
            },
        )

    pair_scores.sort(key=lambda x: x["mean_exp_r_across_campaigns"], reverse=True)
    least_bad = pair_scores[:3] if pair_scores else []
    most_bad = list(reversed(pair_scores[-3:])) if pair_scores else []

    return {
        "pair_scores": pair_scores,
        "least_bad_pairs": least_bad,
        "most_bad_pairs": most_bad,
        "null_centre_exp_r": null_centre,
        "null_std_band": null_std,
    }


def analyze_fold_regimes(
    fold_matrix: dict[int, dict[str, float]],
    null_folds: dict[int, float],
) -> dict[str, Any]:
    universal_fail_folds: list[int] = []
    any_less_bad_folds: list[dict[str, Any]] = []

    for fold_idx in sorted(fold_matrix.keys()):
        by_camp = fold_matrix[fold_idx]
        null_exp = null_folds.get(fold_idx, 0.0)
        camp_vals = [by_camp[c] for c in CANDIDATE_CAMPAIGNS if c in by_camp]
        if not camp_vals:
            continue
        all_negative = all(v < 0 for v in camp_vals)
        all_below_null = all(v < null_exp for v in camp_vals)
        best_camp = max(camp_vals)
        best_cid = next(c for c in CANDIDATE_CAMPAIGNS if by_camp.get(c) == best_camp)
        if all_negative and all_below_null:
            universal_fail_folds.append(fold_idx)
        gap_vs_null = best_camp - null_exp
        if gap_vs_null > MEANINGFUL_NULL_GAP_R:
            any_less_bad_folds.append(
                {
                    "fold_index": fold_idx,
                    "best_campaign": best_cid,
                    "best_exp_r": best_camp,
                    "null_exp_r": null_exp,
                    "gap_r": gap_vs_null,
                },
            )

    return {
        "universal_fail_folds": universal_fail_folds,
        "folds_with_meaningful_beat_null": any_less_bad_folds,
        "fold_campaign_matrix": {
            str(k): v for k, v in sorted(fold_matrix.items())
        },
    }


def analyze_side_and_exits(
    campaigns: dict[str, Path],
) -> dict[str, Any]:
    by_campaign: dict[str, Any] = {}
    aggregate_long_r: list[float] = []
    aggregate_short_r: list[float] = []
    aggregate_exit: Counter[str] = Counter()
    trade_csv_status: dict[str, str] = {}

    for cid, root in campaigns.items():
        csvs = _find_trade_csvs(root)
        if not csvs:
            trade_csv_status[cid] = "MISSING"
            by_campaign[cid] = {"status": "BLOCKED_BY_MISSING_TRADES"}
            continue
        trade_csv_status[cid] = f"OK ({len(csvs)} files)"
        all_trades: list[dict[str, str]] = []
        for p in csvs:
            all_trades.extend(_read_trades(p))
        stats = _trade_side_stats(all_trades)
        by_campaign[cid] = {"status": "OK", **stats}
        # Re-read for aggregate weighting — use per-trade r
        for t in all_trades:
            r = float(t.get("r_multiple", 0) or 0)
            side = (t.get("side") or "").lower()
            if side == "long":
                aggregate_long_r.append(r)
            elif side == "short":
                aggregate_short_r.append(r)
            aggregate_exit[t.get("exit_reason", "unknown")] += 1

    def _exp(rs: list[float]) -> float | None:
        return sum(rs) / len(rs) if rs else None

    long_exp = _exp(aggregate_long_r)
    short_exp = _exp(aggregate_short_r)
    less_bad_side = None
    if long_exp is not None and short_exp is not None:
        less_bad_side = "long" if long_exp > short_exp else "short"

    total_exits = sum(aggregate_exit.values()) or 1
    exit_mix = {
        k: {"count": v, "pct": v / total_exits * 100.0}
        for k, v in aggregate_exit.most_common()
    }

    return {
        "trade_csv_status": trade_csv_status,
        "by_campaign": by_campaign,
        "aggregate_long_exp_r": long_exp,
        "aggregate_short_exp_r": short_exp,
        "less_bad_side": less_bad_side,
        "exit_reason_mix": exit_mix,
        "dominant_loss_driver": _classify_loss_driver(exit_mix, long_exp, short_exp),
    }


def _classify_loss_driver(
    exit_mix: dict[str, dict[str, float]],
    long_exp: float | None,
    short_exp: float | None,
) -> str:
    stop_pct = exit_mix.get("stop", {}).get("pct", 0.0)
    time_pct = exit_mix.get("time", {}).get("pct", 0.0)
    if stop_pct > 45:
        return "stops_dominate"
    if time_pct > 45:
        return "time_exits_dominate"
    if long_exp is not None and short_exp is not None:
        if min(long_exp, short_exp) < -0.05 and max(long_exp, short_exp) > -0.02:
            return "side_asymmetry"
    return "low_hit_rate_mixed"


def analyze_weekly_cost_drag(matrix: dict[str, Any]) -> dict[str, Any]:
    weekly: list[dict[str, Any]] = []
    for row in matrix["campaigns"]:
        if row["role"] != "candidate":
            continue
        cs = row.get("cost_sensitivity") or {}
        is_weekly = "weekly" in row["strategy_name"]
        weekly.append(
            {
                "campaign_id": row["campaign_id"],
                "strategy_name": row["strategy_name"],
                "is_weekly": is_weekly,
                "base_exp_r": row["base_exp_r"],
                "2x_exp_r": row.get("2x_exp_r"),
                "cost_delta_exp_r": cs.get("delta_exp_r"),
                "trade_count": row["trade_count"],
            },
        )
    return {
        "campaigns": weekly,
        "note": (
            "Weekly strategies (C016, C017) show lower trade counts but "
            "still negative base exp_r; 2x cost worsens all candidates."
        ),
    }


def analyze_cell_beat_null(
    matrix: dict[str, Any],
    null_baseline: dict[str, Any],
) -> dict[str, Any]:
    null_centre = null_baseline["aggregate"]["aggregate_expectancy_r"]
    null_std = null_baseline["null_distribution"]["per_fold_expectancy_r_std"]
    null_folds = _null_fold_map(null_baseline)

    meaningful_cells: list[dict[str, Any]] = []
    for row in matrix["campaigns"]:
        if row["role"] != "candidate":
            continue
        cid = row["campaign_id"]
        for f in row.get("per_fold", []):
            fold_idx = int(f["fold_index"])
            exp = float(f["expectancy_r"])
            null_exp = null_folds.get(fold_idx, null_centre)
            gap = exp - null_exp
            if gap >= MEANINGFUL_NULL_GAP_R:
                meaningful_cells.append(
                    {
                        "campaign_id": cid,
                        "cell_type": "fold",
                        "fold_index": fold_idx,
                        "expectancy_r": exp,
                        "null_expectancy_r": null_exp,
                        "gap_r": gap,
                    },
                )
        for p in row.get("per_pair", []):
            exp = float(p["expectancy_r"])
            gap = exp - null_centre
            if gap >= MEANINGFUL_NULL_GAP_R and p["trade_count"] >= 20:
                meaningful_cells.append(
                    {
                        "campaign_id": cid,
                        "cell_type": "pair",
                        "pair": p["instrument"],
                        "trade_count": p["trade_count"],
                        "expectancy_r": exp,
                        "gap_r": gap,
                    },
                )

    return {
        "meaningful_beat_null_threshold_gap_r": MEANINGFUL_NULL_GAP_R,
        "null_std_band": null_std,
        "cells": meaningful_cells,
        "cell_count": len(meaningful_cells),
    }


def classify_findings(analysis: dict[str, Any]) -> dict[str, Any]:
    labels: list[str] = []
    pair_analysis = analysis["pair_analysis"]
    fold_analysis = analysis["fold_regime_analysis"]
    side_analysis = analysis["side_and_exit_analysis"]
    cell_analysis = analysis["cell_beat_null"]

    # Check missing trades
    missing = [
        c
        for c, s in side_analysis["trade_csv_status"].items()
        if s == "MISSING"
    ]
    if missing:
        labels.append("BLOCKED_BY_MISSING_TRADES")

    # Pair-specific signal?
    consistently_pos = [
        p for p in pair_analysis["pair_scores"] if p["consistently_positive"]
    ]
    if len(consistently_pos) >= 1:
        labels.append("PAIR_SPECIFIC_SIGNAL_WORTH_LAB")
    else:
        labels.append("NO_RELIABLE_ARCHETYPE")

    # Side-specific?
    long_exp = side_analysis.get("aggregate_long_exp_r")
    short_exp = side_analysis.get("aggregate_short_exp_r")
    if (
        long_exp is not None
        and short_exp is not None
        and abs(long_exp - short_exp) > 0.05
        and max(long_exp, short_exp) > -0.01
    ):
        labels.append("SIDE_SPECIFIC_SIGNAL_WORTH_LAB")

    # Regime-specific?
    if len(fold_analysis["folds_with_meaningful_beat_null"]) >= 2:
        labels.append("REGIME_SPECIFIC_SIGNAL_WORTH_LAB")

    # Cost dominates?
    for row in analysis["weekly_cost_drag"]["campaigns"]:
        cs = row.get("cost_delta_exp_r")
        if cs is not None and cs < -0.01 and row["base_exp_r"] < 0:
            labels.append("COST_MODEL_DOMINATES")
            break

    # Data sparse?
    sparse = all(
        row["trade_count"] < 200
        for row in analysis["weekly_cost_drag"]["campaigns"]
        if row["campaign_id"] != "CAMPAIGN_015"
    )
    if sparse:
        labels.append("DATA_TOO_SPARSE")

    # Primary classification — prefer NO_RELIABLE if cells don't replicate
    primary = "NO_RELIABLE_ARCHETYPE"
    if "PAIR_SPECIFIC_SIGNAL_WORTH_LAB" in labels and cell_analysis["cell_count"] >= 3:
        primary = "PAIR_SPECIFIC_SIGNAL_WORTH_LAB"
    elif "REGIME_SPECIFIC_SIGNAL_WORTH_LAB" in labels:
        primary = "REGIME_SPECIFIC_SIGNAL_WORTH_LAB"
    elif "SIDE_SPECIFIC_SIGNAL_WORTH_LAB" in labels:
        primary = "SIDE_SPECIFIC_SIGNAL_WORTH_LAB"
    elif "COST_MODEL_DOMINATES" in labels and "NO_RELIABLE_ARCHETYPE" in labels:
        primary = "COST_MODEL_DOMINATES"
    elif "DATA_TOO_SPARSE" in labels:
        primary = "DATA_TOO_SPARSE"

    return {
        "primary_classification": primary,
        "all_labels": sorted(set(labels)),
        "exploratory_disclaimer": (
            "Exploratory labels do NOT approve strategies or justify retuning. "
            "Pair/fold cells that beat null may be noise given WITHIN_NULL aggregate labels."
        ),
    }


def run_analysis(
    matrix: dict[str, Any],
    null_baseline: dict[str, Any],
    campaign_roots: dict[str, Path],
) -> dict[str, Any]:
    null_centre = null_baseline["aggregate"]["aggregate_expectancy_r"]
    null_std = null_baseline["null_distribution"]["per_fold_expectancy_r_std"]

    pair_matrix = _pair_campaign_matrix(matrix)
    fold_matrix = _fold_campaign_matrix(matrix)
    null_folds = _null_fold_map(null_baseline)

    analysis: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "campaigns_analyzed": list(CANDIDATE_CAMPAIGNS),
        "null_reference": {
            "aggregate_expectancy_r": null_centre,
            "per_fold_std": null_std,
        },
        "pair_analysis": analyze_pair_archetypes(pair_matrix, null_centre, null_std),
        "fold_regime_analysis": analyze_fold_regimes(fold_matrix, null_folds),
        "side_and_exit_analysis": analyze_side_and_exits(campaign_roots),
        "weekly_cost_drag": analyze_weekly_cost_drag(matrix),
        "cell_beat_null": analyze_cell_beat_null(matrix, null_baseline),
        "concentration": _concentration_check(matrix),
    }
    analysis["classification"] = classify_findings(analysis)
    return analysis


def _concentration_check(matrix: dict[str, Any]) -> dict[str, Any]:
    out: list[dict[str, Any]] = []
    for row in matrix["campaigns"]:
        if row["role"] != "candidate":
            continue
        per_pair = row.get("per_pair", [])
        if not per_pair:
            continue
        best = max(per_pair, key=lambda p: p.get("expectancy_r", -999))
        total_tc = sum(p.get("trade_count", 0) for p in per_pair)
        best_tc = best.get("trade_count", 0)
        out.append(
            {
                "campaign_id": row["campaign_id"],
                "best_pair": best["instrument"],
                "best_pair_exp_r": best["expectancy_r"],
                "best_pair_trade_share_pct": (
                    best_tc / total_tc * 100.0 if total_tc else 0.0
                ),
                "single_pair_dominance_pct": row.get("single_pair_dominance_pct"),
            },
        )
    return {"by_campaign": out}


def render_md(analysis: dict[str, Any]) -> str:
    cls = analysis["classification"]
    lines = [
        "# Post-Dedup Archetype Analysis",
        "",
        f"**Generated:** {analysis['generated_at']}",
        "",
        f"> **Primary classification:** `{cls['primary_classification']}`",
        "",
        f"> {cls['exploratory_disclaimer']}",
        "",
        "## 1. Pair ranking (least bad → worst)",
        "",
        "| pair | mean exp_r | C015 | C016 | C017 | +campaigns |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for p in analysis["pair_analysis"]["pair_scores"]:
        c = p["campaign_exp_r"]
        lines.append(
            f"| {p['pair']} | {p['mean_exp_r_across_campaigns']:.4f} | "
            f"{c.get('CAMPAIGN_015', float('nan')):.4f} | "
            f"{c.get('CAMPAIGN_016', float('nan')):.4f} | "
            f"{c.get('CAMPAIGN_017', float('nan')):.4f} | "
            f"{p['positive_campaign_count']}/3 |",
        )

    lines.extend(
        [
            "",
            "## 2. Fold / regime periods",
            "",
            f"- Universal fail folds (all campaigns negative, below null): "
            f"{analysis['fold_regime_analysis']['universal_fail_folds']}",
            f"- Folds with meaningful beat-null cell: "
            f"{len(analysis['fold_regime_analysis']['folds_with_meaningful_beat_null'])}",
            "",
        ],
    )
    for f in analysis["fold_regime_analysis"]["folds_with_meaningful_beat_null"]:
        lines.append(
            f"  - fold {f['fold_index']}: {f['best_campaign']} exp_r={f['best_exp_r']:.4f} "
            f"(gap vs null {f['gap_r']:+.4f})",
        )

    side = analysis["side_and_exit_analysis"]
    lines.extend(
        [
            "",
            "## 3. Long vs short (aggregate across trade CSVs)",
            "",
            f"- Long exp_r: {side.get('aggregate_long_exp_r')}",
            f"- Short exp_r: {side.get('aggregate_short_exp_r')}",
            f"- Less bad side: {side.get('less_bad_side')}",
            f"- Dominant loss driver: {side.get('dominant_loss_driver')}",
            "",
            "### Exit reason mix",
            "",
            "| reason | count | pct |",
            "|---|---:|---:|",
        ],
    )
    for reason, info in side.get("exit_reason_mix", {}).items():
        lines.append(f"| {reason} | {info['count']} | {info['pct']:.1f}% |")

    lines.extend(
        [
            "",
            "## 4. Weekly cost sensitivity",
            "",
            "| campaign | base exp_r | 2x exp_r | Δ exp_r | trades |",
            "|---|---:|---:|---:|---:|",
        ],
    )
    for w in analysis["weekly_cost_drag"]["campaigns"]:
        lines.append(
            f"| {w['campaign_id']} | {w['base_exp_r']:.4f} | "
            f"{w.get('2x_exp_r', 0):.4f} | {w.get('cost_delta_exp_r', 0):+.4f} | "
            f"{w['trade_count']} |",
        )

    cells = analysis["cell_beat_null"]
    lines.extend(
        [
            "",
            "## 5. Cells beating null by ≥ 0.05R",
            "",
            f"Count: **{cells['cell_count']}** (exploratory — may be noise)",
            "",
        ],
    )
    for c in cells["cells"][:15]:
        if c["cell_type"] == "fold":
            lines.append(
                f"- {c['campaign_id']} fold {c['fold_index']}: "
                f"exp_r={c['expectancy_r']:.4f} gap={c['gap_r']:+.4f}",
            )
        else:
            lines.append(
                f"- {c['campaign_id']} {c['pair']}: "
                f"exp_r={c['expectancy_r']:.4f} trades={c['trade_count']} gap={c['gap_r']:+.4f}",
            )

    lines.extend(
        [
            "",
            "## 6. Classification labels",
            "",
            f"- Primary: `{cls['primary_classification']}`",
            f"- All: {', '.join(f'`{label}`' for label in cls['all_labels'])}",
            "",
        ],
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metric-matrix", type=Path, default=METRIC_MATRIX_PATH)
    parser.add_argument("--null-baseline", type=Path, default=NULL_BASELINE_PATH)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "research/post_dedup_meta/archetype_analysis.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "research/post_dedup_meta/archetype_analysis.md",
    )
    parser.add_argument(
        "--out-docs-md",
        type=Path,
        default=REPO_ROOT / "docs/research/POST_DEDUP_ARCHETYPE_ANALYSIS.md",
    )
    args = parser.parse_args(argv)

    matrix = _load_json(args.metric_matrix)
    null_baseline = _load_json(args.null_baseline)
    analysis = run_analysis(matrix, null_baseline, CAMPAIGN_BACKTESTS)
    md = render_md(analysis)

    for path in (args.out_json, args.out_md, args.out_docs_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(md + "\n", encoding="utf-8")
    args.out_docs_md.write_text(md + "\n", encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Primary classification: {analysis['classification']['primary_classification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
