"""Research-freeze safety guard — no strategy may run in a paper / demo /
live loop unless it appears in the approved-strategy registry.

These tests prove:
  * the committed registry (configs/approved_strategies.yaml) ships empty,
  * the guard fails closed (missing / empty registry => nothing approved),
  * an unapproved strategy is refused in every loop mode,
  * the paper loop and the practice (demo / live) loop both refuse an
    unapproved strategy before doing any work.
"""

from __future__ import annotations

import pytest

from forex_bot.config import load_settings
from forex_bot.guards import (
    APPROVED_STRATEGIES_PATH,
    StrategyNotApprovedError,
    assert_loop_strategies_approved,
    load_approved_strategies,
)
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
    assert load_approved_strategies() == set()


def test_missing_registry_fails_closed(tmp_path):
    """A missing registry file approves nothing (fail closed)."""
    assert load_approved_strategies(tmp_path / "does_not_exist.yaml") == set()


def test_empty_registry_fails_closed(tmp_path):
    reg = tmp_path / "approved.yaml"
    reg.write_text("approved: []\n", encoding="utf-8")
    assert load_approved_strategies(reg) == set()


@pytest.mark.parametrize("mode", _LOOP_MODES)
@pytest.mark.parametrize("strategy", _ALL_STRATEGIES)
def test_guard_refuses_every_strategy_when_registry_empty(tmp_path, mode, strategy):
    """With an empty registry, every strategy is refused in every loop mode."""
    reg = tmp_path / "approved.yaml"
    reg.write_text("approved: []\n", encoding="utf-8")
    with pytest.raises(StrategyNotApprovedError):
        assert_loop_strategies_approved(mode, [strategy], registry_path=reg)


def test_guard_allows_only_an_explicitly_listed_strategy(tmp_path):
    reg = tmp_path / "approved.yaml"
    reg.write_text("approved:\n  - trend_following\n", encoding="utf-8")
    # The explicitly listed strategy is allowed ...
    assert_loop_strategies_approved("paper", ["trend_following"], registry_path=reg)
    # ... but a mix of listed + unlisted is still refused.
    with pytest.raises(StrategyNotApprovedError):
        assert_loop_strategies_approved(
            "demo", ["trend_following", "mean_reversion"], registry_path=reg
        )


def test_guard_rejects_malformed_registry(tmp_path):
    reg = tmp_path / "approved.yaml"
    reg.write_text("approved: not-a-list\n", encoding="utf-8")
    with pytest.raises(StrategyNotApprovedError):
        load_approved_strategies(reg)


def test_paper_loop_refuses_unapproved_strategy(paper_settings):
    """run_paper_loop refuses before touching the broker — the remaining
    arguments can all be None because the guard is the first statement."""
    with pytest.raises(StrategyNotApprovedError):
        run_paper_loop(
            paper_settings,
            None, None, None, None, None, None, None, None, None,
        )


def test_practice_loop_refuses_unapproved_strategy(practice_config_path):
    """run_practice_loop (the demo / live loop path) refuses likewise,
    before reconciliation or any broker call."""
    settings = load_settings(practice_config_path)
    with pytest.raises(StrategyNotApprovedError):
        run_practice_loop(
            settings,
            None, None, None, None, None, None, None, None, None, None,
            None,
        )
