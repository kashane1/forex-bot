"""Backtrader secondary lane — CAMPAIGN_017 weekly volatility contraction breakout.

Single-pair weekly compression logic is canonical on the bespoke engine.
This module registers the campaign adapter and exposes frozen-parameter
assertions for parity tooling.

``strategy_evidence: false``
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from research.backtrader_lane.runner import CampaignAdapter, register_campaign

REPO_ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN_017_CONFIG_PATH = (
    REPO_ROOT / "configs" / "campaign_017_weekly_volatility_contraction_breakout.yaml"
)

EXPECTED_VERSION = "0.1.0-c017"
FROZEN_PARAMETERS: dict[str, Any] = {
    "version": EXPECTED_VERSION,
    "timeframe": "H4",
    "compression_lookback_weeks": 12,
    "compression_percentile_threshold": 25.0,
    "breakout_buffer_atr_multiple": 0.25,
    "atr_lookback_h4": 14,
    "max_bars_in_trade": 42,
    "take_profit_r": None,
    "trailing_stop_atr_multiple": None,
    "entry_timing": "next_bar_open",
    "same_bar_adverse_stop_wins": True,
    "spread_to_atr_max": 0.15,
    "min_atr_pips": {},
}

CAMPAIGN_017_APPROXIMATION_FLAGS = (
    "fill_timing:next_bar_open",
    "weekly_compression:shared_with_bespoke_weekly_volatility_module",
    "bt_fold_runner:DEFERRED",
)


def _assert_frozen(strategy_cfg: dict[str, Any]) -> None:
    mismatched: list[str] = []
    for key, expected in FROZEN_PARAMETERS.items():
        got = strategy_cfg.get(key)
        if got != expected:
            mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
    if mismatched:
        raise SystemExit(
            "CAMPAIGN_017 frozen-parameter mismatch:\n" + "\n".join(mismatched)
        )


def run_campaign_017_pair(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    """Placeholder — full BT fold runner deferred; bespoke is canonical."""
    raise NotImplementedError(
        "CAMPAIGN_017 Backtrader fold runner not implemented; "
        "bespoke engine is canonical for this sprint."
    )


CAMPAIGN_017_ADAPTER = CampaignAdapter(
    campaign_id="CAMPAIGN_017",
    strategy_id="weekly_volatility_contraction_breakout",
    strategy_version=EXPECTED_VERSION,
    description=(
        "Backtrader registration stub for CAMPAIGN_017 weekly volatility "
        "contraction breakout 0.1.0-c017. Full BT port deferred."
    ),
    runner_fn=run_campaign_017_pair,
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
    approximation_flags=CAMPAIGN_017_APPROXIMATION_FLAGS,
    notes="strategy_evidence: false; BT lane non-decision-blocking stub.",
)
register_campaign(CAMPAIGN_017_ADAPTER)
