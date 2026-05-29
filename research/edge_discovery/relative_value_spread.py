"""Relative-value / cointegration spread reversion screen (CAMPAIGN_028, Phase 1).

This is a **front-gate screen**, not a strategy and not evidence. It asks the
cheap, falsifiable question the edge-discovery lab exists to answer *before* any
campaign is scaffolded:

    For a pair of correlated majors (leg1, leg2), does fading the hedge-ratio-
    adjusted log-spread ``s_t = ln(P1_t) - beta * ln(P2_t)`` when its rolling
    z-score hits an extreme produce a forward-return expectancy that (a) is
    cost-feasible on two legs, (b) beats a random-timing matched null on the
    *same* spread, (c) is actually driven by the z-threshold filter rather than
    just by trading the spread at all, and (d) survives best-of-N selection
    across the candidate pair set?

If the answer is "no" on any leg, the thesis is killed here — exactly as C026
killed the timeframe ladder — and CAMPAIGN_028 becomes a documented rejection
with the freeze intact. If it survives, a precommit + 027-style scaffold is
earned.

Design choices (all deliberately conservative / honest):

* **Train only.** ``beta`` is estimated by OLS on the train window and *frozen*;
  the z-score uses strictly-prior rolling stats (``shift(1)``) so there is no
  look-ahead. The caller (CLI) refuses any window that reaches into validation
  or the sealed TEST lockbox.
* **next-bar-open emulation.** Signals advance one bar before the forward window
  is measured, so the screen never books a same-bar-close edge.
* **Two-leg cost.** Every trade pays round-trip transaction cost on *both* legs
  (leg2 scaled by ``|beta|``) plus a conservative financing stress on both legs.
  A spread trade is twice the cost of a single-instrument trade and the screen
  reflects that.
* **Pure-numpy stationarity.** ``statsmodels`` is not a dependency; the
  mean-reversion diagnostic is an AR(1) half-life computed directly.

Import-isolated: numpy / pandas + the existing lab primitives
(``windows`` / ``null`` / ``costs`` / ``cost_feasibility`` /
``multiple_comparison``). No ``forex_bot.broker`` / ``loops`` / ``approval`` /
``execution`` import. The lab cannot approve, promote, or open a lockbox.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from research.edge_discovery.cost_feasibility import classify_cost_feasibility
from research.edge_discovery.costs import cost_fraction, financing_stress_fraction
from research.edge_discovery.null import NullBaseline, compare_to_null, random_null_baseline
from research.edge_discovery.windows import Side, compute_forward_returns

# Train window for CAMPAIGN_028's front-gate screen. Validation and TEST are
# never touched here (see CAMPAIGN_028_NEW_THESIS_BRIEF.md §1 and the C027 split
# convention: train 2020-01-01..2022-12-31).
TRAIN_START = "2020-01-01"
TRAIN_END = "2022-12-31"

DEFAULT_LOOKBACK = 60          # rolling bars for the spread z-score (H4 → ~10 days)
DEFAULT_THRESHOLD = 2.0        # |z| entry threshold
DEFAULT_WINDOW_BARS = 12       # forward hold (matches C027's 12-bar H4 hold)
DEFAULT_SPREAD_PIPS = 1.5      # conservative per-leg round-trip spread
DEFAULT_SLIP_PIPS = 0.2        # per-leg slippage (×2 inside cost_fraction)


# ---------------------------------------------------------------------------
# Spread construction
# ---------------------------------------------------------------------------


def align_two(frame1: pd.DataFrame, frame2: pd.DataFrame) -> pd.DataFrame:
    """Inner-join two H4 mid-close frames on their UTC index.

    Returns a frame with ``p1`` / ``p2`` mid-close columns on the common bars.
    """
    if "close" not in frame1.columns or "close" not in frame2.columns:
        raise ValueError("both frames must have a 'close' column")
    # Drop any duplicate index labels (e.g. DST-fold timestamps in the store)
    # before aligning — keep the first occurrence on each side.
    c1 = frame1["close"].astype(float)
    c2 = frame2["close"].astype(float)
    c1 = c1[~c1.index.duplicated(keep="first")]
    c2 = c2[~c2.index.duplicated(keep="first")]
    joined = pd.concat({"p1": c1, "p2": c2}, axis=1, join="inner").dropna()
    joined = joined[(joined["p1"] > 0) & (joined["p2"] > 0)]
    joined = joined.sort_index()
    return joined


def estimate_beta(aligned: pd.DataFrame) -> float:
    """OLS hedge ratio ``beta`` from ``ln(p1) = a + beta * ln(p2)`` on the
    supplied (train) bars. Frozen by the caller for the whole screen."""
    if len(aligned) < 10:
        raise ValueError(f"need >=10 aligned bars to estimate beta, got {len(aligned)}")
    lp1 = np.log(aligned["p1"].to_numpy(dtype=float))
    lp2 = np.log(aligned["p2"].to_numpy(dtype=float))
    beta, _intercept = np.polyfit(lp2, lp1, 1)
    return float(beta)


def build_spread_frame(aligned: pd.DataFrame, beta: float) -> pd.DataFrame:
    """Add the log-spread ``s`` and a price-like ``close = exp(s)`` column.

    Encoding the spread as ``close = exp(s)`` lets the existing lab primitives
    (``compute_forward_returns`` / ``random_null_baseline``) operate on it
    unchanged: ``ln(close_{t+w}/close_t) == s_{t+w} - s_t`` is exactly the
    log-P&L of being *long* the spread, and ``Side.SHORT`` flips the sign.
    """
    out = aligned.copy()
    out["s"] = np.log(out["p1"]) - beta * np.log(out["p2"])
    out["close"] = np.exp(out["s"])
    return out


def ar1_half_life(s: np.ndarray) -> dict[str, float | None]:
    """AR(1) mean-reversion diagnostic, pure numpy.

    Regress ``Δs_t = a + b * s_{t-1}``; ``phi = 1 + b``. Half-life of mean
    reversion is ``-ln(2)/ln(phi)`` when ``0 < phi < 1`` (reverting), else None
    (random-walk or explosive). Reported descriptively only.
    """
    s = np.asarray(s, dtype=float)
    if len(s) < 20:
        return {"ar1_phi": None, "half_life_bars": None}
    s_lag = s[:-1]
    ds = np.diff(s)
    b, _a = np.polyfit(s_lag, ds, 1)
    phi = 1.0 + float(b)
    if 0.0 < phi < 1.0:
        half_life = float(-np.log(2.0) / np.log(phi))
    else:
        half_life = None
    return {"ar1_phi": phi, "half_life_bars": half_life}


# ---------------------------------------------------------------------------
# Signal + forward returns
# ---------------------------------------------------------------------------


def rolling_z(s: pd.Series, lookback: int) -> pd.Series:
    """Rolling z-score of ``s`` using strictly-prior stats (``shift(1)``).

    ``mu`` / ``sd`` are computed over the ``lookback`` bars *ending at t-1*, so
    ``z_t`` is knowable at the close of bar t with no look-ahead.
    """
    mu = s.rolling(lookback).mean().shift(1)
    sd = s.rolling(lookback).std(ddof=1).shift(1)
    return (s - mu) / sd


def _advance_one_bar(times: pd.Index, sig_positions: np.ndarray) -> list[pd.Timestamp]:
    """Map signal bar positions to the *next* bar's timestamp (next-bar-open
    emulation). Positions at the last bar are dropped (no next bar)."""
    keep = sig_positions[sig_positions + 1 < len(times)]
    return [times[p + 1] for p in keep]


@dataclass(frozen=True)
class SpreadScreenResult:
    """One candidate spread's front-gate screen result. Descriptive only."""

    label: str
    instrument1: str
    instrument2: str
    beta: float
    lookback: int
    threshold: float
    window_bars: int
    n_bars: int
    n_signals: int
    n_short: int
    n_long: int
    ar1_phi: float | None
    half_life_bars: float | None
    spread_atr_per_bar: float
    two_leg_cost_fraction: float
    spread_atr_ratio: float
    cost_flags: list[str]
    pre_cost_mean: float
    post_cost_mean: float
    all_bar_post_cost_mean: float
    null_mean: float
    null_std: float
    null_band: str
    gap_in_null_stds: float | None
    filter_adds_edge: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        d = self.__dict__.copy()
        d["cost_flags"] = list(self.cost_flags)
        d["notes"] = list(self.notes)
        return d


def screen_one_spread(
    frame1: pd.DataFrame,
    frame2: pd.DataFrame,
    *,
    instrument1: str,
    instrument2: str,
    lookback: int = DEFAULT_LOOKBACK,
    threshold: float = DEFAULT_THRESHOLD,
    window_bars: int = DEFAULT_WINDOW_BARS,
    spread_pips: float = DEFAULT_SPREAD_PIPS,
    slip_pips: float = DEFAULT_SLIP_PIPS,
    apply_financing: bool = True,
    seeds: range = range(20),
) -> SpreadScreenResult:
    """Screen one candidate spread on the supplied (train) frames.

    Both frames must already be restricted to the train window by the caller.
    """
    aligned = align_two(frame1, frame2)
    if len(aligned) < lookback + window_bars + 5:
        raise ValueError(
            f"{instrument1}-{instrument2}: only {len(aligned)} aligned bars; "
            f"need > lookback+window+5 = {lookback + window_bars + 5}"
        )
    beta = estimate_beta(aligned)
    sf = build_spread_frame(aligned, beta)
    s = sf["s"]
    z = rolling_z(s, lookback)
    times = sf.index

    # Spread "ATR" proxy: mean absolute per-bar change of the log-spread.
    spread_atr_per_bar = float(np.abs(np.diff(s.to_numpy(dtype=float))).mean())

    # Two-leg round-trip cost as a fraction of spread-return units, at the
    # median leg prices (a constant approximation used for both the per-trade
    # overlay reference and the null overlay). leg2 scaled by |beta|.
    med_p1 = float(aligned["p1"].median())
    med_p2 = float(aligned["p2"].median())
    cost1 = cost_fraction(instrument1, med_p1, spread_pips=spread_pips, slip_pips=slip_pips)
    cost2 = cost_fraction(instrument2, med_p2, spread_pips=spread_pips, slip_pips=slip_pips)
    two_leg_cost = float(cost1 + abs(beta) * cost2)
    fin = 0.0
    if apply_financing:
        fin1 = financing_stress_fraction(instrument1, bars_held=window_bars)
        fin2 = financing_stress_fraction(instrument2, bars_held=window_bars)
        fin = float(fin1 + abs(beta) * fin2)
    per_trade_cost = two_leg_cost + fin

    spread_atr_ratio = (
        two_leg_cost / spread_atr_per_bar if spread_atr_per_bar > 0 else float("inf")
    )
    cost_cell = classify_cost_feasibility(
        f"{instrument1}-{instrument2}", spread_atr_ratio, kind="pair"
    )

    # Signal positions (fade the extreme): short the spread when z>=+thr, long
    # when z<=-thr. Advance one bar (next-bar-open emulation).
    z_arr = z.to_numpy(dtype=float)
    short_pos = np.where(z_arr >= threshold)[0]
    long_pos = np.where(z_arr <= -threshold)[0]
    short_times = _advance_one_bar(times, short_pos)
    long_times = _advance_one_bar(times, long_pos)

    fr_short = compute_forward_returns(sf, short_times, window_bars=window_bars, side=Side.SHORT)
    fr_long = compute_forward_returns(sf, long_times, window_bars=window_bars, side=Side.LONG)
    parts = [p.per_signal for p in (fr_short, fr_long) if not p.per_signal.empty]
    per_signal = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

    n_short = len(fr_short.per_signal)
    n_long = len(fr_long.per_signal)
    n_signals = n_short + n_long

    if per_signal.empty:
        pre_mean = 0.0
        post_mean = 0.0
    else:
        per_signal = per_signal.copy()
        per_signal["log_return_post_cost"] = per_signal["log_return"] - per_trade_cost
        pre_mean = float(per_signal["log_return"].mean())
        post_mean = float(per_signal["log_return_post_cost"].mean())

    # "Filter off" baseline: fade the sign of z on *every* bar (no threshold),
    # same next-bar-open + same hold + same two-leg cost. If the thresholded
    # entry is no better than this, the z-filter only reduces sample.
    all_pos_short = np.where(z_arr > 0)[0]
    all_pos_long = np.where(z_arr < 0)[0]
    fr_all_short = compute_forward_returns(
        sf, _advance_one_bar(times, all_pos_short), window_bars=window_bars, side=Side.SHORT
    )
    fr_all_long = compute_forward_returns(
        sf, _advance_one_bar(times, all_pos_long), window_bars=window_bars, side=Side.LONG
    )
    all_parts = [p.per_signal for p in (fr_all_short, fr_all_long) if not p.per_signal.empty]
    if all_parts:
        all_df = pd.concat(all_parts, ignore_index=True)
        all_bar_post_mean = float((all_df["log_return"] - per_trade_cost).mean())
    else:
        all_bar_post_mean = 0.0

    # Matched null: random-timing on the *same* spread, same hold, same side mix,
    # post-cost via the constant two-leg cost. Build a per-seed combined mean.
    null = _combined_side_null(
        sf, n_short=n_short, n_long=n_long, window_bars=window_bars,
        seeds=seeds, per_trade_cost=per_trade_cost,
    )
    if null is None:
        null_mean, null_std, band, gns = 0.0, 0.0, "null_collapsed", None
    else:
        cmp = compare_to_null(post_mean, null)
        null_mean = float(null.mean_of_means)
        null_std = float(null.std_of_means)
        band = str(cmp["band"])
        gns = cmp["gap_in_null_stds"]

    # Filter adds edge iff thresholded post-cost mean materially beats BOTH the
    # all-bar fade and the random-timing null.
    filter_adds_edge = bool(
        post_mean > all_bar_post_mean and band in ("slightly_above_null", "materially_above_null")
    )

    notes = [
        "two-leg cost uses median-leg-price constant approximation; documented",
        "next-bar-open emulated by advancing signals one bar",
        "TRAIN window only; validation/TEST never touched",
    ]
    if "COST_HOSTILE" in cost_cell.flags:
        notes.append("spread is cost-hostile on two legs (spread_atr_ratio >= 0.25)")

    return SpreadScreenResult(
        label=f"{instrument1}-{instrument2}",
        instrument1=instrument1,
        instrument2=instrument2,
        beta=beta,
        lookback=lookback,
        threshold=threshold,
        window_bars=window_bars,
        n_bars=len(aligned),
        n_signals=n_signals,
        n_short=n_short,
        n_long=n_long,
        ar1_phi=ar1_half_life(s.to_numpy(dtype=float))["ar1_phi"],
        half_life_bars=ar1_half_life(s.to_numpy(dtype=float))["half_life_bars"],
        spread_atr_per_bar=spread_atr_per_bar,
        two_leg_cost_fraction=two_leg_cost,
        spread_atr_ratio=float(spread_atr_ratio),
        cost_flags=list(cost_cell.flags),
        pre_cost_mean=pre_mean,
        post_cost_mean=post_mean,
        all_bar_post_cost_mean=all_bar_post_mean,
        null_mean=null_mean,
        null_std=null_std,
        null_band=band,
        gap_in_null_stds=gns,
        filter_adds_edge=filter_adds_edge,
        notes=notes,
    )


def _combined_side_null(
    spread_frame: pd.DataFrame,
    *,
    n_short: int,
    n_long: int,
    window_bars: int,
    seeds: range,
    per_trade_cost: float,
) -> NullBaseline | None:
    """Random-timing matched null on the same spread, side-weighted, post-cost.

    Builds a long-side and short-side random-entry null (each is "same spread,
    same hold, random timing") and combines their per-seed means weighted by the
    actual signal counts, then subtracts the constant per-trade cost so the null
    is compared on the same post-cost footing as the study.
    """
    total = n_short + n_long
    if total == 0:
        return None
    per_seed = []
    seed_tuple = tuple(int(s) for s in seeds)
    null_short = (
        random_null_baseline(spread_frame, n_trades=max(n_short, 1), window_bars=window_bars,
                             seeds=seeds, side=Side.SHORT)
        if n_short > 0 else None
    )
    null_long = (
        random_null_baseline(spread_frame, n_trades=max(n_long, 1), window_bars=window_bars,
                             seeds=seeds, side=Side.LONG)
        if n_long > 0 else None
    )
    for i, _sd in enumerate(seed_tuple):
        sm = null_short.per_seed_means.iloc[i] if null_short is not None else 0.0
        lm = null_long.per_seed_means.iloc[i] if null_long is not None else 0.0
        combined = (n_short * sm + n_long * lm) / total - per_trade_cost
        per_seed.append(float(combined))
    arr = pd.Series(per_seed, index=list(seed_tuple), name="seed_mean")
    return NullBaseline(
        per_seed_means=arr,
        mean_of_means=float(arr.mean()),
        std_of_means=float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        n_trades_per_seed=int(total),
        window_bars=int(window_bars),
        seeds_used=seed_tuple,
    )


def candidate_pairs(instruments: list[str]) -> list[tuple[str, str]]:
    """All unordered 2-combinations of the supplied instruments (21 for the 7
    majors). Each is a candidate spread leg1-leg2."""
    return list(itertools.combinations(sorted(instruments), 2))
