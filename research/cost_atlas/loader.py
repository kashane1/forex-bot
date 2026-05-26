"""Load deduped H4 bid/ask candles via CandleRepo (keep_last policy)."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from forex_bot.data.candle_dedupe import DEDUPE_POLICY  # noqa: E402
from forex_bot.data.db import Database  # noqa: E402
from forex_bot.data.repositories import CandleRepo  # noqa: E402
from research.edge_discovery.real_data import (  # noqa: E402
    SEVEN_MAJORS,
    resolve_h4_store_path,
)

SEVEN_PAIR_UNIVERSE = SEVEN_MAJORS


def candles_to_frame(candles) -> pd.DataFrame:
    rows = []
    for c in candles:
        rows.append(
            {
                "time": c.time.astimezone(UTC) if c.time.tzinfo else c.time.replace(tzinfo=UTC),
                "bid_o": float(c.bid_o) if c.bid_o is not None else None,
                "bid_h": float(c.bid_h) if c.bid_h is not None else None,
                "bid_l": float(c.bid_l) if c.bid_l is not None else None,
                "bid_c": float(c.bid_c) if c.bid_c is not None else None,
                "ask_o": float(c.ask_o) if c.ask_o is not None else None,
                "ask_h": float(c.ask_h) if c.ask_h is not None else None,
                "ask_l": float(c.ask_l) if c.ask_l is not None else None,
                "ask_c": float(c.ask_c) if c.ask_c is not None else None,
                "volume": int(c.volume),
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values("time").set_index("time")
    df["open"] = (df["bid_o"] + df["ask_o"]) / 2.0
    df["high"] = (df["bid_h"] + df["ask_h"]) / 2.0
    df["low"] = (df["bid_l"] + df["ask_l"]) / 2.0
    df["close"] = (df["bid_c"] + df["ask_c"]) / 2.0
    return df


def load_deduped_h4_frame(
    repo_root: Path,
    instrument: str,
    *,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    db_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load deduped H4 frame via ``CandleRepo.list()`` (keep_last)."""
    db_path = db_path or resolve_h4_store_path(repo_root)
    if db_path is None:
        raise FileNotFoundError(
            f"H4 SQLite store not found under {repo_root / 'data'}; "
            "set EDGE_DISCOVERY_H4_DB or restore campaign_002.sqlite3"
        )
    db = Database(db_path)
    try:
        repo = CandleRepo(db)
        candles, stats = repo.list_with_dedupe_stats(
            instrument,
            "H4",
            completed_only=True,
            from_time=from_time,
            to_time=to_time,
        )
    finally:
        db.close()
    frame = candles_to_frame(candles)
    provenance = {
        "instrument": instrument,
        "db_path": str(db_path),
        "dedupe_policy": DEDUPE_POLICY,
        "raw_count": stats.raw_count,
        "deduped_count": stats.deduped_count,
        "duplicates_dropped": stats.duplicates_dropped,
        "bar_count": len(frame),
    }
    return frame, provenance
