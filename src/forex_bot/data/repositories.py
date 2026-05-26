"""Repositories. Each class wraps one table and produces/consumes domain models."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from forex_bot.data.candle_dedupe import CandleDedupeStats, dedupe_candles
from forex_bot.data.db import Database
from forex_bot.domain.account import AccountSnapshot
from forex_bot.domain.candles import Candle, Granularity
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import Quote, SpreadSnapshot
from forex_bot.domain.orders import BrokerOrder, BrokerOrderResult, OrderPlan
from forex_bot.domain.risk import RiskDecision, RiskRejectionCode
from forex_bot.domain.signals import Signal
from forex_bot.domain.transactions import ObservedFinancingEvent, Transaction


def _d(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _dec(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _iso(value: datetime) -> str:
    return value.isoformat()


# ---------------------------------------------------------------------------


class InstrumentRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def upsert(self, instrument: Instrument, raw: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO instruments(
                name, type, display_precision, pip_location, trade_units_precision,
                minimum_trade_size, maximum_order_units, maximum_position_size,
                margin_rate, minimum_trailing_stop_distance, maximum_trailing_stop_distance,
                raw_json, inserted_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            ON CONFLICT(name) DO UPDATE SET
                type=excluded.type,
                display_precision=excluded.display_precision,
                pip_location=excluded.pip_location,
                trade_units_precision=excluded.trade_units_precision,
                minimum_trade_size=excluded.minimum_trade_size,
                maximum_order_units=excluded.maximum_order_units,
                maximum_position_size=excluded.maximum_position_size,
                margin_rate=excluded.margin_rate,
                minimum_trailing_stop_distance=excluded.minimum_trailing_stop_distance,
                maximum_trailing_stop_distance=excluded.maximum_trailing_stop_distance,
                raw_json=excluded.raw_json,
                updated_at=datetime('now')
            """,
            (
                instrument.name,
                instrument.type,
                instrument.display_precision,
                instrument.pip_location,
                instrument.trade_units_precision,
                _d(instrument.minimum_trade_size),
                _d(instrument.maximum_order_units),
                _d(instrument.maximum_position_size),
                _d(instrument.margin_rate),
                _d(instrument.minimum_trailing_stop_distance),
                _d(instrument.maximum_trailing_stop_distance),
                json.dumps(raw, default=str, sort_keys=True),
            ),
        )

    def get(self, name: str) -> Instrument | None:
        row = self.db.fetchone("SELECT * FROM instruments WHERE name=?", (name,))
        if row is None:
            return None
        return Instrument(
            name=row["name"],
            type=row["type"],
            display_precision=row["display_precision"],
            pip_location=row["pip_location"],
            trade_units_precision=row["trade_units_precision"],
            minimum_trade_size=_dec(row["minimum_trade_size"]) or Decimal("1"),
            maximum_order_units=_dec(row["maximum_order_units"]),
            maximum_position_size=_dec(row["maximum_position_size"]),
            margin_rate=_dec(row["margin_rate"]) or Decimal("0.05"),
            minimum_trailing_stop_distance=_dec(row["minimum_trailing_stop_distance"]),
            maximum_trailing_stop_distance=_dec(row["maximum_trailing_stop_distance"]),
        )

    def all(self) -> list[Instrument]:
        rows = self.db.fetchall("SELECT * FROM instruments")
        return [
            Instrument(
                name=row["name"],
                type=row["type"],
                display_precision=row["display_precision"],
                pip_location=row["pip_location"],
                trade_units_precision=row["trade_units_precision"],
                minimum_trade_size=_dec(row["minimum_trade_size"]) or Decimal("1"),
                maximum_order_units=_dec(row["maximum_order_units"]),
                maximum_position_size=_dec(row["maximum_position_size"]),
                margin_rate=_dec(row["margin_rate"]) or Decimal("0.05"),
                minimum_trailing_stop_distance=_dec(row["minimum_trailing_stop_distance"]),
                maximum_trailing_stop_distance=_dec(row["maximum_trailing_stop_distance"]),
            )
            for row in rows
        ]


# ---------------------------------------------------------------------------


class CandleRepo:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.last_list_dedupe_stats: CandleDedupeStats | None = None

    def upsert_many(
        self,
        candles: list[Candle],
        *,
        source: str,
        price_components: str,
        request_hash: str | None,
    ) -> int:
        if not candles:
            return 0
        with self.db.transaction() as conn:
            for c in candles:
                conn.execute(
                    """
                    INSERT INTO candles(
                        instrument, granularity, time, complete, volume, price_components,
                        bid_o, bid_h, bid_l, bid_c,
                        ask_o, ask_h, ask_l, ask_c,
                        mid_o, mid_h, mid_l, mid_c,
                        source, request_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(instrument, granularity, time, price_components) DO UPDATE SET
                        complete=excluded.complete,
                        volume=excluded.volume,
                        bid_o=excluded.bid_o, bid_h=excluded.bid_h,
                        bid_l=excluded.bid_l, bid_c=excluded.bid_c,
                        ask_o=excluded.ask_o, ask_h=excluded.ask_h,
                        ask_l=excluded.ask_l, ask_c=excluded.ask_c,
                        mid_o=excluded.mid_o, mid_h=excluded.mid_h,
                        mid_l=excluded.mid_l, mid_c=excluded.mid_c,
                        source=excluded.source,
                        request_hash=excluded.request_hash
                    """,
                    (
                        c.instrument,
                        c.granularity,
                        _iso(c.time),
                        1 if c.complete else 0,
                        c.volume,
                        price_components,
                        _d(c.bid_o), _d(c.bid_h), _d(c.bid_l), _d(c.bid_c),
                        _d(c.ask_o), _d(c.ask_h), _d(c.ask_l), _d(c.ask_c),
                        _d(c.mid_o), _d(c.mid_h), _d(c.mid_l), _d(c.mid_c),
                        source, request_hash,
                    ),
                )
        return len(candles)

    def list(
        self,
        instrument: str,
        granularity: Granularity,
        *,
        completed_only: bool = True,
        limit: int | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> list[Candle]:
        clauses = ["instrument=?", "granularity=?"]
        params: list[object] = [instrument, granularity]
        if completed_only:
            clauses.append("complete=1")
        if from_time is not None:
            clauses.append("time>=?")
            params.append(from_time.isoformat())
        if to_time is not None:
            clauses.append("time<=?")
            params.append(to_time.isoformat())
        sql = (
            f"SELECT * FROM candles WHERE {' AND '.join(clauses)} "
            "ORDER BY time ASC, rowid ASC"
        )
        if limit is not None:
            sql = sql.replace(
                " ORDER BY time ASC, rowid ASC",
                " ORDER BY time DESC, rowid DESC",
            )
            sql += " LIMIT ?"
            params.append(limit)
        rows = self.db.fetchall(sql, tuple(params))
        if limit is not None:
            rows = list(reversed(rows))
        raw = [self._row_to_candle(row) for row in rows]
        deduped, stats = dedupe_candles(raw)
        self.last_list_dedupe_stats = stats
        return deduped

    def list_with_dedupe_stats(
        self,
        instrument: str,
        granularity: Granularity,
        *,
        completed_only: bool = True,
        limit: int | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> tuple[list[Candle], CandleDedupeStats]:
        """Like ``list`` but also returns dedupe statistics for preflight."""
        candles = self.list(
            instrument,
            granularity,
            completed_only=completed_only,
            limit=limit,
            from_time=from_time,
            to_time=to_time,
        )
        stats = self.last_list_dedupe_stats or CandleDedupeStats.empty()
        return candles, stats

    @staticmethod
    def _row_to_candle(row: Any) -> Candle:
        return Candle(
            instrument=row["instrument"],
            granularity=row["granularity"],
            time=datetime.fromisoformat(row["time"]),
            complete=bool(row["complete"]),
            volume=row["volume"],
            bid_o=_dec(row["bid_o"]),
            bid_h=_dec(row["bid_h"]),
            bid_l=_dec(row["bid_l"]),
            bid_c=_dec(row["bid_c"]),
            ask_o=_dec(row["ask_o"]),
            ask_h=_dec(row["ask_h"]),
            ask_l=_dec(row["ask_l"]),
            ask_c=_dec(row["ask_c"]),
            mid_o=_dec(row["mid_o"]),
            mid_h=_dec(row["mid_h"]),
            mid_l=_dec(row["mid_l"]),
            mid_c=_dec(row["mid_c"]),
        )


# ---------------------------------------------------------------------------


class SignalRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def insert(self, signal: Signal) -> None:
        self.db.execute(
            """
            INSERT OR IGNORE INTO signals(
                signal_id, strategy_name, strategy_version, instrument, timeframe,
                timestamp, side, entry_intent, confidence, stop_model, stop_price,
                take_profit_price, exit_model, features_json, reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                signal.signal_id,
                signal.strategy_name,
                signal.strategy_version,
                signal.instrument,
                signal.timeframe,
                _iso(signal.timestamp),
                signal.side,
                signal.entry_intent,
                signal.confidence,
                signal.stop_model,
                _d(signal.stop_price),
                _d(signal.take_profit_price),
                signal.exit_model,
                json.dumps(signal.features, default=str, sort_keys=True),
                signal.reason,
            ),
        )


# ---------------------------------------------------------------------------


class RiskDecisionRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def insert(self, decision: RiskDecision) -> int:
        cur = self.db.execute(
            """
            INSERT INTO risk_decisions(
                signal_id, decided_at, approved, rejection_codes, rejection_messages,
                account_nav, instrument_metadata_version, spread_pips,
                stop_distance_pips, raw_units, units, estimated_risk,
                estimated_margin, config_hash, extras_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision.signal_id,
                _iso(decision.decided_at),
                1 if decision.approved else 0,
                json.dumps([c.value for c in decision.rejection_codes]),
                json.dumps(decision.rejection_messages),
                _d(decision.account_nav),
                decision.instrument_metadata_version,
                _d(decision.spread_pips),
                _d(decision.stop_distance_pips),
                _d(decision.raw_units),
                _d(decision.units),
                _d(decision.estimated_risk),
                _d(decision.estimated_margin),
                decision.config_hash,
                json.dumps(decision.extras, default=str, sort_keys=True),
            ),
        )
        return int(cur.lastrowid or 0)

    def list_for_signal(self, signal_id: str) -> list[RiskDecision]:
        rows = self.db.fetchall(
            "SELECT * FROM risk_decisions WHERE signal_id=? ORDER BY decided_at DESC",
            (signal_id,),
        )
        return [self._row(row) for row in rows]

    @staticmethod
    def _row(row: Any) -> RiskDecision:
        return RiskDecision(
            signal_id=row["signal_id"],
            decided_at=datetime.fromisoformat(row["decided_at"]),
            approved=bool(row["approved"]),
            rejection_codes=[RiskRejectionCode(c) for c in json.loads(row["rejection_codes"] or "[]")],
            rejection_messages=json.loads(row["rejection_messages"] or "[]"),
            account_nav=_dec(row["account_nav"]),
            instrument_metadata_version=row["instrument_metadata_version"],
            spread_pips=_dec(row["spread_pips"]),
            stop_distance_pips=_dec(row["stop_distance_pips"]),
            raw_units=_dec(row["raw_units"]),
            units=_dec(row["units"]),
            estimated_risk=_dec(row["estimated_risk"]),
            estimated_margin=_dec(row["estimated_margin"]),
            config_hash=row["config_hash"],
            extras=json.loads(row["extras_json"] or "{}"),
        )


# ---------------------------------------------------------------------------


class OrderPlanRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def insert(self, plan: OrderPlan) -> None:
        self.db.execute(
            """
            INSERT INTO order_plans(
                plan_id, signal_id, strategy_name, strategy_version, instrument,
                side, order_type, units, requested_price, stop_loss_price,
                take_profit_price, trailing_stop_pips, client_order_id, config_hash,
                created_at, extras_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plan.plan_id,
                plan.signal_id,
                plan.strategy_name,
                plan.strategy_version,
                plan.instrument,
                plan.side,
                plan.order_type,
                _d(plan.units),
                _d(plan.requested_price),
                _d(plan.stop_loss_price),
                _d(plan.take_profit_price),
                _d(plan.trailing_stop_pips),
                plan.client_order_id,
                plan.config_hash,
                _iso(plan.created_at),
                json.dumps(plan.extras, default=str, sort_keys=True),
            ),
        )

    def get_by_client_id(self, client_order_id: str) -> OrderPlan | None:
        row = self.db.fetchone(
            "SELECT * FROM order_plans WHERE client_order_id=?", (client_order_id,)
        )
        if row is None:
            return None
        return OrderPlan(
            plan_id=row["plan_id"],
            signal_id=row["signal_id"],
            strategy_name=row["strategy_name"],
            strategy_version=row["strategy_version"],
            instrument=row["instrument"],
            side=row["side"],
            order_type=row["order_type"],
            units=Decimal(row["units"]),
            requested_price=_dec(row["requested_price"]),
            stop_loss_price=Decimal(row["stop_loss_price"]),
            take_profit_price=_dec(row["take_profit_price"]),
            trailing_stop_pips=_dec(row["trailing_stop_pips"]),
            client_order_id=row["client_order_id"],
            config_hash=row["config_hash"],
            created_at=datetime.fromisoformat(row["created_at"]),
            extras=json.loads(row["extras_json"] or "{}"),
        )


# ---------------------------------------------------------------------------


class BrokerOrderRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def upsert(self, order: BrokerOrder, plan_id: str | None = None) -> None:
        self.db.execute(
            """
            INSERT INTO broker_orders(
                broker_order_id, client_order_id, plan_id, instrument, state, type,
                units, price, time, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(broker_order_id) DO UPDATE SET
                client_order_id=excluded.client_order_id,
                plan_id=excluded.plan_id,
                instrument=excluded.instrument,
                state=excluded.state,
                type=excluded.type,
                units=excluded.units,
                price=excluded.price,
                time=excluded.time,
                raw_json=excluded.raw_json
            """,
            (
                order.broker_order_id,
                order.client_order_id,
                plan_id,
                order.instrument,
                order.state,
                order.type,
                _d(order.units),
                _d(order.price),
                _iso(order.time),
                json.dumps(order.raw, default=str, sort_keys=True),
            ),
        )

    def insert_result(self, plan_id: str, result: BrokerOrderResult) -> None:
        self.db.execute(
            """
            INSERT INTO system_events(kind, level, message, extras_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                "broker_order_result",
                "info" if result.status in {"FILLED", "PENDING"} else "warn",
                f"plan={plan_id} status={result.status}",
                json.dumps(result.model_dump(), default=str, sort_keys=True),
            ),
        )


# ---------------------------------------------------------------------------


class TransactionRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def upsert_many(self, transactions: list[Transaction]) -> int:
        if not transactions:
            return 0
        with self.db.transaction() as conn:
            for tx in transactions:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO transactions(
                        transaction_id, type, account_id, time, instrument, units,
                        price, reason, pl, financing, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tx.transaction_id,
                        tx.type,
                        tx.account_id,
                        _iso(tx.time),
                        tx.instrument,
                        _d(tx.units),
                        _d(tx.price),
                        tx.reason,
                        _d(tx.pl),
                        _d(tx.financing),
                        json.dumps(tx.raw, default=str, sort_keys=True),
                    ),
                )
        return len(transactions)

    def latest_id(self) -> str | None:
        row = self.db.fetchone(
            "SELECT transaction_id FROM transactions ORDER BY CAST(transaction_id AS INTEGER) DESC LIMIT 1"
        )
        if row is None:
            return None
        return row["transaction_id"]


# ---------------------------------------------------------------------------


class AccountSnapshotRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def insert(self, snapshot: AccountSnapshot, raw: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO account_snapshots(
                account_id, time, currency, balance, nav, margin_used,
                margin_available, margin_closeout_percent, unrealized_pl, pl,
                open_trade_count, open_position_count, pending_order_count,
                last_transaction_id, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.account_id,
                _iso(snapshot.time),
                snapshot.currency,
                _d(snapshot.balance),
                _d(snapshot.nav),
                _d(snapshot.margin_used),
                _d(snapshot.margin_available),
                _d(snapshot.margin_closeout_percent),
                _d(snapshot.unrealized_pl),
                _d(snapshot.pl),
                snapshot.open_trade_count,
                snapshot.open_position_count,
                snapshot.pending_order_count,
                snapshot.last_transaction_id,
                json.dumps(raw, default=str, sort_keys=True),
            ),
        )

    def latest(self) -> AccountSnapshot | None:
        row = self.db.fetchone(
            "SELECT * FROM account_snapshots ORDER BY id DESC LIMIT 1"
        )
        if row is None:
            return None
        return AccountSnapshot(
            account_id=row["account_id"],
            currency=row["currency"],
            balance=Decimal(row["balance"]),
            nav=Decimal(row["nav"]),
            margin_used=Decimal(row["margin_used"]),
            margin_available=Decimal(row["margin_available"]),
            margin_closeout_percent=Decimal(row["margin_closeout_percent"]),
            unrealized_pl=Decimal(row["unrealized_pl"]),
            pl=Decimal(row["pl"]),
            open_trade_count=row["open_trade_count"],
            open_position_count=row["open_position_count"],
            pending_order_count=row["pending_order_count"],
            last_transaction_id=row["last_transaction_id"],
            time=datetime.fromisoformat(row["time"]),
        )


# ---------------------------------------------------------------------------


class SpreadSnapshotRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def insert(self, snap: SpreadSnapshot) -> None:
        self.db.execute(
            """
            INSERT INTO spread_snapshots(instrument, time, bid, ask, spread_pips)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                snap.instrument,
                _iso(snap.time),
                _d(snap.bid),
                _d(snap.ask),
                _d(snap.spread_pips),
            ),
        )

    def insert_quote(self, quote: Quote, raw: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO price_snapshots(instrument, time, bid, ask, tradeable, status, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                quote.instrument,
                _iso(quote.time),
                _d(quote.bid),
                _d(quote.ask),
                1 if quote.tradeable else 0,
                quote.status,
                json.dumps(raw, default=str, sort_keys=True),
            ),
        )


# ---------------------------------------------------------------------------


class SystemEventRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def record(self, kind: str, level: str, message: str, extras: dict[str, Any] | None = None) -> None:
        self.db.execute(
            """
            INSERT INTO system_events(kind, level, message, extras_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                kind,
                level,
                message,
                json.dumps(extras or {}, default=str, sort_keys=True),
            ),
        )


# ---------------------------------------------------------------------------


@dataclass
class DataSourceRecord:
    """One row in data_sources. Proves a candle batch came from a real source."""

    instrument: str
    granularity: str
    source: str
    host: str | None = None
    from_time: str | None = None
    to_time: str | None = None
    price_components: str | None = None
    page_count: int = 0
    candles_written: int = 0
    candles_dropped_incomplete: int = 0
    first_ts: str | None = None
    last_ts: str | None = None
    raw_sha256: str | None = None
    normalized_sha256: str | None = None
    request_params_json: str | None = None
    broker_account_id_redacted: str | None = None
    campaign: str | None = None


class DataSourceRepo:
    def __init__(self, db: Database) -> None:
        self.db = db

    def insert(self, rec: DataSourceRecord) -> int:
        cur = self.db.execute(
            """
            INSERT INTO data_sources(
                campaign, instrument, granularity, source, host,
                from_time, to_time, price_components,
                page_count, candles_written, candles_dropped_incomplete,
                first_ts, last_ts, raw_sha256, normalized_sha256,
                request_params_json, broker_account_id_redacted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec.campaign,
                rec.instrument,
                rec.granularity,
                rec.source,
                rec.host,
                rec.from_time,
                rec.to_time,
                rec.price_components,
                rec.page_count,
                rec.candles_written,
                rec.candles_dropped_incomplete,
                rec.first_ts,
                rec.last_ts,
                rec.raw_sha256,
                rec.normalized_sha256,
                rec.request_params_json,
                rec.broker_account_id_redacted,
            ),
        )
        return int(cur.lastrowid or 0)

    def latest_for(self, instrument: str, granularity: str) -> dict[str, Any] | None:
        row = self.db.fetchone(
            "SELECT * FROM data_sources WHERE instrument=? AND granularity=? "
            "ORDER BY id DESC LIMIT 1",
            (instrument, granularity),
        )
        return dict(row) if row else None

    def all_in_campaign(self, campaign: str) -> list[dict[str, Any]]:
        rows = self.db.fetchall(
            "SELECT * FROM data_sources WHERE campaign=? ORDER BY id ASC",
            (campaign,),
        )
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------


class ObservedFinancingEventRepo:
    """Stores and retrieves observed financing events.

    Capture infrastructure for FUTURE paper/demo observation. No current
    loop writes here — the research freeze keeps every order-capable loop
    refused — and an empty table is the expected state. Inserts are
    idempotent on `event_key`, so re-capturing the same transactions is
    safe. See docs/research/OBSERVED_FINANCING_CAPTURE.md.
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    def insert_many(self, events: list[ObservedFinancingEvent]) -> int:
        """Idempotently store events. Returns the number of new rows."""
        if not events:
            return 0
        before = self.count()
        with self.db.transaction() as conn:
            for e in events:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO observed_financing_events(
                        event_key, transaction_id, account_id_hash, instrument,
                        trade_id, units, financing, currency, time, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        e.event_key,
                        e.transaction_id,
                        e.account_id_hash,
                        e.instrument,
                        e.trade_id,
                        _d(e.units),
                        _d(e.financing),
                        e.currency,
                        _iso(e.time),
                        e.source,
                    ),
                )
        return self.count() - before

    def count(self) -> int:
        row = self.db.fetchone("SELECT COUNT(*) AS n FROM observed_financing_events")
        return int(row["n"]) if row else 0

    def list(
        self,
        *,
        instrument: str | None = None,
        account_id_hash: str | None = None,
        limit: int | None = None,
    ) -> list[ObservedFinancingEvent]:
        clauses: list[str] = []
        params: list[object] = []
        if instrument is not None:
            clauses.append("instrument=?")
            params.append(instrument)
        if account_id_hash is not None:
            clauses.append("account_id_hash=?")
            params.append(account_id_hash)
        sql = "SELECT * FROM observed_financing_events"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY time ASC, id ASC"
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        return [self._row(r) for r in self.db.fetchall(sql, tuple(params))]

    @staticmethod
    def _row(row: Any) -> ObservedFinancingEvent:
        return ObservedFinancingEvent(
            transaction_id=row["transaction_id"],
            account_id_hash=row["account_id_hash"],
            instrument=row["instrument"],
            trade_id=row["trade_id"],
            units=_dec(row["units"]),
            financing=Decimal(str(row["financing"])),
            currency=row["currency"],
            time=datetime.fromisoformat(row["time"]),
            source=row["source"],
        )
