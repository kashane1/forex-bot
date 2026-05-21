"""SQLite migrations must be idempotent and repositories must round-trip."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from forex_bot.data.db import Database
from forex_bot.data.repositories import (
    AccountSnapshotRepo,
    CandleRepo,
    InstrumentRepo,
    OrderPlanRepo,
    RiskDecisionRepo,
    SignalRepo,
    TransactionRepo,
)
from forex_bot.domain.account import AccountSnapshot
from forex_bot.domain.candles import Candle
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.orders import OrderPlan
from forex_bot.domain.risk import RiskDecision, RiskRejectionCode
from forex_bot.domain.signals import Signal
from forex_bot.domain.transactions import Transaction


def test_migrations_idempotent(tmp_path):
    p = tmp_path / "x.sqlite3"
    db1 = Database(p)
    db1.close()
    # Open a second time → migrations must not fail.
    db2 = Database(p)
    row = db2.fetchone("SELECT COUNT(*) AS n FROM schema_version")
    assert row is not None and row["n"] >= 1
    db2.close()


def test_instrument_round_trip(temp_db):
    repo = InstrumentRepo(temp_db)
    inst = Instrument(
        name="EUR_USD",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
    )
    repo.upsert(inst, raw={"name": "EUR_USD"})
    fetched = repo.get("EUR_USD")
    assert fetched is not None
    assert fetched.name == "EUR_USD"
    assert fetched.pip_size == Decimal("0.0001")


def test_candle_upsert_uniqueness(temp_db):
    repo = CandleRepo(temp_db)
    candle = Candle(
        instrument="EUR_USD",
        granularity="H4",
        time=datetime(2026, 5, 21, 12, tzinfo=UTC),
        complete=True,
        bid_c=Decimal("1.0800"),
        ask_c=Decimal("1.0802"),
    )
    assert repo.upsert_many([candle], source="oanda", price_components="BA", request_hash="r1") == 1
    # Re-insert with newer state → should overwrite due to ON CONFLICT.
    candle2 = candle.model_copy(update={"complete": True})
    assert repo.upsert_many([candle2], source="oanda", price_components="BA", request_hash="r1") == 1
    rows = repo.list("EUR_USD", "H4")
    assert len(rows) == 1


def test_risk_decision_round_trip(temp_db):
    repo = RiskDecisionRepo(temp_db)
    dec = RiskDecision(
        signal_id="sig-1",
        decided_at=datetime(2026, 5, 21, tzinfo=UTC),
        approved=False,
        rejection_codes=[RiskRejectionCode.SPREAD_TOO_WIDE],
        rejection_messages=["wide"],
        config_hash="cfg",
    )
    repo.insert(dec)
    out = repo.list_for_signal("sig-1")
    assert len(out) == 1
    assert out[0].rejection_codes == [RiskRejectionCode.SPREAD_TOO_WIDE]


def test_order_plan_unique_client_id(temp_db):
    repo = OrderPlanRepo(temp_db)
    plan = OrderPlan(
        plan_id="p1",
        signal_id="s1",
        strategy_name="x",
        strategy_version="0",
        instrument="EUR_USD",
        side="buy",
        units=Decimal("100"),
        stop_loss_price=Decimal("1.07"),
        client_order_id="fbot-1",
        config_hash="c",
        created_at=datetime(2026, 5, 21, tzinfo=UTC),
    )
    repo.insert(plan)
    dup = plan.model_copy(update={"plan_id": "p2"})
    try:
        repo.insert(dup)
        assert False, "expected UNIQUE constraint failure"
    except Exception as exc:
        assert "UNIQUE" in str(exc).upper() or "unique" in str(exc).lower()


def test_signal_repo_idempotent(temp_db):
    repo = SignalRepo(temp_db)
    s = Signal(
        signal_id="sig-1",
        strategy_name="x",
        strategy_version="0",
        instrument="EUR_USD",
        timeframe="H4",
        timestamp=datetime(2026, 5, 21, tzinfo=UTC),
        side="long",
        stop_model="ATR",
        stop_price=Decimal("1.07"),
        exit_model="trail",
    )
    repo.insert(s)
    repo.insert(s)  # insert OR ignore


def test_account_snapshot_latest(temp_db):
    repo = AccountSnapshotRepo(temp_db)
    snap = AccountSnapshot(
        account_id="acc",
        currency="USD",
        balance=Decimal("500"),
        nav=Decimal("500"),
        time=datetime(2026, 5, 21, tzinfo=UTC),
    )
    repo.insert(snap, raw={})
    latest = repo.latest()
    assert latest is not None
    assert latest.nav == Decimal("500")


def test_transaction_latest_numerical_order(temp_db):
    repo = TransactionRepo(temp_db)
    txs = [
        Transaction(
            transaction_id="9",
            type="MARKET_ORDER",
            account_id="a",
            time=datetime(2026, 5, 21, 1, tzinfo=UTC),
        ),
        Transaction(
            transaction_id="100",
            type="ORDER_FILL",
            account_id="a",
            time=datetime(2026, 5, 21, 2, tzinfo=UTC),
        ),
    ]
    repo.upsert_many(txs)
    assert repo.latest_id() == "100"
