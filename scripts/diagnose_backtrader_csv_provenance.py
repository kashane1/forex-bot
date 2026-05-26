#!/usr/bin/env python3
"""Diagnose CSV/provenance mismatch in the Lean-parity export bundle.

Reads every ``<INSTRUMENT>_H4_lean.csv`` + ``<INSTRUMENT>_H4_lean.provenance.json``
pair under a given exports directory and emits a structured report
(JSON + Markdown) describing exactly which files match and which do
not.

For each instrument it reports:
- CSV path, provenance path
- raw file sha256 (full-file)
- row-sha256 (computed via research.backtrader_lane.data_adapter.compute_csv_sha256)
- expected data_sha256 from the provenance JSON
- row count vs provenance candle_count
- first / last timestamp (vs provenance first_ts / last_ts)
- whether the BT-lane sha-strict check would pass
- whether provenance appears stale relative to the CSV (csv mtime > provenance mtime)

This script is read-only and diagnostic. It does NOT modify any
artifact, does NOT change `approved_strategies.yaml`, and does NOT
contact OANDA or any other broker / cloud service.

Usage:
    python scripts/diagnose_backtrader_csv_provenance.py \
        --exports-dir research/lean_parity/exports/campaign_002_h4 \
        --out-json research/campaign_015/diagnostics/backtrader_provenance_mismatch.json \
        --out-md   research/campaign_015/diagnostics/backtrader_provenance_mismatch.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Use the same row-sha algorithm the BT lane uses.
from research.backtrader_lane.data_adapter import (  # noqa: E402
    compute_csv_sha256,
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


def _raw_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _csv_row_count_and_window(path: Path) -> tuple[int, str | None, str | None]:
    """Count data rows and return (count, first_time, last_time)."""
    first: str | None = None
    last: str | None = None
    count = 0
    with path.open("r", encoding="utf-8") as fh:
        header = next(fh, None)
        if header is None:
            return 0, None, None
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            ts = line.split(",", 1)[0]
            if first is None:
                first = ts
            last = ts
            count += 1
    return count, first, last


def diagnose_instrument(
    *,
    instrument: str,
    exports_dir: Path,
) -> dict[str, Any]:
    csv_path = exports_dir / f"{instrument}_H4_lean.csv"
    prov_path = exports_dir / f"{instrument}_H4_lean.provenance.json"
    result: dict[str, Any] = {
        "instrument": instrument,
        "csv_path": str(csv_path.relative_to(ROOT)) if csv_path.is_relative_to(ROOT) else str(csv_path),
        "provenance_path": str(prov_path.relative_to(ROOT)) if prov_path.is_relative_to(ROOT) else str(prov_path),
        "csv_exists": csv_path.exists(),
        "provenance_exists": prov_path.exists(),
        "csv_raw_sha256": None,
        "csv_row_sha256": None,
        "csv_row_count": None,
        "csv_first_ts": None,
        "csv_last_ts": None,
        "csv_mtime": None,
        "provenance_data_sha256": None,
        "provenance_candle_count": None,
        "provenance_first_ts": None,
        "provenance_last_ts": None,
        "provenance_exported_at": None,
        "provenance_mtime": None,
        "row_sha_match": None,
        "raw_sha_matches_provenance_data_sha": None,
        "row_count_match": None,
        "first_ts_match": None,
        "last_ts_match": None,
        "bt_strict_preflight_pass": False,
        "provenance_appears_stale": None,
        "notes": [],
    }
    if not csv_path.exists():
        result["notes"].append("CSV missing")
        return result
    if not prov_path.exists():
        result["notes"].append("provenance JSON missing")
        return result

    raw_sha = _raw_file_sha256(csv_path)
    row_sha = compute_csv_sha256(csv_path)
    row_count, first_ts, last_ts = _csv_row_count_and_window(csv_path)
    csv_mtime = csv_path.stat().st_mtime
    prov_mtime = prov_path.stat().st_mtime
    prov = json.loads(prov_path.read_text(encoding="utf-8"))

    result["csv_raw_sha256"] = raw_sha
    result["csv_row_sha256"] = row_sha
    result["csv_row_count"] = row_count
    result["csv_first_ts"] = first_ts
    result["csv_last_ts"] = last_ts
    result["csv_mtime"] = csv_mtime
    result["provenance_data_sha256"] = prov.get("data_sha256")
    result["provenance_candle_count"] = prov.get("candle_count")
    result["provenance_first_ts"] = prov.get("first_ts")
    result["provenance_last_ts"] = prov.get("last_ts")
    result["provenance_exported_at"] = prov.get("exported_at")
    result["provenance_mtime"] = prov_mtime
    result["row_sha_match"] = row_sha == prov.get("data_sha256")
    result["raw_sha_matches_provenance_data_sha"] = (
        raw_sha == prov.get("data_sha256")
    )
    result["row_count_match"] = row_count == prov.get("candle_count")
    result["first_ts_match"] = first_ts == prov.get("first_ts")
    result["last_ts_match"] = last_ts == prov.get("last_ts")
    result["bt_strict_preflight_pass"] = (
        bool(result["row_sha_match"])
        and bool(result["row_count_match"])
    )
    result["provenance_appears_stale"] = csv_mtime > prov_mtime
    return result


def diagnose(
    *,
    exports_dir: Path,
    instruments: tuple[str, ...] = DEFAULT_INSTRUMENTS,
) -> dict[str, Any]:
    per_instrument = [
        diagnose_instrument(instrument=p, exports_dir=exports_dir)
        for p in instruments
    ]
    all_pass = all(r["bt_strict_preflight_pass"] for r in per_instrument)
    all_fail = all(not r["bt_strict_preflight_pass"] for r in per_instrument)
    any_missing_csv = any(not r["csv_exists"] for r in per_instrument)
    any_missing_prov = any(not r["provenance_exists"] for r in per_instrument)
    any_stale = any(
        r.get("provenance_appears_stale") for r in per_instrument
    )
    return {
        "exports_dir": str(exports_dir),
        "instruments": list(instruments),
        "all_bt_strict_preflight_pass": all_pass,
        "all_bt_strict_preflight_fail": all_fail,
        "any_missing_csv": any_missing_csv,
        "any_missing_provenance": any_missing_prov,
        "any_provenance_stale_vs_csv_mtime": any_stale,
        "per_instrument": per_instrument,
        "diagnostic_disclaimer": (
            "Read-only diagnostic. Does NOT modify any export, "
            "provenance, or registry artifact. Does NOT approve any "
            "strategy. configs/approved_strategies.yaml remains "
            "approved: []."
        ),
    }


def render_md(obj: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Backtrader CAMPAIGN_002 H4 export — CSV/Provenance Mismatch Report")
    lines.append("")
    lines.append(f"**Exports dir:** `{obj['exports_dir']}`")
    lines.append("")
    lines.append(
        f"- all instruments BT-strict-preflight PASS: "
        f"**{obj['all_bt_strict_preflight_pass']}**"
    )
    lines.append(
        f"- all instruments BT-strict-preflight FAIL: "
        f"**{obj['all_bt_strict_preflight_fail']}**"
    )
    lines.append(f"- any CSV missing: {obj['any_missing_csv']}")
    lines.append(f"- any provenance missing: {obj['any_missing_provenance']}")
    lines.append(
        f"- any provenance stale vs CSV mtime: "
        f"{obj['any_provenance_stale_vs_csv_mtime']}"
    )
    lines.append("")
    lines.append("## Per-instrument detail")
    lines.append("")
    lines.append(
        "| instrument | csv? | prov? | row-sha match | row-count match | "
        "first-ts match | last-ts match | BT strict pass | prov stale? |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in obj["per_instrument"]:

        def _tick(v: Any) -> str:
            if v is True:
                return "✓"
            if v is False:
                return "✗"
            return "?"

        lines.append(
            f"| {r['instrument']} "
            f"| {_tick(r['csv_exists'])} "
            f"| {_tick(r['provenance_exists'])} "
            f"| {_tick(r['row_sha_match'])} "
            f"| {_tick(r['row_count_match'])} "
            f"| {_tick(r['first_ts_match'])} "
            f"| {_tick(r['last_ts_match'])} "
            f"| {_tick(r['bt_strict_preflight_pass'])} "
            f"| {_tick(r['provenance_appears_stale'])} |"
        )
    lines.append("")
    lines.append("### Detailed shas (per instrument)")
    lines.append("")
    for r in obj["per_instrument"]:
        lines.append(f"**{r['instrument']}**")
        lines.append("")
        lines.append(
            f"- CSV raw sha256 (full file): "
            f"`{(r['csv_raw_sha256'] or '')[:16] or '(no CSV)'}…`"
        )
        lines.append(
            f"- CSV row-sha256 (data_adapter.compute_csv_sha256): "
            f"`{(r['csv_row_sha256'] or '')[:16] or '(no CSV)'}…`"
        )
        lines.append(
            f"- Provenance data_sha256: "
            f"`{(r['provenance_data_sha256'] or '')[:16] or '(no provenance)'}…`"
        )
        lines.append(
            f"- CSV row count: {r['csv_row_count']} "
            f"vs provenance candle_count: {r['provenance_candle_count']}"
        )
        lines.append(
            f"- CSV first_ts: `{r['csv_first_ts']}` "
            f"vs provenance: `{r['provenance_first_ts']}`"
        )
        lines.append(
            f"- CSV last_ts: `{r['csv_last_ts']}` "
            f"vs provenance: `{r['provenance_last_ts']}`"
        )
        lines.append(
            f"- provenance exported_at: `{r['provenance_exported_at']}`"
        )
        if r.get("notes"):
            lines.append(f"- notes: {r['notes']}")
        lines.append("")
    lines.append(obj["diagnostic_disclaimer"])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--exports-dir",
        default="research/lean_parity/exports/campaign_002_h4",
        type=Path,
    )
    ap.add_argument(
        "--instruments",
        nargs="*",
        default=list(DEFAULT_INSTRUMENTS),
    )
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    args = ap.parse_args(argv)

    if not args.exports_dir.exists():
        print(
            f"BLOCKED: exports-dir does not exist: {args.exports_dir}",
            file=sys.stderr,
        )
        return 2

    obj = diagnose(
        exports_dir=args.exports_dir,
        instruments=tuple(args.instruments),
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(obj, indent=2, default=str), encoding="utf-8"
    )
    args.out_md.write_text(render_md(obj), encoding="utf-8")
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    if obj["all_bt_strict_preflight_pass"]:
        print("status: ALL BT-STRICT PREFLIGHT PASS")
        return 0
    if obj["all_bt_strict_preflight_fail"]:
        print("status: ALL BT-STRICT PREFLIGHT FAIL (complete drift)")
        return 1
    print("status: MIXED — some instruments pass, some fail")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
