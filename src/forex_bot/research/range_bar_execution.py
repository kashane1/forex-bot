"""CAMPAIGN_029 — M1-resolved range-bar execution engine (research only).

Resolves the frozen ``usdjpy_range_bar_mtf_breakout 0.1.0-c029`` rule into trades
against the **underlying M1 tape**, not the compressed range-bar OHLC:

  * **Entry** = the open of the *next completed range bar* after the trigger bar's
    close (the first M1 row of bar ``i+1``). Never a same-(range-)bar fill.
  * **Stop** = the frozen structural stop (``max(5-bar swing, 20pip floor)``),
    **walked forward on M1** within the holding window. Conservative ambiguity:
    within a single M1 candle a stop touch is taken (we never assume we escaped),
    and the stop has priority over the time exit (``stop → time → end_of_data``).
  * **Time stop** = exactly ``max_bars_in_trade`` completed range bars after entry.
  * **No** take-profit.
  * **Cost** = conservative & M1-resolved: the real half-spread at the entry and
    exit M1 fill rows plus ``fixed_slippage_pips`` adverse on each side.

This module is **research only**: no broker / executor / OANDA / order path, no
approval. The HTF trend / D1AGG regime per range bar are supplied precomputed (see
:func:`precompute_h4_trends` / :func:`precompute_d1agg_regimes`) so the engine does
no per-bar HTF frame rebuilding; those use the *same* rule as the strategy module
and are cross-checked in tests.
"""

from __future__ import annotations

import bisect
import math
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from forex_bot.data.non_time_bars import RangeBar, pip_size
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.features.htf_align import HTF_STALE, HTF_UNAVAILABLE
from forex_bot.strategies.indicators import ema
from forex_bot.strategies.usdjpy_range_bar_mtf_breakout import (
    EXIT_EOD,
    EXIT_STOP,
    EXIT_TIME,
    PAIR,
    RangeBarMtfBreakoutConfig,
    Side,
    d1agg_allows,
    is_extreme_overshoot,
    pullback_reclaim_side,
    structural_stop,
)

Trend = str


@dataclass(frozen=True)
class RangeBarTrade:
    """One resolved trade — the campaign's trade-ledger row."""

    signal_bar_index: int
    signal_bar_time: datetime          # trigger range-bar close_time (decision)
    entry_bar_index: int
    entry_bar_time: datetime           # entry range-bar close_time
    entry_source_timestamp: datetime   # M1 open_time of the entry range bar
    exit_bar_index: int
    exit_source_timestamp: datetime    # M1 time of the resolved exit
    side: Side
    entry_mid: float
    exit_mid: float
    stop_level: float
    exit_reason: str
    bars_held: int
    wall_clock_seconds: float
    risk_pips: float
    gross_pips: float
    gross_r: float
    entry_cost_pips: float
    exit_cost_pips: float
    slippage_pips: float
    total_cost_pips: float
    net_pips: float
    net_r: float
    # HTF provenance
    h4_trend: str
    h4_feature_time: datetime | None
    d1agg_regime: str
    d1agg_feature_time: datetime | None
    d1agg_applied: bool
    # range-bar provenance
    trigger_completion_reason: str
    trigger_thresholds_crossed: int
    trigger_overshoot_pips: float
    # safety
    approved: bool = False

    def to_row(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# M1 helpers
# --------------------------------------------------------------------------- #
def _mid_low_high(c: Candle) -> tuple[float, float]:
    """(mid_low, mid_high) for a candle, falling back to (bid+ask)/2 per field."""
    ml = c.mid_l
    mh = c.mid_h
    if ml is None and c.bid_l is not None and c.ask_l is not None:
        ml = (c.bid_l + c.ask_l) / 2
    if mh is None and c.bid_h is not None and c.ask_h is not None:
        mh = (c.bid_h + c.ask_h) / 2
    if ml is None or mh is None:
        raise ValueError(f"missing low/high (mid or bid/ask) at {c.time}")
    return float(ml), float(mh)


def _half_spread_pips(c: Candle, pip: float) -> float:
    """Half the bid/ask spread at the open of ``c``, in pips (0 if unavailable)."""
    if c.bid_o is None or c.ask_o is None:
        return 0.0
    return float((c.ask_o - c.bid_o) / 2) / pip


@dataclass(frozen=True)
class M1Index:
    """Lightweight numeric view of the M1 tape (no Candle objects retained)."""

    times: list[datetime]
    mid_low: np.ndarray
    mid_high: np.ndarray
    mid_open: np.ndarray
    half_spread: np.ndarray

    @classmethod
    def build(cls, m1: Sequence[Candle], pip: float) -> M1Index:
        times: list[datetime] = []
        lows: list[float] = []
        highs: list[float] = []
        opens: list[float] = []
        hs: list[float] = []
        prev: datetime | None = None
        for c in m1:
            t = c.time if c.time.tzinfo else c.time.replace(tzinfo=UTC)
            if prev is not None and t < prev:
                raise ValueError(f"M1 not sorted: {t} < {prev}")
            prev = t
            lo, hi = _mid_low_high(c)
            mo = c.mid_o
            if mo is None and c.bid_o is not None and c.ask_o is not None:
                mo = (c.bid_o + c.ask_o) / 2
            times.append(t)
            lows.append(lo)
            highs.append(hi)
            opens.append(float(mo) if mo is not None else float("nan"))
            hs.append(_half_spread_pips(c, pip))
        return cls(times, np.array(lows), np.array(highs), np.array(opens), np.array(hs))

    def index_at(self, t: datetime) -> int | None:
        i = bisect.bisect_left(self.times, t)
        if i < len(self.times) and self.times[i] == t:
            return i
        return None


# --------------------------------------------------------------------------- #
# Precomputed HTF trend / D1AGG regime (same rule as the strategy module)
# --------------------------------------------------------------------------- #
def _ema_close_arrays(frame: CandleFrame, ema_fast: int, ema_slow: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    df = frame.completed_only().df
    if df.empty:
        empty = np.array([])
        return empty, empty, empty, np.array([], dtype="datetime64[ns]")
    close = df["close"].astype(float).reset_index(drop=True)
    ef = ema(close, ema_fast).to_numpy()
    es = ema(close, ema_slow).to_numpy()
    # tz-naive UTC ns for clean searchsorted (avoids tz-aware datetime64 warnings)
    times = pd.to_datetime(df.index, utc=True).tz_convert("UTC").tz_localize(None).to_numpy()
    return close.to_numpy(), ef, es, times


def _staleness_seconds(decision: pd.Timestamp, feature_time_ns: np.datetime64) -> float:
    return (decision.tz_convert("UTC").tz_localize(None) - feature_time_ns) / np.timedelta64(1, "s")


def precompute_h4_trends(
    h4_frame: CandleFrame,
    decision_times: Sequence[datetime],
    params: RangeBarMtfBreakoutConfig,
    *,
    max_staleness_seconds: float | None = None,
) -> list[tuple[Trend, datetime | None, str | None]]:
    """Per-decision H4 trend (close vs EMA50 + EMA50 slope) — vectorised aligner.

    Identical rule to ``usdjpy_range_bar_mtf_breakout.aligned_h4_trend`` but the
    EMA frame is built once and decisions are resolved with ``searchsorted`` (last
    completed H4 bar at/before the decision). Cross-checked against the strategy in
    tests. If ``max_staleness_seconds`` is set, an aligned bar older than the bound
    is returned as ``HTF_STALE`` (a block) — the frozen "H4 stale ⇒ no trade" policy.
    """
    close, _ef, es, times = _ema_close_arrays(h4_frame, params.h4_ema_fast, params.h4_ema_slow)
    need = params.h4_ema_slow + params.h4_ema_slope_bars + 1
    out: list[tuple[Trend, datetime | None, str | None]] = []
    times_ns = times.astype("datetime64[ns]") if len(times) else times
    dt_index = pd.DatetimeIndex(pd.to_datetime(list(decision_times), utc=True))
    sb = params.h4_ema_slope_bars
    for ts in dt_index:
        if len(times) < need:
            out.append(("neutral", None, HTF_UNAVAILABLE))
            continue
        pos = int(np.searchsorted(times_ns, np.datetime64(ts.tz_convert("UTC").tz_localize(None)), side="right")) - 1
        if pos < sb or pos < 0:
            out.append(("neutral", None, HTF_UNAVAILABLE))
            continue
        c = close[pos]
        es_now = es[pos]
        es_prev = es[pos - sb]
        if not all(math.isfinite(v) for v in (c, es_now, es_prev)):
            out.append(("neutral", None, HTF_UNAVAILABLE))
            continue
        ft = pd.Timestamp(times[pos]).tz_localize("UTC").to_pydatetime()
        if max_staleness_seconds is not None and _staleness_seconds(ts, times_ns[pos]) > max_staleness_seconds:
            out.append(("neutral", ft, HTF_STALE))
            continue
        slope = es_now - es_prev
        if c > es_now and slope > 0:
            out.append(("bullish", ft, None))
        elif c < es_now and slope < 0:
            out.append(("bearish", ft, None))
        else:
            out.append(("neutral", ft, None))
    return out


def precompute_d1agg_regimes(
    d1agg_frame: CandleFrame | None,
    decision_times: Sequence[datetime],
    params: RangeBarMtfBreakoutConfig,
    *,
    max_staleness_seconds: float | None = None,
) -> list[tuple[str, datetime | None, str | None]]:
    """Per-decision D1AGG permissive regime — vectorised, same rule as the strategy.

    With ``max_staleness_seconds`` set, an aligned D1AGG bar older than the bound is
    ``HTF_STALE`` (a block); the engine then skips the optional D1AGG gate.
    """
    n = len(decision_times)
    if d1agg_frame is None:
        return [("unavailable", None, HTF_UNAVAILABLE)] * n
    close, ef, es, times = _ema_close_arrays(d1agg_frame, params.d1_ema_fast, params.d1_ema_slow)
    need = params.d1_ema_slow + params.d1_ema_slope_bars + 1
    out: list[tuple[str, datetime | None, str | None]] = []
    times_ns = times.astype("datetime64[ns]") if len(times) else times
    dt_index = pd.DatetimeIndex(pd.to_datetime(list(decision_times), utc=True))
    sb = params.d1_ema_slope_bars
    for ts in dt_index:
        if len(times) < need:
            out.append(("neither", None, HTF_UNAVAILABLE))
            continue
        pos = int(np.searchsorted(times_ns, np.datetime64(ts.tz_convert("UTC").tz_localize(None)), side="right")) - 1
        if pos < sb or pos < 0:
            out.append(("neither", None, HTF_UNAVAILABLE))
            continue
        c = close[pos]
        es_now = es[pos]
        ef_now = ef[pos]
        ef_prev = ef[pos - sb]
        if not all(math.isfinite(v) for v in (c, es_now, ef_now, ef_prev)):
            out.append(("neither", None, HTF_UNAVAILABLE))
            continue
        ft = pd.Timestamp(times[pos]).tz_localize("UTC").to_pydatetime()
        if max_staleness_seconds is not None and _staleness_seconds(ts, times_ns[pos]) > max_staleness_seconds:
            out.append(("neither", ft, HTF_STALE))
            continue
        slope = ef_now - ef_prev
        not_bearish = c >= es_now or slope >= 0
        not_bullish = c <= es_now or slope <= 0
        ft = pd.Timestamp(times[pos]).tz_localize("UTC").to_pydatetime()
        if not_bearish and not_bullish:
            out.append(("both", ft, None))
        elif not_bearish:
            out.append(("not_bearish_only", ft, None))
        elif not_bullish:
            out.append(("not_bullish_only", ft, None))
        else:
            out.append(("neither", ft, None))
    return out


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #
def run_range_bar_execution(
    *,
    range_bars: Sequence[RangeBar],
    m1_candles: Sequence[Candle] | None = None,
    m1_index: M1Index | None = None,
    h4_trends: Sequence[tuple[str, datetime | None, str | None]],
    d1_regimes: Sequence[tuple[str, datetime | None, str | None]],
    params: RangeBarMtfBreakoutConfig,
    fixed_slippage_pips: float = 0.2,
    instrument: str = PAIR,
) -> list[RangeBarTrade]:
    """Resolve the frozen rule into trades on the M1 tape. Deterministic.

    Provide either ``m1_candles`` (a Candle sequence, indexed here) or a prebuilt
    ``m1_index`` (cheaper for full-corpus runs).
    """
    bars = [b for b in range_bars if not b.incomplete]
    if len(h4_trends) != len(bars) or len(d1_regimes) != len(bars):
        raise ValueError("h4_trends/d1_regimes length must match completed range bars")
    if instrument != PAIR:
        raise ValueError(f"CAMPAIGN_029 is {PAIR}-only; got {instrument!r}")
    pip = float(pip_size(instrument))
    if m1_index is not None:
        m1 = m1_index
    elif m1_candles is not None:
        m1 = M1Index.build(m1_candles, pip)
    else:
        raise ValueError("provide m1_candles or m1_index")
    n = len(bars)
    trades: list[RangeBarTrade] = []
    blocked_until = -1  # one position at a time; no trigger at/before this index

    for i in range(n):
        if i <= blocked_until:
            continue
        if i < params.structure_lookback or i + 1 >= n:
            continue  # need history for the swing, and a next bar to enter on
        trigger = bars[i]
        if trigger.instrument != PAIR:
            raise ValueError(f"CAMPAIGN_029 is {PAIR}-only; got {trigger.instrument!r}")

        window = bars[max(0, i - params.pullback_lookback): i + 1]
        side = pullback_reclaim_side(window, pullback_lookback=params.pullback_lookback)
        if side is None:
            continue
        if is_extreme_overshoot(
            trigger, max_thresholds=params.overshoot_max_thresholds, max_overshoot_pips=params.overshoot_max_pips
        ):
            continue

        h4_trend, h4_time, h4_block = h4_trends[i]
        if h4_block:
            continue
        wanted = "bullish" if side == "long" else "bearish"
        if h4_trend != wanted:
            continue

        regime, d1_time, d1_block = d1_regimes[i]
        d1agg_applied = False
        if not d1_block:
            d1agg_applied = True
            if not d1agg_allows(regime, side):
                continue
        elif params.d1agg_required:
            continue

        struct_window = bars[max(0, i - params.structure_lookback + 1): i + 1]
        stop = structural_stop(
            struct_window,
            side=side,
            structure_lookback=params.structure_lookback,
            range_threshold_pips=params.range_threshold_pips,
            stop_range_multiple=params.stop_range_multiple,
            instrument=instrument,
        )

        trade = _resolve_trade(
            i=i, side=side, stop=stop, bars=bars, m1=m1, params=params, pip=pip,
            fixed_slippage_pips=fixed_slippage_pips,
            h4_trend=h4_trend, h4_time=h4_time,
            regime=regime if d1agg_applied else "unavailable", d1_time=d1_time, d1agg_applied=d1agg_applied,
        )
        if trade is None:
            continue
        trades.append(trade)
        blocked_until = trade.exit_bar_index
    return trades


def _resolve_trade(
    *, i, side, stop, bars, m1, params, pip, fixed_slippage_pips,
    h4_trend, h4_time, regime, d1_time, d1agg_applied,
) -> RangeBarTrade | None:
    n = len(bars)
    entry_bar = bars[i + 1]
    entry_idx = i + 1
    entry_mid = entry_bar.open
    entry_src = entry_bar.open_time
    entry_m1 = m1.index_at(entry_src)
    if entry_m1 is None:
        return None  # entry bar's first M1 row not in the M1 set → cannot fill

    risk_pips = abs(entry_mid - stop) / pip
    if risk_pips <= 0:
        return None

    # time-exit range bar = entry bar + max_bars_in_trade
    time_exit_idx = entry_idx + params.max_bars_in_trade
    has_time_bar = time_exit_idx < n
    walk_end_time = bars[time_exit_idx].open_time if has_time_bar else None
    walk_end_m1 = m1.index_at(walk_end_time) if walk_end_time is not None else len(m1.times)
    if walk_end_m1 is None:
        walk_end_m1 = len(m1.times)

    # Walk M1 from entry row (inclusive) up to (exclusive) the time-exit bar's open.
    exit_reason = None
    exit_src = None
    exit_mid = None
    for j in range(entry_m1, walk_end_m1):
        if side == "long" and m1.mid_low[j] <= stop:
            exit_reason, exit_src, exit_mid = EXIT_STOP, m1.times[j], stop
            break
        if side == "short" and m1.mid_high[j] >= stop:
            exit_reason, exit_src, exit_mid = EXIT_STOP, m1.times[j], stop
            break

    if exit_reason is None:
        if has_time_bar:
            exit_reason = EXIT_TIME
            exit_idx_bar = time_exit_idx
            exit_mid = bars[time_exit_idx].open
            exit_src = bars[time_exit_idx].open_time
        else:
            exit_reason = EXIT_EOD
            exit_idx_bar = n - 1
            exit_mid = bars[n - 1].close
            exit_src = bars[n - 1].close_time
    else:
        # map the stop M1 time back to the range bar that contains it
        exit_idx_bar = _bar_index_for_time(bars, exit_src, lo=entry_idx, hi=min(time_exit_idx, n - 1))

    # cost: half-spread at entry + exit fill rows + adverse slippage each side
    entry_hs = float(m1.half_spread[entry_m1])
    exit_m1 = m1.index_at(exit_src)
    exit_hs = float(m1.half_spread[exit_m1]) if exit_m1 is not None else entry_hs
    entry_cost = entry_hs + fixed_slippage_pips
    exit_cost = exit_hs + fixed_slippage_pips
    total_cost = entry_cost + exit_cost

    direction = 1.0 if side == "long" else -1.0
    gross_pips = direction * (exit_mid - entry_mid) / pip
    net_pips = gross_pips - total_cost
    wall = (exit_src - entry_src).total_seconds()

    return RangeBarTrade(
        signal_bar_index=i,
        signal_bar_time=bars[i].close_time,
        entry_bar_index=entry_idx,
        entry_bar_time=entry_bar.close_time,
        entry_source_timestamp=entry_src,
        exit_bar_index=exit_idx_bar,
        exit_source_timestamp=exit_src,
        side=side,
        entry_mid=entry_mid,
        exit_mid=exit_mid,
        stop_level=stop,
        exit_reason=exit_reason,
        bars_held=exit_idx_bar - entry_idx,
        wall_clock_seconds=wall,
        risk_pips=risk_pips,
        gross_pips=gross_pips,
        gross_r=gross_pips / risk_pips,
        entry_cost_pips=entry_cost,
        exit_cost_pips=exit_cost,
        slippage_pips=2 * fixed_slippage_pips,
        total_cost_pips=total_cost,
        net_pips=net_pips,
        net_r=net_pips / risk_pips,
        h4_trend=h4_trend,
        h4_feature_time=h4_time,
        d1agg_regime=regime,
        d1agg_feature_time=d1_time,
        d1agg_applied=d1agg_applied,
        trigger_completion_reason=bars[i].completion_reason,
        trigger_thresholds_crossed=bars[i].thresholds_crossed,
        trigger_overshoot_pips=bars[i].overshoot_pips,
        approved=False,
    )


def _bar_index_for_time(bars: Sequence[RangeBar], t: datetime, *, lo: int, hi: int) -> int:
    """The range-bar index whose [open_time, close_time] contains ``t`` (within [lo,hi])."""
    for k in range(lo, hi + 1):
        if bars[k].open_time <= t <= bars[k].close_time:
            return k
    return hi


# --------------------------------------------------------------------------- #
# Metrics (compact summary; shared by runner + tests)
# --------------------------------------------------------------------------- #
def _max_drawdown_r(r_values: list[float]) -> float:
    """Max peak-to-trough drawdown of the cumulative per-trade R equity curve."""
    cum = 0.0
    peak = 0.0
    mdd = 0.0
    for r in r_values:
        cum += r
        peak = max(peak, cum)
        mdd = min(mdd, cum - peak)
    return mdd


def _profit_factor(pips: list[float]) -> float | None:
    gains = sum(p for p in pips if p > 0)
    losses = -sum(p for p in pips if p < 0)
    if losses == 0:
        return None if gains == 0 else float("inf")
    return gains / losses


def expectancy_at_cost_multiple(trades: Sequence[RangeBarTrade], multiple: float) -> float | None:
    """Mean per-trade net R if the per-trade cost were scaled by ``multiple``."""
    if not trades:
        return None
    rs = []
    for t in trades:
        net = t.gross_pips - multiple * t.total_cost_pips
        rs.append(net / t.risk_pips)
    return sum(rs) / len(rs)


def summarize_trades(trades: Sequence[RangeBarTrade], *, label: str) -> dict:
    """Compact, JSON-serialisable metrics block for a set of trades."""
    n = len(trades)
    base = {
        "label": label,
        "trades": n,
        "approved": False,
        "evidence_use": "approval_bound",
    }
    if n == 0:
        return {**base, "note": "no trades"}
    net_pips = [t.net_pips for t in trades]
    net_r = [t.net_r for t in trades]
    gross_pips = [t.gross_pips for t in trades]
    gross_r = [t.gross_r for t in trades]
    wins = [t for t in trades if t.net_pips > 0]
    exit_dist: dict[str, int] = {}
    for t in trades:
        exit_dist[t.exit_reason] = exit_dist.get(t.exit_reason, 0) + 1
    longs = sum(1 for t in trades if t.side == "long")
    pf = _profit_factor(net_pips)
    pf_out = round(pf, 4) if isinstance(pf, float) and math.isfinite(pf) else pf
    return {
        **base,
        "gross_pips_total": round(sum(gross_pips), 3),
        "gross_r_total": round(sum(gross_r), 4),
        "net_pips_total": round(sum(net_pips), 3),
        "net_r_total": round(sum(net_r), 4),
        "expectancy_r": round(sum(net_r) / n, 6),
        "gross_expectancy_r": round(sum(gross_r) / n, 6),
        "profit_factor_net_pips": pf_out,
        "max_drawdown_r": round(_max_drawdown_r(net_r), 4),
        "hit_rate": round(len(wins) / n, 4),
        "avg_hold_range_bars": round(sum(t.bars_held for t in trades) / n, 3),
        "avg_hold_wall_clock_sec": round(sum(t.wall_clock_seconds for t in trades) / n, 1),
        "exit_reason_distribution": exit_dist,
        "long_short_split": {"long": longs, "short": n - longs},
        "expectancy_r_cost_2x": round(expectancy_at_cost_multiple(trades, 2.0), 6),
        "avg_total_cost_pips": round(sum(t.total_cost_pips for t in trades) / n, 4),
        "avg_risk_pips": round(sum(t.risk_pips for t in trades) / n, 4),
    }
