"""Loop-guard behaviour: no strategy runs in a paper / demo / live loop
unless the approved-strategy registry approves it (infra-foundation-001).

These tests cover the *loop* side — the committed registry is empty, both
loop entry points refuse, and a malformed registry fails closed. The
approval-entry *schema* itself is covered by tests/unit/test_approval.py.
"""

from __future__ import annotations

import pytest

from forex_bot.approval import (
    APPROVED_STRATEGIES_PATH,
    StrategyNotApprovedError,
    assert_loop_strategies_approved,
    load_approval_registry,
)
from forex_bot.config import load_settings
from forex_bot.loops import run_paper_loop, run_practice_loop

_ALL_STRATEGIES = [
    "trend_following",
    "volatility_breakout",
    "pullback_continuation",
    "mean_reversion",
]
_LOOP_MODES = ["paper", "demo", "live"]


def test_committed_registry_exists_and_is_empty():
    """The registry ships with the repo and approves nothing — the
    research-freeze (Research Marathon 001 = NO-GO) default."""
    assert APPROVED_STRATEGIES_PATH.exists()
    assert load_approval_registry() == []


def test_missing_registry_means_nothing_approved(tmp_path):
    assert load_approval_registry(tmp_path / "does_not_exist.yaml") == []


def test_empty_registry_means_nothing_approved(tmp_path):
    reg = tmp_path / "approved.yaml"
    reg.write_text("approved: []\n", encoding="utf-8")
    assert load_approval_registry(reg) == []


@pytest.mark.parametrize("mode", _LOOP_MODES)
@pytest.mark.parametrize("strategy", _ALL_STRATEGIES)
def test_guard_refuses_every_strategy_when_registry_empty(tmp_path, mode, strategy):
    """With an empty registry, every strategy is refused in every loop mode."""
    reg = tmp_path / "approved.yaml"
    reg.write_text("approved: []\n", encoding="utf-8")
    with pytest.raises(StrategyNotApprovedError):
        assert_loop_strategies_approved(mode, [strategy], registry_path=reg)


def test_guard_fails_closed_on_a_malformed_registry(tmp_path):
    """A malformed registry refuses the loop (fails closed), it never
    silently approves."""
    reg = tmp_path / "approved.yaml"
    reg.write_text("approved: not-a-list\n", encoding="utf-8")
    with pytest.raises(StrategyNotApprovedError):
        assert_loop_strategies_approved("paper", ["trend_following"], registry_path=reg)


def test_paper_loop_refuses_unapproved_strategy(paper_settings):
    """run_paper_loop refuses before touching the broker — the remaining
    arguments can all be None because the guard is the first statement."""
    with pytest.raises(StrategyNotApprovedError):
        run_paper_loop(
            paper_settings,
            None, None, None, None, None, None, None, None, None,
        )


def test_practice_loop_refuses_unapproved_strategy(practice_config_path):
    """run_practice_loop (the demo / live loop path) refuses likewise."""
    settings = load_settings(practice_config_path)
    with pytest.raises(StrategyNotApprovedError):
        run_practice_loop(
            settings,
            None, None, None, None, None, None, None, None, None, None,
            None,
        )
