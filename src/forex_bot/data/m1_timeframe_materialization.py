"""M1 → M5/M15/H1/H4 materialization for Postgres research store."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Literal

from forex_bot.data.m1_corpus_validation import (
    MAJOR_PAIRS,
    _dedupe_candles_by_time,
    _row_to_candle,
    iter_m1_chunks,
    pair_range,
)
from forex_bot.data.postgres_candle_store import CandleRecord, PostgresCandleStore
from forex_bot.data.timeframe_aggregation import aggregate_m1_candles
from forex_bot.domain.candles import Candle

MATERIALIZED_FROM_M1 = ("M5", "M15", "H1", "H4")
MATERIALIZED_SOURCE = "m1_materialized"
NATIVE_H4_SOURCES_PRESERVED = frozenset({"oanda-practice", "oanda-practice-readonly"})
MISSING_POLICY = "omit"
AGGREGATION_CONFIG = {
    "source_granularity": "M1",
    "missing_policy": MISSING_POLICY,
    "alignment_tz": "America/New_York",
    "alignment_hour": 17,
    "targets": list(MATERIALIZED_FROM_M1),
}

_TARGET_MINUTES = {"M5": 5, "M15": 15, "H1": 60, "H4": 240}

OHLC_TOLERANCE = 1e-5


def aggregation_config_hash() -> str:
    payload = json.dumps(AGGREGATION_CONFIG, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass
class TargetMaterializationStats:
    target: str
    rows_upserted: int = 0
    first_utc: datetime | None = None
    last_utc: datetime | None = None
    omitted_incomplete_blocks: int = 0


@dataclass
class MaterializationResult:
    instrument: str
    run_id: str
    from_utc: datetime
    to_utc: datetime
    m1_rows_read: int = 0
    dry_run: bool = False
    targets: dict[str, TargetMaterializationStats] = field(default_factory=dict)
    aggregation_config_hash: str = field(default_factory=aggregation_config_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "instrument": self.instrument,
            "run_id": self.run_id,
            "from_utc": self.from_utc.isoformat(),
            "to_utc": self.to_utc.isoformat(),
            "m1_rows_read": self.m1_rows_read,
            "dry_run": self.dry_run,
            "aggregation_config_hash": self.aggregation_config_hash,
            "targets": {
                name: {
                    "rows_upserted": stats.rows_upserted,
                    "first_utc": stats.first_utc.isoformat() if stats.first_utc else None,
                    "last_utc": stats.last_utc.isoformat() if stats.last_utc else None,
                    "omitted_incomplete_blocks": stats.omitted_incomplete_blocks,
                }
                for name, stats in self.targets.items()
            },
        }


def _decimal_to_float(value: Decimal | None) -> float | None:
    return None if value is None else float(value)


def candle_to_record(candle: Candle, *, fetch_batch_id: str) -> CandleRecord:
    return CandleRecord(
        instrument=candle.instrument,
        granularity=candle.granularity,
        time_utc=candle.time.astimezone(UTC),
        complete=candle.complete,
        volume=int(candle.volume),
        bid_o=_decimal_to_float(candle.bid_o),
        bid_h=_decimal_to_float(candle.bid_h),
        bid_l=_decimal_to_float(candle.bid_l),
        bid_c=_decimal_to_float(candle.bid_c),
        ask_o=_decimal_to_float(candle.ask_o),
        ask_h=_decimal_to_float(candle.ask_h),
        ask_l=_decimal_to_float(candle.ask_l),
        ask_c=_decimal_to_float(candle.ask_c),
        mid_o=_decimal_to_float(candle.mid_o),
        mid_h=_decimal_to_float(candle.mid_h),
        mid_l=_decimal_to_float(candle.mid_l),
        mid_c=_decimal_to_float(candle.mid_c),
        fetch_batch_id=fetch_batch_id,
    )


def _incremental_start(
    store: PostgresCandleStore,
    instrument: str,
    target: str,
    default_start: datetime,
) -> datetime:
    last = store.max_candle_time(
        instrument=instrument,
        granularity=target,
        source=MATERIALIZED_SOURCE,
    )
    if last is None:
        return default_start
    step = timedelta(minutes=_TARGET_MINUTES[target])
    return last + step


def aggregate_m1_window(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_utc: datetime,
    to_utc: datetime,
    targets: tuple[str, ...] = MATERIALIZED_FROM_M1,
    chunk_days: int = 30,
) -> dict[str, list[Candle]]:
    """On-the-fly aggregation reference path (same semantics as campaigns today)."""
    buckets: dict[str, list[Candle]] = {target: [] for target in targets}
    for chunk in iter_m1_chunks(
        store,
        instrument=instrument,
        start_utc=from_utc,
        end_utc=to_utc,
        chunk_days=chunk_days,
    ):
        candles = [_row_to_candle(row, instrument=instrument) for row in chunk]
        for target in targets:
            result = aggregate_m1_candles(candles, target=target, missing_policy=MISSING_POLICY)
            buckets[target].extend(result.candles)
    out: dict[str, list[Candle]] = {}
    for target, items in buckets.items():
        out[target] = _dedupe_candles_by_time(items)
    return out


def materialize_pair(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_utc: datetime,
    to_utc: datetime,
    targets: tuple[str, ...] = MATERIALIZED_FROM_M1,
    chunk_days: int = 30,
    dry_run: bool = False,
    run_id: str | None = None,
) -> MaterializationResult:
    if instrument not in MAJOR_PAIRS:
        raise ValueError(f"instrument not in major universe: {instrument}")
    run = run_id or str(uuid.uuid4())
    result = MaterializationResult(
        instrument=instrument,
        run_id=run,
        from_utc=from_utc.astimezone(UTC),
        to_utc=to_utc.astimezone(UTC),
        dry_run=dry_run,
        targets={target: TargetMaterializationStats(target=target) for target in targets},
    )
    pending: dict[str, list[CandleRecord]] = {target: [] for target in targets}
    batch_size = 2000
    fetched_at = datetime.now(UTC)

    for chunk in iter_m1_chunks(
        store,
        instrument=instrument,
        start_utc=from_utc,
        end_utc=to_utc,
        chunk_days=chunk_days,
    ):
        candles = [_row_to_candle(row, instrument=instrument) for row in chunk]
        result.m1_rows_read += len(candles)
        per_target: dict[str, list[Candle]] = {target: [] for target in targets}
        for target in targets:
            agg = aggregate_m1_candles(candles, target=target, missing_policy=MISSING_POLICY)
            result.targets[target].omitted_incomplete_blocks += agg.omitted_incomplete_blocks
            per_target[target] = agg.candles
        for target in targets:
            for candle in per_target[target]:
                if not candle.complete:
                    continue
                ts = candle.time.astimezone(UTC)
                if ts < from_utc or ts > to_utc:
                    continue
                stats = result.targets[target]
                if stats.first_utc is None or ts < stats.first_utc:
                    stats.first_utc = ts
                if stats.last_utc is None or ts > stats.last_utc:
                    stats.last_utc = ts
                pending[target].append(candle_to_record(candle, fetch_batch_id=run))
                if len(pending[target]) >= batch_size and not dry_run:
                    _flush_target(store, target, pending[target], fetched_at=fetched_at)
                    result.targets[target].rows_upserted += len(pending[target])
                    pending[target] = []

    if not dry_run:
        for target in targets:
            if pending[target]:
                _flush_target(store, target, pending[target], fetched_at=fetched_at)
                result.targets[target].rows_upserted += len(pending[target])
    else:
        for target in targets:
            result.targets[target].rows_upserted = len(pending[target])

    return result


def _flush_target(
    store: PostgresCandleStore,
    target: str,
    records: list[CandleRecord],
    *,
    fetched_at: datetime,
) -> None:
    if target == "H4":
        store.upsert_materialized_candles(
            records,
            source=MATERIALIZED_SOURCE,
            fetched_at_utc=fetched_at,
            preserve_sources=NATIVE_H4_SOURCES_PRESERVED,
        )
    else:
        store.upsert_candles(records, source=MATERIALIZED_SOURCE, fetched_at_utc=fetched_at)


def verify_materialized_pair(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_utc: datetime,
    to_utc: datetime,
    targets: tuple[str, ...] = MATERIALIZED_FROM_M1,
    chunk_days: int = 30,
) -> dict[str, Any]:
    live = aggregate_m1_window(
        store,
        instrument,
        from_utc=from_utc,
        to_utc=to_utc,
        targets=targets,
        chunk_days=chunk_days,
    )
    report: dict[str, Any] = {
        "instrument": instrument,
        "from_utc": from_utc.isoformat(),
        "to_utc": to_utc.isoformat(),
        "aggregation_config_hash": aggregation_config_hash(),
        "targets": {},
        "status": "PASS",
    }
    for target in targets:
        stored_rows = store.query_candles(
            instrument=instrument,
            granularity=target,
            start_utc=from_utc,
            end_utc=to_utc,
            source=MATERIALIZED_SOURCE,
        )
        stored = {
            row["time_utc"].astimezone(UTC): _row_to_candle(
                {**row, "granularity": target},
                instrument=instrument,
            )
            for row in stored_rows
            if row.get("complete")
        }
        expected = {candle.time.astimezone(UTC): candle for candle in live[target] if candle.complete}
        missing_in_store = sorted(set(expected) - set(stored))
        extra_in_store = sorted(set(stored) - set(expected))
        mismatches: list[str] = []
        for ts in sorted(set(expected) & set(stored)):
            exp = expected[ts]
            got = stored[ts]
            for field in ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"):
                ev = _decimal_to_float(getattr(exp, field))
                gv = _decimal_to_float(getattr(got, field))
                if ev is None and gv is None:
                    continue
                if ev is None or gv is None or abs(ev - gv) > OHLC_TOLERANCE:
                    mismatches.append(f"{ts.isoformat()}:{field}")
                    break
        target_status: Literal["PASS", "FAIL"] = (
            "PASS"
            if not missing_in_store and not extra_in_store and not mismatches
            else "FAIL"
        )
        if target_status == "FAIL":
            report["status"] = "FAIL"
        report["targets"][target] = {
            "expected_count": len(expected),
            "stored_count": len(stored),
            "missing_in_store": len(missing_in_store),
            "extra_in_store": len(extra_in_store),
            "ohlc_mismatches": len(mismatches),
            "status": target_status,
        }
    return report


def resolve_pair_window(
    store: PostgresCandleStore,
    instrument: str,
    *,
    from_utc: datetime | None,
    to_utc: datetime | None,
    incremental: bool,
    targets: tuple[str, ...],
) -> tuple[datetime, datetime]:
    pr = pair_range(store, instrument)
    start = (from_utc or pr.start_utc).astimezone(UTC)
    end = (to_utc or pr.end_utc).astimezone(UTC)
    if incremental:
        starts = [
            _incremental_start(store, instrument, target, start)
            for target in targets
        ]
        start = max(starts)
    return start, end
