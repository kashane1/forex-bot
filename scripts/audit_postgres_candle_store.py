#!/usr/bin/env python3
"""Audit the local Postgres candle store."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.postgres_candle_store import (
    PostgresCandleStore,
    common_timestamp_intersection,
    expected_timestamps,
)
from forex_bot.data.research_db import (
    ResearchDatabaseBlocked,
    ResearchDatabaseUnsafe,
    get_research_database_config,
)

DEFAULT_INSTRUMENTS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)


def analyze_rows(rows_by_instrument: dict[str, list[dict[str, Any]]], *, granularity: str) -> dict[str, Any]:
    duplicates: dict[str, int] = {}
    incomplete: dict[str, int] = {}
    ohlc_violations: dict[str, int] = {}
    nonpositive: dict[str, int] = {}
    spread_anomalies: dict[str, int] = {}
    missing_slots: dict[str, int] = {}
    pair_summary: dict[str, Any] = {}
    any_issue = False
    for instrument, rows in rows_by_instrument.items():
        counts = Counter(row["time_utc"] for row in rows)
        duplicates[instrument] = sum(1 for count in counts.values() if count > 1)
        incomplete[instrument] = sum(1 for row in rows if not row["complete"])
        ohlc_violations[instrument] = sum(
            1
            for row in rows
            if (
                row["mid_h"] is not None
                and row["mid_l"] is not None
                and (row["mid_h"] < max(row["mid_o"], row["mid_c"]) or row["mid_l"] > min(row["mid_o"], row["mid_c"]))
            )
        )
        nonpositive[instrument] = sum(
            1
            for row in rows
            for field in ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c")
            if row.get(field) is not None and row[field] <= 0
        )
        spread_anomalies[instrument] = sum(
            1
            for row in rows
            if row.get("spread_close") is not None and row["spread_close"] <= 0
        )
        if rows:
            expected = expected_timestamps(rows[0]["time_utc"], rows[-1]["time_utc"], granularity=granularity)
            missing_slots[instrument] = max(0, len(expected) - len({row["time_utc"] for row in rows}))
        else:
            missing_slots[instrument] = 0
        pair_summary[instrument] = {
            "candle_count": len(rows),
            "first_utc": rows[0]["time_utc"] if rows else None,
            "last_utc": rows[-1]["time_utc"] if rows else None,
        }
        if any(
            (
                duplicates[instrument],
                incomplete[instrument],
                ohlc_violations[instrument],
                nonpositive[instrument],
                spread_anomalies[instrument],
                missing_slots[instrument],
            )
        ):
            any_issue = True
    intersection = common_timestamp_intersection(rows_by_instrument)
    status = "PASS"
    if not rows_by_instrument:
        status = "BLOCKED"
    elif any_issue:
        status = "PARTIAL"
    return {
        "status": status,
        "granularity": granularity,
        "pairs": pair_summary,
        "duplicates": duplicates,
        "incomplete": incomplete,
        "ohlc_violations": ohlc_violations,
        "nonpositive_prices": nonpositive,
        "spread_anomalies": spread_anomalies,
        "missing_slots": missing_slots,
        "common_timestamp_intersection": intersection,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Postgres Candle Store Audit",
        "",
        f"- Status: **{summary['status']}**",
        f"- Granularity: `{summary['granularity']}`",
        f"- Common intersection count: `{summary['common_timestamp_intersection']['count']}`",
        "",
        "| Instrument | Candles | First | Last | Missing H4 slots |",
        "| --- | ---: | --- | --- | ---: |",
    ]
    for instrument, info in sorted(summary["pairs"].items()):
        lines.append(
            f"| {instrument} | {info['candle_count']} | {info['first_utc']} | "
            f"{info['last_utc']} | {summary['missing_slots'][instrument]} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the local Postgres candle store.")
    parser.add_argument("--granularity", default="H4")
    parser.add_argument("--out", default="reports/data_quality/postgres_h4_audit_latest")
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
    rows_by_instrument = {
        instrument: store.query_candles(instrument=instrument, granularity=args.granularity)
        for instrument in DEFAULT_INSTRUMENTS
    }
    summary = analyze_rows(rows_by_instrument, granularity=args.granularity)
    summary["database_name"] = cfg.database_name
    summary["schema_name"] = cfg.schema
    summary["created_at_utc"] = datetime.now(UTC).isoformat()
    out_base = Path(args.out)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    out_base.with_suffix(".json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    out_base.with_suffix(".md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
