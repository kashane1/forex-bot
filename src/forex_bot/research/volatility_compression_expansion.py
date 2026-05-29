"""Read-only USD_JPY volatility-compression → range-expansion taxonomy.

These are **diagnostic functions, not a strategy**. They never place a trade, change
a verdict, tune a parameter, or approve anything. The module provides two families of
pure, vectorized functions over an M15 OHLC frame (mid prices, UTC-indexed):

* **Compression features** — computed from data available *at the decision bar* `i`
  (bars with index ``<= i`` only). They could in principle gate a live decision, so
  they must contain **no lookahead**. Each returns a Series aligned to the frame index.
* **Expansion labels** — computed from *future* bars (``i+1 .. i+h``). They describe
  what happened after the decision bar and are **labels only**: they must never be used
  as a live feature. Each is explicitly tagged direction-agnostic vs directional.

Lookahead policy is enforced by construction (compression uses ``rolling``/``shift(+)``
only; expansion uses ``shift(-)``) and verified by a causality unit test that truncates
the frame at ``i`` and checks the compression value is unchanged.

Nothing here reads credentials, hits a broker, or runs a campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from forex_bot.strategies.indicators import atr as atr_indicator

PIP = 0.01  # USD_JPY pip size

TZ_NY = ZoneInfo("America/New_York")
TZ_LON = ZoneInfo("Europe/London")
TZ_TOK = ZoneInfo("Asia/Tokyo")

__all__ = [
    "COMPRESSION_FEATURES",
    "DIRECTIONAL_EXPANSION_LABELS",
    "DIRECTION_AGNOSTIC_EXPANSION_LABELS",
    "CompressionExpansionParams",
    "atr_percentile",
    "bandwidth_percentile",
    "breakout_followthrough",
    "breakout_labels",
    "compute_compression_features",
    "compute_expansion_labels",
    "false_breakout",
    "forward_mae_pips",
    "forward_mfe_pips",
    "forward_range_pips",
    "forward_signed_move_pips",
    "inside_bar_count",
    "range_percentile",
    "realized_vol_percentile",
    "session_bucket",
]


@dataclass(frozen=True)
class CompressionExpansionParams:
    """Predeclared parameters. Cuts/grids are fixed here, NOT tuned downstream."""

    atr_len: int = 14
    pct_window: int = 96  # trailing M15 bars (~1 trading day) for percentile context
    bb_len: int = 20
    bb_k: float = 2.0
    rv_len: int = 20
    inside_lookback: int = 6  # max consecutive inside bars to count
    range_lookback: int = 16  # prior-range window for breakout reference (4h)
    horizons: tuple[int, ...] = (4, 8, 16, 32)  # expansion label horizons (M15 bars)
    # Predeclared compression cut grid (percentile thresholds). NOT optimized.
    compression_cuts: tuple[float, ...] = (0.10, 0.20, 0.30)
    primary_cut: float = 0.20
    # Follow-through / false-breakout confirmation as a fraction of decision-bar ATR.
    followthrough_atr_frac: float = 0.5


# --------------------------------------------------------------------------- #
# Session classification (canonical, DST-correct; tested)
# --------------------------------------------------------------------------- #
def session_bucket(ts: datetime) -> str:
    """One primary session bucket for a tz-aware UTC timestamp.

    Per-center local opening hours (DST handled by zoneinfo):
      Tokyo 09:00-15:00 JST · London 08:00-16:00 London · NY 08:00-17:00 ET
    Priority: rollover > london_ny_overlap > ny > london > tokyo > off_hours.
    Mirrors the Phase-2 session atlas definition.
    """
    if ts.tzinfo is None:
        raise ValueError("session_bucket requires a tz-aware UTC timestamp")
    ny = ts.astimezone(TZ_NY)
    lon = ts.astimezone(TZ_LON)
    tok = ts.astimezone(TZ_TOK)
    ny_active = 8 <= ny.hour < 17
    lon_active = 8 <= lon.hour < 16
    tok_active = 9 <= tok.hour < 15
    if ny.hour == 17:
        return "rollover"
    if lon_active and ny_active:
        return "london_ny_overlap"
    if ny_active:
        return "ny"
    if lon_active:
        return "london"
    if tok_active:
        return "tokyo"
    return "off_hours"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _atr_pips(frame: pd.DataFrame, length: int) -> pd.Series:
    return atr_indicator(frame["mid_h"], frame["mid_l"], frame["mid_c"], length=length) / PIP


def _trailing_pct_rank(series: pd.Series, window: int) -> pd.Series:
    """Percentile rank in [0,1] of each bar within its trailing ``window`` (incl. self).

    Uses only past+current data — no lookahead. ``min_periods`` set to half the window
    so early bars are NaN rather than ill-defined.
    """
    return series.rolling(window, min_periods=max(2, window // 2)).rank(pct=True)


def _fwd_max(series: pd.Series, h: int) -> pd.Series:
    """max over (i+1 .. i+h) aligned at index i."""
    return series.shift(-1).rolling(h).max().shift(-(h - 1))


def _fwd_min(series: pd.Series, h: int) -> pd.Series:
    return series.shift(-1).rolling(h).min().shift(-(h - 1))


# --------------------------------------------------------------------------- #
# Compression features (decision-time, no lookahead)
# --------------------------------------------------------------------------- #
def range_percentile(frame: pd.DataFrame, params: CompressionExpansionParams) -> pd.Series:
    rng = (frame["mid_h"] - frame["mid_l"]) / PIP
    return _trailing_pct_rank(rng, params.pct_window)


def atr_percentile(frame: pd.DataFrame, params: CompressionExpansionParams) -> pd.Series:
    return _trailing_pct_rank(_atr_pips(frame, params.atr_len), params.pct_window)


def bandwidth_percentile(frame: pd.DataFrame, params: CompressionExpansionParams) -> pd.Series:
    mid = frame["mid_c"]
    ma = mid.rolling(params.bb_len, min_periods=params.bb_len).mean()
    sd = mid.rolling(params.bb_len, min_periods=params.bb_len).std()
    bandwidth = (2.0 * params.bb_k * sd) / ma.replace(0, np.nan)
    return _trailing_pct_rank(bandwidth, params.pct_window)


def inside_bar_count(frame: pd.DataFrame, params: CompressionExpansionParams) -> pd.Series:
    """Consecutive inside-bar count ending at each bar (contraction signal)."""
    inside = ((frame["mid_h"] <= frame["mid_h"].shift(1)) &
              (frame["mid_l"] >= frame["mid_l"].shift(1))).astype(int)
    reset = (inside == 0).cumsum()
    run = inside.groupby(reset).cumsum()
    return run.clip(upper=params.inside_lookback).astype(float)


def realized_vol_percentile(frame: pd.DataFrame, params: CompressionExpansionParams) -> pd.Series:
    ret = frame["mid_c"].pct_change()
    rv = ret.rolling(params.rv_len, min_periods=params.rv_len).std()
    return _trailing_pct_rank(rv, params.pct_window)


# Registry: name -> (callable, "low_is_compressed" orientation).
# For percentile features, LOW percentile = compressed. For inside_bar_count, HIGH count
# = compressed, so it is handled with its own orientation flag.
COMPRESSION_FEATURES: dict[str, dict] = {
    "range_pct": {"fn": range_percentile, "low_is_compressed": True},
    "atr_pct": {"fn": atr_percentile, "low_is_compressed": True},
    "bandwidth_pct": {"fn": bandwidth_percentile, "low_is_compressed": True},
    "realized_vol_pct": {"fn": realized_vol_percentile, "low_is_compressed": True},
    "inside_bar_count": {"fn": inside_bar_count, "low_is_compressed": False},
}


def compute_compression_features(
    frame: pd.DataFrame, params: CompressionExpansionParams | None = None
) -> pd.DataFrame:
    """Return a frame of all compression features aligned to ``frame`` (decision-time)."""
    params = params or CompressionExpansionParams()
    out = pd.DataFrame(index=frame.index)
    for name, spec in COMPRESSION_FEATURES.items():
        out[name] = spec["fn"](frame, params)
    return out


# --------------------------------------------------------------------------- #
# Expansion labels (future bars; labels only)
# --------------------------------------------------------------------------- #
def forward_range_pips(frame: pd.DataFrame, h: int) -> pd.Series:
    """Direction-agnostic: high-low range over (i+1 .. i+h), pips."""
    return (_fwd_max(frame["mid_h"], h) - _fwd_min(frame["mid_l"], h)) / PIP


def forward_signed_move_pips(frame: pd.DataFrame, h: int) -> pd.Series:
    """Directional: close[i+h] - close[i], pips (signed)."""
    return (frame["mid_c"].shift(-h) - frame["mid_c"]) / PIP


def forward_mfe_pips(frame: pd.DataFrame, h: int) -> pd.Series:
    """Long-perspective max favorable excursion over (i+1 .. i+h), pips (>= 0)."""
    return (_fwd_max(frame["mid_h"], h) - frame["mid_c"]) / PIP


def forward_mae_pips(frame: pd.DataFrame, h: int) -> pd.Series:
    """Long-perspective max adverse excursion over (i+1 .. i+h), pips (<= 0)."""
    return (_fwd_min(frame["mid_l"], h) - frame["mid_c"]) / PIP


def _prior_range(frame: pd.DataFrame, params: CompressionExpansionParams) -> tuple[pd.Series, pd.Series]:
    hi = frame["mid_h"].rolling(params.range_lookback).max().shift(1)
    lo = frame["mid_l"].rolling(params.range_lookback).min().shift(1)
    return hi, lo


def breakout_labels(
    frame: pd.DataFrame, h: int, params: CompressionExpansionParams
) -> pd.DataFrame:
    """Breakout of the prior range within horizon h. Columns: up, down, any."""
    hi, lo = _prior_range(frame, params)
    up = _fwd_max(frame["mid_h"], h) > hi
    dn = _fwd_min(frame["mid_l"], h) < lo
    return pd.DataFrame({"breakout_up": up, "breakout_down": dn, "breakout_any": up | dn},
                        index=frame.index)


def breakout_followthrough(
    frame: pd.DataFrame, h: int, params: CompressionExpansionParams
) -> pd.Series:
    """Directional continuation: a prior-range break whose close[i+h] finishes beyond
    the broken level by >= followthrough_atr_frac * decision-bar ATR (in the break dir).
    """
    hi, lo = _prior_range(frame, params)
    atr_px = atr_indicator(frame["mid_h"], frame["mid_l"], frame["mid_c"], length=params.atr_len)
    buf = params.followthrough_atr_frac * atr_px
    bl = breakout_labels(frame, h, params)
    end = frame["mid_c"].shift(-h)
    ft_up = bl["breakout_up"] & (end > (hi + buf))
    ft_dn = bl["breakout_down"] & (end < (lo - buf))
    return (ft_up | ft_dn)


def false_breakout(
    frame: pd.DataFrame, h: int, params: CompressionExpansionParams
) -> pd.Series:
    """A prior-range break whose close[i+h] returns back inside the prior range."""
    hi, lo = _prior_range(frame, params)
    bl = breakout_labels(frame, h, params)
    end = frame["mid_c"].shift(-h)
    fb_up = bl["breakout_up"] & (end < hi)
    fb_dn = bl["breakout_down"] & (end > lo)
    return ((fb_up | fb_dn) & bl["breakout_any"])


DIRECTION_AGNOSTIC_EXPANSION_LABELS = ("fwd_range_pips", "fwd_mfe_pips", "fwd_mae_pips",
                                       "breakout_any")
DIRECTIONAL_EXPANSION_LABELS = ("fwd_signed_move_pips", "breakout_up", "breakout_down",
                                "breakout_followthrough", "false_breakout")


def compute_expansion_labels(
    frame: pd.DataFrame, params: CompressionExpansionParams | None = None
) -> pd.DataFrame:
    """Return all expansion labels across all horizons (suffix ``_h{H}``). Labels only."""
    params = params or CompressionExpansionParams()
    out = pd.DataFrame(index=frame.index)
    for h in params.horizons:
        out[f"fwd_range_pips_h{h}"] = forward_range_pips(frame, h)
        out[f"fwd_signed_move_pips_h{h}"] = forward_signed_move_pips(frame, h)
        out[f"fwd_mfe_pips_h{h}"] = forward_mfe_pips(frame, h)
        out[f"fwd_mae_pips_h{h}"] = forward_mae_pips(frame, h)
        bl = breakout_labels(frame, h, params)
        out[f"breakout_up_h{h}"] = bl["breakout_up"]
        out[f"breakout_down_h{h}"] = bl["breakout_down"]
        out[f"breakout_any_h{h}"] = bl["breakout_any"]
        out[f"breakout_followthrough_h{h}"] = breakout_followthrough(frame, h, params)
        out[f"false_breakout_h{h}"] = false_breakout(frame, h, params)
    return out
