"""Deduped H4 candle feed for Backtrader exit-parity lane."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import backtrader as bt
import pandas as pd

from research.cost_atlas.loader import load_deduped_h4_frame


class DedupedBidAskFeed(bt.feeds.PandasData):
    """PandasData with bid/ask OHLC lines for exit-parity strategies."""

    lines = (
        "bid_open",
        "bid_high",
        "bid_low",
        "bid_close",
        "ask_open",
        "ask_high",
        "ask_low",
        "ask_close",
    )
    params = (
        ("bid_open", -1),
        ("bid_high", -1),
        ("bid_low", -1),
        ("bid_close", -1),
        ("ask_open", -1),
        ("ask_high", -1),
        ("ask_low", -1),
        ("ask_close", -1),
    )


def prepare_candle_window(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize loader/backtrader frame for ``CandleFrame`` / strategy use."""
    df = frame.copy()
    rename = {
        "bid_o": "bid_open",
        "bid_h": "bid_high",
        "bid_l": "bid_low",
        "bid_c": "bid_close",
        "ask_o": "ask_open",
        "ask_h": "ask_high",
        "ask_l": "ask_low",
        "ask_c": "ask_close",
    }
    for src, dst in rename.items():
        if src in df.columns and dst not in df.columns:
            df[dst] = df[src]
    if "open" not in df.columns:
        df["open"] = (df["bid_open"] + df["ask_open"]) / 2.0
        df["high"] = (df["bid_high"] + df["ask_high"]) / 2.0
        df["low"] = (df["bid_low"] + df["ask_low"]) / 2.0
        df["close"] = (df["bid_close"] + df["ask_close"]) / 2.0
    if "complete" not in df.columns:
        df["complete"] = True
    return df


def frame_to_backtrader_df(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize deduped loader frame for ``DedupedBidAskFeed``."""
    return prepare_candle_window(frame)


def load_split_frame(
    repo_root: Path,
    instrument: str,
    *,
    from_time: datetime,
    to_time: datetime,
    db_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    frame, meta = load_deduped_h4_frame(
        repo_root,
        instrument,
        from_time=from_time,
        to_time=to_time,
        db_path=db_path,
    )
    return frame_to_backtrader_df(frame), meta
