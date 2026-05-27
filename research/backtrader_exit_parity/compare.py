"""Compare Backtrader exit-parity output to bespoke deduped forensic trades."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from research.backtrader_exit_parity.constants import (
    BESPOKE_TRADE_GLOBS,
    PARITY_OUT_DIR,
    REPO_ROOT,
)
from research.backtrader_exit_parity.exit_logic import exit_reason_stats


def load_bespoke_trades(repo_root: Path, campaign: str, split: str) -> list[dict[str, Any]]:
    pattern = BESPOKE_TRADE_GLOBS[campaign].format(split=split)
    paths = sorted(repo_root.glob(pattern))
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                row["split"] = split
                rows.append(row)
    return rows


def _normalize_trades(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        out.append(
            {
                "exit_reason": r.get("exit_reason", ""),
                "bars_held": int(float(r.get("bars_held") or 0)),
                "r_multiple": float(r.get("r_multiple") or 0.0),
                "protective_stop_armed": str(r.get("protective_stop_armed", "")).lower()
                in {"true", "1", "yes"},
                "protective_stop_exit": str(r.get("protective_stop_exit", "")).lower()
                in {"true", "1", "yes"},
            }
        )
    return out


def classify_parity(
    bespoke_stats: dict[str, Any],
    backtrader_stats: dict[str, Any],
    *,
    share_tolerance_pct: float = 5.0,
    count_tolerance: int = 2,
) -> str:
    b_total = bespoke_stats.get("total_trades", 0)
    bt_total = backtrader_stats.get("total_trades", 0)
    if b_total == 0 and bt_total == 0:
        return "BLOCKED"
    if abs(b_total - bt_total) > count_tolerance:
        return "MATERIAL_DIVERGENCE"
    b_reasons = bespoke_stats.get("by_exit_reason", {})
    bt_reasons = backtrader_stats.get("by_exit_reason", {})
    all_reasons = set(b_reasons) | set(bt_reasons)
    max_delta = 0.0
    for reason in all_reasons:
        b_share = b_reasons.get(reason, {}).get("share_pct", 0.0)
        bt_share = bt_reasons.get(reason, {}).get("share_pct", 0.0)
        max_delta = max(max_delta, abs(b_share - bt_share))
    if max_delta <= 1.0 and b_total == bt_total:
        return "PASS"
    if max_delta <= share_tolerance_pct:
        return "CLOSE_MATCH"
    return "MATERIAL_DIVERGENCE"


def build_comparison(
    *,
    repo_root: Path = REPO_ROOT,
    out_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out_dir = out_dir or PARITY_OUT_DIR
    rows: list[dict[str, Any]] = []
    classifications: dict[str, Any] = {}

    for campaign in ("C008", "C009", "C018", "C019"):
        bt_summary_path = out_dir / f"{campaign.lower()}_parity_summary.json"
        if not bt_summary_path.exists():
            classifications[campaign] = "BLOCKED"
            continue
        bt_summary = json.loads(bt_summary_path.read_text(encoding="utf-8"))
        campaign_rows: list[dict[str, Any]] = []
        count_tol = 1 if campaign == "C019" else 2

        for split in ("train", "validation"):
            bespoke_raw = load_bespoke_trades(repo_root, campaign, split)
            bespoke_norm = _normalize_trades(bespoke_raw)
            bespoke_stats = exit_reason_stats(bespoke_norm)
            bt_split_stats = bt_summary.get("by_split", {}).get(split, {})
            verdict = classify_parity(
                bespoke_stats, bt_split_stats, count_tolerance=count_tol
            )
            campaign_rows.append(
                {
                    "campaign": campaign,
                    "split": split,
                    "bespoke_trade_count": bespoke_stats.get("total_trades", 0),
                    "backtrader_trade_count": bt_split_stats.get("total_trades", 0),
                    "verdict": verdict,
                    "bespoke_exit_reasons": json.dumps(
                        {k: v["count"] for k, v in bespoke_stats.get("by_exit_reason", {}).items()}
                    ),
                    "backtrader_exit_reasons": json.dumps(
                        {k: v["count"] for k, v in bt_split_stats.get("by_exit_reason", {}).items()}
                    ),
                }
            )
            for reason, bdata in bespoke_stats.get("by_exit_reason", {}).items():
                btdata = bt_split_stats.get("by_exit_reason", {}).get(reason, {})
                rows.append(
                    {
                        "campaign": campaign,
                        "split": split,
                        "exit_reason": reason,
                        "bespoke_count": bdata.get("count", 0),
                        "bespoke_share_pct": bdata.get("share_pct", 0.0),
                        "bespoke_expectancy_r": bdata.get("expectancy_r", 0.0),
                        "backtrader_count": btdata.get("count", 0),
                        "backtrader_share_pct": btdata.get("share_pct", 0.0),
                        "backtrader_expectancy_r": btdata.get("expectancy_r", 0.0),
                        "share_delta_pct": round(
                            abs(bdata.get("share_pct", 0.0) - btdata.get("share_pct", 0.0)), 2
                        ),
                        "verdict": verdict,
                    }
                )

        agg_verdicts = {r["split"]: r["verdict"] for r in campaign_rows}
        if all(v == "PASS" for v in agg_verdicts.values()):
            classifications[campaign] = "PASS"
        elif all(v in {"PASS", "CLOSE_MATCH"} for v in agg_verdicts.values()):
            classifications[campaign] = "CLOSE_MATCH"
        elif any(v == "BLOCKED" for v in agg_verdicts.values()):
            classifications[campaign] = "BLOCKED"
        else:
            classifications[campaign] = "MATERIAL_DIVERGENCE"

    csv_path = out_dir / "exit_reason_comparison.csv"
    if rows:
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    return rows, classifications
