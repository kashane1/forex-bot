#!/usr/bin/env python3
"""Backfill BTC/ETH derivatives (funding, perp OHLCV, index, basis, OI) — public only.

Canonical sources (geo-reachable, USD-quoted): Deribit for funding/index/perp-OHLCV;
OKX rubik for daily OI history. DRY-RUN by default; a real public fetch happens only
with ``--execute-public-fetch``. BTC/ETH perps only; no keys; no trading endpoints.

Normalized CSVs are written under a GITIGNORED backfill dir; only compact manifests
and a validation summary are committed. This script runs NO diagnostics and infers
NO edge.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from research.crypto.derivatives_backfill import (
    DERIBIT_CHART_1D_SPAN_MS,
    DERIBIT_CHART_1H_SPAN_MS,
    DERIBIT_FUNDING_SPAN_MS,
    chunk_time_windows,
)
from research.crypto.derivatives_models import compute_basis
from research.crypto.derivatives_registry import (
    perp_underlying,
    validate_perp,
    venue_symbol,
)
from research.crypto.derivatives_sources import (
    PUBLIC_BASE_URLS,
    UnsafeSourceError,
    assert_no_credentials_required,
    assert_public_url,
    parse_deribit_chart,
    parse_deribit_funding,
    parse_deribit_index_from_funding,
    parse_okx_oi_volume,
)
from research.crypto.derivatives_validation import (
    summarize,
    validate_funding,
    validate_mark_index,
    validate_open_interest,
    validate_perp_ohlcv,
)

BACKFILL_DIR = ROOT / "research" / "crypto" / "derivatives" / "backfill"  # gitignored
MANIFEST_DIR = ROOT / "research" / "crypto" / "derivatives" / "manifests" / "backfill"
SUMMARY_DIR = ROOT / "research" / "crypto" / "derivatives" / "summaries"
CLASSES = ("funding", "ohlcv_1h", "ohlcv_1d", "oi_daily")
REQUEST_DELAY_S = 0.15


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# --- Deribit fetchers (network) --------------------------------------------


def _deribit_get(client: Any, path: str, params: dict[str, Any]) -> Any:
    url = assert_public_url(PUBLIC_BASE_URLS["deribit"] + path)
    resp = client.get(url, params=params, timeout=30.0)
    resp.raise_for_status()
    return resp.json().get("result", [])


def fetch_funding(client: Any, canonical: str, start_ms: int, end_ms: int) -> dict[str, Any]:
    native = venue_symbol(canonical, "deribit")
    funding: list[Any] = []
    index: list[Any] = []
    for s, e in chunk_time_windows(start_ms, end_ms, DERIBIT_FUNDING_SPAN_MS):
        result = _deribit_get(
            client,
            "/api/v2/public/get_funding_rate_history",
            {"instrument_name": native, "start_timestamp": s, "end_timestamp": e},
        )
        funding.extend(parse_deribit_funding(result, canonical_id=canonical))
        index.extend(parse_deribit_index_from_funding(result, canonical_id=canonical))
        time.sleep(REQUEST_DELAY_S)
    return {"funding": _dedup_by_time(funding, "funding_time_utc"),
            "index": _dedup_by_time(index, "time_utc")}


def fetch_chart(
    client: Any, canonical: str, start_ms: int, end_ms: int, *, resolution: str, granularity: str, span_ms: int
) -> list[Any]:
    native = venue_symbol(canonical, "deribit")
    bars: list[Any] = []
    for s, e in chunk_time_windows(start_ms, end_ms, span_ms):
        result = _deribit_get(
            client,
            "/api/v2/public/get_tradingview_chart_data",
            {"instrument_name": native, "start_timestamp": s, "end_timestamp": e, "resolution": resolution},
        )
        if isinstance(result, dict):
            bars.extend(parse_deribit_chart(result, canonical_id=canonical, granularity=granularity))
        time.sleep(REQUEST_DELAY_S)
    return _dedup_by_time(bars, "time_utc")


def fetch_oi_daily(client: Any, canonical: str) -> list[Any]:
    base_ccy = perp_underlying(canonical).split("_")[0]  # BTC_USD -> BTC
    url = assert_public_url(PUBLIC_BASE_URLS["okx"] + "/api/v5/rubik/stat/contracts/open-interest-volume")
    resp = client.get(url, params={"ccy": base_ccy, "period": "1D"}, timeout=30.0)
    resp.raise_for_status()
    return parse_okx_oi_volume(resp.json(), canonical_id=canonical, interval="1D")


def _dedup_by_time(records: list[Any], attr: str) -> list[Any]:
    seen: set[Any] = set()
    out: list[Any] = []
    for r in sorted(records, key=lambda x: getattr(x, attr)):
        k = getattr(r, attr)
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


# --- plan / run -------------------------------------------------------------


def build_plan(instruments: list[str], classes: list[str], start: datetime, end: datetime) -> dict[str, Any]:
    s, e = _ms(start), _ms(end)
    return {
        "instruments": instruments,
        "classes": classes,
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "window_estimate": {
            "funding_chunks_per_instrument": len(chunk_time_windows(s, e, DERIBIT_FUNDING_SPAN_MS)),
            "ohlcv_1h_chunks_per_instrument": len(chunk_time_windows(s, e, DERIBIT_CHART_1H_SPAN_MS)),
            "ohlcv_1d_chunks_per_instrument": len(chunk_time_windows(s, e, DERIBIT_CHART_1D_SPAN_MS)),
        },
        "sources": {"funding/ohlcv/index": "deribit (USD)", "oi_daily": "okx-rubik (USD notional, aggregate)"},
        "backfill_dir": str(BACKFILL_DIR.relative_to(ROOT)),
    }


def run(args: argparse.Namespace, *, environ: dict[str, str] | None = None) -> dict[str, Any]:
    assert_no_credentials_required(environ if environ is not None else {})
    instruments = (
        ["BTC_PERP_USD", "ETH_PERP_USD"] if args.instrument == "all" else [validate_perp(args.instrument)]
    )
    for inst in instruments:
        validate_perp(inst)
    classes = args.classes.split(",")
    for c in classes:
        if c not in CLASSES:
            raise UnsafeSourceError(f"unknown class: {c}")
    start = _parse_dt(args.start)
    end = _parse_dt(args.end) if args.end else datetime.now(UTC)
    plan = build_plan(instruments, classes, start, end)

    if not args.execute_public_fetch:
        return {"status": "DRY_RUN", "plan": plan}

    import httpx

    batch_id = str(uuid.uuid4())
    validations: list[Any] = []
    per_class: dict[str, Any] = {}
    s_ms, e_ms = _ms(start), _ms(end)
    with httpx.Client() as client:
        for inst in instruments:
            inst_dir = BACKFILL_DIR / inst
            if "funding" in classes:
                fr = fetch_funding(client, inst, s_ms, e_ms)
                funding, index = fr["funding"], fr["index"]
                _write_csv(
                    inst_dir / "funding.csv",
                    ["time_utc", "funding_rate", "funding_interval_hours", "venue", "venue_symbol", "canonical_id"],
                    [{"time_utc": r.funding_time_utc.isoformat(), "funding_rate": r.funding_rate,
                      "funding_interval_hours": r.funding_interval_hours, "venue": r.venue,
                      "venue_symbol": r.venue_symbol, "canonical_id": r.canonical_id} for r in funding],
                )
                _write_csv(
                    inst_dir / "index_h1.csv",
                    ["time_utc", "index_close", "venue", "granularity", "canonical_id"],
                    [{"time_utc": r.time_utc.isoformat(), "index_close": r.index_close, "venue": r.venue,
                      "granularity": r.granularity, "canonical_id": r.canonical_id} for r in index],
                )
                validations += [validate_funding(funding), validate_mark_index(index)]
                per_class.setdefault(inst, {})["funding"] = len(funding)
                per_class[inst]["index"] = len(index)
            if "ohlcv_1h" in classes:
                bars = fetch_chart(client, inst, s_ms, e_ms, resolution="60", granularity="H1",
                                   span_ms=DERIBIT_CHART_1H_SPAN_MS)
                _write_ohlcv(inst_dir / "ohlcv_h1.csv", bars)
                validations.append(validate_perp_ohlcv(bars))
                per_class.setdefault(inst, {})["ohlcv_1h"] = len(bars)
                # basis from hourly perp close vs hourly index (if funding fetched)
                if "funding" in classes:
                    _write_basis(inst_dir / "basis_h1.csv", inst, bars, fr["index"])
            if "ohlcv_1d" in classes:
                bars = fetch_chart(client, inst, s_ms, e_ms, resolution="1D", granularity="D1",
                                   span_ms=DERIBIT_CHART_1D_SPAN_MS)
                _write_ohlcv(inst_dir / "ohlcv_d1.csv", bars)
                validations.append(validate_perp_ohlcv(bars))
                per_class.setdefault(inst, {})["ohlcv_1d"] = len(bars)
            if "oi_daily" in classes:
                oi = fetch_oi_daily(client, inst)
                _write_csv(
                    inst_dir / "oi_daily.csv",
                    ["time_utc", "open_interest_usd", "interval", "venue", "canonical_id"],
                    [{"time_utc": r.time_utc.isoformat(), "open_interest_usd": r.open_interest_usd,
                      "interval": r.interval, "venue": r.venue, "canonical_id": r.canonical_id} for r in oi],
                )
                validations.append(validate_open_interest(oi))
                per_class.setdefault(inst, {})["oi_daily"] = len(oi)

    summary = summarize(validations)
    manifest = {
        "batch_id": batch_id, "status": summary["overall_status"], "instruments": instruments,
        "classes": classes, "start_utc": start.isoformat(), "end_utc": end.isoformat(),
        "row_counts": per_class, "fetched_at_utc": datetime.now(UTC).isoformat(),
        "sources": plan["sources"], "backfill_dir": str(BACKFILL_DIR.relative_to(ROOT)),
    }
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    (MANIFEST_DIR / f"{batch_id}.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    (SUMMARY_DIR / "backfill_001_validation.json").write_text(
        json.dumps({"manifest": manifest, "validation": summary}, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {"status": "DONE", "manifest": manifest, "validation_overall": summary["overall_status"]}


def _write_ohlcv(path: Path, bars: list[Any]) -> None:
    _write_csv(
        path,
        ["time_utc", "open", "high", "low", "close", "volume", "venue", "venue_symbol", "granularity", "quote_ccy", "canonical_id"],
        [{"time_utc": b.time_utc.isoformat(), "open": b.open, "high": b.high, "low": b.low, "close": b.close,
          "volume": b.volume, "venue": b.venue, "venue_symbol": b.venue_symbol, "granularity": b.granularity,
          "quote_ccy": b.quote_ccy, "canonical_id": b.canonical_id} for b in bars],
    )


def _write_basis(path: Path, canonical: str, bars: list[Any], index_records: list[Any]) -> None:
    idx = {r.time_utc: r.index_close for r in index_records if r.index_close is not None}
    rows = []
    for b in bars:
        ix = idx.get(b.time_utc)
        if ix is None or ix <= 0:
            continue
        abs_, bps = compute_basis(b.close, ix)
        rows.append({"time_utc": b.time_utc.isoformat(), "perp_close": b.close, "index_close": ix,
                     "basis_abs": abs_, "basis_bps": bps, "canonical_id": canonical})
    _write_csv(path, ["time_utc", "perp_close", "index_close", "basis_abs", "basis_bps", "canonical_id"], rows)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--instrument", default="all", help="all | BTC_PERP_USD | ETH_PERP_USD")
    p.add_argument("--classes", default=",".join(CLASSES), help="comma list: " + ",".join(CLASSES))
    p.add_argument("--start", default="2020-01-01", help="ISO UTC start")
    p.add_argument("--end", default=None, help="ISO UTC end (default now)")
    p.add_argument("--execute-public-fetch", action="store_true", help="actually fetch (default dry-run)")
    return p


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
