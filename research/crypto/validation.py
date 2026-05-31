"""Crypto Postgres store validation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from forex_bot.data.postgres_candle_store import CandleRecord, PostgresCandleStore, validate_candle_record

Status = Literal["PASS", "WARN", "FAIL"]


@dataclass
class ValidationIssue:
    code: str
    message: str


@dataclass
class CryptoStoreValidation:
    instrument: str
    granularity: str
    start_utc: datetime
    end_utc: datetime
    status: Status
    expected_bars: int
    actual_bars: int
    coverage_ratio: float
    gap_count: int
    issues: list[ValidationIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "instrument": self.instrument,
            "granularity": self.granularity,
            "start_utc": self.start_utc.isoformat(),
            "end_utc": self.end_utc.isoformat(),
            "status": self.status,
            "expected_bars": self.expected_bars,
            "actual_bars": self.actual_bars,
            "coverage_ratio": round(self.coverage_ratio, 6),
            "gap_count": self.gap_count,
            "issues": [{"code": i.code, "message": i.message} for i in self.issues],
        }


def expected_m1_bars(start_utc: datetime, end_utc: datetime) -> int:
    start = start_utc.astimezone(UTC).replace(second=0, microsecond=0)
    end = end_utc.astimezone(UTC).replace(second=0, microsecond=0)
    if end < start:
        return 0
    return int((end - start).total_seconds() // 60) + 1


def _fetch_candles(
    store: PostgresCandleStore,
    *,
    instrument: str,
    granularity: str,
    start_utc: datetime,
    end_utc: datetime,
) -> list[dict[str, Any]]:
    sql = f"""
SELECT time_utc, complete, volume,
       bid_o, bid_h, bid_l, bid_c,
       ask_o, ask_h, ask_l, ask_c,
       mid_o, mid_h, mid_l, mid_c
FROM {store.config.schema}.candles
WHERE instrument = %s AND granularity = %s
  AND time_utc >= %s AND time_utc <= %s
ORDER BY time_utc ASC
"""
    with store.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (instrument, granularity, start_utc, end_utc))
            columns = [desc.name for desc in cur.description]
            return [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]


def validate_crypto_series(
    store: PostgresCandleStore,
    *,
    instrument: str,
    granularity: str,
    start_utc: datetime,
    end_utc: datetime,
    min_coverage: float = 0.995,
) -> CryptoStoreValidation:
    rows = _fetch_candles(
        store,
        instrument=instrument,
        granularity=granularity,
        start_utc=start_utc,
        end_utc=end_utc,
    )
    expected = expected_m1_bars(start_utc, end_utc) if granularity == "M1" else len(rows)
    issues: list[ValidationIssue] = []
    gap_count = 0
    prev: datetime | None = None

    for row in rows:
        record = CandleRecord(
            instrument=instrument,
            granularity=granularity,
            time_utc=row["time_utc"],
            complete=bool(row["complete"]),
            volume=int(row["volume"] or 0),
            bid_o=row["bid_o"],
            bid_h=row["bid_h"],
            bid_l=row["bid_l"],
            bid_c=row["bid_c"],
            ask_o=row["ask_o"],
            ask_h=row["ask_h"],
            ask_l=row["ask_l"],
            ask_c=row["ask_c"],
            mid_o=row["mid_o"],
            mid_h=row["mid_h"],
            mid_l=row["mid_l"],
            mid_c=row["mid_c"],
        )
        try:
            validate_candle_record(record)
        except ValueError as exc:
            issues.append(ValidationIssue("ohlc_invalid", str(exc)))
        if int(row["volume"] or 0) < 0:
            issues.append(ValidationIssue("negative_volume", f"negative volume at {row['time_utc']}"))
        ts = row["time_utc"].astimezone(UTC)
        if prev is not None:
            delta = int((ts - prev).total_seconds() // 60)
            if delta <= 0:
                issues.append(ValidationIssue("non_monotonic", f"duplicate or backward ts {ts.isoformat()}"))
            elif granularity == "M1" and delta > 1:
                gap_count += delta - 1
        prev = ts

    actual = len(rows)
    coverage = actual / expected if expected else 0.0
    if coverage < min_coverage:
        issues.append(
            ValidationIssue(
                "coverage_low",
                f"coverage {coverage:.4f} below threshold {min_coverage}",
            )
        )
    if gap_count:
        issues.append(ValidationIssue("gaps_detected", f"{gap_count} missing M1 bars in window"))

    status: Status = "PASS"
    if issues:
        status = "FAIL" if any(i.code in {"ohlc_invalid", "non_monotonic", "coverage_low"} for i in issues) else "WARN"

    return CryptoStoreValidation(
        instrument=instrument,
        granularity=granularity,
        start_utc=start_utc.astimezone(UTC),
        end_utc=end_utc.astimezone(UTC),
        status=status,
        expected_bars=expected,
        actual_bars=actual,
        coverage_ratio=coverage,
        gap_count=gap_count,
        issues=issues,
    )
