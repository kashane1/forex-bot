"""Fill-timing comparison metrics — infrastructure only, not strategy evidence."""

from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

from forex_bot.backtesting.fills import NEXT_BAR_OPEN_UNAVAILABLE


def metrics_from_runs(per_pair: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Aggregate per-pair metric dicts into portfolio-level summary."""
    if not per_pair:
        return {
            "trade_count": 0,
            "expectancy_r": None,
            "profit_factor": None,
            "pairs_positive": 0,
            "pairs_total": 0,
        }
    total = sum(int(m.get("trade_count", 0)) for m in per_pair.values())
    if total == 0:
        return {
            "trade_count": 0,
            "expectancy_r": None,
            "profit_factor": None,
            "pairs_positive": 0,
            "pairs_total": len(per_pair),
            "per_pair": per_pair,
        }
    wexp = (
        sum(float(m["expectancy_r"]) * int(m["trade_count"]) for m in per_pair.values())
        / total
    )
    pfs = [
        float(m["profit_factor"])
        for m in per_pair.values()
        if m.get("profit_factor") is not None
    ]
    pairs_pos = sum(1 for m in per_pair.values() if float(m.get("total_return_pct", 0)) > 0)
    return {
        "trade_count": total,
        "expectancy_r": round(wexp, 4),
        "profit_factor": round(sum(pfs) / len(pfs), 4) if pfs else None,
        "pairs_positive": pairs_pos,
        "pairs_total": len(per_pair),
        "per_pair": per_pair,
    }


def exit_reason_shares(trades: pd.DataFrame) -> dict[str, float]:
    if trades.empty or "exit_reason" not in trades.columns:
        return {}
    counts = trades["exit_reason"].value_counts()
    total = float(counts.sum())
    return {str(k): round(float(v) / total, 4) for k, v in counts.items()}


def compare_exit_reason_shares(
    close_shares: dict[str, float], open_shares: dict[str, float]
) -> list[dict[str, Any]]:
    keys = sorted(set(close_shares) | set(open_shares))
    rows: list[dict[str, Any]] = []
    for k in keys:
        c = close_shares.get(k, 0.0)
        o = open_shares.get(k, 0.0)
        rows.append(
            {
                "exit_reason": k,
                "signal_bar_close_share": c,
                "next_bar_open_share": o,
                "delta_share": round(o - c, 4),
            }
        )
    return rows


def pair_fold_delta_rows(
    close_per_pair: dict[str, dict[str, Any]],
    open_per_pair: dict[str, dict[str, Any]],
    *,
    split: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for instrument in sorted(set(close_per_pair) | set(open_per_pair)):
        c = close_per_pair.get(instrument, {})
        o = open_per_pair.get(instrument, {})
        c_exp = c.get("expectancy_r")
        o_exp = o.get("expectancy_r")
        rows.append(
            {
                "split": split,
                "instrument": instrument,
                "signal_bar_close_trades": c.get("trade_count", 0),
                "next_bar_open_trades": o.get("trade_count", 0),
                "trade_count_delta": int(o.get("trade_count", 0)) - int(c.get("trade_count", 0)),
                "signal_bar_close_expectancy_r": c_exp,
                "next_bar_open_expectancy_r": o_exp,
                "expectancy_r_delta": (
                    round(float(o_exp) - float(c_exp), 4)
                    if c_exp is not None and o_exp is not None
                    else None
                ),
            }
        )
    return rows


def fill_timing_delta(
    close_metrics: dict[str, Any], open_metrics: dict[str, Any]
) -> dict[str, Any]:
    """Portfolio-level deltas (next_bar_open minus signal_bar_close)."""
    def _delta(key: str) -> Any:
        c = close_metrics.get(key)
        o = open_metrics.get(key)
        if c is None or o is None:
            return None
        if isinstance(c, (int, float)) and isinstance(o, (int, float)):
            return round(float(o) - float(c), 4)
        return None

    return {
        "trade_count_delta": _delta("trade_count"),
        "expectancy_r_delta": _delta("expectancy_r"),
        "profit_factor_delta": _delta("profit_factor"),
        "pairs_positive_delta": _delta("pairs_positive"),
        "interpretation": (
            "negative expectancy_r_delta means next_bar_open is worse "
            "(more conservative) than signal_bar_close"
        ),
    }


def entry_price_delta_pips(
    close_trades: pd.DataFrame,
    open_trades: pd.DataFrame,
    *,
    pip_size: float = 0.0001,
) -> dict[str, Any]:
    """Mean entry price delta (open minus close timing) on matched trade counts is approximate."""
    if close_trades.empty or open_trades.empty:
        return {"mean_entry_delta_pips": None, "note": "insufficient trades"}
    if len(close_trades) != len(open_trades):
        return {
            "mean_entry_delta_pips": None,
            "note": "trade counts differ; per-trade pairing not performed",
            "close_trades": len(close_trades),
            "open_trades": len(open_trades),
        }
    c_entry = close_trades["entry_price"].astype(float)
    o_entry = open_trades["entry_price"].astype(float)
    delta = (o_entry - c_entry) / pip_size
    return {
        "mean_entry_delta_pips": round(float(delta.mean()), 4),
        "median_entry_delta_pips": round(float(delta.median()), 4),
    }


def count_next_bar_open_unavailable(rejections: pd.DataFrame | None) -> int:
    if rejections is None or rejections.empty:
        return 0
    if "code" not in rejections.columns:
        return 0
    return int((rejections["code"] == NEXT_BAR_OPEN_UNAVAILABLE).sum())
