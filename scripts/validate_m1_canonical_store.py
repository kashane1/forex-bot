#!/usr/bin/env python3
"""Validate canonical M1 rows and locally generated aggregates."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.postgres_candle_store import PostgresCandleStore, compute_candle_data_hash
from forex_bot.data.research_db import get_research_database_config
from forex_bot.data.timeframe_aggregation import aggregate_m1_candles
from forex_bot.domain.candles import Candle
from forex_bot.project_env import bootstrap_environ


def parse_utc(value: str) -> datetime:
    if "T" not in value:
        value = f"{value}T00:00:00Z"
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def analyze_rows(
    rows: list[dict[str, Any]],
    *,
    instrument: str,
    start_utc: datetime,
    end_utc: datetime,
    extreme_spread_threshold: float = 0.01,
) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: row["time_utc"])
    times = [row["time_utc"].astimezone(UTC) for row in ordered]
    counts = Counter(times)
    expected = expected_market_minutes(start_utc, end_utc)
    observed = set(times)
    missing = [ts for ts in expected if ts not in observed]
    spreads = [row.get("ask_c") - row.get("bid_c") for row in ordered if row.get("ask_c") is not None and row.get("bid_c") is not None]
    candles = [_row_to_candle(row, instrument=instrument) for row in ordered]
    aggregate_counts = {}
    incomplete_aggregates = {}
    for target in ("M5", "M15", "H1", "H4", "D1AGG"):
        result = aggregate_m1_candles(candles, target=target, missing_policy="mark_incomplete")
        aggregate_counts[target] = len(result.candles)
        incomplete_aggregates[target] = sum(1 for candle in result.candles if not candle.complete)
    data_hash = None
    if candles:
        data_hash = compute_candle_data_hash(_candle_to_record_like(candles[-1]))
    return {
        "instrument": instrument,
        "start_utc": start_utc.isoformat(),
        "end_utc": end_utc.isoformat(),
        "expected_m1_count": len(expected),
        "actual_m1_count": len(rows),
        "missing_minutes": len(missing),
        "duplicate_timestamps": sum(count - 1 for count in counts.values() if count > 1),
        "incomplete_candles": sum(1 for row in ordered if not row.get("complete")),
        "negative_or_zero_spreads": sum(1 for spread in spreads if spread <= 0),
        "extreme_spreads": sum(1 for spread in spreads if spread > extreme_spread_threshold),
        "weekend_gaps_excluded": True,
        "first_timestamp": times[0].isoformat() if times else None,
        "last_timestamp": times[-1].isoformat() if times else None,
        "data_hash": data_hash,
        "aggregate_counts": aggregate_counts,
        "incomplete_aggregate_counts": incomplete_aggregates,
    }


def expected_market_minutes(start_utc: datetime, end_utc: datetime) -> list[datetime]:
    out: list[datetime] = []
    cursor = start_utc.astimezone(UTC)
    end = end_utc.astimezone(UTC)
    while cursor < end:
        if cursor.weekday() < 5:
            out.append(cursor)
        cursor += timedelta(minutes=1)
    return out


def _row_to_candle(row: dict[str, Any], *, instrument: str) -> Candle:
    return Candle(
        instrument=instrument,
        granularity="M1",
        time=row["time_utc"],
        complete=bool(row.get("complete")),
        volume=int(row.get("volume") or 0),
        bid_o=_decimal(row.get("bid_o")),
        bid_h=_decimal(row.get("bid_h")),
        bid_l=_decimal(row.get("bid_l")),
        bid_c=_decimal(row.get("bid_c")),
        ask_o=_decimal(row.get("ask_o")),
        ask_h=_decimal(row.get("ask_h")),
        ask_l=_decimal(row.get("ask_l")),
        ask_c=_decimal(row.get("ask_c")),
        mid_o=_decimal(row.get("mid_o")),
        mid_h=_decimal(row.get("mid_h")),
        mid_l=_decimal(row.get("mid_l")),
        mid_c=_decimal(row.get("mid_c")),
    )


def _candle_to_record_like(candle: Candle):
    from forex_bot.data.postgres_candle_store import CandleRecord

    return CandleRecord(
        instrument=candle.instrument,
        granularity=candle.granularity,
        time_utc=candle.time,
        complete=candle.complete,
        volume=candle.volume,
        bid_o=float(candle.bid_o) if candle.bid_o is not None else None,
        bid_h=float(candle.bid_h) if candle.bid_h is not None else None,
        bid_l=float(candle.bid_l) if candle.bid_l is not None else None,
        bid_c=float(candle.bid_c) if candle.bid_c is not None else None,
        ask_o=float(candle.ask_o) if candle.ask_o is not None else None,
        ask_h=float(candle.ask_h) if candle.ask_h is not None else None,
        ask_l=float(candle.ask_l) if candle.ask_l is not None else None,
        ask_c=float(candle.ask_c) if candle.ask_c is not None else None,
    )


def _decimal(value: Any) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Validate local canonical M1 candle rows.")
    parser.add_argument("--instrument", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    cfg = get_research_database_config(environ=environ, require=True)
    store = PostgresCandleStore(cfg)
    start = parse_utc(args.start)
    end = parse_utc(args.end)
    rows = store.query_candles(
        instrument=args.instrument,
        granularity="M1",
        start_utc=start,
        end_utc=end,
    )
    report = analyze_rows(rows, instrument=args.instrument, start_utc=start, end_utc=end)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
