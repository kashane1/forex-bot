#!/usr/bin/env python3
"""Compare a Backtrader-lane run summary against the bespoke reference.

Reads:
- `--backtrader-results <dir>/backtrader_summary.json` (Phase 3 runner output)
- `--bespoke-reference <path>` (e.g. research/lean_parity/campaign_002_h4_bespoke_reference.json)

Writes:
- `<out>/comparison_summary.json` — machine-readable
- `<out>/comparison_summary.md`   — human-readable

Emits one of the divergence labels from
`INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md` §7. Cannot approve a
strategy. Cannot mutate any verdict.

`strategy_evidence: false`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.backtrader_lane.compare import (
    Tolerances,
    compare,
    render_markdown,
    to_json_dict,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare a Backtrader-lane run summary against the bespoke "
            "reference for the same campaign. Local-only; never approves "
            "a strategy."
        )
    )
    parser.add_argument(
        "--campaign",
        type=str,
        required=True,
        help="Campaign id (informational; verified against backtrader_summary.json).",
    )
    parser.add_argument(
        "--backtrader-results",
        type=Path,
        required=True,
        help=(
            "Either a directory containing backtrader_summary.json or "
            "the path to backtrader_summary.json directly."
        ),
    )
    parser.add_argument(
        "--bespoke-reference",
        type=Path,
        required=True,
        help="Path to the bespoke reference JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory for the comparison summary outputs.",
    )
    parser.add_argument(
        "--trade-count-tolerance-pct",
        type=float,
        default=5.0,
        help="Tight tolerance for trade-count percentage delta (default 5%%).",
    )
    parser.add_argument(
        "--expectancy-r-tolerance",
        type=float,
        default=0.03,
        help="Tight tolerance for expectancy R delta (default 0.03).",
    )
    parser.add_argument(
        "--return-pct-tolerance",
        type=float,
        default=0.5,
        help="Tight tolerance for return %% delta in percentage points (default 0.5).",
    )
    parser.add_argument(
        "--win-rate-tolerance",
        type=float,
        default=0.05,
        help="Tight tolerance for win rate delta (default 0.05).",
    )
    return parser.parse_args(argv)


def _resolve_summary_path(p: Path) -> Path:
    if p.is_dir():
        return p / "backtrader_summary.json"
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    summary_path = _resolve_summary_path(args.backtrader_results)
    tolerances = Tolerances(
        trade_count_pct=args.trade_count_tolerance_pct,
        expectancy_r=args.expectancy_r_tolerance,
        return_pct=args.return_pct_tolerance,
        win_rate=args.win_rate_tolerance,
    )
    try:
        report = compare(
            backtrader_summary_path=summary_path,
            bespoke_reference_path=args.bespoke_reference,
            tolerances=tolerances,
        )
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if report.campaign_id != args.campaign:
        print(
            f"warning: --campaign {args.campaign!r} does not match "
            f"backtrader_summary.json campaign_id {report.campaign_id!r}",
            file=sys.stderr,
        )

    (args.output / "comparison_summary.json").write_text(
        json.dumps(to_json_dict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output / "comparison_summary.md").write_text(
        render_markdown(report), encoding="utf-8"
    )

    print(f"Campaign: {report.campaign_id}")
    print(f"Backtrader total trades: {report.bt_total_trades}")
    print(f"Bespoke total trades:    {report.bespoke_total_trades}")
    print(f"Overall classification:  {report.overall_classification.value}")
    print(f"Artifacts: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
