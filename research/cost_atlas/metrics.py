"""Per-bar spread and ATR metrics."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from forex_bot.strategies.indicators import atr  # noqa: E402
from research.cost_atlas.session import (  # noqa: E402
    is_rollover_adjacent,
    is_weekend_adjacent,
    session_bucket,
    weekday_name,
)
from research.edge_discovery.costs import pip_value_for  # noqa: E402


def spread_price(bid_close: float, ask_close: float) -> float:
    return max(ask_close - bid_close, 0.0)


def spread_pips(instrument: str, bid_close: float, ask_close: float) -> float:
    pip = pip_value_for(instrument)
    return spread_price(bid_close, ask_close) / pip


def spread_to_atr(spread_px: float, atr_px: float) -> float:
    if atr_px <= 0:
        return float("inf")
    return spread_px / atr_px


def volatility_regime(atr_series: pd.Series, *, low_pct: float = 33.0, high_pct: float = 67.0) -> pd.Series:
    """Bucket ATR into low / mid / high using rolling percentiles on completed history."""
    ranks = atr_series.rank(pct=True, method="average") * 100.0
    out = pd.Series(index=atr_series.index, dtype="object")
    out[ranks <= low_pct] = "low_vol"
    out[(ranks > low_pct) & (ranks <= high_pct)] = "mid_vol"
    out[ranks > high_pct] = "high_vol"
    return out


def compute_bar_metrics(
    instrument: str,
    frame: pd.DataFrame,
    *,
    atr_length: int = 14,
) -> pd.DataFrame:
    """Return per-bar metrics from a bid/ask H4 frame indexed by UTC time.

    Required columns: ``bid_c``, ``ask_c``, ``bid_h``, ``bid_l``, ``ask_h``,
    ``ask_l``, ``close`` (mid close). Adds spread, ATR, session, weekday,
    vol regime columns.
    """
    required = {"bid_c", "ask_c", "bid_h", "bid_l", "ask_h", "ask_l", "close"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"frame missing columns: {sorted(missing)}")

    out = frame.copy()
    out["spread_px"] = out["ask_c"] - out["bid_c"]
    out["spread_pips"] = out.apply(
        lambda r: spread_pips(instrument, float(r["bid_c"]), float(r["ask_c"])),
        axis=1,
    )
    mid_high = (out["bid_h"] + out["ask_h"]) / 2.0
    mid_low = (out["bid_l"] + out["ask_l"]) / 2.0
    atr_px = atr(mid_high, mid_low, out["close"], length=atr_length)
    out["atr_px"] = atr_px
    out["atr_pips"] = out["atr_px"] / pip_value_for(instrument)
    out["spread_to_atr_pct"] = out["spread_px"] / out["atr_px"].replace(0, pd.NA) * 100.0
    out["hour_utc"] = out.index.hour
    out["session"] = out["hour_utc"].map(session_bucket)
    out["weekday"] = out.index.map(weekday_name)
    out["vol_regime"] = volatility_regime(out["atr_px"].dropna()).reindex(out.index)
    out["rollover_adjacent"] = [
        is_rollover_adjacent(int(h), wd)
        for h, wd in zip(out["hour_utc"], out["weekday"], strict=True)
    ]
    out["weekend_adjacent"] = out["weekday"].map(is_weekend_adjacent)
    return out
