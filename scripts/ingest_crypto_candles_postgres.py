#!/usr/bin/env python3
"""Coinbase spot candle ingestion into local Postgres (BTC/USD, ETH/USD)."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import (
    ResearchDatabaseBlocked,
    ResearchDatabaseUnsafe,
    get_research_database_config,
)
from forex_bot.logging_config import _scrub_value
from forex_bot.project_env import bootstrap_environ
from research.crypto.coinbase import fetch_coinbase_candles, write_batch_manifest
from research.crypto.registry import CANONICAL_INSTRUMENTS, CRYPTO_SOURCE, validate_instrument


def _blocked_payload(message: str) -> dict[str, Any]:
    return {"status": "BLOCKED", "message": message}


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def run_ingestion(args: argparse.Namespace, *, environ: dict[str, str] | None = None) -> dict[str, Any]:
    cfg = get_research_database_config(environ=environ, require=True)
    instrument = validate_instrument(args.instrument)
    if args.granularity != "M1":
        raise ValueError("only --granularity M1 is supported in v1")
    start = _parse_dt(args.start)
    end = _parse_dt(args.end)
    store = PostgresCandleStore(cfg)
    store.ensure_schema()
    batch_id = str(uuid.uuid4())
    started_at = datetime.now(UTC)
    manifest_path = ROOT / "research" / "crypto" / "manifests" / f"{batch_id}.json"
    inserted = 0
    status = "PASS"
    error: str | None = None
    candle_count = 0
    try:
        with httpx.Client() as client:
            candles = fetch_coinbase_candles(
                client,
                instrument=instrument,
                start=start,
                end=end,
                granularity=args.granularity,
            )
        candle_count = len(candles)
        candles = [replace(candle, fetch_batch_id=batch_id) for candle in candles]
        inserted = store.upsert_candles(
            candles,
            source=CRYPTO_SOURCE,
            fetched_at_utc=datetime.now(UTC),
        )
    except Exception as exc:
        status = "FAIL"
        error = _scrub_value(str(exc))
        raise
    finally:
        payload = {
            "batch_id": batch_id,
            "status": status,
            "instrument": instrument,
            "granularity": args.granularity,
            "source": CRYPTO_SOURCE,
            "start_utc": start.isoformat(),
            "end_utc": end.isoformat(),
            "started_at_utc": started_at.isoformat(),
            "finished_at_utc": datetime.now(UTC).isoformat(),
            "candles_fetched": candle_count,
            "candles_upserted": inserted,
            "error": error,
        }
        write_batch_manifest(manifest_path, payload)
        store.record_ingestion_run(
            run_id=batch_id,
            started_at_utc=started_at,
            finished_at_utc=datetime.now(UTC),
            source=CRYPTO_SOURCE,
            instruments_json=json.dumps([instrument]),
            granularity=args.granularity,
            start_utc=start,
            end_utc=end,
            status=status,
            candles_inserted=inserted,
            candles_updated=0,
            error=error,
        )
    return {
        "status": status,
        "batch_id": batch_id,
        "manifest_path": str(manifest_path.relative_to(ROOT)),
        "instrument": instrument,
        "granularity": args.granularity,
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "candles_fetched": candle_count,
        "candles_upserted": inserted,
    }


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Ingest Coinbase spot candles into Postgres.")
    parser.add_argument("--instrument", required=True, choices=list(CANONICAL_INSTRUMENTS))
    parser.add_argument("--granularity", default="M1")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args(argv)
    try:
        payload = run_ingestion(args, environ=environ)
    except ResearchDatabaseBlocked as exc:
        payload = _blocked_payload(str(exc))
        print(json.dumps(payload, indent=2))
        return 2
    except ResearchDatabaseUnsafe as exc:
        print(json.dumps({"status": "FAIL", "message": str(exc)}, indent=2))
        return 1
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "message": _scrub_value(str(exc))}, indent=2))
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
