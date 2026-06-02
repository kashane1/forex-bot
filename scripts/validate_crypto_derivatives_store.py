#!/usr/bin/env python3
"""Validate the crypto derivatives data layer (BTC/ETH perps only).

No DB binding is forced this sprint, so by default this validates the committed
**synthetic fixtures** through the real parsers + validation helpers — a
self-check that the tooling is wired correctly with no network and no store.

Modes:
  (default)        validate synthetic fixtures and print a summary
  --manifests-dir  additionally summarize committed fetch manifests

Runs NO factor diagnostics and infers NO edge. Public-data scaffolding only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from research.crypto.derivatives_sources import (
    parse_binance_funding,
    parse_binance_mark_klines,
    parse_binance_perp_klines,
    parse_bybit_open_interest,
)
from research.crypto.derivatives_validation import (
    summarize,
    validate_funding,
    validate_mark_index,
    validate_open_interest,
    validate_perp_ohlcv,
)

FIX = ROOT / "research" / "crypto" / "fixtures" / "derivatives"
MANIFEST_DIR = ROOT / "research" / "crypto" / "derivatives" / "manifests"


def _load(name: str) -> Any:
    return json.loads((FIX / name).read_text())


def validate_fixtures() -> dict[str, Any]:
    validations = [
        validate_funding(parse_binance_funding(_load("binance_funding_btc.json"))),
        validate_perp_ohlcv(
            parse_binance_perp_klines(
                _load("binance_perp_klines_btc.json"),
                canonical_id="BTC_PERP_USD",
                granularity="H1",
            )
        ),
        validate_mark_index(
            parse_binance_mark_klines(
                _load("binance_mark_klines_btc.json"),
                canonical_id="BTC_PERP_USD",
                granularity="H1",
            )
        ),
        validate_open_interest(
            parse_bybit_open_interest(
                _load("bybit_open_interest_btc.json"),
                canonical_id="BTC_PERP_USD",
                interval="1h",
            )
        ),
    ]
    return summarize(validations)


def summarize_manifests(manifest_dir: Path) -> dict[str, Any]:
    if not manifest_dir.exists():
        return {"manifest_count": 0, "manifests": []}
    manifests = []
    for path in sorted(manifest_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        manifests.append(
            {
                "batch_id": payload.get("batch_id"),
                "source": payload.get("source"),
                "instrument": payload.get("instrument"),
                "endpoint_category": payload.get("endpoint_category"),
                "rows_fetched": payload.get("rows_fetched"),
            }
        )
    return {"manifest_count": len(manifests), "manifests": manifests}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifests-dir",
        type=Path,
        default=None,
        help=f"summarize committed fetch manifests (e.g. {MANIFEST_DIR})",
    )
    args = parser.parse_args(argv)

    result: dict[str, Any] = {"fixtures": validate_fixtures()}
    if args.manifests_dir is not None:
        result["manifests"] = summarize_manifests(args.manifests_dir)

    print(json.dumps(result, indent=2, default=str))
    # Non-zero exit only on a FAIL in fixture validation (tooling regression).
    return 1 if result["fixtures"]["overall_status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
