"""FRED OECD 3M interbank rate fetch (key-less public CSV) for the DEEP-history
robustness run only. The PRIMARY run reuses the cached frozen signal CSV.

NOTE: the JPY series ``IR3TIB01JPM156N`` is retired upstream (HTTP 404 as of this
sprint), so the deep run is necessarily JPY-excluded — handled by the caller.
No credentials; public endpoint.
"""
from __future__ import annotations

import io
import socket
import ssl
import urllib.request
from pathlib import Path

import pandas as pd


def _ssl_context() -> ssl.SSLContext | None:
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return None

# Same family as research.carry.carry_rates.RATE_SERIES, minus the retired JPY.
DEEP_SERIES: dict[str, str] = {
    "USD": "IR3TIB01USM156N",
    "EUR": "IR3TIB01EZM156N",
    "GBP": "IR3TIB01GBM156N",
    "AUD": "IR3TIB01AUM156N",
    "NZD": "IR3TIB01NZM156N",
    "CHF": "IR3TIB01CHM156N",
    "CAD": "IR3TIB01CAM156N",
}
_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
_UA = {"User-Agent": "Mozilla/5.0 (research; carry-diagnostic)"}


def fetch_deep_rates(out_dir: str | Path, fetched_on: str, timeout: int = 30) -> pd.DataFrame:
    """Fetch the reachable FRED series → month-start rate matrix; cache raw CSVs."""
    socket.setdefaulttimeout(timeout)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cols = {}
    for ccy, sid in DEEP_SERIES.items():
        req = urllib.request.Request(_URL.format(sid=sid), headers=_UA)
        text = urllib.request.urlopen(req, context=_ssl_context()).read().decode("utf-8", "replace")
        (out / f"{ccy}_{sid}.csv").write_text(text)
        df = pd.read_csv(io.StringIO(text))
        df.columns = ["date", "rate"]
        df["date"] = pd.to_datetime(df["date"])
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
        s = df.dropna().set_index("date")["rate"]
        s.index = s.index.to_period("M").to_timestamp()
        cols[ccy] = s
    mat = pd.DataFrame(cols).sort_index()
    (out / "_deep_rate_matrix.csv").write_text(mat.to_csv())
    return mat


def load_deep_rates(out_dir: str | Path) -> pd.DataFrame:
    mat = pd.read_csv(Path(out_dir) / "_deep_rate_matrix.csv", index_col=0, parse_dates=True)
    return mat
