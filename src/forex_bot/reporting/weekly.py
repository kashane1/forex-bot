"""Weekly report builder. All data comes from SQLite — no broker calls."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from forex_bot.data.db import Database


@dataclass
class WeeklyReport:
    generated_at: datetime
    window_start: datetime
    window_end: datetime
    account_nav: Decimal | None
    realized_pl: Decimal
    unrealized_pl: Decimal
    closed_trade_count: int
    win_rate: float
    expectancy_r: float
    average_r: float
    average_win: Decimal
    average_loss: Decimal
    profit_factor: float
    largest_single_loss: Decimal
    average_spread_paid_pips: float
    strategy_attribution: dict[str, dict[str, float]] = field(default_factory=dict)
    pair_attribution: dict[str, dict[str, float]] = field(default_factory=dict)
    risk_rejections: dict[str, int] = field(default_factory=dict)
    reconciliation_mismatches: list[str] = field(default_factory=list)
    config_hash: str = ""
    code_commit_hash: str | None = None

    def summary(self) -> dict[str, str]:
        return {
            "generated_at": self.generated_at.isoformat(),
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "realized_pl": str(self.realized_pl),
            "unrealized_pl": str(self.unrealized_pl),
            "closed_trade_count": str(self.closed_trade_count),
            "win_rate": f"{self.win_rate:.2%}",
            "expectancy_r": f"{self.expectancy_r:.2f}",
            "profit_factor": f"{self.profit_factor:.2f}",
            "config_hash": self.config_hash,
        }


def build_weekly_report(
    db: Database,
    *,
    now: datetime,
    config_hash: str,
    code_commit_hash: str | None,
) -> WeeklyReport:
    window_end = now
    window_start = now - timedelta(days=7)

    snapshot = db.fetchone(
        "SELECT * FROM account_snapshots ORDER BY id DESC LIMIT 1"
    )
    account_nav = Decimal(snapshot["nav"]) if snapshot else None
    unrealized_pl = Decimal(snapshot["unrealized_pl"]) if snapshot else Decimal("0")

    # Realized P/L is summed from transactions inside the window.
    txs = db.fetchall(
        "SELECT pl FROM transactions WHERE time >= ? AND time <= ?",
        (window_start.isoformat(), window_end.isoformat()),
    )
    realized_pl = sum((Decimal(row["pl"]) for row in txs if row["pl"]), start=Decimal("0"))

    fills = db.fetchall(
        "SELECT * FROM fills WHERE time >= ? AND time <= ? AND pl IS NOT NULL ORDER BY time ASC",
        (window_start.isoformat(), window_end.isoformat()),
    )
    closed_count = len(fills)
    wins = [Decimal(f["pl"]) for f in fills if Decimal(f["pl"]) > 0]
    losses = [Decimal(f["pl"]) for f in fills if Decimal(f["pl"]) < 0]
    win_rate = (len(wins) / closed_count) if closed_count else 0.0
    profit_sum = sum(wins, start=Decimal("0"))
    loss_sum = -sum(losses, start=Decimal("0"))
    profit_factor = float(profit_sum / loss_sum) if loss_sum > 0 else (
        float("inf") if profit_sum > 0 else 0.0
    )
    average_win = (profit_sum / len(wins)) if wins else Decimal("0")
    average_loss = (sum(losses, start=Decimal("0")) / len(losses)) if losses else Decimal("0")
    largest_loss = min(losses, default=Decimal("0"))

    # Risk rejections by code.
    rej_rows = db.fetchall(
        "SELECT rejection_codes FROM risk_decisions WHERE approved=0 AND decided_at >= ?",
        (window_start.isoformat(),),
    )
    rejection_counts: dict[str, int] = {}
    for r in rej_rows:
        for code in json.loads(r["rejection_codes"] or "[]"):
            rejection_counts[code] = rejection_counts.get(code, 0) + 1

    # Reconciliation events.
    recon_rows = db.fetchall(
        "SELECT message, extras_json FROM system_events WHERE kind='reconcile' AND level='warn' AND time >= ?",
        (window_start.isoformat(),),
    )
    mismatches = [row["message"] for row in recon_rows]

    return WeeklyReport(
        generated_at=now,
        window_start=window_start,
        window_end=window_end,
        account_nav=account_nav,
        realized_pl=realized_pl,
        unrealized_pl=unrealized_pl,
        closed_trade_count=closed_count,
        win_rate=win_rate,
        expectancy_r=0.0,
        average_r=0.0,
        average_win=average_win,
        average_loss=average_loss,
        profit_factor=profit_factor,
        largest_single_loss=largest_loss,
        average_spread_paid_pips=0.0,
        strategy_attribution={},
        pair_attribution={},
        risk_rejections=rejection_counts,
        reconciliation_mismatches=mismatches,
        config_hash=config_hash,
        code_commit_hash=code_commit_hash,
    )
