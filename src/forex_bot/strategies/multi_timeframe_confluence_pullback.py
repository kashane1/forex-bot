"""MTF confluence pullback — ``multi_timeframe_confluence_pullback 0.1.0-c020``.

CAMPAIGN_020 research candidate scaffold only. **NOT approved** for paper,
demo, or live. See ``docs/research/CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md``.

Hypothesis: trade H4 pullback continuations only when D1AGG trend structure,
H4 trend context, and local EMA20 re-acceptance align. Uses shared
``d1agg_htf`` + ``htf_align``; approval-bound evidence must use
``next_bar_open`` (engine fill model, not signal-bar close entry).

No broker / executor imports. Emits ``Signal`` only.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Literal

import pandas as pd

from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
from forex_bot.domain.candles import Candle
from forex_bot.domain.signals import Signal
from forex_bot.features.htf_align import HTF_UNAVAILABLE, align_last_completed
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import adx, atr, ema, rsi

D1Trend = Literal["bullish", "bearish", "neutral"]


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        if isinstance(value, float) and not math.isfinite(value):
            return None
    except TypeError:
        return None
    return Decimal(str(value))


def _mid(bid: Decimal | None, ask: Decimal | None) -> float:
    if bid is None or ask is None:
        return float("nan")
    return float((bid + ask) / 2)


def _df_to_completed_h4_candle_list(
    df: pd.DataFrame, instrument: str
) -> list[Candle]:
    candles: list[Candle] = []
    for ts, row in df.iterrows():
        bar_time: datetime = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
        candles.append(
            Candle(
                instrument=instrument,
                granularity="H4",
                time=bar_time,
                complete=True,
                volume=int(row.get("volume", 0) or 0),
                bid_o=_to_decimal(row.get("bid_open")),
                bid_h=_to_decimal(row.get("bid_high")),
                bid_l=_to_decimal(row.get("bid_low")),
                bid_c=_to_decimal(row.get("bid_close")),
                ask_o=_to_decimal(row.get("ask_open")),
                ask_h=_to_decimal(row.get("ask_high")),
                ask_l=_to_decimal(row.get("ask_low")),
                ask_c=_to_decimal(row.get("ask_close")),
            )
        )
    return candles


def d1agg_trend_htf_frame(
    d1_candles: list[Candle],
    *,
    ema_fast_len: int,
    ema_slow_len: int,
) -> pd.DataFrame:
    """D1AGG mid close + EMAs for ``htf_align`` (completed bars only)."""
    closes = [_mid(c.bid_c, c.ask_c) for c in d1_candles]
    close_series = pd.Series(closes, dtype=float)
    ema_fast = ema(close_series, ema_fast_len)
    ema_slow = ema(close_series, ema_slow_len)
    rows: list[dict[str, Any]] = []
    for i, candle in enumerate(d1_candles):
        rows.append(
            {
                "time": candle.time,
                "complete": True,
                "close": closes[i],
                "ema_fast": float(ema_fast.iloc[i]),
                "ema_slow": float(ema_slow.iloc[i]),
            }
        )
    return pd.DataFrame(rows)


def classify_d1_trend(
    d1_close: float,
    d1_ema_fast: float,
    d1_ema_slow: float,
) -> D1Trend:
    if not all(math.isfinite(v) for v in (d1_close, d1_ema_fast, d1_ema_slow)):
        return "neutral"
    if d1_close > d1_ema_slow and d1_ema_fast > d1_ema_slow:
        return "bullish"
    if d1_close < d1_ema_slow and d1_ema_fast < d1_ema_slow:
        return "bearish"
    return "neutral"


def aligned_d1_trend_at_decision(
    h4_candles: list[Candle],
    decision_time: datetime,
    *,
    instrument: str,
    ema_fast_len: int,
    ema_slow_len: int,
) -> tuple[D1Trend, datetime | None, str | None]:
    try:
        agg = aggregate_h4_to_d1(h4_candles, instrument=instrument)
    except ValueError:
        return "neutral", None, HTF_UNAVAILABLE
    d1_candles = agg.candles
    if len(d1_candles) < ema_slow_len + 2:
        return "neutral", None, HTF_UNAVAILABLE
    htf = d1agg_trend_htf_frame(
        d1_candles, ema_fast_len=ema_fast_len, ema_slow_len=ema_slow_len
    )
    decisions = pd.DatetimeIndex([decision_time])
    aligned = align_last_completed(
        decisions, htf, ["close", "ema_fast", "ema_slow"], prefix="d1agg"
    )
    reason = aligned["d1agg_blocked_reason"].iloc[0]
    if reason:
        return "neutral", None, reason
    d1_close = float(aligned["d1agg_close"].iloc[0])
    d1_ef = float(aligned["d1agg_ema_fast"].iloc[0])
    d1_es = float(aligned["d1agg_ema_slow"].iloc[0])
    d1_time = aligned["d1agg_close_time"].iloc[0]
    ts = pd.Timestamp(d1_time).to_pydatetime() if pd.notna(d1_time) else None
    return classify_d1_trend(d1_close, d1_ef, d1_es), ts, None


def h4_pullback_and_trigger(
    *,
    side: Literal["long", "short"],
    close: pd.Series,
    low: pd.Series,
    high: pd.Series,
    ema_pullback: pd.Series,
    rsi_series: pd.Series,
    atr_series: pd.Series,
    pullback_lookback: int,
    pullback_band_atr: float,
    rsi_pullback_long: float,
    rsi_pullback_short: float,
) -> tuple[bool, bool, str]:
    """Return (had_pullback, trigger_fired, debug_reason)."""
    if len(close) < pullback_lookback + 2:
        return False, False, "insufficient_bars"
    win_low = low.iloc[-(pullback_lookback + 1) : -1]
    win_high = high.iloc[-(pullback_lookback + 1) : -1]
    win_ema = ema_pullback.iloc[-(pullback_lookback + 1) : -1]
    win_rsi = rsi_series.iloc[-(pullback_lookback + 1) : -1]
    last_atr = float(atr_series.iloc[-1])
    band = pullback_band_atr * last_atr if math.isfinite(last_atr) else float("nan")

    last_close = float(close.iloc[-1])
    prev_close = float(close.iloc[-2])
    last_ema = float(ema_pullback.iloc[-1])
    prev_ema = float(ema_pullback.iloc[-2])

    if side == "long":
        touched = bool((win_low <= (win_ema + band)).any()) if math.isfinite(band) else False
        rsi_pull = bool((win_rsi <= rsi_pullback_long).any())
        had_pullback = touched or rsi_pull
        trigger = last_close > last_ema and prev_close <= prev_ema
        reason = f"pullback={had_pullback}(touch={touched},rsi={rsi_pull}),reclaim={trigger}"
        return had_pullback, trigger, reason
    touched = bool((win_high >= (win_ema - band)).any()) if math.isfinite(band) else False
    rsi_pull = bool((win_rsi >= rsi_pullback_short).any())
    had_pullback = touched or rsi_pull
    trigger = last_close < last_ema and prev_close >= prev_ema
    reason = f"pullback={had_pullback}(touch={touched},rsi={rsi_pull}),reclaim={trigger}"
    return had_pullback, trigger, reason


class MultiTimeframeConfluencePullbackStrategy:
    """CAMPAIGN_020 — MTF confluence pullback (scaffold only)."""

    name: str = "multi_timeframe_confluence_pullback"

    def __init__(self, version: str = "0.1.0-c020") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 520

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        d1_ema_fast = int(cfg.get("d1_ema_fast", 20))
        d1_ema_slow = int(cfg.get("d1_ema_slow", 50))
        h4_ema_context = int(cfg.get("h4_ema_context", 50))
        h4_ema_pullback = int(cfg.get("h4_ema_pullback", 20))
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        pullback_lookback = int(cfg.get("pullback_lookback", 6))
        pullback_band_atr = float(cfg.get("pullback_band_atr", 0.5))
        rsi_len = int(cfg.get("rsi_lookback", 14))
        rsi_pullback_long = float(cfg.get("rsi_pullback_long", 40.0))
        rsi_pullback_short = float(cfg.get("rsi_pullback_short", 60.0))
        adx_len = int(cfg.get("adx_lookback", 14))
        adx_min = float(cfg.get("adx_min", 18.0))
        timeframe = cfg.get("timeframe", "H4")
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        needed = max(
            self.warmup_bars_required(),
            h4_ema_context,
            h4_ema_pullback,
            atr_len,
            pullback_lookback,
            rsi_len,
            adx_len,
        ) + 3
        if len(df) < needed:
            return None

        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        close = df["close"]
        high = df["high"]
        low = df["low"]
        h4_ema_ctx = ema(close, h4_ema_context)
        h4_ema_pb = ema(close, h4_ema_pullback)
        atr_series = atr(high, low, close, atr_len)
        rsi_series = rsi(close, rsi_len, warmup_policy="nan")
        adx_series = adx(high, low, close, adx_len)

        last_close = float(close.iloc[-1])
        last_ctx = float(h4_ema_ctx.iloc[-1])
        prior_atr = float(atr_series.iloc[-2])
        last_adx = float(adx_series.iloc[-1])

        if not all(
            math.isfinite(v) for v in (last_close, last_ctx, prior_atr, last_adx)
        ):
            return None
        if last_adx < adx_min:
            return None

        pip_size = float(ctx.instrument.pip_size)
        atr_pips = prior_atr / pip_size if pip_size else 0.0
        if atr_pips < min_atr_pips:
            return None

        idx_t = df.index[-1]
        decision_dt = pd.Timestamp(idx_t).tz_convert(UTC).to_pydatetime()
        h4_candles = _df_to_completed_h4_candle_list(df, ctx.instrument.name)
        d1_trend, d1_time, htf_block = aligned_d1_trend_at_decision(
            h4_candles,
            decision_dt,
            instrument=ctx.instrument.name,
            ema_fast_len=d1_ema_fast,
            ema_slow_len=d1_ema_slow,
        )
        if htf_block or d1_trend == "neutral":
            return None

        side: Literal["long", "short"] | None = None
        gate_reason = ""
        if d1_trend == "bullish" and last_close > last_ctx:
            had_pb, trig, gate_reason = h4_pullback_and_trigger(
                side="long",
                close=close,
                low=low,
                high=high,
                ema_pullback=h4_ema_pb,
                rsi_series=rsi_series,
                atr_series=atr_series,
                pullback_lookback=pullback_lookback,
                pullback_band_atr=pullback_band_atr,
                rsi_pullback_long=rsi_pullback_long,
                rsi_pullback_short=rsi_pullback_short,
            )
            if had_pb and trig:
                side = "long"
        elif d1_trend == "bearish" and last_close < last_ctx:
            had_pb, trig, gate_reason = h4_pullback_and_trigger(
                side="short",
                close=close,
                low=low,
                high=high,
                ema_pullback=h4_ema_pb,
                rsi_series=rsi_series,
                atr_series=atr_series,
                pullback_lookback=pullback_lookback,
                pullback_band_atr=pullback_band_atr,
                rsi_pullback_long=rsi_pullback_long,
                rsi_pullback_short=rsi_pullback_short,
            )
            if had_pb and trig:
                side = "short"

        if side is None:
            return None

        if side == "long":
            stop = last_close - atr_multiple * prior_atr
        else:
            stop = last_close + atr_multiple * prior_atr

        htf_times: dict[str, datetime] = {}
        if d1_time is not None:
            htf_times["d1agg_trend"] = d1_time

        bar_timestamp_iso = pd.Timestamp(idx_t).tz_convert(UTC).isoformat()
        signal_id = _stable_signal_id(
            self.name,
            self.version,
            ctx.instrument.name,
            timeframe,
            bar_timestamp_iso,
            side,
        )

        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=timeframe,
            timestamp=decision_dt,
            side=side,
            entry_intent="market",
            stop_model=f"ATR{atr_len}*{atr_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="hard_stop_or_time",
            campaign_id="CAMPAIGN_020",
            decision_time=decision_dt,
            available_data_cutoff=decision_dt,
            source_candle_timestamp=decision_dt,
            htf_feature_times=htf_times or None,
            features={
                "d1_trend": d1_trend,
                "d1agg_htf_time": d1_time.isoformat() if d1_time else None,
                "h4_ema_context": last_ctx,
                "h4_ema_pullback": float(h4_ema_pb.iloc[-1]),
                "adx": last_adx,
                "prior_atr_h4": prior_atr,
                "gate_reason": gate_reason,
            },
            reason=(
                f"MTF confluence {side}: D1={d1_trend}, H4 ctx OK, "
                f"pullback+EMA{h4_ema_pullback} reclaim ({gate_reason})"
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]
