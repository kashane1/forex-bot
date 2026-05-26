#!/usr/bin/env python3
"""CAMPAIGN_016 post-run anti-overfit diagnostic."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.anti_overfit.campaign_016 import (
    CAMPAIGN_016_CLASSIFIER_LABELS,
    DiagnosticInputs,
    classify_campaign_016,
)
from research.null_baselines.campaign_011_deduped import (
    load_campaign_011_deduped_null_baseline,
)

NULL_BASELINE_PATH = (
    ROOT / "research" / "null_baselines" / "campaign_011_deduped_null_baseline.json"
)


def _build_diagnostic_inputs(
    *,
    campaign_fd: dict[str, Any],
    null_baseline: dict[str, Any],
) -> DiagnosticInputs:
    base = campaign_fd["by_cost"]["base"]
    agg = base["aggregate"]
    folds = base["folds"]
    camp_per_fold = [float(f["expectancy_r"]) for f in folds]

    pair_gross_pos: dict[str, float] = defaultdict(float)
    fold_gross_pos: dict[int, float] = defaultdict(float)
    trade_r_series: list[float] = []
    for f in folds:
        for pr in f["pair_runs"]:
            for r in pr.get("trade_r_series", []):
                rv = float(r)
                trade_r_series.append(rv)
                if rv > 0:
                    pair_gross_pos[pr["instrument"]] += rv
                    fold_gross_pos[f["fold_index"]] += rv

    fold_gross_positive_list = [
        fold_gross_pos.get(f["fold_index"], 0.0) for f in folds
    ]

    null_per_fold = [
        float(row["expectancy_r"]) for row in null_baseline["per_fold"]
    ]
    null_agg = null_baseline["aggregate"]

    blocked = False
    blocked_reasons: list[str] = []
    if len(camp_per_fold) != len(null_per_fold):
        blocked = True
        blocked_reasons.append(
            f"fold-count mismatch: campaign={len(camp_per_fold)}, "
            f"null={len(null_per_fold)}"
        )

    return DiagnosticInputs(
        blocked=blocked,
        blocked_reasons=blocked_reasons,
        campaign_expectancy_r=float(agg["aggregate_expectancy_r"]),
        campaign_return_pct=float(agg["aggregate_return_pct"]),
        campaign_profit_factor=(
            float(agg["profit_factor"])
            if agg.get("profit_factor") is not None
            else None
        ),
        campaign_pairs_positive=int(agg.get("pairs_positive_count", -1)),
        campaign_total_trades=int(agg.get("total_trades", 0)),
        campaign_per_fold_expectancy_r=camp_per_fold,
        campaign_pair_gross_positive_r=dict(pair_gross_pos),
        campaign_fold_gross_positive_r=fold_gross_positive_list,
        campaign_trade_r_series=trade_r_series,
        campaign_total_cost_r=0.0,
        null_expectancy_r=float(null_agg["aggregate_expectancy_r"]),
        null_return_pct=float(null_agg["aggregate_return_pct"]),
        null_profit_factor=float(null_agg.get("profit_factor") or 0.0),
        null_pairs_positive=int(null_agg.get("pairs_positive_count", 3)),
        null_per_fold_expectancy_r=null_per_fold,
    )


def diagnose(
    *,
    campaign_fd: dict[str, Any],
    null_baseline: dict[str, Any],
) -> dict[str, Any]:
    inputs = _build_diagnostic_inputs(
        campaign_fd=campaign_fd, null_baseline=null_baseline,
    )
    classification = classify_campaign_016(inputs)

    gap_series: list[dict[str, Any]] = []
    base = campaign_fd["by_cost"]["base"]
    camp_folds = base["folds"]
    null_folds = null_baseline["per_fold"]
    for cf, nf in zip(camp_folds, null_folds, strict=False):
        gap_series.append(
            {
                "fold_index": cf["fold_index"],
                "test_start": cf["test_start"],
                "test_end": cf["test_end"],
                "campaign_expectancy_r": float(cf["expectancy_r"]),
                "null_expectancy_r": float(nf["expectancy_r"]),
                "gap_r": float(cf["expectancy_r"]) - float(nf["expectancy_r"]),
            }
        )

    null_std = (
        statistics.stdev([g["null_expectancy_r"] for g in gap_series])
        if len(gap_series) >= 2
        else math.nan
    )
    gap_mean = (
        statistics.mean([g["gap_r"] for g in gap_series]) if gap_series else math.nan
    )
    null_centre = float(null_baseline["aggregate"]["aggregate_expectancy_r"])

    return {
        "campaign_id": "CAMPAIGN_016",
        "strategy_name": campaign_fd.get("strategy_name"),
        "strategy_version": campaign_fd.get("strategy_version"),
        "anti_overfit_label": classification["label"],
        "valid_labels": list(CAMPAIGN_016_CLASSIFIER_LABELS),
        "null_centre_exp_r": null_centre,
        "campaign_aggregate_exp_r": float(
            base["aggregate"]["aggregate_expectancy_r"]
        ),
        "gap_vs_null_exp_r": float(base["aggregate"]["aggregate_expectancy_r"])
        - null_centre,
        "null_std_band_exp_r": null_std,
        "gap_mean_per_fold_r": gap_mean,
        "per_fold_gap_series": gap_series,
        "anti_overfit_gates": classification["anti_overfit_gates"],
        "metrics": classification["metrics"],
        "reasons": classification["reasons"],
        "approval_status": "NOT_APPROVED",
    }


def _render_md(report: dict[str, Any]) -> str:
    lines = [
        "# CAMPAIGN_016 Null and Anti-Overfit Diagnostics",
        "",
        f"**Label:** `{report['anti_overfit_label']}`",
        "",
        f"- Null centre exp_r: {report['null_centre_exp_r']:+.6f}",
        f"- Campaign aggregate exp_r: {report['campaign_aggregate_exp_r']:+.6f}",
        f"- Gap vs null: {report['gap_vs_null_exp_r']:+.6f}",
        f"- Null std band (per-fold): {report['null_std_band_exp_r']}",
        "",
        "## Reasons",
        "",
    ]
    for r in report.get("reasons", []):
        lines.append(f"- {r}")
    lines.append("")
    lines.append("**No strategy approved.**")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--campaign-fold-detail",
        default=str(
            ROOT
            / "backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/fold_detail.json"
        ),
    )
    ap.add_argument("--null-baseline", default=str(NULL_BASELINE_PATH))
    ap.add_argument(
        "--out-json",
        default=str(ROOT / "research/campaign_016/diagnostics/null_and_anti_overfit.json"),
    )
    ap.add_argument(
        "--out-md",
        default=str(ROOT / "research/campaign_016/diagnostics/null_and_anti_overfit.md"),
    )
    args = ap.parse_args(argv)

    fold_detail_path = Path(args.campaign_fold_detail)
    if not fold_detail_path.is_file():
        report = {
            "campaign_id": "CAMPAIGN_016",
            "anti_overfit_label": "BLOCKED",
            "reasons": [f"missing fold_detail: {fold_detail_path}"],
            "approval_status": "NOT_APPROVED",
        }
        out_json = Path(args.out_json)
        out_md = Path(args.out_md)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        out_md.write_text(_render_md(report), encoding="utf-8")
        print(f"BLOCKED — wrote {out_json}")
        return 0

    campaign_fd = json.loads(fold_detail_path.read_text(encoding="utf-8"))
    if not campaign_fd.get("by_cost", {}).get("base"):
        report = {
            "campaign_id": "CAMPAIGN_016",
            "anti_overfit_label": "BLOCKED",
            "reasons": ["campaign fold_detail missing base cost lane"],
            "approval_status": "NOT_APPROVED",
        }
        out_json = Path(args.out_json)
        out_md = Path(args.out_md)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        out_md.write_text(_render_md(report), encoding="utf-8")
        return 0

    null_baseline = load_campaign_011_deduped_null_baseline()
    report = diagnose(campaign_fd=campaign_fd, null_baseline=null_baseline)

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    out_md.write_text(_render_md(report), encoding="utf-8")
    print(f"label={report['anti_overfit_label']} wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
