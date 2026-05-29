"""Edge-discovery CLI — matched-null benchmark.

Local-only diagnostic. Reads a trade/signal ledger CSV (``instrument``,
``side``, ``entry_time``, optional ``bars_held``) plus per-pair candle frames,
and reports the strategy's forward-return expectancy against a structure-matched
null distribution.

Frames are read from a directory of per-pair CSVs (``<PAIR>.csv``, loadable by
``loaders.load_candles_csv``). If frames are unavailable in this checkout the
script BLOCKS cleanly (exit 2) rather than fabricating data — the lab's
default-local-only policy.

Approves nothing, opens no test lockbox, never calls the broker.

    python scripts/run_edge_discovery_matched_null.py \
        --ledger-csv path/to/ledger.csv --frames-dir path/to/frames \
        --mode all --window-bars 6 --seeds 0-19 --apply-cost

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

from research.edge_discovery.costs import apply_cost_overlay
from research.edge_discovery.loaders import load_candles_csv
from research.edge_discovery.matched_nulls import (
    MATCHED_NULL_MODES,
    interpret_matched_null,
    matched_null_baseline,
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


def _parse_seeds(spec: str) -> list[int]:
    if "-" in spec and "," not in spec:
        lo, hi = spec.split("-", 1)
        return list(range(int(lo), int(hi) + 1))
    return [int(s) for s in spec.split(",") if s.strip()]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ledger-csv", type=Path, required=True)
    p.add_argument("--frames-dir", type=Path, required=True, help="dir of <PAIR>.csv candle frames")
    p.add_argument("--mode", default="all", help=f"one of {MATCHED_NULL_MODES} or 'all'")
    p.add_argument("--window-bars", type=int, default=6)
    p.add_argument("--seeds", default="0-19", help="e.g. '0-19' or '0,1,2'")
    p.add_argument("--pair-col", default="instrument")
    p.add_argument("--side-col", default="side")
    p.add_argument("--time-col", default="entry_time")
    p.add_argument("--hold-col", default="bars_held")
    p.add_argument("--apply-cost", action="store_true")
    p.add_argument("--min-bucket", type=int, default=5)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--dry-run", action="store_true")
    return p


def _load_frames(frames_dir: Path, pairs: list[str]) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for pair in pairs:
        path = frames_dir / f"{pair}.csv"
        if path.is_file():
            frames[pair] = load_candles_csv(path).frame
    return frames


def run(args: argparse.Namespace) -> int:
    if not args.ledger_csv.is_file():
        print(f"[BLOCKED] ledger CSV not found: {args.ledger_csv}", file=sys.stderr)
        return 2
    if not args.frames_dir.is_dir():
        print(f"[BLOCKED] frames dir not found: {args.frames_dir} "
              "(matched-null needs per-pair candle frames; none available locally)", file=sys.stderr)
        return 2
    modes = list(MATCHED_NULL_MODES) if args.mode == "all" else [args.mode]
    if args.mode != "all" and args.mode not in MATCHED_NULL_MODES:
        print(f"[BLOCKED] unknown mode {args.mode!r}; expected one of {MATCHED_NULL_MODES} or 'all'", file=sys.stderr)
        return 2
    seeds = _parse_seeds(args.seeds)

    ledger = pd.read_csv(args.ledger_csv)
    if args.pair_col not in ledger.columns:
        print(f"[BLOCKED] ledger missing pair column {args.pair_col!r}", file=sys.stderr)
        return 2
    pairs = sorted(ledger[args.pair_col].astype(str).unique())
    frames = _load_frames(args.frames_dir, pairs)
    if not frames:
        print(f"[BLOCKED] no candle frames found in {args.frames_dir} for pairs {pairs}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"[dry-run] modes={modes}, pairs_with_frames={sorted(frames)}, "
              f"window={args.window_bars}, seeds={len(seeds)}, apply_cost={args.apply_cost}")
        return 0

    cost_fn = apply_cost_overlay if args.apply_cost else None
    results = []
    for mode in modes:
        res = matched_null_baseline(
            ledger, frames, mode=mode, window_bars=args.window_bars, seeds=seeds,
            pair_col=args.pair_col, side_col=args.side_col, time_col=args.time_col,
            hold_col=args.hold_col, apply_cost_overlay_fn=cost_fn, min_bucket=args.min_bucket,
        )
        results.append({"result": res.to_dict(), "interpretation": interpret_matched_null(res)})

    out_path = args.out or (DEFAULT_OUTPUT_DIR / f"{args.ledger_csv.stem}_matched_null.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_meta": {
            **SAFETY_META,
            "kind": "edge_discovery.matched_null",
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "modes": modes,
            "apply_cost": args.apply_cost,
        },
        "results": results,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    for r in results:
        print(f"  {r['result']['mode']}: flags={r['interpretation']['flags']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
