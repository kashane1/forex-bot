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
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.postgres_candle_store import CandleRecord, PostgresCandleStore
from forex_bot.data.research_db import (
    ResearchDatabaseBlocked,
    ResearchDatabaseUnsafe,
    get_research_database_config,
)
from forex_bot.domain.cross_instruments import (
    NONUSD_CROSS_PAIRS,
    PRIMARY_CROSS_PAIRS,
)
from forex_bot.logging_config import _scrub_value
from forex_bot.project_env import bootstrap_environ

PRACTICE_HOST = "api-fxpractice.oanda.com"
LIVE_HOST = "api-fxtrade.oanda.com"
MAX_OANDA_CANDLES = 5000
MAX_DAYS_WITHOUT_CHUNK_LIMIT = 7
DEFAULT_CHUNK_MINUTES = 24 * 60
MAJOR_FOREX_PAIRS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)
# Non-USD crosses are additive (first multi-market expansion). The majors
# remain the control universe; the allowlist is widened to the union so the
# same practice-only, candle-endpoint-only ingestion path serves crosses.
ALLOWED_INSTRUMENTS = set(MAJOR_FOREX_PAIRS) | set(NONUSD_CROSS_PAIRS)
_INSTRUMENT_RE = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")


def parse_utc_date(value: str) -> datetime:
    if "T" not in value:
        value = f"{value}T00:00:00Z"
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def validate_instrument(instrument: str) -> str:
    if not _INSTRUMENT_RE.match(instrument) or instrument not in ALLOWED_INSTRUMENTS:
        raise ValueError(f"instrument not allowlisted: {instrument}")
    return instrument


def resolve_instruments(args: argparse.Namespace) -> list[str]:
    if args.majors:
        return list(MAJOR_FOREX_PAIRS)
    if getattr(args, "crosses", False):
        return list(PRIMARY_CROSS_PAIRS)
    if getattr(args, "all_crosses", False):
        return list(NONUSD_CROSS_PAIRS)
    if args.instruments:
        return [validate_instrument(item) for item in args.instruments]
    if args.instrument:
        return [validate_instrument(args.instrument)]
    raise ValueError(
        "one of --instrument, --instruments, --majors, --crosses, or --all-crosses is required"
    )


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


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    reraise=True,
)
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
        timeout=60.0,
    )
    response.raise_for_status()
    return parse_oanda_m1_payload(response.json(), instrument=instrument, fetch_batch_id=fetch_batch_id)


def _log_progress(message: str, *, quiet: bool) -> None:
    if not quiet:
        print(message, file=sys.stderr, flush=True)


def run_one_instrument(
    args: argparse.Namespace,
    instrument: str,
    *,
    environ: dict[str, str] | None = None,
) -> dict[str, Any]:
    if args.granularity != "M1":
        raise ValueError("this script only supports --granularity M1")
    start = parse_utc_date(args.start)
    end = parse_utc_date(args.end)
    chunks = build_chunks(start, end)
    if len(chunks) > MAX_DAYS_WITHOUT_CHUNK_LIMIT and args.max_chunks is None and not args.allow_large_range:
        raise ValueError("BLOCKED_DATE_RANGE: large M1 range requires --max-chunks or --allow-large-range")
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
        for index, (chunk_start, chunk_end) in enumerate(selected_chunks, start=1):
            _log_progress(
                f"[{instrument}] chunk {index}/{len(selected_chunks)} "
                f"{chunk_start.isoformat()} -> {chunk_end.isoformat()}",
                quiet=args.quiet,
            )
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


def run(args: argparse.Namespace, *, environ: dict[str, str] | None = None) -> dict[str, Any]:
    instruments = resolve_instruments(args)
    if len(instruments) == 1:
        return run_one_instrument(args, instruments[0], environ=environ)
    results = [
        run_one_instrument(args, instrument, environ=environ)
        for instrument in instruments
    ]
    statuses = {item.get("status") for item in results}
    status = statuses.pop() if len(statuses) == 1 else "MIXED"
    return {
        "status": status,
        "instruments": instruments,
        "start_utc": results[0]["start_utc"],
        "end_utc": results[0]["end_utc"],
        "network_called": any(item.get("network_called") for item in results),
        "candles_written": sum(int(item.get("candles_written", 0)) for item in results),
        "results": results,
    }


def _float_or_none(value: str | None) -> float | None:
    return None if value is None else float(value)


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Practice-only read-only OANDA M1 candle ingestion.")
    parser.add_argument("--instrument", help="Single allowlisted instrument")
    parser.add_argument(
        "--instruments",
        nargs="+",
        help="One or more allowlisted instruments (see --majors for the default major set)",
    )
    parser.add_argument(
        "--majors",
        action="store_true",
        help=f"Ingest all major pairs: {', '.join(MAJOR_FOREX_PAIRS)}",
    )
    parser.add_argument(
        "--crosses",
        action="store_true",
        help=f"Ingest the primary wave-1 non-USD crosses: {', '.join(PRIMARY_CROSS_PAIRS)}",
    )
    parser.add_argument(
        "--all-crosses",
        action="store_true",
        help=f"Ingest all registered non-USD crosses: {', '.join(NONUSD_CROSS_PAIRS)}",
    )
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--granularity", default="M1")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute-readonly-ingestion", action="store_true")
    parser.add_argument(
        "--allow-large-range",
        action="store_true",
        help="Allow multi-day ingestion without --max-chunks (required for multi-year backfills)",
    )
    parser.add_argument("--max-chunks", type=int)
    parser.add_argument("--store-uri")
    parser.add_argument("--manifest-out")
    parser.add_argument("--quiet", action="store_true", help="Suppress stderr progress lines")
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
