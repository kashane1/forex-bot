"""Frozen perp cost variants + funding cashflow for Family E diagnostics.

Single source of truth = CRYPTO_DERIVATIVES_COST_MODEL_001.md (FROZEN). These
numbers are NOT calibrated from diagnostic outcomes and must not change in this
sprint. All costs are expressed as a fraction of notional (bps / 1e4).
"""

from __future__ import annotations

from typing import Literal

import numpy as np

from research.crypto.derivatives_registry import validate_perp

CostVariant = Literal["gross", "spread_only", "all_in", "stress_2x"]
COST_VARIANTS: tuple[CostVariant, ...] = ("gross", "spread_only", "all_in", "stress_2x")

# Frozen perp half-spread (bps per leg) — CRYPTO_DERIVATIVES_COST_MODEL_001.md §3.
HALF_SPREAD_BPS: dict[str, float] = {"BTC_PERP_USD": 2.0, "ETH_PERP_USD": 3.0}
# Taker round-trip (bps) — §2. Slippage per leg at H1/8h horizon — §4.
TAKER_RT_BPS = 10.0
TAKER_RT_STRESS_BPS = 20.0
SLIPPAGE_BPS_PER_LEG = 1.0  # H1 / 8h-funding horizon


def round_trip_cost_bps(instrument: str, *, variant: CostVariant) -> float:
    """Round-trip transaction cost in bps for a single perp leg (excludes funding)."""
    validate_perp(instrument)
    half = HALF_SPREAD_BPS[instrument]
    if variant == "gross":
        return 0.0
    if variant == "spread_only":
        return 2.0 * half
    if variant == "all_in":
        return 2.0 * half + 2.0 * SLIPPAGE_BPS_PER_LEG + TAKER_RT_BPS
    if variant == "stress_2x":
        return 2.0 * (2.0 * half) + 2.0 * (2.0 * SLIPPAGE_BPS_PER_LEG) + TAKER_RT_STRESS_BPS
    raise ValueError(f"unknown cost variant: {variant}")


def round_trip_cost_fraction(instrument: str, *, variant: CostVariant) -> float:
    return round_trip_cost_bps(instrument, variant=variant) / 1e4


def funding_includes(variant: CostVariant) -> bool:
    """Funding cashflow enters only the all-in and 2x stress variants (cost model §7)."""
    return variant in ("all_in", "stress_2x")


def net_returns(
    signs: np.ndarray,
    fwd_ret: np.ndarray,
    funding_hold: np.ndarray,
    cost_frac: np.ndarray | float,
    *,
    include_funding: bool,
) -> np.ndarray:
    """Per-entry net return for direction ``signs`` ∈ {+1 long, -1 short}.

    ``cost_frac`` is the per-entry (or scalar) round-trip cost fraction. Funding
    sign convention (long pays short when funding>0): the funding term is
    ``- signs * funding_hold`` so a long with positive funding loses funding and a
    short gains it. Cost-array form lets BTC and ETH be pooled with per-leg costs.
    """
    price = signs * fwd_ret
    if include_funding:
        return price - signs * funding_hold - cost_frac
    return price - cost_frac


def net_signed_returns(
    signs: np.ndarray,
    fwd_ret: np.ndarray,
    funding_hold: np.ndarray,
    *,
    instrument: str,
    variant: CostVariant,
) -> np.ndarray:
    """Single-instrument convenience wrapper around :func:`net_returns`."""
    return net_returns(
        signs,
        fwd_ret,
        funding_hold,
        round_trip_cost_fraction(instrument, variant=variant),
        include_funding=funding_includes(variant),
    )


def paired_round_trip_cost_fraction(
    instrument_a: str, instrument_b: str, *, variant: CostVariant
) -> float:
    """Two-leg paired round-trip cost (relative-value disagreement, diag 6)."""
    return round_trip_cost_fraction(instrument_a, variant=variant) + round_trip_cost_fraction(
        instrument_b, variant=variant
    )
