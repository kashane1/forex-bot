#!/usr/bin/env python3
"""Apply modeled financing overlay to existing trade CSV artifacts.

Diagnostic only — ``strategy_evidence: false``. Does not rerun
campaigns, modify engine PnL, or change strategy verdicts.

Usage:
  python scripts/apply_modeled_financing_overlay.py \\
    --trades backtests/.../trades.csv \\
    --output research/financing/overlay_result.json

  python scripts/apply_modeled_financing_overlay.py \\
    --trades-glob 'backtests/CAMPAIGN_008_*/baseline/train/*_train_trades.csv' \\
    --output research/financing/c008_train_overlay.json \\
    --rate-source stress
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.financing.fixtures import load_rate_fixture
from research.financing.manual_csv import load_manual_csv_rate_schedule
from research.financing.overlay import (
    apply_financing_overlay,
    load_trades_from_csv,
    load_trades_from_glob,
    write_overlay_result,
)
from research.financing.rates import FinancingRateSource, default_stress_rate_source


def _resolve_rate_source(args: argparse.Namespace) -> FinancingRateSource:
    if args.rate_source == "stress":
        return default_stress_rate_source()
    if args.rate_source == "fixture":
        if not args.rate_fixture:
            raise SystemExit("--rate-fixture required when --rate-source=fixture")
        source, _ = load_rate_fixture(args.rate_fixture)
        return source
    if args.rate_source == "manual_csv":
        if not args.rate_csv:
            raise SystemExit("--rate-csv required when --rate-source=manual_csv")
        return load_manual_csv_rate_schedule(args.rate_csv)
    raise SystemExit(f"unknown rate source: {args.rate_source}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trades", type=Path, help="Single trades CSV path")
    parser.add_argument("--trades-glob", help="Glob for multiple trade CSVs")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path")
    parser.add_argument(
        "--rate-source",
        choices=("stress", "fixture", "manual_csv"),
        default="stress",
        help="Financing rate source (default: conservative stress)",
    )
    parser.add_argument("--rate-fixture", type=Path, help="JSON rate fixture path")
    parser.add_argument("--rate-csv", type=Path, help="Manual CSV rate schedule")
    parser.add_argument(
        "--diagnostic-label",
        default="SYNTHETIC_FINANCING_DIAGNOSTIC",
        help="Label stamped on output",
    )
    args = parser.parse_args()

    if not args.trades and not args.trades_glob:
        raise SystemExit("Provide --trades or --trades-glob")
    if args.trades and args.trades_glob:
        raise SystemExit("Provide only one of --trades or --trades-glob")

    if args.trades:
        trades = load_trades_from_csv(args.trades)
    else:
        trades = load_trades_from_glob(args.trades_glob)

    if not trades:
        raise SystemExit("No trades loaded")

    source = _resolve_rate_source(args)
    result = apply_financing_overlay(
        trades,
        rate_source=source,
        diagnostic_label=args.diagnostic_label,
    )
    write_overlay_result(result, args.output)
    agg = result["aggregate"]
    print(
        f"Applied {source.name} to {result['trade_count']} trades → {args.output}\n"
        f"  gross exp R: {agg['gross_expectancy_r']:.4f}\n"
        f"  net exp R:   {agg['net_expectancy_r']:.4f}\n"
        f"  fin drag R:  {agg['financing_drag_r']:.4f}\n"
        f"  label:       {result['diagnostic_label']}"
    )


if __name__ == "__main__":
    main()
