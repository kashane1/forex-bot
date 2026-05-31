"""Yahoo Finance EOD ingestion for CME FX-futures continuous series.

Free, key-less public endpoint. Fetches daily closes for the continuous
front-month (`=F`) symbol of each contract, writes one raw CSV per currency
plus a provenance manifest (source URL, fetch range, row count, sha256 of the
content). Lookahead-safe by construction (EOD closes only). No credentials.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import socket
import ssl
import urllib.request
from pathlib import Path

from research.fx_futures.registry import FUTURES_CURRENCIES, yahoo_symbols

_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=30y"
_UA = {"User-Agent": "Mozilla/5.0 (research; carry-diagnostic)"}


def _ssl_context() -> ssl.SSLContext | None:
    """Prefer the certifi CA bundle (fixes macOS framework-Python SSL failures)."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return None


def _fetch_symbol(symbol: str, timeout: int = 30) -> list[tuple[str, float]]:
    """Return [(iso_date, close), ...] for a Yahoo `=F` continuous symbol."""
    socket.setdefaulttimeout(timeout)
    url = _BASE.format(sym=symbol)
    req = urllib.request.Request(url, headers=_UA)
    raw = urllib.request.urlopen(req, context=_ssl_context()).read()
    payload = json.loads(raw)
    result = payload["chart"]["result"][0]
    ts = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    rows: list[tuple[str, float]] = []
    for t, c in zip(ts, closes, strict=False):
        if c is None:
            continue
        d = _dt.datetime.utcfromtimestamp(t).date().isoformat()
        rows.append((d, float(c)))
    return rows


def _sha256_rows(rows: list[tuple[str, float]]) -> str:
    h = hashlib.sha256()
    for d, c in rows:
        h.update(f"{d},{c!r}\n".encode())
    return h.hexdigest()


def ingest(out_dir: str | Path, fetched_on: str) -> dict:
    """Fetch all seven contracts, write raw CSVs + provenance manifest.

    ``fetched_on`` is supplied by the caller (no wall-clock in library code) so
    the manifest is reproducible/auditable.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    symbols = yahoo_symbols()
    manifest: dict = {"source": "yahoo_finance_chart_v8", "fetched_on": fetched_on,
                      "endpoint": _BASE, "contracts": {}}
    for ccy in FUTURES_CURRENCIES:
        sym = symbols[ccy]
        rows = _fetch_symbol(sym)
        csv_path = out / f"{ccy}_{sym.replace('=', '_')}.csv"
        with csv_path.open("w") as f:
            f.write("date,close\n")
            for d, c in rows:
                f.write(f"{d},{c!r}\n")
        manifest["contracts"][ccy] = {
            "symbol": sym, "file": csv_path.name, "rows": len(rows),
            "first": rows[0][0], "last": rows[-1][0],
            "first_close": rows[0][1], "last_close": rows[-1][1],
            "sha256": _sha256_rows(rows),
        }
    (out / "provenance.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def load_raw(out_dir: str | Path) -> dict[str, list[tuple[str, float]]]:
    """Load previously-ingested raw CSVs: currency -> [(iso_date, close), ...]."""
    out = Path(out_dir)
    data: dict[str, list[tuple[str, float]]] = {}
    manifest = json.loads((out / "provenance.json").read_text())
    for ccy, meta in manifest["contracts"].items():
        rows: list[tuple[str, float]] = []
        for line in (out / meta["file"]).read_text().splitlines()[1:]:
            d, c = line.split(",")
            rows.append((d, float(c)))
        data[ccy] = rows
    return data
