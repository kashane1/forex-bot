"""Data loaders for the edge-discovery lab.

Reads CSVs only — never the broker, never the live DB. The CSV column
shape mirrors the existing committed sample
``research/d1_aggregation/sample_EUR_USD_H4_to_D1.csv`` so the lab's
loaders work against any candle CSV in that shape: aggregated D1AGG,
raw H4, or a future export.

A lab study should record which CSV path it used and the file's SHA-256
in the study summary, so anyone re-running the study can confirm they
ran against the same input bytes.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

REQUIRED_CANDLE_COLUMNS = frozenset(
    {"time", "bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"}
)
REQUIRED_EVENT_COLUMNS = frozenset({"time", "event_class"})


@dataclass(frozen=True)
class CandleSample:
    """A small candle frame plus enough provenance to reproduce a study.

    ``frame`` is indexed by UTC close timestamp and exposes mid open /
    high / low / close columns; bid/ask are kept too for cost overlays.
    ``source_sha256`` is the hash of the CSV file's bytes, so the study
    summary can record exactly which input was used.
    """

    instrument: str
    granularity: str
    frame: pd.DataFrame
    source_path: str
    source_sha256: str
    row_count: int


@dataclass(frozen=True)
class EventFixture:
    """A small event-timestamp table plus provenance.

    ``frame`` is indexed by UTC event timestamp. Columns: ``event_class``
    (string — e.g. ``NFP``, ``FOMC``, ``CPI``), and optionally any
    descriptive columns the source CSV carried.
    """

    frame: pd.DataFrame
    source_path: str
    source_sha256: str
    event_count: int
    classes: tuple[str, ...] = field(default=())


def _sha256_of_path(path: Path) -> str:
    sha = hashlib.sha256()
    sha.update(path.read_bytes())
    return sha.hexdigest()


def _infer_instrument(path: Path) -> str:
    """Pull an instrument code out of a filename like
    ``sample_EUR_USD_H4_to_D1.csv``. Returns ``UNKNOWN`` if no
    underscore-major pattern is found — the caller can override."""
    stem = path.stem
    parts = stem.split("_")
    for i in range(len(parts) - 1):
        a, b = parts[i], parts[i + 1]
        if len(a) == 3 and len(b) == 3 and a.isalpha() and b.isalpha() and a.isupper() and b.isupper():
            return f"{a}_{b}"
    return "UNKNOWN"


def load_candles_csv(
    path: str | Path,
    *,
    instrument: str | None = None,
    granularity: str | None = None,
) -> CandleSample:
    """Load a candle CSV in the d1_aggregation sample shape.

    The CSV must have a ``time`` column and bid/ask OHLC columns:
    ``bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c``. A
    ``granularity`` column is honored if present and ``granularity`` is
    not passed in. A mid OHLC is derived as ``(bid + ask) / 2`` at load
    time so downstream code can use ``frame['close']`` without per-row
    re-computation.

    The instrument is inferred from the filename (``EUR_USD`` from
    ``sample_EUR_USD_H4_to_D1.csv``) unless overridden. Pass
    ``instrument="..."`` to avoid ambiguity.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"candle CSV not found: {path}")
    df = pd.read_csv(path)
    missing = REQUIRED_CANDLE_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"candle CSV {path} missing required columns: {sorted(missing)}"
        )
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.sort_values("time").set_index("time")
    df["open"] = (df["bid_o"].astype(float) + df["ask_o"].astype(float)) / 2.0
    df["high"] = (df["bid_h"].astype(float) + df["ask_h"].astype(float)) / 2.0
    df["low"] = (df["bid_l"].astype(float) + df["ask_l"].astype(float)) / 2.0
    df["close"] = (df["bid_c"].astype(float) + df["ask_c"].astype(float)) / 2.0
    if granularity is None:
        if "granularity" in df.columns:
            uniq = df["granularity"].unique().tolist()
            if len(uniq) == 1:
                granularity = str(uniq[0])
        if granularity is None:
            granularity = "UNKNOWN"
    resolved_instrument = instrument or _infer_instrument(path)
    return CandleSample(
        instrument=resolved_instrument,
        granularity=granularity,
        frame=df,
        source_path=str(path),
        source_sha256=_sha256_of_path(path),
        row_count=len(df),
    )


def load_event_fixture(path: str | Path) -> EventFixture:
    """Load an event CSV with ``time`` and ``event_class`` columns.

    Extra descriptive columns are kept as-is. ``time`` is parsed as
    UTC. Duplicates on the (time, event_class) key are dropped silently
    — the lab study reports the deduplicated count and the source hash.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"event CSV not found: {path}")
    df = pd.read_csv(path)
    missing = REQUIRED_EVENT_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"event CSV {path} missing required columns: {sorted(missing)}"
        )
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df["event_class"] = df["event_class"].astype(str)
    df = df.drop_duplicates(subset=["time", "event_class"], keep="first")
    df = df.sort_values("time").set_index("time")
    classes = tuple(sorted(df["event_class"].unique().tolist()))
    return EventFixture(
        frame=df,
        source_path=str(path),
        source_sha256=_sha256_of_path(path),
        event_count=len(df),
        classes=classes,
    )
