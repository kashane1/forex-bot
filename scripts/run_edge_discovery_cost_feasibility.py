"""Edge-discovery CLI — cost feasibility flags.

Local-only diagnostic. Turns spread/ATR ratios (per pair, timeframe, or session)
into pre-campaign cost-feasibility flags so a structurally cost-hostile cell is
rejected before a campaign is built. Reads either a JSON mapping
(``{"M5": 0.45, ...}``) or a CSV with ``label`` + ``spread_atr_ratio`` columns.

Approves nothing, opens no test lockbox, never calls the broker. Writes compact
JSON + CSV artifacts under ``research/edge_discovery/cli_runs/``.

    python scripts/run_edge_discovery_cost_feasibility.py \
        --ratios-json '{"M3":0.59,"M5":0.45,"M15":0.23,"M30":0.15}' \
        --kind timeframe --hostile-ratio 0.25

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

from research.edge_discovery.cost_feasibility import (
    DEFAULT_HOSTILE_RATIO,
    cost_feasibility_table,
)

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
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--ratios-json", type=str, help="inline JSON {label: spread_atr_ratio} or a path to one")
    src.add_argument("--ratios-csv", type=Path, help="CSV with label + spread_atr_ratio columns")
    p.add_argument("--label-col", default="label")
    p.add_argument("--ratio-col", default="spread_atr_ratio")
    p.add_argument("--kind", choices=["pair", "timeframe", "session", "none"], default="none")
    p.add_argument("--hostile-ratio", type=float, default=DEFAULT_HOSTILE_RATIO)
    p.add_argument("--flag-pairs-vs-median", action="store_true")
    p.add_argument("--out-prefix", type=str, default="cost_feasibility")
    p.add_argument("--dry-run", action="store_true")
    return p


def _load_ratios(args: argparse.Namespace) -> dict[str, float] | None:
    if args.ratios_json is not None:
        candidate = Path(args.ratios_json)
        text = candidate.read_text(encoding="utf-8") if candidate.is_file() else args.ratios_json
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            print(f"[BLOCKED] could not parse --ratios-json: {exc}", file=sys.stderr)
            return None
        return {str(k): float(v) for k, v in data.items()}
    if not args.ratios_csv.is_file():
        print(f"[BLOCKED] ratios CSV not found: {args.ratios_csv}", file=sys.stderr)
        return None
    df = pd.read_csv(args.ratios_csv)
    if args.label_col not in df.columns or args.ratio_col not in df.columns:
        print(f"[BLOCKED] {args.ratios_csv} needs {args.label_col!r} + {args.ratio_col!r} "
              f"(have: {list(df.columns)})", file=sys.stderr)
        return None
    return {str(r[args.label_col]): float(r[args.ratio_col]) for _, r in df.iterrows()}


def run(args: argparse.Namespace) -> int:
    ratios = _load_ratios(args)
    if ratios is None:
        return 2
    if not ratios:
        print("[BLOCKED] no ratios to classify", file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"[dry-run] would classify {len(ratios)} cells (kind={args.kind}, hostile={args.hostile_ratio})")
        return 0

    kind = None if args.kind == "none" else args.kind
    table = cost_feasibility_table(
        ratios, kind=kind, hostile_ratio=args.hostile_ratio,
        flag_pairs_vs_median=args.flag_pairs_vs_median,
    )

    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = DEFAULT_OUTPUT_DIR / f"{args.out_prefix}.csv"
    json_path = DEFAULT_OUTPUT_DIR / f"{args.out_prefix}.json"
    table.to_csv(csv_path, index=False)
    payload = {
        "_meta": {
            **SAFETY_META,
            "kind": "edge_discovery.cost_feasibility",
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "hostile_ratio": args.hostile_ratio,
            "cell_kind": args.kind,
        },
        "cells": table.to_dict(orient="records"),
    }
    json_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {csv_path} and {json_path}")
    for rec in table.to_dict(orient="records"):
        print(f"  {rec['label']}: ratio={rec['spread_atr_ratio']:.3f} flags={rec['flags']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
