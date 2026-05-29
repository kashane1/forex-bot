#!/usr/bin/env python3
"""CAMPAIGN_026 Phase 2 — materialize + verify diagnostic M3/M30 from canonical M1.

Dedicated driver for the timeframe-ladder diagnostic. Materializes M3 and M30 for the
seven majors from local canonical M1 (no broker calls) and writes compact verification
artifacts under research/campaign_026/materialization/. It deliberately does NOT use
scripts/materialize_m1_derived_timeframes.py's main(), because that overwrites the
shared research/m1_timeframe_materialization/ manifests for the canonical timeframes.

Verification strategy (rigorous but bounded runtime):
  * full-window: SQL-side checks — row counts, first/last, duplicate buckets,
    OHLC ordering (high>=max(o,c), low<=min(o,c), high>=low for bid/ask),
    bucket-start alignment (minute % bucket == 0, second == 0), provenance.
  * exact cross-check: re-aggregate M1 -> M3/M30 over a bounded sample window per pair
    and assert byte-for-byte OHLC equality with the stored bars (verify_materialized_pair).

No strategy evidence. No approval. No test lockbox. Reads M1 only.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from forex_bot.data.m1_timeframe_materialization import (
    MATERIALIZED_SOURCE,
    STORAGE_GRANULARITY,
    aggregation_config_hash,
    materialize_pair,
    resolve_pair_window,
    verify_materialized_pair,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ

PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"]
TARGETS = ("M3", "M30")
BUCKET_MINUTES = {"M3": 3, "M30": 30}
OUT_DIR = ROOT / "research/campaign_026/materialization"


def _sql_verify(store: PostgresCandleStore, instrument: str, storage_gran: str, bucket_min: int) -> dict:
    sch = store.config.schema
    with store.connector(store.config.url) as conn:
        cur = conn.cursor()
        base = f"FROM {sch}.candles WHERE instrument=%s AND granularity=%s AND source=%s"
        args = (instrument, storage_gran, MATERIALIZED_SOURCE)
        cur.execute(
            f"SELECT COUNT(*), MIN(time_utc) AT TIME ZONE 'UTC', MAX(time_utc) AT TIME ZONE 'UTC' {base}",
            args,
        )
        count, first, last = cur.fetchone()
        cur.execute(
            f"SELECT COUNT(*) - COUNT(DISTINCT time_utc) {base}", args
        )
        dup_buckets = cur.fetchone()[0]
        # bucket-start alignment: minute divisible by bucket, zero seconds
        cur.execute(
            f"SELECT COUNT(*) {base} AND (EXTRACT(MINUTE FROM time_utc)::int %% %s <> 0 "
            f"OR EXTRACT(SECOND FROM time_utc)::int <> 0)",
            (*args, bucket_min),
        )
        misaligned = cur.fetchone()[0]
        # OHLC ordering violations (bid + ask)
        cur.execute(
            f"SELECT COUNT(*) {base} AND ("
            "bid_h < bid_l OR ask_h < ask_l "
            "OR bid_h < bid_o OR bid_h < bid_c OR bid_l > bid_o OR bid_l > bid_c "
            "OR ask_h < ask_o OR ask_h < ask_c OR ask_l > ask_o OR ask_l > ask_c)",
            args,
        )
        ohlc_viol = cur.fetchone()[0]
        # bid/ask ordering (ask >= bid on close)
        cur.execute(
            f"SELECT COUNT(*) {base} AND ask_c < bid_c", args
        )
        bidask_viol = cur.fetchone()[0]
        # incomplete buckets stored (should be zero — omit policy)
        cur.execute(f"SELECT COUNT(*) {base} AND complete = false", args)
        incomplete = cur.fetchone()[0]
        # provenance: distinct granularities/sources present
        cur.execute(f"SELECT COUNT(DISTINCT source) {base}", args)
        n_sources = cur.fetchone()[0]
    return {
        "rows": int(count),
        "first_utc": first.isoformat() if first else None,
        "last_utc": last.isoformat() if last else None,
        "duplicate_buckets": int(dup_buckets),
        "misaligned_buckets": int(misaligned),
        "ohlc_ordering_violations": int(ohlc_viol),
        "bidask_ordering_violations": int(bidask_viol),
        "incomplete_buckets_stored": int(incomplete),
        "distinct_sources": int(n_sources),
        "status": "PASS"
        if (
            count > 0
            and dup_buckets == 0
            and misaligned == 0
            and ohlc_viol == 0
            and bidask_viol == 0
            and incomplete == 0
        )
        else "FAIL",
    }


def main() -> int:
    bootstrap_environ()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument(
        "--sample-verify-days",
        type=int,
        default=45,
        help="window length for the exact re-aggregation cross-check",
    )
    args = parser.parse_args()

    store = PostgresCandleStore(get_research_database_config())
    store.ensure_schema()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    manifest: dict = {
        "campaign_id": "CAMPAIGN_026",
        "phase": 2,
        "started_at_utc": datetime.now(UTC).isoformat(),
        "pairs": PAIRS,
        "targets": list(TARGETS),
        "source": MATERIALIZED_SOURCE,
        "storage_granularity": {tf: STORAGE_GRANULARITY[tf] for tf in TARGETS},
        "aggregation_config_hash": aggregation_config_hash(),
        "network_or_broker_calls": False,
        "verify_only": args.verify_only,
        "pair_results": {},
        "not_approved": True,
    }

    if not args.verify_only:
        for instrument in PAIRS:
            start, end = resolve_pair_window(
                store, instrument, from_utc=None, to_utc=None, incremental=False, targets=TARGETS
            )
            res = materialize_pair(
                store, instrument, from_utc=start, to_utc=end, targets=TARGETS, chunk_days=30
            )
            manifest["pair_results"][instrument] = {
                "window": {"from_utc": start.isoformat(), "to_utc": end.isoformat()},
                "targets": {
                    tf: {
                        "rows_upserted": st.rows_upserted,
                        "first_utc": st.first_utc.isoformat() if st.first_utc else None,
                        "last_utc": st.last_utc.isoformat() if st.last_utc else None,
                        "omitted_incomplete_blocks": st.omitted_incomplete_blocks,
                    }
                    for tf, st in res.targets.items()
                },
            }

    # ---- full-window SQL verification ----
    sql_reports: dict = {}
    all_pass = True
    for instrument in PAIRS:
        sql_reports[instrument] = {}
        for tf in TARGETS:
            rep = _sql_verify(store, instrument, STORAGE_GRANULARITY[tf], BUCKET_MINUTES[tf])
            sql_reports[instrument][tf] = rep
            if rep["status"] != "PASS":
                all_pass = False

    # ---- exact re-aggregation cross-check on a bounded sample per pair ----
    from datetime import timedelta

    exact_reports: dict = {}
    for instrument in PAIRS:
        start, end = resolve_pair_window(
            store, instrument, from_utc=None, to_utc=None, incremental=False, targets=TARGETS
        )
        sample_start = start
        sample_end = min(end, start + timedelta(days=args.sample_verify_days))
        rep = verify_materialized_pair(
            store, instrument, from_utc=sample_start, to_utc=sample_end, targets=TARGETS, chunk_days=30
        )
        exact_reports[instrument] = rep
        if rep["status"] != "PASS":
            all_pass = False

    manifest["elapsed_seconds"] = round(time.time() - t0, 1)
    manifest["status"] = "PASS" if all_pass else "FAIL"

    # ---- write compact artifacts ----
    (OUT_DIR / "m3_m30_materialization_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for tf, fname in (("M3", "m3_coverage_summary.json"), ("M30", "m30_coverage_summary.json")):
        cov = {
            inst: {
                "rows": sql_reports[inst][tf]["rows"],
                "first_utc": sql_reports[inst][tf]["first_utc"],
                "last_utc": sql_reports[inst][tf]["last_utc"],
            }
            for inst in PAIRS
        }
        (OUT_DIR / fname).write_text(
            json.dumps(
                {"campaign_id": "CAMPAIGN_026", "timeframe": tf, "source": MATERIALIZED_SOURCE, "pairs": cov},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    (OUT_DIR / "m3_m30_ohlc_verification.json").write_text(
        json.dumps(
            {"campaign_id": "CAMPAIGN_026", "sql_full_window": sql_reports, "exact_reaggregation_sample": exact_reports},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    gap = {
        inst: {
            tf: {
                "rows": sql_reports[inst][tf]["rows"],
                "duplicate_buckets": sql_reports[inst][tf]["duplicate_buckets"],
                "misaligned_buckets": sql_reports[inst][tf]["misaligned_buckets"],
                "incomplete_buckets_stored": sql_reports[inst][tf]["incomplete_buckets_stored"],
                "first_utc": sql_reports[inst][tf]["first_utc"],
                "last_utc": sql_reports[inst][tf]["last_utc"],
            }
            for tf in TARGETS
        }
        for inst in PAIRS
    }
    (OUT_DIR / "m3_m30_gap_summary.json").write_text(
        json.dumps({"campaign_id": "CAMPAIGN_026", "note": "weekend/session gaps are expected (omit policy)", "pairs": gap}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    prov = {
        "campaign_id": "CAMPAIGN_026",
        "source": MATERIALIZED_SOURCE,
        "source_granularity": "M1",
        "storage_granularity": {tf: STORAGE_GRANULARITY[tf] for tf in TARGETS},
        "aggregation_config_hash": aggregation_config_hash(),
        "distinct_sources_by_pair_tf": {
            inst: {tf: sql_reports[inst][tf]["distinct_sources"] for tf in TARGETS} for inst in PAIRS
        },
        "native_broker_m3_m30_exists": False,
    }
    (OUT_DIR / "m3_m30_provenance_summary.json").write_text(
        json.dumps(prov, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps({"status": manifest["status"], "pairs": len(PAIRS), "elapsed_s": manifest["elapsed_seconds"]}, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
