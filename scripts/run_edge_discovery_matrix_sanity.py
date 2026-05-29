"""Edge-discovery CLI — matrix selection-noise / fragility sanity check.

Local-only diagnostic. Reads a matrix-result CSV (one row per candidate, e.g.
``research/campaign_025/train_matrix/train_matrix_metrics.csv``) and reports
whether the best candidate is meaningfully better than best-of-N selection
noise, plus optional per-pair holdout fragility.

This script approves nothing, opens no test lockbox, changes no campaign
verdict, and never calls the broker. Writes a compact JSON artifact under
``research/edge_discovery/cli_runs/``.

    python scripts/run_edge_discovery_matrix_sanity.py \
        --matrix-csv research/campaign_025/train_matrix/train_matrix_metrics.csv \
        --metric-col expectancy_r --label-col candidate_id \
        --null-reference -0.0029154071495408797 --null-std 0.03

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

from research.edge_discovery.multiple_comparison import matrix_sanity

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
    p.add_argument("--matrix-csv", type=Path, required=True, help="matrix-result CSV (one row per candidate)")
    p.add_argument("--metric-col", default="expectancy_r")
    p.add_argument("--label-col", default="candidate_id")
    p.add_argument("--lower-is-better", action="store_true", help="metric where smaller is better (e.g. a cost)")
    p.add_argument("--null-reference", type=float, default=None, help="null floor to compare best against (e.g. C011)")
    p.add_argument("--null-std", type=float, default=None, help="noise scale; defaults to cross-variant dispersion")
    p.add_argument("--too-many-variants", type=int, default=50)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-resample", type=int, default=2000)
    p.add_argument("--out", type=Path, default=None, help="output JSON path (default: cli_runs/<stem>_matrix_sanity.json)")
    p.add_argument("--dry-run", action="store_true", help="validate inputs + print plan, do not run")
    return p


def run(args: argparse.Namespace) -> int:
    if not args.matrix_csv.is_file():
        print(f"[BLOCKED] matrix CSV not found: {args.matrix_csv}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"[dry-run] would run matrix_sanity on {args.matrix_csv} "
              f"(metric={args.metric_col}, label={args.label_col}, "
              f"higher_is_better={not args.lower_is_better}, seed={args.seed})")
        return 0

    df = pd.read_csv(args.matrix_csv)
    for col in (args.metric_col, args.label_col):
        if col not in df.columns:
            print(f"[BLOCKED] column {col!r} not in {args.matrix_csv} (have: {list(df.columns)})", file=sys.stderr)
            return 2

    result = matrix_sanity(
        df,
        metric_col=args.metric_col,
        label_col=args.label_col,
        higher_is_better=not args.lower_is_better,
        null_reference=args.null_reference,
        null_std=args.null_std,
        n_resample=args.n_resample,
        seed=args.seed,
        too_many_variants=args.too_many_variants,
    )

    out_path = args.out or (DEFAULT_OUTPUT_DIR / f"{args.matrix_csv.stem}_matrix_sanity.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_meta": {
            **SAFETY_META,
            "kind": "edge_discovery.matrix_sanity",
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "input_csv": str(args.matrix_csv.relative_to(ROOT)) if args.matrix_csv.is_relative_to(ROOT) else str(args.matrix_csv),
        },
        "result": result.to_dict(),
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    print(f"  best={result.best_value:+.5f} ({result.best_label}), flags={result.flags}")
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
