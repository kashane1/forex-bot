"""Observed-financing-event capture tests
(Phase 4, infra-execution-fidelity-001).

Capture infrastructure for FUTURE paper/demo observation. These tests
use fixture transactions only — no OANDA connection, no live data — and
prove the account id is hashed (never stored raw), the DAILY_FINANCING
breakdown is parsed correctly, financing signs are preserved, and the
repository stores and retrieves events idempotently.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from forex_bot.broker.mapping import map_daily_financing, observed_financing_events
from forex_bot.data.repositories import ObservedFinancingEventRepo
from forex_bot.domain.transactions import (
    ObservedFinancingEvent,
    hash_account_id,
)
from tests.fixtures.oanda_payloads import (
    DAILY_FINANCING_NO_BREAKDOWN,
    DAILY_FINANCING_TRANSACTION,
    ORDER_FILL_WITH_FINANCING,
    TRANSACTIONS_SINCEID_RESPONSE,
)

_RAW_ACCOUNT = "001-001-1234567-001"


def _by(events, instrument, trade_id):
    matches = [e for e in events if e.instrument == instrument and e.trade_id == trade_id]
    assert len(matches) == 1, f"expected one event for {instrument}/{trade_id}"
    return matches[0]


# --------------------------------------------------------------------------
# Account-id hashing / redaction
# --------------------------------------------------------------------------


def test_hash_account_id_is_deterministic_64_hex():
    h = hash_account_id(_RAW_ACCOUNT)
    assert h == hash_account_id(_RAW_ACCOUNT)
    assert len(h) == 64 and all(c in "0123456789abcdef" for c in h)
    assert h != hash_account_id("001-001-9999999-001")
    assert _RAW_ACCOUNT not in h


def test_event_refuses_a_raw_account_id():
    """The model fails closed: a raw account id cannot be stored in the
    account_id_hash field."""
    with pytest.raises(ValueError, match="SHA-256"):
        ObservedFinancingEvent(
            transaction_id="1",
            account_id_hash=_RAW_ACCOUNT,
            financing=Decimal("-0.1"),
            currency="USD",
            time="2024-03-04T22:00:00Z",  # type: ignore[arg-type]
            source="fixture",
        )


def test_event_accepts_a_proper_hash():
    event = ObservedFinancingEvent(
        transaction_id="1",
        account_id_hash=hash_account_id(_RAW_ACCOUNT),
        financing=Decimal("-0.1"),
        currency="USD",
        time="2024-03-04T22:00:00Z",  # type: ignore[arg-type]
        source="fixture",
    )
    assert event.account_id_hash == hash_account_id(_RAW_ACCOUNT)


# --------------------------------------------------------------------------
# DAILY_FINANCING parsing
# --------------------------------------------------------------------------


def test_map_daily_financing_breaks_down_per_trade():
    events = map_daily_financing(
        DAILY_FINANCING_TRANSACTION, source="fixture", account_currency="USD"
    )
    # EUR_USD x2 trades + USD_JPY x1 trade + GBP_USD position-level = 4.
    assert len(events) == 4
    assert all(e.transaction_id == "512" for e in events)
    assert all(e.currency == "USD" for e in events)
    assert all(e.source == "fixture" for e in events)


def test_map_daily_financing_preserves_signs():
    events = map_daily_financing(
        DAILY_FINANCING_TRANSACTION, source="fixture", account_currency="USD"
    )
    assert _by(events, "EUR_USD", "200").financing == Decimal("-0.3000")  # debit
    assert _by(events, "EUR_USD", "205").financing == Decimal("-0.2123")  # debit
    assert _by(events, "USD_JPY", "210").financing == Decimal("0.3111")   # credit
    # GBP_USD has no per-trade breakdown -> a position-level event.
    assert _by(events, "GBP_USD", None).financing == Decimal("-0.6222")


def test_map_daily_financing_never_exposes_the_raw_account_id():
    events = map_daily_financing(
        DAILY_FINANCING_TRANSACTION, source="fixture", account_currency="USD"
    )
    expected = hash_account_id(_RAW_ACCOUNT)
    for e in events:
        assert e.account_id_hash == expected
        assert _RAW_ACCOUNT not in str(e.model_dump())


def test_map_daily_financing_account_level_fallback():
    events = map_daily_financing(
        DAILY_FINANCING_NO_BREAKDOWN, source="fixture", account_currency="USD"
    )
    assert len(events) == 1
    only = events[0]
    assert only.instrument is None and only.trade_id is None
    assert only.financing == Decimal("-0.4500")


def test_map_daily_financing_rejects_a_non_financing_transaction():
    with pytest.raises(ValueError, match="DAILY_FINANCING"):
        map_daily_financing(
            {"id": "1", "type": "ORDER_FILL"},
            source="fixture",
            account_currency="USD",
        )


# --------------------------------------------------------------------------
# General dispatcher
# --------------------------------------------------------------------------


def test_observed_financing_events_dispatches_daily_financing():
    events = observed_financing_events(
        DAILY_FINANCING_TRANSACTION, source="fixture", account_currency="USD"
    )
    assert len(events) == 4


def test_observed_financing_events_handles_order_fill_financing():
    events = observed_financing_events(
        ORDER_FILL_WITH_FINANCING, source="fixture", account_currency="USD"
    )
    assert len(events) == 1
    event = events[0]
    assert event.instrument == "EUR_USD"
    assert event.trade_id == "200"  # from tradesClosed
    assert event.financing == Decimal("-0.1850")
    assert event.units == Decimal("-100")


def test_observed_financing_events_empty_for_a_transaction_with_no_financing():
    no_financing_tx = TRANSACTIONS_SINCEID_RESPONSE["transactions"][0]
    assert "financing" not in no_financing_tx
    assert observed_financing_events(
        no_financing_tx, source="fixture", account_currency="USD"
    ) == []


# --------------------------------------------------------------------------
# Repository
# --------------------------------------------------------------------------


def test_repo_starts_empty(temp_db):
    repo = ObservedFinancingEventRepo(temp_db)
    assert repo.count() == 0
    assert repo.list() == []


def test_repo_stores_and_retrieves_events(temp_db):
    repo = ObservedFinancingEventRepo(temp_db)
    events = map_daily_financing(
        DAILY_FINANCING_TRANSACTION, source="fixture", account_currency="USD"
    )
    inserted = repo.insert_many(events)
    assert inserted == 4
    assert repo.count() == 4

    eur = repo.list(instrument="EUR_USD")
    assert len(eur) == 2
    assert {e.trade_id for e in eur} == {"200", "205"}

    by_account = repo.list(account_id_hash=hash_account_id(_RAW_ACCOUNT))
    assert len(by_account) == 4


def test_repo_roundtrip_preserves_fields(temp_db):
    repo = ObservedFinancingEventRepo(temp_db)
    repo.insert_many(
        map_daily_financing(
            DAILY_FINANCING_TRANSACTION, source="fixture", account_currency="USD"
        )
    )
    jpy = repo.list(instrument="USD_JPY")[0]
    assert jpy.trade_id == "210"
    assert jpy.financing == Decimal("0.3111")
    assert jpy.currency == "USD"
    assert jpy.source == "fixture"


def test_repo_insert_is_idempotent(temp_db):
    repo = ObservedFinancingEventRepo(temp_db)
    events = map_daily_financing(
        DAILY_FINANCING_TRANSACTION, source="fixture", account_currency="USD"
    )
    assert repo.insert_many(events) == 4
    # Re-capturing the same transaction must add nothing.
    assert repo.insert_many(events) == 0
    assert repo.count() == 4


def test_repo_stores_only_hashed_account_ids(temp_db):
    """Defense in depth: no stored row may contain the raw account id."""
    repo = ObservedFinancingEventRepo(temp_db)
    repo.insert_many(
        map_daily_financing(
            DAILY_FINANCING_TRANSACTION, source="fixture", account_currency="USD"
        )
    )
    rows = temp_db.fetchall("SELECT account_id_hash FROM observed_financing_events")
    assert rows
    for row in rows:
        assert row["account_id_hash"] != _RAW_ACCOUNT
        assert len(row["account_id_hash"]) == 64
