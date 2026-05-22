"""Broker-side transactions and stream heartbeats."""

from __future__ import annotations

import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    transaction_id: str
    type: str
    account_id: str
    time: datetime
    instrument: str | None = None
    units: Decimal | None = None
    price: Decimal | None = None
    reason: str | None = None
    pl: Decimal | None = None
    financing: Decimal | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class Heartbeat(BaseModel):
    model_config = ConfigDict(extra="ignore")

    time: datetime
    last_transaction_id: str | None = None


def hash_account_id(account_id: str) -> str:
    """SHA-256 hex digest of an OANDA account id.

    Observed financing events store only this hash — never the raw
    account id — so a committed research database can never leak an
    account identifier. The digest is stable, so events from the same
    account still group together.
    """
    return hashlib.sha256(account_id.strip().encode("utf-8")).hexdigest()


class ObservedFinancingEvent(BaseModel):
    """One financing charge or credit observed from a broker transaction.

    This is **capture infrastructure for future paper/demo observation**.
    No current loop produces these — the research freeze keeps every
    order-capable loop refused — and recording observed events does NOT
    solve historical financing. See
    docs/research/OBSERVED_FINANCING_CAPTURE.md.

    `account_id_hash` is the redacted account identity: the model refuses
    a value that is not a SHA-256 digest, so a raw account id can never
    be stored by mistake.
    """

    model_config = ConfigDict(extra="ignore", frozen=True)

    transaction_id: str
    account_id_hash: str
    instrument: str | None = None
    trade_id: str | None = None
    units: Decimal | None = None
    financing: Decimal  # signed — a credit is > 0, a debit is < 0
    currency: str  # the account home currency the financing settled in
    time: datetime
    source: str  # provenance, e.g. "oanda-practice" or "fixture"

    @field_validator("account_id_hash")
    @classmethod
    def _must_be_a_hash(cls, value: str) -> str:
        if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError(
                "account_id_hash must be a SHA-256 hex digest, never a raw "
                "account id — construct it with hash_account_id()"
            )
        return value

    @property
    def event_key(self) -> str:
        """Deterministic idempotency key. Re-capturing the same
        transaction yields the same key, so storage can dedupe."""
        raw = f"{self.transaction_id}|{self.instrument or ''}|{self.trade_id or ''}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()
