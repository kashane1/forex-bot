#!/usr/bin/env python3
"""Build the H4 cost atlas from local deduped bid/ask candles.

Diagnostic infrastructure only — no strategy, no broker orders.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.cost_atlas.atlas import build_cost_atlas, write_cost_atlas_outputs
from research.edge_discovery.real_data import resolve_h4_store_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build H4 cost atlas (diagnostic only)")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "research" / "cost_atlas",
        help="Directory for compact atlas outputs",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Override H4 SQLite path (default: resolve from repo)",
    )
    args = parser.parse_args()
    db_path = args.db_path or resolve_h4_store_path(ROOT)
    if db_path is None:
        print(
            "BLOCKED: H4 SQLite store not found. Restore data/campaign_002.sqlite3 "
            "or set EDGE_DISCOVERY_H4_DB.",
            file=sys.stderr,
        )
        return 2
    result = build_cost_atlas(ROOT, db_path=db_path)
    write_cost_atlas_outputs(result, args.output_dir)
    print(f"Wrote cost atlas to {args.output_dir} ({result.summary['bar_count']} bars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
