"""Read-only, lookahead-safe SLOW macro/rates/calendar regime-context features.

This module supports a tradeability-CONTEXT diagnostic, **not** a strategy and **not**
fast-news trading. It builds SLOW (daily/weekly) macro/rates/risk regime features and
event-calendar windows, joined to an intraday index with an explicit **as-of / lagged**
rule so that a decision bar at time ``t`` can only ever see macro values published on or
before ``t - publication_lag``. Nothing here reacts to a release intrabar, predicts an
outcome, or depends on latency: a real signal here must survive being delayed by hours
or days (Phase 3 tests exactly that).

Hard framing (see MACRO_REGIME_CONTEXT_TRADEABILITY_THESIS_FRAMING.md):
  * macro context is a tradeability conditioner / no-trade filter, NEVER an entry signal;
  * event CALENDAR uses public schedule DATES only; the event OUTCOME is never used;
  * all features are daily/weekly cadence; no sub-minute / tick logic.

No credentials, no broker, no campaign, no verdict change.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

# FRED cache feature ids we consume (daily series).
FRED_FEATURES = {
    "DGS2": "us_2y_yield",
    "DGS10": "us_10y_yield",
    "VIXCLS": "vix",
    "SP500": "sp500",
    "DTWEXBGS": "broad_usd_index",
}

# Best-effort FOMC scheduled announcement DATES (UTC date of the day-2 statement),
# 2021-06 .. 2025-06. PUBLIC SCHEDULE — lookahead-safe (known far in advance). Marked
# best-effort: verify against the Fed calendar before any precommit. CPI/BOJ deferred.
FOMC_ANNOUNCEMENT_DATES = [
    "2021-06-16", "2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15",
    "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27",
    "2022-09-21", "2022-11-02", "2022-12-14",
    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26",
    "2023-09-20", "2023-11-01", "2023-12-13",
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31",
    "2024-09-18", "2024-11-07", "2024-12-18",
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
]
FOMC_ANNOUNCEMENT_HOUR_UTC = 18  # ~14:00 ET nominal; exactness not needed for day windows
NFP_RELEASE_HOUR_UTC = 13
NFP_RELEASE_MINUTE_UTC = 30  # 08:30 ET nominal


@dataclass(frozen=True)
class MacroRegimeParams:
    publication_lag_days: int = 1          # as-of lag: no value newer than t - this
    trend_window_days: int = 20            # ~1 month slow trend
    pctile_window_days: int = 252          # ~1y trailing percentile for level regime
    high_pctile: float = 0.67
    low_pctile: float = 0.33
    event_pre_hours: int = 24              # "pre-event" window
    event_post_hours: int = 48            # "post-event" window (stabilization horizons inside)
    stabilization_hours: tuple[int, ...] = field(default=(4, 8, 24, 48))


# --------------------------------------------------------------------------- #
# FRED cache loading
# --------------------------------------------------------------------------- #
def default_fred_cache_dir(start: Path | None = None) -> Path:
    """Locate ``data/external_features/.fred_cache`` (gitignored local data).

    Searches the given start dir (or this module's repo root) and walks up a few
    levels so it works from a git worktree whose ``data/`` is empty while the main
    checkout holds the cache.
    """
    rel = Path("data/external_features/.fred_cache")
    here = start or Path(__file__).resolve()
    for base in [here, *here.parents][:8]:
        cand = base / rel
        if cand.is_dir():
            return cand
    # last resort: repo-root guess
    return Path(__file__).resolve().parents[2] / rel


def load_fred_series(cache_dir: Path, series_id: str) -> pd.Series:
    """Load one daily FRED series as a UTC-indexed float Series (date-normalized)."""
    path = Path(cache_dir) / f"{series_id}.json"
    payload = json.loads(path.read_text())
    rows = payload["data"]
    idx = pd.to_datetime([r["date"] for r in rows], utc=True).normalize()
    vals = pd.to_numeric([r.get("value") for r in rows], errors="coerce")
    return pd.Series(vals, index=idx, name=payload.get("feature_id", series_id)).sort_index()


# --------------------------------------------------------------------------- #
# Slow daily regime features
# --------------------------------------------------------------------------- #
def _trend_sign(s: pd.Series, window_days: int) -> pd.Series:
    return np.sign(s - s.shift(window_days))


def _level_regime(s: pd.Series, window: int, lo: float, hi: float) -> pd.Series:
    rank = s.rolling(window, min_periods=max(20, window // 4)).rank(pct=True)
    out = pd.Series(index=s.index, dtype="object")
    out[rank <= lo] = "low"
    out[(rank > lo) & (rank < hi)] = "mid"
    out[rank >= hi] = "high"
    return out


def build_daily_regime_features(
    cache_dir: Path | None = None, params: MacroRegimeParams | None = None
) -> pd.DataFrame:
    """Daily, UTC-indexed slow regime features from the FRED cache (no lookahead within
    the daily frame; the as-of join applies the publication lag to the intraday index)."""
    params = params or MacroRegimeParams()
    cache_dir = cache_dir or default_fred_cache_dir()
    series = {fid: load_fred_series(cache_dir, sid) for sid, fid in FRED_FEATURES.items()}
    # common daily calendar
    idx = pd.DatetimeIndex(sorted(set().union(*[s.index for s in series.values()])))
    df = pd.DataFrame(index=idx)
    for fid, s in series.items():
        df[fid] = s.reindex(idx).ffill()  # carry last known value forward (slow data)

    tw, pw = params.trend_window_days, params.pctile_window_days
    lo, hi = params.low_pctile, params.high_pctile

    # rates
    df["us_2s10s"] = df["us_10y_yield"] - df["us_2y_yield"]
    df["us_2y_trend"] = _trend_sign(df["us_2y_yield"], tw)        # +1 rising / -1 falling
    df["us_10y_trend"] = _trend_sign(df["us_10y_yield"], tw)
    df["us_2y_regime"] = _level_regime(df["us_2y_yield"], pw, lo, hi)
    df["rates_diff_proxy_regime"] = _level_regime(df["us_2y_yield"], pw, lo, hi)  # US side dominant
    # risk
    df["vix_regime"] = _level_regime(df["vix"], pw, lo, hi)
    df["vix_trend"] = _trend_sign(df["vix"], tw)
    df["sp500_trend"] = _trend_sign(df["sp500"], tw)
    df["broad_usd_trend"] = _trend_sign(df["broad_usd_index"], tw)
    # composite risk-off flag (slow): high VIX OR falling SP500
    df["risk_off"] = (df["vix_regime"] == "high") | (df["sp500_trend"] < 0)
    return df


# --------------------------------------------------------------------------- #
# As-of / lagged join to an intraday index (lookahead-safe)
# --------------------------------------------------------------------------- #
def asof_join(
    daily: pd.DataFrame, target_index: pd.DatetimeIndex, params: MacroRegimeParams | None = None
) -> pd.DataFrame:
    """For each target timestamp t, attach the most recent daily row with
    ``daily.date <= t - publication_lag_days``. Pure backward as-of merge: no future
    leakage. Returns a frame aligned to ``target_index``."""
    params = params or MacroRegimeParams()
    lag = pd.Timedelta(days=params.publication_lag_days)
    left = pd.DataFrame(index=target_index).reset_index(names="t").sort_values("t")
    right = daily.reset_index(names="d").sort_values("d")
    right["avail"] = right["d"] + lag  # value for day d is usable only at/after d + lag
    merged = pd.merge_asof(left, right, left_on="t", right_on="avail", direction="backward")
    merged = merged.set_index("t")
    merged.index.name = target_index.name
    return merged.drop(columns=[c for c in ("d", "avail") if c in merged.columns])


# --------------------------------------------------------------------------- #
# Event calendar (public schedule dates only)
# --------------------------------------------------------------------------- #
def nfp_release_datetimes(start: str, end: str) -> list[pd.Timestamp]:
    """First Friday of each month in [start, end), at 13:30 UTC (08:30 ET nominal)."""
    out = []
    start_ts, end_ts = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
    cur = start_ts.normalize().replace(day=1)
    while cur < end_ts:
        offset = (4 - cur.weekday()) % 7  # weekday(): Mon=0..Sun=6; Friday=4
        first_friday = cur + pd.Timedelta(days=offset)
        ts = first_friday + pd.Timedelta(hours=NFP_RELEASE_HOUR_UTC, minutes=NFP_RELEASE_MINUTE_UTC)
        if start_ts <= ts < end_ts:
            out.append(ts)
        cur = cur + pd.offsets.MonthBegin(1)
    return out


def fomc_announcement_datetimes(start: str, end: str) -> list[pd.Timestamp]:
    out = []
    s, e = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
    for d in FOMC_ANNOUNCEMENT_DATES:
        ts = pd.Timestamp(d, tz="UTC") + pd.Timedelta(hours=FOMC_ANNOUNCEMENT_HOUR_UTC)
        if s <= ts < e:
            out.append(ts)
    return out


def build_event_calendar(start: str, end: str) -> pd.DataFrame:
    """Public-schedule event datetimes (NFP computed exactly; FOMC best-effort fixture).

    CPI/BOJ are intentionally absent (deferred pending a verified source)."""
    rows = []
    for ts in nfp_release_datetimes(start, end):
        rows.append({"event": "NFP", "time_utc": ts, "source": "computed_first_friday"})
    for ts in fomc_announcement_datetimes(start, end):
        rows.append({"event": "FOMC", "time_utc": ts, "source": "best_effort_public_schedule"})
    cal = pd.DataFrame(rows).sort_values("time_utc").reset_index(drop=True)
    return cal


def event_proximity_hours(target_index: pd.DatetimeIndex, event_times: list[pd.Timestamp]) -> pd.Series:
    """Signed hours from each target bar to the NEAREST event (negative = before event,
    positive = after). Uses only event SCHEDULE times (known in advance)."""
    if not event_times:
        return pd.Series(np.nan, index=target_index)
    ev = np.array(sorted(pd.Timestamp(t).value for t in event_times))
    tv = target_index.asi8
    pos = np.searchsorted(ev, tv)
    out = np.full(len(tv), np.nan)
    for k in range(len(tv)):
        # candidate nearest events: the one just before and just after this bar
        cand = []
        if pos[k] < len(ev):
            cand.append(ev[pos[k]])
        if pos[k] > 0:
            cand.append(ev[pos[k] - 1])
        nearest = min(cand, key=lambda e: abs(e - tv[k]))
        # hours_since_event: positive = bar AFTER event, negative = bar BEFORE event
        out[k] = (tv[k] - nearest) / 3.6e12  # ns → hours
    return pd.Series(out, index=target_index)


def event_window_flags(
    target_index: pd.DatetimeIndex, event_times: list[pd.Timestamp],
    params: MacroRegimeParams | None = None,
) -> pd.DataFrame:
    """Boolean pre/post-event flags + 'hours_since_event' for the nearest event."""
    params = params or MacroRegimeParams()
    hse = event_proximity_hours(target_index, event_times)  # +after / -before
    out = pd.DataFrame(index=target_index)
    out["hours_since_event"] = hse
    out["pre_event"] = (hse < 0) & (hse >= -params.event_pre_hours)
    out["post_event"] = (hse >= 0) & (hse <= params.event_post_hours)
    out["event_window"] = out["pre_event"] | out["post_event"]
    return out


def stabilization_bucket(hours_since_event: pd.Series, params: MacroRegimeParams | None = None) -> pd.Series:
    """Bucket post-event time into stabilization windows (<=4h, <=8h, <=24h, <=48h, normal)."""
    params = params or MacroRegimeParams()
    out = pd.Series("normal", index=hours_since_event.index, dtype="object")
    h = hours_since_event
    prev = 0
    for hz in params.stabilization_hours:
        out[(h >= prev) & (h < hz)] = f"post_{hz}h"
        prev = hz
    out[(h < 0) & (h >= -params.event_pre_hours)] = "pre_event"
    return out
