"""LTF MTF confluence entry — ``lower_timeframe_mtf_confluence_entry 0.1.0-c021``.

CAMPAIGN_021 scaffold only. **NOT approved** for paper, demo, or live.
See ``docs/research/CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md``.

M15 execution with H1/H4/D1AGG context via ``align_last_completed``.
D1AGG must use ``native_h4_derived_d1agg`` provenance; M1-derived D1AGG is rejected.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Literal

import pandas as pd

from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.signals import Signal
from forex_bot.features.htf_align import HTF_UNAVAILABLE, align_last_completed
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import adx, atr, ema
from forex_bot.strategies.multi_timeframe_confluence_pullback import (
    classify_d1_trend,
    d1agg_trend_htf_frame,
)

D1Trend = Literal["bullish", "bearish", "neutral"]
D1AGG_SOURCE_NATIVE = "native_h4_derived_d1agg"
D1AGG_SOURCE_M1 = "m1_derived_d1agg"
EXECUTION_TIMEFRAME = "M15"


def validate_c021_data_provenance(provenance: dict[str, Any] | None) -> None:
    """Reject ambiguous or forbidden D1AGG sources for CAMPAIGN_021."""
    if not provenance:
        raise ValueError("BLOCKED_PROVENANCE_AMBIGUITY: data_provenance missing")
    d1_src = provenance.get("d1agg_context") or provenance.get("d1agg_source")
    if d1_src == D1AGG_SOURCE_M1:
        raise ValueError("CAMPAIGN_021 rejects m1_derived_d1agg")
    if d1_src != D1AGG_SOURCE_NATIVE:
        raise ValueError(
            f"CAMPAIGN_021 requires d1agg_context={D1AGG_SOURCE_NATIVE!r}, got {d1_src!r}"
        )
    for key in ("execution_m15", "context_h1", "context_h4"):
        if provenance.get(key) != "m1_derived":
            raise ValueError(f"CAMPAIGN_021 requires {key}=m1_derived")


def _require_context_frames(cfg: dict[str, Any]) -> dict[str, CandleFrame]:
    raw = cfg.get("context_frames")
    if not isinstance(raw, dict):
        raise ValueError("context_frames required in strategy config")
    for name in ("H1", "H4", "D1AGG"):
        if name not in raw or not isinstance(raw[name], CandleFrame):
            raise ValueError(f"missing context frame: {name}")
    return raw


def _htf_frame_from_candles(candles: list[Candle], *, value_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for candle in candles:
        row: dict[str, Any] = {
            "time": candle.time,
            "complete": bool(candle.complete),
        }
        mid_c = candle.mid_c if candle.mid_c is not None else (
            (candle.bid_c + candle.ask_c) / 2
            if candle.bid_c is not None and candle.ask_c is not None
            else None
        )
        if mid_c is not None:
            row["close"] = float(mid_c)
        rows.append(row)
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    close = pd.Series([r.get("close") for r in rows], dtype=float)
    if "ema20" in value_cols or "ema50" in value_cols:
        frame["ema20"] = ema(close, 20)
    if "ema50" in value_cols:
        frame["ema50"] = ema(close, 50)
    return frame


def _frame_rows_to_candles(frame: CandleFrame, granularity: str) -> list[Candle]:
    out: list[Candle] = []
    for ts, row in frame.completed_only().df.iterrows():
        out.append(
            Candle(
                instrument=frame.instrument,
                granularity=granularity,
                time=ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts,
                complete=True,
                volume=int(row.get("volume", 0) or 0),
                bid_o=row.get("bid_open"),
                bid_h=row.get("bid_high"),
                bid_l=row.get("bid_low"),
                bid_c=row.get("bid_close"),
                ask_o=row.get("ask_open"),
                ask_h=row.get("ask_high"),
                ask_l=row.get("ask_low"),
                ask_c=row.get("ask_close"),
            )
        )
    return out


def _aligned_h1_trend(
    h1_frame: CandleFrame,
    decision_time: datetime,
    *,
    slope_bars: int,
) -> tuple[D1Trend, datetime | None, str | None]:
    h1_candles_list = _frame_rows_to_candles(h1_frame, "H1")
    htf = _htf_frame_from_candles(h1_candles_list, value_cols=["ema20"])
    if len(htf) < slope_bars + 2:
        return "neutral", None, HTF_UNAVAILABLE
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_time]),
        htf,
        ["close", "ema20"],
        prefix="h1",
    )
    reason = aligned["h1_blocked_reason"].iloc[0] if "h1_blocked_reason" in aligned else None
    if reason:
        return "neutral", None, reason
    close = float(aligned["h1_close"].iloc[0])
    ema20 = float(aligned["h1_ema20"].iloc[0])
    ema20_time = aligned["h1_close_time"].iloc[0]
    # Slope must be anchored at the aligned (last completed) H1 bar, never the
    # tail of the full frame — the frame may carry bars after decision_time.
    aligned_time = pd.Timestamp(ema20_time)
    if pd.isna(aligned_time):
        return "neutral", None, HTF_UNAVAILABLE
    if aligned_time.tzinfo is None:
        aligned_time = aligned_time.tz_localize("UTC")
    htf_times = pd.to_datetime(htf["time"], utc=True)
    ema_series = htf.loc[htf_times <= aligned_time, "ema20"].dropna()
    if len(ema_series) < slope_bars + 1:
        return "neutral", None, HTF_UNAVAILABLE
    slope = float(ema_series.iloc[-1] - ema_series.iloc[-(slope_bars + 1)])
    ts = aligned_time.to_pydatetime()
    if close > ema20 and slope >= 0:
        return "bullish", ts, None
    if close < ema20 and slope <= 0:
        return "bearish", ts, None
    return "neutral", ts, None


def _aligned_h4_trend(
    h4_frame: CandleFrame,
    decision_time: datetime,
    *,
    ema_len: int,
) -> tuple[D1Trend, datetime | None, str | None]:
    h4_candles_list = _frame_rows_to_candles(h4_frame, "H4")
    htf = _htf_frame_from_candles(h4_candles_list, value_cols=["ema50", "close"])
    if len(htf) < ema_len + 2:
        return "neutral", None, HTF_UNAVAILABLE
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_time]),
        htf,
        ["close", "ema50"],
        prefix="h4",
    )
    reason = aligned.get("h4_blocked_reason", pd.Series([None])).iloc[0]
    if reason:
        return "neutral", None, reason
    close = float(aligned["h4_close"].iloc[0])
    ema50 = float(aligned["h4_ema50"].iloc[0])
    feat_time = aligned["h4_close_time"].iloc[0]
    ts = pd.Timestamp(feat_time).to_pydatetime() if pd.notna(feat_time) else None
    if close > ema50:
        return "bullish", ts, None
    if close < ema50:
        return "bearish", ts, None
    return "neutral", ts, None


def _aligned_d1agg_trend(
    d1agg_frame: CandleFrame,
    decision_time: datetime,
    *,
    ema_fast_len: int,
    ema_slow_len: int,
) -> tuple[D1Trend, datetime | None, str | None]:
    d1_candles = _frame_rows_to_candles(d1agg_frame, "D1AGG")
    if len(d1_candles) < ema_slow_len + 2:
        return "neutral", None, HTF_UNAVAILABLE
    htf = d1agg_trend_htf_frame(d1_candles, ema_fast_len=ema_fast_len, ema_slow_len=ema_slow_len)
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_time]),
        htf,
        ["close", "ema_fast", "ema_slow"],
        prefix="d1agg",
    )
    reason = aligned.get("d1agg_blocked_reason", pd.Series([None])).iloc[0]
    if reason:
        return "neutral", None, reason
    d1_close = float(aligned["d1agg_close"].iloc[0])
    d1_ef = float(aligned["d1agg_ema_fast"].iloc[0])
    d1_es = float(aligned["d1agg_ema_slow"].iloc[0])
    feat_time = aligned["d1agg_close_time"].iloc[0]
    ts = pd.Timestamp(feat_time).to_pydatetime() if pd.notna(feat_time) else None
    return classify_d1_trend(d1_close, d1_ef, d1_es), ts, None


def m15_pullback_and_reclaim(
    *,
    side: Literal["long", "short"],
    close: pd.Series,
    low: pd.Series,
    high: pd.Series,
    ema20: pd.Series,
    ema50: pd.Series,
    pullback_lookback: int,
) -> tuple[bool, bool, str]:
    if len(close) < pullback_lookback + 2:
        return False, False, "insufficient_m15_bars"
    win_low = low.iloc[-(pullback_lookback + 1) : -1]
    win_high = high.iloc[-(pullback_lookback + 1) : -1]
    win_ema20 = ema20.iloc[-(pullback_lookback + 1) : -1]
    win_ema50 = ema50.iloc[-(pullback_lookback + 1) : -1]
    last_close = float(close.iloc[-1])
    prev_close = float(close.iloc[-2])
    last_ema20 = float(ema20.iloc[-1])
    prev_ema20 = float(ema20.iloc[-2])
    if side == "long":
        touched = bool((win_low <= win_ema20).any() or (win_low <= win_ema50).any())
        reclaim = last_close > last_ema20 and prev_close <= prev_ema20
        return touched, reclaim, f"touch={touched},reclaim={reclaim}"
    touched = bool((win_high >= win_ema20).any() or (win_high >= win_ema50).any())
    reclaim = last_close < last_ema20 and prev_close >= prev_ema20
    return touched, reclaim, f"touch={touched},reclaim={reclaim}"


class LowerTimeframeMtfConfluenceEntryStrategy:
    """CAMPAIGN_021 — LTF MTF confluence entry (scaffold only)."""

    name: str = "lower_timeframe_mtf_confluence_entry"

    def __init__(self, version: str = "0.1.0-c021") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 120

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        validate_c021_data_provenance(ctx.config.get("data_provenance"))
        if ctx.candles.granularity != EXECUTION_TIMEFRAME:
            raise ValueError(
                f"execution frame must be {EXECUTION_TIMEFRAME}, got {ctx.candles.granularity}"
            )
        context_frames = _require_context_frames(ctx.config)
        cfg = ctx.config
        d1_ema_fast = int(cfg.get("d1_ema_fast", 20))
        d1_ema_slow = int(cfg.get("d1_ema_slow", 50))
        h4_ema = int(cfg.get("h4_ema_context", 50))
        h1_slope_bars = int(cfg.get("h1_ema_slope_bars", 3))
        m15_pullback_lookback = int(cfg.get("m15_pullback_lookback", 8))
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_multiple = float(cfg.get("atr_stop_multiple", 2.0))
        adx_len = int(cfg.get("adx_lookback", 14))
        adx_min = float(cfg.get("adx_min", 18.0))
        max_bars = int(cfg.get("max_bars_in_trade", 32))
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        df = ctx.candles.completed_only().df
        needed = max(
            self.warmup_bars_required(),
            50,
            atr_len,
            adx_len,
            m15_pullback_lookback,
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
        m15_ema20 = ema(close, 20)
        m15_ema50 = ema(close, 50)
        atr_series = atr(high, low, close, atr_len)
        adx_series = adx(high, low, close, adx_len)

        prior_atr = float(atr_series.iloc[-2])
        last_adx = float(adx_series.iloc[-1])
        last_close = float(close.iloc[-1])
        if not all(math.isfinite(v) for v in (prior_atr, last_adx, last_close)):
            return None
        if last_adx < adx_min:
            return None
        pip_size = float(ctx.instrument.pip_size)
        if pip_size and prior_atr / pip_size < min_atr_pips:
            return None

        idx_t = df.index[-1]
        decision_dt = pd.Timestamp(idx_t).tz_convert(UTC).to_pydatetime()

        d1_trend, d1_time, d1_block = _aligned_d1agg_trend(
            context_frames["D1AGG"],
            decision_dt,
            ema_fast_len=d1_ema_fast,
            ema_slow_len=d1_ema_slow,
        )
        h4_trend, h4_time, h4_block = _aligned_h4_trend(
            context_frames["H4"],
            decision_dt,
            ema_len=h4_ema,
        )
        h1_trend, h1_time, h1_block = _aligned_h1_trend(
            context_frames["H1"],
            decision_dt,
            slope_bars=h1_slope_bars,
        )
        if d1_block or h4_block or h1_block:
            return None
        if d1_trend == "neutral" or h4_trend == "neutral" or h1_trend == "neutral":
            return None

        side: Literal["long", "short"] | None = None
        gate_reason = ""
        if d1_trend == "bullish" and h4_trend == "bullish" and h1_trend == "bullish":
            had_pb, trig, gate_reason = m15_pullback_and_reclaim(
                side="long",
                close=close,
                low=low,
                high=high,
                ema20=m15_ema20,
                ema50=m15_ema50,
                pullback_lookback=m15_pullback_lookback,
            )
            if had_pb and trig:
                side = "long"
        elif d1_trend == "bearish" and h4_trend == "bearish" and h1_trend == "bearish":
            had_pb, trig, gate_reason = m15_pullback_and_reclaim(
                side="short",
                close=close,
                low=low,
                high=high,
                ema20=m15_ema20,
                ema50=m15_ema50,
                pullback_lookback=m15_pullback_lookback,
            )
            if had_pb and trig:
                side = "short"

        if side is None:
            return None

        stop = (
            last_close - atr_multiple * prior_atr
            if side == "long"
            else last_close + atr_multiple * prior_atr
        )

        htf_times: dict[str, datetime] = {}
        if d1_time is not None:
            htf_times["d1agg"] = d1_time
        if h4_time is not None:
            htf_times["h4"] = h4_time
        if h1_time is not None:
            htf_times["h1"] = h1_time

        bar_timestamp_iso = pd.Timestamp(idx_t).tz_convert(UTC).isoformat()
        signal_id = _stable_signal_id(
            self.name,
            self.version,
            ctx.instrument.name,
            EXECUTION_TIMEFRAME,
            bar_timestamp_iso,
            side,
        )
        provenance = ctx.config.get("data_provenance") or {}

        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=EXECUTION_TIMEFRAME,
            timestamp=decision_dt,
            side=side,
            entry_intent="market",
            stop_model=f"M15_ATR{atr_len}*{atr_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="hard_stop_or_time",
            campaign_id="CAMPAIGN_021",
            decision_time=decision_dt,
            available_data_cutoff=decision_dt,
            source_candle_timestamp=decision_dt,
            htf_feature_times=htf_times or None,
            features={
                "d1_trend": d1_trend,
                "h4_trend": h4_trend,
                "h1_trend": h1_trend,
                "gate_reason": gate_reason,
                "max_bars_in_trade": max_bars,
                "data_provenance": dict(provenance),
                "d1agg_source": provenance.get("d1agg_context"),
            },
            reason=(
                f"LTF MTF {side}: D1/H4/H1 aligned, M15 pullback+EMA20 reclaim ({gate_reason})"
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]
