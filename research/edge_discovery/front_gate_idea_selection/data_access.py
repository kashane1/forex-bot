"""Raw-sqlite3 candle loader for the front-gate sprint.

Import-isolation: this file lives under ``research/edge_discovery/`` and is
scanned by ``tests/research/edge_discovery/test_isolation.py``, which forbids any
``forex_bot.*`` import except ``forex_bot.financing``. It therefore reads the
local candle store with **raw sqlite3** (read-only), exactly as
``research.edge_discovery.real_data`` does — no ``forex_bot.data`` dependency, no
broker reach. Returns a UTC-indexed bid/ask + mid OHLC frame shaped like the
``research.cost_atlas`` loader output so ``cost_atlas.metrics.compute_bar_metrics``
consumes it unchanged. Diagnostic only.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

_BIDASK = ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c")


def load_frame(db_path: str | Path, instrument: str, granularity: str) -> pd.DataFrame:
    """Load completed candles for one (instrument, granularity) from the local
    SQLite store. Returns a UTC-indexed frame with bid/ask OHLC, volume, and
    derived mid ``open/high/low/close``. Empty frame if no rows."""
    db_path = Path(db_path)
    if not db_path.is_file():
        raise FileNotFoundError(f"candle store not found: {db_path}")
    query = (
        "SELECT time, bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c, volume "
        "FROM candles WHERE instrument = ? AND granularity = ? AND complete = 1 "
        "ORDER BY time ASC"
    )
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        df = pd.read_sql_query(query, conn, params=[instrument, granularity])
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"], utc=True)
    for col in _BIDASK:
        df[col] = df[col].astype(float)
    df = df.sort_values("time").drop_duplicates("time", keep="last").set_index("time")
    df["open"] = (df["bid_o"] + df["ask_o"]) / 2.0
    df["high"] = (df["bid_h"] + df["ask_h"]) / 2.0
    df["low"] = (df["bid_l"] + df["ask_l"]) / 2.0
    df["close"] = (df["bid_c"] + df["ask_c"]) / 2.0
    return df
