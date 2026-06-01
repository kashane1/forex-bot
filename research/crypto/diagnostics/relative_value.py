"""Family B exploratory BTC/ETH relative-value diagnostics — research only."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np

from research.crypto.trend_persistence import log_returns, round_trip_cost_bps
from research.crypto.diagnostics.trend_persistence import (
    BLOCK_SIZE_BY_TF,
    COST_VARIANTS,
    NULL_MAX_RETURNS,
    NULL_SEED,
    NULL_TRIALS_BY_TF,
    REGIME_HIGH_PCT,
    REGIME_LOW_PCT,
    null_distribution,
    rolling_atr,
)

TIMEFRAMES = ("M15", "H1", "H4", "D1")

LOOKBACKS_BY_TF: dict[str, tuple[int, ...]] = {
    "M15": (4, 16, 48),
    "H1": (4, 24, 72),
    "H4": (3, 6, 18),
    "D1": (3, 7, 21),
}

BETA_WINDOW_BY_TF: dict[str, int] = {
    "M15": 96,
    "H1": 48,
    "H4": 14,
    "D1": 21,
}

ZSCORE_WINDOW_BY_TF: dict[str, int] = {
    "M15": 96,
    "H1": 48,
    "H4": 14,
    "D1": 21,
}

Z_BANDS = (1.0, 1.5, 2.0)
LEAD_LAGS = (1, 2, 4)
FORWARD_HORIZONS = (1, 4)

FAMILY_C_REFERENCE_BPS = {
    "ETH_M15_gross_momentum_edge_bps": 0.20,
    "best_family_c_gross_sharpe": 1.0012,
}

FX_S4_REFERENCE_NOTE = (
    "FX S4 cross relative-value: economically motivated but historically sub-cost-band "
    "(real effect often a few bps gross, defeated by two-leg spread+fees)."
)


def paired_cost_report(timeframe: str) -> dict[str, dict[str, float]]:
    """One-leg and two-leg frozen costs per variant."""
    out: dict[str, dict[str, float]] = {}
    for variant in COST_VARIANTS:
        btc = round_trip_cost_bps("BTC_USD", timeframe, variant=variant)  # type: ignore[arg-type]
        eth = round_trip_cost_bps("ETH_USD", timeframe, variant=variant)  # type: ignore[arg-type]
        out[variant] = {
            "btc_one_leg_bps": btc,
            "eth_one_leg_bps": eth,
            "one_leg_avg_bps": (btc + eth) / 2.0,
            "paired_rt_bps": btc + eth,
        }
    return out


def apply_cost_bps(gross_bps: float, hurdle_bps: float) -> dict[str, float | bool]:
    net = gross_bps - hurdle_bps
    return {
        "gross_bps": gross_bps,
        "net_bps": net,
        "hurdle_bps": hurdle_bps,
        "inside_cost_band": net <= 0,
        "survives": net > 0,
    }


def rolling_beta(eth_rets: np.ndarray, btc_rets: np.ndarray, window: int) -> np.ndarray:
    n = len(btc_rets)
    betas = np.full(n, np.nan)
    for i in range(window, n):
        b = btc_rets[i - window : i]
        e = eth_rets[i - window : i]
        var_b = float(np.var(b, ddof=1))
        if var_b > 1e-18:
            betas[i] = float(np.cov(b, e, ddof=1)[0, 1] / var_b)
    return betas


def beta_adjusted_spread(log_btc: np.ndarray, log_eth: np.ndarray, beta: np.ndarray) -> np.ndarray:
    spread = log_btc - beta * log_eth
    spread[~np.isfinite(beta)] = np.nan
    return spread


def rolling_zscore(series: np.ndarray, window: int) -> np.ndarray:
    n = len(series)
    z = np.full(n, np.nan)
    for i in range(window, n):
        seg = series[i - window : i]
        if not np.all(np.isfinite(seg)):
            continue
        mu = float(np.mean(seg))
        sd = float(np.std(seg, ddof=1))
        if sd > 1e-18:
            z[i] = (series[i] - mu) / sd
    return z


def effect_summary(values: np.ndarray) -> dict[str, float | int | None]:
    v = values[np.isfinite(values)]
    if len(v) < 2:
        return {"mean_bps": None, "median_bps": None, "hit_rate": None, "t_stat": None, "n": len(v)}
    mean = float(np.mean(v))
    std = float(np.std(v, ddof=1))
    t_stat = mean / (std / np.sqrt(len(v))) if std > 0 else None
    return {
        "mean_bps": mean * 10_000.0,
        "median_bps": float(np.median(v)) * 10_000.0,
        "hit_rate": float(np.mean(v > 0)),
        "t_stat": float(t_stat) if t_stat is not None else None,
        "n": int(len(v)),
    }


def lead_lag_block(
    btc_rets: np.ndarray,
    eth_rets: np.ndarray,
    *,
    timeframe: str,
) -> dict[str, Any]:
    costs = paired_cost_report(timeframe)
    same_corr = float(np.corrcoef(btc_rets, eth_rets)[0, 1]) if len(btc_rets) > 10 else None
    rolling_corr: list[float] = []
    w = BETA_WINDOW_BY_TF[timeframe]
    for i in range(w, len(btc_rets), max(1, w)):
        seg_b = btc_rets[i - w : i]
        seg_e = eth_rets[i - w : i]
        if len(seg_b) > 5:
            rolling_corr.append(float(np.corrcoef(seg_b, seg_e)[0, 1]))
    beta = rolling_beta(eth_rets, btc_rets, w)

    def _lag_table(leader: np.ndarray, follower: np.ndarray, name: str) -> dict[str, Any]:
        rows: dict[str, Any] = {}
        for lag in LEAD_LAGS:
            if len(leader) <= lag + 10:
                continue
            x = leader[:-lag]
            y = follower[lag:]
            corr = float(np.corrcoef(x, y)[0, 1])
            long_fwd = y[x > 0]
            short_fwd = y[x < 0]
            gross_bps = float(np.mean(y * np.sign(x)) * 10_000.0) if len(y) else 0.0
            rows[f"lag_{lag}"] = {
                "correlation": corr,
                "effect": effect_summary(y * np.sign(x)),
                "gross_directional_bps": gross_bps,
                "cost_adjusted": {
                    v: apply_cost_bps(gross_bps, costs[v]["one_leg_avg_bps"])
                    for v in COST_VARIANTS
                },
                "paired_cost_adjusted": {
                    v: apply_cost_bps(gross_bps, costs[v]["paired_rt_bps"])
                    for v in COST_VARIANTS
                },
                "null_corr": null_distribution(
                    x,
                    lambda a: float(np.corrcoef(a, y[: len(a)])[0, 1])
                    if len(a) > 10
                    else 0.0,
                    timeframe=timeframe,
                    seed=NULL_SEED,
                ),
            }
        return {"name": name, "lags": rows}

    return {
        "same_bar_correlation": same_corr,
        "rolling_correlation_mean": float(np.mean(rolling_corr)) if rolling_corr else None,
        "rolling_correlation_std": float(np.std(rolling_corr)) if rolling_corr else None,
        "beta_eth_on_btc_mean": float(np.nanmean(beta)),
        "btc_leads_eth": _lag_table(btc_rets, eth_rets, "BTC_to_ETH"),
        "eth_leads_btc": _lag_table(eth_rets, btc_rets, "ETH_to_BTC"),
    }


def relative_momentum_block(
    btc_rets: np.ndarray,
    eth_rets: np.ndarray,
    *,
    timeframe: str,
    beta: np.ndarray | None = None,
) -> dict[str, Any]:
    rel = btc_rets - eth_rets
    if beta is not None:
        rel_beta = btc_rets - beta * eth_rets
        rel_beta[~np.isfinite(beta)] = np.nan
    else:
        rel_beta = rel
    costs = paired_cost_report(timeframe)
    results: dict[str, Any] = {"lookbacks": {}, "beta_adjusted": {}}
    n = len(rel)

    for lb in LOOKBACKS_BY_TF[timeframe]:
        if n < lb + 10:
            continue
        cum = np.concatenate([[0.0], np.cumsum(rel)])
        scores = np.array([cum[i] - cum[i - lb] for i in range(lb, n)])
        fwd1 = rel[lb:n]
        edges = np.percentile(scores, [20, 40, 60, 80])
        top = fwd1[scores >= edges[3]]
        bot = fwd1[scores <= edges[0]]
        spread_gross = float((np.mean(top) - np.mean(bot)) * 10_000.0) if len(top) and len(bot) else 0.0
        results["lookbacks"][str(lb)] = {
            "top_minus_bottom_bps": spread_gross,
            "top_effect": effect_summary(top),
            "bottom_effect": effect_summary(bot),
            "monotonic_quintiles": _quintile_monotonicity(scores, fwd1),
            "cost": {v: apply_cost_bps(spread_gross, costs[v]["paired_rt_bps"]) for v in COST_VARIANTS},
            "null_spread": null_distribution(
                rel,
                lambda r: _null_rel_momentum_spread(r, lb),
                timeframe=timeframe,
                seed=NULL_SEED + lb,
            ),
        }
        if beta is not None:
            cum_b = np.concatenate([[0.0], np.cumsum(rel_beta)])
            scores_b = np.array([cum_b[i] - cum_b[i - lb] for i in range(lb, n)])
            fwd_b = rel_beta[lb:n]
            valid = np.isfinite(scores_b) & np.isfinite(fwd_b)
            if valid.sum() > 50:
                edges_b = np.percentile(scores_b[valid], [20, 40, 60, 80])
                top_b = fwd_b[valid & (scores_b >= edges_b[3])]
                bot_b = fwd_b[valid & (scores_b <= edges_b[0])]
                spread_b = float((np.mean(top_b) - np.mean(bot_b)) * 10_000.0)
                results["beta_adjusted"][str(lb)] = {"top_minus_bottom_bps": spread_b}
    return results


def _quintile_monotonicity(scores: np.ndarray, fwd: np.ndarray) -> dict[str, float]:
    edges = np.percentile(scores, [20, 40, 60, 80])
    means: list[float] = []
    for q in range(5):
        lo = -np.inf if q == 0 else edges[q - 1]
        hi = np.inf if q == 4 else edges[q]
        mask = (scores >= lo) & (scores < hi) if q < 4 else (scores >= edges[3])
        if q == 0:
            mask = scores <= edges[0]
        seg = fwd[mask]
        means.append(float(np.mean(seg)) * 10_000.0 if len(seg) else 0.0)
    return {"q1_bps": means[0], "q5_bps": means[4], "q5_minus_q1_bps": means[4] - means[0]}


def _null_rel_momentum_spread(returns: np.ndarray, lookback: int) -> float:
    n = len(returns)
    if n < lookback + 10:
        return 0.0
    cum = np.concatenate([[0.0], np.cumsum(returns)])
    scores = np.array([cum[i] - cum[i - lookback] for i in range(lookback, n)])
    fwd = returns[lookback:n]
    edges = np.percentile(scores, [20, 80])
    top = fwd[scores >= edges[1]]
    bot = fwd[scores <= edges[0]]
    if len(top) == 0 or len(bot) == 0:
        return 0.0
    return float((np.mean(top) - np.mean(bot)) * 10_000.0)


def divergence_reversion_block(
    log_btc: np.ndarray,
    log_eth: np.ndarray,
    btc_rets: np.ndarray,
    eth_rets: np.ndarray,
    *,
    timeframe: str,
) -> dict[str, Any]:
    w_beta = BETA_WINDOW_BY_TF[timeframe]
    w_z = ZSCORE_WINDOW_BY_TF[timeframe]
    beta = rolling_beta(eth_rets, btc_rets, w_beta)
    spread = beta_adjusted_spread(log_btc, log_eth, beta)
    z = rolling_zscore(spread, w_z)
    costs = paired_cost_report(timeframe)
    bands: dict[str, Any] = {}

    for threshold in Z_BANDS:
        long_mask = z >= threshold
        short_mask = z <= -threshold
        for side, mask in (("long_spread", long_mask), ("short_spread", short_mask)):
            events = _forward_spread_change(spread, mask, FORWARD_HORIZONS)
            paired_ret = _paired_reversion_return(btc_rets, eth_rets, z, mask, beta)
            gross = float(np.mean(paired_ret) * 10_000.0) if len(paired_ret) else 0.0
            key = f"{side}_z_ge_{threshold}".replace(".", "_")
            bands[key] = {
                "event_count": int(mask.sum()),
                "forward_spread_change": events,
                "paired_reversion_return_bps": effect_summary(paired_ret),
                "gross_paired_bps": gross,
                "cost": {v: apply_cost_bps(gross, costs[v]["paired_rt_bps"]) for v in COST_VARIANTS},
                "null": null_distribution(
                    spread[np.isfinite(spread)],
                    lambda s: _null_reversion_gross(s, threshold, w_z),
                    timeframe=timeframe,
                    seed=NULL_SEED + int(threshold * 10),
                    n_trials=min(100, NULL_TRIALS_BY_TF.get(timeframe, 200)),
                ),
            }
    return {
        "beta_window": w_beta,
        "zscore_window": w_z,
        "spread_z_bands": bands,
        "raw_spread_reversion": _raw_spread_reversion(spread, z),
    }


def _forward_spread_change(spread: np.ndarray, mask: np.ndarray, horizons: tuple[int, ...]) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    idx = np.where(mask)[0]
    for h in horizons:
        deltas: list[float] = []
        for i in idx:
            if i + h < len(spread) and np.isfinite(spread[i]) and np.isfinite(spread[i + h]):
                deltas.append(spread[i + h] - spread[i])
        out[f"fwd_{h}_spread_change_bps"] = (
            float(np.mean(deltas)) * 10_000.0 if deltas else None
        )
    return out


def _paired_reversion_return(
    btc_rets: np.ndarray,
    eth_rets: np.ndarray,
    z: np.ndarray,
    mask: np.ndarray,
    beta: np.ndarray,
) -> np.ndarray:
    """Diagnostic proxy: long spread (short BTC, long ETH beta-weighted) when z high."""
    idx = np.where(mask)[0]
    out: list[float] = []
    for i in idx:
        if i + 1 >= len(btc_rets) or not np.isfinite(beta[i]):
            continue
        b = float(beta[i])
        # reversion trade earns -sign(z) * rel move; use next-bar rel return
        rel = btc_rets[i + 1] - b * eth_rets[i + 1]
        out.append(-np.sign(z[i]) * rel)
    return np.array(out, dtype=float)


def _null_reversion_gross(spread: np.ndarray, threshold: float, window: int) -> float:
    z = rolling_zscore(spread, window)
    mask = z >= threshold
    if mask.sum() < 5:
        return 0.0
    deltas = []
    idx = np.where(mask)[0]
    for i in idx:
        if i + 1 < len(spread):
            deltas.append(-(spread[i + 1] - spread[i]))
    return float(np.mean(deltas)) * 10_000.0 if deltas else 0.0


def _raw_spread_reversion(spread: np.ndarray, z: np.ndarray) -> dict[str, Any]:
    valid = np.isfinite(z)
    if valid.sum() < 50:
        return {}
    high = z >= 2
    low = z <= -2
    return {
        "high_z_mean_fwd_change_bps": _forward_spread_change(spread, high, (1,)),
        "low_z_mean_fwd_change_bps": _forward_spread_change(spread, low, (1,)),
    }


def regime_masks(
    btc_rets: np.ndarray,
    eth_rets: np.ndarray,
    btc_high: np.ndarray,
    btc_low: np.ndarray,
    btc_close: np.ndarray,
    eth_high: np.ndarray,
    eth_low: np.ndarray,
    eth_close: np.ndarray,
    *,
    timeframe: str,
) -> dict[str, np.ndarray]:
    w = BETA_WINDOW_BY_TF[timeframe]
    btc_atr = rolling_atr(btc_high, btc_low, btc_close, w)
    eth_atr = rolling_atr(eth_high, eth_low, eth_close, w)
    rel = btc_rets - eth_rets
    corr = np.full(len(btc_rets), np.nan)
    for i in range(w, len(btc_rets)):
        corr[i] = float(np.corrcoef(btc_rets[i - w : i], eth_rets[i - w : i])[0, 1])

    def tercile_mask(series: np.ndarray) -> dict[str, np.ndarray]:
        valid = np.isfinite(series)
        if valid.sum() < 30:
            z = np.zeros(len(series), dtype=bool)
            return {"low": z, "mid": z, "high": z}
        vals = series[valid]
        lo = float(np.percentile(vals, REGIME_LOW_PCT))
        hi = float(np.percentile(vals, REGIME_HIGH_PCT))
        return {
            "low": valid & (series <= lo),
            "mid": valid & (series > lo) & (series < hi),
            "high": valid & (series >= hi),
        }

    lb0 = LOOKBACKS_BY_TF[timeframe][0]
    btc_dom = np.zeros(len(rel), dtype=bool)
    eth_dom = np.zeros(len(rel), dtype=bool)
    for i in range(lb0, len(rel)):
        s = float(np.sum(rel[i - lb0 : i]))
        btc_dom[i] = s > 0
        eth_dom[i] = s < 0

    return {
        "btc_vol": tercile_mask(btc_atr),
        "eth_vol": tercile_mask(eth_atr),
        "correlation": tercile_mask(corr),
        "btc_dominant": btc_dom,
        "eth_dominant": eth_dom,
    }


def analyze_regime_subset(
    metric_series: np.ndarray,
    masks: dict[str, np.ndarray],
) -> dict[str, dict[str, float | None]]:
    out: dict[str, dict[str, float | None]] = {}
    for regime_name, regime_masks in masks.items():
        if isinstance(regime_masks, dict):
            out[regime_name] = {}
            for tier, m in regime_masks.items():
                seg = metric_series[m[: len(metric_series)]]
                out[regime_name][tier] = effect_summary(seg).get("mean_bps")
        else:
            seg = metric_series[regime_masks[: len(metric_series)]]
            out[regime_name] = {"all": effect_summary(seg).get("mean_bps")}
    return out


def analyze_timeframe_pair(
    aligned: dict[str, np.ndarray],
    *,
    timeframe: str,
) -> dict[str, Any]:
    log_btc = np.log(aligned["btc_close"])
    log_eth = np.log(aligned["eth_close"])
    btc_rets = log_returns(aligned["btc_close"])
    eth_rets = log_returns(aligned["eth_close"])
    beta = rolling_beta(eth_rets, btc_rets, BETA_WINDOW_BY_TF[timeframe])

    lead_lag = lead_lag_block(btc_rets, eth_rets, timeframe=timeframe)
    rel_mom = relative_momentum_block(btc_rets, eth_rets, timeframe=timeframe, beta=beta)
    div = divergence_reversion_block(
        log_btc, log_eth, btc_rets, eth_rets, timeframe=timeframe
    )
    masks = regime_masks(
        btc_rets,
        eth_rets,
        aligned["btc_high"],
        aligned["btc_low"],
        aligned["btc_close"],
        aligned["eth_high"],
        aligned["eth_low"],
        aligned["eth_close"],
        timeframe=timeframe,
    )
    rel = btc_rets - eth_rets
    regime_summary = {
        "rel_return_mean_bps_by_regime": analyze_regime_subset(rel, masks),
        "lead_lag_btc_lag1_by_corr_regime": _regime_lead_lag(btc_rets, eth_rets, masks.get("correlation", {})),
    }
    return {
        "aligned_bars": int(aligned["n_aligned"]),
        "dropped_btc_only": int(aligned["n_dropped_btc_only"]),
        "dropped_eth_only": int(aligned["n_dropped_eth_only"]),
        "paired_costs": paired_cost_report(timeframe),
        "lead_lag": lead_lag,
        "relative_momentum": rel_mom,
        "divergence_reversion": div,
        "regime": regime_summary,
    }


def _regime_lead_lag(
    btc_rets: np.ndarray,
    eth_rets: np.ndarray,
    corr_masks: dict[str, np.ndarray],
) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    y = eth_rets[1:]
    x = btc_rets[:-1]
    gross = y * np.sign(x)
    for tier, m in corr_masks.items():
        m2 = m[1 : 1 + len(gross)]
        if m2.sum() < 20:
            out[tier] = None
        else:
            out[tier] = float(np.mean(gross[m2]) * 10_000.0)
    return out


def run_full_diagnostics(
    aligned_by_tf: dict[str, dict[str, np.ndarray]],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "sprint": "crypto-family-b-relative-value-diagnostics-001",
        "type": "exploratory_diagnostic_only",
        "null_seed": NULL_SEED,
        "null_trials_by_tf": NULL_TRIALS_BY_TF,
        "null_max_returns": NULL_MAX_RETURNS,
        "lookbacks_by_tf": {k: list(v) for k, v in LOOKBACKS_BY_TF.items()},
        "family_c_reference_bps": FAMILY_C_REFERENCE_BPS,
        "fx_s4_reference": FX_S4_REFERENCE_NOTE,
        "timeframes": {},
        "comparison_to_family_c": {},
    }
    best: dict[str, float] = {"gross_bps": -999.0, "family": "", "tf": ""}

    for tf in TIMEFRAMES:
        if tf not in aligned_by_tf:
            continue
        block = analyze_timeframe_pair(aligned_by_tf[tf], timeframe=tf)
        payload["timeframes"][tf] = block
        _update_best_effects(block, tf, best)

    payload["strongest_effect"] = best
    payload["classification"] = classify_synthesis(payload)
    return payload


def _update_best_effects(block: dict[str, Any], tf: str, best: dict[str, float]) -> None:
    ll = block["lead_lag"]["btc_leads_eth"]["lags"].get("lag_1", {})
    g = ll.get("gross_directional_bps", -999)
    if g > best["gross_bps"]:
        best.update({"gross_bps": g, "family": "btc_leads_eth_lag1", "tf": tf})
    for lb, row in block["relative_momentum"]["lookbacks"].items():
        g2 = row.get("top_minus_bottom_bps", -999)
        if g2 > best["gross_bps"]:
            best.update({"gross_bps": g2, "family": f"rel_momentum_lb{lb}", "tf": tf})


def classify_synthesis(payload: dict[str, Any]) -> dict[str, Any]:
    any_spread_paired = False
    any_allin_paired = False
    any_null_sig = False
    any_gross_material = False
    max_gross = payload.get("strongest_effect", {}).get("gross_bps", 0.0)

    for tf, block in payload.get("timeframes", {}).items():
        costs = block.get("paired_costs", {})
        for lb, row in block.get("relative_momentum", {}).get("lookbacks", {}).items():
            for v in COST_VARIANTS:
                c = row.get("cost", {}).get(v, {})
                if v == "spread_only" and c.get("survives"):
                    any_spread_paired = True
                if v == "all_in" and c.get("survives"):
                    any_allin_paired = True
            null_p = (row.get("null_spread") or {}).get("shuffle", {}).get("p_value_two_sided")
            if null_p is not None and null_p < 0.05:
                any_null_sig = True
            if abs(row.get("top_minus_bottom_bps", 0)) > 2.0:
                any_gross_material = True
        for band in block.get("divergence_reversion", {}).get("spread_z_bands", {}).values():
            for v in COST_VARIANTS:
                if band.get("cost", {}).get(v, {}).get("survives"):
                    if v == "spread_only":
                        any_spread_paired = True
                    if v == "all_in":
                        any_allin_paired = True

    beats_family_c = max_gross > FAMILY_C_REFERENCE_BPS["ETH_M15_gross_momentum_edge_bps"]

    if any_allin_paired and any_null_sig and beats_family_c:
        label = "PROMISING_FOR_FACTOR_VALIDATION"
        rationale = (
            "Relative-value effect survives all-in paired costs with null support and exceeds "
            "Family C gross scale — warrants pre-registered factor validation (not campaign)."
        )
    elif any_gross_material or any_null_sig:
        label = "STATISTICAL_ONLY_COST_DEFEATED"
        rationale = (
            "BTC/ETH relative structure shows lead-lag, momentum, or reversion statistics but "
            "paired spread+fee hurdles (similar to FX S4) defeat economic tradability."
        )
    elif max_gross > 0.5:
        label = "MIXED_REQUIRES_TARGETED_FOLLOWUP"
        rationale = (
            "Small gross relative-value hints without cost survival — narrow follow-up on slow "
            "horizons or single effect family only; no strategy logic."
        )
    else:
        label = "WEAK_OR_NULL"
        rationale = (
            "No material BTC/ETH relative-value edge vs nulls; prefer Family D non-time bars or "
            "Family E preparation over tuning RV."
        )

    return {
        "label": label,
        "rationale": rationale,
        "any_spread_paired_survives": any_spread_paired,
        "any_allin_paired_survives": any_allin_paired,
        "beats_family_c_gross_scale": beats_family_c,
        "max_gross_bps_observed": max_gross,
    }
