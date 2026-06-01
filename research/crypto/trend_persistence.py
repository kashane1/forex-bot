"""Exploratory Family C trend-persistence diagnostics for canonical crypto spot data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

import numpy as np

from research.crypto.registry import HALF_SPREAD_BPS, validate_instrument

CostVariant = Literal["gross", "spread_only", "all_in", "stress_2x"]

TIMEFRAME_STORAGE: dict[str, str] = {
    "M15": "M15",
    "H1": "H1",
    "H4": "H4M1",
    "D1": "D1",
}

SLIPPAGE_BPS_PER_LEG: dict[str, float] = {
    "M15": 2.0,
    "H1": 2.0,
    "H4": 0.0,
    "D1": 0.0,
}

TAKER_FEE_RT_BPS = 120.0
TAKER_FEE_RT_STRESS_BPS = 200.0
MATERIALIZED_SOURCE = "m1_materialized"
BARS_PER_YEAR: dict[str, float] = {
    "M15": 365.25 * 24 * 4,
    "H1": 365.25 * 24,
    "H4": 365.25 * 6,
    "D1": 365.25,
}


@dataclass(frozen=True)
class CostBreakdown:
    spread_rt_bps: float
    slippage_rt_bps: float
    fee_rt_bps: float

    @property
    def all_in_rt_bps(self) -> float:
        return self.spread_rt_bps + self.slippage_rt_bps + self.fee_rt_bps


def round_trip_cost_bps(
    instrument: str,
    timeframe: str,
    *,
    variant: CostVariant,
) -> float:
    validate_instrument(instrument)
    half = HALF_SPREAD_BPS[instrument]
    slip_leg = SLIPPAGE_BPS_PER_LEG[timeframe]
    if variant == "gross":
        return 0.0
    if variant == "spread_only":
        return 2.0 * half
    if variant == "all_in":
        return 2.0 * half + 2.0 * slip_leg + TAKER_FEE_RT_BPS
    if variant == "stress_2x":
        return 2.0 * (2.0 * half) + 2.0 * (2.0 * slip_leg) + TAKER_FEE_RT_STRESS_BPS
    raise ValueError(f"unknown cost variant: {variant}")


def cost_breakdown(instrument: str, timeframe: str, *, stress: bool = False) -> CostBreakdown:
    validate_instrument(instrument)
    mult = 2.0 if stress else 1.0
    return CostBreakdown(
        spread_rt_bps=2.0 * HALF_SPREAD_BPS[instrument] * mult,
        slippage_rt_bps=2.0 * SLIPPAGE_BPS_PER_LEG[timeframe] * mult,
        fee_rt_bps=TAKER_FEE_RT_STRESS_BPS if stress else TAKER_FEE_RT_BPS,
    )


def log_returns(closes: np.ndarray) -> np.ndarray:
    closes = closes.astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        rets = np.diff(np.log(closes))
    return rets[np.isfinite(rets)]


def autocorr_lag1(values: np.ndarray) -> float | None:
    x = values.astype(float)
    x = x[np.isfinite(x)]
    if len(x) < 10:
        return None
    x = x - x.mean()
    denom = float(np.dot(x, x))
    if denom <= 0:
        return None
    return float(np.dot(x[1:], x[:-1]) / denom)


def run_length_stats(signs: np.ndarray) -> dict[str, float]:
    if len(signs) == 0:
        return {"mean_run": 0.0, "max_run": 0.0, "runs": 0.0}
    runs: list[int] = []
    current = 1
    for idx in range(1, len(signs)):
        if signs[idx] == signs[idx - 1] and signs[idx] != 0:
            current += 1
        else:
            if signs[idx - 1] != 0:
                runs.append(current)
            current = 1
    if signs[-1] != 0:
        runs.append(current)
    if not runs:
        return {"mean_run": 0.0, "max_run": 0.0, "runs": 0.0}
    return {
        "mean_run": float(np.mean(runs)),
        "max_run": float(max(runs)),
        "runs": float(len(runs)),
    }


def momentum_positions(returns: np.ndarray, *, lookback: int) -> np.ndarray:
    """Always-in-market {-1,+1} positions from sign of cumulative lookback return."""
    n = len(returns)
    positions = np.zeros(n + 1, dtype=float)
    cum = np.concatenate([[0.0], np.cumsum(returns)])
    for idx in range(lookback, n + 1):
        past = cum[idx] - cum[idx - lookback]
        positions[idx] = 1.0 if past > 0 else (-1.0 if past < 0 else 0.0)
    return positions[1:]


def simulate_momentum_pnl(
    returns: np.ndarray,
    *,
    instrument: str,
    timeframe: str,
    lookback: int,
    variant: CostVariant,
) -> dict[str, float]:
    if len(returns) < lookback + 2:
        return {"mean_net": 0.0, "sharpe": 0.0, "turnover": 0.0, "n": 0.0}
    positions = momentum_positions(returns, lookback=lookback)
    aligned_pos = positions[:-1]
    aligned_ret = returns[1:]
    gross = aligned_pos * aligned_ret
    deltas = np.abs(np.diff(np.concatenate([[0.0], positions])))
    rt_cost = round_trip_cost_bps(instrument, timeframe, variant=variant) / 10_000.0
    costs = (deltas[1:] / 2.0) * rt_cost
    net = gross - costs
    mean_net = float(np.mean(net))
    std = float(np.std(net, ddof=1)) if len(net) > 1 else 0.0
    sharpe = (
        mean_net / std * np.sqrt(BARS_PER_YEAR[timeframe])
        if std > 0
        else 0.0
    )
    return {
        "mean_net": mean_net,
        "sharpe": float(sharpe),
        "turnover": float(np.mean(deltas[1:] / 2.0)),
        "n": float(len(net)),
    }


def null_autocorr_distribution(
    returns: np.ndarray,
    *,
    n_draws: int = 200,
    block_size: int = 24,
    seed: int = 42,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    actual = autocorr_lag1(returns)
    nulls: list[float] = []
    n = len(returns)
    if n < block_size * 2:
        return {"actual": actual, "null_mean": 0.0, "null_p95": 0.0, "p_value": 1.0}
    n_blocks = int(np.ceil(n / block_size))
    blocks = [returns[i * block_size : min(n, (i + 1) * block_size)] for i in range(n_blocks)]
    for _ in range(n_draws):
        perm = rng.permutation(n_blocks)
        shuffled = np.concatenate([blocks[i] for i in perm])[:n]
        ac = autocorr_lag1(shuffled)
        if ac is not None:
            nulls.append(ac)
    if not nulls or actual is None:
        return {"actual": actual, "null_mean": 0.0, "null_p95": 0.0, "p_value": 1.0}
    null_arr = np.array(nulls)
    p_value = float(np.mean(null_arr >= actual))
    return {
        "actual": actual,
        "null_mean": float(np.mean(null_arr)),
        "null_p95": float(np.percentile(null_arr, 95)),
        "p_value": p_value,
    }


def regime_split_autocorr(
    returns: np.ndarray,
    *,
    vol_window: int = 60,
) -> dict[str, float | None]:
    if len(returns) < vol_window + 10:
        return {"low_vol_ac1": None, "high_vol_ac1": None}
    vol = pd_rolling_std(returns, vol_window)
    valid = vol[vol_window - 1 :]
    rets = returns[vol_window - 1 :]
    if len(valid) < 20:
        return {"low_vol_ac1": None, "high_vol_ac1": None}
    low_cut = float(np.percentile(valid, 33))
    high_cut = float(np.percentile(valid, 67))
    low = rets[valid <= low_cut]
    high = rets[valid >= high_cut]
    return {
        "low_vol_ac1": autocorr_lag1(low),
        "high_vol_ac1": autocorr_lag1(high),
    }


def pd_rolling_std(values: np.ndarray, window: int) -> np.ndarray:
    out = np.full(len(values), np.nan)
    for idx in range(window - 1, len(values)):
        seg = values[idx - window + 1 : idx + 1]
        out[idx] = float(np.std(seg, ddof=1))
    return out


def analyze_series(
    closes: np.ndarray,
    *,
    instrument: str,
    timeframe: str,
    lookback: int,
) -> dict[str, Any]:
    rets = log_returns(closes)
    signs = np.sign(rets)
    ac1 = autocorr_lag1(rets)
    runs = run_length_stats(signs)
    null = null_autocorr_distribution(rets)
    regime = regime_split_autocorr(rets)
    momentum: dict[str, dict[str, float]] = {}
    for variant in ("gross", "spread_only", "all_in", "stress_2x"):
        momentum[variant] = simulate_momentum_pnl(
            rets,
            instrument=instrument,
            timeframe=timeframe,
            lookback=lookback,
            variant=variant,  # type: ignore[arg-type]
        )
    return {
        "bars": int(len(closes)),
        "return_ac1": ac1,
        "run_lengths": runs,
        "null_autocorr": null,
        "regime_ac1": regime,
        "momentum_lookback": lookback,
        "momentum": momentum,
    }


def default_lookback(timeframe: str) -> int:
    return {"M15": 4, "H1": 4, "H4": 6, "D1": 5}.get(timeframe, 4)


def rows_to_closes(rows: list[dict[str, Any]]) -> tuple[list[datetime], np.ndarray]:
    times = [row["time_utc"].astimezone(UTC) for row in rows]
    closes = np.array([float(row["mid_c"]) for row in rows], dtype=float)
    return times, closes
