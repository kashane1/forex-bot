"""Executor safety tests: paper-mode refusal, duplicate client-id refusal,
missing stop refusal, unknown-status block."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from forex_bot.broker.errors import BrokerUnknownStatusError
from forex_bot.config import ConfigError, Settings, load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import (
    AccountSnapshotRepo,
    BrokerOrderRepo,
    OrderPlanRepo,
    SystemEventRepo,
    TransactionRepo,
)
from forex_bot.domain.account import AccountDetails, AccountSnapshot
from forex_bot.domain.orders import BrokerOrder, BrokerOrderResult, OrderPlan
from forex_bot.domain.positions import Position, Trade
from forex_bot.domain.transactions import Transaction
from forex_bot.execution.executor import Executor
from forex_bot.execution.reconciliation import Reconciler


class FakeBroker:
    environment = "practice"
    account_id = "acc"

    def __init__(self, *, open_orders=None, submit_outcome="fill") -> None:
        self.open_orders = open_orders or []
        self.submit_outcome = submit_outcome
        self.submit_calls: list[OrderPlan] = []

    # read-only helpers --------------------------------------------------
    def get_account_summary(self) -> AccountSnapshot:
        return AccountSnapshot(
            account_id="acc",
            currency="USD",
            balance=Decimal("500"),
            nav=Decimal("500"),
            margin_used=Decimal("0"),
            margin_available=Decimal("500"),
            margin_closeout_percent=Decimal("0"),
            unrealized_pl=Decimal("0"),
            pl=Decimal("0"),
            open_trade_count=0,
            open_position_count=0,
            pending_order_count=0,
            time=datetime(2026, 5, 21, tzinfo=UTC),
            last_transaction_id="1",
        )

    def get_account_details(self) -> AccountDetails:
        return AccountDetails(snapshot=self.get_account_summary())

    def list_open_orders(self) -> list[BrokerOrder]:
        return list(self.open_orders)

    def list_open_trades(self) -> list[Trade]:
        return []

    def list_positions(self) -> list[Position]:
        return []

    def get_transactions_since(self, last_id: str) -> list[Transaction]:
        return []

    def list_instruments(self):
        return []

    def get_candles(self, request):
        return []

    def get_prices(self, instruments):
        return []

    def stream_prices(self, instruments) -> Iterator:
        return iter(())

    def stream_transactions(self) -> Iterator:
        return iter(())

    def close_trade(self, trade_id, units=None) -> BrokerOrderResult:
        return BrokerOrderResult(status="FILLED")

    # mutating -----------------------------------------------------------
    def submit_order(self, plan: OrderPlan) -> BrokerOrderResult:
        self.submit_calls.append(plan)
        if self.submit_outcome == "unknown":
            raise BrokerUnknownStatusError("simulated timeout")
        if self.submit_outcome == "fill":
            return BrokerOrderResult(
                status="FILLED",
                broker_order_id="42",
                client_order_id=plan.client_order_id,
                fill_transaction_id="43",
                fill_price=Decimal("1.08015"),
                filled_units=plan.units,
                trade_opened_id="100",
                last_transaction_id="43",
                raw={
                    "orderCreateTransaction": {
                        "id": "42",
                        "instrument": plan.instrument,
                        "type": "MARKET_ORDER",
                        "units": str(plan.units),
                        "createTime": "2026-05-21T12:00:00Z",
                        "stopLossOnFill": {"price": str(plan.stop_loss_price)},
                    },
                    "orderFillTransaction": {
                        "id": "43",
                        "price": "1.08015",
                        "units": str(plan.units),
                    },
                    "lastTransactionID": "43",
                },
            )
        if self.submit_outcome == "fill_unprotected":
            return BrokerOrderResult(
                status="FILLED",
                broker_order_id="42",
                client_order_id=plan.client_order_id,
                fill_price=Decimal("1.08015"),
                filled_units=plan.units,
                raw={
                    "orderCreateTransaction": {
                        "id": "42",
                        "instrument": plan.instrument,
                        "type": "MARKET_ORDER",
                        "units": str(plan.units),
                        "createTime": "2026-05-21T12:00:00Z",
                    }
                },
            )
        return BrokerOrderResult(status="REJECTED", error_message="oops")


def _plan(client_id: str = "fbot-test") -> OrderPlan:
    return OrderPlan(
        plan_id="plan-1",
        signal_id="sig-1",
        strategy_name="trend_following",
        strategy_version="0.1.0",
        instrument="EUR_USD",
        side="buy",
        order_type="MARKET",
        units=Decimal("100"),
        requested_price=Decimal("1.08010"),
        stop_loss_price=Decimal("1.07810"),
        client_order_id=client_id,
        config_hash="cfghash",
        created_at=datetime(2026, 5, 21, 12, tzinfo=UTC),
    )


@pytest.fixture
def practice_settings(practice_config_path: Path, monkeypatch, tmp_path):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "x")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "y")
    text = practice_config_path.read_text(encoding="utf-8")
    text = text.replace("./KILL_SWITCH", str(tmp_path / "KILL_SWITCH"))
    text = text.replace("./data/bot.sqlite3", str(tmp_path / "bot.sqlite3"))
    text = text.replace("./logs/bot.jsonl", str(tmp_path / "bot.jsonl"))
    out = tmp_path / "practice.yaml"
    out.write_text(text, encoding="utf-8")
    return load_settings(out)


def _make_executor(settings: Settings, broker: FakeBroker, db: Database) -> Executor:
    plans_repo = OrderPlanRepo(db)
    orders_repo = BrokerOrderRepo(db)
    transactions_repo = TransactionRepo(db)
    snapshots_repo = AccountSnapshotRepo(db)
    events = SystemEventRepo(db)
    reconciler = Reconciler(
        broker=broker, transactions=transactions_repo, snapshots=snapshots_repo, events=events
    )
    return Executor(
        settings=settings,
        broker=broker,
        plans=plans_repo,
        orders=orders_repo,
        transactions=transactions_repo,
        snapshots=snapshots_repo,
        events=events,
        reconciler=reconciler,
    )


def test_paper_mode_executor_refuses(paper_config_path, monkeypatch, tmp_path):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "x")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "y")
    text = paper_config_path.read_text(encoding="utf-8")
    text = text.replace("./KILL_SWITCH", str(tmp_path / "KILL_SWITCH"))
    text = text.replace("./data/bot.sqlite3", str(tmp_path / "bot.sqlite3"))
    text = text.replace("./logs/bot.jsonl", str(tmp_path / "bot.jsonl"))
    out = tmp_path / "paper.yaml"
    out.write_text(text, encoding="utf-8")
    settings = load_settings(out)
    db = Database(settings.app.database_path)
    broker = FakeBroker()
    executor = _make_executor(settings, broker, db)
    plan = _plan()
    OrderPlanRepo(db).insert(plan)
    result = executor.submit(plan)
    assert not result.submitted
    assert "disallows" in result.reason
    assert broker.submit_calls == []


def test_unknown_status_blocks_trading(practice_settings, tmp_path):
    db = Database(practice_settings.app.database_path)
    broker = FakeBroker(submit_outcome="unknown")
    executor = _make_executor(practice_settings, broker, db)
    plan = _plan()
    OrderPlanRepo(db).insert(plan)
    result = executor.submit(plan)
    assert not result.submitted
    assert result.trading_blocked
    assert executor.trading_blocked


def test_duplicate_client_id_in_local_ledger_blocks(practice_settings, tmp_path):
    db = Database(practice_settings.app.database_path)
    broker = FakeBroker()
    executor = _make_executor(practice_settings, broker, db)

    plan = _plan(client_id="fbot-dup")
    OrderPlanRepo(db).insert(plan)
    second = _plan(client_id="fbot-dup")
    # second plan with same client_id but different plan_id
    second = OrderPlan(
        plan_id="plan-2",
        signal_id=second.signal_id,
        strategy_name=second.strategy_name,
        strategy_version=second.strategy_version,
        instrument=second.instrument,
        side=second.side,
        order_type=second.order_type,
        units=second.units,
        requested_price=second.requested_price,
        stop_loss_price=second.stop_loss_price,
        client_order_id="fbot-dup",
        config_hash=second.config_hash,
        created_at=second.created_at,
    )
    result = executor.submit(second)
    assert not result.submitted
    assert result.trading_blocked
    assert broker.submit_calls == []


def test_broker_already_has_open_client_id_blocks(practice_settings):
    db = Database(practice_settings.app.database_path)
    plan = _plan(client_id="fbot-x")
    OrderPlanRepo(db).insert(plan)
    broker = FakeBroker(
        open_orders=[
            BrokerOrder(
                broker_order_id="b1",
                client_order_id="fbot-x",
                instrument="EUR_USD",
                state="PENDING",
                type="MARKET",
                units=Decimal("100"),
                time=datetime(2026, 5, 21, tzinfo=UTC),
            )
        ]
    )
    executor = _make_executor(practice_settings, broker, db)
    result = executor.submit(plan)
    assert not result.submitted
    assert result.trading_blocked


def test_filled_with_protection_succeeds(practice_settings):
    db = Database(practice_settings.app.database_path)
    plan = _plan(client_id="fbot-ok")
    OrderPlanRepo(db).insert(plan)
    broker = FakeBroker(submit_outcome="fill")
    executor = _make_executor(practice_settings, broker, db)
    result = executor.submit(plan)
    assert result.submitted
    assert result.result is not None
    assert result.result.status == "FILLED"
    assert not executor.trading_blocked


def test_filled_without_protection_blocks(practice_settings):
    db = Database(practice_settings.app.database_path)
    plan = _plan(client_id="fbot-unp")
    OrderPlanRepo(db).insert(plan)
    broker = FakeBroker(submit_outcome="fill_unprotected")
    executor = _make_executor(practice_settings, broker, db)
    result = executor.submit(plan)
    assert result.submitted
    assert executor.trading_blocked, "missing stopLossOnFill must block trading"


def test_live_environment_refused_even_with_practice_gates(practice_settings):
    db = Database(practice_settings.app.database_path)
    broker = FakeBroker()
    executor = _make_executor(practice_settings, broker, db)
    # Force the settings to claim live mode but without live gates green.
    executor.settings.broker.environment = "live"
    plan = _plan(client_id="fbot-live")
    OrderPlanRepo(db).insert(plan)
    with pytest.raises(ConfigError):
        executor.submit(plan)


def test_paper_executor_never_submits_even_with_credentials(paper_config_path, monkeypatch, tmp_path):
    """Defense in depth: even if someone forces an Executor in paper mode
    with valid creds, the config gate blocks submission."""
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "x")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "y")
    text = paper_config_path.read_text(encoding="utf-8")
    text = text.replace("./KILL_SWITCH", str(tmp_path / "K"))
    text = text.replace("./data/bot.sqlite3", str(tmp_path / "bot.sqlite3"))
    text = text.replace("./logs/bot.jsonl", str(tmp_path / "bot.jsonl"))
    p = tmp_path / "paper.yaml"
    p.write_text(text, encoding="utf-8")
    settings = load_settings(p)
    db = Database(settings.app.database_path)
    broker = FakeBroker(submit_outcome="fill")
    executor = _make_executor(settings, broker, db)
    plan = _plan(client_id="fbot-paper")
    OrderPlanRepo(db).insert(plan)
    result = executor.submit(plan)
    assert not result.submitted
    assert broker.submit_calls == []
