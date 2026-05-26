#!/usr/bin/env python3
"""CAMPAIGN_015 concentration + fragility diagnostics — diagnostic only.

Reads the CAMPAIGN_015 rehydrate ``fold_detail.json`` (which already
contains per-fold, per-pair, per-trade R series) and emits:

- top-K trade / pair / fold / pair-fold-cell contributions to total R
- leave-one-out by fold and by pair (aggregate R, expectancy, gate
  pass count)
- trade-R distribution (min, p10, p25, median, p75, p90, max)
- exit reason rollup
- median vs mean per-fold expectancy gap

This is a diagnostic. It does NOT change `approved_strategies.yaml`
and does NOT revise the runner verdict.

Usage:
    python scripts/diagnose_campaign_015_concentration.py \
        --fold-detail research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json \
        --out-json research/campaign_015/diagnostics/concentration.json \
        --out-md   research/campaign_015/diagnostics/concentration.md
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _percentile(sorted_vals: list[float], p: float) -> float:
    """Linear-interpolation percentile of a SORTED list."""
    if not sorted_vals:
        return float("nan")
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    k = (len(sorted_vals) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(sorted_vals) - 1)
    if lo == hi:
        return float(sorted_vals[lo])
    frac = k - lo
    return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)


def _fold_gates_eval(
    *,
    trades: int,
    expectancy_r: float,
    pairs_positive: int,
    spd_pct: float,
    fold_gate_spec: dict[str, Any],
) -> bool:
    return (
        trades >= int(fold_gate_spec.get("trade_count_min", 30))
        and expectancy_r >= float(fold_gate_spec.get("expectancy_r_min", 0.0))
        and pairs_positive
        >= int(fold_gate_spec.get("pairs_positive_min", 3))
        and spd_pct
        <= float(fold_gate_spec.get("single_pair_dominance_max_pct", 60.0))
    )


def concentration(fold_detail: dict[str, Any]) -> dict[str, Any]:
    """Pure-function concentration math; unit-testable."""
    out: dict[str, Any] = {
        "campaign_id": fold_detail.get("campaign_id"),
        "strategy_name": fold_detail.get("strategy_name"),
        "strategy_version": fold_detail.get("strategy_version"),
        "config_hash": fold_detail.get("config_hash"),
        "by_cost": {},
    }
    fold_gate_spec = fold_detail.get("fold_gates", {})

    for cost, block in fold_detail.get("by_cost", {}).items():
        folds = block["folds"]
        # Flatten all trades with provenance.
        trades: list[dict[str, Any]] = []
        per_fold_total_r: dict[int, float] = defaultdict(float)
        per_pair_total_r: dict[str, float] = defaultdict(float)
        per_cell_total_r: dict[tuple[int, str], float] = defaultdict(float)
        per_cell_trades: dict[tuple[int, str], int] = defaultdict(int)
        per_pair_trade_count: dict[str, int] = defaultdict(int)
        per_fold_trade_count: dict[int, int] = defaultdict(int)
        exit_counter: Counter[str] = Counter()
        rejection_counter: Counter[str] = Counter()
        for f in folds:
            for pr in f["pair_runs"]:
                key = (f["fold_index"], pr["instrument"])
                for r in pr.get("trade_r_series", []):
                    trades.append(
                        {
                            "fold_index": f["fold_index"],
                            "pair": pr["instrument"],
                            "r": float(r),
                        }
                    )
                    per_fold_total_r[f["fold_index"]] += float(r)
                    per_pair_total_r[pr["instrument"]] += float(r)
                    per_cell_total_r[key] += float(r)
                    per_cell_trades[key] += 1
                    per_pair_trade_count[pr["instrument"]] += 1
                    per_fold_trade_count[f["fold_index"]] += 1
                for k, v in pr.get("exit_reason_counts", {}).items():
                    exit_counter[k] += int(v)
                for k, v in pr.get("rejection_counts", {}).items():
                    rejection_counter[k] += int(v)

        total_r = sum(t["r"] for t in trades)
        total_trades = len(trades)
        positive_trades = [t for t in trades if t["r"] > 0]
        negative_trades = [t for t in trades if t["r"] < 0]
        gross_pos_r = sum(t["r"] for t in positive_trades)
        gross_neg_r = sum(t["r"] for t in negative_trades)

        # Top-K trade contributions.
        sorted_pos = sorted(
            positive_trades, key=lambda t: t["r"], reverse=True
        )
        sorted_neg = sorted(negative_trades, key=lambda t: t["r"])
        top_trade_share = (
            {
                f"top_{k}_positive_trade_share_of_gross_positive_r": (
                    sum(t["r"] for t in sorted_pos[:k]) / gross_pos_r
                    if gross_pos_r
                    else 0.0
                )
                for k in (1, 3, 5)
            }
        )
        top_trade_share_of_total = {
            f"top_{k}_positive_trade_share_of_total_r": (
                sum(t["r"] for t in sorted_pos[:k]) / total_r
                if total_r
                else 0.0
            )
            for k in (1, 3, 5)
        }
        top_trade_details = [
            {"fold_index": t["fold_index"], "pair": t["pair"], "r": t["r"]}
            for t in sorted_pos[:5]
        ]
        worst_trade_details = [
            {"fold_index": t["fold_index"], "pair": t["pair"], "r": t["r"]}
            for t in sorted_neg[:5]
        ]

        # Top-1 fold / pair / cell contribution.
        if per_fold_total_r:
            top_fold = max(per_fold_total_r.items(), key=lambda kv: kv[1])
        else:
            top_fold = (None, 0.0)
        if per_pair_total_r:
            top_pair = max(per_pair_total_r.items(), key=lambda kv: kv[1])
        else:
            top_pair = (None, 0.0)
        if per_cell_total_r:
            top_cell = max(per_cell_total_r.items(), key=lambda kv: kv[1])
        else:
            top_cell = ((None, None), 0.0)

        top_fold_share = top_fold[1] / total_r if total_r else 0.0
        top_pair_share = top_pair[1] / total_r if total_r else 0.0
        top_cell_share = top_cell[1] / total_r if total_r else 0.0

        # Leave-one-out by fold.
        per_fold_expectancy = [
            float(f["expectancy_r"]) for f in folds if f["trade_count"] > 0
        ]
        mean_pf_exp = (
            statistics.fmean(per_fold_expectancy) if per_fold_expectancy else 0.0
        )
        median_pf_exp = (
            statistics.median(per_fold_expectancy) if per_fold_expectancy else 0.0
        )
        loo_fold: list[dict[str, Any]] = []
        for f in folds:
            drop_idx = f["fold_index"]
            kept_trades = [t for t in trades if t["fold_index"] != drop_idx]
            kept_n = len(kept_trades)
            kept_sum_r = sum(t["r"] for t in kept_trades)
            kept_exp_r = kept_sum_r / kept_n if kept_n else 0.0
            # pairs positive after dropping this fold
            kept_pair_r: dict[str, float] = defaultdict(float)
            for t in kept_trades:
                kept_pair_r[t["pair"]] += t["r"]
            pairs_pos = sum(1 for r in kept_pair_r.values() if r > 0)
            loo_fold.append(
                {
                    "dropped_fold": drop_idx,
                    "remaining_trades": kept_n,
                    "remaining_total_r": kept_sum_r,
                    "remaining_expectancy_r": kept_exp_r,
                    "remaining_pairs_positive": pairs_pos,
                }
            )

        # Leave-one-out by pair.
        loo_pair: list[dict[str, Any]] = []
        all_pairs = sorted(per_pair_total_r.keys())
        for drop_pair in all_pairs:
            kept_trades = [t for t in trades if t["pair"] != drop_pair]
            kept_n = len(kept_trades)
            kept_sum_r = sum(t["r"] for t in kept_trades)
            kept_exp_r = kept_sum_r / kept_n if kept_n else 0.0
            # Per-fold gate recompute under LOO-pair.
            fold_pass_after_drop = 0
            for f in folds:
                fold_trades = [
                    t
                    for t in trades
                    if t["fold_index"] == f["fold_index"]
                    and t["pair"] != drop_pair
                ]
                if not fold_trades:
                    continue
                f_pair_r: dict[str, float] = defaultdict(float)
                for t in fold_trades:
                    f_pair_r[t["pair"]] += t["r"]
                pairs_pos_f = sum(1 for r in f_pair_r.values() if r > 0)
                f_total = sum(t["r"] for t in fold_trades)
                f_exp = f_total / len(fold_trades) if fold_trades else 0.0
                # SPD recompute: gross-positive-R share, matching the runner.
                gross_pos = {p: r for p, r in f_pair_r.items() if r > 0}
                spd_pct = (
                    100.0 * (max(gross_pos.values()) / sum(gross_pos.values()))
                    if gross_pos
                    else 0.0
                )
                if _fold_gates_eval(
                    trades=len(fold_trades),
                    expectancy_r=f_exp,
                    pairs_positive=pairs_pos_f,
                    spd_pct=spd_pct,
                    fold_gate_spec=fold_gate_spec,
                ):
                    fold_pass_after_drop += 1
            loo_pair.append(
                {
                    "dropped_pair": drop_pair,
                    "remaining_trades": kept_n,
                    "remaining_total_r": kept_sum_r,
                    "remaining_expectancy_r": kept_exp_r,
                    "fold_pass_count_after_drop": fold_pass_after_drop,
                }
            )

        # Trade-R distribution.
        rs_sorted = sorted(t["r"] for t in trades)
        dist = {
            "min": rs_sorted[0] if rs_sorted else float("nan"),
            "p10": _percentile(rs_sorted, 0.10),
            "p25": _percentile(rs_sorted, 0.25),
            "median": _percentile(rs_sorted, 0.50),
            "p75": _percentile(rs_sorted, 0.75),
            "p90": _percentile(rs_sorted, 0.90),
            "max": rs_sorted[-1] if rs_sorted else float("nan"),
        }

        out["by_cost"][cost] = {
            "total_trades": total_trades,
            "total_r": total_r,
            "gross_positive_r": gross_pos_r,
            "gross_negative_r": gross_neg_r,
            "implied_profit_factor": (
                (gross_pos_r / abs(gross_neg_r)) if gross_neg_r else float("inf")
            ),
            "per_fold_total_r": {
                int(k): v for k, v in sorted(per_fold_total_r.items())
            },
            "per_pair_total_r": dict(sorted(per_pair_total_r.items())),
            "per_cell_total_r": {
                f"fold_{fi:02d}_{p}": v
                for (fi, p), v in sorted(per_cell_total_r.items())
            },
            "per_cell_trade_counts": {
                f"fold_{fi:02d}_{p}": v
                for (fi, p), v in sorted(per_cell_trades.items())
            },
            "top_positive_trades": top_trade_details,
            "worst_negative_trades": worst_trade_details,
            **top_trade_share,
            **top_trade_share_of_total,
            "top_fold_index": top_fold[0],
            "top_fold_r": top_fold[1],
            "top_fold_share_of_total_r": top_fold_share,
            "top_pair": top_pair[0],
            "top_pair_r": top_pair[1],
            "top_pair_share_of_total_r": top_pair_share,
            "top_cell": (
                f"fold_{top_cell[0][0]:02d}_{top_cell[0][1]}"
                if top_cell[0][0] is not None
                else None
            ),
            "top_cell_r": top_cell[1],
            "top_cell_share_of_total_r": top_cell_share,
            "mean_per_fold_expectancy_r": mean_pf_exp,
            "median_per_fold_expectancy_r": median_pf_exp,
            "mean_minus_median_per_fold_expectancy_r": (
                mean_pf_exp - median_pf_exp
            ),
            "trade_r_distribution": dist,
            "exit_reason_counts": dict(exit_counter),
            "rejection_counts": dict(rejection_counter),
            "loo_by_fold": loo_fold,
            "loo_by_pair": loo_pair,
        }

    return out


def render_md(c: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# CAMPAIGN_015 — Concentration & Fragility Diagnostics")
    lines.append("")
    lines.append(
        f"**Strategy:** `{c.get('strategy_name')} "
        f"{c.get('strategy_version', '')}`"
    )
    lines.append(f"**Config hash:** `{c.get('config_hash')}`")
    lines.append("")
    lines.append(
        "> Diagnostic only. Does NOT approve any strategy, does NOT relax "
        "any gate, does NOT revise the verdict."
    )
    lines.append("")
    for cost, b in c["by_cost"].items():
        lines.append(f"## {cost} cost")
        lines.append("")
        lines.append(f"- total_trades = **{b['total_trades']}**")
        lines.append(f"- total_r = **{b['total_r']:+.4f}**")
        lines.append(f"- gross_positive_r = **{b['gross_positive_r']:+.4f}**")
        lines.append(f"- gross_negative_r = **{b['gross_negative_r']:+.4f}**")
        lines.append(
            f"- implied profit factor (from trade-R) = "
            f"**{b['implied_profit_factor']:.4f}**"
        )
        lines.append("")
        lines.append("### Top-trade concentration")
        lines.append("")
        lines.append("| trade rank | fold | pair | R |")
        lines.append("|---|---|---|---|")
        for i, t in enumerate(b["top_positive_trades"], 1):
            lines.append(
                f"| {i} | {t['fold_index']} | {t['pair']} | {t['r']:+.4f} |"
            )
        lines.append("")
        lines.append(
            f"- Top-1 positive trade contributes "
            f"**{100*b['top_1_positive_trade_share_of_total_r']:.1f}%** of "
            f"total R (and **{100*b['top_1_positive_trade_share_of_gross_positive_r']:.1f}%** of gross positive R)."
        )
        lines.append(
            f"- Top-3 positive trades contribute "
            f"**{100*b['top_3_positive_trade_share_of_total_r']:.1f}%** of "
            f"total R."
        )
        lines.append(
            f"- Top-5 positive trades contribute "
            f"**{100*b['top_5_positive_trade_share_of_total_r']:.1f}%** of "
            f"total R."
        )
        lines.append("")
        lines.append("### Worst losers")
        lines.append("")
        lines.append("| trade rank | fold | pair | R |")
        lines.append("|---|---|---|---|")
        for i, t in enumerate(b["worst_negative_trades"], 1):
            lines.append(
                f"| {i} | {t['fold_index']} | {t['pair']} | {t['r']:+.4f} |"
            )
        lines.append("")
        lines.append("### Pair / fold / cell concentration")
        lines.append("")
        lines.append("Per-pair total R:")
        for p, r in b["per_pair_total_r"].items():
            lines.append(f"- `{p}` = {r:+.4f}")
        lines.append("")
        lines.append("Per-fold total R:")
        for fi, r in b["per_fold_total_r"].items():
            lines.append(f"- fold {fi} = {r:+.4f}")
        lines.append("")
        lines.append(
            f"Top fold: fold **{b['top_fold_index']}** with R = "
            f"**{b['top_fold_r']:+.4f}** "
            f"(**{100*b['top_fold_share_of_total_r']:.1f}%** of total R)."
        )
        lines.append(
            f"Top pair: **{b['top_pair']}** with R = "
            f"**{b['top_pair_r']:+.4f}** "
            f"(**{100*b['top_pair_share_of_total_r']:.1f}%** of total R)."
        )
        lines.append(
            f"Top pair-fold cell: **{b['top_cell']}** with R = "
            f"**{b['top_cell_r']:+.4f}** "
            f"(**{100*b['top_cell_share_of_total_r']:.1f}%** of total R)."
        )
        lines.append("")
        lines.append("### Per-fold expectancy: mean vs median")
        lines.append("")
        lines.append(
            f"- mean per-fold expectancy R = "
            f"**{b['mean_per_fold_expectancy_r']:+.4f}**"
        )
        lines.append(
            f"- median per-fold expectancy R = "
            f"**{b['median_per_fold_expectancy_r']:+.4f}**"
        )
        lines.append(
            f"- mean − median gap = "
            f"**{b['mean_minus_median_per_fold_expectancy_r']:+.4f}**"
        )
        lines.append("")
        lines.append("### Trade-R distribution")
        lines.append("")
        d = b["trade_r_distribution"]
        lines.append(
            f"min={d['min']:+.4f} | p10={d['p10']:+.4f} | "
            f"p25={d['p25']:+.4f} | median={d['median']:+.4f} | "
            f"p75={d['p75']:+.4f} | p90={d['p90']:+.4f} | "
            f"max={d['max']:+.4f}"
        )
        lines.append("")
        lines.append("### Exit-reason mix")
        lines.append("")
        for k, v in sorted(b["exit_reason_counts"].items()):
            lines.append(f"- `{k}` = {v}")
        lines.append("")
        lines.append("### Leave-one-out by fold")
        lines.append("")
        lines.append(
            "| dropped fold | remaining trades | remaining total R | "
            "remaining expectancy R | remaining pairs+ |"
        )
        lines.append("|---|---|---|---|---|")
        for row in b["loo_by_fold"]:
            lines.append(
                f"| {row['dropped_fold']} | {row['remaining_trades']} | "
                f"{row['remaining_total_r']:+.4f} | "
                f"{row['remaining_expectancy_r']:+.4f} | "
                f"{row['remaining_pairs_positive']} |"
            )
        lines.append("")
        lines.append("### Leave-one-out by pair")
        lines.append("")
        lines.append(
            "| dropped pair | remaining trades | remaining total R | "
            "remaining expectancy R | fold-pass count after drop |"
        )
        lines.append("|---|---|---|---|---|")
        for row in b["loo_by_pair"]:
            lines.append(
                f"| {row['dropped_pair']} | {row['remaining_trades']} | "
                f"{row['remaining_total_r']:+.4f} | "
                f"{row['remaining_expectancy_r']:+.4f} | "
                f"{row['fold_pass_count_after_drop']} |"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold-detail", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    args = ap.parse_args(argv)

    if not args.fold_detail.exists():
        print(
            f"BLOCKED: fold-detail path does not exist: {args.fold_detail}",
            file=sys.stderr,
        )
        return 2

    fold_detail = json.loads(args.fold_detail.read_text(encoding="utf-8"))
    obj = concentration(fold_detail)
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
