"""Observed OANDA DAILY_FINANCING parsing and sanitization.

Import-isolated from ``forex_bot``. Diagnostic only —
``strategy_evidence: false``.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_INSTRUMENT = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")

REDACTED_ACCOUNT = "REDACTED_ACCOUNT"
REDACTED_USER = "REDACTED_USER"
REDACTED_REQUEST = "REDACTED_REQUEST"


def hash_account_id(account_id: str) -> str:
    return hashlib.sha256(account_id.strip().encode("utf-8")).hexdigest()


def redact_trade_id(trade_id: str) -> str:
    digest = hashlib.sha256(trade_id.encode("utf-8")).hexdigest()[:12]
    return f"trade_{digest}"


def redact_transaction_id(transaction_id: str) -> str:
    digest = hashlib.sha256(transaction_id.encode("utf-8")).hexdigest()[:12]
    return f"tx_{digest}"


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _parse_rfc3339(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class SanitizedOpenTradeFinancing(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    trade_id_redacted: str
    financing: str
    units: str | None = None
    financing_rate: str | None = None


class SanitizedPositionFinancing(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instrument: str
    financing: str
    base_financing: str | None = None
    quote_financing: str | None = None
    open_trade_financings: list[SanitizedOpenTradeFinancing] = Field(default_factory=list)


class SanitizedDailyFinancingTransaction(BaseModel):
    """One sanitized DAILY_FINANCING transaction."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    transaction_id_redacted: str
    time: str
    financing: str
    account_balance: str | None = None
    account_financing_mode: str | None = None
    position_financings: list[SanitizedPositionFinancing] = Field(default_factory=list)


class SanitizedFinancingEvent(BaseModel):
    """Flat event row for overlay / fixture compatibility."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    transaction_id_redacted: str
    instrument: str | None = None
    trade_id_redacted: str | None = None
    units: str | None = None
    financing: str
    time: str


def sanitize_identifier_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a copy with account/user/request IDs redacted."""
    out = dict(payload)
    if "accountID" in out:
        out["accountID"] = REDACTED_ACCOUNT
    if "userID" in out:
        out["userID"] = REDACTED_USER
    if "requestID" in out:
        out["requestID"] = REDACTED_REQUEST
    return out


def parse_daily_financing_transaction(
    payload: dict[str, Any],
) -> SanitizedDailyFinancingTransaction | None:
    """Parse one DAILY_FINANCING transaction; ignore other types."""
    if payload.get("type") != "DAILY_FINANCING":
        return None

    tx_id = str(payload["id"])
    when = _parse_rfc3339(payload.get("time", "1970-01-01T00:00:00Z"))
    total_fin = _decimal(payload.get("financing"))
    balance = _decimal(payload.get("accountBalance"))

    position_rows: list[SanitizedPositionFinancing] = []
    for pf in payload.get("positionFinancings") or []:
        instrument = pf.get("instrument")
        if not instrument or not _INSTRUMENT.fullmatch(instrument):
            continue
        pf_fin = _decimal(pf.get("financing"))
        base_fin = _decimal(pf.get("baseFinancing"))
        quote_fin = _decimal(pf.get("quoteFinancing"))
        open_rows: list[SanitizedOpenTradeFinancing] = []
        for otf in pf.get("openTradeFinancings") or []:
            raw_trade = otf.get("tradeID")
            if not raw_trade:
                continue
            otf_fin = _decimal(otf.get("financing"))
            otf_units = _decimal(otf.get("units"))
            otf_rate = _decimal(otf.get("financingRate"))
            open_rows.append(
                SanitizedOpenTradeFinancing(
                    trade_id_redacted=redact_trade_id(str(raw_trade)),
                    financing=str(otf_fin if otf_fin is not None else Decimal("0")),
                    units=str(otf_units) if otf_units is not None else None,
                    financing_rate=str(otf_rate) if otf_rate is not None else None,
                )
            )
        position_rows.append(
            SanitizedPositionFinancing(
                instrument=instrument,
                financing=str(pf_fin if pf_fin is not None else Decimal("0")),
                base_financing=str(base_fin) if base_fin is not None else None,
                quote_financing=str(quote_fin) if quote_fin is not None else None,
                open_trade_financings=open_rows,
            )
        )

    return SanitizedDailyFinancingTransaction(
        transaction_id_redacted=redact_transaction_id(tx_id),
        time=when.isoformat(),
        financing=str(total_fin if total_fin is not None else Decimal("0")),
        account_balance=str(balance) if balance is not None else None,
        account_financing_mode=payload.get("accountFinancingMode"),
        position_financings=position_rows,
    )


def flatten_sanitized_events(
    tx: SanitizedDailyFinancingTransaction,
) -> list[SanitizedFinancingEvent]:
    """Expand a sanitized DAILY_FINANCING into flat event rows."""
    events: list[SanitizedFinancingEvent] = []
    if tx.position_financings:
        for pf in tx.position_financings:
            if pf.open_trade_financings:
                for otf in pf.open_trade_financings:
                    events.append(
                        SanitizedFinancingEvent(
                            transaction_id_redacted=tx.transaction_id_redacted,
                            instrument=pf.instrument,
                            trade_id_redacted=otf.trade_id_redacted,
                            units=otf.units,
                            financing=otf.financing,
                            time=tx.time,
                        )
                    )
            else:
                events.append(
                    SanitizedFinancingEvent(
                        transaction_id_redacted=tx.transaction_id_redacted,
                        instrument=pf.instrument,
                        trade_id_redacted=None,
                        units=None,
                        financing=pf.financing,
                        time=tx.time,
                    )
                )
    else:
        events.append(
            SanitizedFinancingEvent(
                transaction_id_redacted=tx.transaction_id_redacted,
                instrument=None,
                trade_id_redacted=None,
                units=None,
                financing=tx.financing,
                time=tx.time,
            )
        )
    return events


def parse_transactions_batch(
    transactions: list[dict[str, Any]],
) -> tuple[list[SanitizedDailyFinancingTransaction], list[SanitizedFinancingEvent]]:
    """Parse and flatten a batch; non-DAILY_FINANCING ignored."""
    parsed: list[SanitizedDailyFinancingTransaction] = []
    events: list[SanitizedFinancingEvent] = []
    for raw in transactions:
        if raw.get("type") != "DAILY_FINANCING":
            continue
        tx = parse_daily_financing_transaction(raw)
        if tx is None:
            continue
        parsed.append(tx)
        events.extend(flatten_sanitized_events(tx))
    return parsed, events
