"""Independent exit state machine ported from ``BacktestEngine``.

Mirrors stop / target / time / protective-stop precedence from
``src/forex_bot/backtesting/engine.py`` without importing the engine loop.
Gap-fill policy defaults to ``none`` (CAMPAIGN_001–018 byte-identical).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import pandas as pd


@dataclass
class OpenTrade:
    side: str
    units: int
    entry_price: Decimal
    entry_time: pd.Timestamp
    stop_price: Decimal
    initial_stop_price: Decimal
    spread_pips_at_entry: Decimal
    take_profit_price: Decimal | None = None
    bars_held: int = 0
    peak_mfe_r: float = 0.0
    protective_armed: bool = False
    protective_arm_bar: int | None = None
    protective_arm_mfe_r: float | None = None
    protective_arm_time: pd.Timestamp | None = None


@dataclass(frozen=True)
class ExitResult:
    exit_reason: str
    exit_price: Decimal
    ambiguous_exit: bool = False
    gap_fill: bool = False
    gap_fill_distance_pips: Decimal | None = None


def _dec(row: pd.Series, col: str, fallback: str) -> Decimal:
    val = row[col]
    if pd.notna(val):
        return Decimal(str(val))
    return Decimal(str(row[fallback]))


def process_bar_exit(
    trade: OpenTrade,
    row: pd.Series,
    ts: pd.Timestamp,
    *,
    max_bars_in_trade: int,
    protective_stop_after_r: float | None,
    pip_size: Decimal,
    gap_fill_policy: str = "none",
    trailing_stop_atr_multiple: float | None = None,
    atr_value: float | None = None,
) -> ExitResult | None:
    """Advance ``trade`` by one bar; return an exit if triggered."""
    trade.bars_held += 1

    bid_low = _dec(row, "bid_low", "low")
    ask_high = _dec(row, "ask_high", "high")
    bid_high = _dec(row, "bid_high", "high")
    ask_low = _dec(row, "ask_low", "low")
    bid_close = _dec(row, "bid_close", "close")
    ask_close = _dec(row, "ask_close", "close")
    bid_open = _dec(row, "bid_open", "open")
    ask_open = _dec(row, "ask_open", "open")

    pre_trailing_stop_price = trade.stop_price

    risk_dist = (trade.entry_price - trade.initial_stop_price).copy_abs()
    if risk_dist > 0:
        if trade.side == "long":
            fav_move = bid_high - trade.entry_price
        else:
            fav_move = trade.entry_price - ask_low
        if fav_move > 0:
            mfe_r = float(fav_move / risk_dist)
            trade.peak_mfe_r = max(trade.peak_mfe_r, mfe_r)
        if (
            protective_stop_after_r is not None
            and not trade.protective_armed
            and trade.peak_mfe_r >= protective_stop_after_r
        ):
            trade.protective_armed = True
            trade.protective_arm_bar = trade.bars_held
            trade.protective_arm_mfe_r = trade.peak_mfe_r
            trade.protective_arm_time = ts
            be_stop = trade.entry_price
            if trade.side == "long":
                if be_stop > trade.stop_price:
                    trade.stop_price = be_stop
            elif be_stop < trade.stop_price:
                trade.stop_price = be_stop

    if (
        trailing_stop_atr_multiple is not None
        and atr_value is not None
        and pd.notna(atr_value)
    ):
        cur_atr = Decimal(str(atr_value))
        if trade.side == "long":
            new_stop = bid_close - cur_atr * Decimal(str(trailing_stop_atr_multiple))
            if new_stop > trade.stop_price:
                trade.stop_price = new_stop
        else:
            new_stop = ask_close + cur_atr * Decimal(str(trailing_stop_atr_multiple))
            if new_stop < trade.stop_price:
                trade.stop_price = new_stop

    exit_reason: str | None = None
    exit_price: Decimal | None = None
    did_gap_fill = False
    gap_fill_distance_pips: Decimal | None = None
    tp = trade.take_profit_price

    if gap_fill_policy == "gap_through":
        is_long = trade.side == "long"
        open_px = bid_open if is_long else ask_open
        stop_breached = (
            open_px < pre_trailing_stop_price if is_long else open_px > pre_trailing_stop_price
        )
        tp_breached = tp is not None and (open_px > tp if is_long else open_px < tp)
        if stop_breached:
            exit_reason = (
                "trailing_stop"
                if trade.stop_price != trade.initial_stop_price
                else "stop"
            )
            exit_price = open_px
            did_gap_fill = True
            gap_fill_distance_pips = (pre_trailing_stop_price - open_px).copy_abs() / pip_size
        elif tp_breached and tp is not None:
            exit_reason = "target"
            exit_price = open_px
            did_gap_fill = True
            gap_fill_distance_pips = (open_px - tp).copy_abs() / pip_size

    if not did_gap_fill:
        if trade.side == "long":
            if bid_low <= trade.stop_price:
                if trade.protective_armed and trade.stop_price == trade.entry_price:
                    exit_reason = "protective_stop"
                else:
                    exit_reason = (
                        "trailing_stop"
                        if trade.stop_price != trade.initial_stop_price
                        else "stop"
                    )
                exit_price = trade.stop_price
            elif tp is not None and bid_high >= tp:
                exit_reason = "target"
                exit_price = tp
            elif trade.bars_held >= max_bars_in_trade:
                exit_reason = "time"
                exit_price = bid_close
        else:
            if ask_high >= trade.stop_price:
                if trade.protective_armed and trade.stop_price == trade.entry_price:
                    exit_reason = "protective_stop"
                else:
                    exit_reason = (
                        "trailing_stop"
                        if trade.stop_price != trade.initial_stop_price
                        else "stop"
                    )
                exit_price = trade.stop_price
            elif tp is not None and ask_low <= tp:
                exit_reason = "target"
                exit_price = tp
            elif trade.bars_held >= max_bars_in_trade:
                exit_reason = "time"
                exit_price = ask_close

    if exit_reason is None or exit_price is None:
        return None

    tp_also_in_range = False
    if exit_reason in {"stop", "trailing_stop"} and tp is not None:
        tp_also_in_range = (
            bid_high >= tp if trade.side == "long" else ask_low <= tp
        )

    return ExitResult(
        exit_reason=exit_reason,
        exit_price=exit_price,
        ambiguous_exit=tp_also_in_range,
        gap_fill=did_gap_fill,
        gap_fill_distance_pips=gap_fill_distance_pips,
    )


def exit_reason_stats(trades: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate exit-reason counts and expectancy R."""
    if not trades:
        return {"total_trades": 0, "by_exit_reason": {}}
    by_reason: dict[str, list[float]] = {}
    bars_by_reason: dict[str, list[int]] = {}
    for t in trades:
        reason = t["exit_reason"]
        by_reason.setdefault(reason, []).append(float(t.get("r_multiple") or 0.0))
        bars_by_reason.setdefault(reason, []).append(int(t.get("bars_held") or 0))
    total = len(trades)
    out: dict[str, Any] = {"total_trades": total, "by_exit_reason": {}}
    for reason, rs in sorted(by_reason.items()):
        count = len(rs)
        out["by_exit_reason"][reason] = {
            "count": count,
            "share_pct": round(100.0 * count / total, 2),
            "expectancy_r": round(sum(rs) / count, 4) if count else 0.0,
            "avg_bars_held": round(sum(bars_by_reason[reason]) / count, 2) if count else 0.0,
        }
    return out
