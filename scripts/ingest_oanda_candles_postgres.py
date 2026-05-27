#!/usr/bin/env python3
"""Read-only OANDA practice candle ingestion into local Postgres."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
from forex_bot.logging_config import _scrub_value
from forex_bot.project_env import bootstrap_environ

DEFAULT_INSTRUMENTS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)
DEFAULT_GRANULARITY = "H4"
_INSTRUMENT_RE = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")
_MAX_OANDA_COUNT = 5000


def _blocked_payload(message: str) -> dict[str, Any]:
    return {"status": "BLOCKED", "message": message}


def require_practice_oanda_env(environ: dict[str, str] | None = None) -> tuple[str, str]:
    env = environ if environ is not None else os.environ
    if env.get("OANDA_ENVIRONMENT", "practice").strip().lower() == "live":
        raise RuntimeError("Refusing live OANDA environment for historical ingestion.")
    account_id = env.get("OANDA_ACCOUNT_ID_PRACTICE", "").strip()
    token = env.get("OANDA_ACCESS_TOKEN_PRACTICE", "").strip()
    if not account_id or not token:
        raise ResearchDatabaseBlocked("OANDA practice credentials are absent; ingestion is BLOCKED.")
    return account_id, token


def validate_instruments(instruments: list[str]) -> list[str]:
    out: list[str] = []
    for instrument in instruments:
        if not _INSTRUMENT_RE.match(instrument):
            raise ValueError(f"Invalid OANDA instrument: {instrument}")
        out.append(instrument)
    return out


def _f(value: str | None) -> float | None:
    return None if value is None else float(value)


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _fmt_dt(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_oanda_candles(payload: dict[str, Any], *, instrument: str, granularity: str) -> list[CandleRecord]:
    out: list[CandleRecord] = []
    for row in payload.get("candles", []):
        complete = bool(row.get("complete", False))
        if not complete:
            continue
        bid = row.get("bid") or {}
        ask = row.get("ask") or {}
        mid = row.get("mid") or {}
        candle = CandleRecord(
            instrument=instrument,
            granularity=granularity,
            time_utc=datetime.fromisoformat(row["time"].replace("Z", "+00:00")),
            complete=complete,
            volume=int(row.get("volume", 0)),
            bid_o=_f(bid.get("o")),
            bid_h=_f(bid.get("h")),
            bid_l=_f(bid.get("l")),
            bid_c=_f(bid.get("c")),
            ask_o=_f(ask.get("o")),
            ask_h=_f(ask.get("h")),
            ask_l=_f(ask.get("l")),
            ask_c=_f(ask.get("c")),
            mid_o=_f(mid.get("o")),
            mid_h=_f(mid.get("h")),
            mid_l=_f(mid.get("l")),
            mid_c=_f(mid.get("c")),
        )
        out.append(candle)
    return out


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(httpx.HTTPError),
)
def fetch_oanda_candles_page(
    client: httpx.Client,
    *,
    token: str,
    instrument: str,
    granularity: str,
    start: str,
    count: int = _MAX_OANDA_COUNT,
) -> list[CandleRecord]:
    url = f"https://api-fxpractice.oanda.com/v3/instruments/{instrument}/candles"
    response = client.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "price": "BAM",
            "granularity": granularity,
            "from": start,
            "count": count,
            "includeFirst": "true",
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return parse_oanda_candles(response.json(), instrument=instrument, granularity=granularity)


def fetch_oanda_candles(
    client: httpx.Client,
    *,
    token: str,
    instrument: str,
    granularity: str,
    start: str,
    end: str,
) -> list[CandleRecord]:
    requested_end = _parse_dt(end)
    cursor = _parse_dt(start)
    all_rows: list[CandleRecord] = []
    seen: set[tuple[str, str, datetime]] = set()
    while cursor <= requested_end:
        page = fetch_oanda_candles_page(
            client,
            token=token,
            instrument=instrument,
            granularity=granularity,
            start=_fmt_dt(cursor),
            count=_MAX_OANDA_COUNT,
        )
        if not page:
            break
        page_in_window = [row for row in page if row.time_utc <= requested_end]
        for row in page_in_window:
            key = (row.instrument, row.granularity, row.time_utc)
            if key not in seen:
                seen.add(key)
                all_rows.append(row)
        last_time = page[-1].time_utc
        if last_time <= cursor or last_time >= requested_end:
            break
        cursor = last_time
    all_rows.sort(key=lambda row: row.time_utc)
    return all_rows


def run_ingestion(args: argparse.Namespace, *, environ: dict[str, str] | None = None) -> dict[str, Any]:
    cfg = get_research_database_config(environ=environ, require=True)
    account_id, token = require_practice_oanda_env(environ=environ)
    instruments = validate_instruments(args.instruments or list(DEFAULT_INSTRUMENTS))
    store = PostgresCandleStore(cfg)
    store.ensure_schema()
    run_id = str(uuid.uuid4())
    started_at = datetime.now(UTC)
    inserted = 0
    status = "PASS"
    error: str | None = None
    try:
        with httpx.Client() as client:
            for instrument in instruments:
                candles = fetch_oanda_candles(
                    client,
                    token=token,
                    instrument=instrument,
                    granularity=args.granularity,
                    start=args.start,
                    end=args.end,
                )
                inserted += store.upsert_candles(
                    candles,
                    source="oanda-practice",
                    fetched_at_utc=datetime.now(UTC),
                )
    except Exception as exc:
        status = "FAIL"
        error = _scrub_value(str(exc))
        raise
    finally:
        store.record_ingestion_run(
            run_id=run_id,
            started_at_utc=started_at,
            finished_at_utc=datetime.now(UTC),
            source="oanda-practice",
            instruments_json=json.dumps(instruments),
            granularity=args.granularity,
            start_utc=datetime.fromisoformat(args.start.replace("Z", "+00:00")),
            end_utc=datetime.fromisoformat(args.end.replace("Z", "+00:00")),
            status=status,
            candles_inserted=inserted,
            candles_updated=0,
            error=error,
        )
    return {
        "status": status,
        "run_id": run_id,
        "database_name": cfg.database_name,
        "schema_name": cfg.schema,
        "database_url_redacted": cfg.redacted_url,
        "granularity": args.granularity,
        "instruments": instruments,
        "start_utc": args.start,
        "end_utc": args.end,
        "candles_inserted": inserted,
        "account_id_redacted": _scrub_value(account_id),
    }


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Ingest OANDA practice candles into local Postgres.")
    parser.add_argument("--granularity", default=DEFAULT_GRANULARITY)
    parser.add_argument("--start", required=False, default="2020-01-01T00:00:00Z")
    parser.add_argument("--end", required=False, default=datetime.now(UTC).isoformat().replace("+00:00", "Z"))
    parser.add_argument("--instruments", nargs="*", default=list(DEFAULT_INSTRUMENTS))
    parser.add_argument("--incremental", action="store_true")
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
