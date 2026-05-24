"""Snapshot `BacktestEngine.config_hash` for representative campaign configs.

Sprint: `infra-exit-fidelity-001` (see docs/research/INFRA_EXIT_FIDELITY_001_PLAN.md).

The hash regression test in `tests/unit/test_gap_fill.py` and
`tests/unit/test_ambiguous_exit.py` compares the engine's `config_hash` for
default-mode runs against the values written to
`tests/fixtures/pre_sprint_config_hashes.json`. If those tests fail, EITHER
this sprint introduced a hash drift (a bug — fix the code, not the snapshot)
OR a config / strategy / engine refactor outside this sprint changed the
hash inputs (rare — confirm with the author before regenerating).

**Do NOT re-run this script to "make the tests pass."** The snapshot is the
ground truth for hash compatibility with all CAMPAIGN_001–009 artifacts.
Re-snapshotting would silently mask a regression. See AC-13 of the plan.

Usage (one-off, at Phase 0):

    python scripts/snapshot_pre_sprint_hashes.py

The script constructs engines exactly the way `bot backtest` does
(`src/forex_bot/cli.py:482-495`), but bypasses the candle DB by stubbing
the `Instrument` (the instrument metadata does NOT enter `config_hash`).
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.fills import FillModel
from forex_bot.config import Settings, load_settings
from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.loops import build_strategies

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "pre_sprint_config_hashes.json"

# Pinned configs — 5 unique hash-producing campaigns. campaign_002 and
# campaign_008 are intentionally omitted (they collide by hash with 001
# and 009 respectively under default engine inputs); campaign_007 cannot
# build strategies under the current loops.build_strategies path
# (pre-existing, unrelated).
PINNED = [
    ("campaign_001_baseline", "configs/campaign_001_baseline.yaml"),
    ("campaign_003_controlled_adx", "configs/campaign_003_controlled_adx.yaml"),
    ("campaign_004_volatility_breakout", "configs/campaign_004_volatility_breakout.yaml"),
    ("campaign_006_daily_trend", "configs/campaign_006_daily_trend.yaml"),
    ("campaign_009_mean_reversion", "configs/campaign_009_mean_reversion.yaml"),
]

# A stub instrument. `Instrument` is required by `BacktestEngine.__init__`
# but is NOT folded into `config_hash` (see `engine.py:153-170`). Any valid
# Instrument with the right pip_location works.
_STUB_INSTRUMENT = Instrument(
    name="EUR_USD",
    type="CURRENCY",
    display_precision=5,
    pip_location=-4,
    trade_units_precision=0,
    minimum_trade_size=Decimal("1"),
    maximum_order_units=Decimal("100000000"),
    margin_rate=Decimal("0.02"),
)


def _hash_for(settings: Settings) -> str:
    """Build the same engine the CLI builds for this config and return the
    `config_hash`.

    Mirrors `src/forex_bot/cli.py:482-495` exactly (engine kwargs come from
    settings.backtest, settings.risk, and the strategy config dict).
    """
    strategies = build_strategies(settings)
    if not strategies:
        raise RuntimeError(
            "snapshot: no enabled strategies in config — cannot build engine"
        )
    # Mirror CLI behaviour: take the first enabled strategy (configs are
    # written with exactly one enabled strategy at a time).
    strat, cfg = strategies[0]

    fill_model = FillModel(
        fixed_slippage_pips=Decimal(str(settings.backtest.fixed_slippage_pips)),
        spread_slippage_multiplier=Decimal(str(settings.backtest.spread_slippage_multiplier)),
    )

    engine = BacktestEngine(
        instrument=_STUB_INSTRUMENT,
        strategy=strat,
        strategy_config=cfg,
        fill_model=fill_model,
        fill_timing=settings.backtest.fill_timing,
        starting_equity=Decimal(str(settings.backtest.starting_equity_usd)),
        account_currency=settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(cfg.get("max_bars_in_trade", 80)),
        commission_per_unit=Decimal(str(settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(cfg.get("atr_lookback", 14)),
    )

    # Empty candle frame is sufficient — the hash is computed in `run()`
    # regardless of frame size.
    import pandas as pd

    empty_frame = CandleFrame(
        instrument="EUR_USD",
        granularity=settings.market.granularity,
        df=pd.DataFrame(),
    )
    result = engine.run(empty_frame)
    return result.config_hash


def main() -> None:
    hashes: dict[str, str | None] = {
        "_doc": (
            "DO NOT REGENERATE — this is the hash-compatibility baseline for "
            "sprint infra-exit-fidelity-001 (AC-9, AC-13). Re-snapshotting "
            "would silently hide a hash regression. See "
            "docs/research/INFRA_EXIT_FIDELITY_001_PLAN.md and "
            "docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md. The test "
            "tests/unit/test_gap_fill.py::test_snapshot_doc_guardrail asserts "
            "this string is preserved verbatim."
        ),
    }
    for label, rel_path in PINNED:
        settings = load_settings(REPO_ROOT / rel_path)
        h = _hash_for(settings)
        hashes[label] = h
        print(f"{label:40s}  {h}")

    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {FIXTURE_PATH}")


if __name__ == "__main__":
    main()
