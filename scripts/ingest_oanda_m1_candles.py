#!/usr/bin/env python3
"""Practice-only read-only OANDA M1 candle ingestion scaffold."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.postgres_candle_store import CandleRecord, PostgresCandleStore
from forex_bot.data.research_db import (
    ResearchDatabaseBlocked,
    ResearchDatabaseUnsafe,
    get_research_database_config,
)
from forex_bot.logging_config import _scrub_value

PRACTICE_HOST = "api-fxpractice.oanda.com"
LIVE_HOST = "api-fxtrade.oanda.com"
MAX_OANDA_CANDLES = 5000
MAX_DAYS_WITHOUT_CHUNK_LIMIT = 7
DEFAULT_CHUNK_MINUTES = 24 * 60
ALLOWED_INSTRUMENTS = {
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
}
_INSTRUMENT_RE = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")


def parse_utc_date(value: str) -> datetime:
    if "T" not in value:
        value = f"{value}T00:00:00Z"
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def validate_instrument(instrument: str) -> str:
    if not _INSTRUMENT_RE.match(instrument) or instrument not in ALLOWED_INSTRUMENTS:
        raise ValueError(f"instrument not allowlisted: {instrument}")
    return instrument


def validate_endpoint_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.netloc == LIVE_HOST:
        raise RuntimeError("refusing live OANDA host")
    if parsed.netloc != PRACTICE_HOST:
        raise RuntimeError("refusing non-practice OANDA host")
    path = parsed.path
    forbidden = ("/orders", "/trades", "/positions", "/transactions")
    if any(fragment in path for fragment in forbidden):
        raise RuntimeError("refusing OANDA mutation or account endpoint")
    if not re.fullmatch(r"/v3/instruments/[A-Z]{3}_[A-Z]{3}/candles", path):
        raise RuntimeError("refusing non-candle endpoint")


def candle_url(instrument: str) -> str:
    return f"https://{PRACTICE_HOST}/v3/instruments/{validate_instrument(instrument)}/candles"


def require_practice_credentials(environ: dict[str, str] | None = None) -> str:
    env = environ if environ is not None else os.environ
    if env.get("OANDA_ENVIRONMENT", "practice").strip().lower() == "live":
        raise RuntimeError("refusing live OANDA environment")
    token = env.get("OANDA_ACCESS_TOKEN_PRACTICE", "").strip()
    if not token:
        raise ResearchDatabaseBlocked("BLOCKED_READONLY_CREDENTIALS")
    return token


def build_chunks(start: datetime, end: datetime, *, chunk_minutes: int = DEFAULT_CHUNK_MINUTES) -> list[tuple[datetime, datetime]]:
    if end <= start:
        raise ValueError("end must be after start")
    chunks: list[tuple[datetime, datetime]] = []
    cursor = start
    step = timedelta(minutes=chunk_minutes)
    while cursor < end:
        chunk_end = min(cursor + step, end)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end
    return chunks


def parse_oanda_m1_payload(
    payload: dict[str, Any],
    *,
    instrument: str,
    fetch_batch_id: str,
) -> list[CandleRecord]:
    rows: list[CandleRecord] = []
    for item in payload.get("candles", []):
        bid = item.get("bid") or {}
        ask = item.get("ask") or {}
        mid = item.get("mid") or {}
        rows.append(
            CandleRecord(
                instrument=instrument,
                granularity="M1",
                time_utc=parse_utc_date(item["time"]),
                complete=bool(item.get("complete", False)),
                volume=int(item.get("volume", 0)),
                bid_o=_float_or_none(bid.get("o")),
                bid_h=_float_or_none(bid.get("h")),
                bid_l=_float_or_none(bid.get("l")),
                bid_c=_float_or_none(bid.get("c")),
                ask_o=_float_or_none(ask.get("o")),
                ask_h=_float_or_none(ask.get("h")),
                ask_l=_float_or_none(ask.get("l")),
                ask_c=_float_or_none(ask.get("c")),
                mid_o=_float_or_none(mid.get("o")),
                mid_h=_float_or_none(mid.get("h")),
                mid_l=_float_or_none(mid.get("l")),
                mid_c=_float_or_none(mid.get("c")),
                fetch_batch_id=fetch_batch_id,
            )
        )
    return rows


def fetch_chunk(
    client: httpx.Client,
    *,
    token: str,
    instrument: str,
    start: datetime,
    end: datetime,
    fetch_batch_id: str,
) -> list[CandleRecord]:
    url = candle_url(instrument)
    validate_endpoint_url(url)
    response = client.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "price": "BAM",
            "granularity": "M1",
            "from": start.isoformat().replace("+00:00", "Z"),
            "to": end.isoformat().replace("+00:00", "Z"),
            "includeFirst": "true",
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return parse_oanda_m1_payload(response.json(), instrument=instrument, fetch_batch_id=fetch_batch_id)


def run(args: argparse.Namespace, *, environ: dict[str, str] | None = None) -> dict[str, Any]:
    instrument = validate_instrument(args.instrument)
    if args.granularity != "M1":
        raise ValueError("this script only supports --granularity M1")
    start = parse_utc_date(args.start)
    end = parse_utc_date(args.end)
    chunks = build_chunks(start, end)
    if len(chunks) > MAX_DAYS_WITHOUT_CHUNK_LIMIT and args.max_chunks is None:
        raise ValueError("BLOCKED_DATE_RANGE: large M1 range requires --max-chunks")
    selected_chunks = chunks[: args.max_chunks] if args.max_chunks else chunks
    manifest: dict[str, Any] = {
        "status": "DRY_RUN" if args.dry_run or not args.execute_readonly_ingestion else "PASS",
        "instrument": instrument,
        "granularity": "M1",
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "chunk_count": len(selected_chunks),
        "network_called": False,
        "candles_written": 0,
        "raw_payload_committed": False,
    }
    if args.dry_run or not args.execute_readonly_ingestion:
        return manifest

    token = require_practice_credentials(environ)
    cfg = get_research_database_config(environ=environ, require=True)
    store = PostgresCandleStore(cfg)
    store.ensure_schema()
    fetch_batch_id = str(uuid.uuid4())
    written = 0
    with httpx.Client() as client:
        for chunk_start, chunk_end in selected_chunks:
            rows = fetch_chunk(
                client,
                token=token,
                instrument=instrument,
                start=chunk_start,
                end=chunk_end,
                fetch_batch_id=fetch_batch_id,
            )
            written += store.upsert_candles(rows, source="oanda-practice-m1")
    manifest.update(
        {
            "status": "PASS",
            "network_called": True,
            "candles_written": written,
            "fetch_batch_id": fetch_batch_id,
            "store": cfg.redacted_url,
        }
    )
    return manifest


def _float_or_none(value: str | None) -> float | None:
    return None if value is None else float(value)


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Practice-only read-only OANDA M1 candle ingestion.")
    parser.add_argument("--instrument", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--granularity", default="M1")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute-readonly-ingestion", action="store_true")
    parser.add_argument("--max-chunks", type=int)
    parser.add_argument("--store-uri")
    parser.add_argument("--manifest-out")
    args = parser.parse_args(argv)
    try:
        payload = run(args, environ=environ)
    except ResearchDatabaseBlocked as exc:
        payload = {"status": str(exc)}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2
    except (ResearchDatabaseUnsafe, RuntimeError, ValueError) as exc:
        payload = {"status": "BLOCKED", "message": _scrub_value(str(exc))}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.manifest_out:
        Path(args.manifest_out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
