"""Matched-null benchmarks for the edge-discovery lab.

The generic ``null.py`` baseline draws *uniform random* entries from a single
candle frame. That answers "is this study better than picking random bars on
one pair?" — but a real strategy ledger has structure (a pair mix, a long/short
mix, a session/weekday concentration, a holding-period distribution) and a fair
null must reproduce that structure before randomizing the rest. Otherwise a
"beats null" result can be an artifact of *which pairs/sessions the strategy
happened to trade*, not of timing skill.

This module builds **sample-matched** nulls from a trade/signal ledger plus the
per-pair candle frames the ledger's pairs were drawn from. For each null mode
it preserves some structure and randomizes the rest, then computes the null
distribution of mean forward log-return across seeds and compares the
strategy's *own* mean forward log-return (computed identically from the same
frames) against it.

Everything is measured in one metric — signed forward **log-return** over a
window — so the strategy and the null are directly comparable. The ledger does
not need to carry returns; they are derived from the frames at the ledger's
entry timestamps. (A real campaign ledger that only carries ``r_multiple`` and
no frames is therefore a compatibility gap, documented in the retrospective.)

Null modes (``MATCHED_NULL_MODES``):

  1. ``timestamp_random_same_pair`` — preserve per-pair trade counts; draw
     uniform random entries within each pair's frame. Side per pair = the
     pair's majority real side. Randomizes timing only.
  2. ``side_shuffled`` — keep the *real* entry bars exactly; randomly permute
     the long/short labels (preserving long/short counts). Isolates whether the
     direction assignment carries information beyond the entries themselves.
  3. ``pair_matched_random`` — preserve per-(pair, side) counts; draw uniform
     random entries within each pair. Randomizes timing, preserves pair+side
     mix.
  4. ``session_matched_random`` — preserve per-(pair, side, session) counts;
     draw random entries only from bars in the matching UTC session bucket.
  5. ``holding_period_matched_random`` — preserve per-(pair, side) counts; draw
     random entries and assign each the forward window sampled from the pair's
     *real* holding-bar distribution (rather than a single fixed window).
  6. ``full_matched_null`` — preserve per-(pair, side, session, weekday) counts
     and the per-pair holding-bar distribution simultaneously, as far as the
     available bars allow.

The output is descriptive: null distribution statistics, the strategy's
percentile within the null, P(null >= strategy), and an effect size. It never
emits a verdict word and never claims statistical significance.

Import-isolated: imports only from ``research.edge_discovery`` and numpy/pandas
(plus ``forex_bot.financing`` transitively via the cost overlay).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

MATCHED_NULL_MODES = (
    "timestamp_random_same_pair",
    "side_shuffled",
    "pair_matched_random",
    "session_matched_random",
    "holding_period_matched_random",
    "full_matched_null",
)

# Modes that preserve session structure (need a session mask per draw).
_SESSION_MODES = frozenset({"session_matched_random", "full_matched_null"})
# Modes that preserve weekday structure.
_WEEKDAY_MODES = frozenset({"full_matched_null"})
# Modes that match the per-pair holding-bar distribution instead of one window.
_HOLD_MODES = frozenset({"holding_period_matched_random", "full_matched_null"})

_LONG = "long"
_SHORT = "short"


def session_bucket_utc(ts: pd.Timestamp) -> str:
    """UTC-hour session bucket (self-contained; mirrors the lab convention).

    asia [0,7) · london [7,12) · london_ny_overlap [12,16) · new_york
    [16,21) · late [21,24).
    """
    h = int(ts.hour)
    if 0 <= h < 7:
        return "asia"
    if 7 <= h < 12:
        return "london"
    if 12 <= h < 16:
        return "london_ny_overlap"
    if 16 <= h < 21:
        return "new_york"
    return "late"


def weekday_utc(ts: pd.Timestamp) -> str:
    """Mon..Sun label from a UTC timestamp."""
    return ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[int(ts.weekday())]


def _normalize_side(value: object) -> str:
    """Map a side value (``'long'``/``'short'``/``+1``/``-1``/``'buy'``...) to
    ``'long'``/``'short'``."""
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("long", "buy", "+1", "1", "l"):
            return _LONG
        if v in ("short", "sell", "-1", "s"):
            return _SHORT
        raise ValueError(f"unrecognized side label {value!r}")
    iv = int(value)
    if iv > 0:
        return _LONG
    if iv < 0:
        return _SHORT
    raise ValueError("side value 0 is ambiguous; use long/short")


def _sign_of(side: str) -> float:
    return 1.0 if side == _LONG else -1.0


@dataclass(frozen=True)
class MatchedNullResult:
    """Matched-null distribution and strategy comparison for one mode.

    ``per_seed_means`` is one mean forward log-return per seed (post-cost when a
    cost overlay is supplied). ``strategy_expectancy`` is the strategy's own
    mean forward log-return computed identically from the same frames.
    """

    mode: str
    metric: str
    n_trades: int
    window_bars: int | None
    strategy_expectancy: float
    per_seed_means: pd.Series
    null_mean: float
    null_median: float
    null_std: float
    null_p05: float
    null_p95: float
    prob_null_ge_strategy: float
    strategy_percentile: float
    effect_size: float | None
    seeds_used: tuple[int, ...]
    matched_keys: tuple[str, ...]
    sparse_buckets: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    extras: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "metric": self.metric,
            "n_trades": self.n_trades,
            "window_bars": self.window_bars,
            "strategy_expectancy": self.strategy_expectancy,
            "null_distribution": {
                "mean": self.null_mean,
                "median": self.null_median,
                "std": self.null_std,
                "p05": self.null_p05,
                "p95": self.null_p95,
                "n_seeds": len(self.seeds_used),
            },
            "prob_null_ge_strategy": self.prob_null_ge_strategy,
            "strategy_percentile": self.strategy_percentile,
            "effect_size": self.effect_size,
            "seeds_used": list(self.seeds_used),
            "matched_keys": list(self.matched_keys),
            "sparse_buckets": list(self.sparse_buckets),
            "notes": list(self.notes),
        }


# ---------------------------------------------------------------------------
# Ledger preparation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _PreparedTrade:
    pair: str
    side: str
    entry_idx: int
    session: str
    weekday: str
    hold_bars: int


def _prepare_ledger(
    ledger: pd.DataFrame,
    frames_by_pair: Mapping[str, pd.DataFrame],
    *,
    pair_col: str,
    side_col: str,
    time_col: str,
    hold_col: str | None,
    default_window: int,
) -> tuple[list[_PreparedTrade], list[str]]:
    """Resolve each ledger row to a bar index in its pair's frame, plus the
    session/weekday/hold metadata used for matching.

    Rows whose pair has no frame, or whose entry time is past the frame's end,
    are dropped and reported in the returned notes list.
    """
    for col in (pair_col, side_col, time_col):
        if col not in ledger.columns:
            raise ValueError(f"ledger missing required column {col!r}")
    notes: list[str] = []
    prepared: list[_PreparedTrade] = []
    for _, row in ledger.iterrows():
        pair = str(row[pair_col])
        frame = frames_by_pair.get(pair)
        if frame is None or frame.empty or "close" not in frame.columns:
            notes.append(f"dropped trade on {pair}: no usable frame")
            continue
        side = _normalize_side(row[side_col])
        when = pd.Timestamp(row[time_col])
        when = when.tz_convert("UTC") if when.tzinfo else when.tz_localize("UTC")
        pos = int(frame.index.searchsorted(when, side="left"))
        if pos >= len(frame.index):
            notes.append(f"dropped trade on {pair}: entry time past frame end")
            continue
        ts = frame.index[pos]
        if hold_col is not None and hold_col in ledger.columns and not pd.isna(row[hold_col]):
            hold = max(1, int(row[hold_col]))
        else:
            hold = int(default_window)
        prepared.append(
            _PreparedTrade(
                pair=pair,
                side=side,
                entry_idx=pos,
                session=session_bucket_utc(ts),
                weekday=weekday_utc(ts),
                hold_bars=hold,
            )
        )
    return prepared, notes


# ---------------------------------------------------------------------------
# Forward-return helpers (log-return space, signed by side)
# ---------------------------------------------------------------------------


def _signed_log_return(
    closes: np.ndarray,
    entry_idx: np.ndarray,
    window: np.ndarray,
    sign: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized signed log-return for entry indices with per-trade windows.

    Returns ``(returns, entry_prices, windows)`` for the trades whose exit bar
    exists and whose prices are positive — all three arrays aligned to the same
    surviving trades; trades that fall off the end are excluded.
    """
    exit_idx = entry_idx + window
    n = len(closes)
    valid = exit_idx < n
    ei = entry_idx[valid]
    xi = exit_idx[valid]
    sg = sign[valid]
    wv = window[valid]
    ep = closes[ei]
    xp = closes[xi]
    good = (ep > 0) & (xp > 0)
    ret = np.log(xp[good] / ep[good]) * sg[good]
    return ret, ep[good], wv[good]


def _apply_cost(
    ret: np.ndarray,
    entry_prices: np.ndarray,
    window: np.ndarray,
    *,
    instrument: str,
    apply_cost_overlay_fn,
    cost_kwargs: dict | None,
) -> np.ndarray:
    if apply_cost_overlay_fn is None or len(ret) == 0:
        return ret
    df = pd.DataFrame(
        {
            "entry_price": entry_prices,
            "log_return": ret,
            "bars_held": window.astype(int),
        }
    )
    out = apply_cost_overlay_fn(df, instrument, **(cost_kwargs or {}))
    return out["log_return_post_cost"].to_numpy(dtype=float)


def _strategy_expectancy(
    prepared: list[_PreparedTrade],
    frames_by_pair: Mapping[str, pd.DataFrame],
    *,
    window_bars: int,
    use_hold: bool,
    apply_cost_overlay_fn,
    cost_kwargs: dict | None,
) -> tuple[float, int]:
    """Mean forward log-return of the *real* trades (entries fixed, signed by
    real side). Returns ``(mean, n_used)``."""
    rets: list[np.ndarray] = []
    for pair, frame in frames_by_pair.items():
        rows = [t for t in prepared if t.pair == pair]
        if not rows:
            continue
        closes = frame["close"].to_numpy(dtype=float)
        ei = np.array([t.entry_idx for t in rows], dtype=int)
        win = np.array([t.hold_bars if use_hold else window_bars for t in rows], dtype=int)
        sg = np.array([_sign_of(t.side) for t in rows], dtype=float)
        ret, ep, wv = _signed_log_return(closes, ei, win, sg)
        ret = _apply_cost(
            ret, ep, wv,
            instrument=pair,
            apply_cost_overlay_fn=apply_cost_overlay_fn,
            cost_kwargs=cost_kwargs,
        )
        rets.append(ret)
    if not rets:
        return 0.0, 0
    allret = np.concatenate(rets) if rets else np.array([])
    return (float(allret.mean()) if len(allret) else 0.0), len(allret)


# ---------------------------------------------------------------------------
# Null draw
# ---------------------------------------------------------------------------


def _bucket_key(t: _PreparedTrade, mode: str) -> tuple:
    key: list[object] = [t.pair]
    if mode in ("pair_matched_random", "session_matched_random", "full_matched_null",
                "holding_period_matched_random"):
        key.append(t.side)
    if mode in _SESSION_MODES:
        key.append(t.session)
    if mode in _WEEKDAY_MODES:
        key.append(t.weekday)
    return tuple(key)


def _pool_mask(
    frame: pd.DataFrame,
    *,
    session: str | None,
    weekday: str | None,
    max_entry: int,
) -> np.ndarray:
    """Boolean mask over entry indices [0, max_entry] restricted to bars in the
    requested session/weekday bucket."""
    idx = frame.index[: max_entry + 1]
    mask = np.ones(len(idx), dtype=bool)
    if session is not None:
        mask &= np.array([session_bucket_utc(ts) == session for ts in idx], dtype=bool)
    if weekday is not None:
        mask &= np.array([weekday_utc(ts) == weekday for ts in idx], dtype=bool)
    return mask


def _draw_null_means(
    prepared: list[_PreparedTrade],
    frames_by_pair: Mapping[str, pd.DataFrame],
    *,
    mode: str,
    window_bars: int,
    seeds: tuple[int, ...],
    apply_cost_overlay_fn,
    cost_kwargs: dict | None,
    min_bucket: int,
) -> tuple[pd.Series, list[str]]:
    """One mean forward log-return per seed under the matched null.

    Returns ``(per_seed_means, sparse_buckets)``.
    """
    use_hold = mode in _HOLD_MODES
    if mode == "side_shuffled":
        return _draw_side_shuffled(
            prepared, frames_by_pair,
            window_bars=window_bars, seeds=seeds,
            apply_cost_overlay_fn=apply_cost_overlay_fn, cost_kwargs=cost_kwargs,
        ), []
    # Group trades into matched buckets; each bucket draws ``count`` random
    # entries from its pair's frame, restricted to the matching session/weekday.
    buckets: dict[tuple, list[_PreparedTrade]] = {}
    for t in prepared:
        buckets.setdefault(_bucket_key(t, mode), []).append(t)

    sparse: list[str] = []
    # Pre-resolve, per bucket, the candidate entry-index pool and the per-trade
    # window sample source — independent of seed.
    bucket_plans = []
    for key in sorted(buckets, key=lambda k: tuple(str(x) for x in k)):
        rows = buckets[key]
        pair = rows[0].pair
        frame = frames_by_pair[pair]
        closes = frame["close"].to_numpy(dtype=float)
        n = len(closes)
        # Largest window we may need (hold distribution or fixed window).
        hold_samples = np.array([t.hold_bars for t in rows], dtype=int) if use_hold else None
        max_win = int(hold_samples.max()) if use_hold and len(hold_samples) else int(window_bars)
        max_entry = n - max_win - 1
        if max_entry < 0:
            sparse.append(f"{key}: frame too short for window {max_win}")
            continue
        session = rows[0].session if mode in _SESSION_MODES else None
        weekday = rows[0].weekday if mode in _WEEKDAY_MODES else None
        mask = _pool_mask(frame, session=session, weekday=weekday, max_entry=max_entry)
        pool = np.nonzero(mask)[0]
        if len(pool) < max(min_bucket, 1):
            sparse.append(f"{key}: only {len(pool)} candidate bars (<{min_bucket})")
            if len(pool) == 0:
                continue
        sign = _sign_of(rows[0].side) if mode != "timestamp_random_same_pair" else _majority_sign(rows)
        bucket_plans.append(
            {
                "key": key,
                "closes": closes,
                "pool": pool,
                "count": len(rows),
                "sign": sign,
                "fixed_window": int(window_bars),
                "hold_samples": hold_samples,
                "use_hold": use_hold,
                "pair": pair,
            }
        )

    per_seed: list[float] = []
    for s in seeds:
        rng = np.random.default_rng(s)
        seed_rets: list[np.ndarray] = []
        for plan in bucket_plans:
            pool = plan["pool"]
            count = plan["count"]
            draws = rng.integers(0, len(pool), size=count)
            entry_idx = pool[draws]
            if plan["use_hold"] and plan["hold_samples"] is not None and len(plan["hold_samples"]):
                win = rng.choice(plan["hold_samples"], size=count, replace=True).astype(int)
            else:
                win = np.full(count, plan["fixed_window"], dtype=int)
            sign = np.full(count, plan["sign"], dtype=float)
            ret, ep, wv = _signed_log_return(plan["closes"], entry_idx, win, sign)
            ret = _apply_cost(
                ret, ep, wv,
                instrument=plan["pair"],
                apply_cost_overlay_fn=apply_cost_overlay_fn,
                cost_kwargs=cost_kwargs,
            )
            if len(ret):
                seed_rets.append(ret)
        if seed_rets:
            allret = np.concatenate(seed_rets)
            per_seed.append(float(allret.mean()))
        else:
            per_seed.append(0.0)
    return pd.Series(per_seed, index=list(seeds), name="seed_mean"), sparse


def _majority_sign(rows: list[_PreparedTrade]) -> float:
    longs = sum(1 for t in rows if t.side == _LONG)
    return 1.0 if longs >= (len(rows) - longs) else -1.0


def _draw_side_shuffled(
    prepared: list[_PreparedTrade],
    frames_by_pair: Mapping[str, pd.DataFrame],
    *,
    window_bars: int,
    seeds: tuple[int, ...],
    apply_cost_overlay_fn,
    cost_kwargs: dict | None,
) -> pd.Series:
    """Keep the real entry bars; permute long/short labels each seed."""
    # Pre-resolve per-pair arrays of real entry indices and windows.
    pair_blocks = []
    real_signs: list[float] = []
    for t in prepared:
        real_signs.append(_sign_of(t.side))
    for pair, frame in frames_by_pair.items():
        rows = [t for t in prepared if t.pair == pair]
        if not rows:
            continue
        closes = frame["close"].to_numpy(dtype=float)
        ei = np.array([t.entry_idx for t in rows], dtype=int)
        win = np.array([window_bars] * len(rows), dtype=int)
        pair_blocks.append({"pair": pair, "closes": closes, "ei": ei, "win": win, "rows": rows})

    n = len(prepared)
    base_signs = np.array(real_signs, dtype=float)
    per_seed: list[float] = []
    for s in seeds:
        rng = np.random.default_rng(s)
        perm = rng.permutation(n)
        shuffled = base_signs[perm]
        # Map shuffled signs back to trades in original order, then per pair.
        sign_by_trade = {id(t): shuffled[i] for i, t in enumerate(prepared)}
        seed_rets: list[np.ndarray] = []
        for blk in pair_blocks:
            sg = np.array([sign_by_trade[id(t)] for t in blk["rows"]], dtype=float)
            ret, ep, vw = _signed_log_return(blk["closes"], blk["ei"], blk["win"], sg)
            ret = _apply_cost(
                ret, ep, vw, instrument=blk["pair"],
                apply_cost_overlay_fn=apply_cost_overlay_fn, cost_kwargs=cost_kwargs,
            )
            if len(ret):
                seed_rets.append(ret)
        per_seed.append(float(np.concatenate(seed_rets).mean()) if seed_rets else 0.0)
    return pd.Series(per_seed, index=list(seeds), name="seed_mean")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def matched_null_baseline(
    ledger: pd.DataFrame,
    frames_by_pair: Mapping[str, pd.DataFrame],
    *,
    mode: str,
    window_bars: int,
    seeds: Iterable[int] = range(20),
    pair_col: str = "instrument",
    side_col: str = "side",
    time_col: str = "entry_time",
    hold_col: str | None = "bars_held",
    apply_cost_overlay_fn=None,
    cost_kwargs: dict | None = None,
    min_bucket: int = 5,
) -> MatchedNullResult:
    """Build a sample-matched null and compare the strategy to it.

    ``ledger`` rows need ``pair_col``/``side_col``/``time_col``; ``hold_col`` is
    used only by holding-period-matched modes (falls back to ``window_bars``).
    ``frames_by_pair`` maps each pair to its UTC-indexed candle frame (a
    ``close`` column, as produced by ``loaders.load_candles_csv`` /
    ``real_data.load_h4_candles_from_sqlite``).

    Pass ``apply_cost_overlay_fn=research.edge_discovery.costs.apply_cost_overlay``
    to measure post-cost; both strategy and null then pay the same overlay.
    """
    if mode not in MATCHED_NULL_MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {MATCHED_NULL_MODES}")
    if window_bars < 1:
        raise ValueError(f"window_bars must be >= 1, got {window_bars}")
    if ledger is None or ledger.empty:
        raise ValueError("ledger is empty; nothing to benchmark")
    seed_tuple = tuple(int(s) for s in seeds)
    if not seed_tuple:
        raise ValueError("seeds must be non-empty")

    use_hold = mode in _HOLD_MODES
    prepared, prep_notes = _prepare_ledger(
        ledger, frames_by_pair,
        pair_col=pair_col, side_col=side_col, time_col=time_col,
        hold_col=hold_col, default_window=window_bars,
    )
    if not prepared:
        raise ValueError(
            "no ledger rows resolved to a usable frame bar; "
            f"check pair/time alignment ({'; '.join(prep_notes[:3])})"
        )

    strat_mean, n_used = _strategy_expectancy(
        prepared, frames_by_pair,
        window_bars=window_bars, use_hold=use_hold,
        apply_cost_overlay_fn=apply_cost_overlay_fn, cost_kwargs=cost_kwargs,
    )

    per_seed, sparse = _draw_null_means(
        prepared, frames_by_pair,
        mode=mode, window_bars=window_bars, seeds=seed_tuple,
        apply_cost_overlay_fn=apply_cost_overlay_fn, cost_kwargs=cost_kwargs,
        min_bucket=min_bucket,
    )

    null_mean = float(per_seed.mean())
    null_std = float(per_seed.std(ddof=1)) if len(per_seed) > 1 else 0.0
    prob_ge = float((per_seed.to_numpy() >= strat_mean).mean())
    pctl = float((per_seed.to_numpy() < strat_mean).mean() * 100.0)
    effect = None if null_std == 0 else (strat_mean - null_mean) / null_std

    matched_keys = _matched_keys_for_mode(mode)
    notes = list(prep_notes)
    if use_hold:
        notes.append("forward window per null trade sampled from the pair's real hold-bar distribution")

    return MatchedNullResult(
        mode=mode,
        metric="forward_log_return_post_cost" if apply_cost_overlay_fn else "forward_log_return",
        n_trades=int(n_used),
        window_bars=None if use_hold else int(window_bars),
        strategy_expectancy=strat_mean,
        per_seed_means=per_seed,
        null_mean=null_mean,
        null_median=float(per_seed.median()),
        null_std=null_std,
        null_p05=float(per_seed.quantile(0.05)),
        null_p95=float(per_seed.quantile(0.95)),
        prob_null_ge_strategy=prob_ge,
        strategy_percentile=pctl,
        effect_size=effect,
        seeds_used=seed_tuple,
        matched_keys=matched_keys,
        sparse_buckets=sparse,
        notes=notes,
        extras={"prepared_trades": len(prepared)},
    )


def _matched_keys_for_mode(mode: str) -> tuple[str, ...]:
    keys = ["pair"]
    if mode != "timestamp_random_same_pair":
        keys.append("side")
    if mode in _SESSION_MODES:
        keys.append("session")
    if mode in _WEEKDAY_MODES:
        keys.append("weekday")
    if mode in _HOLD_MODES:
        keys.append("hold_bars")
    if mode == "side_shuffled":
        return ("entry_bars_fixed", "side_counts")
    return tuple(keys)


def interpret_matched_null(result: MatchedNullResult) -> dict[str, object]:
    """Descriptive interpretation flags — never a verdict.

    Flags:
      - ``BEATS_MATCHED_NULL`` — strategy mean > null p95 (top 5% of null draws)
      - ``ABOVE_MATCHED_NULL`` — strategy above null mean but within p95
      - ``WITHIN_MATCHED_NULL`` — strategy within the bulk of the null
      - ``BELOW_MATCHED_NULL`` — strategy below the null mean
      - ``MATCHED_NULL_SPARSE`` — one or more buckets were too sparse to match
        faithfully (interpret with caution)
    """
    flags: list[str] = []
    s = result.strategy_expectancy
    if result.sparse_buckets:
        flags.append("MATCHED_NULL_SPARSE")
    if s > result.null_p95:
        flags.append("BEATS_MATCHED_NULL")
    elif s > result.null_mean:
        flags.append("ABOVE_MATCHED_NULL")
    elif s < result.null_mean:
        flags.append("BELOW_MATCHED_NULL")
    else:
        flags.append("WITHIN_MATCHED_NULL")
    return {
        "mode": result.mode,
        "flags": flags,
        "strategy_expectancy": s,
        "null_mean": result.null_mean,
        "null_p95": result.null_p95,
        "prob_null_ge_strategy": result.prob_null_ge_strategy,
        "strategy_percentile": result.strategy_percentile,
        "effect_size": result.effect_size,
    }
