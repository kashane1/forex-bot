#!/usr/bin/env python3
"""Compare Backtrader fold-window output vs bespoke CAMPAIGN_015 rehydrate.

Reads:
- Backtrader fold-window run under ``--backtrader-dir``
- Bespoke rehydrate fold trades under ``--bespoke-dir``

Writes comparison JSON + Markdown to ``--output``.

Emits one divergence label. Cannot approve a strategy.

`strategy_evidence: false`.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class FoldComparisonLabel(str, Enum):
    PASS = "PASS"
    TOLERABLE_DRIFT = "TOLERABLE_DRIFT"
    DATA_MISMATCH = "DATA_MISMATCH"
    TIMESTAMP_MISMATCH = "TIMESTAMP_MISMATCH"
    SIGNAL_RULE_MISMATCH = "SIGNAL_RULE_MISMATCH"
    FILL_TIMING_MISMATCH = "FILL_TIMING_MISMATCH"
    STOP_OR_TIME_EXIT_MISMATCH = "STOP_OR_TIME_EXIT_MISMATCH"
    SIZING_OR_PNL_MISMATCH = "SIZING_OR_PNL_MISMATCH"
    BLOCKED = "BLOCKED"


TRADE_COUNT_TOLERANCE_PCT = 10.0


@dataclass
class FoldCellComparison:
    fold_index: int
    instrument: str
    bt_trades: int
    bespoke_trades: int
    delta: int
    delta_pct: float | None


@dataclass
class FoldComparisonReport:
    bt_total_trades: int
    bespoke_total_trades: int
    prior_bt_full_window_trades: int | None
    prior_classification: str | None
    classification: FoldComparisonLabel
    cells: list[FoldCellComparison]
    bt_by_fold: dict[int, int]
    bespoke_by_fold: dict[int, int]
    bt_by_pair: dict[str, int]
    bespoke_by_pair: dict[str, int]
    bt_side: dict[str, int]
    bespoke_side: dict[str, int]
    notes: list[str] = field(default_factory=list)
    generated_at: str = ""


def _load_bt_trades(bt_dir: Path) -> list[dict[str, Any]]:
    path = bt_dir / "backtrader_trades.jsonl"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _load_bespoke_trades(bespoke_dir: Path, *, cost: str = "base") -> list[dict[str, Any]]:
    base = bespoke_dir / "folds" / cost
    if not base.exists():
        return []
    rows: list[dict[str, Any]] = []
    for fold_dir in sorted(base.glob("fold_*")):
        fold_index = int(fold_dir.name.split("_")[1])
        for csv_path in sorted(fold_dir.glob("*_trades.csv")):
            parts = csv_path.stem.split("_")
            instrument = f"{parts[2]}_{parts[3]}"
            with csv_path.open(encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    row["fold_index"] = fold_index
                    row["instrument"] = row.get("instrument") or instrument
                    rows.append(row)
    return rows


def _side_counts(trades: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for t in trades:
        out[t.get("side", "?")] += 1
    return dict(out)


def _count_by(trades: list[dict[str, Any]], key: str) -> dict[Any, int]:
    out: dict[Any, int] = defaultdict(int)
    for t in trades:
        out[t[key]] += 1
    return dict(out)


def _pct_delta(bt: int, ref: int) -> float | None:
    if ref == 0:
        return None if bt == 0 else float("inf")
    return (bt - ref) / abs(ref) * 100.0


def classify(
    *,
    bt_total: int,
    bespoke_total: int,
    cells: list[FoldCellComparison],
    prior_bt_full: int | None,
    prior_class: str | None,
) -> tuple[FoldComparisonLabel, list[str]]:
    notes: list[str] = []
    if bt_total == 0 and bespoke_total == 0:
        return FoldComparisonLabel.BLOCKED, ["both sides empty"]
    if bespoke_total == 0:
        return FoldComparisonLabel.BLOCKED, ["bespoke side empty"]
    if bt_total == 0:
        return FoldComparisonLabel.BLOCKED, ["backtrader fold-window side empty"]

    delta_pct = _pct_delta(bt_total, bespoke_total)
    if delta_pct is not None and abs(delta_pct) <= TRADE_COUNT_TOLERANCE_PCT:
        notes.append(
            f"total trade-count delta {delta_pct:+.2f}% within ±{TRADE_COUNT_TOLERANCE_PCT}% band"
        )
        return FoldComparisonLabel.PASS, notes

    if prior_bt_full is not None and prior_class == "TIMESTAMP_MISMATCH":
        shrink = prior_bt_full - bt_total
        notes.append(
            f"full-window BT had {prior_bt_full} trades vs fold-window {bt_total}; "
            f"gap vs bespoke {bespoke_total} shrank by {shrink} from full-window excess"
        )
        if delta_pct is not None and abs(delta_pct) > TRADE_COUNT_TOLERANCE_PCT:
            if prior_bt_full - bespoke_total > bt_total - bespoke_total:
                notes.append(
                    "TIMESTAMP_MISMATCH resolved (window coverage aligned); "
                    "residual trade-count drift likely SIGNAL_RULE_MISMATCH or "
                    "FILL_TIMING_MISMATCH"
                )
                return FoldComparisonLabel.SIGNAL_RULE_MISMATCH, notes
            notes.append("residual drift after window alignment")
            return FoldComparisonLabel.SIGNAL_RULE_MISMATCH, notes

    if delta_pct is not None and abs(delta_pct) > 50:
        return FoldComparisonLabel.SIGNAL_RULE_MISMATCH, notes
    return FoldComparisonLabel.TOLERABLE_DRIFT, notes


def compare_fold_windows(
    *,
    backtrader_dir: Path,
    bespoke_dir: Path,
    prior_bt_full_window_trades: int | None = None,
    prior_classification: str | None = None,
) -> FoldComparisonReport:
    bt_trades = _load_bt_trades(backtrader_dir)
    bespoke_trades = _load_bespoke_trades(bespoke_dir)
    bt_by_fold = _count_by(bt_trades, "fold_index")
    bespoke_by_fold = _count_by(bespoke_trades, "fold_index")
    bt_by_pair = _count_by(bt_trades, "instrument")
    bespoke_by_pair = _count_by(bespoke_trades, "instrument")

    cells: list[FoldCellComparison] = []
    all_folds = sorted(set(bt_by_fold) | set(bespoke_by_fold))
    all_pairs = sorted(set(bt_by_pair) | set(bespoke_by_pair))
    for fi in all_folds:
        for pair in all_pairs:
            bt_n = sum(
                1
                for t in bt_trades
                if t.get("fold_index") == fi and t.get("instrument") == pair
            )
            b_n = sum(
                1
                for t in bespoke_trades
                if t.get("fold_index") == fi and t.get("instrument") == pair
            )
            cells.append(
                FoldCellComparison(
                    fold_index=int(fi),
                    instrument=pair,
                    bt_trades=bt_n,
                    bespoke_trades=b_n,
                    delta=bt_n - b_n,
                    delta_pct=_pct_delta(bt_n, b_n),
                )
            )

    bt_total = len(bt_trades)
    bespoke_total = len(bespoke_trades)
    label, notes = classify(
        bt_total=bt_total,
        bespoke_total=bespoke_total,
        cells=cells,
        prior_bt_full=prior_bt_full_window_trades,
        prior_class=prior_classification,
    )
    return FoldComparisonReport(
        bt_total_trades=bt_total,
        bespoke_total_trades=bespoke_total,
        prior_bt_full_window_trades=prior_bt_full_window_trades,
        prior_classification=prior_classification,
        classification=label,
        cells=cells,
        bt_by_fold={int(k): v for k, v in bt_by_fold.items()},
        bespoke_by_fold={int(k): v for k, v in bespoke_by_fold.items()},
        bt_by_pair=bt_by_pair,
        bespoke_by_pair=bespoke_by_pair,
        bt_side=_side_counts(bt_trades),
        bespoke_side=_side_counts(bespoke_trades),
        notes=notes,
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
    )


def render_markdown(report: FoldComparisonReport) -> str:
    lines = [
        "# Backtrader Fold-Window vs Bespoke Rehydrate — CAMPAIGN_015",
        "",
        "> `strategy_evidence: false`. Does **not** approve any strategy.",
        "",
        f"- Generated at: `{report.generated_at}`",
        f"- Backtrader fold-window trades: **{report.bt_total_trades}**",
        f"- Bespoke rehydrate trades: **{report.bespoke_total_trades}**",
        f"- Delta: **{report.bt_total_trades - report.bespoke_total_trades:+d}**",
    ]
    if report.prior_bt_full_window_trades is not None:
        lines.append(
            f"- Prior full-window BT trades: **{report.prior_bt_full_window_trades}** "
            f"(classification `{report.prior_classification}`)"
        )
    lines.extend(
        [
            f"- **Classification: `{report.classification.value}`**",
            "",
            "## Per-fold totals",
            "",
            "| fold | BT | bespoke | Δ |",
            "|---:|---:|---:|---:|",
        ]
    )
    folds = sorted(set(report.bt_by_fold) | set(report.bespoke_by_fold))
    for fi in folds:
        bt = report.bt_by_fold.get(fi, 0)
        b = report.bespoke_by_fold.get(fi, 0)
        lines.append(f"| {fi} | {bt} | {b} | {bt - b:+d} |")
    lines.extend(["", "## Per-pair totals", "", "| pair | BT | bespoke | Δ |", "|---|---:|---:|---:|"])
    pairs = sorted(set(report.bt_by_pair) | set(report.bespoke_by_pair))
    for p in pairs:
        bt = report.bt_by_pair.get(p, 0)
        b = report.bespoke_by_pair.get(p, 0)
        lines.append(f"| {p} | {bt} | {b} | {bt - b:+d} |")
    lines.extend(["", "## Side distribution", ""])
    lines.append(f"- BT: `{report.bt_side}`")
    lines.append(f"- bespoke: `{report.bespoke_side}`")
    if report.notes:
        lines.extend(["", "## Notes", ""])
        for n in report.notes:
            lines.append(f"- {n}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backtrader-dir", type=Path, required=True)
    ap.add_argument("--bespoke-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--prior-bt-full-trades", type=int, default=None)
    ap.add_argument("--prior-classification", type=str, default="TIMESTAMP_MISMATCH")
    args = ap.parse_args(argv)

    if not args.backtrader_dir.exists():
        print(f"BLOCKED: backtrader dir missing: {args.backtrader_dir}", file=sys.stderr)
        return 2
    if not args.bespoke_dir.exists():
        print(f"BLOCKED: bespoke dir missing: {args.bespoke_dir}", file=sys.stderr)
        return 2

    report = compare_fold_windows(
        backtrader_dir=args.backtrader_dir,
        bespoke_dir=args.bespoke_dir,
        prior_bt_full_window_trades=args.prior_bt_full_trades,
        prior_classification=args.prior_classification,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    payload = {
        "bt_total_trades": report.bt_total_trades,
        "bespoke_total_trades": report.bespoke_total_trades,
        "prior_bt_full_window_trades": report.prior_bt_full_window_trades,
        "prior_classification": report.prior_classification,
        "classification": report.classification.value,
        "bt_by_fold": report.bt_by_fold,
        "bespoke_by_fold": report.bespoke_by_fold,
        "bt_by_pair": report.bt_by_pair,
        "bespoke_by_pair": report.bespoke_by_pair,
        "bt_side": report.bt_side,
        "bespoke_side": report.bespoke_side,
        "notes": report.notes,
        "generated_at": report.generated_at,
        "cells": [
            {
                "fold_index": c.fold_index,
                "instrument": c.instrument,
                "bt_trades": c.bt_trades,
                "bespoke_trades": c.bespoke_trades,
                "delta": c.delta,
                "delta_pct": c.delta_pct,
            }
            for c in report.cells
        ],
        "strategy_evidence": False,
    }
    (args.output / "fold_window_comparison.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "fold_window_comparison.md").write_text(
        render_markdown(report), encoding="utf-8"
    )
    print(f"BT trades: {report.bt_total_trades}")
    print(f"Bespoke trades: {report.bespoke_total_trades}")
    print(f"Classification: {report.classification.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
