#!/usr/bin/env python3
"""Align normalized cross-asset features to H4 research timestamps."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.cost_atlas.loader import SEVEN_PAIR_UNIVERSE, load_deduped_h4_frame
from research.cross_asset_features.alignment import load_normalized_wide, write_h4_alignment_outputs
from research.cross_asset_features.normalizer import write_normalized_outputs
from research.edge_discovery.real_data import resolve_h4_store_path


def _load_h4_index(repo_root: Path, db_path: Path | None) -> pd.DatetimeIndex:
    db_path = db_path or resolve_h4_store_path(repo_root)
    if db_path is None:
        raise FileNotFoundError("H4 SQLite store not found")
    indices: list[pd.DatetimeIndex] = []
    for instrument in SEVEN_PAIR_UNIVERSE:
        frame, _ = load_deduped_h4_frame(repo_root, instrument, db_path=db_path)
        if len(frame):
            indices.append(frame.index)
    if not indices:
        raise ValueError("no H4 bars loaded")
    combined = indices[0]
    for idx in indices[1:]:
        combined = combined.union(idx)
    return combined.sort_values()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--normalized-csv",
        type=Path,
        default=ROOT / "research" / "cross_asset_features" / "normalized_features.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "research" / "cross_asset_features",
    )
    parser.add_argument("--db-path", type=Path, default=None)
    args = parser.parse_args()

    if not args.normalized_csv.is_file():
        write_normalized_outputs(ROOT, args.output_dir)
    wide = load_normalized_wide(args.normalized_csv)
    try:
        h4_index = _load_h4_index(ROOT, args.db_path)
    except FileNotFoundError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    paths = write_h4_alignment_outputs(ROOT, h4_index, wide, args.output_dir)
    print(f"Wrote H4 alignment outputs: {paths}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
