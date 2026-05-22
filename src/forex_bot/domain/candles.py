"""Candles, candle frames, and candle requests."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

# "D" is native OANDA daily (closes at the 17:00 NY rollover — invalid for
# this backtester, see CAMPAIGN_006). "D1AGG" is a synthetic daily bar
# aggregated from H4 candles by forex_bot.backtesting.d1_aggregation; it is
# the only valid daily-research source. The two are deliberately distinct.
Granularity = Literal["M1", "M5", "M15", "M30", "H1", "H4", "D", "D1AGG"]
PriceComponent = Literal["B", "A", "M", "BA", "BM", "AM", "BAM"]


class Candle(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    instrument: str
    granularity: Granularity
    time: datetime
    complete: bool
    volume: int = 0
    bid_o: Decimal | None = None
    bid_h: Decimal | None = None
    bid_l: Decimal | None = None
    bid_c: Decimal | None = None
    ask_o: Decimal | None = None
    ask_h: Decimal | None = None
    ask_l: Decimal | None = None
    ask_c: Decimal | None = None
    mid_o: Decimal | None = None
    mid_h: Decimal | None = None
    mid_l: Decimal | None = None
    mid_c: Decimal | None = None

    @property
    def mid_close(self) -> Decimal | None:
        if self.mid_c is not None:
            return self.mid_c
        if self.bid_c is not None and self.ask_c is not None:
            return (self.bid_c + self.ask_c) / 2
        return None


class CandleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instrument: str
    granularity: Granularity
    price: PriceComponent = "BA"
    count: int | None = None
    from_time: datetime | None = None
    to_time: datetime | None = None
    daily_alignment: int = 17
    alignment_timezone: str = "America/New_York"
    weekly_alignment: str = "Friday"
    include_first: bool = True


class CandleFrame(BaseModel):
    """A typed wrapper around a pandas DataFrame of completed candles.

    The DataFrame is indexed by candle close timestamp (tz-aware UTC) and
    contains the columns we actually use in indicators: open, high, low,
    close (mid-derived if unavailable), bid_close, ask_close, complete,
    volume.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    instrument: str
    granularity: Granularity
    df: pd.DataFrame = Field(default_factory=pd.DataFrame)

    @classmethod
    def from_candles(
        cls, instrument: str, granularity: Granularity, candles: list[Candle]
    ) -> CandleFrame:
        rows: list[dict[str, object]] = []
        for c in candles:
            mid_c = c.mid_close
            mid_h = c.mid_h
            mid_l = c.mid_l
            mid_o = c.mid_o
            if mid_c is None or mid_h is None or mid_l is None or mid_o is None:
                if c.bid_c and c.ask_c and c.bid_o and c.ask_o:
                    mid_o = (c.bid_o + c.ask_o) / 2
                    mid_c = (c.bid_c + c.ask_c) / 2
                    mid_h = (
                        (c.bid_h + c.ask_h) / 2
                        if c.bid_h and c.ask_h
                        else max(mid_o, mid_c)
                    )
                    mid_l = (
                        (c.bid_l + c.ask_l) / 2
                        if c.bid_l and c.ask_l
                        else min(mid_o, mid_c)
                    )
            rows.append(
                {
                    "time": c.time,
                    "open": float(mid_o) if mid_o is not None else None,
                    "high": float(mid_h) if mid_h is not None else None,
                    "low": float(mid_l) if mid_l is not None else None,
                    "close": float(mid_c) if mid_c is not None else None,
                    "bid_open": float(c.bid_o) if c.bid_o is not None else None,
                    "bid_high": float(c.bid_h) if c.bid_h is not None else None,
                    "bid_low": float(c.bid_l) if c.bid_l is not None else None,
                    "bid_close": float(c.bid_c) if c.bid_c is not None else None,
                    "ask_open": float(c.ask_o) if c.ask_o is not None else None,
                    "ask_high": float(c.ask_h) if c.ask_h is not None else None,
                    "ask_low": float(c.ask_l) if c.ask_l is not None else None,
                    "ask_close": float(c.ask_c) if c.ask_c is not None else None,
                    "complete": c.complete,
                    "volume": c.volume,
                }
            )
        df = pd.DataFrame(rows)
        if not df.empty:
            df["time"] = pd.to_datetime(df["time"], utc=True)
            df = df.set_index("time").sort_index()
        return cls(instrument=instrument, granularity=granularity, df=df)

    def completed_only(self) -> CandleFrame:
        if self.df.empty:
            return self
        filtered = self.df[self.df["complete"]]
        return CandleFrame(instrument=self.instrument, granularity=self.granularity, df=filtered)

    def __len__(self) -> int:
        return len(self.df)
