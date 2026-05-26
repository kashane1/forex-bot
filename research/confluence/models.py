"""Confluence data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TrendState = Literal["trend_up", "trend_down", "range", "unknown"]
H4Setup = Literal["breakout", "pullback", "mean_reversion", "no_setup"]
TriggerState = Literal["confirmation", "rejection", "no_trigger", "unknown"]
CostStateLabel = Literal["acceptable", "marginal", "hostile", "unknown"]
ConfluenceGrade = Literal["A", "B", "C", "REJECT"]
AlignmentState = Literal["aligned", "mixed", "conflicting", "unknown"]
DivergenceFlag = Literal["none", "bullish", "bearish", "conflicting"]


@dataclass(frozen=True)
class TimeframeState:
    w1: TrendState = "unknown"
    d1: TrendState = "unknown"
    h4_setup: H4Setup = "no_setup"
    h1_trigger: TriggerState = "unknown"


@dataclass(frozen=True)
class CrossAssetState:
    usd_regime: Literal["strengthening", "weakening", "neutral", "unknown"] = "unknown"
    risk_regime: Literal["risk_on", "risk_off", "neutral", "unknown"] = "unknown"
    rates_bias: Literal["higher", "lower", "flat", "unknown"] = "unknown"
    gold_confirm: bool | None = None
    oil_confirm: bool | None = None
    missing_features: tuple[str, ...] = ()


@dataclass(frozen=True)
class CostState:
    label: CostStateLabel = "unknown"
    spread_to_atr_pct: float | None = None


@dataclass(frozen=True)
class ConfluenceScore:
    grade: ConfluenceGrade
    alignment: AlignmentState
    timeframe: TimeframeState
    cross_asset: CrossAssetState
    cost: CostState
    divergence: DivergenceFlag
    reason_codes: tuple[str, ...] = ()
    side: Literal["long", "short"] | None = None

    def to_features_dict(self) -> dict[str, object]:
        """Shape for ``Signal.features['confluence']`` research prototype."""
        return {
            "grade": self.grade,
            "alignment": self.alignment,
            "w1_state": self.timeframe.w1,
            "d1_state": self.timeframe.d1,
            "h4_setup": self.timeframe.h4_setup,
            "h1_trigger": self.timeframe.h1_trigger,
            "cross_asset_state": {
                "usd_regime": self.cross_asset.usd_regime,
                "risk_regime": self.cross_asset.risk_regime,
                "rates_bias": self.cross_asset.rates_bias,
                "gold_confirm": self.cross_asset.gold_confirm,
                "oil_confirm": self.cross_asset.oil_confirm,
                "missing_features": list(self.cross_asset.missing_features),
            },
            "cost_state": self.cost.label,
            "spread_to_atr_pct": self.cost.spread_to_atr_pct,
            "divergence_flag": self.divergence,
            "reason_codes": list(self.reason_codes),
            "strategy_evidence": False,
        }
