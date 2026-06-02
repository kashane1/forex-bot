"""Validation helpers for the crypto derivatives layer (BTC/ETH perps only).

Operates on the canonical record dataclasses from ``derivatives_models`` (storage
agnostic — no DB binding is forced this sprint). Mirrors the spot validation
status model (PASS / WARN / FAIL) in ``research/crypto/validation.py``.

This module runs NO factor diagnostics and infers NO edge — it only checks data
integrity for a future Family E exploratory diagnostics sprint.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

from research.crypto.derivatives_models import (
    FundingRateRecord,
    MarkIndexRecord,
    OpenInterestRecord,
    PerpOhlcvRecord,
)
from research.crypto.derivatives_registry import CANONICAL_PERPS

Status = Literal["PASS", "WARN", "FAIL"]

# Wide sanity bands (NOT trading thresholds) — flag obviously broken rows.
_FUNDING_ABS_SANITY = 0.003  # 0.3% per 8h interval
_BASIS_BPS_SANITY = 5000.0  # 50% basis is absurd for BTC/ETH perps


@dataclass
class ValidationIssue:
    code: str
    message: str
    level: Status = "WARN"


@dataclass
class DerivativesClassValidation:
    canonical_id: str
    data_class: str
    venue: str
    status: Status
    row_count: int
    issues: list[ValidationIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_id": self.canonical_id,
            "data_class": self.data_class,
            "venue": self.venue,
            "status": self.status,
            "row_count": self.row_count,
            "issues": [{"code": i.code, "message": i.message, "level": i.level} for i in self.issues],
        }


def _worst(issues: Sequence[ValidationIssue], *, base: Status = "PASS") -> Status:
    order = {"PASS": 0, "WARN": 1, "FAIL": 2}
    current = base
    for issue in issues:
        if order[issue.level] > order[current]:
            current = issue.level
    return current


def _check_btc_eth_only(canonical_id: str, issues: list[ValidationIssue]) -> None:
    if canonical_id not in CANONICAL_PERPS:
        issues.append(
            ValidationIssue("non_btc_eth", f"unauthorized perp {canonical_id!r}", "FAIL")
        )


def _check_monotonic(times: list[Any], issues: list[ValidationIssue]) -> None:
    if times != sorted(times):
        issues.append(ValidationIssue("non_monotonic", "timestamps not sorted ascending", "FAIL"))
    if len(set(times)) != len(times):
        issues.append(ValidationIssue("duplicate_ts", "duplicate timestamps present", "FAIL"))


def validate_funding(records: Sequence[FundingRateRecord]) -> DerivativesClassValidation:
    issues: list[ValidationIssue] = []
    canonical = records[0].canonical_id if records else "?"
    venue = records[0].venue if records else "?"
    if not records:
        issues.append(ValidationIssue("empty", "no funding records", "WARN"))
        return DerivativesClassValidation(canonical, "funding", venue, "WARN", 0, issues)
    _check_btc_eth_only(canonical, issues)
    times = [r.funding_time_utc for r in records]
    _check_monotonic(times, issues)
    # funding interval consistency
    intervals = {r.funding_interval_hours for r in records}
    if len(intervals) > 1:
        issues.append(ValidationIssue("mixed_interval", f"mixed funding intervals {intervals}", "WARN"))
    interval_h = records[0].funding_interval_hours
    for prev, cur in zip(times, times[1:], strict=False):
        gap = (cur - prev).total_seconds() / 3600.0
        if gap > interval_h * 1.5:
            issues.append(
                ValidationIssue("funding_gap", f"gap {gap:.1f}h > {interval_h}h cadence", "WARN")
            )
            break
    for r in records:
        if abs(r.funding_rate) > _FUNDING_ABS_SANITY:
            issues.append(
                ValidationIssue("funding_outlier", f"|rate|={abs(r.funding_rate):.4f} extreme", "WARN")
            )
            break
    return DerivativesClassValidation(
        canonical, "funding", venue, _worst(issues), len(records), issues
    )


def validate_open_interest(records: Sequence[OpenInterestRecord]) -> DerivativesClassValidation:
    issues: list[ValidationIssue] = []
    canonical = records[0].canonical_id if records else "?"
    venue = records[0].venue if records else "?"
    if not records:
        # OI history is a known free-data gap — absence is WARN, not FAIL.
        issues.append(ValidationIssue("oi_unavailable", "no open-interest records", "WARN"))
        return DerivativesClassValidation(canonical, "open_interest", venue, "WARN", 0, issues)
    _check_btc_eth_only(canonical, issues)
    _check_monotonic([r.time_utc for r in records], issues)
    if all(r.open_interest_base is None and r.open_interest_usd is None for r in records):
        issues.append(ValidationIssue("oi_all_null", "every OI value null", "FAIL"))
    return DerivativesClassValidation(
        canonical, "open_interest", venue, _worst(issues), len(records), issues
    )


def validate_perp_ohlcv(records: Sequence[PerpOhlcvRecord]) -> DerivativesClassValidation:
    issues: list[ValidationIssue] = []
    canonical = records[0].canonical_id if records else "?"
    venue = records[0].venue if records else "?"
    if not records:
        issues.append(ValidationIssue("empty", "no perp OHLCV records", "WARN"))
        return DerivativesClassValidation(canonical, "perp_ohlcv", venue, "WARN", 0, issues)
    _check_btc_eth_only(canonical, issues)
    _check_monotonic([r.time_utc for r in records], issues)
    for r in records:
        if r.high < r.low or min(r.open, r.high, r.low, r.close) <= 0:
            issues.append(ValidationIssue("ohlcv_insane", f"bad OHLC at {r.time_utc}", "FAIL"))
            break
    return DerivativesClassValidation(
        canonical, "perp_ohlcv", venue, _worst(issues), len(records), issues
    )


def validate_mark_index(records: Sequence[MarkIndexRecord]) -> DerivativesClassValidation:
    issues: list[ValidationIssue] = []
    canonical = records[0].canonical_id if records else "?"
    venue = records[0].venue if records else "?"
    if not records:
        issues.append(ValidationIssue("empty", "no mark/index records", "WARN"))
        return DerivativesClassValidation(canonical, "mark_index", venue, "WARN", 0, issues)
    _check_btc_eth_only(canonical, issues)
    _check_monotonic([r.time_utc for r in records], issues)
    if all(r.mark_close is None and r.index_close is None for r in records):
        issues.append(ValidationIssue("mark_index_all_null", "every mark/index null", "FAIL"))
    return DerivativesClassValidation(
        canonical, "mark_index", venue, _worst(issues), len(records), issues
    )


def basis_computable(
    perp: Sequence[PerpOhlcvRecord], spot_times: Sequence[Any]
) -> tuple[int, int]:
    """Return ``(matched_buckets, total_perp_buckets)`` for spot/perp basis.

    A basis row is computable only where a perp bar shares a UTC bucket with a
    spot bar. Reports overlap so the diagnostics sprint knows basis coverage.
    """
    spot_set = set(spot_times)
    matched = sum(1 for r in perp if r.time_utc in spot_set)
    return matched, len(perp)


def summarize(validations: Sequence[DerivativesClassValidation]) -> dict[str, Any]:
    statuses = [v.status for v in validations]
    overall: Status = "PASS"
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "WARN" in statuses:
        overall = "WARN"
    return {
        "overall_status": overall,
        "class_count": len(validations),
        "classes": [v.to_dict() for v in validations],
    }
