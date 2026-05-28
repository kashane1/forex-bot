"""H4/H1 pullback resolution entry — ``h4_h1_pullback_resolution_entry 0.1.0-c022``.

CAMPAIGN_022 scaffold only. **NOT approved** for paper, demo, or live.
See ``docs/research/CAMPAIGN_022_H4_H1_PULLBACK_RESOLUTION_PRECOMMIT.md``.

Thesis (vs C020/C021 "all-green" alignment): H4 sets directional bias, H1 must be
in a *counter-trend pullback that still holds*, and M15 fires only when that pullback
*resolves back* into the H4 direction. H1 is NOT required to agree with H4.

Top timeframe is H4 — there is no D1 / D1AGG layer. All H4/H1 features are read at the
``align_last_completed`` bar for the decision time; slope and pullback windows are bounded
to bars with ``time <= aligned_feature_time`` (no tail-of-frame lookahead).

No broker / executor imports. Emits ``Signal`` only.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Literal

import pandas as pd

from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.signals import Signal
from forex_bot.features.htf_align import align_last_completed
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import adx, atr, ema, rsi
from forex_bot.strategies.lower_timeframe_mtf_confluence_entry import (
    m15_pullback_and_reclaim,
)

Bias = Literal["bullish", "bearish", "neutral"]
EXECUTION_TIMEFRAME = "M15"
HTF_UNAVAILABLE = "HTF_UNAVAILABLE"


def validate_c022_data_provenance(provenance: dict[str, Any] | None) -> None:
    """Require three m1_derived layers and reject any daily-layer keys."""
    if not provenance:
        raise ValueError("BLOCKED_PROVENANCE_AMBIGUITY: data_provenance missing")
    for forbidden in ("d1agg_context", "d1agg_source", "d1_context", "d1_source"):
        if provenance.get(forbidden) is not None:
            raise ValueError(
                f"CAMPAIGN_022 has no daily layer; unexpected {forbidden!r}"
            )
    for key in ("execution_m15", "context_h1", "context_h4"):
        if provenance.get(key) != "m1_derived":
            raise ValueError(f"CAMPAIGN_022 requires {key}=m1_derived")


def _require_context_frames(cfg: dict[str, Any]) -> dict[str, CandleFrame]:
    raw = cfg.get("context_frames")
    if not isinstance(raw, dict):
        raise ValueError("context_frames required in strategy config")
    for name in ("H1", "H4"):
        if name not in raw or not isinstance(raw[name], CandleFrame):
            raise ValueError(f"missing context frame: {name}")
    return raw


def _htf_indicator_frame(
    frame: CandleFrame,
    *,
    ema_fast_len: int,
    ema_slow_len: int,
    adx_len: int | None = None,
    rsi_len: int | None = None,
) -> pd.DataFrame:
    """Completed-bar HTF frame with precomputed indicators for ``align_last_completed``."""
    df = frame.completed_only().df
    if df.empty:
        return pd.DataFrame()
    close = pd.Series(df["close"].to_numpy(dtype=float))
    high = pd.Series(df["high"].to_numpy(dtype=float))
    low = pd.Series(df["low"].to_numpy(dtype=float))
    out = pd.DataFrame(
        {
            "time": pd.to_datetime(df.index, utc=True).to_numpy(),
            "complete": True,
            "close": close.to_numpy(),
            "high": high.to_numpy(),
            "low": low.to_numpy(),
            "ema_fast": ema(close, ema_fast_len).to_numpy(),
            "ema_slow": ema(close, ema_slow_len).to_numpy(),
        }
    )
    if adx_len is not None:
        out["adx"] = adx(high, low, close, adx_len).to_numpy()
    if rsi_len is not None:
        out["rsi"] = rsi(close, rsi_len, warmup_policy="nan").to_numpy()
    return out


def _aligned_feature_time(aligned: pd.DataFrame, prefix: str) -> pd.Timestamp | None:
    raw = aligned[f"{prefix}_close_time"].iloc[0]
    ts = pd.Timestamp(raw)
    if pd.isna(ts):
        return None
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def aligned_h4_bias(
    h4_frame: CandleFrame,
    decision_time: datetime,
    *,
    ema_fast_len: int,
    ema_slow_len: int,
    slope_bars: int,
    adx_len: int,
    adx_min: float,
) -> tuple[Bias, datetime | None, str | None]:
    """H4 directional bias: >=2 of 3 votes (price>EMA50, EMA20>EMA50, EMA50 slope) gated by ADX."""
    htf = _htf_indicator_frame(
        h4_frame, ema_fast_len=ema_fast_len, ema_slow_len=ema_slow_len, adx_len=adx_len
    )
    if len(htf) < max(ema_slow_len, adx_len) + slope_bars + 2:
        return "neutral", None, HTF_UNAVAILABLE
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_time]),
        htf,
        ["close", "ema_fast", "ema_slow", "adx"],
        prefix="h4",
    )
    reason = aligned["h4_blocked_reason"].iloc[0]
    if reason:
        return "neutral", None, reason
    feat_time = _aligned_feature_time(aligned, "h4")
    if feat_time is None:
        return "neutral", None, HTF_UNAVAILABLE
    ts = feat_time.to_pydatetime()

    close = float(aligned["h4_close"].iloc[0])
    ema_fast = float(aligned["h4_ema_fast"].iloc[0])
    ema_slow = float(aligned["h4_ema_slow"].iloc[0])
    adx_val = float(aligned["h4_adx"].iloc[0])

    htf_times = pd.to_datetime(htf["time"], utc=True)
    slow_hist = htf.loc[htf_times <= feat_time, "ema_slow"].dropna()
    if len(slow_hist) < slope_bars + 1:
        return "neutral", ts, HTF_UNAVAILABLE
    slope = float(slow_hist.iloc[-1] - slow_hist.iloc[-(slope_bars + 1)])

    if not all(math.isfinite(v) for v in (close, ema_fast, ema_slow, adx_val, slope)):
        return "neutral", ts, None
    if adx_val < adx_min:
        return "neutral", ts, None

    bull_votes = (close > ema_slow) + (ema_fast > ema_slow) + (slope > 0)
    bear_votes = (close < ema_slow) + (ema_fast < ema_slow) + (slope < 0)
    if bull_votes >= 2:
        return "bullish", ts, None
    if bear_votes >= 2:
        return "bearish", ts, None
    return "neutral", ts, None


def aligned_h1_pullback_holds(
    h1_frame: CandleFrame,
    decision_time: datetime,
    side: Literal["long", "short"],
    *,
    ema_fast_len: int,
    ema_slow_len: int,
    rsi_len: int,
    lookback: int,
    rsi_pullback_long: float,
    rsi_pullback_short: float,
) -> tuple[bool, datetime | None, str | None]:
    """H1 counter-trend pullback that holds: pullback (EMA20 touch or RSI reset) AND
    latest H1 close still on the trend side of EMA50."""
    htf = _htf_indicator_frame(
        h1_frame, ema_fast_len=ema_fast_len, ema_slow_len=ema_slow_len, rsi_len=rsi_len
    )
    if len(htf) < max(ema_slow_len, rsi_len) + lookback + 2:
        return False, None, HTF_UNAVAILABLE
    aligned = align_last_completed(
        pd.DatetimeIndex([decision_time]),
        htf,
        ["close", "ema_fast", "ema_slow", "rsi"],
        prefix="h1",
    )
    reason = aligned["h1_blocked_reason"].iloc[0]
    if reason:
        return False, None, reason
    feat_time = _aligned_feature_time(aligned, "h1")
    if feat_time is None:
        return False, None, HTF_UNAVAILABLE
    ts = feat_time.to_pydatetime()

    close = float(aligned["h1_close"].iloc[0])
    ema_slow = float(aligned["h1_ema_slow"].iloc[0])
    if not all(math.isfinite(v) for v in (close, ema_slow)):
        return False, ts, None

    htf_times = pd.to_datetime(htf["time"], utc=True)
    hist = htf.loc[htf_times <= feat_time]
    if len(hist) < lookback + 1:
        return False, ts, HTF_UNAVAILABLE
    win = hist.iloc[-lookback:]

    if side == "long":
        touched = bool((win["low"] <= win["ema_fast"]).any())
        rsi_reset = bool((win["rsi"] <= rsi_pullback_long).any())
        holds = close >= ema_slow
        return (touched or rsi_reset) and holds, ts, None
    touched = bool((win["high"] >= win["ema_fast"]).any())
    rsi_reset = bool((win["rsi"] >= rsi_pullback_short).any())
    holds = close <= ema_slow
    return (touched or rsi_reset) and holds, ts, None


class H4H1PullbackResolutionEntryStrategy:
    """H4/H1 pullback resolution entry (scaffold only).

    Shared by CAMPAIGN_022 (default, ``0.1.0-c022``, H4 ADX gate 20) and its
    pre-registered ADX22 sibling CAMPAIGN_023 (``0.1.0-c023``, H4 ADX gate 22).
    ``version`` / ``campaign_id`` and the H4 ADX threshold are supplied per campaign
    via constructor + config, so the two campaigns share one logic path with no fork.
    """

    name: str = "h4_h1_pullback_resolution_entry"

    def __init__(
        self, version: str = "0.1.0-c022", campaign_id: str = "CAMPAIGN_022"
    ) -> None:
        self.version = version
        self.campaign_id = campaign_id

    def warmup_bars_required(self) -> int:
        return 120

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        validate_c022_data_provenance(ctx.config.get("data_provenance"))
        if ctx.candles.granularity != EXECUTION_TIMEFRAME:
            raise ValueError(
                f"execution frame must be {EXECUTION_TIMEFRAME}, got {ctx.candles.granularity}"
            )
        context_frames = _require_context_frames(ctx.config)
        cfg = ctx.config
        h4_ema_fast = int(cfg.get("h4_ema_fast", 20))
        h4_ema_slow = int(cfg.get("h4_ema_slow", 50))
        h4_slope_bars = int(cfg.get("h4_ema_slope_bars", 3))
        h4_adx_len = int(cfg.get("h4_adx_lookback", 14))
        h4_adx_min = float(cfg.get("h4_adx_min", 20.0))
        h1_ema_fast = int(cfg.get("h1_ema_fast", 20))
        h1_ema_slow = int(cfg.get("h1_ema_slow", 50))
        h1_rsi_len = int(cfg.get("h1_rsi_lookback", 14))
        h1_pullback_lookback = int(cfg.get("h1_pullback_lookback", 6))
        h1_rsi_long = float(cfg.get("h1_rsi_pullback_long", 45.0))
        h1_rsi_short = float(cfg.get("h1_rsi_pullback_short", 55.0))
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
            self.warmup_bars_required(), 50, atr_len, adx_len, m15_pullback_lookback
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

        h4_bias, h4_time, h4_block = aligned_h4_bias(
            context_frames["H4"],
            decision_dt,
            ema_fast_len=h4_ema_fast,
            ema_slow_len=h4_ema_slow,
            slope_bars=h4_slope_bars,
            adx_len=h4_adx_len,
            adx_min=h4_adx_min,
        )
        if h4_block or h4_bias == "neutral":
            return None

        side: Literal["long", "short"] = "long" if h4_bias == "bullish" else "short"

        h1_holds, h1_time, h1_block = aligned_h1_pullback_holds(
            context_frames["H1"],
            decision_dt,
            side,
            ema_fast_len=h1_ema_fast,
            ema_slow_len=h1_ema_slow,
            rsi_len=h1_rsi_len,
            lookback=h1_pullback_lookback,
            rsi_pullback_long=h1_rsi_long,
            rsi_pullback_short=h1_rsi_short,
        )
        if h1_block or not h1_holds:
            return None

        had_pb, trig, gate_reason = m15_pullback_and_reclaim(
            side=side,
            close=close,
            low=low,
            high=high,
            ema20=m15_ema20,
            ema50=m15_ema50,
            pullback_lookback=m15_pullback_lookback,
        )
        if not (had_pb and trig):
            return None

        stop = (
            last_close - atr_multiple * prior_atr
            if side == "long"
            else last_close + atr_multiple * prior_atr
        )

        htf_times: dict[str, datetime] = {}
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
            campaign_id=self.campaign_id,
            decision_time=decision_dt,
            available_data_cutoff=decision_dt,
            source_candle_timestamp=decision_dt,
            htf_feature_times=htf_times or None,
            features={
                "h4_bias": h4_bias,
                "h1_pullback_holds": h1_holds,
                "gate_reason": gate_reason,
                "max_bars_in_trade": max_bars,
                "data_provenance": dict(provenance),
            },
            reason=(
                f"H4/H1 pullback resolution {side}: H4 bias {h4_bias}, "
                f"H1 holding pullback, M15 reclaim ({gate_reason})"
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]
