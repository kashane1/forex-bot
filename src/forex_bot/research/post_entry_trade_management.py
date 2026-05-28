"""Read-only post-entry trade-management diagnostic events (USD_JPY).

These are **diagnostic event functions, not a strategy**. They never place or manage a
real trade, change a verdict, tune a parameter, or approve anything. Given the M15 path
*after* a C022 entry (bars strictly after entry, up to exit), with causal EMA/ATR
already computed, they describe post-entry behavior at a small fixed set of decision
horizons (2 / 4 / 8 / 16 M15 bars).

Liveness — every event is labelled in ``EVENT_LIVENESS``:
  * **live_manageable** — knowable in real time by horizon N while the trade is open;
    could *in principle* inform a management decision at +N bars.
  * **hindsight_only** — knowable only across the full realized path (e.g. the full
    time-to-threshold); never usable as a live management signal.
  * **descriptive** — metadata (e.g. bars-to-exit).

A horizon-N event uses only post-entry bars ``1..N`` (and only matters for trades still
open at N). No event reads bars beyond its declared horizon. Excursion R uses the
entry→initial-stop risk distance, adverse-first on intrabar ties (conservative — never
overstates how early a favorable threshold was reached).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "DEFAULT_HORIZONS",
    "EVENT_LIVENESS",
    "PostEntryParams",
    "compute_post_entry_events",
    "excursion_path",
]

DEFAULT_HORIZONS = (2, 4, 8, 16)

# event base name -> liveness class. Per-horizon variants inherit the base's class.
EVENT_LIVENESS: dict[str, str] = {
    "early_retest_hold": "live_manageable",
    "early_reclaim_failure": "live_manageable",
    "no_continuation": "live_manageable",
    "early_adverse_expansion": "live_manageable",
    "early_favorable_displacement": "live_manageable",
    "trap_or_failed_breakout": "live_manageable",
    "range_compression_after_entry": "live_manageable",
    "reached_plus_025": "live_manageable",
    "reached_plus_05": "live_manageable",
    "mae_by": "live_manageable",
    "open_at": "descriptive",
    "time_to_first_plus_025": "hindsight_only",
    "time_to_first_plus_05": "hindsight_only",
    "time_to_first_plus_10": "hindsight_only",
    "time_to_first_minus_025": "hindsight_only",
    "time_to_first_minus_05": "hindsight_only",
    "time_to_first_minus_09": "hindsight_only",
    "bars_to_exit": "descriptive",
}


@dataclass(frozen=True)
class PostEntryParams:
    """Fixed diagnostic horizons and *conventional* (non-tuned) cuts."""

    horizons: tuple[int, ...] = DEFAULT_HORIZONS
    plus_025: float = 0.25
    plus_05: float = 0.5
    plus_10: float = 1.0
    minus_025: float = 0.25
    minus_05: float = 0.5
    minus_09: float = 0.9
    retest_tol_atr: float = 0.25
    compression_atr_mult: float = 2.0  # window range <= mult*median(ATR) => "compressed"
    trap_window: int = 2


@dataclass(frozen=True)
class ExcursionPath:
    fav: list[float]          # per-bar favorable R
    adv: list[float]          # per-bar adverse R
    cum_fav: list[float]      # running max favorable R
    cum_adv: list[float]      # running min adverse R
    first_fav_bar: dict[float, int | None]  # threshold -> 1-indexed bar
    first_adv_bar: dict[float, int | None]

    def __len__(self) -> int:
        return len(self.fav)


def _sign(side: str | int | float) -> int:
    if isinstance(side, str):
        return 1 if side.strip().lower() in {"long", "buy", "b", "1"} else -1
    return 1 if float(side) >= 0 else -1


def excursion_path(
    side, entry_price: float, stop_price: float,
    highs, lows, *,
    fav_thresholds=(0.25, 0.5, 1.0), adv_thresholds=(0.25, 0.5, 0.9),
) -> ExcursionPath | None:
    """Per-bar favorable/adverse excursion (R) for post-entry bars.

    ``highs``/``lows`` are the post-entry bar extremes (strictly after entry, in order).
    Returns ``None`` if risk is zero or no bars. First-threshold bars use adverse-first
    on ties (the stop is assumed to fill before a same-bar favorable touch).
    """
    sign = _sign(side)
    risk = abs(entry_price - stop_price)
    highs = list(highs)
    lows = list(lows)
    if risk == 0 or not highs or len(highs) != len(lows):
        return None
    fav: list[float] = []
    adv: list[float] = []
    cum_fav: list[float] = []
    cum_adv: list[float] = []
    first_fav: dict[float, int | None] = dict.fromkeys(fav_thresholds, None)
    first_adv: dict[float, int | None] = dict.fromkeys(adv_thresholds, None)
    run_fav = -math.inf
    run_adv = math.inf
    for k, (h, lo) in enumerate(zip(highs, lows, strict=True), start=1):
        if sign == 1:
            f = (h - entry_price) / risk
            a = (lo - entry_price) / risk
        else:
            f = (entry_price - lo) / risk
            a = (entry_price - h) / risk
        fav.append(f)
        adv.append(a)
        run_fav = max(run_fav, f)
        run_adv = min(run_adv, a)
        cum_fav.append(run_fav)
        cum_adv.append(run_adv)
        for t in adv_thresholds:
            if first_adv[t] is None and a <= -t:
                first_adv[t] = k
        for t in fav_thresholds:
            # adverse-first: only credit a favorable threshold on a bar that did NOT
            # also breach the stop (-1.0R) for the first time here.
            if first_fav[t] is None and f >= t and not (a <= -1.0):
                first_fav[t] = k
    return ExcursionPath(fav, adv, cum_fav, cum_adv, first_fav, first_adv)


def compute_post_entry_events(
    *,
    side,
    entry_price: float,
    stop_price: float,
    post_high,
    post_low,
    post_close,
    post_ema,
    post_atr,
    params: PostEntryParams = PostEntryParams(),
) -> dict[str, object]:
    """Compute post-entry trade-management events for one trade.

    ``post_*`` are arrays for bars **strictly after entry, up to exit**, in order, with
    causal EMA/ATR values at each post bar. Returns a flat dict with per-horizon
    booleans/values keyed ``<event>_h<N>`` plus hindsight/descriptive fields. Values are
    ``None`` when unavailable (never fabricated).
    """
    sign = _sign(side)
    ph = list(post_high)
    pl = list(post_low)
    pc = list(post_close)
    pe = list(post_ema)
    pa = list(post_atr)
    n = len(pc)
    feat: dict[str, object] = {"bars_to_exit": n}

    path = excursion_path(side, entry_price, stop_price, ph, pl)
    if path is None or n == 0:
        for nbar in params.horizons:
            feat[f"open_at_h{nbar}"] = False
            for base in ("early_retest_hold", "early_reclaim_failure", "no_continuation",
                         "early_adverse_expansion", "early_favorable_displacement",
                         "range_compression_after_entry", "reached_plus_025",
                         "reached_plus_05"):
                feat[f"{base}_h{nbar}"] = None
            feat[f"mae_by_h{nbar}"] = None
        feat["trap_or_failed_breakout"] = None
        for k in ("plus_025", "plus_05", "plus_10"):
            feat[f"time_to_first_{k}"] = None
        for k in ("minus_025", "minus_05", "minus_09"):
            feat[f"time_to_first_{k}"] = None
        return feat

    def _retest_hold(eff: int) -> bool:
        for k in range(eff):
            e, a, c, lo, hi = pe[k], pa[k], pc[k], pl[k], ph[k]
            if not all(math.isfinite(x) for x in (e, a, c)):
                continue
            if sign == 1 and lo <= e + params.retest_tol_atr * a and c >= e:
                return True
            if sign == -1 and hi >= e - params.retest_tol_atr * a and c <= e:
                return True
        return False

    def _reclaim_failure_bar(eff: int) -> int | None:
        for k in range(eff):
            e, c = pe[k], pc[k]
            if not math.isfinite(e) or not math.isfinite(c):
                continue
            if (c < e) if sign == 1 else (c > e):
                return k + 1  # 1-indexed
        return None

    def _compressed(eff: int) -> bool:
        seg_h = ph[:eff]
        seg_l = pl[:eff]
        seg_a = [x for x in pa[:eff] if math.isfinite(x)]
        if not seg_h or not seg_a:
            return False
        rng = max(seg_h) - min(seg_l)
        med_atr = sorted(seg_a)[len(seg_a) // 2]
        return bool(med_atr > 0 and rng <= params.compression_atr_mult * med_atr)

    for nbar in params.horizons:
        eff = min(nbar, n)
        feat[f"open_at_h{nbar}"] = bool(n > nbar)  # still open strictly after horizon N
        cf = path.cum_fav[eff - 1]
        ca = path.cum_adv[eff - 1]
        reached_025 = cf >= params.plus_025
        reached_05 = cf >= params.plus_05
        feat[f"reached_plus_025_h{nbar}"] = bool(reached_025)
        feat[f"reached_plus_05_h{nbar}"] = bool(reached_05)
        feat[f"mae_by_h{nbar}"] = round(float(ca), 6)
        feat[f"no_continuation_h{nbar}"] = bool(not reached_025)
        feat[f"early_favorable_displacement_h{nbar}"] = bool(reached_025 and ca > -params.minus_05)
        # adverse before favorable, within N
        fa = path.first_adv_bar[params.minus_05]
        ff = path.first_fav_bar[params.plus_025]
        adv_first = fa is not None and fa <= eff and (ff is None or fa < ff)
        feat[f"early_adverse_expansion_h{nbar}"] = bool(adv_first)
        feat[f"early_retest_hold_h{nbar}"] = _retest_hold(eff)
        feat[f"early_reclaim_failure_h{nbar}"] = bool(_reclaim_failure_bar(eff) is not None)
        feat[f"range_compression_after_entry_h{nbar}"] = _compressed(eff)

    # trap: reclaim invalidated within the first trap_window bars, before any +0.25R.
    tw = min(params.trap_window, n)
    fail_bar = _reclaim_failure_bar(tw)
    ff025 = path.first_fav_bar[params.plus_025]
    feat["trap_or_failed_breakout"] = bool(
        fail_bar is not None and (ff025 is None or fail_bar <= ff025)
    )

    # hindsight: full time-to-threshold (bars; None if never reached on the path).
    feat["time_to_first_plus_025"] = path.first_fav_bar[params.plus_025]
    feat["time_to_first_plus_05"] = path.first_fav_bar[params.plus_05]
    feat["time_to_first_plus_10"] = path.first_fav_bar[params.plus_10]
    feat["time_to_first_minus_025"] = path.first_adv_bar[params.minus_025]
    feat["time_to_first_minus_05"] = path.first_adv_bar[params.minus_05]
    feat["time_to_first_minus_09"] = path.first_adv_bar[params.minus_09]
    return feat


def liveness_of(column: str) -> str:
    """Classify a feature column by its event base name."""
    if column.startswith("open_at_h"):
        return "descriptive"
    base = column
    if "_h" in column:
        base = column.rsplit("_h", 1)[0]
    return EVENT_LIVENESS.get(base, "descriptive")
