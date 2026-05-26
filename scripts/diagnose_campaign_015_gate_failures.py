#!/usr/bin/env python3
"""CAMPAIGN_015 gate-failure autopsy — diagnostic only.

Reads the CAMPAIGN_015 rehydrate walk-forward outputs (or any
equivalent ``fold_detail.json`` + ``gate_result.json`` pair) and emits
a structured autopsy of which gates failed and why.

This is a diagnostic. It does NOT re-judge the campaign, does NOT
relax any gate, and does NOT change `approved_strategies.yaml`. The
counterfactual "fold-pass count with trade_count gate removed" is
labeled non-gating and is purely informational — the actual gating
result remains REJECT.

Usage:
    python scripts/diagnose_campaign_015_gate_failures.py \
        --gate-result research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/gate_result.json \
        --fold-detail research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json \
        --out-json research/campaign_015/diagnostics/gate_failure_autopsy.json \
        --out-md   research/campaign_015/diagnostics/gate_failure_autopsy.md
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_CAMPAIGN_ID = "CAMPAIGN_015"
REQUIRED_STRATEGY = "failed_breakout_reversal"


def _bucket(n: int) -> str:
    if n == 0:
        return "0_trades"
    if n == 1:
        return "1_trade"
    if n <= 3:
        return "2_to_3_trades"
    if n <= 9:
        return "4_to_9_trades"
    return "10_or_more_trades"


CELL_BUCKETS_ORDER = (
    "0_trades",
    "1_trade",
    "2_to_3_trades",
    "4_to_9_trades",
    "10_or_more_trades",
)


def autopsy(
    gate_result: dict[str, Any],
    fold_detail: dict[str, Any],
) -> dict[str, Any]:
    """Pure computation, easy to unit test.

    Both inputs are taken as parsed dicts so callers can pass fixtures.
    """
    if gate_result.get("campaign_id") != REQUIRED_CAMPAIGN_ID:
        raise ValueError(
            f"gate_result.campaign_id must be {REQUIRED_CAMPAIGN_ID!r}; "
            f"got {gate_result.get('campaign_id')!r}",
        )
    if gate_result.get("strategy_name") != REQUIRED_STRATEGY:
        raise ValueError(
            f"gate_result.strategy_name must be {REQUIRED_STRATEGY!r}; "
            f"got {gate_result.get('strategy_name')!r}",
        )

    out: dict[str, Any] = {
        "campaign_id": gate_result["campaign_id"],
        "strategy_name": gate_result["strategy_name"],
        "strategy_version": gate_result.get("strategy_version"),
        "config_hash": gate_result.get("config_hash"),
        "fold_count": gate_result.get("fold_count"),
        "runner_verdict": gate_result.get("verdict"),
        "approval_status": gate_result.get("approval_status"),
        "by_cost": {},
        "summary": {},
        "counterfactual_disclaimer": (
            "Counterfactual fold-pass counts shown below are non-gating "
            "and diagnostic only. They do NOT relax any pre-committed "
            "gate, and the runner verdict remains REJECT regardless."
        ),
    }

    cost_labels = list(gate_result.get("by_cost", {}).keys())
    if not cost_labels:
        raise ValueError("gate_result.by_cost is empty")

    fold_count_per_fold = None
    for cost in cost_labels:
        agg = gate_result["by_cost"][cost]
        fold_cost_block = fold_detail["by_cost"][cost]
        folds = fold_cost_block["folds"]
        if fold_count_per_fold is None:
            fold_count_per_fold = len(folds)
        elif len(folds) != fold_count_per_fold:
            raise ValueError(
                f"per-cost fold counts differ: {fold_count_per_fold} vs "
                f"{len(folds)} for cost={cost!r}",
            )

        failed_agg_gates = sorted(
            [k for k, v in agg.get("aggregate_gates", {}).items() if not v]
        )
        passed_agg_gates = sorted(
            [k for k, v in agg.get("aggregate_gates", {}).items() if v]
        )

        # Per-fold gate accounting.
        per_fold: list[dict[str, Any]] = []
        gate_fail_counter: Counter[str] = Counter()
        any_fold_passed = 0
        cf_passed_minus_tradecount = 0
        cf_passed_minus_tradecount_and_pairspos = 0
        for f in folds:
            g = f["gates"]
            failed = sorted([k for k, v in g.items() if not v])
            for gname in failed:
                gate_fail_counter[gname] += 1
            gates_excl_tradecount = {
                k: v for k, v in g.items() if k != "trade_count_ge_30"
            }
            gates_excl_tc_and_pp = {
                k: v
                for k, v in g.items()
                if k not in ("trade_count_ge_30", "pairs_positive_ge_3")
            }
            cf_pass_excl_tc = all(gates_excl_tradecount.values())
            cf_pass_excl_tc_pp = all(gates_excl_tc_and_pp.values())
            if f.get("passes"):
                any_fold_passed += 1
            if cf_pass_excl_tc:
                cf_passed_minus_tradecount += 1
            if cf_pass_excl_tc_pp:
                cf_passed_minus_tradecount_and_pairspos += 1
            per_fold.append(
                {
                    "fold_index": f["fold_index"],
                    "test_start": f["test_start"],
                    "test_end": f["test_end"],
                    "trade_count": f["trade_count"],
                    "expectancy_r": f["expectancy_r"],
                    "pairs_positive": f["pairs_positive"],
                    "single_pair_dominance_pct": (
                        f["single_pair_dominance_pct"]
                    ),
                    "gates": g,
                    "failed_gates": failed,
                    "passes": f["passes"],
                    "counterfactual_passes_excluding_trade_count_gate": (
                        cf_pass_excl_tc
                    ),
                    "counterfactual_passes_excluding_trade_count_and_pairs_positive_gates": (
                        cf_pass_excl_tc_pp
                    ),
                }
            )

        # Pair-fold cell trade-count distribution.
        bucket_counts: Counter[str] = Counter()
        pair_fold_cells: list[dict[str, Any]] = []
        for f in folds:
            for pr in f["pair_runs"]:
                n = int(pr["trade_count"])
                bucket_counts[_bucket(n)] += 1
                pair_fold_cells.append(
                    {
                        "fold_index": f["fold_index"],
                        "pair": pr["instrument"],
                        "trade_count": n,
                        "expectancy_r": pr["expectancy_r"],
                        "return_pct": pr["return_pct"],
                    }
                )
        bucket_dist = {b: int(bucket_counts.get(b, 0)) for b in CELL_BUCKETS_ORDER}

        out["by_cost"][cost] = {
            "verdict": agg.get("aggregate_pass") and "PASS" or "FAIL",
            "aggregate_metrics": {
                k: agg.get(k)
                for k in (
                    "aggregate_expectancy_r",
                    "aggregate_return_pct",
                    "profit_factor",
                    "total_trades",
                    "fold_pass_rate",
                    "folds_passing",
                    "pairs_positive_count",
                    "single_pair_dominance_pct",
                    "median_per_fold_expectancy_r",
                    "trade_level_cumulative_r",
                    "expectancy_min_applied",
                    "profit_factor_min_applied",
                )
            },
            "aggregate_gates_passed": passed_agg_gates,
            "aggregate_gates_failed": failed_agg_gates,
            "per_fold": per_fold,
            "per_fold_gate_failure_counts": dict(
                sorted(gate_fail_counter.items())
            ),
            "folds_passing_actual": any_fold_passed,
            "folds_passing_counterfactual_no_trade_count_gate": (
                cf_passed_minus_tradecount
            ),
            "folds_passing_counterfactual_no_trade_count_or_pairs_positive": (
                cf_passed_minus_tradecount_and_pairspos
            ),
            "pair_fold_cell_distribution": bucket_dist,
            "pair_fold_cell_count": sum(bucket_dist.values()),
            "pair_fold_cells": pair_fold_cells,
        }

    # Summary across base + 2xcost.
    base = out["by_cost"].get("base", {})
    twox = out["by_cost"].get("2xcost", {})
    out["summary"] = {
        "primary_failing_aggregate_gates_base": base.get(
            "aggregate_gates_failed", []
        ),
        "primary_failing_aggregate_gates_2xcost": twox.get(
            "aggregate_gates_failed", []
        ),
        "all_folds_fail_actual": (
            base.get("folds_passing_actual", -1) == 0
            and twox.get("folds_passing_actual", -1) == 0
        ),
        "every_fold_fails_trade_count_ge_30_base": (
            base.get("per_fold_gate_failure_counts", {}).get(
                "trade_count_ge_30", 0
            )
            == fold_count_per_fold
        ),
        "every_fold_fails_trade_count_ge_30_2xcost": (
            twox.get("per_fold_gate_failure_counts", {}).get(
                "trade_count_ge_30", 0
            )
            == fold_count_per_fold
        ),
        "fold_pass_counterfactual_drop_trade_count_base": (
            base.get(
                "folds_passing_counterfactual_no_trade_count_gate", -1
            )
        ),
        "fold_pass_counterfactual_drop_trade_count_2xcost": (
            twox.get(
                "folds_passing_counterfactual_no_trade_count_gate", -1
            )
        ),
        "any_fold_failed_expectancy_despite_positive_aggregate_base": (
            any(
                pf["failed_gates"]
                and "expectancy_r_ge_0" in pf["failed_gates"]
                for pf in base.get("per_fold", [])
            )
        ),
        "any_fold_failed_pairs_positive_base": any(
            pf["failed_gates"]
            and "pairs_positive_ge_3" in pf["failed_gates"]
            for pf in base.get("per_fold", [])
        ),
        "any_fold_failed_single_pair_dominance_base": any(
            pf["failed_gates"]
            and "single_pair_dominance_le_60pct" in pf["failed_gates"]
            for pf in base.get("per_fold", [])
        ),
        "pair_fold_cell_distribution_base": base.get(
            "pair_fold_cell_distribution", {}
        ),
        "pair_fold_cell_distribution_2xcost": twox.get(
            "pair_fold_cell_distribution", {}
        ),
    }
    return out


def render_md(autopsy_obj: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# CAMPAIGN_015 — Gate-Failure Autopsy")
    lines.append("")
    lines.append(
        f"**Strategy:** `{autopsy_obj['strategy_name']} "
        f"{autopsy_obj.get('strategy_version', '')}`"
    )
    lines.append(f"**Config hash:** `{autopsy_obj.get('config_hash')}`")
    lines.append(f"**Runner verdict:** **{autopsy_obj['runner_verdict']}**")
    lines.append(
        f"**Approval status:** **{autopsy_obj['approval_status']}** "
        f"— `configs/approved_strategies.yaml` remains `approved: []`."
    )
    lines.append("")
    lines.append(
        "> Diagnostic only. Counterfactual fold-pass figures are "
        "NON-GATING; the runner verdict remains REJECT."
    )
    lines.append("")

    for cost, block in autopsy_obj["by_cost"].items():
        lines.append(f"## {cost} cost")
        am = block["aggregate_metrics"]
        lines.append("")
        lines.append("Aggregate metrics:")
        for k, v in am.items():
            if isinstance(v, float):
                lines.append(f"- `{k}` = {v:+.4f}" if v < 0 or "expect" in k or "trade_level" in k else f"- `{k}` = {v:.4f}")
            else:
                lines.append(f"- `{k}` = {v}")
        lines.append("")
        lines.append(
            f"**Aggregate gates failed:** "
            f"{block['aggregate_gates_failed'] or '_none_'}"
        )
        lines.append(
            f"**Aggregate gates passed:** "
            f"{block['aggregate_gates_passed'] or '_none_'}"
        )
        lines.append("")
        lines.append("Per-fold:")
        lines.append("")
        lines.append(
            "| fold | trades | exp_R | pairs+ | spd% | "
            "trade_count_ge_30 | expectancy_r_ge_0 | "
            "pairs_positive_ge_3 | spd_le_60pct | "
            "passes | CF-pass (no trade-count) |"
        )
        lines.append(
            "|---|---|---|---|---|---|---|---|---|---|---|"
        )
        for pf in block["per_fold"]:
            g = pf["gates"]

            def _tick(b: bool) -> str:
                return "✓" if b else "✗"

            lines.append(
                f"| {pf['fold_index']} "
                f"| {pf['trade_count']} "
                f"| {pf['expectancy_r']:+.3f} "
                f"| {pf['pairs_positive']} "
                f"| {pf['single_pair_dominance_pct']:.1f} "
                f"| {_tick(g['trade_count_ge_30'])} "
                f"| {_tick(g['expectancy_r_ge_0'])} "
                f"| {_tick(g['pairs_positive_ge_3'])} "
                f"| {_tick(g['single_pair_dominance_le_60pct'])} "
                f"| {_tick(pf['passes'])} "
                f"| {_tick(pf['counterfactual_passes_excluding_trade_count_gate'])} |"
            )
        lines.append("")
        lines.append(
            f"**Per-fold gate failure counts:** "
            f"{block['per_fold_gate_failure_counts']}"
        )
        lines.append(
            f"**Folds passing (actual / gating):** "
            f"{block['folds_passing_actual']} / "
            f"{len(block['per_fold'])}"
        )
        lines.append(
            f"**Folds passing (counterfactual, NON-GATING, drop "
            f"`trade_count_ge_30`):** "
            f"{block['folds_passing_counterfactual_no_trade_count_gate']} "
            f"/ {len(block['per_fold'])}"
        )
        lines.append(
            f"**Folds passing (counterfactual, NON-GATING, drop "
            f"`trade_count_ge_30` AND `pairs_positive_ge_3`):** "
            f"{block['folds_passing_counterfactual_no_trade_count_or_pairs_positive']} "
            f"/ {len(block['per_fold'])}"
        )
        lines.append("")
        lines.append("Pair-fold cell trade-count distribution:")
        for b, n in block["pair_fold_cell_distribution"].items():
            lines.append(f"- `{b}` = {n}")
        lines.append("")

    s = autopsy_obj["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"- Primary failing aggregate gates (base): "
        f"`{s['primary_failing_aggregate_gates_base']}`"
    )
    lines.append(
        f"- Primary failing aggregate gates (2xcost): "
        f"`{s['primary_failing_aggregate_gates_2xcost']}`"
    )
    lines.append(
        f"- All folds fail in both cost regimes: "
        f"{s['all_folds_fail_actual']}"
    )
    lines.append(
        f"- Every fold fails `trade_count_ge_30` (base): "
        f"{s['every_fold_fails_trade_count_ge_30_base']}"
    )
    lines.append(
        f"- Every fold fails `trade_count_ge_30` (2xcost): "
        f"{s['every_fold_fails_trade_count_ge_30_2xcost']}"
    )
    lines.append(
        f"- Any fold failed expectancy_r_ge_0 despite positive "
        f"aggregate (base): "
        f"{s['any_fold_failed_expectancy_despite_positive_aggregate_base']}"
    )
    lines.append(
        f"- Any fold failed pairs_positive_ge_3 (base): "
        f"{s['any_fold_failed_pairs_positive_base']}"
    )
    lines.append(
        f"- Any fold failed single_pair_dominance_le_60pct (base): "
        f"{s['any_fold_failed_single_pair_dominance_base']}"
    )
    lines.append("")
    lines.append(autopsy_obj["counterfactual_disclaimer"])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-result", required=True, type=Path)
    ap.add_argument("--fold-detail", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    args = ap.parse_args(argv)

    if not args.gate_result.exists():
        print(
            f"BLOCKED: gate-result path does not exist: {args.gate_result}",
            file=sys.stderr,
        )
        return 2
    if not args.fold_detail.exists():
        print(
            f"BLOCKED: fold-detail path does not exist: {args.fold_detail}",
            file=sys.stderr,
        )
        return 2

    gate_result = json.loads(args.gate_result.read_text(encoding="utf-8"))
    fold_detail = json.loads(args.fold_detail.read_text(encoding="utf-8"))

    obj = autopsy(gate_result, fold_detail)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(obj, indent=2, default=str), encoding="utf-8"
    )
    args.out_md.write_text(render_md(obj), encoding="utf-8")
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
