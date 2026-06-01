"""Family C exploratory trend-persistence diagnostics — research only."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np

from research.crypto.registry import CANONICAL_INSTRUMENTS, validate_instrument
from research.crypto.trend_persistence import (
    CostVariant,
    autocorr_lag1,
    default_lookback,
    log_returns,
    round_trip_cost_bps,
    run_length_stats,
    simulate_momentum_pnl,
)

NULL_SEED = 42
NULL_TRIALS_DEFAULT = 500
NULL_TRIALS_BY_TF: dict[str, int] = {
    "M15": 100,
    "H1": 200,
    "H4": 300,
    "D1": 500,
}
NULL_MAX_RETURNS = 8000
AUTOCORR_LAGS = (1, 2, 4, 8)
CONTINUATION_STREAKS = (1, 2, 3, 4)
REGIME_LOW_PCT = 33.0
REGIME_HIGH_PCT = 67.0

CostVariantName = Literal["gross", "spread_only", "all_in", "stress_2x"]
COST_VARIANTS: tuple[CostVariantName, ...] = (
    "gross",
    "spread_only",
    "all_in",
    "stress_2x",
)

BLOCK_SIZE_BY_TF: dict[str, int] = {
    "M15": 96,
    "H1": 24,
    "H4": 12,
    "D1": 5,
}

ATR_WINDOW_BY_TF: dict[str, int] = {
    "M15": 96,
    "H1": 48,
    "H4": 14,
    "D1": 14,
}


def autocorr_at_lags(values: np.ndarray, lags: tuple[int, ...] = AUTOCORR_LAGS) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for lag in lags:
        if lag == 1:
            out[f"ac{lag}"] = autocorr_lag1(values)
            continue
        x = values.astype(float)
        x = x[np.isfinite(x)]
        if len(x) <= lag + 5:
            out[f"ac{lag}"] = None
            continue
        x = x - x.mean()
        denom = float(np.dot(x, x))
        if denom <= 0:
            out[f"ac{lag}"] = None
            continue
        out[f"ac{lag}"] = float(np.dot(x[lag:], x[:-lag]) / denom)
    return out


def rolling_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, window: int) -> np.ndarray:
    n = len(close)
    tr = np.full(n, np.nan)
    for i in range(n):
        if i == 0:
            tr[i] = high[i] - low[i]
        else:
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1]),
            )
    atr = np.full(n, np.nan)
    for i in range(window - 1, n):
        atr[i] = float(np.mean(tr[i - window + 1 : i + 1]))
    return atr


def volatility_regime_masks(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    *,
    timeframe: str,
) -> dict[str, np.ndarray]:
    window = ATR_WINDOW_BY_TF[timeframe]
    atr = rolling_atr(high, low, close, window)
    valid = np.isfinite(atr)
    if valid.sum() < 30:
        empty = np.zeros(len(close), dtype=bool)
        return {"low": empty, "mid": empty, "high": empty}
    atr_valid = atr[valid]
    low_cut = float(np.percentile(atr_valid, REGIME_LOW_PCT))
    high_cut = float(np.percentile(atr_valid, REGIME_HIGH_PCT))
    low = valid & (atr <= low_cut)
    high = valid & (atr >= high_cut)
    mid = valid & ~low & ~high
    return {"low": low, "mid": mid, "high": high}


def continuation_probabilities(signs: np.ndarray, streaks: tuple[int, ...] = CONTINUATION_STREAKS) -> dict[str, float | None]:
    """P(next bar same sign | prior k same-direction bars)."""
    out: dict[str, float | None] = {}
    for k in streaks:
        hits = 0
        trials = 0
        for i in range(k, len(signs) - 1):
            window = signs[i - k + 1 : i + 1]
            if np.all(window == window[0]) and window[0] != 0:
                trials += 1
                if signs[i + 1] == window[0]:
                    hits += 1
        out[f"after_{k}_bars"] = hits / trials if trials > 0 else None
    return out


def momentum_quintile_forward(
    returns: np.ndarray,
    *,
    lookback: int,
    forward: int = 1,
) -> dict[str, Any]:
    n = len(returns)
    if n < lookback + forward + 50:
        return {"quintiles": [], "sample_size": 0}
    cum = np.concatenate([[0.0], np.cumsum(returns)])
    scores = np.array([cum[i] - cum[i - lookback] for i in range(lookback, n)])
    fwd = np.array(
        [np.sum(returns[i : i + forward]) for i in range(lookback, n - forward + 1)]
    )
    scores = scores[: len(fwd)]
    if len(scores) < 50:
        return {"quintiles": [], "sample_size": len(scores)}
    edges = np.percentile(scores, [20, 40, 60, 80])
    quintiles: list[dict[str, float | int]] = []
    bins = [-np.inf, *edges.tolist(), np.inf]
    for q in range(5):
        mask = (scores >= bins[q]) & (scores < bins[q + 1])
        if q == 4:
            mask = scores >= bins[q]
        seg = fwd[mask]
        if len(seg) == 0:
            continue
        quintiles.append(
            {
                "quintile": q + 1,
                "n": int(len(seg)),
                "mean_fwd": float(np.mean(seg)),
                "median_fwd": float(np.median(seg)),
                "hit_rate": float(np.mean(seg > 0)),
            }
        )
    return {"lookback": lookback, "forward_bars": forward, "quintiles": quintiles, "sample_size": int(len(scores))}


def effect_size_summary(returns: np.ndarray) -> dict[str, float | int | None]:
    r = returns[np.isfinite(returns)]
    if len(r) < 2:
        return {"mean": None, "median": None, "hit_rate": None, "t_stat": None, "n": len(r)}
    mean = float(np.mean(r))
    std = float(np.std(r, ddof=1))
    t_stat = mean / (std / np.sqrt(len(r))) if std > 0 else None
    return {
        "mean": mean,
        "median": float(np.median(r)),
        "hit_rate": float(np.mean(r > 0)),
        "t_stat": float(t_stat) if t_stat is not None else None,
        "n": int(len(r)),
    }


def _block_bootstrap_series(returns: np.ndarray, rng: np.random.Generator, block_size: int) -> np.ndarray:
    n = len(returns)
    if n < block_size * 2:
        return rng.permutation(returns)
    n_blocks = int(np.ceil(n / block_size))
    blocks = [returns[i * block_size : min(n, (i + 1) * block_size)] for i in range(n_blocks)]
    perm = rng.permutation(n_blocks)
    return np.concatenate([blocks[i] for i in perm])[:n]


def _subsample_returns(returns: np.ndarray, max_len: int, seed: int) -> np.ndarray:
    if len(returns) <= max_len:
        return returns
    rng = np.random.default_rng(seed)
    idx = np.sort(rng.choice(len(returns), size=max_len, replace=False))
    return returns[idx]


def null_distribution(
    returns: np.ndarray,
    metric_fn,
    *,
    n_trials: int | None = None,
    seed: int = NULL_SEED,
    timeframe: str = "M15",
    null_types: tuple[str, ...] = ("shuffle", "sign_flip", "block_bootstrap"),
) -> dict[str, Any]:
    n_trials = n_trials or NULL_TRIALS_BY_TF.get(timeframe, NULL_TRIALS_DEFAULT)
    work = _subsample_returns(returns, NULL_MAX_RETURNS, seed)
    rng = np.random.default_rng(seed)
    observed = metric_fn(work)
    block_size = BLOCK_SIZE_BY_TF.get(timeframe, 24)
    results: dict[str, Any] = {
        "observed": observed,
        "observed_full_sample": metric_fn(returns),
        "seed": seed,
        "n_trials": n_trials,
        "null_sample_size": int(len(work)),
    }
    for null_type in null_types:
        nulls: list[float] = []
        for _ in range(n_trials):
            if null_type == "shuffle":
                sample = rng.permutation(work)
            elif null_type == "sign_flip":
                sample = work * rng.choice([-1.0, 1.0], size=len(work))
            elif null_type == "block_bootstrap":
                sample = _block_bootstrap_series(work, rng, block_size)
            else:
                continue
            val = metric_fn(sample)
            if val is not None and np.isfinite(val):
                nulls.append(float(val))
        if not nulls or observed is None or not np.isfinite(observed):
            results[null_type] = {
                "null_mean": None,
                "null_p95": None,
                "percentile": None,
                "p_value_two_sided": None,
            }
            continue
        null_arr = np.array(nulls)
        pct = float(np.mean(null_arr <= observed) * 100.0)
        p_two = float(2 * min(np.mean(null_arr >= observed), np.mean(null_arr <= observed)))
        results[null_type] = {
            "null_mean": float(np.mean(null_arr)),
            "null_p95": float(np.percentile(null_arr, 95)),
            "null_p05": float(np.percentile(null_arr, 5)),
            "percentile": pct,
            "p_value_two_sided": min(1.0, p_two),
        }
    return results


def cost_adjusted_edge_bps(
    mean_gross_return: float,
    *,
    instrument: str,
    timeframe: str,
) -> dict[str, float]:
    """Convert mean per-bar log return to approximate bps; subtract round-trip cost on flip proxy."""
    gross_bps = mean_gross_return * 10_000.0
    out: dict[str, float] = {"gross_edge_bps": gross_bps}
    for variant in COST_VARIANTS:
        rt = round_trip_cost_bps(instrument, timeframe, variant=variant)  # type: ignore[arg-type]
        out[f"{variant}_edge_bps"] = gross_bps - rt
    out["cost_hurdle_all_in_bps"] = round_trip_cost_bps(instrument, timeframe, variant="all_in")
    return out


def continuation_event_cost_analysis(
    signs: np.ndarray,
    returns: np.ndarray,
    *,
    instrument: str,
    timeframe: str,
) -> dict[str, Any]:
    """Diagnostic: one continuation event pays forward return minus event round-trip cost."""
    streak = 2
    events: list[float] = []
    for i in range(streak, len(signs) - 1):
        window = signs[i - streak + 1 : i + 1]
        if np.all(window == window[0]) and window[0] != 0:
            events.append(float(returns[i + 1]) * window[0])
    if not events:
        return {"n_events": 0, "cost_variants": {}}
    mean_gross = float(np.mean(events))
    variants: dict[str, dict[str, float | str]] = {}
    for variant in COST_VARIANTS:
        rt = round_trip_cost_bps(instrument, timeframe, variant=variant)  # type: ignore[arg-type]
        net_bps = mean_gross * 10_000.0 - rt
        hurdle = round_trip_cost_bps(instrument, timeframe, variant="all_in")
        variants[variant] = {
            "mean_net_bps": net_bps,
            "inside_cost_band": net_bps > 0,
            "vs_all_in_hurdle": "outside" if net_bps > hurdle else "inside",
        }
    return {
        "n_events": len(events),
        "mean_gross_bps": mean_gross * 10_000.0,
        "cost_variants": variants,
        "turnover_warning": "continuation events imply discrete flips; not a strategy backtest",
    }


def horizon_to_horizon_persistence(
    higher: dict[str, np.ndarray],
    lower: dict[str, np.ndarray],
    *,
    higher_tf: str,
    lower_tf: str,
) -> dict[str, Any]:
    """Whether higher-TF bar direction aligns with next lower-TF return (diagnostic only)."""
    h_close = higher["close"]
    l_returns = log_returns(lower["close"])
    if len(h_close) < 5 or len(l_returns) < 20:
        return {"higher_tf": higher_tf, "lower_tf": lower_tf, "sample_size": 0}
    h_dir = np.sign(np.diff(h_close))
    h_times = higher["times"][1:]
    l_times = lower["times"][1:]
    aligned: list[float] = []
    j = 0
    for i, ht in enumerate(h_times):
        direction = h_dir[i]
        if direction == 0:
            continue
        while j < len(l_times) and l_times[j] <= ht:
            j += 1
        if j < len(l_returns):
            aligned.append(float(direction * l_returns[j]))
    if len(aligned) < 30:
        return {"higher_tf": higher_tf, "lower_tf": lower_tf, "sample_size": len(aligned)}
    arr = np.array(aligned)
    return {
        "higher_tf": higher_tf,
        "lower_tf": lower_tf,
        "sample_size": int(len(arr)),
        "mean_aligned_return": float(np.mean(arr)),
        "hit_rate": float(np.mean(arr > 0)),
        "effect": effect_size_summary(arr),
    }


def analyze_timeframe(
    ohlcv: dict[str, np.ndarray],
    *,
    instrument: str,
    timeframe: str,
) -> dict[str, Any]:
    validate_instrument(instrument)
    close = ohlcv["close"]
    rets = log_returns(close)
    signs = np.sign(rets)
    lookback = default_lookback(timeframe)
    masks = volatility_regime_masks(ohlcv["high"], ohlcv["low"], close, timeframe=timeframe)

    regime_ac: dict[str, float | None] = {}
    for name, mask in masks.items():
        m = mask[1 : 1 + len(rets)]
        if len(m) != len(rets):
            m = mask[-len(rets) :]
        seg = rets[m[: len(rets)]]
        if len(seg) >= 30:
            regime_ac[f"{name}_vol_ac1"] = autocorr_lag1(seg)
        else:
            regime_ac[f"{name}_vol_ac1"] = None

    mom_proxy = {
        v: simulate_momentum_pnl(
            rets, instrument=instrument, timeframe=timeframe, lookback=lookback, variant=v
        )
        for v in COST_VARIANTS
    }
    mean_gross = mom_proxy["gross"]["mean_net"]
    cost_edges = cost_adjusted_edge_bps(mean_gross, instrument=instrument, timeframe=timeframe)

    return {
        "bars": int(len(close)),
        "first_utc": ohlcv["times"][0].isoformat() if len(ohlcv["times"]) else None,
        "last_utc": ohlcv["times"][-1].isoformat() if len(ohlcv["times"]) else None,
        "autocorr": autocorr_at_lags(rets),
        "effect_size_returns": effect_size_summary(rets),
        "momentum_quintiles_fwd1": momentum_quintile_forward(rets, lookback=lookback, forward=1),
        "momentum_quintiles_fwd4": momentum_quintile_forward(rets, lookback=lookback, forward=4),
        "run_lengths": run_length_stats(signs),
        "continuation": continuation_probabilities(signs),
        "null_ac1": null_distribution(
            rets,
            autocorr_lag1,
            timeframe=timeframe,
            seed=NULL_SEED,
        ),
        "null_continuation_after_2": null_distribution(
            rets,
            lambda r: continuation_probabilities(np.sign(r)).get("after_2_bars"),
            timeframe=timeframe,
            seed=NULL_SEED + 1,
            n_trials=min(100, NULL_TRIALS_BY_TF.get(timeframe, 200)),
            null_types=("shuffle", "sign_flip"),
        ),
        "regime_autocorr": regime_ac,
        "momentum_lookback": lookback,
        "momentum_proxy": mom_proxy,
        "cost_edges_momentum_mean": cost_edges,
        "continuation_cost": continuation_event_cost_analysis(
            signs, rets, instrument=instrument, timeframe=timeframe
        ),
    }


def run_full_diagnostics(
    series: dict[str, dict[str, dict[str, np.ndarray]]],
    *,
    timeframes: tuple[str, ...] = ("M15", "H1", "H4", "D1"),
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "sprint": "crypto-family-c-trend-persistence-diagnostics-001",
        "type": "exploratory_diagnostic_only",
        "null_seed": NULL_SEED,
        "null_trials_by_tf": NULL_TRIALS_BY_TF,
        "null_max_returns": NULL_MAX_RETURNS,
        "regime_definition": {
            "measure": "rolling_ATR_percentile",
            "low_pct": REGIME_LOW_PCT,
            "high_pct": REGIME_HIGH_PCT,
            "atr_window_by_tf": ATR_WINDOW_BY_TF,
        },
        "instruments": {},
        "pooled": {},
        "horizon_cross": {},
        "gap_policy": {
            "interpolation": False,
            "use_available_bars_only": True,
            "notes": "Exchange-side M1 gaps accepted per operator; see CRYPTO_CANONICAL_DATASET_VALIDATION_001.md",
        },
    }

    pooled_ac1: dict[str, list[float]] = {tf: [] for tf in timeframes}

    for instrument in CANONICAL_INSTRUMENTS:
        if instrument not in series:
            continue
        payload["instruments"][instrument] = {"timeframes": {}}
        for tf in timeframes:
            ohlcv = series[instrument][tf]
            result = analyze_timeframe(ohlcv, instrument=instrument, timeframe=tf)
            payload["instruments"][instrument]["timeframes"][tf] = result
            ac1 = result["autocorr"].get("ac1")
            if ac1 is not None:
                pooled_ac1[tf].append(ac1)

        payload["horizon_cross"][instrument] = {}
        if "H4" in series[instrument] and "M15" in series[instrument]:
            payload["horizon_cross"][instrument]["H4_to_M15"] = horizon_to_horizon_persistence(
                series[instrument]["H4"],
                series[instrument]["M15"],
                higher_tf="H4",
                lower_tf="M15",
            )
        if "D1" in series[instrument] and "H1" in series[instrument]:
            payload["horizon_cross"][instrument]["D1_to_H1"] = horizon_to_horizon_persistence(
                series[instrument]["D1"],
                series[instrument]["H1"],
                higher_tf="D1",
                lower_tf="H1",
            )

    for tf in timeframes:
        vals = pooled_ac1[tf]
        payload["pooled"][tf] = {
            "mean_ac1": sum(vals) / len(vals) if vals else None,
            "n_instruments": len(vals),
            "both_positive_ac1": all(v > 0 for v in vals) if vals else False,
        }

    payload["classification"] = classify_synthesis(payload)
    return payload


def classify_synthesis(payload: dict[str, Any]) -> dict[str, Any]:
    """Map exploratory results to sprint classification labels."""
    any_positive_ac1 = False
    any_null_sig = False
    any_spread_survives = False
    any_allin_survives = False
    any_gross_sharpe_positive = False
    eth_drives = False
    btc_drives = False
    strongest_tf = None
    strongest_ac1 = -999.0

    for instrument, block in payload.get("instruments", {}).items():
        for tf, tf_block in block.get("timeframes", {}).items():
            ac1 = tf_block.get("autocorr", {}).get("ac1")
            if ac1 is not None and ac1 > 0:
                any_positive_ac1 = True
                if ac1 > strongest_ac1:
                    strongest_ac1 = ac1
                    strongest_tf = f"{instrument}/{tf}"
            null = tf_block.get("null_ac1", {})
            for nt in ("shuffle", "sign_flip", "block_bootstrap"):
                p = (null.get(nt) or {}).get("p_value_two_sided")
                if p is not None and p < 0.05:
                    any_null_sig = True
            mom = tf_block.get("momentum_proxy", {})
            if mom.get("gross", {}).get("sharpe", 0) > 0:
                any_gross_sharpe_positive = True
            if mom.get("spread_only", {}).get("sharpe", 0) > 0:
                any_spread_survives = True
            if mom.get("all_in", {}).get("sharpe", 0) > 0:
                any_allin_survives = True
            edges = tf_block.get("cost_edges_momentum_mean", {})
            if edges.get("spread_only_edge_bps", -999) > 0:
                any_spread_survives = True
            if edges.get("all_in_edge_bps", -999) > 0:
                any_allin_survives = True

    eth_ac1_m15 = (
        payload.get("instruments", {})
        .get("ETH_USD", {})
        .get("timeframes", {})
        .get("M15", {})
        .get("autocorr", {})
        .get("ac1")
    )
    btc_ac1_m15 = (
        payload.get("instruments", {})
        .get("BTC_USD", {})
        .get("timeframes", {})
        .get("M15", {})
        .get("autocorr", {})
        .get("ac1")
    )
    if eth_ac1_m15 and btc_ac1_m15:
        eth_drives = eth_ac1_m15 > btc_ac1_m15 and eth_ac1_m15 > 0.005
        btc_drives = btc_ac1_m15 > eth_ac1_m15 and btc_ac1_m15 > 0.005

    if any_allin_survives or (any_spread_survives and any_null_sig):
        label = "PROMISING_FOR_FACTOR_VALIDATION"
        rationale = (
            "At least one horizon shows positive spread-only or all-in diagnostic edge under "
            "frozen costs; warrants a pre-registered factor-validation sprint (not campaign)."
        )
    elif any_positive_ac1 or any_null_sig:
        label = "STATISTICAL_ONLY_COST_DEFEATED"
        rationale = (
            "Some horizons show weak positive autocorrelation or null rejection, but simple "
            "momentum/continuation diagnostics do not survive spread+fee hurdles — similar to FX "
            "cost-defeat pattern despite slightly stronger ETH short-horizon AC1."
        )
    elif any_gross_sharpe_positive:
        label = "MIXED_REQUIRES_TARGETED_FOLLOWUP"
        rationale = (
            "Gross-only momentum proxy positive at some horizons but net costs negative everywhere; "
            "narrow follow-up on slow horizons only if desired — no strategy logic."
        )
    else:
        label = "WEAK_OR_NULL"
        rationale = (
            "No consistent positive autocorrelation or cost-surviving persistence; Family B or D "
            "may offer better information gain than tuning Family C."
        )

    return {
        "label": label,
        "rationale": rationale,
        "strongest_signal": strongest_tf,
        "eth_drives_short_horizon": eth_drives,
        "btc_drives_short_horizon": btc_drives,
        "any_spread_survives": any_spread_survives,
        "any_allin_survives": any_allin_survives,
    }
