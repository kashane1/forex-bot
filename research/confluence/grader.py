"""Confluence grading — explainable A/B/C/REJECT labels."""

from __future__ import annotations

from research.confluence.models import (
    AlignmentState,
    ConfluenceGrade,
    ConfluenceScore,
    CostState,
    CrossAssetState,
    DivergenceFlag,
    TimeframeState,
)
from research.cost_atlas.atlas import classify_cost_state


def _alignment_for_side(
    side: str,
    w1: str,
    d1: str,
) -> tuple[AlignmentState, list[str]]:
    reasons: list[str] = []
    bullish = side == "long"
    hostile_w1 = (bullish and w1 == "trend_down") or (not bullish and w1 == "trend_up")
    hostile_d1 = (bullish and d1 == "trend_down") or (not bullish and d1 == "trend_up")
    aligned_d1 = (bullish and d1 == "trend_up") or (not bullish and d1 == "trend_down")
    range_ok = w1 == "range" or d1 == "range"
    if w1 == "unknown" or d1 == "unknown":
        reasons.append("htf_unknown")
        return "unknown", reasons
    if hostile_w1 and not range_ok:
        reasons.append("w1_hostile")
        return "conflicting", reasons
    if hostile_d1 and not range_ok:
        reasons.append("d1_hostile")
        return "conflicting", reasons
    if aligned_d1 or (range_ok and not hostile_w1):
        reasons.append("d1_aligned")
        return "aligned", reasons
    reasons.append("mixed_htf")
    return "mixed", reasons


def _cross_asset_penalty(side: str, cross: CrossAssetState) -> list[str]:
    reasons: list[str] = []
    if cross.missing_features:
        reasons.append("cross_asset_missing")
    if side == "long" and cross.usd_regime == "strengthening":
        reasons.append("usd_headwind")
    if side == "short" and cross.usd_regime == "weakening":
        reasons.append("usd_headwind")
    if side == "long" and cross.risk_regime == "risk_off":
        reasons.append("risk_off_headwind")
    return reasons


def grade_confluence(
    *,
    side: str,
    timeframe: TimeframeState,
    cross_asset: CrossAssetState | None = None,
    cost_spread_to_atr_pct: float | None = None,
    divergence: DivergenceFlag = "none",
    h4_setup_for_mr: bool = False,
) -> ConfluenceScore:
    """Grade trade context. Research prototype — not strategy evidence."""
    cross = cross_asset or CrossAssetState()
    cost_label = (
        classify_cost_state(float(cost_spread_to_atr_pct))
        if cost_spread_to_atr_pct is not None and cost_spread_to_atr_pct == cost_spread_to_atr_pct
        else "unknown"
    )
    cost = CostState(label=cost_label, spread_to_atr_pct=cost_spread_to_atr_pct)
    alignment, reasons = _alignment_for_side(side, timeframe.w1, timeframe.d1)
    reasons.extend(_cross_asset_penalty(side, cross))

    if divergence == "bearish" and side == "long":
        reasons.append("divergence_against")
    if divergence == "bullish" and side == "short":
        reasons.append("divergence_against")
    if divergence in ("bullish", "bearish") and h4_setup_for_mr:
        reasons.append("divergence_mr_boost")

    if cost.label == "hostile":
        reasons.append("cost_hostile")
        return ConfluenceScore(
            grade="REJECT",
            alignment=alignment,
            timeframe=timeframe,
            cross_asset=cross,
            cost=cost,
            divergence=divergence,
            reason_codes=tuple(reasons),
            side=side,  # type: ignore[arg-type]
        )

    if alignment == "conflicting":
        reasons.append("grade_reject_conflict")
        return ConfluenceScore(
            grade="REJECT",
            alignment=alignment,
            timeframe=timeframe,
            cross_asset=cross,
            cost=cost,
            divergence=divergence,
            reason_codes=tuple(reasons),
            side=side,  # type: ignore[arg-type]
        )

    if alignment == "unknown" or cost.label == "unknown":
        reasons.append("grade_c_unknown")
        return ConfluenceScore(
            grade="C",
            alignment=alignment,
            timeframe=timeframe,
            cross_asset=cross,
            cost=cost,
            divergence=divergence,
            reason_codes=tuple(reasons),
            side=side,  # type: ignore[arg-type]
        )

    penalty_count = sum(
        1
        for r in reasons
        if r in ("usd_headwind", "risk_off_headwind", "divergence_against", "cross_asset_missing", "mixed_htf")
    )
    if alignment == "aligned" and cost.label == "acceptable" and penalty_count == 0:
        reasons.append("grade_a")
        grade: ConfluenceGrade = "A"
    elif penalty_count <= 1 and cost.label in ("acceptable", "marginal"):
        reasons.append("grade_b")
        grade = "B"
    else:
        reasons.append("grade_c")
        grade = "C"

    return ConfluenceScore(
        grade=grade,
        alignment=alignment,
        timeframe=timeframe,
        cross_asset=cross,
        cost=cost,
        divergence=divergence,
        reason_codes=tuple(reasons),
        side=side,  # type: ignore[arg-type]
    )
