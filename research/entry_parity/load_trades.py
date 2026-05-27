"""Load bespoke and Backtrader trade / rejection artifacts."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from research.backtrader_exit_parity.compare import load_bespoke_trades
from research.entry_parity.constants import (
    BESPOKE_REJECTION_GLOBS,
    BT_TRADES_DIR,
    CAMPAIGN_BT_TRADE_FILES,
)


def _parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def entry_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        row["instrument"],
        _parse_ts(row["entry_time"]).isoformat(),
        row["side"],
    )


def load_backtrader_trades(repo_root: Path, campaign: str) -> list[dict[str, Any]]:
    path = BT_TRADES_DIR / CAMPAIGN_BT_TRADE_FILES[campaign]
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_bespoke_rejections(
    repo_root: Path, campaign: str, split: str
) -> list[dict[str, Any]]:
    pattern = BESPOKE_REJECTION_GLOBS[campaign].format(split=split)
    paths = sorted(repo_root.glob(pattern))
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                row["split"] = split
                rows.append(row)
    return rows


def load_campaign_entries(
    repo_root: Path, campaign: str
) -> dict[str, Any]:
    bespoke = load_bespoke_trades(repo_root, campaign, "train") + load_bespoke_trades(
        repo_root, campaign, "validation"
    )
    backtrader = load_backtrader_trades(repo_root, campaign)
    rejections = load_bespoke_rejections(repo_root, campaign, "train") + load_bespoke_rejections(
        repo_root, campaign, "validation"
    )
    return {
        "bespoke": bespoke,
        "backtrader": backtrader,
        "rejections": rejections,
    }
