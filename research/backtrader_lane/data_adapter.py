"""Backtrader-compatible adapter over the existing Lean H4 export CSVs.

This module is the *only* path a Backtrader Cerebro takes to local
candle data inside this repo. It reads:

  research/lean_parity/exports/campaign_002_h4/<INSTRUMENT>_H4_lean.csv
  research/lean_parity/exports/campaign_002_h4/<INSTRUMENT>_H4_lean.provenance.json

(both gitignored bulk data + a committed sidecar; format defined in
`research/lean_parity/lean_h4_export_format.md`), validates the CSV's
SHA-256 against the committed provenance JSON, and returns a pandas
DataFrame + per-bar `half_spread` series suitable for a custom
Backtrader feed.

No network. No broker. No credential read. No edit to the source CSVs.

`strategy_evidence: false`.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPORT_DIR = _REPO_ROOT / "research" / "lean_parity" / "exports" / "campaign_002_h4"

# The CSV column order we consume. Mirrors `lean_h4_export_format.md`
# exactly; the loader fails loud if the header drifts.
EXPECTED_CSV_HEADER: tuple[str, ...] = (
    "time",
    "bid_open",
    "bid_high",
    "bid_low",
    "bid_close",
    "ask_open",
    "ask_high",
    "ask_low",
    "ask_close",
    "volume",
)

# Bars must be exactly 4h apart for completed-H4 candles. The store
# already excludes incomplete candles; we treat any gap > 4h as a
# weekend / market-closed gap (allowed) and any gap < 4h as malformed.
H4_SECONDS = 4 * 3600


class CandleProvenanceError(RuntimeError):
    """Raised when the committed `*.provenance.json` cannot validate a
    CSV — either the sha256 differs or the row count differs from the
    sidecar's expectation. A clean blocker, not a verifier bug."""


class CandleSchemaError(RuntimeError):
    """Raised when the CSV header / column ordering does not match the
    documented Lean H4 export format."""


@dataclass(frozen=True)
class CandleProvenance:
    """A typed view of one `*.provenance.json` sidecar."""

    instrument: str
    granularity: str
    source: str
    requested_from: str
    requested_to: str
    candle_count: int
    first_ts: str
    last_ts: str
    data_sha256: str
    campaign_002_data_request_hash: str
    lean_csv: str
    exported_by: str
    exported_at: str
    note: str = ""

    @classmethod
    def from_json(cls, path: Path) -> CandleProvenance:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            instrument=raw["instrument"],
            granularity=raw["granularity"],
            source=raw["source"],
            requested_from=raw["requested_from"],
            requested_to=raw["requested_to"],
            candle_count=int(raw["candle_count"]),
            first_ts=raw["first_ts"],
            last_ts=raw["last_ts"],
            data_sha256=raw["data_sha256"],
            campaign_002_data_request_hash=raw["campaign_002_data_request_hash"],
            lean_csv=raw["lean_csv"],
            exported_by=raw["exported_by"],
            exported_at=raw["exported_at"],
            note=raw.get("note", ""),
        )


@dataclass(frozen=True)
class CandleAdapterResult:
    """One instrument's worth of Backtrader-ready candles.

    `mid_df` has the OHLCV-named columns Backtrader's `PandasData` needs,
    indexed by tz-aware UTC datetimes (the bar's open time, per the
    Lean export contract). `bid_ohlc_df` and `ask_ohlc_df` carry the
    raw bid/ask separately so the runner can compute a faithful slippage
    if it wants to (the default lane uses `half_spread_close`).
    """

    instrument: str
    provenance: CandleProvenance
    csv_sha256: str
    mid_df: pd.DataFrame
    bid_ohlc_df: pd.DataFrame
    ask_ohlc_df: pd.DataFrame
    half_spread_close: pd.Series
    first_ts: datetime
    last_ts: datetime
    bar_count: int
    approximation_flags: list[str] = field(default_factory=list)


def _parse_csv_time(raw: str) -> datetime:
    """Strict ISO-8601 with UTC offset, matching what the exporter writes."""

    s = raw.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    parsed = datetime.fromisoformat(s)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _row_to_bytes(row: list[str]) -> bytes:
    """Match `scripts/export_lean_parity_data.py`'s hashing convention:
    `"|".join(row).encode("utf-8")` per row in time-sorted order."""

    return ("|".join(row)).encode("utf-8")


def compute_csv_sha256(csv_path: Path) -> str:
    """Reproduce the sha256 that the exporter wrote into provenance.

    The exporter hashes the row strings (joined by `|`) in time-sorted
    order — we replicate that exactly so a re-export bit-matches and we
    can detect any drift from the committed sidecar value.
    """

    rows: list[tuple[str, list[str]]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or tuple(reader.fieldnames) != EXPECTED_CSV_HEADER:
            raise CandleSchemaError(
                f"CSV header mismatch in {csv_path}: "
                f"got {reader.fieldnames!r}, expected {list(EXPECTED_CSV_HEADER)!r}"
            )
        for row in reader:
            time_key = row["time"]
            ordered = [row[col] for col in EXPECTED_CSV_HEADER]
            rows.append((time_key, ordered))
    rows.sort(key=lambda kv: kv[0])
    hasher = hashlib.sha256()
    for _, ordered in rows:
        hasher.update(_row_to_bytes(ordered))
    return hasher.hexdigest()


def load_candles(
    instrument: str,
    export_dir: Path = DEFAULT_EXPORT_DIR,
    *,
    strict: bool = True,
) -> CandleAdapterResult:
    """Load one instrument's CSV + provenance and return a
    `CandleAdapterResult`.

    Raises:
        FileNotFoundError: CSV or provenance JSON missing.
        CandleSchemaError: CSV column ordering wrong.
        CandleProvenanceError: sha256 / count drift versus the
            committed sidecar (only when ``strict=True``).
        ValueError: bar ordering / OHLC invariants violated.
    """

    csv_path = export_dir / f"{instrument}_H4_lean.csv"
    prov_path = export_dir / f"{instrument}_H4_lean.provenance.json"
    if not prov_path.exists():
        raise FileNotFoundError(
            f"Provenance sidecar not found at {prov_path}. The CSVs are "
            "gitignored regenerable bulk data — regenerate with "
            "scripts/export_lean_parity_data.py."
        )
    provenance = CandleProvenance.from_json(prov_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV not found at {csv_path}. The Lean parity export CSVs "
            "are gitignored regenerable bulk data — see "
            "research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md."
        )

    csv_sha = compute_csv_sha256(csv_path)
    if strict and csv_sha != provenance.data_sha256:
        raise CandleProvenanceError(
            f"sha256 drift for {instrument}: csv={csv_sha[:12]}…, "
            f"provenance={provenance.data_sha256[:12]}…"
        )

    times: list[datetime] = []
    mid_open: list[float] = []
    mid_high: list[float] = []
    mid_low: list[float] = []
    mid_close: list[float] = []
    bid_o: list[float] = []
    bid_h: list[float] = []
    bid_l: list[float] = []
    bid_c: list[float] = []
    ask_o: list[float] = []
    ask_h: list[float] = []
    ask_l: list[float] = []
    ask_c: list[float] = []
    half_spread_close: list[float] = []
    volumes: list[int] = []

    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or tuple(reader.fieldnames) != EXPECTED_CSV_HEADER:
            raise CandleSchemaError(
                f"CSV header mismatch in {csv_path}: "
                f"got {reader.fieldnames!r}, expected {list(EXPECTED_CSV_HEADER)!r}"
            )
        for row in reader:
            t = _parse_csv_time(row["time"])
            bo, bh, bl, bc = (
                float(row["bid_open"]),
                float(row["bid_high"]),
                float(row["bid_low"]),
                float(row["bid_close"]),
            )
            ao, ah, al, ac = (
                float(row["ask_open"]),
                float(row["ask_high"]),
                float(row["ask_low"]),
                float(row["ask_close"]),
            )
            o = (bo + ao) / 2.0
            h = (bh + ah) / 2.0
            lo = (bl + al) / 2.0
            c = (bc + ac) / 2.0
            if not (lo <= o <= h and lo <= c <= h):
                raise ValueError(
                    f"mid OHLC invariant broken at {t.isoformat()} for {instrument}: "
                    f"o={o} h={h} l={lo} c={c}"
                )
            times.append(t)
            mid_open.append(o)
            mid_high.append(h)
            mid_low.append(lo)
            mid_close.append(c)
            bid_o.append(bo)
            bid_h.append(bh)
            bid_l.append(bl)
            bid_c.append(bc)
            ask_o.append(ao)
            ask_h.append(ah)
            ask_l.append(al)
            ask_c.append(ac)
            half_spread_close.append((ac - bc) / 2.0)
            volumes.append(int(row.get("volume", 0) or 0))

    if len(times) == 0:
        raise ValueError(f"empty CSV at {csv_path}")
    if strict and len(times) != provenance.candle_count:
        raise CandleProvenanceError(
            f"row count drift for {instrument}: csv={len(times)}, "
            f"provenance={provenance.candle_count}"
        )

    # Monotonic time ordering + no sub-4h gaps.
    for prev, curr in zip(times, times[1:], strict=False):
        if curr <= prev:
            raise ValueError(
                f"non-monotonic timestamps in {csv_path}: {prev.isoformat()} → {curr.isoformat()}"
            )
        gap = (curr - prev).total_seconds()
        if gap < H4_SECONDS:
            raise ValueError(
                f"sub-H4 gap in {csv_path}: {prev.isoformat()} → {curr.isoformat()} ({gap}s)"
            )

    mid_df = pd.DataFrame(
        {
            "open": mid_open,
            "high": mid_high,
            "low": mid_low,
            "close": mid_close,
            "volume": volumes,
        },
        index=pd.DatetimeIndex(times, name="time"),
    )
    bid_df = pd.DataFrame(
        {"open": bid_o, "high": bid_h, "low": bid_l, "close": bid_c},
        index=mid_df.index,
    )
    ask_df = pd.DataFrame(
        {"open": ask_o, "high": ask_h, "low": ask_l, "close": ask_c},
        index=mid_df.index,
    )
    half_spread = pd.Series(half_spread_close, index=mid_df.index, name="half_spread_close")

    approximations: list[str] = []
    # Mid prices are derived; this is an explicit approximation.
    approximations.append(
        "MID_OHLC_DERIVED: mid OHLC computed as (bid + ask) / 2 per OHLC component; "
        "the Backtrader feed sees mid only, with half-spread carried separately."
    )
    # Bar timestamp is the OPEN time per the Lean export contract.
    approximations.append(
        "BAR_OPEN_TIMESTAMP: index is the bar OPEN time (17:00-NY aligned). The "
        "Backtrader strategy must remember that signals fire on the bar whose "
        "open is the index value."
    )
    # Half-spread close used as the per-bar slippage proxy.
    approximations.append(
        "HALF_SPREAD_CLOSE: per-bar half-spread carried at bar close only. Intra-bar "
        "spread dynamics (open/high/low spread vs close spread) are not modelled."
    )

    return CandleAdapterResult(
        instrument=instrument,
        provenance=provenance,
        csv_sha256=csv_sha,
        mid_df=mid_df,
        bid_ohlc_df=bid_df,
        ask_ohlc_df=ask_df,
        half_spread_close=half_spread,
        first_ts=times[0],
        last_ts=times[-1],
        bar_count=len(times),
        approximation_flags=approximations,
    )


def available_instruments(export_dir: Path = DEFAULT_EXPORT_DIR) -> list[str]:
    """Return the instruments whose provenance JSON is present.

    Used by the runner's preflight to report BLOCKED with a clean
    explanation when a CSV is missing locally.
    """

    if not export_dir.exists():
        return []
    out: list[str] = []
    for path in sorted(export_dir.glob("*_H4_lean.provenance.json")):
        instrument = path.name.removesuffix("_H4_lean.provenance.json")
        if (export_dir / f"{instrument}_H4_lean.csv").exists():
            out.append(instrument)
    return out


def expected_instruments(export_dir: Path = DEFAULT_EXPORT_DIR) -> list[str]:
    """Return instruments whose committed provenance sidecar exists,
    regardless of whether the gitignored CSV is locally present."""

    if not export_dir.exists():
        return []
    out: list[str] = []
    for path in sorted(export_dir.glob("*_H4_lean.provenance.json")):
        instrument = path.name.removesuffix("_H4_lean.provenance.json")
        out.append(instrument)
    return out


def manifest_for(result: CandleAdapterResult) -> dict[str, Any]:
    """A compact dict used by the runner's manifest. Mirrors the
    provenance JSON but adds the in-memory bar count and approximations."""

    return {
        "instrument": result.instrument,
        "granularity": result.provenance.granularity,
        "source": result.provenance.source,
        "first_ts": result.first_ts.isoformat(),
        "last_ts": result.last_ts.isoformat(),
        "bar_count": result.bar_count,
        "csv_sha256": result.csv_sha256,
        "provenance_data_sha256": result.provenance.data_sha256,
        "provenance_campaign_002_data_request_hash": (
            result.provenance.campaign_002_data_request_hash
        ),
        "approximation_flags": list(result.approximation_flags),
    }
