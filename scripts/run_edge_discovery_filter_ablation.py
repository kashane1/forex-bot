"""Edge-discovery CLI — filter ablation.

Local-only diagnostic. Reads a staged-signal CSV (one row per triggered signal,
boolean filter columns, a per-signal value column) and reports whether each
filter adds edge or merely shrinks the sample.

Approves nothing, opens no test lockbox, never calls the broker. Writes a
compact JSON artifact under ``research/edge_discovery/cli_runs/``.

    python scripts/run_edge_discovery_filter_ablation.py \
        --signals-csv path/to/signals.csv \
        --filter-cols adx_ok,trend_ok,vol_ok --value-col log_return

Use ``--dry-run`` to validate inputs and print the plan without running.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.edge_discovery.filter_ablation import filter_ablation

DEFAULT_OUTPUT_DIR = ROOT / "research" / "edge_discovery" / "cli_runs"

SAFETY_META = {
    "diagnostic_only": True,
    "strategy_evidence": False,
    "not_approved": True,
    "approves_strategy": False,
    "test_lockbox_opened": False,
    "NOT_edge_claim": True,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--signals-csv", type=Path, required=True)
    p.add_argument("--filter-cols", required=True, help="comma-separated boolean filter columns")
    p.add_argument("--value-col", default="log_return")
    p.add_argument("--post-cost-col", default="log_return_post_cost")
    p.add_argument("--pair-col", default="instrument")
    p.add_argument("--side-col", default="side")
    p.add_argument("--min-sample", type=int, default=20)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--dry-run", action="store_true")
    return p


def run(args: argparse.Namespace) -> int:
    if not args.signals_csv.is_file():
        print(f"[BLOCKED] signals CSV not found: {args.signals_csv}", file=sys.stderr)
        return 2
    filter_cols = [c.strip() for c in args.filter_cols.split(",") if c.strip()]
    if not filter_cols:
        print("[BLOCKED] --filter-cols is empty", file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"[dry-run] would ablate {filter_cols} on {args.signals_csv} (value={args.value_col})")
        return 0

    df = pd.read_csv(args.signals_csv)
    missing = [c for c in [*filter_cols, args.value_col] if c not in df.columns]
    if missing:
        print(f"[BLOCKED] columns missing from {args.signals_csv}: {missing}", file=sys.stderr)
        return 2

    post_cost_col = args.post_cost_col if args.post_cost_col in df.columns else None
    result = filter_ablation(
        df,
        filter_cols=filter_cols,
        value_col=args.value_col,
        post_cost_col=post_cost_col,
        pair_col=args.pair_col if args.pair_col in df.columns else None,
        side_col=args.side_col if args.side_col in df.columns else None,
        min_sample=args.min_sample,
    )

    out_path = args.out or (DEFAULT_OUTPUT_DIR / f"{args.signals_csv.stem}_filter_ablation.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_meta": {
            **SAFETY_META,
            "kind": "edge_discovery.filter_ablation",
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "filter_cols": filter_cols,
        },
        "result": result.to_dict(),
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    for c in result.contributions:
        print(f"  {c.filter}: marginal={c.marginal_expectancy_gain:+.6f} flags={c.flags}")
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
