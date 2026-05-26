#!/usr/bin/env python3
"""Backtrader secondary-lane runner.

Drives the Backtrader-lane runner over a registered campaign adapter
and writes the compact comparable artifacts to ``--output``:

- ``backtrader_summary.json``
- ``backtrader_trades.jsonl``
- ``backtrader_metrics.json``
- ``run_manifest.json``
- ``run_log_summary.md``

The lane is **local-only**. It reads:

- the same CAMPAIGN_002 Lean parity export bundle
  (``research/lean_parity/exports/campaign_002_h4/``) for H4 candles,
- the committed ``*.provenance.json`` sidecars for sha verification.

It does **not** call OANDA, LEAN, QuantConnect, or any cloud backtest.
It cannot approve a strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain blocked.

`strategy_evidence: false`.

Examples
--------

Preflight a campaign without running Cerebro:

    python scripts/run_backtrader_parity.py \\
        --campaign SMOKE_FIXTURE --output /tmp/bt_lane_smoke \\
        --data-export-dir tests/unit/backtrader_lane/fixtures \\
        --dry-run

Run a campaign:

    python scripts/run_backtrader_parity.py \\
        --campaign CAMPAIGN_002 \\
        --output research/backtrader_lane/results/campaign_002/

List registered campaigns:

    python scripts/run_backtrader_parity.py --list-campaigns
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Ensure registered campaigns are imported. Adapters self-register on import.
from research.backtrader_lane import strategies  # noqa: F401  - side-effect import
from research.backtrader_lane.runner import (
    RunOptions,
    list_campaigns,
    preflight,
    run,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Local Backtrader secondary-lane runner. Strictly local; no "
            "broker, no OANDA, no LEAN, no cloud."
        )
    )
    parser.add_argument(
        "--campaign",
        type=str,
        help="Campaign id (e.g. SMOKE_FIXTURE, CAMPAIGN_002).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for run artifacts.",
    )
    parser.add_argument(
        "--instruments",
        nargs="+",
        default=None,
        help="Override instrument subset. Defaults to the campaign's default set.",
    )
    parser.add_argument(
        "--data-export-dir",
        type=Path,
        default=None,
        help=(
            "Path to the H4 candle CSV directory. Defaults to "
            "research/lean_parity/exports/campaign_002_h4/."
        ),
    )
    parser.add_argument(
        "--starting-equity-usd",
        type=float,
        default=None,
        help="Override starting equity (defaults to the campaign's default).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only preflight data availability — do not run Cerebro.",
    )
    parser.add_argument(
        "--no-strict-data",
        action="store_true",
        help=(
            "Allow CSVs whose sha256 differs from the committed provenance "
            "JSON. OFF by default; only set this if you are intentionally "
            "regenerating data and accept that comparison is meaningless."
        ),
    )
    parser.add_argument(
        "--list-campaigns",
        action="store_true",
        help="Print the registered campaign ids and exit.",
    )
    parser.add_argument(
        "--run-mode",
        choices=("full", "fold_windows"),
        default="full",
        help=(
            "full = iterate entire CSV (default). fold_windows = run each "
            "walk-forward test window independently (requires --fold-plan)."
        ),
    )
    parser.add_argument(
        "--fold-plan",
        type=Path,
        default=None,
        help="Path to walk_forward/plan.json for fold_windows mode.",
    )
    parser.add_argument(
        "--warmup-days",
        type=int,
        default=90,
        help="Calendar-day warmup margin before each fold test_start (default 90).",
    )
    parser.add_argument(
        "--strict-test-window",
        action="store_true",
        help=(
            "When set with fold_windows, only count trades whose entry falls "
            "inside the fold test window. Default (off) mirrors bespoke engine "
            "behaviour including warmup-margin trades."
        ),
    )
    parser.add_argument(
        "--entry-bar-stop-policy",
        choices=("backtrader_default", "bespoke_current_no_entry_bar_stop"),
        default="backtrader_default",
        help=(
            "Entry-bar adverse-stop policy for CAMPAIGN_015. "
            "backtrader_default = current BT same-bar stop on entry; "
            "bespoke_current_no_entry_bar_stop = parity with current bespoke "
            "BacktestEngine (skip entry-bar adverse stop)."
        ),
    )
    parser.add_argument(
        "--risk-engine-parity",
        action="store_true",
        help=(
            "When set, CAMPAIGN_015 runs read-only RiskEngine rejection parity "
            "at fill time (spread/session/drawdown gates; no broker)."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.list_campaigns:
        for cid in list_campaigns():
            print(cid)
        return 0

    if not args.campaign:
        print("error: --campaign is required (or pass --list-campaigns)", file=sys.stderr)
        return 2
    if not args.output:
        print("error: --output is required", file=sys.stderr)
        return 2

    from research.backtrader_lane.data_adapter import DEFAULT_EXPORT_DIR

    data_dir = args.data_export_dir if args.data_export_dir else DEFAULT_EXPORT_DIR

    options = RunOptions(
        campaign_id=args.campaign,
        output_dir=args.output,
        instruments=args.instruments,
        data_export_dir=data_dir,
        starting_equity_usd=args.starting_equity_usd,
        dry_run=args.dry_run,
        strict_data=not args.no_strict_data,
        run_mode=args.run_mode,
        fold_plan_path=args.fold_plan,
        warmup_days=args.warmup_days,
        strict_test_window=args.strict_test_window,
        entry_bar_stop_policy=args.entry_bar_stop_policy,
        risk_engine_parity=args.risk_engine_parity,
    )

    if args.run_mode == "fold_windows" and args.fold_plan is None:
        print("error: --fold-plan is required when --run-mode fold_windows", file=sys.stderr)
        return 2

    if args.dry_run:
        pf = preflight(options)
        print(json.dumps(pf, indent=2, sort_keys=True))
        # Still call run() to write the preflight manifest+summary so a CI
        # operator can inspect the artifacts a real run would emit.
        run(options)
        return 0

    try:
        summary = run(options)
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Campaign: {summary['campaign_id']}")
    print(f"Total trades: {summary['total_trades']}")
    print(f"Total PnL (account): {summary['total_pnl_account']:.4f}")
    if summary["blocked_instruments"]:
        print(f"BLOCKED instruments: {summary['blocked_instruments']}", file=sys.stderr)
    print(f"Artifacts: {options.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
