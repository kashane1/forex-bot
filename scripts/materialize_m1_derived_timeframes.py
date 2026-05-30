#!/usr/bin/env python3
"""Materialize M1-derived M5/M15/H1/H4 candles into Postgres."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.m1_corpus_validation import MAJOR_PAIRS, SUPPORTED_PAIRS
from forex_bot.data.m1_timeframe_materialization import (
    MATERIALIZED_FROM_M1,
    MATERIALIZED_SOURCE,
    SUPPORTED_MATERIALIZATION_TARGETS,
    aggregation_config_hash,
    materialize_pair,
    resolve_pair_window,
    verify_materialized_pair,
)
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.domain.cross_instruments import NONUSD_CROSS_PAIRS
from forex_bot.project_env import bootstrap_environ

OUT_DIR = ROOT / "research/m1_timeframe_materialization"


def _parse_utc(value: str) -> datetime:
    if "T" not in value:
        value = f"{value}T00:00:00Z"
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _resolve_pairs(args: argparse.Namespace) -> list[str]:
    if args.all_majors:
        return list(MAJOR_PAIRS)
    if args.all_crosses:
        return list(NONUSD_CROSS_PAIRS)
    if args.pair:
        # Majors (control universe) and registered non-USD crosses are both
        # materializable via the same price-agnostic aggregation rules.
        if args.pair not in SUPPORTED_PAIRS:
            raise SystemExit(f"pair not in supported universe: {args.pair}")
        return [args.pair]
    raise SystemExit("specify --pair EUR_GBP, --all-majors, or --all-crosses")


def _resolve_targets(raw: str | None) -> tuple[str, ...]:
    # Default (no --targets) = canonical recurring set only. Diagnostic M3/M30 are
    # opt-in via explicit --targets and validated against the supported union.
    if not raw:
        return MATERIALIZED_FROM_M1
    targets = tuple(part.strip() for part in raw.split(",") if part.strip())
    bad = [target for target in targets if target not in SUPPORTED_MATERIALIZATION_TARGETS]
    if bad:
        raise SystemExit(
            f"unsupported targets: {bad}; allowed={SUPPORTED_MATERIALIZATION_TARGETS}"
        )
    return targets


def main() -> int:
    bootstrap_environ()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair")
    parser.add_argument("--all-majors", action="store_true")
    parser.add_argument(
        "--all-crosses",
        action="store_true",
        help=f"Materialize every registered non-USD cross: {', '.join(NONUSD_CROSS_PAIRS)}",
    )
    parser.add_argument(
        "--targets",
        help="Comma-separated. Default (omit) = M5,M15,H1,H4. Diagnostic: M3,M30.",
    )
    parser.add_argument("--from", dest="from_utc")
    parser.add_argument("--to", dest="to_utc")
    parser.add_argument("--incremental", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--chunk-days", type=int, default=30)
    args = parser.parse_args()

    pairs = _resolve_pairs(args)
    targets = _resolve_targets(args.targets)
    from_arg = _parse_utc(args.from_utc) if args.from_utc else None
    to_arg = _parse_utc(args.to_utc) if args.to_utc else None

    db_cfg = get_research_database_config()
    store = PostgresCandleStore(db_cfg)
    store.ensure_schema()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    run_manifest: dict[str, object] = {
        "started_at_utc": datetime.now(UTC).isoformat(),
        "pairs": pairs,
        "targets": list(targets),
        "source": MATERIALIZED_SOURCE,
        "aggregation_config_hash": aggregation_config_hash(),
        "incremental": args.incremental,
        "dry_run": args.dry_run,
        "verify_only": args.verify_only,
        "pair_results": {},
        "verification": {},
        "not_approved": True,
    }

    if args.verify_only:
        all_pass = True
        for instrument in pairs:
            start, end = resolve_pair_window(
                store,
                instrument,
                from_utc=from_arg,
                to_utc=to_arg,
                incremental=False,
                targets=targets,
            )
            report = verify_materialized_pair(
                store,
                instrument,
                from_utc=start,
                to_utc=end,
                targets=targets,
                chunk_days=args.chunk_days,
            )
            run_manifest["verification"][instrument] = report
            if report["status"] != "PASS":
                all_pass = False
        run_manifest["status"] = "PASS" if all_pass else "FAIL"
        run_manifest["elapsed_seconds"] = round(time.time() - t0, 1)
        _write_artifacts(run_manifest)
        print(json.dumps({"status": run_manifest["status"], "pairs": len(pairs)}, indent=2))
        return 0 if all_pass else 1

    for instrument in pairs:
        start, end = resolve_pair_window(
            store,
            instrument,
            from_utc=from_arg,
            to_utc=to_arg,
            incremental=args.incremental,
            targets=targets,
        )
        if start >= end:
            run_manifest["pair_results"][instrument] = {
                "status": "SKIP",
                "reason": "empty window",
                "from_utc": start.isoformat(),
                "to_utc": end.isoformat(),
            }
            continue
        result = materialize_pair(
            store,
            instrument,
            from_utc=start,
            to_utc=end,
            targets=targets,
            chunk_days=args.chunk_days,
            dry_run=args.dry_run,
        )
        run_manifest["pair_results"][instrument] = result.to_dict()

    if not args.dry_run:
        all_pass = True
        for instrument in pairs:
            start, end = resolve_pair_window(
                store,
                instrument,
                from_utc=from_arg,
                to_utc=to_arg,
                incremental=False,
                targets=targets,
            )
            report = verify_materialized_pair(
                store,
                instrument,
                from_utc=start,
                to_utc=end,
                targets=targets,
                chunk_days=args.chunk_days,
            )
            run_manifest["verification"][instrument] = report
            if report["status"] != "PASS":
                all_pass = False
        run_manifest["status"] = "PASS" if all_pass else "FAIL"
    else:
        run_manifest["status"] = "DRY_RUN"

    run_manifest["elapsed_seconds"] = round(time.time() - t0, 1)
    _write_artifacts(run_manifest)
    print(json.dumps({"status": run_manifest["status"], "pairs": len(pairs)}, indent=2))
    return 0 if run_manifest.get("status") in {"PASS", "DRY_RUN"} else 1


def _write_artifacts(manifest: dict[str, object]) -> None:
    (OUT_DIR / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    coverage = {}
    for instrument, payload in manifest.get("pair_results", {}).items():
        if isinstance(payload, dict) and "targets" in payload:
            coverage[instrument] = payload["targets"]
    (OUT_DIR / "coverage_summary.json").write_text(
        json.dumps(
            {
                "aggregation_config_hash": manifest.get("aggregation_config_hash"),
                "pairs": coverage,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    verification = manifest.get("verification", {})
    (OUT_DIR / "verification_result.json").write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
