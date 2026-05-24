#!/usr/bin/env python3
"""CAMPAIGN_013 walk-forward evidence runner.

Drives ``cross_pair_currency_strength_rotation 0.1.0-c013`` against
each fold's TEST window from a walk-forward plan, on the 7-pair H4
OANDA practice universe, and emits per-fold metrics + aggregate + a
campaign-level ``WalkForwardResults`` JSON/Markdown via the existing
``research.walk_forward`` harness.

**CAMPAIGN_013 is a research candidate scaffold; this runner produces
research evidence but cannot approve any strategy.** Even a clean
PASS produces ``RESEARCH_PASS_UNAPPROVED`` pending the verifier-
extension sprint + a deliberate human approval action per
``STRATEGY_APPROVAL_PROCESS.md``.

Strict rules — enforced by this script:

  * The strategy must be ``cross_pair_currency_strength_rotation``
    (i.e. ``strategy.enabled == ['cross_pair_currency_strength_rotation']``).
  * The strategy parameters must match the pre-commit verbatim
    (``CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`` §4). Mismatch aborts
    before any backtest fires.
  * The walk-forward plan must be ``parameter_mode == 'frozen'``,
    ``split_style == 'rolling'``, ``strategy_evidence: false``.
  * Every per-pair, per-fold candle source must be ``oanda-practice``
    (no synthetic fallback).
  * The runner makes no broker call. It reads the local SQLite store
    only.
  * No tuning. No parameter sweep. No re-run with altered parameters
    to improve results. No relaxing of ``max_open_positions`` or
    risk settings.

**CROSS-PAIR RUNNER INTEGRATION CONTRACT (binding):**

  The strategy requires sibling-pair close series via
  ``ctx.config["cross_pair_closes"]``. The runner MUST:

    1. Load all 7 pairs' completed H4 candles for the test window
       + warm-up margin.
    2. Align all 7 pairs' completed H4 close series to a common
       timestamp index (intersection of completed bars).
    3. Build per-pair closes-only ``pd.Series`` indexed by the
       common index.
    4. Inject the dict ``{pair: pd.Series}`` into
       ``strategy_config["cross_pair_closes"]`` for each pair's
       engine invocation.
    5. Fail closed (classify verdict as ``BLOCKED``) if any required
       pair is missing, misaligned, non-finite, or insufficient.

  If the runner cannot satisfy this contract, the verdict is
  ``BLOCKED`` — NOT a strategy-rule modification.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.exporters import write_summary_json, write_trades_csv
from forex_bot.backtesting.fills import FillModel
from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo, InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.cross_pair_currency_strength_rotation import (
    CrossPairCurrencyStrengthRotationStrategy,
)

# isort: off
from research.walk_forward import (
    AggregateMetrics,
    Fold,
    FoldMetrics,
    ParameterMode,
    SplitStyle,
    WalkForwardPlan,
    WalkForwardResults,
    render_results_md,
)
# isort: on

REQUIRED_DATA_SOURCE = "oanda-practice"
EXPECTED_VERSION = "0.1.0-c013"
EXPECTED_STRATEGY = "cross_pair_currency_strength_rotation"
EXPECTED_PAIRS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)

# Pre-commit frozen parameter values (verbatim from
# CAMPAIGN_013_PRECOMMIT_CHECKLIST.md §4). Any mismatch aborts
# before any backtest fires.
FROZEN_PARAMETERS: dict[str, Any] = {
    "version": EXPECTED_VERSION,
    "timeframe": "H4",
    "currency_strength_lookback_bars": 24,
    "rank_gap_threshold": 4,
    "atr_lookback": 14,
    "atr_stop_multiple": 2.0,
    "trailing_stop_atr_multiple": None,
    "max_bars_in_trade": 6,
    "min_atr_pips": {},
}

# Inherited gate thresholds (verbatim from CAMPAIGN_010 / 011 / 012).
TEST_FOLD_GATES = {
    "expectancy_r_min": 0.05,
    "profit_factor_min": 1.10,
    "trade_count_min": 30,
    "pairs_positive_min": 4,
    "single_pair_dominance_max_pct": 60.0,
}
AGGREGATE_GATES = {
    "fold_pass_rate_min": 1.0,
    "fold_count_min": 6,
    "expectancy_r_min": 0.05,
    "profit_factor_min": 1.10,
    "trade_count_min": 200,
    "pairs_positive_min": 4,
    "single_fold_dominance_max_pct": 60.0,
    "single_pair_dominance_max_pct": 40.0,
}


# ---------------------------------------------------------------------------
# Provenance helpers


def _git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        return ""
    return r.stdout.strip()


# ---------------------------------------------------------------------------
# Cross-pair runner integration contract


@dataclass
class CrossPairFoldContext:
    """Per-fold cross-pair closes context.

    Built once per fold: holds the 7-pair aligned closes (one
    ``pd.Series`` per pair) and runner-level diagnostics.
    """

    fold_index: int
    cross_pair_closes: dict[str, pd.Series]
    common_index_length: int
    per_pair_raw_lengths: dict[str, int]
    contract_satisfied: bool
    blocker: str | None  # None when contract satisfied


def _fold_dates_to_dts(fold: Fold) -> tuple[datetime, datetime]:
    """Convert fold test-window dates to UTC datetimes that cover the
    inclusive day range — PLUS warm-up margin (250 calendar days)."""
    warm_up_days_margin = 250
    start = datetime.combine(
        fold.test_start - timedelta(days=warm_up_days_margin),
        datetime.min.time(), tzinfo=UTC,
    )
    end = datetime.combine(
        fold.test_end, datetime.max.time().replace(microsecond=0), tzinfo=UTC
    )
    return start, end


def _build_cross_pair_context(
    *,
    fold: Fold,
    candle_repo: CandleRepo,
    ds_repo: DataSourceRepo,
) -> CrossPairFoldContext:
    """Build the cross-pair closes dict for this fold (binding contract).

    Loads all 7 pairs' completed H4 candles in the (test window +
    warm-up) window; verifies each pair's data source is
    ``oanda-practice``; aligns all 7 pairs to a common timestamp
    index (intersection of completed bars); builds per-pair closes-
    only ``pd.Series``; returns a ``CrossPairFoldContext`` with the
    aligned dict + diagnostics.

    If any pair is missing, misaligned, or insufficient, returns a
    context with ``contract_satisfied=False`` and a populated
    ``blocker`` string.
    """
    frm, to = _fold_dates_to_dts(fold)
    per_pair_series: dict[str, pd.Series] = {}
    per_pair_raw_lengths: dict[str, int] = {}

    # Load each pair's completed-only H4 closes.
    for pair in EXPECTED_PAIRS:
        src = (ds_repo.latest_for(pair, "H4") or {}).get("source", "unknown")
        if src != REQUIRED_DATA_SOURCE:
            return CrossPairFoldContext(
                fold_index=fold.fold_index,
                cross_pair_closes={},
                common_index_length=0,
                per_pair_raw_lengths=per_pair_raw_lengths,
                contract_satisfied=False,
                blocker=(
                    f"pair {pair} H4 source is {src!r}, expected "
                    f"{REQUIRED_DATA_SOURCE!r}"
                ),
            )
        rows = candle_repo.list(
            pair, "H4", completed_only=True,
            from_time=frm, to_time=to,  # type: ignore[arg-type]
        )
        per_pair_raw_lengths[pair] = len(rows)
        if not rows:
            return CrossPairFoldContext(
                fold_index=fold.fold_index,
                cross_pair_closes={},
                common_index_length=0,
                per_pair_raw_lengths=per_pair_raw_lengths,
                contract_satisfied=False,
                blocker=(
                    f"pair {pair} has zero candles in fold "
                    f"{fold.fold_index} test window + warm-up"
                ),
            )
        # CandleFrame.from_candles handles bid/ask -> mid conversion;
        # we want the resulting df["close"] indexed by tz-aware UTC.
        frame = CandleFrame.from_candles(pair, "H4", rows)  # type: ignore[arg-type]
        if frame.df.empty:
            return CrossPairFoldContext(
                fold_index=fold.fold_index,
                cross_pair_closes={},
                common_index_length=0,
                per_pair_raw_lengths=per_pair_raw_lengths,
                contract_satisfied=False,
                blocker=f"pair {pair} CandleFrame is empty after conversion",
            )
        per_pair_series[pair] = frame.df["close"]

    # Align all 7 pairs to a common index (intersection of timestamps).
    common_index = None
    for series in per_pair_series.values():
        if common_index is None:
            common_index = series.index
        else:
            common_index = common_index.intersection(series.index)
    if common_index is None or len(common_index) == 0:
        return CrossPairFoldContext(
            fold_index=fold.fold_index,
            cross_pair_closes={},
            common_index_length=0,
            per_pair_raw_lengths=per_pair_raw_lengths,
            contract_satisfied=False,
            blocker="common index empty after intersection of 7 pairs",
        )
    # Need at least currency_strength_lookback_bars + 1 = 25 bars to
    # produce any signal.
    if len(common_index) < 25:
        return CrossPairFoldContext(
            fold_index=fold.fold_index,
            cross_pair_closes={},
            common_index_length=len(common_index),
            per_pair_raw_lengths=per_pair_raw_lengths,
            contract_satisfied=False,
            blocker=(
                f"common index has only {len(common_index)} bars; "
                f"need >= 25 for currency_strength_lookback_bars=24 + 1"
            ),
        )
    aligned: dict[str, pd.Series] = {
        pair: per_pair_series[pair].loc[common_index] for pair in EXPECTED_PAIRS
    }
    # Validate finite + positive endpoints (defensive — the strategy's
    # R4 also checks, but failing here lets us classify the fold as
    # BLOCKED rather than running 7 backtests that all return None).
    for pair, s in aligned.items():
        if s.isna().any():
            return CrossPairFoldContext(
                fold_index=fold.fold_index,
                cross_pair_closes={},
                common_index_length=len(common_index),
                per_pair_raw_lengths=per_pair_raw_lengths,
                contract_satisfied=False,
                blocker=f"pair {pair} aligned series contains NaN",
            )
        if (s <= 0).any():
            return CrossPairFoldContext(
                fold_index=fold.fold_index,
                cross_pair_closes={},
                common_index_length=len(common_index),
                per_pair_raw_lengths=per_pair_raw_lengths,
                contract_satisfied=False,
                blocker=f"pair {pair} aligned series contains <= 0 close",
            )

    return CrossPairFoldContext(
        fold_index=fold.fold_index,
        cross_pair_closes=aligned,
        common_index_length=len(common_index),
        per_pair_raw_lengths=per_pair_raw_lengths,
        contract_satisfied=True,
        blocker=None,
    )


# ---------------------------------------------------------------------------
# Per-fold per-pair backtest


@dataclass
class PairFoldRun:
    fold_index: int
    instrument: str
    trade_count: int
    expectancy_r: float
    return_pct: float
    profit_factor: float | None
    max_drawdown_pct: float
    win_rate: float
    bars_in_test_window: int
    long_trades: int
    short_trades: int
    starting_equity: float
    final_equity: float
    data_request_hash: str
    config_hash: str
    rejection_count: int
    rejection_counts: dict[str, int]
    risk_engine_used: bool

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _run_pair_fold(
    *,
    settings: Any,
    fold: Fold,
    instrument: str,
    cross_pair_ctx: CrossPairFoldContext,
    candle_repo: CandleRepo,
    ds_repo: DataSourceRepo,
    instr_repo: InstrumentRepo,
    risk_engine: RiskEngine,
    strategy_cfg: dict[str, Any],
    out_dir: Path,
) -> PairFoldRun:
    meta = instr_repo.get(instrument)
    if meta is None:
        raise SystemExit(f"missing instrument metadata for {instrument}")
    src = (ds_repo.latest_for(instrument, "H4") or {}).get("source", "unknown")
    if src != REQUIRED_DATA_SOURCE:
        raise SystemExit(
            f"data source for {instrument} H4 is {src!r}, expected "
            f"{REQUIRED_DATA_SOURCE!r}. CAMPAIGN_013 aborts."
        )
    frm, to = _fold_dates_to_dts(fold)
    rows = candle_repo.list(
        instrument, "H4", completed_only=True,
        from_time=frm, to_time=to,  # type: ignore[arg-type]
    )
    if not rows:
        raise SystemExit(
            f"no candles for {instrument} fold={fold.fold_index} "
            f"test_window {fold.test_start}..{fold.test_end}"
        )
    frame = CandleFrame.from_candles(instrument, "H4", rows)  # type: ignore[arg-type]
    data_hash = compute_data_request_hash(
        instrument=instrument, granularity="H4",
        from_time=frm.isoformat(), to_time=to.isoformat(),
        source=src, candle_count=len(rows),
    )
    # Inject cross_pair_closes into the strategy_config dict for this
    # invocation (cross-pair runner integration contract; binding).
    strategy_cfg_with_cross_pair = dict(strategy_cfg)
    strategy_cfg_with_cross_pair["cross_pair_closes"] = cross_pair_ctx.cross_pair_closes
    engine = BacktestEngine(
        instrument=meta,
        strategy=CrossPairCurrencyStrengthRotationStrategy(version=strategy_cfg["version"]),
        strategy_config=strategy_cfg_with_cross_pair,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(settings.backtest.fixed_slippage_pips)),
            spread_slippage_multiplier=Decimal(
                str(settings.backtest.spread_slippage_multiplier)
            ),
        ),
        starting_equity=Decimal(str(settings.backtest.starting_equity_usd)),
        account_currency=settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(strategy_cfg["max_bars_in_trade"]),
        commission_per_unit=Decimal(str(settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=strategy_cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(strategy_cfg["atr_lookback"]),
        risk_engine=risk_engine,
        settings=settings,
    )
    result = engine.run(frame, data_request_hash=data_hash)
    fold_dir = out_dir / "folds" / f"fold_{fold.fold_index:02d}"
    fold_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"fold_{fold.fold_index:02d}_{instrument}"
    write_summary_json(result, fold_dir / f"{prefix}_summary.json")
    write_trades_csv(result, fold_dir / f"{prefix}_trades.csv")
    long_trades = sum(1 for t in result.trades if t.side == "long")
    short_trades = sum(1 for t in result.trades if t.side == "short")
    return PairFoldRun(
        fold_index=fold.fold_index,
        instrument=instrument,
        trade_count=result.metrics.trade_count,
        expectancy_r=float(result.metrics.expectancy_r),
        return_pct=float(result.metrics.total_return_pct),
        profit_factor=(
            None if result.metrics.profit_factor == float("inf")
            else float(result.metrics.profit_factor)
        ),
        max_drawdown_pct=float(result.metrics.max_drawdown_pct),
        win_rate=float(result.metrics.win_rate),
        bars_in_test_window=len(rows),
        long_trades=long_trades,
        short_trades=short_trades,
        starting_equity=float(result.metrics.starting_equity),
        final_equity=float(result.metrics.final_equity),
        data_request_hash=data_hash,
        config_hash=result.config_hash,
        rejection_count=len(result.rejected_signals),
        rejection_counts=dict(result.rejection_counts),
        risk_engine_used=result.risk_engine_used,
    )


# ---------------------------------------------------------------------------
# Fold-level aggregation


@dataclass
class FoldRollup:
    fold_index: int
    pair_runs: list[PairFoldRun]
    cross_pair_diagnostics: dict[str, Any]

    @property
    def trade_count(self) -> int:
        return sum(p.trade_count for p in self.pair_runs)

    @property
    def aggregate_return_pct(self) -> float:
        return sum(p.return_pct for p in self.pair_runs)

    @property
    def expectancy_r(self) -> float:
        total = sum(p.trade_count for p in self.pair_runs)
        if total == 0:
            return 0.0
        return sum(p.expectancy_r * p.trade_count for p in self.pair_runs) / total

    @property
    def pairs_positive(self) -> int:
        return sum(1 for p in self.pair_runs if p.expectancy_r > 0.0)

    @property
    def single_pair_dominance_pct(self) -> float:
        total = sum(abs(p.return_pct) for p in self.pair_runs)
        if total == 0:
            return 0.0
        return 100.0 * max(abs(p.return_pct) for p in self.pair_runs) / total

    def profit_factor(self) -> float | None:
        gains = sum(p.return_pct for p in self.pair_runs if p.return_pct > 0)
        losses = -sum(p.return_pct for p in self.pair_runs if p.return_pct < 0)
        if losses == 0:
            return None if gains > 0 else 0.0
        return gains / losses

    def gate_vector(self) -> dict[str, bool]:
        pf = self.profit_factor()
        pf_pass = (pf is None and self.trade_count > 0) or (
            pf is not None and pf >= TEST_FOLD_GATES["profit_factor_min"]
        )
        return {
            "expectancy_r_ge_0p05": self.expectancy_r >= TEST_FOLD_GATES["expectancy_r_min"],
            "profit_factor_ge_1p10": pf_pass,
            "trade_count_ge_30": self.trade_count >= TEST_FOLD_GATES["trade_count_min"],
            "pairs_positive_ge_4_of_7": self.pairs_positive >= TEST_FOLD_GATES["pairs_positive_min"],
            "single_pair_dominance_le_60pct": self.single_pair_dominance_pct
            <= TEST_FOLD_GATES["single_pair_dominance_max_pct"],
        }

    def passes(self) -> bool:
        return all(self.gate_vector().values())


# ---------------------------------------------------------------------------
# Aggregate


def _aggregate(rollups: list[FoldRollup]) -> dict[str, Any]:
    fold_count = len(rollups)
    folds_passing = sum(1 for r in rollups if r.passes())
    total_trades = sum(r.trade_count for r in rollups)
    pair_totals: dict[str, float] = {p: 0.0 for p in EXPECTED_PAIRS}
    pair_trade_counts: dict[str, int] = {p: 0 for p in EXPECTED_PAIRS}
    pair_expectancy_weighted: dict[str, float] = {p: 0.0 for p in EXPECTED_PAIRS}
    for r in rollups:
        for pr in r.pair_runs:
            pair_totals[pr.instrument] += pr.return_pct
            pair_trade_counts[pr.instrument] += pr.trade_count
            pair_expectancy_weighted[pr.instrument] += pr.expectancy_r * pr.trade_count
    aggregate_return_pct = sum(r.aggregate_return_pct for r in rollups)
    aggregate_expectancy_r = (
        sum(r.expectancy_r * r.trade_count for r in rollups) / total_trades
        if total_trades > 0 else 0.0
    )
    pair_expectancy: dict[str, float] = {}
    for pair, weighted in pair_expectancy_weighted.items():
        n = pair_trade_counts[pair]
        pair_expectancy[pair] = (weighted / n) if n > 0 else 0.0
    pairs_positive_count = sum(1 for p in EXPECTED_PAIRS if pair_expectancy[p] > 0)
    total_abs_return = sum(abs(v) for v in pair_totals.values())
    single_pair_dom_pct = (
        100.0 * max(abs(v) for v in pair_totals.values()) / total_abs_return
        if total_abs_return > 0 else 0.0
    )
    fold_abs_returns = [abs(r.aggregate_return_pct) for r in rollups]
    sum_abs = sum(fold_abs_returns) or 0.0
    single_fold_dom_pct = (
        100.0 * max(fold_abs_returns) / sum_abs if sum_abs > 0 else 0.0
    )
    gains = sum(r.aggregate_return_pct for r in rollups if r.aggregate_return_pct > 0)
    losses = -sum(r.aggregate_return_pct for r in rollups if r.aggregate_return_pct < 0)
    if losses == 0:
        agg_pf: float | None = None if gains > 0 else 0.0
    else:
        agg_pf = gains / losses
    pf_pass = (agg_pf is None and total_trades > 0) or (
        agg_pf is not None and agg_pf >= AGGREGATE_GATES["profit_factor_min"]
    )
    gate_vector = {
        "fold_pass_rate_eq_100pct": (folds_passing == fold_count and fold_count > 0),
        "fold_count_ge_6": fold_count >= AGGREGATE_GATES["fold_count_min"],
        "expectancy_r_ge_0p05": aggregate_expectancy_r
        >= AGGREGATE_GATES["expectancy_r_min"],
        "profit_factor_ge_1p10": pf_pass,
        "trade_count_ge_200": total_trades >= AGGREGATE_GATES["trade_count_min"],
        "pairs_positive_ge_4_of_7": pairs_positive_count
        >= AGGREGATE_GATES["pairs_positive_min"],
        "single_fold_dominance_le_60pct": single_fold_dom_pct
        <= AGGREGATE_GATES["single_fold_dominance_max_pct"],
        "single_pair_dominance_le_40pct": single_pair_dom_pct
        <= AGGREGATE_GATES["single_pair_dominance_max_pct"],
    }
    overall_pass = all(gate_vector.values())
    return {
        "fold_count": fold_count,
        "folds_passing": folds_passing,
        "fold_pass_rate": (folds_passing / fold_count) if fold_count > 0 else 0.0,
        "total_trades": total_trades,
        "aggregate_return_pct": aggregate_return_pct,
        "aggregate_expectancy_r": aggregate_expectancy_r,
        "profit_factor": agg_pf,
        "pairs_positive_count": pairs_positive_count,
        "pair_returns_pct": pair_totals,
        "pair_trade_counts": pair_trade_counts,
        "pair_expectancy_r": pair_expectancy,
        "single_fold_dominance_pct": single_fold_dom_pct,
        "single_pair_dominance_pct": single_pair_dom_pct,
        "gates": gate_vector,
        "overall_verdict": "PASS" if overall_pass else "REJECT",
    }


# ---------------------------------------------------------------------------
# Frozen-parameter enforcement


def _assert_frozen(strategy_cfg: dict[str, Any]) -> None:
    """Fail-closed if the loaded YAML deviates from the pre-commit."""
    mismatched: list[str] = []
    for key, expected in FROZEN_PARAMETERS.items():
        got = strategy_cfg.get(key)
        if isinstance(expected, dict) and isinstance(got, dict):
            if got != expected:
                mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
        elif got != expected:
            mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
    if mismatched:
        raise SystemExit(
            "CAMPAIGN_013 frozen-parameter mismatch — see "
            "CAMPAIGN_013_PRECOMMIT_CHECKLIST.md §4:\n"
            + "\n".join(mismatched)
        )


# ---------------------------------------------------------------------------
# CLI


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--plan", required=True, help="Path to walk_forward/plan.json")
    ap.add_argument("--out", required=True, help="Campaign output directory")
    args = ap.parse_args()

    config_path = Path(args.config)
    plan_path = Path(args.plan)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    settings = load_settings(config_path)

    sc = settings.strategy
    if sc.enabled != [EXPECTED_STRATEGY] or sc.cross_pair_currency_strength_rotation is None:
        raise SystemExit(
            f"CAMPAIGN_013 config must enable only {EXPECTED_STRATEGY!r}; "
            f"got {sc.enabled}"
        )
    strategy_cfg = sc.cross_pair_currency_strength_rotation.model_dump()
    _assert_frozen(strategy_cfg)

    pairs = tuple(settings.market.instruments)
    if pairs != EXPECTED_PAIRS:
        raise SystemExit(
            f"CAMPAIGN_013 universe mismatch — got {pairs}, expected "
            f"{EXPECTED_PAIRS}"
        )

    plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
    plan = WalkForwardPlan(**plan_payload)
    if plan.parameter_mode is not ParameterMode.FROZEN:
        raise SystemExit(
            f"CAMPAIGN_013 plan must use parameter_mode=frozen; "
            f"got {plan.parameter_mode.value!r}"
        )
    if plan.split_style is not SplitStyle.ROLLING:
        raise SystemExit(
            f"CAMPAIGN_013 plan must use split_style=rolling; "
            f"got {plan.split_style.value!r}"
        )
    if plan.strategy_evidence:
        raise SystemExit("plan.strategy_evidence must be False")
    if len(plan.folds) < AGGREGATE_GATES["fold_count_min"]:
        raise SystemExit(
            f"plan has only {len(plan.folds)} folds; "
            f"≥ {AGGREGATE_GATES['fold_count_min']} required"
        )

    db = Database(settings.app.database_path)
    candle_repo = CandleRepo(db)
    ds_repo = DataSourceRepo(db)
    instr_repo = InstrumentRepo(db)
    risk_engine = RiskEngine(settings, mode="backtest")

    print(
        f"=== CAMPAIGN_013 walk-forward run started "
        f"{datetime.now(UTC).isoformat()} ==="
    )
    print(f"folds: {len(plan.folds)}  pairs: {len(pairs)}")
    print(
        f"cross-pair: lookback={strategy_cfg['currency_strength_lookback_bars']} "
        f"rank_gap_threshold={strategy_cfg['rank_gap_threshold']} "
        f"atr_stop={strategy_cfg['atr_stop_multiple']}*ATR{strategy_cfg['atr_lookback']}"
    )

    t0 = time.time()
    rollups: list[FoldRollup] = []
    blocked_folds: list[tuple[int, str]] = []
    for fold in plan.folds:
        # Build the cross-pair context for this fold (binding contract).
        cross_pair_ctx = _build_cross_pair_context(
            fold=fold,
            candle_repo=candle_repo,
            ds_repo=ds_repo,
        )
        if not cross_pair_ctx.contract_satisfied:
            print(
                f"  fold {fold.fold_index:>2d} BLOCKED: {cross_pair_ctx.blocker}"
            )
            blocked_folds.append((fold.fold_index, cross_pair_ctx.blocker or ""))
            continue
        print(
            f"  fold {fold.fold_index:>2d} cross-pair ctx ready: "
            f"common_index={cross_pair_ctx.common_index_length} bars"
        )
        pair_runs: list[PairFoldRun] = []
        for pair in pairs:
            run = _run_pair_fold(
                settings=settings,
                fold=fold,
                instrument=pair,
                cross_pair_ctx=cross_pair_ctx,
                candle_repo=candle_repo,
                ds_repo=ds_repo,
                instr_repo=instr_repo,
                risk_engine=risk_engine,
                strategy_cfg=strategy_cfg,
                out_dir=out_dir,
            )
            pair_runs.append(run)
            print(
                f"  fold {fold.fold_index:>2d} test=[{fold.test_start}..{fold.test_end}] "
                f"{pair}: trades={run.trade_count:>4d} exp_r={run.expectancy_r:+.3f} "
                f"ret_pct={run.return_pct:+.2f}%"
            )
        cross_pair_diagnostics = {
            "common_index_length": cross_pair_ctx.common_index_length,
            "per_pair_raw_lengths": cross_pair_ctx.per_pair_raw_lengths,
            "contract_satisfied": cross_pair_ctx.contract_satisfied,
        }
        rollups.append(
            FoldRollup(
                fold_index=fold.fold_index,
                pair_runs=pair_runs,
                cross_pair_diagnostics=cross_pair_diagnostics,
            )
        )

    elapsed = time.time() - t0
    print(f"\nbacktests complete in {elapsed:.1f}s")
    if blocked_folds:
        print(
            f"\n!! WARNING: {len(blocked_folds)} fold(s) BLOCKED by cross-pair contract:"
        )
        for fi, blk in blocked_folds:
            print(f"  fold {fi}: {blk}")

    # If any folds were blocked, the verdict is BLOCKED (regardless of
    # any other fold metrics).
    blocked_verdict = bool(blocked_folds)

    fold_metrics: list[FoldMetrics] = []
    for r in rollups:
        pf = r.profit_factor()
        fold_metrics.append(
            FoldMetrics(
                fold_index=r.fold_index,
                total_trades=r.trade_count,
                bars_in_test_window=sum(p.bars_in_test_window for p in r.pair_runs)
                // max(1, len(r.pair_runs)),
                expectancy_r=r.expectancy_r,
                return_pct=r.aggregate_return_pct,
                profit_factor=pf,
                max_drawdown_pct=statistics.median(
                    [p.max_drawdown_pct for p in r.pair_runs]
                ) if r.pair_runs else 0.0,
                win_rate=(
                    statistics.mean([p.win_rate for p in r.pair_runs])
                    if r.pair_runs else 0.0
                ),
                long_trades=sum(p.long_trades for p in r.pair_runs),
                short_trades=sum(p.short_trades for p in r.pair_runs),
                pass_pre_commit_gates=r.passes(),
            )
        )

    agg = _aggregate(rollups)
    aggregate_model = AggregateMetrics(
        fold_count=agg["fold_count"],
        folds_passing_gates=agg["folds_passing"],
        fold_pass_rate=agg["fold_pass_rate"],
        total_trades_across_folds=agg["total_trades"],
        aggregate_expectancy_r=agg["aggregate_expectancy_r"],
        aggregate_return_pct=agg["aggregate_return_pct"],
        single_fold_max_return_share=(
            agg["single_fold_dominance_pct"] / 100.0
            if agg["fold_count"] > 0 else None
        ),
    )
    overall = "BLOCKED" if blocked_verdict else agg["overall_verdict"]
    results = WalkForwardResults(
        plan=plan,
        fold_metrics=fold_metrics,
        aggregate=aggregate_model,
        overall_verdict=overall,
    )

    wf_dir = out_dir / "walk_forward"
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / "results.json").write_text(
        json.dumps(results.model_dump(mode="json"), indent=2, default=str),
        encoding="utf-8",
    )
    (wf_dir / "results.md").write_text(render_results_md(results), encoding="utf-8")

    detail_path = wf_dir / "fold_detail.json"
    detail_path.write_text(
        json.dumps(
            {
                "campaign_id": "CAMPAIGN_013",
                "strategy_name": EXPECTED_STRATEGY,
                "strategy_version": EXPECTED_VERSION,
                "null_model": False,
                "approval_path": (
                    "RESEARCH_PASS_UNAPPROVED at best — see "
                    "STRATEGY_APPROVAL_PROCESS.md"
                ),
                "git_commit": (_git("rev-parse", "HEAD") or "unknown"),
                "git_dirty": bool(_git("status", "--porcelain")),
                "config_path": str(config_path),
                "config_hash": settings.config_hash,
                "data_source": REQUIRED_DATA_SOURCE,
                "risk_engine_mode": "backtest",
                "fold_gate_thresholds": TEST_FOLD_GATES,
                "aggregate_gate_thresholds": AGGREGATE_GATES,
                "cross_pair_runner_contract": {
                    "blocked_folds": blocked_folds,
                    "blocked_verdict": blocked_verdict,
                },
                "folds": [
                    {
                        "fold_index": r.fold_index,
                        "test_start": str(plan.folds[r.fold_index].test_start),
                        "test_end": str(plan.folds[r.fold_index].test_end),
                        "trade_count": r.trade_count,
                        "aggregate_return_pct": r.aggregate_return_pct,
                        "expectancy_r": r.expectancy_r,
                        "profit_factor": r.profit_factor(),
                        "pairs_positive": r.pairs_positive,
                        "single_pair_dominance_pct": r.single_pair_dominance_pct,
                        "gates": r.gate_vector(),
                        "passes": r.passes(),
                        "pair_runs": [pr.to_dict() for pr in r.pair_runs],
                        "cross_pair_diagnostics": r.cross_pair_diagnostics,
                    }
                    for r in rollups
                ],
                "aggregate": agg,
                "generated_at": datetime.now(UTC).isoformat(),
            },
            indent=2, default=str,
        ),
        encoding="utf-8",
    )
    print(f"wrote {wf_dir / 'results.json'}")
    print(f"wrote {wf_dir / 'results.md'}")
    print(f"wrote {detail_path}")
    print(f"\nINHERITED-GATE VERDICT: {overall}")
    if blocked_verdict:
        print(
            "\n!! BLOCKED — cross-pair runner contract failed on one or more folds. "
            "Phase 5 must classify the campaign as BLOCKED. "
            "DO NOT modify strategy rules to work around. "
            "DO NOT relax max_open_positions or risk settings."
        )
    elif overall == "PASS":
        print(
            "\n!! INHERITED GATES PASS — the Phase 5 verdict doc must "
            "additionally apply the CAMPAIGN_011 null-baseline comparison "
            "per CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md §3. Even a "
            "full PASS produces RESEARCH_PASS_UNAPPROVED — verifier "
            "extension + human approval action remain required. "
            "DO NOT add cross_pair_currency_strength_rotation to "
            "configs/approved_strategies.yaml."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
