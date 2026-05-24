"""Real-artifact loaders for the edge-discovery lab.

The synthetic-fixture loaders in ``loaders.py`` are intentionally
narrow — a CSV in / a small typed dataclass out. This module is the
hydrated-mode complement: it reads the local research artifacts that
land on the operator's machine via prior sprints (the gitignored H4
SQLite store, the committed CAMPAIGN_010-014 walk-forward result
JSONs, the committed per-fold per-pair summary JSONs and trade CSVs,
and the committed CAMPAIGN_014 event fixture JSON).

Each loader returns the same kind of typed sample/fixture as
``loaders.py`` so downstream studies can swap inputs without touching
their analysis code. Every loader either succeeds with `data_kind =
"real"` provenance, raises a friendly error pointing at the missing
artifact, or — for the H4 store specifically — returns ``None`` so the
caller can fall back to the synthetic fixture with explicit
``data_kind = "synthetic-fallback"`` provenance. Never silently
substitute.

No broker import. No `forex_bot.broker` / `forex_bot.loops` /
`forex_bot.approval` / `forex_bot.execution` dependency.
``tests/research/edge_discovery/test_isolation.py`` regression-guards
this.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from research.edge_discovery.loaders import (
    REQUIRED_CANDLE_COLUMNS,
    CandleSample,
    EventFixture,
)

# Worktree- and operator-aware default location of the canonical H4
# store. The lab tries each location in order; the first one that
# exists wins.
DEFAULT_H4_DB_FILENAME = "campaign_002.sqlite3"
EDGE_DISCOVERY_H4_DB_ENV = "EDGE_DISCOVERY_H4_DB"

# These are the seven majors the H4 universe always contains. Studies
# may restrict to a subset.
SEVEN_MAJORS = ("EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD")


# ---------------------------------------------------------------------------
# H4 SQLite store
# ---------------------------------------------------------------------------


def _candidate_h4_store_paths(repo_root: Path) -> list[Path]:
    """Build the ordered candidate-path list for the H4 store.

    Probed in order:

      1. ``$EDGE_DISCOVERY_H4_DB`` if the env var is set.
      2. ``<repo_root>/data/campaign_002.sqlite3`` — the path every
         CAMPAIGN_002+ config references and the location every prior
         sprint has used.
      3. ``<repo_root>/../../../data/campaign_002.sqlite3`` — the
         worktree-aware fallback: when the lab is being run from
         ``<repo>/.claude/worktrees/<name>/`` the canonical store
         usually lives in the original checkout's ``data/`` dir.

    The function does *not* check existence; that is the caller's
    job, so the caller can log which candidates it tried.
    """
    candidates: list[Path] = []
    env_path = os.environ.get(EDGE_DISCOVERY_H4_DB_ENV)
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(repo_root / "data" / DEFAULT_H4_DB_FILENAME)
    # Two levels up from .claude/worktrees/<name>/ → the original
    # checkout's data/ dir.
    if ".claude" in repo_root.parts and "worktrees" in repo_root.parts:
        idx = repo_root.parts.index(".claude")
        original_root = Path(*repo_root.parts[:idx])
        candidates.append(original_root / "data" / DEFAULT_H4_DB_FILENAME)
    return candidates


def resolve_h4_store_path(repo_root: Path) -> Path | None:
    """Return the first existing candidate path, or ``None`` if none
    of them resolves.

    Callers should treat ``None`` as "real H4 store unavailable; fall
    back to the synthetic fixture and tag the provenance
    ``synthetic-fallback``". Callers should NOT raise — the absence is
    expected for a fresh git clone.
    """
    for cand in _candidate_h4_store_paths(repo_root):
        if cand.is_file():
            return cand
    return None


def _sha256_of_path(path: Path, *, max_bytes: int = 16 * 1024 * 1024) -> str:
    """SHA-256 of file bytes up to ``max_bytes``.

    The H4 SQLite store is ~110 MB; hashing the whole file on every
    study run is slow. We hash a header window so the provenance can
    still detect "different bytes" cheaply. For artifact-shaped JSON /
    CSV files (small), call this with the default and the full file is
    hashed.
    """
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        remaining = max_bytes
        while remaining > 0:
            chunk = fh.read(min(remaining, 1024 * 1024))
            if not chunk:
                break
            sha.update(chunk)
            remaining -= len(chunk)
    return sha.hexdigest()


def load_h4_candles_from_sqlite(
    db_path: str | Path,
    instrument: str,
    *,
    from_time: str | None = None,
    to_time: str | None = None,
) -> CandleSample:
    """Load completed H4 bars for one instrument from the canonical
    SQLite store and return them in the same ``CandleSample`` shape as
    ``loaders.load_candles_csv``.

    The query reads only ``completed = 1`` candles with
    ``granularity = 'H4'``, projects bid/ask OHLC, and derives the
    mid OHLC (``(bid + ask) / 2``) at load time — matching the CSV
    loader's behavior so downstream code is shape-identical regardless
    of source.

    Raises ``FileNotFoundError`` if the DB does not exist (the caller
    should have used ``resolve_h4_store_path`` and handled ``None``
    before calling this) and ``ValueError`` if the requested
    instrument has zero H4 rows in the store.
    """
    db_path = Path(db_path)
    if not db_path.is_file():
        raise FileNotFoundError(f"H4 SQLite store not found: {db_path}")
    if instrument not in SEVEN_MAJORS:
        # Soft-allow other instruments — the caller may have a reason
        # — but warn via the row-count check below.
        pass

    query = (
        "SELECT time, bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c, volume "
        "FROM candles "
        "WHERE instrument = ? AND granularity = 'H4' AND complete = 1"
    )
    params: list[str] = [instrument]
    if from_time is not None:
        query += " AND time >= ?"
        params.append(from_time)
    if to_time is not None:
        query += " AND time <= ?"
        params.append(to_time)
    query += " ORDER BY time ASC"

    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        df = pd.read_sql_query(query, conn, params=params)
    if df.empty:
        raise ValueError(
            f"H4 SQLite store at {db_path} has zero completed H4 rows for "
            f"instrument {instrument!r} in the requested range "
            f"[{from_time!r}, {to_time!r}]."
        )
    df["time"] = pd.to_datetime(df["time"], utc=True)
    for col in ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"):
        df[col] = df[col].astype(float)
    # Cross-check the projection matches the CSV loader's contract
    # before we set_index and drop ``time`` from columns. ``time`` is
    # part of REQUIRED_CANDLE_COLUMNS so check pre-index.
    missing = REQUIRED_CANDLE_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"H4 SQLite frame for {instrument} missing required columns after "
            f"projection: {sorted(missing)}"
        )
    df = df.sort_values("time").set_index("time")
    df["open"] = (df["bid_o"] + df["ask_o"]) / 2.0
    df["high"] = (df["bid_h"] + df["ask_h"]) / 2.0
    df["low"] = (df["bid_l"] + df["ask_l"]) / 2.0
    df["close"] = (df["bid_c"] + df["ask_c"]) / 2.0
    return CandleSample(
        instrument=instrument,
        granularity="H4",
        frame=df,
        source_path=str(db_path),
        source_sha256=_sha256_of_path(db_path),
        row_count=len(df),
    )


# ---------------------------------------------------------------------------
# CAMPAIGN_010-014 walk-forward result roll-ups
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CampaignWalkForwardResult:
    """One campaign's committed walk-forward result roll-up.

    Mirrors the on-disk JSON schema:

      * ``plan`` — the authoritative fold layout (universe range,
        rolling vs anchored, per-fold train/validation/test windows).
      * ``fold_metrics`` — list of per-fold aggregates.
      * ``aggregate`` — across-folds summary.
      * ``overall_verdict`` — ``REJECT`` / ``DIAGNOSTIC`` / etc.
      * ``strategy_evidence`` — ``False`` for every campaign on this
        branch (every CAMPAIGN_010-014 row is non-approval).
    """

    campaign_name: str
    source_path: str
    source_sha256: str
    plan: dict[str, object]
    fold_metrics: list[dict[str, object]]
    aggregate: dict[str, object]
    overall_verdict: str
    strategy_evidence: bool


def load_campaign_walk_forward_result(
    campaign_dir: str | Path,
) -> CampaignWalkForwardResult:
    """Load ``<campaign_dir>/walk_forward/results.json`` into a typed
    dataclass.

    ``campaign_dir`` is the campaign root, e.g.
    ``backtests/CAMPAIGN_014_calendar_event_window_anomaly``. The
    function does not interpret the result; the lab is consuming the
    campaign's verdict, not re-deriving one.
    """
    campaign_dir = Path(campaign_dir)
    results_path = campaign_dir / "walk_forward" / "results.json"
    if not results_path.is_file():
        raise FileNotFoundError(
            f"campaign walk_forward results.json not found: {results_path}"
        )
    with results_path.open(encoding="utf-8") as fh:
        d = json.load(fh)
    name = campaign_dir.name
    return CampaignWalkForwardResult(
        campaign_name=name,
        source_path=str(results_path),
        source_sha256=_sha256_of_path(results_path),
        plan=d.get("plan", {}),
        fold_metrics=list(d.get("fold_metrics", [])),
        aggregate=dict(d.get("aggregate", {})),
        overall_verdict=str(d.get("overall_verdict", "")),
        strategy_evidence=bool(d.get("strategy_evidence", False)),
    )


# ---------------------------------------------------------------------------
# Per-fold per-pair summary JSONs (280 files for CAMPAIGN_010-014)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FoldPairSummary:
    """One ``fold_NN_<PAIR>_summary.json`` decoded into the row shape
    studies want.

    Studies aggregating across folds and pairs assemble a list of
    these and then turn them into a DataFrame via
    ``fold_pair_summaries_to_frame``.
    """

    campaign_name: str
    fold_index: int
    instrument: str
    strategy_name: str
    strategy_version: str
    granularity: str
    from_time: str
    to_time: str
    config_hash: str
    data_request_hash: str
    metrics: dict[str, float]
    source_path: str


def _parse_fold_index(fold_dir_name: str) -> int:
    # "fold_03" -> 3
    return int(fold_dir_name.split("_", 1)[1])


def load_campaign_fold_pair_summaries(
    campaign_dir: str | Path,
) -> list[FoldPairSummary]:
    """Walk ``<campaign_dir>/folds/fold_NN/`` and load every
    ``fold_NN_<PAIR>_summary.json`` into a typed list.

    Order: ascending fold index, then alphabetical instrument. Skips
    missing fold dirs silently — a campaign with fewer folds (rare;
    CAMPAIGN_010-014 all have 8) still loads.
    """
    campaign_dir = Path(campaign_dir)
    folds_dir = campaign_dir / "folds"
    if not folds_dir.is_dir():
        raise FileNotFoundError(f"campaign folds dir not found: {folds_dir}")
    out: list[FoldPairSummary] = []
    name = campaign_dir.name
    for fold_path in sorted(folds_dir.iterdir()):
        if not fold_path.is_dir() or not fold_path.name.startswith("fold_"):
            continue
        fold_idx = _parse_fold_index(fold_path.name)
        for summary_path in sorted(fold_path.glob(f"{fold_path.name}_*_summary.json")):
            with summary_path.open(encoding="utf-8") as fh:
                d = json.load(fh)
            out.append(
                FoldPairSummary(
                    campaign_name=name,
                    fold_index=fold_idx,
                    instrument=str(d.get("instrument", "")),
                    strategy_name=str(d.get("strategy_name", "")),
                    strategy_version=str(d.get("strategy_version", "")),
                    granularity=str(d.get("granularity", "")),
                    from_time=str(d.get("from_time", "")),
                    to_time=str(d.get("to_time", "")),
                    config_hash=str(d.get("config_hash", "")),
                    data_request_hash=str(d.get("data_request_hash", "")),
                    metrics=dict(d.get("metrics", {})),
                    source_path=str(summary_path),
                )
            )
    return out


def fold_pair_summaries_to_frame(summaries: Iterable[FoldPairSummary]) -> pd.DataFrame:
    """Flatten a list of ``FoldPairSummary`` into one DataFrame.

    Columns: ``campaign_name``, ``fold_index``, ``instrument``,
    ``strategy_name``, ``strategy_version``, ``granularity``,
    ``from_time``, ``to_time``, ``config_hash``, ``data_request_hash``,
    plus every key inside the ``metrics`` dict (lifted to top-level
    columns prefixed with ``metric_``). Missing metrics become NaN.
    """
    rows: list[dict[str, object]] = []
    for s in summaries:
        row: dict[str, object] = {
            "campaign_name": s.campaign_name,
            "fold_index": s.fold_index,
            "instrument": s.instrument,
            "strategy_name": s.strategy_name,
            "strategy_version": s.strategy_version,
            "granularity": s.granularity,
            "from_time": s.from_time,
            "to_time": s.to_time,
            "config_hash": s.config_hash,
            "data_request_hash": s.data_request_hash,
        }
        for k, v in s.metrics.items():
            row[f"metric_{k}"] = v
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Per-fold per-pair trades CSVs
# ---------------------------------------------------------------------------


CAMPAIGN_TRADES_COLUMNS = (
    "instrument",
    "side",
    "units",
    "entry_time",
    "exit_time",
    "entry_price",
    "exit_price",
    "stop_price",
    "pnl",
    "r_multiple",
    "bars_held",
    "spread_paid_pips",
    "exit_reason",
    "fill_timing",
)


def load_campaign_trades(
    campaign_dir: str | Path,
    *,
    instruments: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Concatenate every ``fold_NN_<PAIR>_trades.csv`` under
    ``<campaign_dir>/folds/`` into one DataFrame.

    Adds ``campaign_name`` and ``fold_index`` columns. Each trade keeps
    its original schema (``instrument, side, units, entry_time,
    exit_time, entry_price, exit_price, stop_price, pnl, r_multiple,
    bars_held, spread_paid_pips, exit_reason, fill_timing``). Returns
    an empty DataFrame (with the columns above plus
    ``campaign_name``/``fold_index``) if no trade files are found.

    ``instruments`` (optional) restricts the read to a subset.
    """
    campaign_dir = Path(campaign_dir)
    folds_dir = campaign_dir / "folds"
    if not folds_dir.is_dir():
        raise FileNotFoundError(f"campaign folds dir not found: {folds_dir}")
    instruments_filter = frozenset(instruments) if instruments is not None else None
    pieces: list[pd.DataFrame] = []
    name = campaign_dir.name
    for fold_path in sorted(folds_dir.iterdir()):
        if not fold_path.is_dir() or not fold_path.name.startswith("fold_"):
            continue
        fold_idx = _parse_fold_index(fold_path.name)
        for trades_path in sorted(fold_path.glob(f"{fold_path.name}_*_trades.csv")):
            df = pd.read_csv(trades_path)
            if instruments_filter is not None:
                df = df[df["instrument"].isin(instruments_filter)]
            if df.empty:
                continue
            df = df.assign(campaign_name=name, fold_index=fold_idx)
            pieces.append(df)
    if not pieces:
        return pd.DataFrame(columns=list(CAMPAIGN_TRADES_COLUMNS) + ["campaign_name", "fold_index"])
    out = pd.concat(pieces, ignore_index=True)
    out["entry_time"] = pd.to_datetime(out["entry_time"], utc=True)
    out["exit_time"] = pd.to_datetime(out["exit_time"], utc=True)
    out["r_multiple"] = out["r_multiple"].astype(float)
    return out


# ---------------------------------------------------------------------------
# CAMPAIGN_014 event fixture (JSON)
# ---------------------------------------------------------------------------


def load_event_fixture_json(path: str | Path) -> EventFixture:
    """Load the CAMPAIGN_014 calendar event fixture JSON into the
    ``EventFixture`` shape the existing studies already use.

    The JSON's schema (``schema_version =
    campaign_014.event_fixture.v1``) carries an array of events with
    ``{event_id, event_class, event_time_utc}``. This loader flattens
    them into a DataFrame indexed by ``event_time_utc`` (UTC tz-aware)
    with columns ``event_class`` and ``event_id``, so an event-window
    study can substitute the JSON fixture in for the synthetic CSV
    fixture without changing its analysis code.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"event fixture JSON not found: {path}")
    with path.open(encoding="utf-8") as fh:
        d = json.load(fh)
    events = d.get("events", [])
    if not events:
        raise ValueError(
            f"event fixture JSON at {path} contains an empty events array"
        )
    df = pd.DataFrame(events)
    if "event_time_utc" not in df.columns or "event_class" not in df.columns:
        raise ValueError(
            f"event fixture JSON at {path} missing required keys "
            f"event_time_utc / event_class"
        )
    df["time"] = pd.to_datetime(df["event_time_utc"], utc=True)
    df["event_class"] = df["event_class"].astype(str)
    df = df.drop_duplicates(subset=["time", "event_class"], keep="first")
    df = df.sort_values("time").set_index("time")
    keep_cols = [c for c in ("event_class", "event_id") if c in df.columns]
    classes = tuple(sorted(df["event_class"].unique().tolist()))
    return EventFixture(
        frame=df[keep_cols].copy(),
        source_path=str(path),
        source_sha256=_sha256_of_path(path),
        event_count=len(df),
        classes=classes,
    )


# ---------------------------------------------------------------------------
# Provenance helper for real-data studies
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StudyInput:
    """One artifact a real-data study consumed."""

    kind: str  # "h4_sqlite_store" | "campaign_walk_forward_results" | "campaign_fold_summaries" | "campaign_trades" | "event_fixture_json" | "candle_csv" | "event_csv"
    path: str
    sha256: str
    rows: int | None = None
    extra: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class StudyProvenance:
    """Provenance block every real-data study output must carry.

    See ``docs/research/EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md`` §6
    for the binding requirement list."""

    data_kind: str  # "real" or "synthetic-fallback"
    inputs: list[StudyInput]
    date_coverage: dict[str, str]  # {"start_utc": "...", "end_utc": "..."}
    pair_universe: list[str]
    limitations: list[str]
    exploratory_only: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "data_kind": self.data_kind,
            "inputs": [
                {
                    "kind": i.kind,
                    "path": i.path,
                    "sha256": i.sha256,
                    "rows": i.rows,
                    **({"extra": i.extra} if i.extra else {}),
                }
                for i in self.inputs
            ],
            "date_coverage": dict(self.date_coverage),
            "pair_universe": list(self.pair_universe),
            "limitations": list(self.limitations),
            "exploratory_only": bool(self.exploratory_only),
        }


def assert_real_data_kind(provenance: StudyProvenance) -> None:
    """Helper for tests: assert the provenance was actually populated
    with real artifacts and not silently filled with the fallback."""
    if provenance.data_kind not in ("real", "synthetic-fallback"):
        raise ValueError(
            f"unrecognized provenance data_kind {provenance.data_kind!r}; "
            "expected 'real' or 'synthetic-fallback'"
        )
    if provenance.data_kind == "real" and not provenance.inputs:
        raise ValueError(
            "provenance claims data_kind='real' but no inputs were recorded"
        )
    if not provenance.exploratory_only:
        raise ValueError(
            "lab provenance MUST set exploratory_only=True; the lab cannot "
            "produce strategy evidence"
        )
