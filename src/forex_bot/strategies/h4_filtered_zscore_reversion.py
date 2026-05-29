"""Filtered H4 z-score mean-reversion — `h4_filtered_zscore_reversion` (c027).

CAMPAIGN_027 research **scaffold** — NOT APPROVED, `paper_only`, no evidence run.
See the binding precommit
``docs/research/CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md``.

This is the single frozen candidate that survived the edge-discovery front gate
(`research-edge-discovery-front-gate-idea-selection-001`): the only idea in the
program to clear cost-feasibility, forward-return information, all six matched
nulls, filter-adds-edge ablation, conservative financing cost, pair-robustness,
and multi-year positivity together. It is **still borderline** (wafer-thin edge;
2024/2026 negative) and must be killed quickly if a future train/validation
sprint fails — nothing here is approved.

Frozen rule (last completed H4 bar `t`, mid OHLC, **no lookahead**):

  * **z-score** of the mid close over ``zscore_lookback`` (=20) bars, with the
    rolling mean/σ **shifted one bar** (σ uses pandas ``ddof=1``) so bar `t`'s z
    compares the current close to the *prior* 20 bars. This matches the lab
    engine that produced the evidence (``run_filter_ablation.py``) — a deliberate
    fidelity choice, hence the z/ATR are computed inline rather than via
    ``indicators.zscore`` (``ddof=0``) / ``indicators.atr`` (Wilder).
  * **entry** when ``z >= +strong_extension_abs_z`` (=2.5): a rich extension to
    **sell** (revert down). **Short-only** — the long side hurt edge in ablation
    (``FILTER_HURTS_EDGE``) and is never entered (optionally surfaced as a
    diagnostic-only decision, never sized).
  * **low-vol filter**: trailing ``atr_percentile_window`` (=250) percentile rank
    of ATR-``atr_lookback`` (=14, simple mean of true range), shifted one bar,
    ``<= atr_percentile_max`` (=0.33).
  * **quiet-session filter**: UTC-hour session bucket of bar `t` in
    ``quiet_sessions`` (={asia, london}).
  * **exit** (campaign convention, not emitted by this module): time stop at
    ``max_bars_in_trade`` (=12) H4 bars + a wide protective ATR stop
    (``atr_stop_multiple`` =3.0 × ATR-14). No take-profit, no trailing.

The emitted Signal declares the protective stop and the time-stop exit model; the
fill convention (``next_bar_open``) and the time/stop simulation belong to the
campaign runner, not this pure-signal module. No broker/executor import; the loop
refuses to run this family while ``approved_strategies.yaml`` is empty.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC
from decimal import Decimal
from typing import Any

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext

# UTC-hour session buckets (mirrors research.edge_discovery.matched_nulls
# .session_bucket_utc — kept local so the strategy has no research-lab import).
_SESSION_BUCKETS = (
    ("asia", 0, 7),
    ("london", 7, 12),
    ("london_ny_overlap", 12, 16),
    ("new_york", 16, 21),
    ("late", 21, 24),
)


def session_bucket_utc(ts: pd.Timestamp) -> str:
    """UTC-hour session bucket. asia[0,7) london[7,12) overlap[12,16)
    new_york[16,21) late[21,24)."""
    h = int(pd.Timestamp(ts).tz_convert(UTC).hour) if ts.tzinfo else int(ts.hour)
    for name, lo, hi in _SESSION_BUCKETS:
        if lo <= h < hi:
            return name
    return "late"


@dataclass(frozen=True)
class ZScoreDecision:
    """Pure per-bar decision components for the last completed bar."""

    timestamp: pd.Timestamp
    close: float
    atr14: float
    zscore: float
    atr_percentile: float
    session_bucket: str
    f_strong_extension: bool
    f_low_vol: bool
    f_quiet_session: bool
    raw_side: str  # 'short' if z>0, 'long' if z<0 (toward the mean)
    entered_short: bool


def _isnan(v: Any) -> bool:
    try:
        return v != v
    except TypeError:
        return False


def _true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    return pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)


def compute_decision(df: pd.DataFrame, cfg: dict[str, Any]) -> ZScoreDecision | None:
    """Compute the frozen-rule decision on the **last completed** bar of ``df``.

    ``df`` is a completed-bars frame indexed by UTC time with mid ``open/high/
    low/close``. Returns ``None`` if warmup is insufficient or any feature is NaN.
    No lookahead: rolling mean/σ and the ATR percentile are ``.shift(1)``.
    """
    z_len = int(cfg.get("zscore_lookback", 20))
    strong_z = float(cfg.get("strong_extension_abs_z", 2.5))
    atr_len = int(cfg.get("atr_lookback", 14))
    pct_window = int(cfg.get("atr_percentile_window", 250))
    pct_max = float(cfg.get("atr_percentile_max", 0.33))
    quiet = set(cfg.get("quiet_sessions", ("asia", "london")))
    std_ddof = int(cfg.get("zscore_std_ddof", 1))

    needed = max(z_len, atr_len + pct_window) + 2
    if len(df) < needed:
        return None

    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)

    mean = close.rolling(window=z_len, min_periods=z_len).mean().shift(1)
    std = close.rolling(window=z_len, min_periods=z_len).std(ddof=std_ddof).shift(1)
    z = (close - mean) / std

    tr = _true_range(high, low, close)
    atr = tr.rolling(window=atr_len, min_periods=atr_len).mean()
    atr_pct = (
        atr.rolling(window=pct_window, min_periods=pct_window)
        .apply(lambda a: (a[-1] >= a).mean(), raw=True)
        .shift(1)
    )

    ts = pd.Timestamp(df.index[-1])
    last_close = float(close.iloc[-1])
    last_atr = float(atr.iloc[-1])
    last_z = float(z.iloc[-1])
    last_pct = float(atr_pct.iloc[-1])
    if any(_isnan(v) for v in (last_atr, last_z, last_pct)):
        return None

    session = session_bucket_utc(ts)
    f_strong = abs(last_z) >= strong_z
    f_low_vol = last_pct <= pct_max
    f_quiet = session in quiet
    raw_side = "short" if last_z > 0 else "long"
    entered_short = (last_z >= strong_z) and f_low_vol and f_quiet  # short-only

    return ZScoreDecision(
        timestamp=ts,
        close=last_close,
        atr14=last_atr,
        zscore=last_z,
        atr_percentile=last_pct,
        session_bucket=session,
        f_strong_extension=f_strong,
        f_low_vol=f_low_vol,
        f_quiet_session=f_quiet,
        raw_side=raw_side,
        entered_short=entered_short,
    )


class H4FilteredZscoreReversionStrategy:
    """Short-only filtered H4 z-score reversion (CAMPAIGN_027 scaffold)."""

    name: str = "h4_filtered_zscore_reversion"
    paper_only: bool = True  # research-only — never auto-promoted to live

    def __init__(self, version: str = "0.1.0-c027") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # atr_percentile_window (250) + atr_lookback (14) + z buffer
        return 270

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        cfg = ctx.config
        timeframe = cfg.get("timeframe", "H4")
        atr_len = int(cfg.get("atr_lookback", 14))
        atr_stop_multiple = float(cfg.get("atr_stop_multiple", 3.0))
        max_bars = int(cfg.get("max_bars_in_trade", 12))

        decision = compute_decision(df, cfg)
        if decision is None:
            return None

        # Short-only: the long side is diagnostic-only and never entered.
        if not decision.entered_short:
            return None

        # One position per instrument (RiskEngine also enforces this).
        if any(
            not pos.is_flat and pos.instrument == ctx.instrument.name
            for pos in ctx.open_positions
        ):
            return None

        # Protective hard stop — wide (tail-risk control), above entry for a short.
        stop = decision.close + atr_stop_multiple * decision.atr14

        features: dict[str, Any] = {
            "zscore": decision.zscore,
            "atr14": decision.atr14,
            "atr_percentile": decision.atr_percentile,
            "session_bucket": decision.session_bucket,
            "f_low_vol": decision.f_low_vol,
            "f_quiet_session": decision.f_quiet_session,
            "f_strong_extension": decision.f_strong_extension,
            "last_close": decision.close,
            "max_bars_in_trade": max_bars,
        }
        last_idx = df.index[-1]
        return Signal(
            signal_id=_stable_signal_id(
                self.name, self.version, ctx.instrument.name, timeframe,
                last_idx, "short",
            ),
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=timeframe,
            timestamp=pd.Timestamp(last_idx).tz_convert(UTC).to_pydatetime(),
            side="short",
            entry_intent="market",
            stop_model=f"ATR{atr_len}*{atr_stop_multiple}",
            stop_price=ctx.instrument.round_price(Decimal(str(stop))),
            take_profit_price=None,
            exit_model=f"protective_atr_stop_or_time_stop_{max_bars}",
            features=features,
            reason=(
                f"H4 filtered z-reversion short: z={decision.zscore:.2f}>=2.5, "
                f"atr_pct={decision.atr_percentile:.2f}<=0.33, "
                f"session={decision.session_bucket}"
            ),
        )


def _stable_signal_id(*parts: Any) -> str:
    canonical = "|".join(str(p) for p in parts)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:24]
