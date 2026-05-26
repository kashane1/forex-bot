#!/usr/bin/env python3
"""Build a per-pair bespoke reference JSON for the CAMPAIGN_015
Backtrader-vs-bespoke comparison harness.

Aggregates the per-fold, per-pair detail from the CAMPAIGN_015 rehydrate
walk-forward into a single per-pair record that the existing
``scripts/compare_backtrader_parity.py`` knows how to ingest.

This is read-only against the rehydrate artifact; it just consolidates
numbers that already exist. No strategy is approved.

Usage:
    python scripts/build_campaign_015_bespoke_reference.py \
        --fold-detail research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json \
        --out         research/campaign_015/diagnostics/campaign_015_bespoke_reference.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def build(*, fold_detail: dict[str, Any], cost: str = "base") -> dict[str, Any]:
    agg = fold_detail["by_cost"][cost]
    pair_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "trades": 0,
            "return_pct": 0.0,
            "wins": 0,
            "losses": 0,
            "all_r": [],
        }
    )
    data_request_hashes: dict[str, str] = {}
    for f in agg["folds"]:
        for pr in f["pair_runs"]:
            inst = pr["instrument"]
            ps = pair_stats[inst]
            rs = pr.get("trade_r_series", [])
            ps["trades"] += pr["trade_count"]
            ps["return_pct"] += pr["return_pct"]
            ps["all_r"].extend(rs)
            ps["wins"] += sum(1 for r in rs if r > 0)
            ps["losses"] += sum(1 for r in rs if r < 0)
            # Keep the FIRST data_request_hash seen per pair (any is fine —
            # they differ across folds because the windows differ).
            if inst not in data_request_hashes and pr.get("data_request_hash"):
                data_request_hashes[inst] = pr["data_request_hash"]

    pairs = []
    for inst in sorted(pair_stats.keys()):
        ps = pair_stats[inst]
        n = ps["trades"]
        exp_r = (sum(ps["all_r"]) / n) if n else 0.0
        win_rate = (ps["wins"] / n) if n else 0.0
        gross_pos = sum(r for r in ps["all_r"] if r > 0)
        gross_neg = -sum(r for r in ps["all_r"] if r < 0)
        pf = (gross_pos / gross_neg) if gross_neg > 0 else float("inf")
        pairs.append(
            {
                "instrument": inst,
                "candle_count": None,  # bespoke iterates per-fold, not whole-window
                "trades": n,
                "expectancy_r": round(exp_r, 4),
                "return_pct": round(ps["return_pct"], 4),
                "win_rate": round(win_rate, 4),
                "profit_factor": (
                    round(pf, 4) if pf != float("inf") else None
                ),
                "max_drawdown_pct": None,  # not aggregated here
            }
        )

    total_trades = sum(p["trades"] for p in pairs)
    return {
        "campaign_id": fold_detail.get("campaign_id"),
        "strategy_name": fold_detail.get("strategy_name"),
        "strategy_version": fold_detail.get("strategy_version"),
        "config_hash": fold_detail.get("config_hash"),
        "cost_label": cost,
        "fill_timing": fold_detail.get("fill_timing"),
        "data_request_hashes": data_request_hashes,
        "total_trades": total_trades,
        "approval_path": "none (post-run diagnostic only)",
        "approved_strategies_yaml_state": "approved: []",
        "diagnostic_disclaimer": (
            "Aggregated from the rehydrate walk-forward across 8 fold "
            "test windows; does NOT cover the full 2020-2026 universe "
            "the BT lane iterates. A trade-count delta between BT and "
            "this reference is expected on window-coverage grounds "
            "alone and is documented by the comparison harness as the "
            "appropriate divergence class."
        ),
        "pairs": pairs,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold-detail", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--cost", default="base")
    args = ap.parse_args(argv)

    if not args.fold_detail.exists():
        print(
            f"BLOCKED: fold-detail does not exist: {args.fold_detail}",
            file=sys.stderr,
        )
        return 2
    fd = json.loads(args.fold_detail.read_text(encoding="utf-8"))
    obj = build(fold_detail=fd, cost=args.cost)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
