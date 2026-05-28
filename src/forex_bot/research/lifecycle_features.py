"""Forward-looking lifecycle feature-capture schema for future campaigns.

Where `trade_lifecycle.TradeLifecycleRecord` *loads/normalizes existing* trade
artifacts, this module defines the richer schema future campaign trade writers
should **emit** so stop/entry/exit lifecycle quality can be diagnosed without a
rebuild: MFE/MAE, stop geometry, ATR/spread context, and HTF signal features.

Design rules:
  * Every field except `campaign_id` is **optional**; missingness is explicit
    (``None``) and counted by `missing_field_counts` — never fabricated.
  * Stable CSV column order (`CSV_COLUMNS`) so future writers and downstream
    loaders agree without negotiation.
  * R is the **pair-agnostic, price-based** convention (`price_based_r`): R = −1
    at the initial stop for every instrument, including JPY/USD-base pairs. This
    deliberately fixes the C022 exporter quirk documented in
    `docs/research/C022_R_MULTIPLE_CONVENTION_AUDIT.md` going forward.

This module is research/diagnostics scaffolding. It approves nothing, changes no
verdict, and is not imported by any broker/executor/live path.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, fields
from datetime import datetime
from pathlib import Path

__all__ = [
    "CSV_COLUMNS",
    "LifecycleFeatureRecord",
    "derive_stop_distance_pips",
    "missing_field_counts",
    "pip_size",
    "price_based_r",
    "record_from_trade_row",
    "records_from_trade_rows",
    "session_bucket_from_utc",
    "weekday_from",
    "write_lifecycle_features_csv",
]


@dataclass(frozen=True)
class LifecycleFeatureRecord:
    """One trade's full lifecycle feature capture. Core fields first."""

    campaign_id: str
    strategy_name: str | None = None
    split: str | None = None
    instrument: str | None = None
    side: str | None = None

    entry_time: datetime | None = None
    exit_time: datetime | None = None
    entry_price: float | None = None
    exit_price: float | None = None

    # Stop geometry / cost context
    initial_stop_price: float | None = None
    stop_distance_pips: float | None = None
    stop_distance_atr: float | None = None
    atr_at_entry: float | None = None
    spread_pips: float | None = None
    spread_to_atr_pct: float | None = None

    bars_held: int | None = None
    result_r: float | None = None
    exit_reason: str | None = None

    # Excursion (filled by MFE/MAE reconstruction or at trade close)
    mfe_r: float | None = None
    mae_r: float | None = None
    reached_plus_0_25r: bool | None = None
    reached_plus_0_5r: bool | None = None
    reached_plus_1_0r: bool | None = None
    touched_minus_0_5r: bool | None = None
    touched_minus_0_9r: bool | None = None

    # HTF / signal features at entry
    h4_adx_at_entry: float | None = None
    h4_bias_score: float | None = None
    h4_ema_slope: float | None = None
    h1_pullback_depth_atr: float | None = None
    h1_rsi_at_entry: float | None = None
    m15_reclaim_distance_atr: float | None = None
    m15_adx_at_entry: float | None = None

    # Context buckets
    session_bucket: str | None = None
    weekday: str | None = None
    volatility_regime: str | None = None

    # Provenance: the close timestamps of the HTF frames used for features,
    # so lookahead can be audited after the fact.
    h1_feature_time: datetime | None = None
    h4_feature_time: datetime | None = None

    def to_csv_row(self) -> dict[str, str]:
        """Serialize to a flat str->str mapping (datetimes ISO, None -> '')."""
        row: dict[str, str] = {}
        for f in fields(self):
            v = getattr(self, f.name)
            if v is None:
                row[f.name] = ""
            elif isinstance(v, datetime):
                row[f.name] = v.isoformat()
            elif isinstance(v, bool):
                row[f.name] = "True" if v else "False"
            else:
                row[f.name] = str(v)
        return row

    @classmethod
    def from_mapping(cls, m: Mapping[str, object], *, campaign_id: str | None = None) -> LifecycleFeatureRecord:
        """Build a record from a loose mapping (e.g. a CSV row). Tolerant of
        missing keys and blank strings; unknown keys are ignored."""
        kwargs: dict[str, object] = {}
        type_by_name = {f.name: f.type for f in fields(cls)}
        for name in type_by_name:
            if name == "campaign_id":
                continue
            raw = m.get(name)
            kwargs[name] = _coerce(name, raw)
        cid = campaign_id if campaign_id is not None else (m.get("campaign_id") or "")
        return cls(campaign_id=str(cid), **kwargs)  # type: ignore[arg-type]


CSV_COLUMNS: tuple[str, ...] = tuple(f.name for f in fields(LifecycleFeatureRecord))

_BOOL_FIELDS = {
    "reached_plus_0_25r", "reached_plus_0_5r", "reached_plus_1_0r",
    "touched_minus_0_5r", "touched_minus_0_9r",
}
_INT_FIELDS = {"bars_held"}
_DT_FIELDS = {"entry_time", "exit_time", "h1_feature_time", "h4_feature_time"}
_STR_FIELDS = {
    "strategy_name", "split", "instrument", "side", "exit_reason",
    "session_bucket", "weekday", "volatility_regime",
}


def _coerce(name: str, raw: object) -> object | None:
    if raw is None or raw == "":
        return None
    if name in _STR_FIELDS:
        return str(raw)
    if name in _DT_FIELDS:
        try:
            return datetime.fromisoformat(str(raw))
        except ValueError:
            return None
    if name in _BOOL_FIELDS:
        return str(raw).strip().lower() in {"true", "1", "yes"}
    if name in _INT_FIELDS:
        try:
            return int(float(raw))  # type: ignore[arg-type]
        except (ValueError, TypeError):
            return None
    # default: float
    try:
        return float(raw)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None


def pip_size(instrument: str | None) -> float:
    """Pip size for FX majors: 0.01 for JPY-quote, else 0.0001."""
    if instrument and instrument.upper().endswith("JPY"):
        return 0.01
    return 0.0001


def price_based_r(
    side: str,
    entry_price: float,
    exit_price: float,
    initial_stop_price: float,
) -> float | None:
    """Pair-agnostic, price-based R. Returns −1.0 exactly when the trade exits at
    its initial stop, for ANY instrument (the correct convention — see the C022
    R-multiple audit). ``None`` if risk is zero or the side is unrecognized."""
    s = side.strip().lower()
    risk = abs(entry_price - initial_stop_price)
    if risk == 0:
        return None
    if s in {"long", "buy"}:
        return (exit_price - entry_price) / risk
    if s in {"short", "sell"}:
        return (entry_price - exit_price) / risk
    return None


def derive_stop_distance_pips(
    instrument: str | None,
    entry_price: float | None,
    initial_stop_price: float | None,
) -> float | None:
    if entry_price is None or initial_stop_price is None:
        return None
    return abs(entry_price - initial_stop_price) / pip_size(instrument)


def missing_field_counts(records: list[LifecycleFeatureRecord]) -> dict[str, int]:
    """Per-field count of records where the field is missing (None). Includes a
    `_total_records` key. Fields never missing are omitted."""
    counts: dict[str, int] = {}
    for f in fields(LifecycleFeatureRecord):
        missing = sum(1 for r in records if getattr(r, f.name) is None)
        if missing:
            counts[f.name] = missing
    counts["_total_records"] = len(records)
    return counts


# Coarse FX session buckets by UTC hour (diagnostic only — approximate windows).
def session_bucket_from_utc(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    h = dt.hour
    if 0 <= h < 7:
        return "asia"
    if 7 <= h < 12:
        return "london"
    if 12 <= h < 16:
        return "london_ny_overlap"
    if 16 <= h < 21:
        return "new_york"
    return "late"


def weekday_from(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[dt.weekday()]


def _f(m: Mapping[str, object], *keys: str) -> float | None:
    for k in keys:
        v = m.get(k)
        if v is not None and v != "":
            try:
                return float(v)  # type: ignore[arg-type]
            except (ValueError, TypeError):
                return None
    return None


def _i(m: Mapping[str, object], *keys: str) -> int | None:
    for k in keys:
        v = m.get(k)
        if v is not None and v != "":
            try:
                return int(float(v))  # type: ignore[arg-type]
            except (ValueError, TypeError):
                return None
    return None


def _s(m: Mapping[str, object], *keys: str) -> str | None:
    for k in keys:
        v = m.get(k)
        if v is not None and v != "":
            return str(v)
    return None


def _dt(m: Mapping[str, object], *keys: str) -> datetime | None:
    raw = _s(m, *keys)
    if raw is None:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def record_from_trade_row(
    row: Mapping[str, object],
    *,
    campaign_id: str,
    strategy_name: str | None = None,
    split: str | None = None,
) -> LifecycleFeatureRecord:
    """Map a campaign trade CSV row (C022-style columns) to a feature record.

    `result_r` is recomputed with the **corrected pair-agnostic** convention
    (`price_based_r`), deliberately not copying the source `r_multiple` (which
    carries the USD-base scaling quirk — see the C022 R-multiple audit). MFE/MAE
    and HTF signal features are left **None** (not present in historical trades);
    they are populated only by instrumented future runs / MFE-MAE reconstruction.
    `weekday` and `session_bucket` are derived from `entry_time` (no fabrication).
    """
    instrument = _s(row, "instrument")
    side = _s(row, "side")
    entry_price = _f(row, "entry_price")
    exit_price = _f(row, "exit_price")
    stop_price = _f(row, "stop_price", "initial_stop_price")
    entry_time = _dt(row, "entry_time")

    result_r = None
    if side and entry_price is not None and exit_price is not None and stop_price is not None:
        result_r = price_based_r(side, entry_price, exit_price, stop_price)

    return LifecycleFeatureRecord(
        campaign_id=campaign_id,
        strategy_name=strategy_name,
        split=split,
        instrument=instrument,
        side=side,
        entry_time=entry_time,
        exit_time=_dt(row, "exit_time"),
        entry_price=entry_price,
        exit_price=exit_price,
        initial_stop_price=stop_price,
        stop_distance_pips=derive_stop_distance_pips(instrument, entry_price, stop_price),
        spread_pips=_f(row, "spread_paid_pips", "spread_pips"),
        bars_held=_i(row, "bars_held"),
        result_r=result_r,
        exit_reason=_s(row, "exit_reason"),
        session_bucket=session_bucket_from_utc(entry_time),
        weekday=weekday_from(entry_time),
    )


def records_from_trade_rows(
    rows: Iterable[Mapping[str, object]],
    *,
    campaign_id: str,
    strategy_name: str | None = None,
    split: str | None = None,
) -> list[LifecycleFeatureRecord]:
    return [
        record_from_trade_row(
            row, campaign_id=campaign_id, strategy_name=strategy_name, split=split
        )
        for row in rows
    ]


def write_lifecycle_features_csv(
    records: Iterable[LifecycleFeatureRecord], path: str | Path
) -> Path:
    """Write records to a compact CSV with the canonical `CSV_COLUMNS` header."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(CSV_COLUMNS))
        writer.writeheader()
        for rec in records:
            writer.writerow(rec.to_csv_row())
    return p
