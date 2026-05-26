#!/usr/bin/env python3
"""Build a single ``EXPORT_MANIFEST.json`` from the per-instrument
provenance sidecars in a Lean-parity exports directory.

This consolidates the seven ``*.provenance.json`` files into one
machine-readable manifest that records which DB the export came from
and which CAMPAIGN it was generated for, so downstream consumers can
verify the bundle in one place.

Read-only against the existing sidecars (it only writes
``EXPORT_MANIFEST.json``).

Usage:
    python scripts/build_lean_parity_export_manifest.py \
        --exports-dir research/lean_parity/exports/campaign_002_h4 \
        --campaign-id CAMPAIGN_002_H4_LEAN_PARITY \
        --source-db data/campaign_002.sqlite3
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_manifest(
    *,
    exports_dir: Path,
    campaign_id: str,
    source_db: str,
    instruments: tuple[str, ...] = (
        "EUR_USD",
        "GBP_USD",
        "USD_JPY",
        "AUD_USD",
        "USD_CAD",
        "USD_CHF",
        "NZD_USD",
    ),
) -> dict:
    per_instrument = []
    for inst in instruments:
        prov_path = exports_dir / f"{inst}_H4_lean.provenance.json"
        if not prov_path.exists():
            per_instrument.append(
                {"instrument": inst, "missing_provenance": True}
            )
            continue
        prov = json.loads(prov_path.read_text(encoding="utf-8"))
        per_instrument.append(
            {
                "instrument": inst,
                "csv": prov.get("lean_csv"),
                "provenance": prov_path.name,
                "candle_count": prov.get("candle_count"),
                "first_ts": prov.get("first_ts"),
                "last_ts": prov.get("last_ts"),
                "data_sha256": prov.get("data_sha256"),
                "campaign_002_data_request_hash": prov.get(
                    "campaign_002_data_request_hash"
                ),
                "source": prov.get("source"),
                "exported_at": prov.get("exported_at"),
            }
        )
    return {
        "campaign_id": campaign_id,
        "manifest_generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_db": source_db,
        "instruments": list(instruments),
        "per_instrument": per_instrument,
        "approved_strategies_yaml_state": "approved: []",
        "diagnostic_disclaimer": (
            "Manifest is a reproduction aid, not an approval. "
            "configs/approved_strategies.yaml remains approved: []."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--exports-dir",
        default="research/lean_parity/exports/campaign_002_h4",
        type=Path,
    )
    ap.add_argument(
        "--campaign-id",
        default="CAMPAIGN_002_H4_LEAN_PARITY",
    )
    ap.add_argument(
        "--source-db",
        default="data/campaign_002.sqlite3",
    )
    args = ap.parse_args(argv)

    if not args.exports_dir.exists():
        print(
            f"BLOCKED: exports-dir does not exist: {args.exports_dir}",
            file=sys.stderr,
        )
        return 2

    obj = build_manifest(
        exports_dir=args.exports_dir,
        campaign_id=args.campaign_id,
        source_db=args.source_db,
    )
    out_path = args.exports_dir / "EXPORT_MANIFEST.json"
    out_path.write_text(
        json.dumps(obj, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
