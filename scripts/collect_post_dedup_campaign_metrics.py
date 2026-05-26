#!/usr/bin/env python3
"""Collect comparable dedup-safe campaign metrics for post-dedup meta-analysis.

Reads CAMPAIGN_011 deduped null baseline and CAMPAIGN_015/016/017 gate +
fold-detail JSON. Emits a metric matrix for cross-campaign comparison.

This is descriptive research tooling. It does NOT approve strategies,
relax gates, or change ``approved_strategies.yaml``.

Usage:
    python scripts/collect_post_dedup_campaign_metrics.py
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

NULL_BASELINE_PATH = REPO_ROOT / "research/null_baselines/campaign_011_deduped_null_baseline.json"

CAMPAIGN_PATHS: dict[str, dict[str, Path]] = {
    "CAMPAIGN_015": {
        "gate_result": REPO_ROOT
        / "backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/gate_result.json",
        "fold_detail": REPO_ROOT
        / "backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/fold_detail.json",
        "anti_overfit": REPO_ROOT
        / "research/campaign_015/diagnostics/null_and_anti_overfit_deduped.json",
        "backtrader": REPO_ROOT
        / "research/campaign_015/diagnostics/backtrader_fold_window_deduped/fold_window_comparison.json",
        "backtests_root": REPO_ROOT / "backtests/CAMPAIGN_015_failed_breakout_reversal_deduped",
    },
    "CAMPAIGN_016": {
        "gate_result": REPO_ROOT
        / "backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/gate_result.json",
        "fold_detail": REPO_ROOT
        / "backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/fold_detail.json",
        "anti_overfit": REPO_ROOT
        / "research/campaign_016/diagnostics/null_and_anti_overfit.json",
        "backtrader": REPO_ROOT
        / "research/campaign_016/diagnostics/backtrader_comparison.json",
        "backtests_root": REPO_ROOT / "backtests/CAMPAIGN_016_weekly_cross_sectional_momentum",
    },
    "CAMPAIGN_017": {
        "gate_result": REPO_ROOT
        / "backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/gate_result.json",
        "fold_detail": REPO_ROOT
        / "backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/fold_detail.json",
        "anti_overfit": REPO_ROOT
        / "research/campaign_017/diagnostics/null_and_anti_overfit.json",
        "backtrader": REPO_ROOT
        / "research/campaign_017/diagnostics/backtrader_comparison.json",
        "backtests_root": REPO_ROOT / "backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout",
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _optional_load(path: Path) -> dict[str, Any] | None:
    if path.is_file():
        return _load_json(path)
    return None


def _backtrader_status(backtrader: dict[str, Any] | None) -> str:
    if backtrader is None:
        return "MISSING"
    classification = backtrader.get("classification") or backtrader.get(
        "divergence_classification",
    )
    if classification is None:
        return "UNKNOWN"
    non_blocking = backtrader.get("non_decision_blocking") or backtrader.get(
        "decision_blocking",
    ) is False
    suffix = ", non-decision-blocking" if non_blocking else ""
    return f"{classification}{suffix}"


def _aggregate_pair_runs(fold_detail: dict[str, Any], cost: str = "base") -> list[dict[str, Any]]:
    """Sum pair-level metrics across all folds for a cost label."""
    by_instrument: dict[str, dict[str, Any]] = {}
    folds = fold_detail.get("by_cost", {}).get(cost, {}).get("folds", [])
    for fold in folds:
        for pr in fold.get("pair_runs", []):
            inst = pr["instrument"]
            bucket = by_instrument.setdefault(
                inst,
                {
                    "instrument": inst,
                    "trade_count": 0,
                    "long_trades": 0,
                    "short_trades": 0,
                    "r_sum": 0.0,
                    "folds_seen": 0,
                    "folds_positive": 0,
                },
            )
            tc = int(pr.get("trade_count", 0))
            exp_r = float(pr.get("expectancy_r", 0.0))
            bucket["trade_count"] += tc
            bucket["long_trades"] += int(pr.get("long_trades", 0))
            bucket["short_trades"] += int(pr.get("short_trades", 0))
            bucket["r_sum"] += exp_r * tc
            bucket["folds_seen"] += 1
            if exp_r > 0:
                bucket["folds_positive"] += 1
    out: list[dict[str, Any]] = []
    for inst, b in sorted(by_instrument.items()):
        tc = b["trade_count"]
        exp_r = b["r_sum"] / tc if tc else 0.0
        out.append(
            {
                "instrument": inst,
                "trade_count": tc,
                "expectancy_r": exp_r,
                "long_trades": b["long_trades"],
                "short_trades": b["short_trades"],
                "folds_positive": b["folds_positive"],
                "folds_seen": b["folds_seen"],
            },
        )
    return out


def _fold_expectancies(fold_detail: dict[str, Any], cost: str = "base") -> list[dict[str, Any]]:
    folds = fold_detail.get("by_cost", {}).get(cost, {}).get("folds", [])
    return [
        {
            "fold_index": f["fold_index"],
            "test_start": f.get("test_start"),
            "test_end": f.get("test_end"),
            "trade_count": f.get("trade_count"),
            "expectancy_r": f.get("expectancy_r"),
            "profit_factor": f.get("profit_factor"),
            "passes": f.get("passes"),
        }
        for f in folds
    ]


def _cost_sensitivity(base_exp: float, exp_2x: float) -> dict[str, Any]:
    delta = exp_2x - base_exp
    pct = (delta / abs(base_exp) * 100.0) if base_exp != 0 else None
    return {
        "base_exp_r": base_exp,
        "2x_exp_r": exp_2x,
        "delta_exp_r": delta,
        "delta_pct_of_base": pct,
    }


def build_null_row(null_baseline: dict[str, Any]) -> dict[str, Any]:
    agg = null_baseline["aggregate"]
    null_std = null_baseline["null_distribution"]["per_fold_expectancy_r_std"]
    return {
        "campaign_id": null_baseline["campaign_id"],
        "strategy_name": null_baseline["strategy_name"],
        "strategy_version": null_baseline["strategy_version"],
        "role": "null_baseline",
        "verdict": null_baseline["overall_verdict"],
        "base_exp_r": agg["aggregate_expectancy_r"],
        "2x_exp_r": None,
        "gap_vs_deduped_null": 0.0,
        "trade_count": agg["total_trades"],
        "fold_pass_count": agg["folds_passing"],
        "fold_count": agg["fold_count"],
        "pairs_positive": agg["pairs_positive_count"],
        "profit_factor": agg["profit_factor"],
        "single_pair_dominance_pct": agg.get("single_pair_dominance_pct"),
        "single_fold_dominance_pct": agg.get("single_fold_dominance_pct"),
        "null_fold_std": null_std,
        "anti_overfit_label": None,
        "backtrader_status": "n/a",
        "dedupe_input": null_baseline.get("dedupe_probe", {}).get("status"),
        "per_pair": null_baseline.get("per_pair", []),
        "per_fold": null_baseline.get("per_fold", []),
        "cost_sensitivity": None,
    }


def build_campaign_row(
    campaign_id: str,
    gate_result: dict[str, Any],
    fold_detail: dict[str, Any],
    anti_overfit: dict[str, Any] | None,
    backtrader: dict[str, Any] | None,
    null_centre_exp_r: float,
) -> dict[str, Any]:
    base = gate_result["by_cost"]["base"]
    exp_2x = gate_result["by_cost"]["2xcost"]["aggregate_expectancy_r"]
    base_exp = base["aggregate_expectancy_r"]
    per_pair = _aggregate_pair_runs(fold_detail, "base")
    per_fold = _fold_expectancies(fold_detail, "base")

    long_total = sum(p["long_trades"] for p in per_pair)
    short_total = sum(p["short_trades"] for p in per_pair)

    return {
        "campaign_id": campaign_id,
        "strategy_name": gate_result["strategy_name"],
        "strategy_version": gate_result["strategy_version"],
        "role": "candidate",
        "verdict": gate_result["verdict"],
        "base_exp_r": base_exp,
        "2x_exp_r": exp_2x,
        "gap_vs_deduped_null": base_exp - null_centre_exp_r,
        "trade_count": base["total_trades"],
        "fold_pass_count": base["folds_passing"],
        "fold_count": gate_result.get("fold_count"),
        "pairs_positive": base.get("pairs_positive_count"),
        "profit_factor": base.get("profit_factor"),
        "single_pair_dominance_pct": base.get("single_pair_dominance_pct"),
        "median_per_fold_expectancy_r": base.get("median_per_fold_expectancy_r"),
        "trade_level_cumulative_r": base.get("trade_level_cumulative_r"),
        "anti_overfit_label": (anti_overfit or {}).get("anti_overfit_label"),
        "gap_vs_null_from_anti_overfit": (anti_overfit or {}).get("gap_vs_null_exp_r"),
        "backtrader_status": _backtrader_status(backtrader),
        "dedupe_input": gate_result.get("preflight", {}).get("input_classification"),
        "long_trades": long_total,
        "short_trades": short_total,
        "per_pair": per_pair,
        "per_fold": per_fold,
        "cost_sensitivity": _cost_sensitivity(base_exp, exp_2x),
    }


def collect_metrics(
    null_baseline: dict[str, Any],
    campaigns: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    null_centre = null_baseline["aggregate"]["aggregate_expectancy_r"]
    null_std = null_baseline["null_distribution"]["per_fold_expectancy_r_std"]

    rows = [build_null_row(null_baseline)]
    for cid, bundle in campaigns.items():
        rows.append(
            build_campaign_row(
                cid,
                bundle["gate_result"],
                bundle["fold_detail"],
                bundle.get("anti_overfit"),
                bundle.get("backtrader"),
                null_centre,
            ),
        )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "null_reference": {
            "campaign_id": "CAMPAIGN_011",
            "aggregate_expectancy_r": null_centre,
            "per_fold_expectancy_r_std": null_std,
            "path": "research/null_baselines/campaign_011_deduped_null_baseline.json",
        },
        "campaigns": rows,
        "disclaimer": (
            "Descriptive meta-analysis only. WITHIN_NULL does not imply edge. "
            "No strategy approved. approved: []"
        ),
    }


def render_md(matrix: dict[str, Any]) -> str:
    null_ref = matrix["null_reference"]
    lines = [
        "# Post-Dedup Campaign Metric Matrix",
        "",
        f"**Generated:** {matrix['generated_at']}",
        "",
        f"> Null centre exp_r = **{null_ref['aggregate_expectancy_r']:.6f}** · "
        f"fold std = **{null_ref['per_fold_expectancy_r_std']:.4f}**",
        "",
        "> Descriptive only — does not approve any strategy.",
        "",
        "## Headline comparison",
        "",
        "| campaign | strategy | verdict | base exp_r | 2x exp_r | gap vs null | trades | fold pass | +pairs | PF | anti-overfit | Backtrader |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in matrix["campaigns"]:
        exp2 = row.get("2x_exp_r")
        exp2_s = f"{exp2:.4f}" if exp2 is not None else "n/a"
        gap = row.get("gap_vs_deduped_null")
        gap_s = f"{gap:+.4f}" if gap is not None else "n/a"
        pf = row.get("profit_factor")
        pf_s = f"{pf:.3f}" if pf is not None else "n/a"
        ao = row.get("anti_overfit_label") or "n/a"
        lines.append(
            f"| {row['campaign_id']} | {row['strategy_name']} | {row['verdict']} | "
            f"{row['base_exp_r']:.4f} | {exp2_s} | {gap_s} | {row['trade_count']} | "
            f"{row['fold_pass_count']}/{row['fold_count']} | "
            f"{row.get('pairs_positive', 'n/a')} | {pf_s} | {ao} | "
            f"{row.get('backtrader_status', 'n/a')} |",
        )

    lines.extend(["", "## Per-campaign pair expectancy (base cost)", ""])
    for row in matrix["campaigns"]:
        if row["role"] == "null_baseline":
            lines.append(f"### {row['campaign_id']} (null baseline)")
        else:
            lines.append(f"### {row['campaign_id']} — {row['strategy_name']}")
        lines.append("")
        lines.append("| pair | trades | exp_r | folds + |")
        lines.append("|---|---:|---:|---:|")
        for p in row.get("per_pair", []):
            if "instrument" in p:
                inst = p["instrument"]
                tc = p.get("trade_count", 0)
                exp = p.get("expectancy_r", 0)
                fp = p.get("folds_positive", "n/a")
            else:
                inst = p["instrument"]
                tc = p.get("trade_count", 0)
                exp = p.get("expectancy_r", 0)
                fp = "n/a"
            lines.append(f"| {inst} | {tc} | {exp:.4f} | {fp} |")
        lines.append("")

    lines.extend(["", "## Per-campaign fold expectancy (base cost)", ""])
    for row in matrix["campaigns"]:
        lines.append(f"### {row['campaign_id']}")
        lines.append("")
        lines.append("| fold | window | trades | exp_r | pass |")
        lines.append("|---:|---|---:|---:|:---:|")
        for f in row.get("per_fold", []):
            window = f"{f.get('test_start', '?')}..{f.get('test_end', '?')}"
            pass_s = "✓" if f.get("passes") or f.get("passes_gates") else "✗"
            lines.append(
                f"| {f['fold_index']} | {window} | {f.get('trade_count', 'n/a')} | "
                f"{f.get('expectancy_r', 0):.4f} | {pass_s} |",
            )
        lines.append("")

    return "\n".join(lines)


def load_campaign_bundle(paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "gate_result": _load_json(paths["gate_result"]),
        "fold_detail": _load_json(paths["fold_detail"]),
        "anti_overfit": _optional_load(paths["anti_overfit"]),
        "backtrader": _optional_load(paths["backtrader"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--null-baseline",
        type=Path,
        default=NULL_BASELINE_PATH,
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=REPO_ROOT / "research/post_dedup_meta/campaign_metric_matrix.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=REPO_ROOT / "research/post_dedup_meta/campaign_metric_matrix.md",
    )
    parser.add_argument(
        "--out-docs-md",
        type=Path,
        default=REPO_ROOT / "docs/research/POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md",
    )
    args = parser.parse_args(argv)

    null_baseline = _load_json(args.null_baseline)
    campaigns = {
        cid: load_campaign_bundle(paths) for cid, paths in CAMPAIGN_PATHS.items()
    }
    matrix = collect_metrics(null_baseline, campaigns)
    md = render_md(matrix)

    for path in (args.out_json, args.out_md, args.out_docs_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(md + "\n", encoding="utf-8")
    args.out_docs_md.write_text(md + "\n", encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")
    print(f"Wrote {args.out_docs_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
