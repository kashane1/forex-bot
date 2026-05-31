#!/usr/bin/env python3
"""Validate canonical crypto candle series in local Postgres."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import ResearchDatabaseBlocked, get_research_database_config
from forex_bot.project_env import bootstrap_environ
from research.crypto.registry import CANONICAL_INSTRUMENTS, validate_instrument
from research.crypto.validation import validate_crypto_series


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def run_validation(args: argparse.Namespace, *, environ: dict[str, str] | None = None) -> dict[str, Any]:
    cfg = get_research_database_config(environ=environ, require=True)
    instrument = validate_instrument(args.instrument)
    store = PostgresCandleStore(cfg)
    result = validate_crypto_series(
        store,
        instrument=instrument,
        granularity=args.granularity,
        start_utc=_parse_dt(args.start),
        end_utc=_parse_dt(args.end),
        min_coverage=args.min_coverage,
    )
    return result.to_dict()


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Validate crypto candles in Postgres.")
    parser.add_argument("--instrument", required=True, choices=list(CANONICAL_INSTRUMENTS))
    parser.add_argument("--granularity", default="M1")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--min-coverage", type=float, default=0.995)
    args = parser.parse_args(argv)
    try:
        payload = run_validation(args, environ=environ)
    except ResearchDatabaseBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "message": str(exc)}, indent=2))
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
