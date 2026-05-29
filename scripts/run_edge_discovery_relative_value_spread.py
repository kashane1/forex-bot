"""Edge-discovery CLI — CAMPAIGN_028 relative-value spread reversion front-gate screen.

Local-only diagnostic. Reads completed H4 mid-close bars for the 7 majors from
the canonical SQLite store, builds every candidate leg1-leg2 spread, and runs the
front-gate screen (cost feasibility → forward-return info → matched null →
filter-adds-edge → best-of-N matrix sanity) on the **train window only**.

It approves nothing, opens no test lockbox, never calls the broker, and never
touches validation or the sealed TEST window. The lab cannot emit a verdict word.

    PYTHONPATH=$PWD/src python scripts/run_edge_discovery_relative_value_spread.py
    PYTHONPATH=$PWD/src python scripts/run_edge_discovery_relative_value_spread.py --dry-run
    PYTHONPATH=$PWD/src python scripts/run_edge_discovery_relative_value_spread.py \
        --lookback 60 --threshold 2.0 --window-bars 12

If the H4 store is unavailable in this checkout the script BLOCKS cleanly
(exit 2) rather than fabricating data — the lab's default-local-only policy.
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
from research.edge_discovery.real_data import (
    SEVEN_MAJORS,
    load_h4_candles_from_sqlite,
    resolve_h4_store_path,
)
from research.edge_discovery.relative_value_spread import (
    DEFAULT_LOOKBACK,
    DEFAULT_THRESHOLD,
    DEFAULT_WINDOW_BARS,
    TRAIN_END,
    TRAIN_START,
    candidate_pairs,
    screen_one_spread,
)

DEFAULT_OUTPUT_DIR = ROOT / "research" / "campaign_028" / "front_gate"

SAFETY_META = {
    "diagnostic_only": True,
    "strategy_evidence": False,
    "not_approved": True,
    "approves_strategy": False,
    "test_lockbox_opened": False,
    "NOT_edge_claim": True,
    "train_only": True,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--lookback", type=int, default=DEFAULT_LOOKBACK)
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    p.add_argument("--window-bars", type=int, default=DEFAULT_WINDOW_BARS)
    p.add_argument("--from-time", default=TRAIN_START)
    p.add_argument("--to-time", default=TRAIN_END, help="must not reach past the train end")
    p.add_argument("--no-financing", action="store_true", help="disable financing-stress overlay")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--dry-run", action="store_true")
    return p


def _guard_train_only(to_time: str) -> None:
    if to_time > TRAIN_END:
        raise SystemExit(
            f"[BLOCKED] --to-time {to_time!r} reaches past the train end {TRAIN_END!r}. "
            "The front-gate screen runs on TRAIN ONLY; validation/TEST stay sealed."
        )


def _md_report(payload: dict) -> str:
    rows = payload["spreads"]
    ms = payload["matrix_sanity"]
    lines: list[str] = []
    lines.append("# CAMPAIGN_028 — relative-value spread reversion front-gate screen")
    lines.append("")
    lines.append("> Exploratory edge-discovery lab output. Train-only. Not a strategy verdict; ")
    lines.append("> does not approve, promote, or change any campaign status. ")
    lines.append("> See `docs/research/CAMPAIGN_028_NEW_THESIS_BRIEF.md`.")
    lines.append("")
    lines.append("## Setup")
    lines.append("")
    cfg = payload["_meta"]
    lines.append(f"- Train window: `{cfg['from_time']}` → `{cfg['to_time']}`")
    lines.append(f"- Lookback: `{cfg['lookback']}`  Threshold |z|: `{cfg['threshold']}`  Hold (bars): `{cfg['window_bars']}`")
    lines.append(f"- Financing stress: `{cfg['apply_financing']}`  Candidate spreads: `{len(rows)}`")
    lines.append("")
    lines.append("## Per-spread screen (sorted by post-cost mean)")
    lines.append("")
    lines.append("| spread | beta | n | half-life | spread/ATR | cost flags | pre-cost | post-cost | null band | gap σ | filter adds edge |")
    lines.append("|---|---:|---:|---:|---:|---|---:|---:|---|---:|:--:|")
    for r in sorted(rows, key=lambda x: x["post_cost_mean"], reverse=True):
        hl = f"{r['half_life_bars']:.1f}" if r["half_life_bars"] is not None else "—"
        gns = f"{r['gap_in_null_stds']:+.2f}" if r["gap_in_null_stds"] is not None else "—"
        lines.append(
            f"| {r['label']} | {r['beta']:+.3f} | {r['n_signals']} | {hl} | "
            f"{r['spread_atr_ratio']:.3f} | {';'.join(r['cost_flags'])} | "
            f"{r['pre_cost_mean']:+.6f} | {r['post_cost_mean']:+.6f} | {r['null_band']} | "
            f"{gns} | {'yes' if r['filter_adds_edge'] else 'no'} |"
        )
    lines.append("")
    lines.append("## Best-of-N matrix sanity (selection-noise check)")
    lines.append("")
    lines.append(f"- Variants screened: `{ms['n_variants']}`")
    lines.append(f"- Best: `{ms['best_label']}` = `{ms['best_value']:+.6f}` (median `{ms['median_value']:+.6f}`)")
    lines.append(f"- Null reference: `{ms['null_reference']}`  best vs null: `{ms['best_vs_null']}`")
    lines.append(f"- Expected best-of-N under noise: `{ms['expected_max_under_null']:+.6f}` (p95 `{ms['expected_max_p95']:+.6f}`)")
    lines.append(f"- Deflated improvement: `{ms['deflated_improvement']:+.6f}`")
    lines.append(f"- P(best ≤ noise max): `{ms['prob_best_le_null_max']:.3f}`")
    lines.append(f"- Flags: `{';'.join(ms['flags'])}`")
    lines.append("")
    lines.append("## Reading this (front-gate decision logic)")
    lines.append("")
    lines.append("- A spread is a live candidate only if it is `COST_FEASIBLE`, its post-cost ")
    lines.append("  mean is `materially_above_null`, and `filter adds edge = yes`.")
    lines.append("- The whole thesis advances to a precommit scaffold only if the best spread is ")
    lines.append("  `ROBUST_MATRIX_SIGNAL` (not `LIKELY_SELECTION_NOISE`) across the candidate set.")
    lines.append("- Any other outcome → CAMPAIGN_028 is written up as a documented rejection, ")
    lines.append("  freeze intact, exactly as C026 closed the timeframe ladder.")
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    _guard_train_only(args.to_time)
    store = resolve_h4_store_path(ROOT)
    if store is None:
        print(
            "[BLOCKED] canonical H4 SQLite store not found "
            "(tried $EDGE_DISCOVERY_H4_DB, ./data, and the worktree-parent checkout). "
            "Provide data/campaign_002.sqlite3 to run the screen; not fabricating data.",
            file=sys.stderr,
        )
        return 2

    pairs = candidate_pairs(list(SEVEN_MAJORS))
    if args.dry_run:
        print(
            f"[dry-run] store={store}\n  train={args.from_time}→{args.to_time} "
            f"lookback={args.lookback} threshold={args.threshold} window={args.window_bars}\n"
            f"  spreads={len(pairs)} financing={not args.no_financing}"
        )
        return 0

    # Load each major's train-window H4 frame once.
    frames: dict[str, pd.DataFrame] = {}
    for instr in SEVEN_MAJORS:
        frames[instr] = load_h4_candles_from_sqlite(
            store, instr, from_time=args.from_time, to_time=args.to_time
        ).frame

    spreads: list[dict] = []
    for a, b in pairs:
        res = screen_one_spread(
            frames[a], frames[b],
            instrument1=a, instrument2=b,
            lookback=args.lookback, threshold=args.threshold, window_bars=args.window_bars,
            apply_financing=not args.no_financing,
        )
        spreads.append(res.to_dict())

    table = pd.DataFrame(
        {"label": [s["label"] for s in spreads],
         "expectancy_r": [s["post_cost_mean"] for s in spreads]}
    )
    ms = matrix_sanity(
        table, metric_col="expectancy_r", label_col="label",
        higher_is_better=True, null_reference=0.0, seed=20260528,
    ).to_dict()

    payload = {
        "_meta": {
            **SAFETY_META,
            "kind": "edge_discovery.relative_value_spread",
            "campaign": "CAMPAIGN_028",
            "phase": "front_gate_screen",
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "store_path": str(store),
            "from_time": args.from_time,
            "to_time": args.to_time,
            "lookback": args.lookback,
            "threshold": args.threshold,
            "window_bars": args.window_bars,
            "apply_financing": not args.no_financing,
            "universe": list(SEVEN_MAJORS),
        },
        "spreads": spreads,
        "matrix_sanity": ms,
    }

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "relative_value_spread_screen.json"
    md_path = out_dir / "relative_value_spread_screen.md"
    json_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    md_path.write_text(_md_report(payload) + "\n", encoding="utf-8")

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    feasible = [s for s in spreads if "COST_FEASIBLE" in s["cost_flags"]]
    above = [s for s in spreads if s["null_band"] in ("slightly_above_null", "materially_above_null")]
    adds = [s for s in spreads if s["filter_adds_edge"]]
    print(f"  cost_feasible: {len(feasible)}/{len(spreads)}  above_null: {len(above)}  filter_adds_edge: {len(adds)}")
    print(f"  matrix_sanity flags: {';'.join(ms['flags'])}  best={ms['best_label']} ({ms['best_value']:+.6f})")
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
