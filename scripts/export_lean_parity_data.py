#!/usr/bin/env python3
"""Export real OANDA H4 candles to Lean custom-data CSV for a parity run.

Reads completed H4 bid/ask candles from a local SQLite store and writes
a Lean custom-data CSV plus a provenance sidecar JSON (data hash, count,
window, and the CAMPAIGN_002 data-request hash so the Lean side can
confirm it is replaying the exact same candles).

Real data only. The export refuses synthetic candles — every candle's
`source` must be an `oanda-*` label. No QuantConnect cloud, no paid
service, no network call.

If no real OANDA H4 store is present, this script exports nothing and
exits non-zero. It never fabricates data. The CSV format is documented
in research/lean_parity/lean_h4_export_format.md.

Usage:
    python scripts/export_lean_parity_data.py \\
        --db data/oanda_h4_research.sqlite3 --instrument EUR_USD \\
        --from 2020-01-01 --to 2026-05-20

See docs/research/LEAN_PARITY_EXECUTION_GUIDE.md.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.backtesting.engine import compute_data_request_hash
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo
from forex_bot.domain.candles import Candle

# The rehydrated real-OANDA H4 store (scripts/rehydrate_oanda_h4_store.py).
DEFAULT_DB = ROOT / "data" / "oanda_h4_research.sqlite3"
DEFAULT_OUT_DIR = ROOT / "research" / "lean_parity" / "exports" / "campaign_002_h4"

# Lean custom-data CSV columns. `time` is the OANDA bar OPEN time
# (17:00-NY aligned); bid/ask OHLC are carried separately so the Lean
# algorithm can replicate the bespoke engine's bid/ask-aware fills.
LEAN_CSV_HEADER = [
    "time",
    "bid_open", "bid_high", "bid_low", "bid_close",
    "ask_open", "ask_high", "ask_low", "ask_close",
    "volume",
]


def candle_to_lean_row(c: Candle) -> list[str]:
    """One Lean custom-data CSV row from an H4 candle. Exact Decimal
    strings — no float round-trip — so the export is reproducible.

    Timestamps are normalised to UTC before serialisation so the
    output (and therefore ``data_sha256``) is independent of the
    exporting machine's local timezone — the bug that caused the
    2026-05-22 vs 2026-05-25 row-sha drift in
    ``research/lean_parity/exports/campaign_002_h4/``."""
    t_utc = c.time.astimezone(UTC) if c.time.tzinfo is not None else c.time.replace(tzinfo=UTC)
    return [
        t_utc.isoformat(),
        str(c.bid_o), str(c.bid_h), str(c.bid_l), str(c.bid_c),
        str(c.ask_o), str(c.ask_h), str(c.ask_l), str(c.ask_c),
        str(c.volume),
    ]


def data_sha256(candles: list[Candle]) -> str:
    """Deterministic hash over the exported candle rows."""
    hasher = hashlib.sha256()
    for c in sorted(candles, key=lambda x: x.time):
        hasher.update(("|".join(candle_to_lean_row(c))).encode("utf-8"))
    return hasher.hexdigest()


def sources_are_real_oanda(sources: list[str]) -> bool:
    """True only if every distinct candle source is an `oanda-*` label —
    the guard that keeps synthetic candles out of a parity export."""
    return bool(sources) and all(s.startswith("oanda") for s in sources)


def build_provenance(
    *,
    instrument: str,
    candles: list[Candle],
    source: str,
    from_arg: str,
    to_arg: str,
    csv_name: str,
) -> dict:
    # Same UTC normalisation as candle_to_lean_row so the provenance
    # first/last_ts strings are reproducible across timezones.
    first = (
        candles[0].time.astimezone(UTC) if candles[0].time.tzinfo is not None
        else candles[0].time.replace(tzinfo=UTC)
    ).isoformat()
    last = (
        candles[-1].time.astimezone(UTC) if candles[-1].time.tzinfo is not None
        else candles[-1].time.replace(tzinfo=UTC)
    ).isoformat()
    return {
        "instrument": instrument,
        "granularity": "H4",
        "source": source,
        "requested_from": from_arg,
        "requested_to": to_arg,
        "candle_count": len(candles),
        "first_ts": first,
        "last_ts": last,
        "data_sha256": data_sha256(candles),
        "campaign_002_data_request_hash": compute_data_request_hash(
            instrument=instrument,
            granularity="H4",
            from_time=from_arg,
            to_time=to_arg,
            source=source,
            candle_count=len(candles),
        ),
        "lean_csv": csv_name,
        "exported_by": "scripts/export_lean_parity_data.py",
        "exported_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "note": (
            "Real OANDA H4 bid/ask candles. Before comparing a Lean run, "
            "confirm campaign_002_data_request_hash matches the value in the "
            "CAMPAIGN_002 artifacts — that proves both engines replay the "
            "same candles."
        ),
    }


def distinct_sources(db: Database, instrument: str) -> list[str]:
    rows = db.fetchall(
        "SELECT DISTINCT source FROM candles WHERE instrument=? AND granularity='H4'",
        (instrument,),
    )
    return sorted(str(r["source"]) for r in rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="Export OANDA H4 candles for Lean parity.")
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--instrument", default="EUR_USD")
    ap.add_argument("--from", dest="from_date", default="2020-01-01")
    ap.add_argument("--to", dest="to_date", default="2026-05-20")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()

    db_path = Path(args.db)
    try:
        db_display = str(db_path.resolve().relative_to(ROOT))
    except ValueError:
        db_display = str(db_path)
    if not db_path.exists():
        print(
            f"ERROR: no OANDA H4 candle store at {db_display}.\n"
            "This script exports REAL stored candles only — it never "
            "fabricates data. Fetch real OANDA practice candles first "
            "(see docs/research/LEAN_PARITY_EXECUTION_GUIDE.md), then re-run.",
            file=sys.stderr,
        )
        return 2

    db = Database(db_path)
    repo = CandleRepo(db)
    from_dt = datetime.fromisoformat(args.from_date).replace(tzinfo=UTC)
    to_dt = datetime.fromisoformat(args.to_date).replace(tzinfo=UTC)
    candles = repo.list(
        args.instrument, "H4", completed_only=True, from_time=from_dt, to_time=to_dt
    )
    if not candles:
        print(
            f"ERROR: no completed H4 candles for {args.instrument} in "
            f"{args.from_date}..{args.to_date}.",
            file=sys.stderr,
        )
        return 1

    sources = distinct_sources(db, args.instrument)
    if not sources_are_real_oanda(sources):
        print(
            f"ERROR: refusing to export — {args.instrument} H4 candle "
            f"source(s) {sources} are not real OANDA data. A parity export "
            "must use real OANDA candles only.",
            file=sys.stderr,
        )
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_name = f"{args.instrument}_H4_lean.csv"
    csv_path = out_dir / csv_name
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(LEAN_CSV_HEADER)
        for c in candles:
            writer.writerow(candle_to_lean_row(c))

    provenance = build_provenance(
        instrument=args.instrument,
        candles=list(candles),
        source=sources[0],
        from_arg=args.from_date,
        to_arg=args.to_date,
        csv_name=csv_name,
    )
    prov_path = out_dir / f"{args.instrument}_H4_lean.provenance.json"
    prov_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    print(f"exported {len(candles)} H4 candles → {csv_path}")
    print(f"  data_sha256: {provenance['data_sha256']}")
    print(f"  campaign_002_data_request_hash: {provenance['campaign_002_data_request_hash']}")
    print(f"  provenance → {prov_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
