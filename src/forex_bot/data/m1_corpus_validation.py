"""Full M1 corpus inventory, quality, aggregation, and drift validation."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator, Literal

import pandas as pd

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.backtesting.ltf_preflight import run_ltf_backtest_preflight
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.timeframe_aggregation import aggregate_m1_candles
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.features.ltf_htf_alignment import align_ltf_execution_context

Status = Literal["PASS", "WARN", "FAIL"]

MAJOR_PAIRS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)

EXPECTED_M1_COUNTS: dict[str, int] = {
    "EUR_USD": 1_843_476,
    "GBP_USD": 1_836_170,
    "USD_JPY": 1_844_454,
    "AUD_USD": 1_822_196,
    "USD_CAD": 1_836_013,
    "USD_CHF": 1_786_535,
    "NZD_USD": 1_824_352,
}

TARGET_GRANULARITIES = ("M5", "M15", "H1", "H4", "D1AGG")
OHLC_TOLERANCE = 1e-5
MID_TOLERANCE = 1e-5
VOLUME_TOLERANCE = 0


@dataclass
class PairRange:
    instrument: str
    start_utc: datetime
    end_utc: datetime


def classify_count_delta(actual: int, expected: int) -> Status:
    delta = abs(actual - expected)
    if delta == 0:
        return "PASS"
    pct = delta / expected if expected else 1.0
    if pct <= 0.005:
        return "WARN"
    return "FAIL"


def extreme_spread_threshold(instrument: str) -> float:
    """Price-unit threshold; JPY quotes use larger absolute spreads."""
    return 0.05 if "JPY" in instrument else 0.01


def classify_quality(report: dict[str, Any]) -> Status:
    if report.get("duplicate_timestamps", 0) > 0:
        return "FAIL"
    if report.get("bid_ask_violations", 0) > 0:
        return "FAIL"
    if report.get("ohlc_violations", 0) > 0:
        return "FAIL"
    if report.get("negative_or_zero_spreads", 0) > 0:
        return "FAIL"
    missing = report.get("missing_minutes", 0)
    expected = report.get("expected_weekday_minutes", 1)
    missing_pct = missing / expected if expected else 0
    # Weekday calendar minutes over-count FX close; treat large gaps separately.
    if missing_pct > 0.05:
        return "FAIL"
    if missing_pct > 0.02 or report.get("extreme_spreads", 0) > 0:
        return "WARN"
    return "PASS"


def inventory_sql(store: PostgresCandleStore) -> dict[str, Any]:
    schema = store.config.schema
    sql = f"""
        SELECT instrument,
               COUNT(*) AS row_count,
               MIN(time_utc) AS first_ts,
               MAX(time_utc) AS last_ts,
               SUM(CASE WHEN complete THEN 1 ELSE 0 END) AS complete_count,
               SUM(CASE WHEN NOT complete THEN 1 ELSE 0 END) AS incomplete_count,
               COUNT(*) - COUNT(DISTINCT time_utc) AS duplicate_timestamps,
               COUNT(DISTINCT fetch_batch_id) AS fetch_batch_ids,
               SUM(CASE WHEN data_hash IS NOT NULL AND data_hash <> '' THEN 1 ELSE 0 END) AS data_hash_rows
        FROM {schema}.candles
        WHERE granularity = 'M1'
        GROUP BY instrument
        ORDER BY instrument
    """
    pairs: list[dict[str, Any]] = []
    with store.connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        for row in cur.fetchall():
            instrument = row[0]
            actual = int(row[1])
            expected = EXPECTED_M1_COUNTS.get(instrument)
            pairs.append(
                {
                    "instrument": instrument,
                    "row_count": actual,
                    "expected_row_count": expected,
                    "row_count_delta": None if expected is None else actual - expected,
                    "row_count_status": "PASS" if expected is None else classify_count_delta(actual, expected),
                    "first_timestamp": _iso(row[2]),
                    "last_timestamp": _iso(row[3]),
                    "complete_count": int(row[4]),
                    "incomplete_count": int(row[5]),
                    "duplicate_timestamps": int(row[6]),
                    "fetch_batch_id_count": int(row[7]),
                    "data_hash_coverage": round(int(row[8]) / actual, 6) if actual else 0.0,
                }
            )
    present = {p["instrument"] for p in pairs}
    missing = [p for p in MAJOR_PAIRS if p not in present]
    extra = [p for p in present if p not in MAJOR_PAIRS]
    overall = "FAIL" if missing or any(p["row_count_status"] == "FAIL" for p in pairs) else (
        "WARN" if any(p["row_count_status"] == "WARN" for p in pairs) else "PASS"
    )
    return {
        "pairs": pairs,
        "missing_pairs": missing,
        "extra_pairs": sorted(extra),
        "overall_status": overall,
    }


def iter_m1_chunks(
    store: PostgresCandleStore,
    *,
    instrument: str,
    start_utc: datetime,
    end_utc: datetime,
    chunk_days: int = 14,
) -> Iterator[list[dict[str, Any]]]:
    cursor = start_utc.astimezone(UTC)
    end = end_utc.astimezone(UTC)
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=chunk_days), end)
        rows = store.query_candles(
            instrument=instrument,
            granularity="M1",
            start_utc=cursor,
            end_utc=chunk_end,
        )
        if rows:
            yield rows
        cursor = chunk_end


def pair_range(store: PostgresCandleStore, instrument: str) -> PairRange:
    schema = store.config.schema
    with store.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT MIN(time_utc), MAX(time_utc)
            FROM {schema}.candles
            WHERE instrument = %s AND granularity = 'M1'
            """,
            (instrument,),
        )
        row = cur.fetchone()
    if not row or row[0] is None:
        raise ValueError(f"no M1 rows for {instrument}")
    return PairRange(instrument, row[0].astimezone(UTC), row[1].astimezone(UTC))


def expected_weekday_minutes(start_utc: datetime, end_utc: datetime) -> int:
    count = 0
    cursor = start_utc.astimezone(UTC)
    end = end_utc.astimezone(UTC)
    while cursor < end:
        if cursor.weekday() < 5:
            count += 1
        cursor += timedelta(minutes=1)
    return count


def quality_sql_base(store: PostgresCandleStore, instrument: str) -> dict[str, Any]:
    schema = store.config.schema
    sql = f"""
        SELECT COUNT(*) AS row_count,
               COUNT(DISTINCT time_utc) AS distinct_times,
               MIN(time_utc) AS first_ts,
               MAX(time_utc) AS last_ts,
               SUM(CASE WHEN NOT complete THEN 1 ELSE 0 END) AS incomplete_candles,
               SUM(CASE WHEN bid_c IS NOT NULL AND ask_c IS NOT NULL AND bid_c > ask_c THEN 1 ELSE 0 END) AS bid_ask_violations,
               SUM(CASE WHEN bid_c IS NOT NULL AND ask_c IS NOT NULL AND (ask_c - bid_c) <= 0 THEN 1 ELSE 0 END) AS bad_spreads,
               SUM(CASE WHEN bid_c IS NOT NULL AND ask_c IS NOT NULL AND (ask_c - bid_c) > %s THEN 1 ELSE 0 END) AS extreme_spreads,
               SUM(CASE WHEN bid_h IS NOT NULL AND bid_l IS NOT NULL AND bid_h < bid_l THEN 1 ELSE 0 END)
                 + SUM(CASE WHEN ask_h IS NOT NULL AND ask_l IS NOT NULL AND ask_h < ask_l THEN 1 ELSE 0 END) AS ohlc_violations,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY (ask_c - bid_c)) AS spread_p50,
               percentile_cont(0.9) WITHIN GROUP (ORDER BY (ask_c - bid_c)) AS spread_p90,
               percentile_cont(0.99) WITHIN GROUP (ORDER BY (ask_c - bid_c)) AS spread_p99
        FROM {schema}.candles
        WHERE instrument = %s AND granularity = 'M1'
    """
    threshold = extreme_spread_threshold(instrument)
    with store.connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (threshold, instrument))
        row = cur.fetchone()
    row_count = int(row[0])
    distinct_times = int(row[1])
    return {
        "actual_m1_count": row_count,
        "distinct_timestamps": distinct_times,
        "duplicate_timestamps": row_count - distinct_times,
        "first_timestamp": _iso(row[2]),
        "last_timestamp": _iso(row[3]),
        "incomplete_candles": int(row[4]),
        "bid_ask_violations": int(row[5]),
        "negative_or_zero_spreads": int(row[6]),
        "extreme_spreads": int(row[7]),
        "ohlc_violations": int(row[8]),
        "spread_percentiles": {
            "p50": float(row[9]) if row[9] is not None else None,
            "p90": float(row[10]) if row[10] is not None else None,
            "p99": float(row[11]) if row[11] is not None else None,
        },
    }


def scan_largest_gap(
    store: PostgresCandleStore,
    instrument: str,
    *,
    start_utc: datetime,
    end_utc: datetime,
) -> list[dict[str, str]]:
    prev: datetime | None = None
    max_gap = timedelta(0)
    gap_start: datetime | None = None
    for chunk in iter_m1_chunks(store, instrument=instrument, start_utc=start_utc, end_utc=end_utc):
        for row in chunk:
            ts = row["time_utc"].astimezone(UTC)
            if prev is not None and prev.weekday() < 5:
                delta = ts - prev
                if delta > timedelta(minutes=1) and delta > max_gap:
                    max_gap = delta
                    gap_start = prev
            prev = ts
    if gap_start is not None and max_gap > timedelta(minutes=5):
        return [{"start": gap_start.isoformat(), "minutes": int(max_gap.total_seconds() // 60)}]
    return []


def quality_for_pair(store: PostgresCandleStore, instrument: str) -> dict[str, Any]:
    pr = pair_range(store, instrument)
    base = quality_sql_base(store, instrument)
    expected = expected_weekday_minutes(pr.start_utc, pr.end_utc)
    missing = max(0, expected - base["distinct_timestamps"])
    report = {
        "instrument": instrument,
        "start_utc": pr.start_utc.isoformat(),
        "end_utc": pr.end_utc.isoformat(),
        "expected_weekday_minutes": expected,
        "missing_minutes": missing,
        "largest_gaps": scan_largest_gap(
            store, instrument, start_utc=pr.start_utc, end_utc=pr.end_utc
        ),
        **base,
    }
    report["status"] = classify_quality(report)
    return report


def _row_to_candle(row: dict[str, Any], *, instrument: str) -> Candle:
    def dec(v: Any) -> Decimal | None:
        return None if v is None else Decimal(str(v))

    return Candle(
        instrument=instrument,
        granularity="M1",
        time=row["time_utc"],
        complete=bool(row.get("complete")),
        volume=int(row.get("volume") or 0),
        bid_o=dec(row.get("bid_o")),
        bid_h=dec(row.get("bid_h")),
        bid_l=dec(row.get("bid_l")),
        bid_c=dec(row.get("bid_c")),
        ask_o=dec(row.get("ask_o")),
        ask_h=dec(row.get("ask_h")),
        ask_l=dec(row.get("ask_l")),
        ask_c=dec(row.get("ask_c")),
        mid_o=dec(row.get("mid_o")),
        mid_h=dec(row.get("mid_h")),
        mid_l=dec(row.get("mid_l")),
        mid_c=dec(row.get("mid_c")),
    )


@dataclass
class AggregateAccumulator:
    counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    omitted: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    incomplete: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    first_ts: dict[str, datetime | None] = field(default_factory=dict)
    last_ts: dict[str, datetime | None] = field(default_factory=dict)
    source_m1_per_bar: dict[str, list[int]] = field(default_factory=lambda: defaultdict(list))


def aggregate_chunk(acc: AggregateAccumulator, candles: list[Candle]) -> None:
    for target in TARGET_GRANULARITIES:
        result = aggregate_m1_candles(candles, target=target, missing_policy="omit")
        acc.omitted[target] += result.omitted_incomplete_blocks
        for cov in result.coverage:
            acc.source_m1_per_bar[target].append(cov.observed_minutes)
        for candle in result.candles:
            key = target
            acc.counts[key] += 1
            if not candle.complete:
                acc.incomplete[key] += 1
            ts = candle.time.astimezone(UTC)
            if key not in acc.first_ts or acc.first_ts[key] is None or ts < acc.first_ts[key]:
                acc.first_ts[key] = ts
            if key not in acc.last_ts or acc.last_ts[key] is None or ts > acc.last_ts[key]:
                acc.last_ts[key] = ts


def aggregation_coverage_for_pair(store: PostgresCandleStore, instrument: str) -> dict[str, Any]:
    pr = pair_range(store, instrument)
    acc = AggregateAccumulator()
    for chunk in iter_m1_chunks(store, instrument=instrument, start_utc=pr.start_utc, end_utc=pr.end_utc):
        candles = [_row_to_candle(row, instrument=instrument) for row in chunk]
        aggregate_chunk(acc, candles)
    expected_m1 = expected_weekday_minutes(pr.start_utc, pr.end_utc)
    timeframes: dict[str, Any] = {}
    for target in TARGET_GRANULARITIES:
        count = acc.counts.get(target, 0)
        samples = acc.source_m1_per_bar.get(target, [])
        timeframes[target] = {
            "bar_count": count,
            "first_timestamp": _iso(acc.first_ts.get(target)),
            "last_timestamp": _iso(acc.last_ts.get(target)),
            "omitted_incomplete_blocks": acc.omitted.get(target, 0),
            "incomplete_bars": acc.incomplete.get(target, 0),
            "avg_source_m1_per_bar": round(sum(samples) / len(samples), 2) if samples else 0,
            "coverage_pct_vs_m1": round(count / expected_m1 * 100, 4) if expected_m1 else 0,
        }
    return {"instrument": instrument, "expected_m1_minutes": expected_m1, "timeframes": timeframes}


def _candle_key(candle: Candle) -> datetime:
    return candle.time.astimezone(UTC)


def _float_close(a: Decimal | None, b: float | None, tol: float) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tol


def compare_h4_bars(native: Candle, derived: Candle) -> dict[str, Any] | None:
    if _candle_key(native) != _candle_key(derived):
        return None
    diffs: dict[str, float] = {}
    for field_name in ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"):
        n = getattr(native, field_name)
        d = getattr(derived, field_name)
        if not _float_close(n, float(d) if d is not None else None, OHLC_TOLERANCE):
            diffs[field_name] = abs(float(n) - float(d)) if n is not None and d is not None else -1
    if native.volume != derived.volume and abs(native.volume - derived.volume) > VOLUME_TOLERANCE:
        diffs["volume"] = abs(native.volume - derived.volume)
    if not diffs:
        return None
    return {"timestamp": _iso(native.time), "diffs": diffs}


def h4_drift_for_pair(store: PostgresCandleStore, instrument: str, *, max_examples: int = 25) -> dict[str, Any]:
    pr = pair_range(store, instrument)
    native_rows = store.query_candles(
        instrument=instrument, granularity="H4", start_utc=pr.start_utc, end_utc=pr.end_utc
    )
    if not native_rows:
        return {
            "instrument": instrument,
            "status": "WARN",
            "reason": "no_native_h4_in_store",
            "native_h4_count": 0,
            "derived_h4_count": 0,
        }
    native = [_row_to_candle(r, instrument=instrument) for r in native_rows]
    native_by_time = {_candle_key(c): c for c in native}
    derived_by_time: dict[datetime, Candle] = {}
    for chunk in iter_m1_chunks(store, instrument=instrument, start_utc=pr.start_utc, end_utc=pr.end_utc):
        candles = [_row_to_candle(row, instrument=instrument) for row in chunk]
        result = aggregate_m1_candles(candles, target="H4", missing_policy="omit")
        for candle in result.candles:
            derived_by_time[_candle_key(candle)] = candle
    overlap = sorted(set(native_by_time) & set(derived_by_time))
    matched = 0
    ohlc_mismatch = 0
    volume_mismatch = 0
    examples: list[dict[str, Any]] = []
    missing_in_derived = sorted(set(native_by_time) - set(derived_by_time))
    extra_in_derived = sorted(set(derived_by_time) - set(native_by_time))
    for ts in overlap:
        diff = compare_h4_bars(native_by_time[ts], derived_by_time[ts])
        if diff is None:
            matched += 1
        else:
            ohlc_mismatch += 1
            if "volume" in diff["diffs"]:
                volume_mismatch += 1
            if len(examples) < max_examples:
                examples.append(diff)
    status: Status = "PASS"
    if len(overlap) == 0:
        status = "FAIL"
    elif ohlc_mismatch / max(len(overlap), 1) > 0.01:
        status = "FAIL"
    elif missing_in_derived or extra_in_derived or ohlc_mismatch > 0:
        status = "WARN"
    likely_causes: list[str] = []
    if missing_in_derived:
        likely_causes.append("missing_minute_coverage")
    if ohlc_mismatch and volume_mismatch == 0:
        likely_causes.append("bid_ask_aggregation_difference")
    if ohlc_mismatch:
        likely_causes.append("timestamp_convention_or_alignment_difference")
    if not likely_causes and status == "PASS":
        likely_causes.append("within_tolerance")
    return {
        "instrument": instrument,
        "status": status,
        "native_h4_count": len(native_by_time),
        "derived_h4_count": len(derived_by_time),
        "overlap_count": len(overlap),
        "exact_match_count": matched,
        "ohlc_mismatch_count": ohlc_mismatch,
        "volume_mismatch_count": volume_mismatch,
        "missing_in_derived_count": len(missing_in_derived),
        "extra_in_derived_count": len(extra_in_derived),
        "likely_causes": likely_causes,
        "examples": examples,
    }


def d1agg_for_pair(store: PostgresCandleStore, instrument: str) -> dict[str, Any]:
    pr = pair_range(store, instrument)
    derived_h4: list[Candle] = []
    for chunk in iter_m1_chunks(store, instrument=instrument, start_utc=pr.start_utc, end_utc=pr.end_utc):
        candles = [_row_to_candle(row, instrument=instrument) for row in chunk]
        derived_h4.extend(aggregate_m1_candles(candles, target="H4", missing_policy="omit").candles)
    m1_d1 = aggregate_h4_to_d1(derived_h4, instrument=instrument)
    native_h4_rows = store.query_candles(
        instrument=instrument, granularity="H4", start_utc=pr.start_utc, end_utc=pr.end_utc
    )
    native_h4 = [_row_to_candle(r, instrument=instrument) for r in native_h4_rows]
    native_d1 = aggregate_h4_to_d1(native_h4, instrument=instrument) if native_h4 else None
    m1_by_time = {_candle_key(c): c for c in m1_d1.candles}
    ref_by_time = {_candle_key(c): c for c in native_d1.candles} if native_d1 else {}
    overlap = sorted(set(m1_by_time) & set(ref_by_time))
    mismatches = 0
    for ts in overlap:
        if compare_h4_bars(ref_by_time[ts], m1_by_time[ts]) is not None:
            mismatches += 1
    status: Status = "PASS" if mismatches == 0 and m1_d1.aggregated_count > 0 else (
        "WARN" if mismatches / max(len(overlap), 1) < 0.02 else "FAIL"
    )
    return {
        "instrument": instrument,
        "status": status,
        "m1_derived_d1agg_count": m1_d1.aggregated_count,
        "h4_derived_d1agg_count": native_d1.aggregated_count if native_d1 else 0,
        "overlap_count": len(overlap),
        "ohlc_mismatch_count": mismatches,
        "incomplete_days": m1_d1.incomplete_count,
        "ambiguous_days": m1_d1.ambiguous_count,
        "convention": "H4_first_five_to_13NY_D1AGG",
    }


def _frame_from_candles(candles: list[Candle]) -> pd.DataFrame:
    rows = []
    for c in candles:
        rows.append(
            {
                "time": _candle_key(c),
                "complete": c.complete,
                "value": float(c.mid_c) if c.mid_c is not None else float(c.bid_c or 0),
            }
        )
    frame = pd.DataFrame(rows).set_index("time")
    frame.index = pd.DatetimeIndex(frame.index)
    if frame.index.tz is None:
        frame.index = frame.index.tz_localize("UTC")
    return frame.sort_index()


def ltf_alignment_for_pair(
    store: PostgresCandleStore,
    instrument: str,
    *,
    execution_timeframe: str = "M15",
    sample_decisions: int = 500,
) -> dict[str, Any]:
    pr = pair_range(store, instrument)
    m15: list[Candle] = []
    h1: list[Candle] = []
    h4: list[Candle] = []
    d1: list[Candle] = []
    for chunk in iter_m1_chunks(
        store,
        instrument=instrument,
        start_utc=pr.start_utc,
        end_utc=min(pr.end_utc, pr.start_utc + timedelta(days=120)),
        chunk_days=30,
    ):
        candles = [_row_to_candle(row, instrument=instrument) for row in chunk]
        m15.extend(aggregate_m1_candles(candles, target=execution_timeframe, missing_policy="omit").candles)
        h1.extend(aggregate_m1_candles(candles, target="H1", missing_policy="omit").candles)
        h4.extend(aggregate_m1_candles(candles, target="H4", missing_policy="omit").candles)
        d1.extend(aggregate_m1_candles(candles, target="D1AGG", missing_policy="omit").candles)
    if len(m15) < 10:
        return {"instrument": instrument, "status": "FAIL", "reason": "insufficient_sample_bars"}
    decisions = pd.DatetimeIndex([c.time for c in m15[:: max(1, len(m15) // sample_decisions)]])
    aligned = align_ltf_execution_context(
        decisions,
        execution_timeframe=execution_timeframe,
        h1_frame=_frame_from_candles(h1),
        h4_frame=_frame_from_candles(h4),
        d1agg_frame=_frame_from_candles(d1),
        value_columns=["value"],
        max_staleness=pd.Timedelta("7D"),
    )
    violations = 0
    stale = 0
    unavailable = 0
    for prefix in ("h1", "h4", "d1agg"):
        time_col = f"{prefix}_feature_time"
        if time_col not in aligned.columns:
            unavailable += len(aligned)
            continue
        for decision_time, feature_time in zip(aligned.index, aligned[time_col], strict=False):
            if pd.isna(feature_time):
                unavailable += 1
                continue
            if feature_time > decision_time:
                violations += 1
            if decision_time - feature_time > pd.Timedelta("7D"):
                stale += 1
    status: Status = "PASS" if violations == 0 and unavailable < len(aligned) * 0.05 else "WARN"
    if violations > len(aligned) * 0.01:
        status = "FAIL"
    return {
        "instrument": instrument,
        "status": status,
        "execution_timeframe": execution_timeframe,
        "decision_samples": len(aligned),
        "lookahead_violations": violations,
        "stale_features": stale,
        "unavailable_features": unavailable,
    }


def preflight_for_pair(store: PostgresCandleStore, instrument: str) -> dict[str, Any]:
    pr = pair_range(store, instrument)
    m15: list[Candle] = []
    h1: list[Candle] = []
    h4: list[Candle] = []
    d1: list[Candle] = []
    for chunk in iter_m1_chunks(
        store,
        instrument=instrument,
        start_utc=pr.start_utc,
        end_utc=min(pr.end_utc, pr.start_utc + timedelta(days=60)),
        chunk_days=30,
    ):
        candles = [_row_to_candle(row, instrument=instrument) for row in chunk]
        m15.extend(aggregate_m1_candles(candles, target="M15", missing_policy="omit").candles)
        h1.extend(aggregate_m1_candles(candles, target="H1", missing_policy="omit").candles)
        h4.extend(aggregate_m1_candles(candles, target="H4", missing_policy="omit").candles)
        d1.extend(aggregate_m1_candles(candles, target="D1AGG", missing_policy="omit").candles)
    if len(m15) < 5:
        return {"instrument": instrument, "status": "FAIL", "errors": ["insufficient_m15_bars"]}
    exec_frame = CandleFrame.from_candles(instrument, "M15", m15)

    def ctx(candles: list[Candle], granularity: str) -> CandleFrame:
        return CandleFrame.from_candles(instrument, granularity, candles)

    signal_time = m15[len(m15) // 2].time
    result = run_ltf_backtest_preflight(
        exec_frame,
        signal_time=signal_time,
        context_frames={"H1": ctx(h1, "H1"), "H4": ctx(h4, "H4"), "D1AGG": ctx(d1, "D1AGG")},
        time_stop_bars=48,
    )
    return {
        "instrument": instrument,
        "status": "PASS" if result.ok else "FAIL",
        "errors": result.errors,
        "execution_timeframe": result.execution_timeframe,
        "next_bar_open_available": result.next_bar_open_time is not None,
        "time_stop_bars": result.time_stop_bars,
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    return str(value)


def overall_status(statuses: list[Status]) -> Status:
    if "FAIL" in statuses:
        return "FAIL"
    if "WARN" in statuses:
        return "WARN"
    return "PASS"
