#!/usr/bin/env python3
"""Run entry orchestration parity diagnostics (Phases 1–3)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from research.entry_parity.adjustment_experiment import run_adjustment_experiment
from research.entry_parity.compare_entries import compare_all_campaigns
from research.entry_parity.constants import ENTRY_PARITY_OUT_DIR, REPO_ROOT
from research.entry_parity.risk_attribution import build_risk_filter_attribution


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Entry orchestration parity diagnostics")
    parser.add_argument("--skip-adjustment", action="store_true")
    args = parser.parse_args()

    ENTRY_PARITY_OUT_DIR.mkdir(parents=True, exist_ok=True)

    comparison = compare_all_campaigns(repo_root=REPO_ROOT)
    comp_path = ENTRY_PARITY_OUT_DIR / "entry_timestamp_comparison.json"
    comp_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")

    split_rows: list[dict] = []
    detail_rows: list[dict] = []
    for campaign, data in comparison["campaigns"].items():
        for split, counts in data.get("by_split", {}).items():
            split_rows.append(
                {
                    "campaign": campaign,
                    "split": split,
                    "bespoke_entries": counts.get("common", 0) + counts.get("bespoke_only", 0),
                    "backtrader_entries": counts.get("common", 0) + counts.get("backtrader_only", 0),
                    "common": counts.get("common", 0),
                    "bespoke_only": counts.get("bespoke_only", 0),
                    "backtrader_only": counts.get("backtrader_only", 0),
                }
            )
        for detail in data.get("bespoke_only_details", []):
            detail_rows.append(
                {
                    "campaign": campaign,
                    "split": detail.get("split", ""),
                    "instrument": detail.get("instrument", ""),
                    "entry_time": detail.get("entry_time", ""),
                    "side": detail.get("side", ""),
                    "attribution": detail.get("attribution", ""),
                    "weekday": detail.get("weekday", ""),
                    "session": detail.get("session", ""),
                }
            )
    _write_csv(split_rows, ENTRY_PARITY_OUT_DIR / "entry_timestamp_comparison.csv")
    if detail_rows:
        _write_csv(detail_rows, ENTRY_PARITY_OUT_DIR / "entry_timestamp_bespoke_only.csv")

    attribution = build_risk_filter_attribution(repo_root=REPO_ROOT)
    attr_path = ENTRY_PARITY_OUT_DIR / "risk_filter_attribution.json"
    attr_path.write_text(json.dumps(attribution, indent=2), encoding="utf-8")

    experiment: dict = {"legacy_bt": {}, "engine_aligned": {}}
    if not args.skip_adjustment:
        # Legacy counts from prior exit-parity sprint artifacts
        for campaign in ("C008", "C009", "C018"):
            summary_path = REPO_ROOT / "research/backtrader_exit_parity" / f"{campaign.lower()}_parity_summary.json"
            if summary_path.exists():
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                experiment["legacy_bt"][campaign] = {
                    "backtrader_trade_count": summary.get("aggregate", {}).get("total_trades", 0),
                }
        aligned = run_adjustment_experiment(mode="engine_aligned")
        experiment["engine_aligned"] = aligned.get("campaigns", {})
        exp_path = ENTRY_PARITY_OUT_DIR / "backtrader_adjustment_experiment.json"
        exp_path.write_text(json.dumps(experiment, indent=2, default=str), encoding="utf-8")

    print(json.dumps({"comparison": comp_path.name, "attribution": attr_path.name}, indent=2))


if __name__ == "__main__":
    main()
