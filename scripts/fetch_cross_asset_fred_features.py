#!/usr/bin/env python3
"""Fetch FRED cross-asset features — read-only, diagnostic only."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.cross_asset_features.fred import (
    fetch_all_fred_features,
    get_fred_api_key,
    write_blocked_report,
)
from research.cross_asset_features.normalizer import write_normalized_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch FRED cross-asset features (diagnostic only)")
    parser.add_argument("--observation-start", default="2019-01-01")
    parser.add_argument("--observation-end", default=None)
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

    api_key = get_fred_api_key()
    if not api_key:
        out = write_blocked_report(
            args.output_dir,
            reason="FRED_API_KEY not set in environment or .env",
        )
        print(f"BLOCKED: FRED_API_KEY missing — wrote {out}")
        return 2

    results, status = fetch_all_fred_features(
        cache_dir=args.cache_dir,
        observation_start=args.observation_start,
        observation_end=args.observation_end,
    )
    for r in results:
        print(f"{r.feature_id} ({r.series_id}): {r.status} rows={r.rows}")
    if status != "OK":
        print(f"FRED fetch finished with status={status}", file=sys.stderr)
        return 1

    paths = write_normalized_outputs(
        ROOT,
        args.output_dir,
        observation_start=args.observation_start,
        observation_end=args.observation_end,
    )
    print(f"Wrote normalized outputs: {paths}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
