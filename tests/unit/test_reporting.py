"""Weekly report builds from SQLite alone, no broker calls, no secret leaks."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from forex_bot.data.repositories import (
    AccountSnapshotRepo,
    SystemEventRepo,
    TransactionRepo,
)
from forex_bot.domain.account import AccountSnapshot
from forex_bot.domain.transactions import Transaction
from forex_bot.reporting.render import render_html, render_markdown
from forex_bot.reporting.weekly import build_weekly_report


def test_weekly_report_runs_with_no_data(temp_db):
    now = datetime(2026, 5, 21, tzinfo=UTC)
    report = build_weekly_report(temp_db, now=now, config_hash="cfg", code_commit_hash="abc")
    assert report.closed_trade_count == 0
    assert "abc" in render_markdown(report)
    assert "cfg" in render_html(report)


def test_weekly_report_summarises_transactions(temp_db):
    AccountSnapshotRepo(temp_db).insert(
        AccountSnapshot(
            account_id="a",
            currency="USD",
            balance=Decimal("510"),
            nav=Decimal("510"),
            time=datetime(2026, 5, 21, tzinfo=UTC),
        ),
        raw={},
    )
    txs = [
        Transaction(
            transaction_id=str(100 + i),
            type="ORDER_FILL",
            account_id="a",
            time=datetime(2026, 5, 18, tzinfo=UTC) + timedelta(hours=i),
            pl=Decimal("1.50"),
        )
        for i in range(3)
    ]
    TransactionRepo(temp_db).upsert_many(txs)
    report = build_weekly_report(
        temp_db,
        now=datetime(2026, 5, 21, tzinfo=UTC),
        config_hash="cfg",
        code_commit_hash=None,
    )
    assert report.realized_pl == Decimal("4.50")


def test_report_does_not_leak_secrets(temp_db):
    SystemEventRepo(temp_db).record(
        "loop", "info", "Bearer abcdef1234567890abcdef1234567890 should not appear",
        {"OANDA_ACCESS_TOKEN_PRACTICE": "shhh"},
    )
    report = build_weekly_report(
        temp_db,
        now=datetime(2026, 5, 21, tzinfo=UTC),
        config_hash="cfg",
        code_commit_hash=None,
    )
    md = render_markdown(report)
    assert "abcdef1234567890" not in md
    assert "shhh" not in md
