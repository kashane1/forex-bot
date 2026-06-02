"""Lookahead-free loaders + alignment for Family E derivatives diagnostics.

All time is reduced to an integer **hour index** = ``epoch_seconds // 3600``.
Hour index 0 is 1970-01-01T00:00 UTC, so ``hour % 8 == 0`` marks the
00:00 / 08:00 / 16:00 UTC funding-settlement boundaries used for 8h resampling.

No interpolation: windows that cross a missing funding / index / OHLCV bar are
skipped and counted (see ``EligibleSample.n_skipped``).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from research.crypto.derivatives_registry import validate_perp

HOUR_SECONDS = 3600
FUNDING_SETTLEMENT_HOURS = 8


def hour_index(dt: datetime) -> int:
    """Integer hour index (UTC) for a timezone-aware/naive datetime."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return int(dt.timestamp()) // HOUR_SECONDS


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"missing Family E backfill file: {path}")
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@dataclass(frozen=True)
class InstrumentSeries:
    """Hour-indexed maps for one perp instrument. Keys are integer hour indices."""

    canonical_id: str
    funding: dict[int, float]  # hour -> realized 1h funding_rate
    open_px: dict[int, float]  # hour -> perp open (price exactly at hour boundary)
    close_px: dict[int, float]  # hour -> perp close
    basis_bps: dict[int, float]  # hour -> basis_bps (perp vs index)
    index_close: dict[int, float]  # hour -> index close
    oi_usd: dict[int, float] = field(default_factory=dict)  # day-hour -> OI (shallow)

    @property
    def funding_hours(self) -> int:
        return len(self.funding)


def load_instrument_series(backfill_dir: Path, canonical_id: str) -> InstrumentSeries:
    """Load the gitignored backfill CSVs for one BTC/ETH perp into hour-indexed maps."""
    validate_perp(canonical_id)
    base = backfill_dir / canonical_id

    funding = {
        hour_index(parse_iso(r["time_utc"])): float(r["funding_rate"])
        for r in _read_csv(base / "funding.csv")
    }
    ohlcv = _read_csv(base / "ohlcv_h1.csv")
    open_px = {hour_index(parse_iso(r["time_utc"])): float(r["open"]) for r in ohlcv}
    close_px = {hour_index(parse_iso(r["time_utc"])): float(r["close"]) for r in ohlcv}
    basis_bps = {
        hour_index(parse_iso(r["time_utc"])): float(r["basis_bps"])
        for r in _read_csv(base / "basis_h1.csv")
    }
    index_close = {
        hour_index(parse_iso(r["time_utc"])): float(r["index_close"])
        for r in _read_csv(base / "index_h1.csv")
    }
    oi_usd: dict[int, float] = {}
    oi_path = base / "oi_daily.csv"
    if oi_path.exists():
        oi_usd = {
            hour_index(parse_iso(r["time_utc"])): float(r["open_interest_usd"])
            for r in _read_csv(oi_path)
        }
    return InstrumentSeries(
        canonical_id=canonical_id,
        funding=funding,
        open_px=open_px,
        close_px=close_px,
        basis_bps=basis_bps,
        index_close=index_close,
        oi_usd=oi_usd,
    )


def funding_8h_windows(funding: dict[int, float]) -> dict[int, float]:
    """Map settlement-boundary entry hour -> summed 8h realized funding.

    Window ``k`` covers hours ``[8k, 8k+8)``; its summed funding becomes known at
    the entry hour ``8k+8``. Only windows with all 8 hourly rows present are kept
    (no interpolation). The returned key is the **entry hour** (settlement end).
    """
    if not funding:
        return {}
    hours = sorted(funding)
    first_window = hours[0] // FUNDING_SETTLEMENT_HOURS
    last_window = hours[-1] // FUNDING_SETTLEMENT_HOURS
    out: dict[int, float] = {}
    for k in range(first_window, last_window + 1):
        win_hours = range(k * FUNDING_SETTLEMENT_HOURS, (k + 1) * FUNDING_SETTLEMENT_HOURS)
        vals = [funding.get(h) for h in win_hours]
        if any(v is None for v in vals):
            continue
        entry_hour = (k + 1) * FUNDING_SETTLEMENT_HOURS
        out[entry_hour] = float(sum(v for v in vals if v is not None))
    return out


def forward_log_return(open_px: dict[int, float], entry_hour: int, horizon_h: int) -> float | None:
    """Open-to-open log return entry_hour -> entry_hour+horizon. None if a leg is missing."""
    p0 = open_px.get(entry_hour)
    p1 = open_px.get(entry_hour + horizon_h)
    if p0 is None or p1 is None or p0 <= 0 or p1 <= 0:
        return None
    return float(np.log(p1 / p0))


def realized_funding_over_hold(
    funding: dict[int, float], entry_hour: int, horizon_h: int
) -> float | None:
    """Sum of hourly funding settling during a hold ``[entry_hour, entry_hour+horizon)``.

    None if any settling hour is missing (no interpolation). This is the funding
    *rate fraction* of notional; sign convention applied by the cost layer.
    """
    total = 0.0
    for h in range(entry_hour, entry_hour + horizon_h):
        v = funding.get(h)
        if v is None:
            return None
        total += v
    return total


@dataclass(frozen=True)
class EligibleSample:
    """Per-entry aligned arrays for one (instrument, diagnostic, horizon) cell."""

    canonical_id: str
    entry_hours: np.ndarray  # int
    signal: np.ndarray  # float — the conditioning signal value
    fwd_ret: np.ndarray  # float — open-to-open forward log return over horizon
    funding_hold: np.ndarray  # float — summed funding rate over the hold
    horizon_h: int
    n_skipped: int

    @property
    def n(self) -> int:
        return int(self.entry_hours.size)


def build_funding_sample(
    series: InstrumentSeries, *, horizon_h: int
) -> EligibleSample:
    """Eligible sample keyed on 8h-summed funding signal with forward perp returns."""
    windows = funding_8h_windows(series.funding)
    entry_hours: list[int] = []
    signal: list[float] = []
    fwd: list[float] = []
    fund: list[float] = []
    skipped = 0
    for entry_hour in sorted(windows):
        ret = forward_log_return(series.open_px, entry_hour, horizon_h)
        hold = realized_funding_over_hold(series.funding, entry_hour, horizon_h)
        if ret is None or hold is None:
            skipped += 1
            continue
        entry_hours.append(entry_hour)
        signal.append(windows[entry_hour])
        fwd.append(ret)
        fund.append(hold)
    return EligibleSample(
        canonical_id=series.canonical_id,
        entry_hours=np.array(entry_hours, dtype=np.int64),
        signal=np.array(signal, dtype=float),
        fwd_ret=np.array(fwd, dtype=float),
        funding_hold=np.array(fund, dtype=float),
        horizon_h=horizon_h,
        n_skipped=skipped,
    )


def build_funding_persistence_sample(
    series: InstrumentSeries, *, k: int, horizon_h: int
) -> EligibleSample:
    """Sample whose signal is the signed run-length of k same-sign 8h funding settlements.

    ``signal`` is +1 if the last ``k`` 8h funding values (ending at the settlement
    before entry) are all positive, -1 if all negative, else 0 (excluded as a cohort).
    """
    windows = funding_8h_windows(series.funding)
    ordered = sorted(windows)
    entry_hours: list[int] = []
    signal: list[float] = []
    fwd: list[float] = []
    fund: list[float] = []
    skipped = 0
    for idx in range(k, len(ordered)):
        entry_hour = ordered[idx]
        recent = [windows[ordered[idx - j]] for j in range(1, k + 1)]
        if all(v > 0 for v in recent):
            sign = 1.0
        elif all(v < 0 for v in recent):
            sign = -1.0
        else:
            sign = 0.0
        ret = forward_log_return(series.open_px, entry_hour, horizon_h)
        hold = realized_funding_over_hold(series.funding, entry_hour, horizon_h)
        if ret is None or hold is None:
            skipped += 1
            continue
        entry_hours.append(entry_hour)
        signal.append(sign)
        fwd.append(ret)
        fund.append(hold)
    return EligibleSample(
        canonical_id=series.canonical_id,
        entry_hours=np.array(entry_hours, dtype=np.int64),
        signal=np.array(signal, dtype=float),
        fwd_ret=np.array(fwd, dtype=float),
        funding_hold=np.array(fund, dtype=float),
        horizon_h=horizon_h,
        n_skipped=skipped,
    )


def build_basis_sample(series: InstrumentSeries, *, horizon_h: int) -> EligibleSample:
    """Sample keyed on hourly basis_bps known at the prior bar; forward perp return.

    Basis from the H1 bar timestamped ``t`` is actionable at ``t+1`` (bar end), so
    entry hour = ``t+1`` with open-to-open forward return; funding over the hold.
    """
    entry_hours: list[int] = []
    signal: list[float] = []
    fwd: list[float] = []
    fund: list[float] = []
    skipped = 0
    for bar_hour in sorted(series.basis_bps):
        entry_hour = bar_hour + 1
        ret = forward_log_return(series.open_px, entry_hour, horizon_h)
        hold = realized_funding_over_hold(series.funding, entry_hour, horizon_h)
        if ret is None or hold is None:
            skipped += 1
            continue
        entry_hours.append(entry_hour)
        signal.append(series.basis_bps[bar_hour])
        fwd.append(ret)
        fund.append(hold)
    return EligibleSample(
        canonical_id=series.canonical_id,
        entry_hours=np.array(entry_hours, dtype=np.int64),
        signal=np.array(signal, dtype=float),
        fwd_ret=np.array(fwd, dtype=float),
        funding_hold=np.array(fund, dtype=float),
        horizon_h=horizon_h,
        n_skipped=skipped,
    )


def align_on_entry_hours(
    a: EligibleSample, b: EligibleSample
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Intersect two samples on entry hour. Returns (hours, a_sig, a_ret, b_sig, b_ret)."""
    a_map = {int(h): i for i, h in enumerate(a.entry_hours)}
    b_map = {int(h): i for i, h in enumerate(b.entry_hours)}
    common = sorted(set(a_map) & set(b_map))
    if not common:
        empty = np.array([], dtype=float)
        return np.array([], dtype=np.int64), empty, empty, empty, empty
    ai = [a_map[h] for h in common]
    bi = [b_map[h] for h in common]
    return (
        np.array(common, dtype=np.int64),
        a.signal[ai],
        a.fwd_ret[ai],
        b.signal[bi],
        b.fwd_ret[bi],
    )
