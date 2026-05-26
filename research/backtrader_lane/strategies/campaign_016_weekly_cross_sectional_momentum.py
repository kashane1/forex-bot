"""Backtrader secondary lane — CAMPAIGN_016 weekly cross-sectional momentum.

Cross-pair weekly portfolio logic is canonical on the bespoke engine.
This module registers the campaign adapter and exposes frozen-parameter
assertions for parity tooling. Full fold-window trade parity for the
seven-pair portfolio is **not** decision-blocking when classification
is BLOCKED with documented cross-pair state-machine gap.

``strategy_evidence: false``
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from research.backtrader_lane.runner import CampaignAdapter, register_campaign

REPO_ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN_016_CONFIG_PATH = (
    REPO_ROOT / "configs" / "campaign_016_weekly_cross_sectional_momentum.yaml"
)

EXPECTED_VERSION = "0.1.0-c016"
FROZEN_PARAMETERS: dict[str, Any] = {
    "version": EXPECTED_VERSION,
    "timeframe": "H4",
    "momentum_lookback_fast_weeks": 4,
    "momentum_lookback_slow_weeks": 12,
    "momentum_blend_fast": 0.5,
    "momentum_blend_slow": 0.5,
    "volatility_lookback_weeks": 12,
    "volatility_floor": 1.0e-8,
    "max_same_currency_exposure": 1,
    "atr_lookback": 14,
    "atr_stop_multiple": 2.5,
    "max_bars_in_trade": 42,
    "take_profit_r": None,
    "trailing_stop_atr_multiple": None,
    "entry_timing": "next_bar_open",
    "same_bar_adverse_stop_wins": True,
    "spread_to_atr_max": 0.15,
    "min_atr_pips": {},
}

CAMPAIGN_016_APPROXIMATION_FLAGS = (
    "cross_pair_portfolio_state:NOT_PORTED",
    "fill_timing:next_bar_open",
    "weekly_rebalance:shared_with_bespoke_weekly_momentum_module",
)


def _assert_frozen(strategy_cfg: dict[str, Any]) -> None:
    mismatched: list[str] = []
    for key, expected in FROZEN_PARAMETERS.items():
        got = strategy_cfg.get(key)
        if got != expected:
            mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
    if mismatched:
        raise SystemExit(
            "CAMPAIGN_016 frozen-parameter mismatch:\n" + "\n".join(mismatched)
        )


def run_campaign_016_pair(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    """Placeholder — cross-pair weekly BT port not required for REJECT verdict."""
    raise NotImplementedError(
        "CAMPAIGN_016 Backtrader cross-pair portfolio runner not implemented; "
        "bespoke engine is canonical for this sprint."
    )


CAMPAIGN_016_ADAPTER = CampaignAdapter(
    campaign_id="CAMPAIGN_016",
    strategy_id="weekly_cross_sectional_momentum_low_turnover",
    strategy_version=EXPECTED_VERSION,
    description=(
        "Backtrader registration stub for CAMPAIGN_016 weekly "
        "cross-sectional momentum 0.1.0-c016. Cross-pair portfolio "
        "BT port deferred; bespoke engine canonical."
    ),
    runner_fn=run_campaign_016_pair,
    default_instruments=(
        "EUR_USD",
        "GBP_USD",
        "USD_JPY",
        "AUD_USD",
        "USD_CAD",
        "USD_CHF",
        "NZD_USD",
    ),
    default_starting_equity_usd=500.0,
    risk_per_trade_pct=0.50,
    approximation_flags=CAMPAIGN_016_APPROXIMATION_FLAGS,
    notes="strategy_evidence: false; BT lane BLOCKED for portfolio parity.",
)
register_campaign(CAMPAIGN_016_ADAPTER)
