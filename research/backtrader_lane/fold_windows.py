"""Walk-forward fold-window helpers for the Backtrader secondary lane.

Loads fold test windows from a committed walk-forward ``plan.json`` and
slices candle data to the same inclusive date ranges the bespoke
``scripts/run_campaign_015.py`` runner uses:

* candle load window: ``[test_start - warmup_days, test_end]`` (inclusive
  calendar days, UTC midnight/end-of-day bounds);
* per fold × pair: independent run with equity reset (handled by the
  runner, not this module).

``strategy_evidence: false``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from research.backtrader_lane.data_adapter import CandleAdapterResult
from research.walk_forward.models import Fold, WalkForwardPlan


# Matches ``scripts/run_campaign_015.py`` ``_fold_dates_to_dts``.
DEFAULT_WARMUP_DAYS = 90


@dataclass(frozen=True)
class FoldWindowSpec:
    """One fold's test window plus derived candle-load bounds."""

    fold_index: int
    test_start: date
    test_end: date
    warmup_days: int = DEFAULT_WARMUP_DAYS

    @property
    def candle_load_start(self) -> datetime:
        return datetime.combine(
            self.test_start - timedelta(days=self.warmup_days),
            datetime.min.time(),
            tzinfo=UTC,
        )

    @property
    def candle_load_end(self) -> datetime:
        return datetime.combine(
            self.test_end,
            datetime.max.time().replace(microsecond=0),
            tzinfo=UTC,
        )

    @classmethod
    def from_fold(cls, fold: Fold, *, warmup_days: int = DEFAULT_WARMUP_DAYS) -> FoldWindowSpec:
        return cls(
            fold_index=fold.fold_index,
            test_start=fold.test_start,
            test_end=fold.test_end,
            warmup_days=warmup_days,
        )


def load_fold_plan(path: Path) -> WalkForwardPlan:
    """Load a walk-forward plan JSON (``plan.json`` shape)."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    return WalkForwardPlan.model_validate(raw)


def fold_specs_from_plan(
    plan: WalkForwardPlan,
    *,
    warmup_days: int = DEFAULT_WARMUP_DAYS,
) -> list[FoldWindowSpec]:
    return [FoldWindowSpec.from_fold(f, warmup_days=warmup_days) for f in plan.folds]


def slice_candles(
    candles: CandleAdapterResult,
    *,
    from_time: datetime,
    to_time: datetime,
) -> CandleAdapterResult:
    """Return a view of ``candles`` restricted to ``[from_time, to_time]``.

    The provenance / sha256 metadata is preserved from the parent load;
    ``bar_count`` and ``first_ts`` / ``last_ts`` reflect the slice.
    """

    mid = candles.mid_df
    mask = (mid.index >= from_time) & (mid.index <= to_time)
    if not mask.any():
        raise ValueError(
            f"no candles for {candles.instrument} in "
            f"{from_time.isoformat()}..{to_time.isoformat()}"
        )
    sliced_mid = mid.loc[mask]
    sliced_bid = candles.bid_ohlc_df.loc[mask]
    sliced_ask = candles.ask_ohlc_df.loc[mask]
    sliced_spread = candles.half_spread_close.loc[mask]
    return CandleAdapterResult(
        instrument=candles.instrument,
        provenance=candles.provenance,
        csv_sha256=candles.csv_sha256,
        mid_df=sliced_mid,
        bid_ohlc_df=sliced_bid,
        ask_ohlc_df=sliced_ask,
        half_spread_close=sliced_spread,
        first_ts=sliced_mid.index[0].to_pydatetime(),
        last_ts=sliced_mid.index[-1].to_pydatetime(),
        bar_count=len(sliced_mid),
        approximation_flags=list(candles.approximation_flags),
    )


def bar_date_utc(ts: datetime) -> date:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts.astimezone(UTC).date()


def entry_in_test_window(
    entry_time: datetime,
    *,
    test_start: date,
    test_end: date,
    strict: bool,
) -> bool:
    """Return whether ``entry_time`` counts as a test-window trade.

    When ``strict`` is False, every trade emitted by the fold slice run
    counts (mirrors the bespoke engine, which does not filter entries
    to ``test_start`` even though the 90-day warmup margin precedes it).
    """

    if not strict:
        return True
    d = bar_date_utc(entry_time)
    return test_start <= d <= test_end


def preflight_fold_windows(
    *,
    instruments: list[str],
    fold_specs: list[FoldWindowSpec],
    load_fn,
) -> dict[str, Any]:
    """Check that every fold × instrument has warmup + test coverage.

    ``load_fn(name)`` must return a ``CandleAdapterResult`` (typically
    ``load_candles`` bound with export_dir / strict flags).
    """

    blocked: list[str] = []
    fold_reports: list[dict[str, Any]] = []
    for spec in fold_specs:
        per_pair: dict[str, Any] = {}
        fold_blocked: list[str] = []
        for name in instruments:
            try:
                candles = load_fn(name)
            except FileNotFoundError:
                fold_blocked.append(name)
                blocked.append(f"{name}:csv_missing")
                continue
            try:
                sliced = slice_candles(
                    candles,
                    from_time=spec.candle_load_start,
                    to_time=spec.candle_load_end,
                )
            except ValueError as exc:
                fold_blocked.append(name)
                blocked.append(f"{name}:fold_{spec.fold_index}:{exc}")
                continue
            per_pair[name] = {
                "candle_count": sliced.bar_count,
                "first_ts": sliced.first_ts.isoformat(),
                "last_ts": sliced.last_ts.isoformat(),
            }
        fold_reports.append(
            {
                "fold_index": spec.fold_index,
                "test_start": str(spec.test_start),
                "test_end": str(spec.test_end),
                "candle_load_start": spec.candle_load_start.isoformat(),
                "candle_load_end": spec.candle_load_end.isoformat(),
                "pairs": per_pair,
                "blocked_instruments": sorted(fold_blocked),
            }
        )
    runnable = not blocked
    return {
        "mode": "fold_windows",
        "fold_count": len(fold_specs),
        "instruments": instruments,
        "warmup_days": fold_specs[0].warmup_days if fold_specs else DEFAULT_WARMUP_DAYS,
        "folds": fold_reports,
        "blocked_reasons": blocked,
        "runnable": runnable,
    }
