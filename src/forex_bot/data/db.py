"""Thin SQLite wrapper.

Single connection per Database instance, used in the single-process bot.
SQLite is fine for v0 and trivially auditable. Migrations are run on open.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from threading import RLock

from forex_bot.data.migrations import apply_migrations


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(
            str(self.path),
            isolation_level=None,  # autocommit; we manage transactions ourselves
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        self._lock = RLock()
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute("PRAGMA synchronous=NORMAL")
        apply_migrations(self._connection)

    @property
    def connection(self) -> sqlite3.Connection:
        return self._connection

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                yield self._connection
            except Exception:
                self._connection.execute("ROLLBACK")
                raise
            else:
                self._connection.execute("COMMIT")

    def execute(self, sql: str, params: tuple | dict | None = None) -> sqlite3.Cursor:
        with self._lock:
            return self._connection.execute(sql, params or ())

    def fetchone(self, sql: str, params: tuple | dict | None = None) -> sqlite3.Row | None:
        cur = self.execute(sql, params)
        try:
            return cur.fetchone()
        finally:
            cur.close()

    def fetchall(self, sql: str, params: tuple | dict | None = None) -> list[sqlite3.Row]:
        cur = self.execute(sql, params)
        try:
            return cur.fetchall()
        finally:
            cur.close()


def get_db(path: str | Path) -> Database:
    return Database(path)
