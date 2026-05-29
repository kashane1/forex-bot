"""CAMPAIGN_027 artifact-contract validation.

Scaffold-only guardrails: the machine-readable artifact contract
(``research/campaign_027/artifact_contract.json``) must parse, declare the
required edge-discovery-compatible ledgers/metadata, and assert the scaffold
safety state (not approved, lockbox sealed, no evidence produced this sprint).

No strategy evidence is read or produced here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "research/campaign_027/artifact_contract.json"


@pytest.fixture(scope="module")
def contract() -> dict:
    assert CONTRACT.is_file(), f"artifact contract missing: {CONTRACT}"
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_contract_identity(contract: dict) -> None:
    assert contract["campaign_id"] == "CAMPAIGN_027"
    assert contract["strategy_family"] == "h4_filtered_zscore_reversion"
    assert contract["version"] == "0.1.0-c027"
    assert contract["timeframe"] == "H4"
    assert contract["status"] == "SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED"


def test_scaffold_state_is_safe(contract: dict) -> None:
    state = contract["scaffold_state"]
    assert state["not_approved"] is True
    assert state["scaffold_only"] is True
    assert state["promotion_eligible"] is False
    assert state["paper_demo_live_enabled"] is False
    assert state["strategy_evidence"] is False
    assert state["approved"] is False


def test_test_lockbox_sealed(contract: dict) -> None:
    lock = contract["test_lockbox"]
    assert lock["sealed"] is True
    assert lock["runnable_in_scaffold"] is False
    assert lock["window"] == ["2025-01-01", "2026-05-20"]


def test_no_future_artifact_produced_in_scaffold(contract: dict) -> None:
    arts = contract["required_future_artifacts"]
    assert arts, "contract must declare the future artifacts"
    for art in arts:
        assert art["produced_in_scaffold"] is False, art["name"]


def test_trade_ledger_has_canonical_schema(contract: dict) -> None:
    trade = next(a for a in contract["required_future_artifacts"] if a["name"] == "trade_ledger")
    required = {
        "instrument", "side", "units", "entry_time", "exit_time",
        "entry_price", "exit_price", "stop_price", "pnl", "r_multiple",
        "bars_held", "spread_paid_pips", "exit_reason", "fill_timing",
    }
    assert required.issubset(set(trade["required_fields"]))
    assert trade["side_constraint"] == "short_only_entered"


def test_required_metadata_items_present(contract: dict) -> None:
    meta = contract["required_metadata"]
    # items 4-12 of FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS must all be declared
    for key in (
        "item_4_pair_side_session",
        "item_5_hold_duration_bars_held",
        "item_7_split_window_tag_per_row",
        "item_12_random_seed_metadata",
    ):
        assert meta[key] is True, key
    assert meta["item_9_timeframe_column_explicit"] == "H4"
    assert "spread_paid_pips" in meta["item_6_spread_cost_fields"]


def test_precommitted_rule_matches_frozen_scope(contract: dict) -> None:
    rule = contract["precommitted_rule"]
    sig = rule["signal"]
    assert sig["zscore_lookback"] == 20
    assert sig["zscore_shift_bars"] == 1
    assert sig["zscore_std_ddof"] == 1
    assert sig["strong_extension_abs_z"] == 2.5
    side = rule["side"]
    assert side["entered"] == "short_only"
    assert side["short_when_z_ge"] == 2.5
    assert side["long_entered"] is False
    lv = rule["filters"]["low_vol"]
    assert lv["atr_lookback"] == 14
    assert lv["atr_percentile_window"] == 250
    assert lv["threshold_le"] == 0.33
    assert rule["filters"]["quiet_session"]["sessions"] == ["asia", "london"]
    ex = rule["exit"]
    assert ex["max_bars_in_trade"] == 12
    assert ex["atr_stop_multiple"] == 3.0
    assert ex["take_profit"] == "none"
    assert ex["trailing_stop"] == "none"
    assert rule["entry"]["fill_timing"] == "next_bar_open"


def test_dropped_filters_recorded(contract: dict) -> None:
    dropped = contract["precommitted_rule"]["filters"]["dropped"]
    assert dropped["cost_adv_pair"] == "FILTER_ONLY_REDUCES_SAMPLE"
    assert dropped["long_side"] == "FILTER_HURTS_EDGE"


def test_no_approval_flag_set_true_anywhere(contract: dict) -> None:
    """Defensive scan: no key named like approval/promotion is ever True."""
    banned = {"approved", "promotion_eligible", "paper_demo_live_enabled",
              "strategy_evidence", "runnable_in_scaffold"}

    def walk(obj: object) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in banned and v is True:
                    raise AssertionError(f"unsafe flag {k!r} is True")
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(contract)
