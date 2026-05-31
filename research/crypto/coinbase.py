"""Coinbase Exchange public REST candle parsing and fetch helpers."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from forex_bot.data.postgres_candle_store import CandleRecord

from research.crypto.registry import half_spread_bps, validate_instrument, venue_symbol

COINBASE_API_BASE = "https://api.exchange.coinbase.com"
GRANULARITY_SECONDS = {"M1": 60}
MAX_CANDLES_PER_REQUEST = 300
REQUEST_DELAY_SECONDS = 0.1


def _f(value: float) -> float:
    return float(value)


def _mid_with_spread(mid: float, *, instrument: str, side: str) -> float:
    bps = half_spread_bps(instrument)
    delta = mid * (bps / 10_000.0)
    return mid - delta if side == "bid" else mid + delta


def parse_coinbase_candles(
    payload: list[list[float | int]],
    *,
    instrument: str,
    granularity: str,
) -> list[CandleRecord]:
    """Parse Coinbase candle arrays: [time, low, high, open, close, volume]."""
    validate_instrument(instrument)
    out: list[CandleRecord] = []
    for row in payload:
        if len(row) < 6:
            continue
        ts = datetime.fromtimestamp(int(row[0]), tz=UTC)
        low, high, open_, close = _f(row[1]), _f(row[2]), _f(row[3]), _f(row[4])
        volume = int(float(row[5]))
        record = CandleRecord(
            instrument=instrument,
            granularity=granularity,
            time_utc=ts,
            complete=True,
            volume=volume,
            mid_o=open_,
            mid_h=high,
            mid_l=low,
            mid_c=close,
            bid_o=_mid_with_spread(open_, instrument=instrument, side="bid"),
            bid_h=_mid_with_spread(high, instrument=instrument, side="bid"),
            bid_l=_mid_with_spread(low, instrument=instrument, side="bid"),
            bid_c=_mid_with_spread(close, instrument=instrument, side="bid"),
            ask_o=_mid_with_spread(open_, instrument=instrument, side="ask"),
            ask_h=_mid_with_spread(high, instrument=instrument, side="ask"),
            ask_l=_mid_with_spread(low, instrument=instrument, side="ask"),
            ask_c=_mid_with_spread(close, instrument=instrument, side="ask"),
        )
        out.append(record)
    out.sort(key=lambda candle: candle.time_utc)
    return out


def _fmt_dt(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(httpx.HTTPError),
)
def fetch_coinbase_candles_page(
    client: httpx.Client,
    *,
    product_id: str,
    start: datetime,
    end: datetime,
    granularity: str = "M1",
) -> list[list[float | int]]:
    gran_sec = GRANULARITY_SECONDS[granularity]
    response = client.get(
        f"{COINBASE_API_BASE}/products/{product_id}/candles",
        params={
            "granularity": gran_sec,
            "start": _fmt_dt(start),
            "end": _fmt_dt(end),
        },
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(f"unexpected Coinbase payload shape: {type(payload)!r}")
    return payload


def iter_coinbase_chunks(
    start: datetime,
    end: datetime,
    *,
    granularity: str = "M1",
    max_candles: int = MAX_CANDLES_PER_REQUEST,
) -> list[tuple[datetime, datetime]]:
    if start > end:
        raise ValueError("start must be <= end")
    step = timedelta(seconds=GRANULARITY_SECONDS[granularity] * max_candles)
    chunks: list[tuple[datetime, datetime]] = []
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + step - timedelta(seconds=GRANULARITY_SECONDS[granularity]), end)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end + timedelta(seconds=GRANULARITY_SECONDS[granularity])
    return chunks


def fetch_coinbase_candles(
    client: httpx.Client,
    *,
    instrument: str,
    start: datetime,
    end: datetime,
    granularity: str = "M1",
) -> list[CandleRecord]:
    product_id = venue_symbol(instrument)
    seen: set[datetime] = set()
    rows: list[CandleRecord] = []
    for chunk_start, chunk_end in iter_coinbase_chunks(start, end, granularity=granularity):
        page = fetch_coinbase_candles_page(
            client,
            product_id=product_id,
            start=chunk_start,
            end=chunk_end,
            granularity=granularity,
        )
        for candle in parse_coinbase_candles(
            page, instrument=instrument, granularity=granularity
        ):
            if chunk_start <= candle.time_utc <= end and candle.time_utc not in seen:
                seen.add(candle.time_utc)
                rows.append(candle)
        time.sleep(REQUEST_DELAY_SECONDS)
    rows.sort(key=lambda candle: candle.time_utc)
    return rows


def write_batch_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
