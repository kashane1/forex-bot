"""Tests for research/financing/observed.py parser and sanitizer."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from research.financing.observed import (
    REDACTED_ACCOUNT,
    REDACTED_REQUEST,
    REDACTED_USER,
    flatten_sanitized_events,
    parse_daily_financing_transaction,
    parse_transactions_batch,
    redact_trade_id,
    sanitize_identifier_fields,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "observed_financing"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_sanitize_identifier_fields() -> None:
    raw = {
        "accountID": "001-001-1234567-001",
        "userID": "u-123",
        "requestID": "r-456",
        "type": "DAILY_FINANCING",
    }
    out = sanitize_identifier_fields(raw)
    assert out["accountID"] == REDACTED_ACCOUNT
    assert out["userID"] == REDACTED_USER
    assert out["requestID"] == REDACTED_REQUEST


def test_parse_daily_financing_one_position() -> None:
    tx = parse_daily_financing_transaction(_load("daily_financing_one_position.json"))
    assert tx is not None
    assert tx.account_financing_mode == "SECOND_BY_SECOND"
    assert len(tx.position_financings) == 1
    pf = tx.position_financings[0]
    assert pf.instrument == "EUR_USD"
    assert pf.base_financing == "-0.2000"
    assert pf.quote_financing == "-0.2500"
    assert len(pf.open_trade_financings) == 1
    assert pf.open_trade_financings[0].financing_rate == "-0.00012"


def test_parse_daily_financing_multi_position() -> None:
    tx = parse_daily_financing_transaction(_load("daily_financing_multi_position.json"))
    assert tx is not None
    assert len(tx.position_financings) == 3
    events = flatten_sanitized_events(tx)
    assert len(events) == 4  # 2 EUR trades + 1 JPY + 1 GBP position-level


def test_parse_daily_financing_no_open_trades() -> None:
    tx = parse_daily_financing_transaction(_load("daily_financing_no_open_trades.json"))
    assert tx is not None
    assert len(tx.position_financings[0].open_trade_financings) == 0


def test_non_daily_financing_ignored() -> None:
    assert parse_daily_financing_transaction(_load("non_daily_financing.json")) is None


def test_negative_and_positive_financing_preserved() -> None:
    _, events = parse_transactions_batch([
        _load("daily_financing_multi_position.json"),
    ])
    jpy = next(e for e in events if e.instrument == "USD_JPY")
    assert Decimal(jpy.financing) > 0
    eur = next(e for e in events if e.instrument == "EUR_USD")
    assert Decimal(eur.financing) < 0


def test_trade_ids_redacted_stably() -> None:
    a = redact_trade_id("7001")
    b = redact_trade_id("7001")
    c = redact_trade_id("7002")
    assert a == b
    assert a != c
    assert a.startswith("trade_")


def test_batch_filters_non_daily() -> None:
    parsed, events = parse_transactions_batch([
        _load("non_daily_financing.json"),
        _load("daily_financing_one_position.json"),
    ])
    assert len(parsed) == 1
    assert len(events) == 1
