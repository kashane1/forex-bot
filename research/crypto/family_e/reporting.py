"""Holm multiple-comparisons + pre-committed classification for Family E.

Classification labels and gates are frozen in
CRYPTO_FAMILY_E_EXPLORATORY_RUN_SPEC_001.md and must not be relaxed post-hoc.
"""

from __future__ import annotations

from dataclasses import dataclass

LABELS = (
    "rejected",
    "statistical_only_cost_defeated",
    "cost_defeated",
    "candidate_for_front_gate",
    "blocked_data_quality",
    "blocked_low_power_oi",
)

ALPHA = 0.05


def holm_adjust(pvalues: dict[str, float]) -> dict[str, float]:
    """Holm-Bonferroni step-down adjusted p-values, keyed as input. Monotone enforced."""
    if not pvalues:
        return {}
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted: dict[str, float] = {}
    running = 0.0
    for rank, (key, p) in enumerate(items):
        q = min(1.0, (m - rank) * p)
        running = max(running, q)  # enforce non-decreasing along ascending p
        adjusted[key] = running
    return adjusted


@dataclass(frozen=True)
class GateInputs:
    """Booleans/values feeding the candidate_for_front_gate decision."""

    gross_effect_clears_null: bool  # pooled gross clears matched null after Holm
    all_in_net_positive: bool  # pooled all-in edge > 0 in predicted direction
    stress_net_positive: bool  # pooled 2x stress edge > 0
    btc_supportive: bool  # BTC-only directionally supportive
    eth_supportive: bool  # ETH-only directionally supportive
    pooled_supportive: bool  # pooled directionally supportive
    sufficient_observations: bool
    not_single_regime_slice: bool = True
    oi_depth_limited: bool = False


def classify(inputs: GateInputs) -> tuple[str, str]:
    """Return (label, rationale) from the frozen decision tree."""
    if inputs.oi_depth_limited:
        return (
            "blocked_low_power_oi",
            "OI-dependent and limited to ~180d aggregate daily OI; insufficient power.",
        )
    if not inputs.sufficient_observations:
        return (
            "blocked_data_quality",
            "Too few eligible observations to evaluate the cohort.",
        )
    candidate = (
        inputs.gross_effect_clears_null
        and inputs.all_in_net_positive
        and inputs.stress_net_positive
        and inputs.btc_supportive
        and inputs.eth_supportive
        and inputs.pooled_supportive
        and inputs.sufficient_observations
        and inputs.not_single_regime_slice
        and not inputs.oi_depth_limited
    )
    if candidate:
        return (
            "candidate_for_front_gate",
            "Clears matched null after Holm, all-in AND 2x stress net-positive, "
            "BTC and ETH both supportive, pooled supportive — eligible for a FUTURE "
            "front-gate DESIGN only (no campaign/strategy/approval here).",
        )
    if inputs.gross_effect_clears_null and not inputs.all_in_net_positive:
        return (
            "statistical_only_cost_defeated",
            "A real effect clears the matched null gross, but all-in net (incl. costs "
            "and funding) is not positive — sub-cost-band, not tradable.",
        )
    if inputs.all_in_net_positive and not inputs.gross_effect_clears_null:
        return (
            "cost_defeated",
            "Net flips positive only without robust statistical separation from the "
            "matched null — not a reliable effect.",
        )
    if (inputs.btc_supportive or inputs.eth_supportive) and not (
        inputs.btc_supportive and inputs.eth_supportive
    ):
        return (
            "rejected",
            "Single-asset only (not robust across BTC and ETH) and not net-positive — rejected.",
        )
    return ("rejected", "No effect distinguishable from the matched null; rejected.")


def fmt(value: float | int | None, *, digits: int = 4) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)
