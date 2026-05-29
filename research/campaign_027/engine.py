"""CAMPAIGN_027 train/validation execution engine (frozen rule, no tuning).

Simulates the **single frozen candidate** from the precommit on the campaign's
own H4 ledgers and emits edge-discovery-compatible artifacts. Two parallel views,
deliberately separated (see the plan's compatibility note):

  * **Signal / funnel ledger** — base-trigger ``|z| >= 2.0`` decisions, BOTH sides
    (long rows are diagnostic-only, ``entered=false``), each carrying a
    **fixed-horizon h12 close-to-close** value proxy signed toward the mean. This
    is the front-gate-comparable ``filter_ablation`` input and the matched-null
    timing/direction information benchmark.
  * **Trade ledger** — realized **short-only** trades: ``next_bar_open`` entry,
    wide 3xATR protective stop (adverse wins a same-bar tie), 12-bar time stop,
    optimistic + conservative (binding) post-cost, R-multiple. This drives the
    expectancy / profit-factor / recency gates.

The z / ATR / ATR-percentile formulas are computed inline and are **identical** to
``forex_bot.strategies.h4_filtered_zscore_reversion.compute_decision`` (shift-1,
ddof=1, simple-mean ATR) and to the lab engine that produced the front-gate
evidence — a parity test pins this.

No broker / executor / approval import. Nothing here approves a strategy, tunes a
parameter, or reads the sealed test window (the caller passes window bounds and
the self-contained-completion policy keeps every trade inside its split).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from research.edge_discovery.costs import (  # noqa: E402
    apply_cost_overlay,
    financing_stress_fraction,
    pip_value_for,
)
from research.edge_discovery.filter_ablation import filter_ablation  # noqa: E402
from research.edge_discovery.matched_nulls import (  # noqa: E402
    interpret_matched_null,
    matched_null_baseline,
    session_bucket_utc,
)

# Front-gate filter order (cumulative_order), reused verbatim for ablation parity.
ABLATION_FILTERS = ["f_low_vol", "f_strong_extension", "f_quiet_session", "f_cost_adv_pair", "f_long_side"]
# Matched-null modes we run on the campaign's own ledger. ``side_shuffled`` is
# degenerate for a single-side (short-only) ledger and is reported with a note.
MATCHED_NULL_MODES_RUN = (
    "timestamp_random_same_pair",
    "session_matched_random",
    "full_matched_null",
    "side_shuffled",
)

# Frozen parameters (mirror the precommit; the runner re-asserts them from config).
SEVEN_MAJORS = ("EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD")
COST_ADVANTAGED = frozenset({"USD_JPY", "GBP_USD", "AUD_USD", "EUR_USD"})
SLIP_PIPS = 0.2
HOURS_PER_BAR = 4.0
# Conservative (binding) cost knobs.
CONS_SPREAD_PIPS = 1.5
QUIET_SESSIONS = ("asia", "london")


@dataclass(frozen=True)
class FrozenParams:
    zscore_lookback: int = 20
    zscore_std_ddof: int = 1
    base_trigger_abs_z: float = 2.0
    strong_extension_abs_z: float = 2.5
    atr_lookback: int = 14
    atr_percentile_window: int = 250
    atr_percentile_max: float = 0.33
    atr_stop_multiple: float = 3.0
    max_bars_in_trade: int = 12
    quiet_sessions: tuple[str, ...] = QUIET_SESSIONS


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_BIDASK = ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c")


def load_pair_frame(db_path: Path, instrument: str) -> pd.DataFrame:
    """Completed H4 candles for one instrument: UTC-indexed mid OHLC + per-bar
    spread (open and close), read-only. ``spread_open`` is the realized bid/ask
    spread at the bar open (used for the optimistic entry-cost diagnostic)."""
    import sqlite3

    query = (
        "SELECT time, bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c, volume "
        "FROM candles WHERE instrument = ? AND granularity = 'H4' AND complete = 1 "
        "ORDER BY time ASC"
    )
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        df = pd.read_sql_query(query, conn, params=[instrument])
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"], utc=True)
    for col in _BIDASK:
        df[col] = df[col].astype(float)
    df = df.sort_values("time").drop_duplicates("time", keep="last").set_index("time")
    out = pd.DataFrame(index=df.index)
    out["open"] = (df["bid_o"] + df["ask_o"]) / 2.0
    out["high"] = (df["bid_h"] + df["ask_h"]) / 2.0
    out["low"] = (df["bid_l"] + df["ask_l"]) / 2.0
    out["close"] = (df["bid_c"] + df["ask_c"]) / 2.0
    out["spread_open"] = (df["ask_o"] - df["bid_o"]).abs()
    out["spread_close"] = (df["ask_c"] - df["bid_c"]).abs()
    return out


# ---------------------------------------------------------------------------
# Features (vectorized; identical formulas to the frozen strategy module)
# ---------------------------------------------------------------------------


def compute_features(df: pd.DataFrame, p: FrozenParams) -> pd.DataFrame:
    """Add z, atr14, atr_percentile, session and filter booleans. No lookahead:
    mean/std and the ATR percentile are ``.shift(1)``."""
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)

    mean = close.rolling(window=p.zscore_lookback, min_periods=p.zscore_lookback).mean().shift(1)
    std = (
        close.rolling(window=p.zscore_lookback, min_periods=p.zscore_lookback)
        .std(ddof=p.zscore_std_ddof)
        .shift(1)
    )
    z = (close - mean) / std

    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    atr = tr.rolling(window=p.atr_lookback, min_periods=p.atr_lookback).mean()
    atr_pct = (
        atr.rolling(window=p.atr_percentile_window, min_periods=p.atr_percentile_window)
        .apply(lambda a: float((a[-1] >= a).mean()), raw=True)
        .shift(1)
    )

    feat = pd.DataFrame(index=df.index)
    feat["close"] = close
    feat["high"] = high
    feat["open"] = df["open"].astype(float)
    feat["spread_open"] = df["spread_open"].astype(float)
    feat["zscore"] = z
    feat["atr14"] = atr
    feat["atr_percentile"] = atr_pct
    feat["session_bucket"] = [session_bucket_utc(ts) for ts in df.index]
    feat["base_trigger"] = z.abs() >= p.base_trigger_abs_z
    feat["f_strong_extension"] = z.abs() >= p.strong_extension_abs_z
    feat["f_low_vol"] = atr_pct <= p.atr_percentile_max
    feat["f_quiet_session"] = feat["session_bucket"].isin(p.quiet_sessions)
    feat["raw_side"] = np.where(z > 0, "short", "long")
    return feat


# ---------------------------------------------------------------------------
# Signal / funnel ledger (base trigger, both sides, fixed-horizon h12 proxy)
# ---------------------------------------------------------------------------


def build_signal_rows(
    feat: pd.DataFrame,
    instrument: str,
    *,
    window_start: pd.Timestamp,
    window_end: pd.Timestamp,
    split: str,
    p: FrozenParams,
) -> list[dict]:
    """One row per base-trigger (``|z|>=2.0``) signal whose decision bar is in
    [window_start, window_end]. Includes diagnostic long rows. The value proxy is
    the front-gate-comparable fixed-horizon h12 close-to-close signed return; it
    is filled only when bar ``t+12`` is also within the window (else left NaN)."""
    idx = feat.index
    close = feat["close"].to_numpy(dtype=float)
    z = feat["zscore"].to_numpy(dtype=float)
    n = len(idx)
    pip = pip_value_for(instrument)
    slip_px = SLIP_PIPS * pip
    in_win = (idx >= window_start) & (idx <= window_end)
    rows: list[dict] = []
    h = p.max_bars_in_trade
    for i in range(n):
        if not in_win[i]:
            continue
        zv = z[i]
        if not np.isfinite(zv) or abs(zv) < p.base_trigger_abs_z:
            continue
        side = "short" if zv > 0 else "long"
        sign = -1.0 if side == "short" else 1.0  # toward the mean
        log_ret = log_ret_cost_opt = log_ret_cost_cons = r_mult = np.nan
        if i + h < n and idx[i + h] <= window_end:
            entry, exit_ = close[i], close[i + h]
            if entry > 0 and exit_ > 0:
                signed = sign * float(np.log(exit_ / entry))
                cost_opt = (float(feat["spread_open"].to_numpy()[i]) + 2 * slip_px) / entry
                cost_cons = (CONS_SPREAD_PIPS * pip + 2 * slip_px) / entry + financing_stress_fraction(
                    instrument, bars_held=h, hours_per_bar=HOURS_PER_BAR
                )
                risk_frac = p.atr_stop_multiple * float(feat["atr14"].to_numpy()[i]) / entry
                log_ret = signed
                log_ret_cost_opt = signed - cost_opt
                log_ret_cost_cons = signed - cost_cons
                r_mult = signed / risk_frac if risk_frac > 0 else np.nan
        entered = bool(
            side == "short"
            and feat["f_strong_extension"].to_numpy()[i]
            and feat["f_low_vol"].to_numpy()[i]
            and feat["f_quiet_session"].to_numpy()[i]
            and i + h + 1 < n
            and idx[i + h + 1] <= window_end
        )
        rows.append(
            {
                "instrument": instrument,
                "split": split,
                "signal_time_utc": idx[i].isoformat(),
                "year": int(idx[i].year),
                "timeframe": "H4",
                "side": side,
                "zscore": round(float(zv), 6),
                "atr14": round(float(feat["atr14"].to_numpy()[i]), 8),
                "atr_percentile": round(float(feat["atr_percentile"].to_numpy()[i]), 6),
                "session_bucket": str(feat["session_bucket"].to_numpy()[i]),
                "trigger": True,
                "f_low_vol": bool(feat["f_low_vol"].to_numpy()[i]),
                "f_strong_extension": bool(feat["f_strong_extension"].to_numpy()[i]),
                "f_quiet_session": bool(feat["f_quiet_session"].to_numpy()[i]),
                "f_cost_adv_pair": instrument in COST_ADVANTAGED,
                "f_long_side": side == "long",
                "f_low_vol_pass": bool(feat["f_low_vol"].to_numpy()[i]),
                "f_strong_extension_pass": bool(feat["f_strong_extension"].to_numpy()[i]),
                "f_quiet_session_pass": bool(feat["f_quiet_session"].to_numpy()[i]),
                "log_return": None if np.isnan(log_ret) else round(float(log_ret), 8),
                "log_return_post_cost": None if np.isnan(log_ret_cost_opt) else round(float(log_ret_cost_opt), 8),
                "log_return_post_cost_conservative": None
                if np.isnan(log_ret_cost_cons)
                else round(float(log_ret_cost_cons), 8),
                "r_multiple": None if np.isnan(r_mult) else round(float(r_mult), 6),
                "entered": entered,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Trade ledger (realized short-only; next_bar_open + 3xATR stop + 12-bar time stop)
# ---------------------------------------------------------------------------


def simulate_trades(
    feat: pd.DataFrame,
    instrument: str,
    *,
    window_start: pd.Timestamp,
    window_end: pd.Timestamp,
    split: str,
    p: FrozenParams,
) -> tuple[list[dict], int]:
    """Realized short-only trades. Entry at open[t+1]; protective stop at
    entry + 3xATR(14)_at_signal scanned over bars t+1..t+12 (adverse wins a
    same-bar tie); otherwise time stop at open[t+13]. A signal is entered only if
    bar t+13 exists and lies within the window (self-contained completion).
    Returns ``(trades, dropped_trailing)`` where ``dropped_trailing`` counts
    entry-eligible short signals skipped solely because they could not complete
    in-window."""
    idx = feat.index
    o = feat["open"].to_numpy(dtype=float)
    hi = feat["high"].to_numpy(dtype=float)
    z = feat["zscore"].to_numpy(dtype=float)
    atr = feat["atr14"].to_numpy(dtype=float)
    spread_open = feat["spread_open"].to_numpy(dtype=float)
    strong = feat["f_strong_extension"].to_numpy()
    low_vol = feat["f_low_vol"].to_numpy()
    quiet = feat["f_quiet_session"].to_numpy()
    n = len(idx)
    pip = pip_value_for(instrument)
    slip_px = SLIP_PIPS * pip
    h = p.max_bars_in_trade
    in_win = (idx >= window_start) & (idx <= window_end)

    trades: list[dict] = []
    dropped = 0
    last_exit_bar = -1  # one position per instrument at a time
    for t in range(n):
        if not in_win[t]:
            continue
        zv = z[t]
        if not np.isfinite(zv):
            continue
        # short-only entry decision on bar t
        if not (zv >= p.strong_extension_abs_z and strong[t] and low_vol[t] and quiet[t]):
            continue
        entry_bar = t + 1
        exit_bar_time = t + 1 + h  # open of t+13
        if entry_bar >= n or exit_bar_time >= n:
            dropped += 1
            continue
        if idx[exit_bar_time] > window_end:
            dropped += 1
            continue
        if entry_bar <= last_exit_bar:
            continue  # still in a position
        entry_price = o[entry_bar]
        atr_sig = atr[t]
        if not (entry_price > 0 and np.isfinite(atr_sig) and atr_sig > 0):
            continue
        stop_price = entry_price + p.atr_stop_multiple * atr_sig
        # intrabar protective-stop scan over the holding bars t+1 .. t+12
        exit_reason = "time_stop"
        exit_bar = exit_bar_time
        exit_price = o[exit_bar_time]
        for j in range(entry_bar, entry_bar + h):
            if hi[j] >= stop_price:  # adverse for a short; adverse wins the tie
                exit_reason = "protective_atr_stop"
                exit_bar = j
                exit_price = stop_price
                break
        bars_held = (exit_bar - entry_bar) if exit_reason == "protective_atr_stop" else h
        bars_held = max(bars_held, 1)
        signed = -1.0 * float(np.log(exit_price / entry_price))  # short
        risk_frac = p.atr_stop_multiple * atr_sig / entry_price
        cost_opt = (float(spread_open[entry_bar]) + 2 * slip_px) / entry_price
        cost_cons = (CONS_SPREAD_PIPS * pip + 2 * slip_px) / entry_price + financing_stress_fraction(
            instrument, bars_held=bars_held, hours_per_bar=HOURS_PER_BAR
        )
        net_opt = signed - cost_opt
        net_cons = signed - cost_cons
        spread_paid_pips = float(spread_open[entry_bar]) / pip
        last_exit_bar = exit_bar
        trades.append(
            {
                "instrument": instrument,
                "split": split,
                "side": "short",
                "units": round((500 * 0.0025) / (p.atr_stop_multiple * atr_sig)),
                "entry_time": idx[entry_bar].isoformat(),
                "exit_time": idx[exit_bar].isoformat(),
                "year": int(idx[entry_bar].year),
                "entry_price": round(entry_price, 6),
                "exit_price": round(exit_price, 6),
                "stop_price": round(stop_price, 6),
                "zscore": round(float(zv), 6),
                "atr14": round(float(atr_sig), 8),
                "session_bucket": str(feat["session_bucket"].to_numpy()[t]),
                "gross_log_return": round(signed, 8),
                "pnl": round(net_cons, 8),  # binding (conservative) post-cost return fraction
                "pnl_optimistic": round(net_opt, 8),
                "cost_optimistic": round(cost_opt, 8),
                "cost_conservative": round(cost_cons, 8),
                "r_multiple": round(signed / risk_frac, 6) if risk_frac > 0 else None,
                "r_multiple_conservative": round(net_cons / risk_frac, 6) if risk_frac > 0 else None,
                "bars_held": int(bars_held),
                "spread_paid_pips": round(spread_paid_pips, 4),
                "exit_reason": exit_reason,
                "fill_timing": "next_bar_open",
                "timeframe": "H4",
            }
        )
    return trades, dropped


# ---------------------------------------------------------------------------
# Metrics + gates
# ---------------------------------------------------------------------------


def _safe_pf(net: np.ndarray) -> float | None:
    pos = float(net[net > 0].sum())
    neg = float(-net[net < 0].sum())
    if neg == 0:
        return None if pos == 0 else float("inf")
    return pos / neg


def trade_metrics(trades: list[dict]) -> dict:
    """Aggregate metrics over a trade list. Expectancy/PF are on the binding
    conservative post-cost return; optimistic reported alongside."""
    if not trades:
        return {
            "trade_count": 0,
            "expectancy_conservative": None,
            "expectancy_optimistic": None,
            "expectancy_r_conservative": None,
            "profit_factor_conservative": None,
            "hit_rate_conservative": None,
            "per_pair_expectancy_conservative": {},
            "per_year_expectancy_conservative": {},
            "pairs_nonneg": 0,
            "years_nonneg": 0,
            "exit_reason_counts": {},
            "avg_bars_held": None,
            "avg_spread_paid_pips": None,
            "side_counts": {"short": 0},
        }
    df = pd.DataFrame(trades)
    net = df["pnl"].to_numpy(dtype=float)
    net_opt = df["pnl_optimistic"].to_numpy(dtype=float)
    rc = df["r_multiple_conservative"].astype(float).to_numpy()
    per_pair = {p: round(float(g["pnl"].mean()), 8) for p, g in df.groupby("instrument")}
    per_year = {str(int(y)): round(float(g["pnl"].mean()), 8) for y, g in df.groupby("year")}
    return {
        "trade_count": len(df),
        "expectancy_conservative": round(float(net.mean()), 8),
        "expectancy_optimistic": round(float(net_opt.mean()), 8),
        "expectancy_r_conservative": round(float(np.nanmean(rc)), 6),
        "profit_factor_conservative": _safe_pf(net),
        "hit_rate_conservative": round(float((net > 0).mean()), 4),
        "per_pair_expectancy_conservative": per_pair,
        "per_year_expectancy_conservative": per_year,
        "pairs_nonneg": int(sum(1 for v in per_pair.values() if v >= 0)),
        "years_nonneg": int(sum(1 for v in per_year.values() if v >= 0)),
        "exit_reason_counts": {k: int(v) for k, v in df["exit_reason"].value_counts().items()},
        "avg_bars_held": round(float(df["bars_held"].mean()), 3),
        "avg_spread_paid_pips": round(float(df["spread_paid_pips"].mean()), 4),
        "side_counts": {"short": len(df)},
    }


def cost_stress_2x(trades: list[dict]) -> dict:
    """Recompute conservative expectancy with spread and slippage doubled."""
    if not trades:
        return {"trade_count": 0, "expectancy_conservative_2x": None, "profit_factor_2x": None}
    rows = []
    for t in trades:
        inst = t["instrument"]
        pip = pip_value_for(inst)
        entry = t["entry_price"]
        extra = (CONS_SPREAD_PIPS * pip + 2 * SLIP_PIPS * pip) / entry  # the doubled-portion delta
        net2 = t["pnl"] - extra
        rows.append(net2)
    arr = np.array(rows, dtype=float)
    return {
        "trade_count": len(rows),
        "expectancy_conservative_2x": round(float(arr.mean()), 8),
        "profit_factor_2x": _safe_pf(arr),
    }


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str


def evaluate_train_gates(m: dict, stress: dict, *, min_trades: int = 100) -> list[GateResult]:
    exp = m["expectancy_conservative"]
    pf = m["profit_factor_conservative"]
    g = [
        GateResult("train_expectancy_conservative_gt_0", bool(exp is not None and exp > 0),
                   f"expectancy={exp}"),
        GateResult("train_profit_factor_gte_1_05", bool(pf is not None and pf >= 1.05),
                   f"pf={pf}"),
        GateResult("train_trades_gte_min", bool(m["trade_count"] >= min_trades),
                   f"trades={m['trade_count']} (min={min_trades})"),
        GateResult("train_pairs_nonneg_gte_4", bool(m["pairs_nonneg"] >= 4),
                   f"pairs_nonneg={m['pairs_nonneg']}/7"),
        GateResult("train_years_nonneg_gte_2of3", bool(m["years_nonneg"] >= 2),
                   f"years_nonneg={m['years_nonneg']}/{len(m['per_year_expectancy_conservative'])}"),
        GateResult("train_cost_stress_2x_gte_0",
                   bool(stress["expectancy_conservative_2x"] is not None
                        and stress["expectancy_conservative_2x"] >= 0),
                   f"stress_2x={stress['expectancy_conservative_2x']}"),
    ]
    return g


@dataclass
class MatchedNullSummary:
    mode: str
    n_trades: int
    strategy_expectancy: float
    null_mean: float
    null_p95: float
    strategy_percentile: float
    prob_null_ge_strategy: float
    effect_size: float | None
    flags: list[str] = field(default_factory=list)
    note: str = ""


def run_matched_null(
    trades: list[dict],
    frames_by_pair: dict[str, pd.DataFrame],
    *,
    window_bars: int = 12,
    seeds=range(50),
    modes=MATCHED_NULL_MODES_RUN,
) -> list[dict]:
    """Run matched-null benchmarks on the campaign's own trade ledger, post
    conservative cost (both strategy and null pay the same overlay). Returns one
    descriptive dict per mode (never a verdict word)."""
    if not trades:
        return []
    ledger = pd.DataFrame(
        [{"instrument": t["instrument"], "side": t["side"], "entry_time": t["entry_time"],
          "bars_held": t["bars_held"]} for t in trades]
    )
    cost_kwargs = {"spread_pips": CONS_SPREAD_PIPS, "slip_pips": SLIP_PIPS,
                   "apply_financing": True, "hours_per_bar": int(HOURS_PER_BAR)}
    out: list[dict] = []
    for mode in modes:
        note = ""
        try:
            res = matched_null_baseline(
                ledger, frames_by_pair, mode=mode, window_bars=window_bars,
                seeds=seeds, apply_cost_overlay_fn=apply_cost_overlay, cost_kwargs=cost_kwargs,
            )
        except ValueError as exc:
            out.append({"mode": mode, "error": str(exc)})
            continue
        flags = list(interpret_matched_null(res)["flags"])
        if mode == "side_shuffled":
            note = ("degenerate for a short-only ledger — all sides identical, so the "
                    "shuffle reproduces the strategy; not an informative benchmark here")
        out.append({
            "mode": mode,
            "n_trades": res.n_trades,
            "strategy_expectancy": res.strategy_expectancy,
            "null_mean": res.null_mean,
            "null_p95": res.null_p95,
            "strategy_percentile": res.strategy_percentile,
            "prob_null_ge_strategy": res.prob_null_ge_strategy,
            "effect_size": res.effect_size,
            "flags": flags,
            "sparse_buckets": list(res.sparse_buckets),
            "note": note,
        })
    return out


def run_filter_ablation_confirmation(signal_rows: list[dict]) -> dict:
    """Re-derive FILTER_ADDS_EDGE for each retained filter on the campaign's own
    base-trigger funnel (fixed-horizon h12 value proxy), matching the front-gate
    method. Rows with a missing value proxy (window-edge) are dropped."""
    df = pd.DataFrame([r for r in signal_rows if r.get("log_return") is not None])
    if df.empty:
        return {"error": "no funnel rows with a value proxy"}
    for c in ABLATION_FILTERS:
        df[c] = df[c].astype(bool)
    res = filter_ablation(
        df, filter_cols=ABLATION_FILTERS, value_col="log_return",
        post_cost_col="log_return_post_cost_conservative", pair_col="instrument",
        side_col="side", cumulative_order=ABLATION_FILTERS,
    )
    contribs = {c.filter: {"marginal_expectancy_gain": round(c.marginal_expectancy_gain, 8),
                           "leave_out_delta": round(c.leave_out_delta, 8),
                           "reduction_ratio": round(c.reduction_ratio, 4),
                           "flags": list(c.flags)} for c in res.contributions}
    retained = ["f_low_vol", "f_strong_extension", "f_quiet_session"]

    def _stage_row(kind, s):
        return {"kind": kind, "stage": s.stage, "filters_applied": ";".join(s.filters_applied),
                "n": s.n, "reduction_ratio": round(s.reduction_ratio, 4),
                "expectancy": round(s.expectancy, 8),
                "post_cost_expectancy": None if s.post_cost_expectancy is None
                else round(s.post_cost_expectancy, 8),
                "hit_rate": round(s.hit_rate, 4)}

    stage_table = [_stage_row("trigger_only", res.trigger_only)]
    stage_table += [_stage_row("single_filter", s) for s in res.single_filter]
    stage_table += [_stage_row("cumulative", s) for s in res.cumulative]
    stage_table += [_stage_row("leave_one_out", s) for s in res.leave_one_out]
    stage_table.append(_stage_row("all_filters", res.all_filters))
    return {
        "trigger_only_expectancy": round(res.trigger_only.expectancy, 8),
        "all_filters_n": res.all_filters.n,
        "contributions": contribs,
        "retained_filters_all_add_edge": all(
            "FILTER_ADDS_EDGE" in contribs[f]["flags"] for f in retained
        ),
        "long_side_flag": contribs["f_long_side"]["flags"],
        "stage_table": stage_table,
        "notes": list(res.notes),
    }


def evaluate_validation_gates(m: dict, stress: dict, *, min_trades: int = 100) -> list[GateResult]:
    exp = m["expectancy_conservative"]
    pf = m["profit_factor_conservative"]
    year2024 = m["per_year_expectancy_conservative"].get("2024")
    g = [
        GateResult("validation_expectancy_conservative_gt_0", bool(exp is not None and exp > 0),
                   f"expectancy={exp}"),
        GateResult("validation_profit_factor_gte_1_05", bool(pf is not None and pf >= 1.05),
                   f"pf={pf}"),
        GateResult("validation_trades_gte_min", bool(m["trade_count"] >= min_trades),
                   f"trades={m['trade_count']} (min={min_trades})"),
        GateResult("validation_pairs_nonneg_gte_4", bool(m["pairs_nonneg"] >= 4),
                   f"pairs_nonneg={m['pairs_nonneg']}/7"),
        GateResult("validation_2024_not_materially_negative",
                   bool(year2024 is not None and year2024 >= 0),
                   f"2024_expectancy={year2024}"),
        GateResult("validation_cost_stress_2x_gte_0",
                   bool(stress["expectancy_conservative_2x"] is not None
                        and stress["expectancy_conservative_2x"] >= 0),
                   f"stress_2x={stress['expectancy_conservative_2x']}"),
    ]
    return g
