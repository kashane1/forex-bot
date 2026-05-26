#!/usr/bin/env python3
"""Fetch FRED cross-asset features — read-only, diagnostic only."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.cross_asset_features.fred import (
    get_fred_api_key,
    run_fred_fetch_for_window,
    write_blocked_report,
)
from research.cross_asset_features.normalizer import write_normalized_outputs
from research.cross_asset_features.research_window import resolve_h4_research_window


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch FRED cross-asset features (diagnostic only)")
    parser.add_argument("--observation-start", default=None)
    parser.add_argument("--observation-end", default=None)
    parser.add_argument("--use-h4-window", action="store_true", default=True)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=ROOT / "data" / "external_features" / ".fred_cache",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "research" / "cross_asset_features",
    )
    args = parser.parse_args()

    obs_start = args.observation_start
    obs_end = args.observation_end
    if args.use_h4_window and obs_start is None:
        try:
            window = resolve_h4_research_window(ROOT, warmup_start="2018-01-01")
            obs_start = window.observation_start
            obs_end = obs_end or window.observation_end
        except FileNotFoundError:
            obs_start = obs_start or "2018-01-01"
    obs_start = obs_start or "2018-01-01"

    api_key = get_fred_api_key()
    if not api_key:
        out = write_blocked_report(
            args.output_dir,
            reason="FRED_API_KEY not set in environment or .env",
        )
        run_fred_fetch_for_window(
            cache_dir=args.cache_dir,
            observation_start=obs_start,
            observation_end=obs_end,
            output_dir=args.output_dir,
        )
        print(f"BLOCKED: FRED_API_KEY missing — wrote {out}")
        return 2

    results, status_report = run_fred_fetch_for_window(
        cache_dir=args.cache_dir,
        observation_start=obs_start,
        observation_end=obs_end,
        output_dir=args.output_dir,
    )
    for r in results:
        print(f"{r.feature_id} ({r.series_id}): {r.status} rows={r.rows}")
    if status_report["overall_status"] != "OK":
        print(f"FRED fetch finished with status={status_report['overall_status']}", file=sys.stderr)
        return 1

    paths = write_normalized_outputs(
        ROOT,
        args.output_dir,
        observation_start=obs_start,
        observation_end=obs_end,
        allow_fixture_fallback=False,
    )
    print(f"Wrote normalized outputs: {paths}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
