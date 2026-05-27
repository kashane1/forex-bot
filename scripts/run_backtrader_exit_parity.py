#!/usr/bin/env python3
"""Run C008/C009/C018 Backtrader exit-parity diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from research.backtrader_exit_parity.compare import build_comparison
from research.backtrader_exit_parity.constants import PARITY_OUT_DIR, REPO_ROOT
from research.backtrader_exit_parity.runner import (
    run_all_campaigns,
    run_campaign_parity,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtrader exit-parity diagnostics")
    parser.add_argument(
        "--campaign",
        choices=["C008", "C009", "C018", "all"],
        default="all",
    )
    parser.add_argument("--out-dir", type=Path, default=PARITY_OUT_DIR)
    parser.add_argument("--compare-only", action="store_true")
    args = parser.parse_args()

    if not args.compare_only:
        if args.campaign == "all":
            results = run_all_campaigns(repo_root=REPO_ROOT, out_dir=args.out_dir)
        else:
            results = {
                args.campaign: run_campaign_parity(
                    args.campaign, repo_root=REPO_ROOT, out_dir=args.out_dir
                )
            }
        print(json.dumps({k: v.get("aggregate", {}) for k, v in results.items()}, indent=2))

    rows, classifications = build_comparison(repo_root=REPO_ROOT, out_dir=args.out_dir)
    print(json.dumps(classifications, indent=2))
    print(f"Wrote {args.out_dir / 'exit_reason_comparison.csv'} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
