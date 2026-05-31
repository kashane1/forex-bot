#!/usr/bin/env python3
"""Materialize crypto M1 candles into derived timeframes (UTC-aligned)."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from forex_bot.data.crypto_pairs import CRYPTO_INSTRUMENTS, CRYPTO_MATERIALIZED_FROM_M1
from forex_bot.data.m1_timeframe_materialization import materialize_pair
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import ResearchDatabaseBlocked, get_research_database_config
from forex_bot.project_env import bootstrap_environ
from research.crypto.coinbase import write_batch_manifest
from research.crypto.registry import validate_instrument


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def run_materialization(args: argparse.Namespace, *, environ: dict[str, str] | None = None) -> dict[str, Any]:
    cfg = get_research_database_config(environ=environ, require=True)
    instrument = validate_instrument(args.instrument)
    targets = tuple(t.strip() for t in args.targets.split(",") if t.strip())
    for target in targets:
        if target not in CRYPTO_MATERIALIZED_FROM_M1:
            raise ValueError(f"unsupported target granularity: {target}")
    store = PostgresCandleStore(cfg)
    store.ensure_schema()
    run_id = str(uuid.uuid4())
    result = materialize_pair(
        store,
        instrument,
        from_utc=_parse_dt(args.start),
        to_utc=_parse_dt(args.end),
        targets=targets,
        dry_run=args.dry_run,
        run_id=run_id,
        alignment_tz="UTC",
        alignment_hour=0,
        allowed_instruments=CRYPTO_INSTRUMENTS,
    )
    manifest = {
        "run_id": run_id,
        "instrument": instrument,
        "from_utc": result.from_utc.isoformat(),
        "to_utc": result.to_utc.isoformat(),
        "dry_run": result.dry_run,
        "m1_rows_read": result.m1_rows_read,
        "targets": {
            target: {
                "rows_upserted": stats.rows_upserted,
                "first_utc": stats.first_utc.isoformat() if stats.first_utc else None,
                "last_utc": stats.last_utc.isoformat() if stats.last_utc else None,
            }
            for target, stats in result.targets.items()
        },
    }
    if not args.dry_run:
        path = ROOT / "research" / "crypto" / "materialization" / f"{run_id}.json"
        write_batch_manifest(path, manifest)
        manifest["manifest_path"] = str(path.relative_to(ROOT))
    return manifest


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Materialize crypto derived timeframes from M1.")
    parser.add_argument("--instrument", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--targets", default=",".join(CRYPTO_MATERIALIZED_FROM_M1))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        payload = run_materialization(args, environ=environ)
    except ResearchDatabaseBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "message": str(exc)}, indent=2))
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
