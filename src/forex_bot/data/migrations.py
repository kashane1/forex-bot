"""Idempotent SQLite migrations.

Each migration is (version, statements). `apply_migrations` runs everything
above the current schema version. Migrations are append-only; never edit a
shipped one.
"""

from __future__ import annotations

import sqlite3

MIGRATIONS: list[tuple[int, list[str]]] = [
    (
        1,
        [
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS instruments (
                name TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                display_precision INTEGER NOT NULL,
                pip_location INTEGER NOT NULL,
                trade_units_precision INTEGER NOT NULL,
                minimum_trade_size TEXT,
                maximum_order_units TEXT,
                maximum_position_size TEXT,
                margin_rate TEXT,
                minimum_trailing_stop_distance TEXT,
                maximum_trailing_stop_distance TEXT,
                raw_json TEXT NOT NULL,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS candles (
                instrument TEXT NOT NULL,
                granularity TEXT NOT NULL,
                time TEXT NOT NULL,
                complete INTEGER NOT NULL,
                volume INTEGER NOT NULL DEFAULT 0,
                price_components TEXT NOT NULL,
                bid_o TEXT, bid_h TEXT, bid_l TEXT, bid_c TEXT,
                ask_o TEXT, ask_h TEXT, ask_l TEXT, ask_c TEXT,
                mid_o TEXT, mid_h TEXT, mid_l TEXT, mid_c TEXT,
                source TEXT NOT NULL,
                request_hash TEXT,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (instrument, granularity, time, price_components)
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_candles_inst_gran_time
                ON candles(instrument, granularity, time DESC)
            """,
            """
            CREATE TABLE IF NOT EXISTS price_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument TEXT NOT NULL,
                time TEXT NOT NULL,
                bid TEXT NOT NULL,
                ask TEXT NOT NULL,
                tradeable INTEGER NOT NULL,
                status TEXT,
                raw_json TEXT NOT NULL,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_price_snapshots_inst_time
                ON price_snapshots(instrument, time DESC)
            """,
            """
            CREATE TABLE IF NOT EXISTS spread_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument TEXT NOT NULL,
                time TEXT NOT NULL,
                bid TEXT NOT NULL,
                ask TEXT NOT NULL,
                spread_pips TEXT NOT NULL,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS signals (
                signal_id TEXT PRIMARY KEY,
                strategy_name TEXT NOT NULL,
                strategy_version TEXT NOT NULL,
                instrument TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_intent TEXT NOT NULL,
                confidence REAL,
                stop_model TEXT NOT NULL,
                stop_price TEXT NOT NULL,
                take_profit_price TEXT,
                exit_model TEXT NOT NULL,
                features_json TEXT,
                reason TEXT,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS risk_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT NOT NULL,
                decided_at TEXT NOT NULL,
                approved INTEGER NOT NULL,
                rejection_codes TEXT,
                rejection_messages TEXT,
                account_nav TEXT,
                instrument_metadata_version TEXT,
                spread_pips TEXT,
                stop_distance_pips TEXT,
                raw_units TEXT,
                units TEXT,
                estimated_risk TEXT,
                estimated_margin TEXT,
                config_hash TEXT NOT NULL,
                extras_json TEXT,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS order_plans (
                plan_id TEXT PRIMARY KEY,
                signal_id TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                strategy_version TEXT NOT NULL,
                instrument TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                units TEXT NOT NULL,
                requested_price TEXT,
                stop_loss_price TEXT NOT NULL,
                take_profit_price TEXT,
                trailing_stop_pips TEXT,
                client_order_id TEXT NOT NULL UNIQUE,
                config_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                extras_json TEXT,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS broker_orders (
                broker_order_id TEXT PRIMARY KEY,
                client_order_id TEXT,
                plan_id TEXT,
                instrument TEXT NOT NULL,
                state TEXT NOT NULL,
                type TEXT NOT NULL,
                units TEXT NOT NULL,
                price TEXT,
                time TEXT NOT NULL,
                raw_json TEXT NOT NULL,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_broker_orders_client_id
                ON broker_orders(client_order_id)
            """,
            """
            CREATE TABLE IF NOT EXISTS fills (
                fill_id TEXT PRIMARY KEY,
                trade_id TEXT,
                instrument TEXT NOT NULL,
                units TEXT NOT NULL,
                price TEXT NOT NULL,
                time TEXT NOT NULL,
                pl TEXT,
                financing TEXT,
                raw_json TEXT NOT NULL,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                account_id TEXT NOT NULL,
                time TEXT NOT NULL,
                instrument TEXT,
                units TEXT,
                price TEXT,
                reason TEXT,
                pl TEXT,
                financing TEXT,
                raw_json TEXT NOT NULL,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_transactions_time
                ON transactions(time DESC)
            """,
            """
            CREATE TABLE IF NOT EXISTS account_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                time TEXT NOT NULL,
                currency TEXT NOT NULL,
                balance TEXT NOT NULL,
                nav TEXT NOT NULL,
                margin_used TEXT NOT NULL,
                margin_available TEXT NOT NULL,
                margin_closeout_percent TEXT NOT NULL,
                unrealized_pl TEXT NOT NULL,
                pl TEXT NOT NULL,
                open_trade_count INTEGER NOT NULL,
                open_position_count INTEGER NOT NULL,
                pending_order_count INTEGER NOT NULL,
                last_transaction_id TEXT,
                raw_json TEXT NOT NULL,
                inserted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS positions (
                instrument TEXT PRIMARY KEY,
                long_units TEXT NOT NULL,
                long_average_price TEXT,
                short_units TEXT NOT NULL,
                short_average_price TEXT,
                unrealized_pl TEXT,
                raw_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS strategy_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                strategy_version TEXT NOT NULL,
                run_type TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                config_hash TEXT NOT NULL,
                notes TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS backtest_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                strategy_version TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                config_hash TEXT NOT NULL,
                data_request_hash TEXT,
                instruments TEXT NOT NULL,
                granularity TEXT NOT NULL,
                from_time TEXT,
                to_time TEXT,
                metrics_json TEXT,
                trades_json TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT NOT NULL DEFAULT (datetime('now')),
                kind TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                extras_json TEXT
            )
            """,
        ],
    ),
    (
        2,
        [
            """
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign TEXT,
                instrument TEXT NOT NULL,
                granularity TEXT NOT NULL,
                source TEXT NOT NULL,
                host TEXT,
                from_time TEXT,
                to_time TEXT,
                price_components TEXT,
                page_count INTEGER NOT NULL DEFAULT 0,
                candles_written INTEGER NOT NULL DEFAULT 0,
                candles_dropped_incomplete INTEGER NOT NULL DEFAULT 0,
                first_ts TEXT,
                last_ts TEXT,
                raw_sha256 TEXT,
                normalized_sha256 TEXT,
                request_params_json TEXT,
                broker_account_id_redacted TEXT,
                fetched_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_data_sources_inst_gran
                ON data_sources(instrument, granularity, fetched_at DESC)
            """,
        ],
    ),
]


def _current_version(conn: sqlite3.Connection) -> int:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
    )
    row = cur.fetchone()
    cur.close()
    if row is None:
        return 0
    cur = conn.execute("SELECT MAX(version) FROM schema_version")
    version_row = cur.fetchone()
    cur.close()
    return int(version_row[0]) if version_row and version_row[0] is not None else 0


def apply_migrations(conn: sqlite3.Connection) -> None:
    current = _current_version(conn)
    for version, statements in MIGRATIONS:
        if version <= current:
            continue
        for statement in statements:
            conn.execute(statement)
        conn.execute(
            "INSERT INTO schema_version (version) VALUES (?)", (version,)
        )
