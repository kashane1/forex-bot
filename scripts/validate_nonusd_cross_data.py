#!/usr/bin/env python3
"""Validate & diagnose non-USD FX cross data (compact summaries only).

Read-only validation/diagnostics for registered non-USD crosses. Every
capability degrades gracefully when a cross has no rows yet
(`NOT_INGESTED`) and when no research database is configured
(`db_state = UNAVAILABLE`) — the expected state until a credentialed M1
fetch is run. Output is a single compact JSON summary; this is
diagnostic-only and never strategy evidence.

Capabilities: instrument-metadata checks, row counts, missing-bar
analysis, aggregation consistency, spread diagnostics, session
diagnostics.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.cross_ingestion import cross_coverage, cross_ingestion_targets
from forex_bot.domain.cross_instruments import cross_spec, registered_crosses
from forex_bot.research.cost_models import cross_cost_profile

# Reuse the cost-atlas session buckets so cross diagnostics line up with
# the majors' session conventions.
sys.path.insert(0, str(ROOT))
from research.cost_atlas.session import session_bucket


def metadata_check() -> dict[str, Any]:
    """Validate registry metadata for every registered cross (no DB)."""
    rows: list[dict[str, Any]] = []
    ok = True
    for name in registered_crosses():
        spec = cross_spec(name)
        jpy = spec.is_jpy_cross
        expected_pip = -2 if jpy else -4
        expected_dp = 3 if jpy else 5
        problems: list[str] = []
        if spec.pip_location != expected_pip:
            problems.append("pip_location")
        if spec.display_precision != expected_dp:
            problems.append("display_precision")
        if "USD" in name.split("_"):
            problems.append("has_usd_leg")
        if spec.conservative_bp_per_day <= 0:
            problems.append("missing_bp_per_day")
        ok = ok and not problems
        rows.append({
            "instrument": name, "tier": spec.tier, "quote": spec.quote_currency,
            "pip_location": spec.pip_location, "display_precision": spec.display_precision,
            "cost_band": spec.cost_band, "ok": not problems, "problems": problems,
        })
    return {"status": "PASS" if ok else "FAIL", "crosses": rows}


def session_spread_summary(rows: list[dict[str, Any]], *, pip_size: float) -> dict[str, Any]:
    """Compact per-session spread summary from M1 bid/ask rows."""
    by_session: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        bid_c, ask_c, ts = row.get("bid_c"), row.get("ask_c"), row.get("time_utc")
        if bid_c is None or ask_c is None or ts is None:
            continue
        spread_pips = (float(ask_c) - float(bid_c)) / pip_size
        by_session[session_bucket(ts.hour)].append(spread_pips)
    out: dict[str, Any] = {}
    for session, spreads in by_session.items():
        spreads.sort()
        n = len(spreads)
        out[session] = {
            "n": n,
            "median_pips": round(spreads[n // 2], 4) if n else None,
            "p90_pips": round(spreads[min(n - 1, round(0.9 * (n - 1)))], 4) if n else None,
        }
    return out


def diagnose_cross(store: Any, instrument: str, *, run_diagnostics: bool) -> dict[str, Any]:
    """Per-cross compact validation+diagnostics; NOT_INGESTED when empty."""
    coverage = cross_coverage(store, instrument)
    entry: dict[str, Any] = {
        "instrument": instrument,
        "state": coverage.state,
        "row_count": coverage.row_count,
        "last_timestamp": coverage.last_timestamp,
        "cost_profile": cross_cost_profile(instrument),
    }
    if coverage.state == "NOT_INGESTED" or not run_diagnostics:
        return entry
    # Ingested: layer real-data diagnostics via the corpus validator.
    from forex_bot.data.m1_corpus_validation import (
        aggregation_coverage_for_pair,
        h4_drift_for_pair,
        quality_for_pair,
    )
    quality = quality_for_pair(store, instrument)
    entry["quality"] = {
        "status": quality["status"],
        "missing_minutes": quality.get("missing_minutes"),
        "duplicate_timestamps": quality.get("duplicate_timestamps"),
        "spread_percentiles": quality.get("spread_percentiles"),
    }
    agg = aggregation_coverage_for_pair(store, instrument)
    entry["aggregation"] = {
        tf: {"bar_count": v["bar_count"], "coverage_pct_vs_m1": v["coverage_pct_vs_m1"]}
        for tf, v in agg["timeframes"].items()
    }
    drift = h4_drift_for_pair(store, instrument)
    entry["h4_consistency"] = {"status": drift["status"], "ohlc_mismatch_count": drift.get("ohlc_mismatch_count")}
    entry["session_spread"] = _session_diagnostics(store, instrument)
    return entry


def _session_diagnostics(store: Any, instrument: str, *, sample_days: int = 30) -> dict[str, Any]:
    """Per-session spread summary from a bounded M1 sample (first window)."""
    from datetime import timedelta

    from forex_bot.data.m1_corpus_validation import iter_m1_chunks, pair_range

    pip = float(cross_spec(instrument).pip_size)
    pr = pair_range(store, instrument)
    rows: list[dict[str, Any]] = []
    for chunk in iter_m1_chunks(
        store, instrument=instrument,
        start_utc=pr.start_utc, end_utc=min(pr.end_utc, pr.start_utc + timedelta(days=sample_days)),
    ):
        rows.extend(chunk)
    return session_spread_summary(rows, pip_size=pip)


def build_report(store: Any, *, scope: str = "all", run_diagnostics: bool = True) -> dict[str, Any]:
    """Build the compact validation report across the scoped crosses."""
    targets = registered_crosses() if scope == "all" else cross_ingestion_targets(scope=scope)
    meta = metadata_check()
    crosses = [diagnose_cross(store, name, run_diagnostics=run_diagnostics) for name in targets]
    ingested = [c for c in crosses if c["state"] == "INGESTED"]
    return {
        "strategy_evidence": False,
        "diagnostic_only": True,
        "scope": scope,
        "metadata_check": meta["status"],
        "target_count": len(targets),
        "ingested_count": len(ingested),
        "not_ingested": [c["instrument"] for c in crosses if c["state"] == "NOT_INGESTED"],
        "metadata": meta["crosses"],
        "crosses": crosses,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["all", "primary"], default="all")
    parser.add_argument(
        "--no-diagnostics", action="store_true",
        help="Metadata + coverage only; skip per-pair quality/aggregation/spread.",
    )
    parser.add_argument("--out")
    args = parser.parse_args(argv)

    # Metadata always works without a DB.
    try:
        from forex_bot.data.postgres_candle_store import PostgresCandleStore
        from forex_bot.data.research_db import get_research_database_config
        from forex_bot.project_env import bootstrap_environ

        bootstrap_environ()
        cfg = get_research_database_config(require=True)
        store: Any = PostgresCandleStore(cfg)
        store.ensure_schema()
        db_state = "AVAILABLE"
    except Exception as exc:
        store = None
        db_state = f"UNAVAILABLE:{type(exc).__name__}"

    if store is None:
        meta = metadata_check()
        report = {
            "strategy_evidence": False,
            "diagnostic_only": True,
            "db_state": db_state,
            "metadata_check": meta["status"],
            "metadata": meta["crosses"],
            "note": "No research database configured; metadata validated, coverage/diagnostics skipped.",
        }
    else:
        report = build_report(store, scope=args.scope, run_diagnostics=not args.no_diagnostics)
        report["db_state"] = db_state

    text = json.dumps(report, indent=2, sort_keys=True, default=str)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
