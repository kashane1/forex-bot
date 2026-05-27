#!/usr/bin/env python3
"""Preflight the local PostgreSQL research database."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import (
    ResearchDatabaseBlocked,
    ResearchDatabaseUnsafe,
    get_research_database_config,
)
from forex_bot.project_env import bootstrap_environ


def build_report(*, create_schema: bool, environ: dict[str, str] | None = None) -> dict:
    cfg = get_research_database_config(environ=environ, require=True)
    store = PostgresCandleStore(cfg)
    with store.connection() as conn:
        if create_schema:
            store.ensure_schema()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name
                """,
                (cfg.schema,),
            )
            tables = [row[0] for row in cur.fetchall()]
            counts: dict[str, int] = {}
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {cfg.schema}.{table}")
                counts[table] = int(cur.fetchone()[0])
    return {
        "status": "PASS",
        "database_name": cfg.database_name,
        "schema_name": cfg.schema,
        "database_url_redacted": cfg.redacted_url,
        "create_schema": create_schema,
        "tables": tables,
        "counts": counts,
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Preflight the local research PostgreSQL DB.")
    parser.add_argument("--create-schema", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = build_report(create_schema=args.create_schema, environ=environ)
    except ResearchDatabaseBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, indent=2))
        return 2
    except ResearchDatabaseUnsafe as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        return 1
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
