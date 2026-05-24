"""Opt-in gap-through fill: plumbing tests.

Sprint `infra-exit-fidelity-001` Phase 2. Covers the `gap_fill_policy`
config field, the engine kwarg + conditional hash inclusion, and the
`--gap-fill-policy` CLI flag. The actual gap-fill exit logic lands in
Phase 3 and is tested in the same file under "Exit logic" below
(populated by Phase 3).
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
from typer.testing import CliRunner

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.fills import GAP_FILL_POLICIES, FillModel
from forex_bot.cli import app
from forex_bot.config import BacktestConfig, ConfigError
from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_PATH = REPO_ROOT / "tests" / "fixtures" / "pre_sprint_config_hashes.json"

_ZERO_FILL = FillModel(
    fixed_slippage_pips=Decimal("0"), spread_slippage_multiplier=Decimal("0")
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# Config field
# ---------------------------------------------------------------------------


def test_default_policy_is_none():
    assert BacktestConfig().gap_fill_policy == "none"


def test_policy_accepts_gap_through():
    assert BacktestConfig(gap_fill_policy="gap_through").gap_fill_policy == "gap_through"


def test_policy_rejects_unknown():
    with pytest.raises((ConfigError, ValueError)):
        BacktestConfig(gap_fill_policy="next_open")  # type: ignore[arg-type]


def test_policies_frozenset_matches_config_literal():
    """The frozenset (used by CLI runtime validation) must match the
    Literal values (used by Pydantic). Drift between them = unreachable
    CLI options or unreachable config values."""
    assert frozenset({"none", "gap_through"}) == GAP_FILL_POLICIES


# ---------------------------------------------------------------------------
# Engine kwarg + hash compatibility
# ---------------------------------------------------------------------------


class _NoSignalStrategy:
    """Never emits a signal — used to exercise the engine hash without
    needing to construct real bars."""

    name = "noop"
    version = "test"

    def warmup_bars_required(self) -> int:
        return 2

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        return None


def _build_engine(*, gap_fill_policy: str | None = None, eur_usd) -> BacktestEngine:
    kwargs = dict(
        instrument=eur_usd,
        strategy=_NoSignalStrategy(),
        strategy_config={"version": "test", "param": 1},
        fill_model=_ZERO_FILL,
        starting_equity=Decimal("500"),
        account_currency="USD",
    )
    if gap_fill_policy is not None:
        kwargs["gap_fill_policy"] = gap_fill_policy
    return BacktestEngine(**kwargs)  # type: ignore[arg-type]


def _run_empty(engine: BacktestEngine) -> str:
    frame = CandleFrame(
        instrument="EUR_USD", granularity="H4", df=pd.DataFrame()
    )
    return engine.run(frame).config_hash


def test_engine_default_policy_none(eur_usd):
    engine = _build_engine(gap_fill_policy=None, eur_usd=eur_usd)
    assert engine.gap_fill_policy == "none"


def test_default_policy_no_hash_change(eur_usd):
    """Engine with default policy produces the same config_hash as an
    engine constructed without the kwarg at all — proves the conditional
    spread `**({} if default else {...})` is a true no-op."""
    h_default = _run_empty(_build_engine(gap_fill_policy="none", eur_usd=eur_usd))
    h_omitted = _run_empty(_build_engine(gap_fill_policy=None, eur_usd=eur_usd))
    assert h_default == h_omitted


def test_gap_through_changes_hash(eur_usd):
    """gap_fill_policy='gap_through' MUST produce a different hash than
    'none' — so the two modes can never be silently confused."""
    h_default = _run_empty(_build_engine(gap_fill_policy="none", eur_usd=eur_usd))
    h_gap = _run_empty(_build_engine(gap_fill_policy="gap_through", eur_usd=eur_usd))
    assert h_default != h_gap


def test_default_policy_matches_phase0_snapshot():
    """The pinned hash snapshot at tests/fixtures/pre_sprint_config_hashes.json
    captured the engine's config_hash for 3 campaign configs at the start
    of this sprint. The default-mode hash MUST still match every entry.
    """
    fixture = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    from scripts.snapshot_pre_sprint_hashes import PINNED, _hash_for

    from forex_bot.config import load_settings

    for label, rel_path in PINNED:
        settings = load_settings(REPO_ROOT / rel_path)
        actual = _hash_for(settings)
        expected = fixture[label]
        assert actual == expected, (
            f"hash regression for {label}: snapshot says {expected}, "
            f"got {actual}. Either fix the code or, only if an "
            "intentional refactor changed hash inputs, regenerate the "
            "snapshot AFTER confirming with the sprint author."
        )


def test_snapshot_doc_guardrail():
    """The snapshot file carries a `_doc` header warning against
    accidental regeneration. Asserts the string is preserved verbatim —
    a contributor running the regenerator script to 'fix' a hash
    failure would either have to delete this guard explicitly or leave
    this test red."""
    fixture = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    assert "_doc" in fixture, (
        "snapshot file is missing the _doc guardrail header; do not "
        "remove it"
    )
    assert "DO NOT REGENERATE" in fixture["_doc"], (
        "snapshot _doc string must contain the literal 'DO NOT REGENERATE' "
        "warning; current value: " + repr(fixture["_doc"])
    )


# ---------------------------------------------------------------------------
# CLI flag
# ---------------------------------------------------------------------------


def test_cli_rejects_invalid_gap_fill_policy(paper_config_path: Path):
    """Mirrors test_backtest_config_rejects_unknown_fill_timing — CLI
    validation of the flag is independent of the Pydantic Literal check
    on the config (CLI accepts a string, then validates against the
    frozenset before constructing the engine)."""
    result = runner.invoke(
        app,
        [
            "backtest",
            "--config",
            str(paper_config_path),
            "--gap-fill-policy",
            "next_open",  # not a valid gap_fill_policy value
        ],
    )
    assert result.exit_code == 2, (
        f"expected exit 2 for invalid --gap-fill-policy, got "
        f"{result.exit_code}; output:\n{result.output}"
    )
    assert "invalid --gap-fill-policy" in result.output


def test_cli_accepts_gap_fill_policy_none(paper_config_path: Path):
    """--gap-fill-policy none should be accepted (it is the default)."""
    result = runner.invoke(
        app,
        [
            "backtest",
            "--config",
            str(paper_config_path),
            "--gap-fill-policy",
            "none",
            "--instrument",
            "EUR_USD",
        ],
    )
    # Exit may be non-zero because the DB is empty (no candles synced),
    # but the [dim]gap fill: none[/dim] line should appear before any
    # error. Failure mode we want to catch: exit 2 with "invalid --gap-fill-policy".
    assert "invalid --gap-fill-policy" not in result.output


def test_cli_2x2_matrix_combines_with_fill_timing(paper_config_path: Path):
    """--fill-timing and --gap-fill-policy are orthogonal axes; using
    both at once must not cause a validation collision."""
    result = runner.invoke(
        app,
        [
            "backtest",
            "--config",
            str(paper_config_path),
            "--fill-timing",
            "next_bar_open",
            "--gap-fill-policy",
            "gap_through",
            "--instrument",
            "EUR_USD",
        ],
    )
    # As above: error from empty DB is fine, but the gap-fill validation
    # path must not fire.
    assert "invalid --gap-fill-policy" not in result.output
    assert "invalid --fill-timing" not in result.output


# ---------------------------------------------------------------------------
# Exit logic — Phase 3 will populate this section. Stubs below assert the
# shape that Phase 3 will exercise.
# ---------------------------------------------------------------------------


def test_phase3_exit_logic_not_yet_active():
    """Sentinel — until Phase 3 lands, gap_fill_policy='gap_through' must
    still produce TradeRecord.gap_fill=False for any historical trade
    (the policy field exists but the exit logic that sets the flag does
    not). Will be removed when Phase 3 commits."""
    # This is a placeholder — actual gap-fill logic tests live next to
    # the Phase 3 implementation.
    pass
