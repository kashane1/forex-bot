#!/usr/bin/env python3
"""Orchestrate full-window external feature ingest — diagnostic only."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.cross_asset_features.fred import run_fred_fetch_for_window
from research.cross_asset_features.local_csv_fallback import write_local_csv_fallback_status
from research.cross_asset_features.normalizer import write_normalized_outputs
from research.cross_asset_features.research_window import (
    research_window_report,
    resolve_h4_research_window,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Full-window external data pipeline (diagnostic only)")
    parser.add_argument("--warmup-start", default="2018-01-01")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "research" / "cross_asset_features")
    parser.add_argument(
        "--allow-fixture-fallback",
        action="store_true",
        help="Allow fixture fallback when FRED/local CSV unavailable (default: false for full-window)",
    )
    args = parser.parse_args()

    try:
        window = resolve_h4_research_window(ROOT, warmup_start=args.warmup_start)
    except (FileNotFoundError, ValueError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2

    h4_report = research_window_report(ROOT)
    print(
        f"H4 window: {window.h4_first} -> {window.h4_last}; "
        f"observations {window.observation_start} -> {window.observation_end}"
    )

    cache_dir = ROOT / "data" / "external_features" / ".fred_cache"
    results, fetch_report = run_fred_fetch_for_window(
        cache_dir=cache_dir,
        observation_start=window.observation_start,
        observation_end=window.observation_end,
        output_dir=args.output_dir,
        h4_first=str(window.h4_first),
        h4_last=str(window.h4_last),
    )
    write_local_csv_fallback_status(ROOT)

    allow_fixtures = args.allow_fixture_fallback
    if fetch_report["overall_status"] == "BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED":
        print("FRED fetch blocked — see fred_fetch_status_real_window.json")
        if not allow_fixtures:
            print("Full-window mode: not using fixture fallback")

    paths = write_normalized_outputs(
        ROOT,
        args.output_dir,
        observation_start=window.observation_start,
        observation_end=window.observation_end,
        allow_fixture_fallback=allow_fixtures,
        h4_window=h4_report,
    )
    print(f"Normalized outputs: {paths}")
    for r in results:
        print(f"  {r.feature_id}: {r.status} rows={r.rows}")
    return 0 if fetch_report.get("required_series_complete") else 2


if __name__ == "__main__":
    raise SystemExit(main())
