"""CAMPAIGN_029 independent parity verifier (no shared execution code).

A deliberately separate re-implementation of the frozen rule's *entry/stop/exit
accounting*, used to cross-check the primary engine (``range_bar_execution``).
It shares only **data inputs** — the precomputed range bars, the M1 index, and the
precomputed H4/D1AGG context labels (themselves cross-checked against the strategy
module) — and reimplements the trigger, stop, fill, and M1-walked exit with its own
code. It imports **none** of the engine's decision/execution helpers.

Backtrader cannot represent irregular-time range bars natively (see
``CAMPAIGN_029_BACKTRADER_PARITY_DESIGN.md``), so this is the "small independent
local verifier" alternative the design allows.
"""

from __future__ import annotations

import bisect
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from forex_bot.data.non_time_bars import RangeBar, pip_size
from forex_bot.research.range_bar_execution import M1Index
from forex_bot.strategies.usdjpy_range_bar_mtf_breakout import RangeBarMtfBreakoutConfig

PAIR = "USD_JPY"


def independent_verify(
    *,
    range_bars: Sequence[RangeBar],
    m1_index: M1Index,
    h4_trends: Sequence[tuple[str, datetime | None, str | None]],
    d1_regimes: Sequence[tuple[str, datetime | None, str | None]],
    params: RangeBarMtfBreakoutConfig,
    fixed_slippage_pips: float = 0.2,
) -> list[dict[str, Any]]:
    bars = [b for b in range_bars if not b.incomplete]
    pip = float(pip_size(PAIR))
    n = len(bars)
    times = m1_index.times
    out: list[dict[str, Any]] = []
    busy_until = -1

    for i in range(n):
        if i <= busy_until:
            continue
        if i < params.structure_lookback or i + 1 >= n:
            continue
        trig = bars[i]

        # --- trigger (independent) ---
        prior = bars[max(0, i - params.pullback_lookback): i]
        prior_reasons = {b.completion_reason for b in prior}
        if trig.completion_reason == "range_up" and "range_down" in prior_reasons:
            want_side = "long"
        elif trig.completion_reason == "range_down" and "range_up" in prior_reasons:
            want_side = "short"
        else:
            continue

        # --- overshoot guard ---
        if trig.thresholds_crossed > params.overshoot_max_thresholds or trig.overshoot_pips > params.overshoot_max_pips:
            continue

        # --- H4 (mandatory) ---
        h4_label, _h4t, h4_block = h4_trends[i]
        if h4_block:
            continue
        if h4_label != ("bullish" if want_side == "long" else "bearish"):
            continue

        # --- D1AGG (optional) ---
        regime, _d1t, d1_block = d1_regimes[i]
        if not d1_block:
            permits = (regime in ("not_bearish_only", "both")) if want_side == "long" else (regime in ("not_bullish_only", "both"))
            if not permits:
                continue
        elif params.d1agg_required:
            continue

        # --- stop (independent) ---
        swing_bars = bars[max(0, i - params.structure_lookback + 1): i + 1]
        if want_side == "long":
            level = min(b.low for b in swing_bars)
        else:
            level = max(b.high for b in swing_bars)
        floor = params.stop_range_multiple * params.range_threshold_pips * pip
        dist = max(abs(trig.close - level), floor)
        stop = trig.close - dist if want_side == "long" else trig.close + dist

        # --- entry ---
        entry_bar = bars[i + 1]
        entry_t = entry_bar.open_time
        e_idx = bisect.bisect_left(times, entry_t)
        if e_idx >= len(times) or times[e_idx] != entry_t:
            continue
        risk = abs(entry_bar.open - stop) / pip
        if risk <= 0:
            continue

        # --- M1-walked exit ---
        time_bar = i + 1 + params.max_bars_in_trade
        if time_bar < n:
            end_t = bars[time_bar].open_time
            w_end = bisect.bisect_left(times, end_t)
            if w_end >= len(times) or times[w_end] != end_t:
                w_end = len(times)
        else:
            w_end = len(times)

        exit_reason = exit_mid = exit_bar = exit_fill_t = None
        for j in range(e_idx, w_end):
            if want_side == "long" and m1_index.mid_low[j] <= stop:
                exit_reason, exit_mid, exit_fill_t = "stop", stop, times[j]
                exit_bar = _bar_for_time(bars, times[j], i + 1, min(time_bar, n - 1))
                break
            if want_side == "short" and m1_index.mid_high[j] >= stop:
                exit_reason, exit_mid, exit_fill_t = "stop", stop, times[j]
                exit_bar = _bar_for_time(bars, times[j], i + 1, min(time_bar, n - 1))
                break
        if exit_reason is None:
            if time_bar < n:
                exit_reason, exit_mid, exit_bar, exit_fill_t = "time", bars[time_bar].open, time_bar, bars[time_bar].open_time
            else:
                exit_reason, exit_mid, exit_bar, exit_fill_t = "end_of_data", bars[n - 1].close, n - 1, bars[n - 1].close_time

        sign = 1.0 if want_side == "long" else -1.0
        gross = sign * (exit_mid - entry_bar.open) / pip
        e_hs = float(m1_index.half_spread[e_idx])
        x_i = bisect.bisect_left(times, exit_fill_t)
        x_hs = float(m1_index.half_spread[x_i]) if (x_i < len(times) and times[x_i] == exit_fill_t) else e_hs
        cost = (e_hs + fixed_slippage_pips) + (x_hs + fixed_slippage_pips)
        net = gross - cost

        out.append({
            "signal_bar_index": i,
            "side": want_side,
            "entry_bar_index": i + 1,
            "exit_bar_index": exit_bar,
            "exit_reason": exit_reason,
            "net_r": net / risk,
            "gross_r": gross / risk,
        })
        busy_until = exit_bar
    return out


def _bar_for_time(bars: Sequence[RangeBar], t: datetime, lo: int, hi: int) -> int:
    for k in range(lo, hi + 1):
        if bars[k].open_time <= t <= bars[k].close_time:
            return k
    return hi


def compare(primary: Sequence[Any], verifier: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Compare primary engine trades vs the independent verifier (parity acceptance)."""
    p_by_sig = {t.signal_bar_index: t for t in primary}
    v_by_sig = {t["signal_bar_index"]: t for t in verifier}
    common = sorted(set(p_by_sig) & set(v_by_sig))
    only_p = sorted(set(p_by_sig) - set(v_by_sig))
    only_v = sorted(set(v_by_sig) - set(p_by_sig))

    exit_match = 0
    r_diffs = []
    side_match = 0
    for s in common:
        p, v = p_by_sig[s], v_by_sig[s]
        if p.exit_reason == v["exit_reason"]:
            exit_match += 1
        if p.side == v["side"]:
            side_match += 1
        r_diffs.append(abs(p.net_r - v["net_r"]))
    n_common = len(common)
    mean_r_diff = sum(r_diffs) / n_common if n_common else 0.0
    max_r_diff = max(r_diffs) if r_diffs else 0.0
    exit_share = exit_match / n_common if n_common else 1.0
    count_diff = abs(len(primary) - len(verifier))

    passed = (
        count_diff <= 1
        and exit_share >= 0.99
        and mean_r_diff <= 0.02
        and not only_p[2:]  # allow tiny boundary set
        and side_match == n_common
    )
    return {
        "primary_trades": len(primary),
        "verifier_trades": len(verifier),
        "common": n_common,
        "trade_count_diff": count_diff,
        "only_primary_signal_bars": only_p[:10],
        "only_verifier_signal_bars": only_v[:10],
        "exit_reason_aligned_share": round(exit_share, 4),
        "side_aligned": side_match == n_common,
        "mean_net_r_diff": round(mean_r_diff, 6),
        "max_net_r_diff": round(max_r_diff, 6),
        "acceptance": {
            "trade_count_diff_le_1": count_diff <= 1,
            "exit_reason_share_ge_0_99": exit_share >= 0.99,
            "mean_r_diff_le_0_02": mean_r_diff <= 0.02,
        },
        "status": "PASS" if passed else "FAIL",
    }
