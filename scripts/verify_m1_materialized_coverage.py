#!/usr/bin/env python3
"""Verify materialized M1-derived timeframe coverage in Postgres."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.m1_corpus_validation import MAJOR_PAIRS
from forex_bot.data.m1_timeframe_materialization import (
    MATERIALIZED_FROM_M1,
    MATERIALIZED_SOURCE,
    STORAGE_GRANULARITY,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ

OUT_DIR = ROOT / "research/m1_timeframe_materialization"


def main() -> int:
    bootstrap_environ()
    store = PostgresCandleStore(get_research_database_config())
    report: dict[str, object] = {
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "source": MATERIALIZED_SOURCE,
        "targets": list(MATERIALIZED_FROM_M1),
        "pairs": {},
        "status": "PASS",
    }
    for instrument in MAJOR_PAIRS:
        pair_report: dict[str, object] = {"targets": {}}
        for target in MATERIALIZED_FROM_M1:
            storage = STORAGE_GRANULARITY[target]
            count = store.count_candles(
                instrument=instrument,
                granularity=storage,
                source=MATERIALIZED_SOURCE,
            )
            last = store.max_candle_time(
                instrument=instrument,
                granularity=storage,
                source=MATERIALIZED_SOURCE,
            )
            pair_report["targets"][target] = {
                "storage_granularity": storage,
                "row_count": count,
                "last_utc": last.isoformat() if last else None,
            }
            if count == 0:
                report["status"] = "FAIL"
                pair_report["status"] = "FAIL"
        if "status" not in pair_report:
            pair_report["status"] = "PASS"
        report["pairs"][instrument] = pair_report

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "store_coverage_check.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "pairs": len(MAJOR_PAIRS)}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
