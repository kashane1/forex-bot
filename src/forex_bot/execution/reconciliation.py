"""Compare local ledger against broker state. Block trading on mismatch."""

from __future__ import annotations

from dataclasses import dataclass, field

from forex_bot.broker.base import Broker
from forex_bot.data.repositories import (
    AccountSnapshotRepo,
    SystemEventRepo,
    TransactionRepo,
)


@dataclass
class ReconciliationReport:
    clean: bool
    differences: list[str] = field(default_factory=list)
    fetched_transactions: int = 0
    last_transaction_id: str | None = None


@dataclass
class Reconciler:
    broker: Broker
    transactions: TransactionRepo
    snapshots: AccountSnapshotRepo
    events: SystemEventRepo

    def run(self) -> ReconciliationReport:
        differences: list[str] = []
        details = self.broker.get_account_details()
        snapshot = details.snapshot

        local_last = self.transactions.latest_id()
        broker_last = snapshot.last_transaction_id
        new_count = 0
        if broker_last and broker_last != local_last:
            since = local_last or "0"
            new_txs = self.broker.get_transactions_since(since)
            new_count = self.transactions.upsert_many(new_txs)

        self.snapshots.insert(snapshot, raw=snapshot.raw)

        broker_open_trades = set(details.open_trade_ids)
        if snapshot.open_trade_count != len(broker_open_trades):
            differences.append(
                f"open_trade_count mismatch: snapshot={snapshot.open_trade_count} "
                f"trades_list={len(broker_open_trades)}"
            )
        if snapshot.pending_order_count != len(details.pending_order_ids):
            differences.append(
                f"pending_order_count mismatch: snapshot={snapshot.pending_order_count} "
                f"orders_list={len(details.pending_order_ids)}"
            )

        report = ReconciliationReport(
            clean=not differences,
            differences=differences,
            fetched_transactions=new_count,
            last_transaction_id=broker_last,
        )
        self.events.record(
            "reconcile",
            "info" if report.clean else "warn",
            f"clean={report.clean} new_txs={new_count}",
            {"differences": differences, "last_transaction_id": broker_last},
        )
        return report
