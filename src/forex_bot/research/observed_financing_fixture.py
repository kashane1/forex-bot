"""Sanitized observed OANDA practice financing fixture schema (v1)."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_INSTRUMENT = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")
_RAW_ACCOUNT = re.compile(r"^\d{3}-\d{3}-\d+-\d{3}$")
_TOKENISH = re.compile(r"(?i)(bearer|api[_-]?key|access[_-]?token|authorization)")

KNOWN_FINANCING_TYPES: frozenset[str] = frozenset(
    {
        "DAILY_FINANCING",
        "FINANCING",
        "DIVIDEND_ADJUSTMENT",
    }
)


class ObservedFinancingEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    local_id: str
    transaction_id_hash: str
    instrument: str | None = None
    side: str | None = None
    units: str | None = None
    financing_home: str
    account_currency: str
    transaction_time: str
    effective_date: str
    transaction_type: str
    raw_type: str
    redaction_status: Literal["sanitized"] = "sanitized"

    @field_validator("instrument")
    @classmethod
    def _instrument(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not _INSTRUMENT.fullmatch(v):
            raise ValueError(f"invalid instrument: {v!r}")
        return v

    @field_validator("transaction_id_hash", "local_id")
    @classmethod
    def _no_raw_ids(cls, v: str) -> str:
        if _RAW_ACCOUNT.search(v):
            raise ValueError("raw account id pattern in fixture id field")
        return v


class ObservedFinancingFixture(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fixture_version: int = 1
    source: Literal["oanda_practice_observed"] = "oanda_practice_observed"
    captured_at_utc: str
    account_id_hash: str
    environment: Literal["practice"] = "practice"
    account_currency: str = "USD"
    capture_window: dict[str, str] = Field(default_factory=dict)
    redaction_status: Literal["sanitized"] = "sanitized"
    entries: list[ObservedFinancingEntry] = Field(default_factory=list)
    transaction_counts: dict[str, int] = Field(default_factory=dict)

    @field_validator("account_id_hash")
    @classmethod
    def _hash(cls, v: str) -> str:
        if not _HEX64.fullmatch(v):
            raise ValueError("account_id_hash must be 64-char hex sha256")
        return v

    @field_validator("captured_at_utc", mode="before")
    @classmethod
    def _ts(cls, v: str) -> str:
        datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return str(v)


def classify_transaction_type(raw_type: str) -> Literal["financing", "unknown"]:
    if raw_type in KNOWN_FINANCING_TYPES:
        return "financing"
    return "unknown"


def reject_secret_like_strings(payload: Any, *, path: str = "") -> None:
    if isinstance(payload, dict):
        for k, v in payload.items():
            if _TOKENISH.search(str(k)):
                raise ValueError(f"token-like key at {path}.{k}")
            reject_secret_like_strings(v, path=f"{path}.{k}")
    elif isinstance(payload, list):
        for i, item in enumerate(payload):
            reject_secret_like_strings(item, path=f"{path}[{i}]")
    elif isinstance(payload, str):
        if _RAW_ACCOUNT.fullmatch(payload.strip()):
            raise ValueError(f"raw account id at {path}")
        if _TOKENISH.search(payload) and len(payload) > 20:
            raise ValueError(f"token-like string at {path}")


def validate_observed_fixture(data: dict[str, Any]) -> ObservedFinancingFixture:
    reject_secret_like_strings(data)
    return ObservedFinancingFixture.model_validate(data)


def effective_date_from_time(iso_time: str) -> str:
    return datetime.fromisoformat(iso_time.replace("Z", "+00:00")).date().isoformat()


def empty_observed_fixture(
    *,
    account_id_hash: str,
    captured_at_utc: str,
    capture_window: dict[str, str],
    account_currency: str = "USD",
) -> ObservedFinancingFixture:
    return ObservedFinancingFixture(
        captured_at_utc=captured_at_utc,
        account_id_hash=account_id_hash,
        capture_window=capture_window,
        account_currency=account_currency,
        entries=[],
        transaction_counts={
            "total": 0,
            "financing": 0,
            "unknown": 0,
        },
    )
