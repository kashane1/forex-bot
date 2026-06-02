#!/usr/bin/env python3
"""Dry-run-default public derivatives data fetch for BTC/ETH perps.

Safety posture (CRYPTO_FAMILY_E_DERIVATIVES_DATA_PREP_001_PLAN.md §4):
- DRY-RUN by default — prints the resolved public plan and exits without network.
- A real public fetch happens ONLY with ``--execute-public-fetch``.
- Public market-data endpoints only (allowlist enforced in derivatives_sources).
- BTC and ETH perps only; unknown / non-BTC-ETH symbols are refused.
- Refuses to run if exchange credential env vars are present (public-only).
- Raw responses, if ever written, go to a gitignored local dir; only the compact
  manifest is suitable for commit.

This script creates NO strategy, campaign, front gate, or approval.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from research.crypto.derivatives_registry import (
    quote_ccy,
    validate_perp,
    validate_venue,
    venue_symbol,
)
from research.crypto.derivatives_sources import (
    UnsafeSourceError,
    assert_no_credentials_required,
    build_request_url,
    count_payload_rows,
    endpoint_for,
)

DATA_CLASSES = ("funding", "open_interest", "mark_index", "perp_ohlcv")
RAW_DIR = ROOT / "research" / "crypto" / "derivatives" / "raw"  # gitignored
MANIFEST_DIR = ROOT / "research" / "crypto" / "derivatives" / "manifests"


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    """Resolve and safety-check the requested fetch into a plan dict (no I/O)."""
    venue = validate_venue(args.source)
    canonical = validate_perp(args.instrument)  # BTC/ETH-only guard (raises ValueError)
    if args.data_class not in DATA_CLASSES:
        raise UnsafeSourceError(f"unknown data class: {args.data_class}")
    endpoint = endpoint_for(venue, args.data_class)
    url = build_request_url(venue, args.data_class)
    return {
        "venue": venue,
        "canonical_id": canonical,
        "venue_symbol": venue_symbol(canonical, venue),
        "quote_ccy": quote_ccy(canonical, venue),
        "data_class": args.data_class,
        "endpoint_path": endpoint.path,
        "request_url": url,
        "start_utc": _parse_dt(args.start).isoformat() if args.start else None,
        "end_utc": _parse_dt(args.end).isoformat() if args.end else None,
        "limit": args.limit,
        "note": endpoint.note,
    }


def _venue_params(plan: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    """Build venue-specific public query params (symbol + window).

    Only ``binance-usdm`` and ``bybit`` are wired for execute mode in this prep
    sprint; other venues are reachable in dry-run but raise here to avoid sending
    a malformed request. The native symbol is path-encoded for kraken-futures.
    """
    venue = plan["venue"]
    params: dict[str, Any] = {}
    if plan["start_utc"]:
        params["startTime"] = int(_parse_dt(args.start).timestamp() * 1000)
    if plan["end_utc"]:
        params["endTime"] = int(_parse_dt(args.end).timestamp() * 1000)
    if args.limit:
        params["limit"] = args.limit
    if venue == "binance-usdm":
        params["symbol"] = plan["venue_symbol"]
    elif venue == "bybit":
        params["symbol"] = plan["venue_symbol"]
        params["category"] = "linear"
        if plan["data_class"] == "open_interest":
            params["intervalTime"] = "1h"
    elif venue == "okx":
        params.pop("startTime", None)
        params.pop("endTime", None)
        params["instId"] = plan["venue_symbol"]
        if plan["data_class"] == "open_interest":
            params["instType"] = "SWAP"
    else:
        raise UnsafeSourceError(
            f"execute-public-fetch wired for binance-usdm/bybit/okx only in prep sprint; got {venue!r}"
        )
    return params


def run(args: argparse.Namespace, *, environ: dict[str, str] | None = None) -> dict[str, Any]:
    # Public-only guard: refuse if exchange credentials are present.
    assert_no_credentials_required(environ if environ is not None else {})
    plan = build_plan(args)

    if not args.execute_public_fetch:
        return {"status": "DRY_RUN", "would_fetch": plan, "raw_dir": str(RAW_DIR)}

    # --- real public fetch path (guarded) ---
    import httpx  # local import keeps dry-run import-light

    started_at = datetime.now(UTC)
    batch_id = str(uuid.uuid4())
    params = _venue_params(plan, args)
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(plan["request_url"], params=params)
        resp.raise_for_status()
        payload = resp.json()

    raw_rows = count_payload_rows(payload)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{batch_id}.json"
    raw_path.write_text(json.dumps(payload), encoding="utf-8")  # gitignored

    manifest = {
        "batch_id": batch_id,
        "status": "PASS",
        "source": plan["venue"],
        "endpoint_category": plan["data_class"],
        "instrument": plan["canonical_id"],
        "native_symbol": plan["venue_symbol"],
        "canonical_symbol": plan["canonical_id"],
        "quote_ccy": plan["quote_ccy"],
        "start_utc": plan["start_utc"],
        "end_utc": plan["end_utc"],
        "rows_fetched": raw_rows,
        "fetched_at_utc": started_at.isoformat(),
        "local_raw_path": str(raw_path.relative_to(ROOT)),  # repo-relative; file itself gitignored
    }
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    (MANIFEST_DIR / f"{batch_id}.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {"status": "FETCHED", "manifest": manifest}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="binance-usdm", help="public venue (e.g. binance-usdm, bybit)")
    parser.add_argument("--instrument", default="BTC_PERP_USD", help="BTC_PERP_USD or ETH_PERP_USD")
    parser.add_argument("--data-class", default="funding", choices=DATA_CLASSES)
    parser.add_argument("--start", default=None, help="ISO UTC start (optional)")
    parser.add_argument("--end", default=None, help="ISO UTC end (optional)")
    parser.add_argument("--limit", type=int, default=None, help="max rows (venue-capped)")
    parser.add_argument(
        "--execute-public-fetch",
        action="store_true",
        help="actually perform the public fetch (default: dry-run plan only)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    import os

    args = build_parser().parse_args(argv)
    try:
        result = run(args, environ=dict(os.environ))
    except UnsafeSourceError as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
