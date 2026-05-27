#!/usr/bin/env python3
"""Export Postgres research candles to CSV and optional SQLite compatibility."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.postgres_candle_store import PostgresCandleStore, common_timestamp_intersection
from forex_bot.data.research_db import (
    ResearchDatabaseBlocked,
    ResearchDatabaseUnsafe,
    get_research_database_config,
)
from forex_bot.project_env import bootstrap_environ

CSV_HEADER = [
    "time",
    "bid_open",
    "bid_high",
    "bid_low",
    "bid_close",
    "ask_open",
    "ask_high",
    "ask_low",
    "ask_close",
    "volume",
]

DEFAULT_INSTRUMENTS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)


def rows_to_csv_rows(rows: list[dict[str, Any]]) -> list[list[str]]:
    return [
        [
            row["time_utc"].isoformat(),
            str(row["bid_o"]),
            str(row["bid_h"]),
            str(row["bid_l"]),
            str(row["bid_c"]),
            str(row["ask_o"]),
            str(row["ask_h"]),
            str(row["ask_l"]),
            str(row["ask_c"]),
            str(row["volume"]),
        ]
        for row in rows
    ]


def hash_csv_rows(rows: list[list[str]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update("|".join(row).encode("utf-8"))
    return digest.hexdigest()


def write_compat_sqlite(path: Path, rows_by_instrument: dict[str, list[dict[str, Any]]], *, granularity: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS candles (
              instrument TEXT NOT NULL,
              granularity TEXT NOT NULL,
              time TEXT NOT NULL,
              complete INTEGER NOT NULL,
              volume INTEGER,
              price_components TEXT NOT NULL,
              bid_o TEXT,
              bid_h TEXT,
              bid_l TEXT,
              bid_c TEXT,
              ask_o TEXT,
              ask_h TEXT,
              ask_l TEXT,
              ask_c TEXT,
              mid_o TEXT,
              mid_h TEXT,
              mid_l TEXT,
              mid_c TEXT,
              source TEXT,
              request_hash TEXT,
              PRIMARY KEY (instrument, granularity, time, price_components)
            )
            """
        )
        for instrument, rows in rows_by_instrument.items():
            for row in rows:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO candles (
                      instrument, granularity, time, complete, volume, price_components,
                      bid_o, bid_h, bid_l, bid_c,
                      ask_o, ask_h, ask_l, ask_c,
                      mid_o, mid_h, mid_l, mid_c,
                      source, request_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        instrument,
                        granularity,
                        row["time_utc"].isoformat(),
                        1 if row["complete"] else 0,
                        row["volume"],
                        "BA",
                        row["bid_o"],
                        row["bid_h"],
                        row["bid_l"],
                        row["bid_c"],
                        row["ask_o"],
                        row["ask_h"],
                        row["ask_l"],
                        row["ask_c"],
                        row["mid_o"],
                        row["mid_h"],
                        row["mid_l"],
                        row["mid_c"],
                        row.get("source", "oanda-practice"),
                        None,
                    ),
                )
        conn.commit()
    finally:
        conn.close()


def build_manifest(
    rows_by_instrument: dict[str, list[dict[str, Any]]],
    *,
    granularity: str,
    database_name: str,
    schema_name: str,
) -> dict[str, Any]:
    files: dict[str, Any] = {}
    for instrument, rows in rows_by_instrument.items():
        csv_rows = rows_to_csv_rows(rows)
        if not csv_rows:
            raise ValueError(f"Missing pair for export: {instrument}")
        files[instrument] = {
            "row_count": len(csv_rows),
            "first_utc": rows[0]["time_utc"].isoformat(),
            "last_utc": rows[-1]["time_utc"].isoformat(),
            "sha256": hash_csv_rows(csv_rows),
        }
    intersection = common_timestamp_intersection(rows_by_instrument)
    return {
        "status": "PASS",
        "granularity": granularity,
        "database_name": database_name,
        "schema_name": schema_name,
        "extracted_at_utc": datetime.now(UTC).isoformat(),
        "common_timestamp_intersection": {
            "count": intersection["count"],
            "start_utc": intersection["start_utc"].isoformat() if intersection["start_utc"] else None,
            "end_utc": intersection["end_utc"].isoformat() if intersection["end_utc"] else None,
        },
        "files": files,
    }


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Export research candles from Postgres.")
    parser.add_argument("--granularity", default="H4")
    parser.add_argument("--out", default="research/lean_parity/exports/campaign_002_h4")
    parser.add_argument("--sqlite-out")
    args = parser.parse_args(argv)
    try:
        cfg = get_research_database_config(environ=environ, require=True)
    except ResearchDatabaseBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "message": str(exc)}, indent=2))
        return 2
    except ResearchDatabaseUnsafe as exc:
        print(json.dumps({"status": "FAIL", "message": str(exc)}, indent=2))
        return 1
    store = PostgresCandleStore(cfg)
    rows_by_instrument: dict[str, list[dict[str, Any]]] = {
        instrument: store.query_candles(instrument=instrument, granularity=args.granularity)
        for instrument in DEFAULT_INSTRUMENTS
    }
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(
        rows_by_instrument,
        granularity=args.granularity,
        database_name=cfg.database_name,
        schema_name=cfg.schema,
    )
    for instrument, rows in rows_by_instrument.items():
        csv_path = out_dir / f"{instrument}_{args.granularity}_lean.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(CSV_HEADER)
            writer.writerows(rows_to_csv_rows(rows))
    (out_dir / "EXPORT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    if args.sqlite_out:
        write_compat_sqlite(Path(args.sqlite_out), rows_by_instrument, granularity=args.granularity)
    print(json.dumps(manifest, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
