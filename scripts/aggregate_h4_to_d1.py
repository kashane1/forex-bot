#!/usr/bin/env python3
"""Aggregate real OANDA H4 candles into D1AGG research candles.

Reads completed H4 bid/ask candles from a campaign SQLite store and
writes synthetic daily (D1AGG) candles plus a provenance / classification
summary. This runs no strategy and produces no trading result — it is a
data-preparation tool. See docs/research/D1_AGGREGATION_DESIGN.md.

Example:
  python scripts/aggregate_h4_to_d1.py \\
      --db data/campaign_002.sqlite3 --instrument EUR_USD \\
      --from 2024-01-01 --to 2024-02-01 \\
      --out research/d1_aggregation/sample_EUR_USD_H4_to_D1.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True, help="SQLite candle store path")
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--from", dest="from_date", required=True, help="ISO date")
    ap.add_argument("--to", dest="to_date", required=True, help="ISO date")
    ap.add_argument("--out", required=True, help="output CSV for D1AGG candles")
    args = ap.parse_args()

    frm = datetime.fromisoformat(args.from_date).replace(tzinfo=UTC)
    to = datetime.fromisoformat(args.to_date).replace(tzinfo=UTC)

    repo = CandleRepo(Database(args.db))
    h4 = repo.list(
        args.instrument, "H4", completed_only=True, from_time=frm, to_time=to,
    )
    if not h4:
        raise SystemExit(
            f"no completed H4 candles for {args.instrument} in {frm}..{to}"
        )

    result = aggregate_h4_to_d1(list(h4), instrument=args.instrument)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "time", "granularity", "bid_o", "bid_h", "bid_l", "bid_c",
            "ask_o", "ask_h", "ask_l", "ask_c", "volume", "complete",
        ])
        for c in result.candles:
            writer.writerow([
                c.time.isoformat(), c.granularity,
                c.bid_o, c.bid_h, c.bid_l, c.bid_c,
                c.ask_o, c.ask_h, c.ask_l, c.ask_c, c.volume, c.complete,
            ])

    meta = {
        "instrument": result.instrument,
        "source": "H4 -> D1AGG aggregation (no strategy, no trading result)",
        "window": {"from": args.from_date, "to": args.to_date},
        "source_h4_count": result.source_h4_count,
        "source_hash": result.source_hash,
        "alignment_hour": result.alignment_hour,
        "alignment_tz": result.alignment_tz,
        "d1agg_candles": len(result.candles),
        "aggregated_days": result.aggregated_count,
        "incomplete_days": result.incomplete_count,
        "ambiguous_days": result.ambiguous_count,
        "missing_weekdays": [d.isoformat() for d in result.missing_weekdays],
    }
    meta_path = out.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"wrote {len(result.candles)} D1AGG candles -> {out}")
    print(
        f"  aggregated={result.aggregated_count} "
        f"incomplete={result.incomplete_count} "
        f"ambiguous={result.ambiguous_count} "
        f"missing_weekdays={len(result.missing_weekdays)}"
    )
    print(f"  source_h4={result.source_h4_count} "
          f"source_hash={result.source_hash[:16]}")
    print(f"  meta -> {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
