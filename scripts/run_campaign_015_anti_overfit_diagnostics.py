#!/usr/bin/env python3
"""CAMPAIGN_015 post-run anti-overfit diagnostic.

Wires the existing `research.anti_overfit.campaign_015` classifier to
the live CAMPAIGN_015 rehydrate walk-forward outputs and the existing
CAMPAIGN_011 random-entry null artifacts, and emits a structured
diagnostic + label.

This is post-run. It does NOT re-run any strategy, does NOT change
`approved_strategies.yaml`, and does NOT modify CAMPAIGN_011 evidence.
It cannot approve the strategy. Even a `ROBUST_ABOVE_NULL` label is
informational and routes to a *new pre-committed candidate* — not to
this strategy's approval.

Usage:
    python scripts/run_campaign_015_anti_overfit_diagnostics.py \
        --campaign-fold-detail research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json \
        --null-fold-detail backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json \
        --out-json research/campaign_015/diagnostics/null_and_anti_overfit.json \
        --out-md   research/campaign_015/diagnostics/null_and_anti_overfit.md
"""

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

from research.anti_overfit.campaign_015 import (
    CAMPAIGN_015_CLASSIFIER_LABELS,
    DiagnosticInputs,
    classify_campaign_015,
)


def _build_diagnostic_inputs(
    *,
    campaign_fd: dict[str, Any],
    null_fd: dict[str, Any],
) -> DiagnosticInputs:
    """Construct DiagnosticInputs from the rehydrate + null artifacts."""
    # Campaign side — pick base cost (the canonical aggregate).
    base = campaign_fd["by_cost"]["base"]
    agg = base["aggregate"]
    folds = base["folds"]

    # Per-fold expectancy R (campaign).
    camp_per_fold = [float(f["expectancy_r"]) for f in folds]

    # Per-pair gross positive R.
    pair_gross_pos: dict[str, float] = defaultdict(float)
    fold_gross_pos: dict[int, float] = defaultdict(float)
    trade_r_series: list[float] = []
    for f in folds:
        for pr in f["pair_runs"]:
            for r in pr.get("trade_r_series", []):
                if r > 0:
                    pair_gross_pos[pr["instrument"]] += float(r)
                    fold_gross_pos[f["fold_index"]] += float(r)
                trade_r_series.append(float(r))

    fold_gross_positive_list = [
        fold_gross_pos.get(f["fold_index"], 0.0) for f in folds
    ]

    # Null side.
    null_folds = null_fd["folds"]
    null_per_fold = [float(f["expectancy_r"]) for f in null_folds]
    null_agg = null_fd.get("aggregate", {})

    # Match check: same number of folds AND same test windows in order.
    blocked = False
    blocked_reasons: list[str] = []
    if len(camp_per_fold) != len(null_per_fold):
        blocked = True
        blocked_reasons.append(
            f"fold-count mismatch: campaign={len(camp_per_fold)}, "
            f"null={len(null_per_fold)}"
        )
    else:
        for i, (cf, nf) in enumerate(zip(folds, null_folds, strict=True)):
            if cf["test_start"] != nf["test_start"] or cf["test_end"] != nf["test_end"]:
                blocked = True
                blocked_reasons.append(
                    f"fold {i} window mismatch: "
                    f"campaign={cf['test_start']}..{cf['test_end']} "
                    f"null={nf['test_start']}..{nf['test_end']}"
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
        null_expectancy_r=float(
            null_agg.get("aggregate_expectancy_r")
            if null_agg.get("aggregate_expectancy_r") is not None
            else math.nan
        ),
        null_return_pct=float(
            null_agg.get("aggregate_return_pct")
            if null_agg.get("aggregate_return_pct") is not None
            else math.nan
        ),
        null_profit_factor=(
            float(null_agg["profit_factor"])
            if null_agg.get("profit_factor") is not None
            else None
        ),
        null_pairs_positive=int(null_agg.get("pairs_positive_count", -1)),
        null_per_fold_expectancy_r=null_per_fold,
    )


def diagnose(
    *,
    campaign_fd: dict[str, Any],
    null_fd: dict[str, Any],
) -> dict[str, Any]:
    inputs = _build_diagnostic_inputs(campaign_fd=campaign_fd, null_fd=null_fd)
    classification = classify_campaign_015(inputs)

    # Per-fold gap series for the report (regardless of label).
    gap_series: list[dict[str, Any]] = []
    base = campaign_fd["by_cost"]["base"]
    camp_folds = base["folds"]
    null_folds = null_fd["folds"]
    if len(camp_folds) == len(null_folds):
        for cf, nf in zip(camp_folds, null_folds, strict=True):
            gap_series.append(
                {
                    "fold_index": cf["fold_index"],
                    "test_start": cf["test_start"],
                    "test_end": cf["test_end"],
                    "campaign_expectancy_r": float(cf["expectancy_r"]),
                    "null_expectancy_r": float(nf["expectancy_r"]),
                    "gap_r": float(cf["expectancy_r"]) - float(nf["expectancy_r"]),
                    "campaign_trades": int(cf["trade_count"]),
                    "null_trades": int(nf["trade_count"]),
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

    return {
        "campaign_id": campaign_fd.get("campaign_id"),
        "strategy_name": campaign_fd.get("strategy_name"),
        "strategy_version": campaign_fd.get("strategy_version"),
        "config_hash": campaign_fd.get("config_hash"),
        "null_model": null_fd.get("strategy_name"),
        "null_config_hash": null_fd.get("config_hash"),
        "anti_overfit_label": classification["label"],
        "anti_overfit_gates": classification["anti_overfit_gates"],
        "anti_overfit_metrics": classification["metrics"],
        "anti_overfit_reasons": classification["reasons"],
        "per_fold_gap_series": gap_series,
        "null_per_fold_std_r": null_std,
        "mean_per_fold_gap_r": gap_mean,
        "campaign_total_trades": inputs.campaign_total_trades,
        "null_total_trades_per_fold": [
            int(f["trade_count"]) for f in null_folds
        ],
        "approval_status": "NOT_APPROVED",
        "approved_strategies_yaml_state": "approved: []",
        "diagnostic_disclaimer": (
            "Even a ROBUST_ABOVE_NULL label here does NOT approve "
            "failed_breakout_reversal; approval requires a fresh "
            "pre-committed campaign on a clean candidate and a human "
            "registry edit. CAMPAIGN_011 evidence is read-only."
        ),
    }


def render_md(obj: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# CAMPAIGN_015 — Null + Anti-Overfit Post-Run Diagnostic")
    lines.append("")
    lines.append(
        f"**Campaign:** `{obj.get('strategy_name')} "
        f"{obj.get('strategy_version', '')}`"
    )
    lines.append(f"**Null model:** `{obj.get('null_model')}`")
    lines.append(
        f"**Anti-overfit label:** **`{obj['anti_overfit_label']}`**"
    )
    lines.append(
        f"**Approval status:** `{obj['approval_status']}` "
        f"— `{obj['approved_strategies_yaml_state']}`"
    )
    lines.append("")
    lines.append(
        "> " + obj["diagnostic_disclaimer"]
    )
    lines.append("")
    lines.append("## Per-fold gap vs matched CAMPAIGN_011 null")
    lines.append("")
    lines.append(
        "| fold | window | campaign exp R | null exp R | gap R | "
        "campaign trades | null trades |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for g in obj["per_fold_gap_series"]:
        lines.append(
            f"| {g['fold_index']} "
            f"| {g['test_start']}..{g['test_end']} "
            f"| {g['campaign_expectancy_r']:+.4f} "
            f"| {g['null_expectancy_r']:+.4f} "
            f"| **{g['gap_r']:+.4f}** "
            f"| {g['campaign_trades']} "
            f"| {g['null_trades']} |"
        )
    lines.append("")
    lines.append(
        f"- mean per-fold gap R = **{obj['mean_per_fold_gap_r']:+.4f}**"
    )
    lines.append(
        f"- null per-fold std R = **{obj['null_per_fold_std_r']:.4f}**"
    )
    lines.append("")
    lines.append("## Anti-overfit gates")
    lines.append("")
    if obj["anti_overfit_gates"]:
        for k, v in obj["anti_overfit_gates"].items():
            mark = "✓" if v else "✗"
            lines.append(f"- {mark} `{k}` = {v}")
    else:
        lines.append("(none — classifier returned BLOCKED before gate eval)")
    lines.append("")
    lines.append("## Anti-overfit metrics")
    lines.append("")
    for k, v in obj["anti_overfit_metrics"].items():
        if isinstance(v, float):
            lines.append(f"- `{k}` = {v:+.4f}")
        else:
            lines.append(f"- `{k}` = {v}")
    lines.append("")
    lines.append("## Reasons")
    lines.append("")
    for r in obj["anti_overfit_reasons"]:
        lines.append(f"- {r}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-fold-detail", required=True, type=Path)
    ap.add_argument("--null-fold-detail", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    args = ap.parse_args(argv)

    if not args.campaign_fold_detail.exists():
        print(
            f"BLOCKED: campaign fold-detail does not exist: "
            f"{args.campaign_fold_detail}",
            file=sys.stderr,
        )
        return 2
    if not args.null_fold_detail.exists():
        print(
            f"BLOCKED: null fold-detail does not exist: "
            f"{args.null_fold_detail}",
            file=sys.stderr,
        )
        return 2

    campaign_fd = json.loads(
        args.campaign_fold_detail.read_text(encoding="utf-8")
    )
    null_fd = json.loads(args.null_fold_detail.read_text(encoding="utf-8"))
    obj = diagnose(campaign_fd=campaign_fd, null_fd=null_fd)

    if obj["anti_overfit_label"] not in CAMPAIGN_015_CLASSIFIER_LABELS:
        print(
            f"unexpected label: {obj['anti_overfit_label']!r}",
            file=sys.stderr,
        )
        return 3

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(obj, indent=2, default=str), encoding="utf-8"
    )
    args.out_md.write_text(render_md(obj), encoding="utf-8")
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    print(f"label: {obj['anti_overfit_label']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
