"""Weekly cross-sectional momentum — ``weekly_cross_sectional_momentum_low_turnover 0.1.0-c016``.

CAMPAIGN_016 research candidate. CANDIDATE SCAFFOLD ONLY — not approved
for paper / demo / live trading.

Cross-pair runner contract: ``ctx.config["cross_pair_h4_closes"]`` must
be a dict ``{pair: pd.Series}`` of aligned H4 close series (completed
bars only). The strategy ranks all seven pairs at weekly rebalance
boundaries and emits a signal only for the selected long (rank 1) or
short (rank 7) candidate for ``ctx.instrument``.
"""

from __future__ import annotations

import hashlib
import math
from datetime import UTC
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.features.weekly_momentum import (
    aggregate_h4_to_weekly_closes,
    is_rebalance_bar,
    rank_pairs_by_score,
    vol_adjusted_momentum_score,
    week_start_monday_utc,
)
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr

EXPECTED_PAIRS: tuple[str, ...] = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)


def _parse_pair(name: str) -> tuple[str, str]:
    base, quote = name.split("_", 1)
    return base, quote


def _usd_leg_direction(pair: str, side: str) -> int:
    """+1 if net long USD, -1 if net short USD, 0 if no USD leg."""
    base, quote = _parse_pair(pair)
    if base == "USD":
        return 1 if side == "long" else -1
    if quote == "USD":
        return -1 if side == "long" else 1
    return 0


def _apply_usd_exposure_gate(
    long_pair: str | None,
    short_pair: str | None,
    max_same_currency_exposure: int,
) -> tuple[str | None, str | None, str | None]:
    """Return (long, short, rejection_reason). max=1 blocks same USD dir."""
    if long_pair is None and short_pair is None:
        return None, None, "no_selection"
    if max_same_currency_exposure >= 2:
        return long_pair, short_pair, None
    long_usd = _usd_leg_direction(long_pair, "long") if long_pair else 0
    short_usd = _usd_leg_direction(short_pair, "short") if short_pair else 0
    if long_usd != 0 and short_usd != 0 and long_usd == short_usd:
        return None, None, "usd_exposure_conflict_both_blocked"
    return long_pair, short_pair, None


class WeeklyCrossSectionalMomentumLowTurnoverStrategy:
    name: str = "weekly_cross_sectional_momentum_low_turnover"

    def __init__(self, version: str = "0.1.0-c016") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        return 420

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config

        fast_weeks = int(cfg.get("momentum_lookback_fast_weeks", 4))
        slow_weeks = int(cfg.get("momentum_lookback_slow_weeks", 12))
        vol_weeks = int(cfg.get("volatility_lookback_weeks", 12))
        blend_fast = float(cfg.get("momentum_blend_fast", 0.5))
        blend_slow = float(cfg.get("momentum_blend_slow", 0.5))
        vol_floor = float(cfg.get("volatility_floor", 1.0e-8))
        atr_len = int(cfg.get("atr_lookback", 14))
        stop_mult = float(cfg.get("atr_stop_multiple", 2.5))
        spread_to_atr_max = float(cfg.get("spread_to_atr_max", 0.15))
        max_same_ccy = int(cfg.get("max_same_currency_exposure", 1))
        timeframe = cfg.get("timeframe", "H4")
        min_atr_pips_by_pair = cfg.get("min_atr_pips", {}) or {}
        min_atr_pips = float(min_atr_pips_by_pair.get(ctx.instrument.name, 0.0))

        if len(df) < self.warmup_bars_required():
            return None

        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        cross_pair: dict[str, pd.Series] | None = cfg.get("cross_pair_h4_closes")
        if not cross_pair or set(cross_pair.keys()) != set(EXPECTED_PAIRS):
            return None

        bar_ts = df.index[-1]
        if len(df.index) < 2:
            return None
        prior_ts = df.index[-2]
        if not is_rebalance_bar(bar_ts, prior_ts):
            return None

        pair_metrics: dict[str, dict[str, Any]] = {}
        pair_scores: dict[str, float] = {}
        for pair in EXPECTED_PAIRS:
            series = cross_pair[pair]
            if bar_ts not in series.index:
                aligned = series.loc[:bar_ts]
            else:
                aligned = series.loc[:bar_ts]
            if len(aligned) < slow_weeks * 6:
                continue
            weekly = aggregate_h4_to_weekly_closes(aligned.index, aligned)
            metrics = vol_adjusted_momentum_score(
                weekly,
                fast_weeks=fast_weeks,
                slow_weeks=slow_weeks,
                vol_weeks=vol_weeks,
                blend_fast=blend_fast,
                blend_slow=blend_slow,
                as_of_week_exclusive=bar_ts,
                volatility_floor=vol_floor,
            )
            pair_metrics[pair] = metrics
            score = metrics.get("score")
            if score is not None and math.isfinite(float(score)):
                pair_scores[pair] = float(score)

        if len(pair_scores) < len(EXPECTED_PAIRS):
            return None

        ranked = rank_pairs_by_score(pair_scores)
        long_pair = ranked[0][0]
        short_pair = ranked[-1][0]
        long_pair, short_pair, usd_reject = _apply_usd_exposure_gate(
            long_pair, short_pair, max_same_ccy,
        )
        if usd_reject:
            return None

        instrument = ctx.instrument.name
        selected_side: str | None = None
        rank = 0
        if instrument == long_pair:
            selected_side = "long"
            rank = 1
        elif instrument == short_pair:
            selected_side = "short"
            rank = len(ranked)
        else:
            return None

        high = df["high"]
        low = df["low"]
        close = df["close"]
        atr_series = atr(high, low, close, atr_len)
        last_atr = float(atr_series.iloc[-1])
        last_close = float(close.iloc[-1])
        if not (math.isfinite(last_atr) and last_atr > 0 and math.isfinite(last_close)):
            return None

        pip_size = float(ctx.instrument.pip_size)
        atr_pips = last_atr / pip_size if pip_size else 0.0
        if atr_pips < min_atr_pips:
            return None

        spread_pips = float(getattr(ctx, "spread_pips", 0.0) or 0.0)
        if spread_pips / last_atr > spread_to_atr_max:
            return None

        stop_distance = stop_mult * last_atr
        if selected_side == "long":
            stop = last_close - stop_distance
        else:
            stop = last_close + stop_distance

        metrics = pair_metrics[instrument]
        rebalance_ts = week_start_monday_utc(bar_ts).isoformat()
        signal_id = _stable_signal_id(
            self.name,
            self.version,
            instrument,
            timeframe,
            rebalance_ts,
            selected_side,
        )
        features: dict[str, Any] = {
            "fast_return": metrics.get("fast_return"),
            "slow_return": metrics.get("slow_return"),
            "volatility": metrics.get("volatility"),
            "score": metrics.get("score"),
            "rank": rank,
            "selected_side": selected_side,
            "rebalance_timestamp": rebalance_ts,
            "stop_distance": stop_distance,
            "long_candidate": long_pair,
            "short_candidate": short_pair,
            "rejection_reason": None,
        }
        ts = pd.Timestamp(bar_ts).tz_convert(UTC).to_pydatetime()
        return Signal(
            signal_id=signal_id,
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=instrument,
            timeframe=timeframe,
            timestamp=ts,
            side=selected_side,  # type: ignore[arg-type]
            entry_intent="market",
            stop_model=f"{stop_mult}*ATR{atr_len} hard stop",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            exit_model="hard_stop_or_time_stop",
            features=features,
            reason=(
                f"weekly cross-sectional momentum {selected_side}: "
                f"rank={rank}/{len(ranked)} score={metrics.get('score'):.4f} "
                f"rebalance={rebalance_ts}"
            ),
        )


def _stable_signal_id(
    name: str,
    version: str,
    instrument: str,
    timeframe: str,
    rebalance_ts: str,
    side: str,
) -> str:
    payload = f"{name}|{version}|{instrument}|{timeframe}|{rebalance_ts}|{side}"
    return hashlib.sha1(payload.encode()).hexdigest()[:16]
