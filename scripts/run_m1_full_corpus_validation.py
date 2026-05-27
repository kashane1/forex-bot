#!/usr/bin/env python3
"""Run full M1 corpus validation phases (inventory, quality, aggregation, drift)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.m1_corpus_validation import (
    MAJOR_PAIRS,
    aggregation_coverage_for_pair,
    d1agg_for_pair,
    h4_drift_for_pair,
    inventory_sql,
    ltf_alignment_for_pair,
    overall_status,
    preflight_for_pair,
    quality_for_pair,
    write_csv,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ

OUTPUT_DIR = ROOT / "research" / "m1_full_corpus_validation"


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_inventory(store: PostgresCandleStore) -> dict:
    payload = inventory_sql(store)
    payload["generated_at_utc"] = datetime.now(UTC).isoformat()
    _write_json(OUTPUT_DIR / "m1_corpus_inventory.json", payload)
    return payload


def run_quality(store: PostgresCandleStore) -> dict:
    by_pair = [quality_for_pair(store, instrument) for instrument in MAJOR_PAIRS]
    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "pairs": by_pair,
        "overall_status": overall_status([p["status"] for p in by_pair]),
    }
    _write_json(OUTPUT_DIR / "m1_quality_summary.json", summary)
    write_csv(
        OUTPUT_DIR / "m1_quality_by_pair.csv",
        by_pair,
        [
            "instrument",
            "status",
            "actual_m1_count",
            "missing_minutes",
            "duplicate_timestamps",
            "incomplete_candles",
            "negative_or_zero_spreads",
            "extreme_spreads",
            "bid_ask_violations",
            "ohlc_violations",
        ],
    )
    gap_rows = [
        {"instrument": p["instrument"], **gap}
        for p in by_pair
        for gap in p.get("largest_gaps", [])
    ]
    write_csv(OUTPUT_DIR / "m1_gap_summary_by_pair.csv", gap_rows, ["instrument", "start", "minutes"])
    spread_rows = [
        {"instrument": p["instrument"], **{k: v for k, v in p.get("spread_percentiles", {}).items()}}
        for p in by_pair
    ]
    fieldnames = ["instrument"] + sorted({k for row in spread_rows for k in row if k != "instrument"})
    write_csv(OUTPUT_DIR / "m1_spread_percentiles_by_pair.csv", spread_rows, fieldnames)
    return summary


def run_aggregation(store: PostgresCandleStore) -> dict:
    by_pair = [aggregation_coverage_for_pair(store, instrument) for instrument in MAJOR_PAIRS]
    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "pairs": by_pair,
        "overall_status": "PASS",
    }
    _write_json(OUTPUT_DIR / "aggregate_coverage_summary.json", summary)
    flat: list[dict] = []
    for pair in by_pair:
        for tf, stats in pair["timeframes"].items():
            flat.append({"instrument": pair["instrument"], "timeframe": tf, **stats})
    write_csv(
        OUTPUT_DIR / "aggregate_coverage_by_pair.csv",
        flat,
        [
            "instrument",
            "timeframe",
            "bar_count",
            "first_timestamp",
            "last_timestamp",
            "omitted_incomplete_blocks",
            "incomplete_bars",
            "avg_source_m1_per_bar",
            "coverage_pct_vs_m1",
        ],
    )
    return summary


def run_h4_drift(store: PostgresCandleStore) -> dict:
    by_pair = [h4_drift_for_pair(store, instrument) for instrument in MAJOR_PAIRS]
    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "pairs": by_pair,
        "overall_status": overall_status([p["status"] for p in by_pair]),
    }
    _write_json(OUTPUT_DIR / "h4_drift_summary.json", summary)
    write_csv(
        OUTPUT_DIR / "h4_drift_by_pair.csv",
        by_pair,
        [
            "instrument",
            "status",
            "native_h4_count",
            "derived_h4_count",
            "overlap_count",
            "exact_match_count",
            "ohlc_mismatch_count",
            "missing_in_derived_count",
            "extra_in_derived_count",
        ],
    )
    examples = [ex for p in by_pair for ex in p.get("examples", [])]
    if examples:
        write_csv(OUTPUT_DIR / "h4_drift_examples.csv", examples, ["timestamp", "diffs"])
    return summary


def run_d1agg(store: PostgresCandleStore) -> dict:
    by_pair = [d1agg_for_pair(store, instrument) for instrument in MAJOR_PAIRS]
    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "pairs": by_pair,
        "overall_status": overall_status([p["status"] for p in by_pair]),
    }
    _write_json(OUTPUT_DIR / "d1agg_convention_summary.json", summary)
    write_csv(
        OUTPUT_DIR / "d1agg_by_pair.csv",
        by_pair,
        [
            "instrument",
            "status",
            "m1_derived_d1agg_count",
            "h4_derived_d1agg_count",
            "overlap_count",
            "ohlc_mismatch_count",
            "incomplete_days",
            "ambiguous_days",
        ],
    )
    return summary


def run_alignment(store: PostgresCandleStore) -> dict:
    m15 = [ltf_alignment_for_pair(store, instrument, execution_timeframe="M15") for instrument in MAJOR_PAIRS]
    m5 = [ltf_alignment_for_pair(store, instrument, execution_timeframe="M5") for instrument in MAJOR_PAIRS[:2]]
    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "m15": m15,
        "m5_subset": m5,
        "overall_status": overall_status([p["status"] for p in m15]),
    }
    _write_json(OUTPUT_DIR / "ltf_htf_alignment_summary.json", summary)
    write_csv(
        OUTPUT_DIR / "ltf_htf_alignment_by_pair.csv",
        m15,
        [
            "instrument",
            "status",
            "execution_timeframe",
            "decision_samples",
            "lookahead_violations",
            "stale_features",
            "unavailable_features",
        ],
    )
    return summary


def run_preflight(store: PostgresCandleStore) -> dict:
    by_pair = [preflight_for_pair(store, instrument) for instrument in MAJOR_PAIRS]
    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "pairs": by_pair,
        "overall_status": overall_status([p["status"] for p in by_pair]),
    }
    _write_json(OUTPUT_DIR / "ltf_preflight_summary.json", summary)
    return summary


PHASE_RUNNERS = {
    "inventory": run_inventory,
    "quality": run_quality,
    "aggregation": run_aggregation,
    "h4-drift": run_h4_drift,
    "d1agg": run_d1agg,
    "alignment": run_alignment,
    "preflight": run_preflight,
}


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="M1 full corpus validation runner.")
    parser.add_argument(
        "--phase",
        choices=[*PHASE_RUNNERS.keys(), "all"],
        default="all",
        help="Validation phase to run",
    )
    args = parser.parse_args(argv)
    cfg = get_research_database_config(environ=environ, require=True)
    store = PostgresCandleStore(cfg)
    phases = list(PHASE_RUNNERS) if args.phase == "all" else [args.phase]
    results: dict[str, object] = {}
    for phase in phases:
        print(f"running phase: {phase}", file=sys.stderr, flush=True)
        results[phase] = PHASE_RUNNERS[phase](store)
    print(json.dumps({"phases": phases, "output_dir": str(OUTPUT_DIR)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
