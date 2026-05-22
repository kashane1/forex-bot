"""Persistence layer. SQLite is the operational ledger; raw JSON is stored
in `raw_json` columns where the broker payload is needed verbatim for
reconciliation or replay."""

from forex_bot.data.db import Database, get_db
from forex_bot.data.migrations import MIGRATIONS, apply_migrations
from forex_bot.data.repositories import (
    AccountSnapshotRepo,
    BrokerOrderRepo,
    CandleRepo,
    DataSourceRecord,
    DataSourceRepo,
    InstrumentRepo,
    OrderPlanRepo,
    RiskDecisionRepo,
    SignalRepo,
    SpreadSnapshotRepo,
    SystemEventRepo,
    TransactionRepo,
)

__all__ = [
    "MIGRATIONS",
    "AccountSnapshotRepo",
    "BrokerOrderRepo",
    "CandleRepo",
    "DataSourceRecord",
    "DataSourceRepo",
    "Database",
    "InstrumentRepo",
    "OrderPlanRepo",
    "RiskDecisionRepo",
    "SignalRepo",
    "SpreadSnapshotRepo",
    "SystemEventRepo",
    "TransactionRepo",
    "apply_migrations",
    "get_db",
]
