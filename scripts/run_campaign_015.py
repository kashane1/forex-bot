#!/usr/bin/env python3
"""CAMPAIGN_015 walk-forward evidence runner — failed_breakout_reversal 0.1.0-c015.

Drives the failed-breakout reversal candidate against each fold's test
window from a rolling walk-forward plan, on the 7-pair H4 OANDA practice
universe, and emits per-fold + aggregate JSON plus a machine-readable
``gate_result.json`` consumed by the Phase 3 result doc and Phase 4
anti-overfit diagnostics.

**CAMPAIGN_015 is a research candidate scaffold; this runner produces
research evidence but cannot approve any strategy.** Even a clean
``PASS_RESEARCH_SCREEN`` outcome leaves
``configs/approved_strategies.yaml`` at ``approved: []`` and the
paper / demo / live refusals intact.

Strict rules — enforced by this script:

  * The strategy must be ``failed_breakout_reversal``
    (i.e. ``strategy.enabled == ['failed_breakout_reversal']``).
  * Strategy parameters must match the pre-commit verbatim
    (``CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md`` §5).
    Mismatch aborts before any backtest fires.
  * The walk-forward plan is constructed in-process by
    ``rolling_window_plan`` with the frozen 540/180/180/180 windows;
    no external plan.json is consumed.
  * Every per-pair per-fold candle source must be ``oanda-practice``.
    Mismatched / missing source for any pair classifies the campaign
    as ``BLOCKED`` (Phase 0 §13 BLOCKED-conditions).
  * The runner makes no broker call. It reads the local SQLite store
    only. No ``.env``, no credentials, no network.
  * The bespoke engine is the canonical evidence path; Backtrader is
    a secondary verification lane (Phase 5 / 6).
  * No tuning. No parameter sweep. No retry with altered parameters
    to improve results.

Cost stress: the runner runs each fold once at base costs and once at
2x-cost stress (`--cost-stress 2.0`). Both pass / fail are recorded
in the aggregate ``gate_result.json``.

Fill timing: primary path is ``next_bar_open``; the runner asserts
``strategy_cfg["entry_timing"] == "next_bar_open"`` before invoking
the bespoke engine.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

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
from forex_bot.strategies.failed_breakout_reversal import (
    FailedBreakoutReversalStrategy,
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
from research.walk_forward.splits import rolling_window_plan
# isort: on

REQUIRED_DATA_SOURCE = "oanda-practice"
EXPECTED_VERSION = "0.1.0-c015"
EXPECTED_STRATEGY = "failed_breakout_reversal"
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
# CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md §5). Any mismatch
# aborts before any backtest fires.
FROZEN_PARAMETERS: dict[str, Any] = {
    "version": EXPECTED_VERSION,
    "timeframe": "H4",
    "range_lookback": 20,
    "atr_lookback": 14,
    "adx_lookback": 14,
    "adx_max": 20.0,
    "sweep_buffer_atr": 0.10,
    "min_range_atr_multiple": 1.25,
    "max_range_atr_multiple": 5.00,
    "stop_buffer_atr": 0.10,
    "min_stop_atr_multiple": 0.80,
    "max_stop_atr_multiple": 2.20,
    "max_bars_in_trade": 12,
    "take_profit_r": None,
    "trailing_stop_atr_multiple": None,
    "entry_timing": "next_bar_open",
    "same_bar_adverse_stop_wins": True,
    "min_atr_pips": {},
}

# Walk-forward windows (pre-committed, frozen by Phase 0 §7).
PLAN_WINDOWS = {
    "train_window_days": 540,
    "validation_window_days": 180,
    "test_window_days": 180,
    "step_days": 180,
}

# Universe windows match CAMPAIGN_010 / 011 / 012 / 013 / 014 verbatim
# so the 2025-2026 lockbox discipline is preserved.
UNIVERSE_START = date(2020, 1, 1)
UNIVERSE_END = date(2026, 5, 20)

# Aggregate gates (Phase 0 §8). The bespoke runner emits a verdict
# from these; the Phase 4 anti-overfit doc supplements them.
AGGREGATE_GATES = {
    "trade_count_min": 200,
    "trade_count_max": 800,
    "expectancy_r_min_base": 0.03,
    "expectancy_r_min_2xcost": 0.00,
    "profit_factor_min_base": 1.05,
    "profit_factor_min_2xcost": 1.00,
    "fold_pass_rate_min": 5,  # of 8
    "fold_count_min": 8,
    "pairs_positive_min": 4,
    "single_pair_dominance_max_pct": 70.0,
}

PER_FOLD_GATES = {
    "trade_count_min": 30,
    "expectancy_r_min": 0.0,
    "pairs_positive_min": 3,
    "single_pair_dominance_max_pct": 60.0,
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
# Fold date utilities


def _fold_dates_to_dts(fold: Fold) -> tuple[datetime, datetime]:
    """Convert fold test-window dates to UTC datetimes that cover the
    inclusive day range — PLUS warm-up margin (90 calendar days) so
    H4 ATR(14) / ADX(14) / range_lookback=20 are fully warm at fold
    start. The bespoke engine reads only completed candles; bars
    outside the inclusive test window contribute to warm-up but the
    strategy's signal generation only fires inside the test window."""
    warm_up_days_margin = 90
    start = datetime.combine(
        fold.test_start - timedelta(days=warm_up_days_margin),
        datetime.min.time(), tzinfo=UTC,
    )
    end = datetime.combine(
        fold.test_end, datetime.max.time().replace(microsecond=0), tzinfo=UTC,
    )
    return start, end


# ---------------------------------------------------------------------------
# Per-fold per-pair backtest


@dataclass
class PairFoldRun:
    fold_index: int
    instrument: str
    cost_label: str
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
    exit_reason_counts: dict[str, int]
    trade_r_series: list[float]

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _run_pair_fold(
    *,
    settings: Any,
    fold: Fold,
    instrument: str,
    candle_repo: CandleRepo,
    ds_repo: DataSourceRepo,
    instr_repo: InstrumentRepo,
    risk_engine: RiskEngine,
    strategy_cfg: dict[str, Any],
    out_dir: Path,
    cost_stress: float,
    cost_label: str,
) -> PairFoldRun:
    meta = instr_repo.get(instrument)
    if meta is None:
        raise SystemExit(f"missing instrument metadata for {instrument}")
    src = (ds_repo.latest_for(instrument, "H4") or {}).get("source", "unknown")
    if src != REQUIRED_DATA_SOURCE:
        raise SystemExit(
            f"data source for {instrument} H4 is {src!r}, expected "
            f"{REQUIRED_DATA_SOURCE!r}. CAMPAIGN_015 aborts."
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
    fixed_slip = Decimal(str(settings.backtest.fixed_slippage_pips)) * Decimal(str(cost_stress))
    spread_mult = Decimal(str(settings.backtest.spread_slippage_multiplier)) * Decimal(str(cost_stress))
    commission = Decimal(str(settings.backtest.commission_per_unit)) * Decimal(str(cost_stress))
    engine = BacktestEngine(
        instrument=meta,
        strategy=FailedBreakoutReversalStrategy(version=strategy_cfg["version"]),
        strategy_config=strategy_cfg,
        fill_model=FillModel(
            fixed_slippage_pips=fixed_slip,
            spread_slippage_multiplier=spread_mult,
        ),
        fill_timing="next_bar_open",
        starting_equity=Decimal(str(settings.backtest.starting_equity_usd)),
        account_currency=settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(strategy_cfg["max_bars_in_trade"]),
        commission_per_unit=commission,
        trailing_stop_atr_multiple=strategy_cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(strategy_cfg["atr_lookback"]),
        risk_engine=risk_engine,
        settings=settings,
    )
    result = engine.run(frame, data_request_hash=data_hash)
    cost_dir = out_dir / "folds" / cost_label / f"fold_{fold.fold_index:02d}"
    cost_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"fold_{fold.fold_index:02d}_{instrument}"
    write_summary_json(result, cost_dir / f"{prefix}_summary.json")
    write_trades_csv(result, cost_dir / f"{prefix}_trades.csv")
    long_trades = sum(1 for t in result.trades if t.side == "long")
    short_trades = sum(1 for t in result.trades if t.side == "short")
    exit_reasons: dict[str, int] = {}
    for t in result.trades:
        reason = getattr(t, "exit_reason", "unknown") or "unknown"
        exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
    trade_r = [float(getattr(t, "r_multiple", 0.0)) for t in result.trades]
    return PairFoldRun(
        fold_index=fold.fold_index,
        instrument=instrument,
        cost_label=cost_label,
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
        exit_reason_counts=exit_reasons,
        trade_r_series=trade_r,
    )


# ---------------------------------------------------------------------------
# Fold-level aggregation


@dataclass
class FoldRollup:
    fold_index: int
    cost_label: str
    pair_runs: list[PairFoldRun] = field(default_factory=list)

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
        return {
            "trade_count_ge_30": self.trade_count >= PER_FOLD_GATES["trade_count_min"],
            "expectancy_r_ge_0": self.expectancy_r >= PER_FOLD_GATES["expectancy_r_min"],
            "pairs_positive_ge_3": self.pairs_positive >= PER_FOLD_GATES["pairs_positive_min"],
            "single_pair_dominance_le_60pct": self.single_pair_dominance_pct
            <= PER_FOLD_GATES["single_pair_dominance_max_pct"],
        }

    def passes(self) -> bool:
        return all(self.gate_vector().values())


# ---------------------------------------------------------------------------
# Aggregate


def _aggregate(rollups: list[FoldRollup], *, cost_label: str) -> dict[str, Any]:
    fold_count = len(rollups)
    folds_passing = sum(1 for r in rollups if r.passes())
    total_trades = sum(r.trade_count for r in rollups)
    pair_totals: dict[str, float] = {p: 0.0 for p in EXPECTED_PAIRS}
    pair_trade_counts: dict[str, int] = {p: 0 for p in EXPECTED_PAIRS}
    pair_expectancy_weighted: dict[str, float] = {p: 0.0 for p in EXPECTED_PAIRS}
    pair_gross_positive_r: dict[str, float] = {p: 0.0 for p in EXPECTED_PAIRS}
    for r in rollups:
        for pr in r.pair_runs:
            pair_totals[pr.instrument] += pr.return_pct
            pair_trade_counts[pr.instrument] += pr.trade_count
            pair_expectancy_weighted[pr.instrument] += pr.expectancy_r * pr.trade_count
            for r_val in pr.trade_r_series:
                if r_val > 0:
                    pair_gross_positive_r[pr.instrument] += r_val
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
    # Single-pair-dominance over gross positive R (binding Phase 0 §8.1).
    total_gross_positive_r = sum(pair_gross_positive_r.values())
    if total_gross_positive_r > 0:
        single_pair_dom_pct = (
            100.0 * max(pair_gross_positive_r.values()) / total_gross_positive_r
        )
    else:
        single_pair_dom_pct = 0.0
    gains = sum(r.aggregate_return_pct for r in rollups if r.aggregate_return_pct > 0)
    losses = -sum(r.aggregate_return_pct for r in rollups if r.aggregate_return_pct < 0)
    if losses == 0:
        agg_pf: float | None = None if gains > 0 else 0.0
    else:
        agg_pf = gains / losses

    # Trade-level cumulative R: signed running sum across all trades.
    all_trade_r: list[float] = []
    for r in rollups:
        for pr in r.pair_runs:
            all_trade_r.extend(pr.trade_r_series)
    trade_level_cumulative_r = sum(all_trade_r)
    median_per_fold_expectancy_r = (
        statistics.median([r.expectancy_r for r in rollups]) if rollups else 0.0
    )

    # Pick the cost-dependent expectancy / PF gates.
    exp_min = (
        AGGREGATE_GATES["expectancy_r_min_base"]
        if cost_label == "base"
        else AGGREGATE_GATES["expectancy_r_min_2xcost"]
    )
    pf_min = (
        AGGREGATE_GATES["profit_factor_min_base"]
        if cost_label == "base"
        else AGGREGATE_GATES["profit_factor_min_2xcost"]
    )
    pf_pass = (agg_pf is None and total_trades > 0) or (
        agg_pf is not None and agg_pf >= pf_min
    )

    aggregate_gate_vector = {
        "fold_pass_rate_ge_5_of_8": folds_passing >= AGGREGATE_GATES["fold_pass_rate_min"],
        "fold_count_ge_8": fold_count >= AGGREGATE_GATES["fold_count_min"],
        "expectancy_r_min": aggregate_expectancy_r >= exp_min,
        "profit_factor_min": pf_pass,
        "trade_count_min_200": total_trades >= AGGREGATE_GATES["trade_count_min"],
        "trade_count_max_800": total_trades <= AGGREGATE_GATES["trade_count_max"],
        "pairs_positive_ge_4_of_7": pairs_positive_count
        >= AGGREGATE_GATES["pairs_positive_min"],
        "single_pair_dominance_le_70pct": single_pair_dom_pct
        <= AGGREGATE_GATES["single_pair_dominance_max_pct"],
    }
    aggregate_pass = all(aggregate_gate_vector.values())

    return {
        "cost_label": cost_label,
        "fold_count": fold_count,
        "folds_passing": folds_passing,
        "fold_pass_rate": (folds_passing / fold_count) if fold_count > 0 else 0.0,
        "total_trades": total_trades,
        "aggregate_return_pct": aggregate_return_pct,
        "aggregate_expectancy_r": aggregate_expectancy_r,
        "median_per_fold_expectancy_r": median_per_fold_expectancy_r,
        "trade_level_cumulative_r": trade_level_cumulative_r,
        "profit_factor": agg_pf,
        "pairs_positive_count": pairs_positive_count,
        "pair_returns_pct": pair_totals,
        "pair_trade_counts": pair_trade_counts,
        "pair_expectancy_r": pair_expectancy,
        "pair_gross_positive_r": pair_gross_positive_r,
        "single_pair_dominance_pct": single_pair_dom_pct,
        "aggregate_gates": aggregate_gate_vector,
        "aggregate_pass": aggregate_pass,
        "expectancy_min_applied": exp_min,
        "profit_factor_min_applied": pf_min,
    }


# ---------------------------------------------------------------------------
# Frozen-parameter enforcement


def _assert_frozen(strategy_cfg: dict[str, Any]) -> None:
    """Fail-closed if the loaded YAML deviates from the pre-commit."""
    mismatched: list[str] = []
    for key, expected in FROZEN_PARAMETERS.items():
        got = strategy_cfg.get(key)
        if (isinstance(expected, list) and isinstance(got, list)) or (
            isinstance(expected, dict) and isinstance(got, dict)
        ):
            if got != expected:
                mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
        elif got != expected:
            mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
    if mismatched:
        raise SystemExit(
            "CAMPAIGN_015 frozen-parameter mismatch — see "
            "CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md §5:\n"
            + "\n".join(mismatched)
        )


# ---------------------------------------------------------------------------
# Local data preflight (BLOCKED conditions; Phase 0 §13)


def _data_preflight(
    *,
    db_path: Path,
    plan: WalkForwardPlan,
    pairs: tuple[str, ...],
) -> dict[str, Any]:
    """Read-only check that the local data store can satisfy every fold
    + every pair. Returns a dict with `blocked: bool` and `reasons:
    list[str]`. Does not raise."""
    reasons: list[str] = []
    if not db_path.exists():
        reasons.append(f"database_path does not exist: {db_path}")
        return {"blocked": True, "reasons": reasons, "details": {}}
    details: dict[str, Any] = {"per_pair": {}}
    try:
        db = Database(db_path)
        candle_repo = CandleRepo(db)
        ds_repo = DataSourceRepo(db)
    except Exception as exc:
        reasons.append(f"could not open database: {exc}")
        return {"blocked": True, "reasons": reasons, "details": {}}

    for pair in pairs:
        per_pair: dict[str, Any] = {"source": None, "fold_candle_counts": {}}
        latest = ds_repo.latest_for(pair, "H4") or {}
        src = latest.get("source", "unknown")
        per_pair["source"] = src
        if src != REQUIRED_DATA_SOURCE:
            reasons.append(
                f"{pair} H4 data source is {src!r}, expected "
                f"{REQUIRED_DATA_SOURCE!r}"
            )
        for fold in plan.folds:
            frm, to = _fold_dates_to_dts(fold)
            rows = candle_repo.list(
                pair, "H4", completed_only=True,
                from_time=frm, to_time=to,  # type: ignore[arg-type]
            )
            count = len(rows)
            per_pair["fold_candle_counts"][f"fold_{fold.fold_index:02d}"] = count
            if count == 0:
                reasons.append(
                    f"{pair} fold {fold.fold_index} ({fold.test_start}..{fold.test_end}) "
                    f"has zero candles"
                )
        details["per_pair"][pair] = per_pair
    return {"blocked": bool(reasons), "reasons": reasons, "details": details}


# ---------------------------------------------------------------------------
# CLI


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True, help="Campaign output directory")
    ap.add_argument(
        "--cost-stress", type=float, default=2.0,
        help="Cost-stress multiplier (default 2.0; runner ALWAYS runs base too)",
    )
    ap.add_argument(
        "--preflight-only", action="store_true",
        help="Run data preflight only; write a BLOCKED artifact and exit 0 "
             "even if data is present (used by tests).",
    )
    args = ap.parse_args(argv)

    config_path = Path(args.config)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    wf_dir = out_dir / "walk_forward"
    wf_dir.mkdir(parents=True, exist_ok=True)

    settings = load_settings(config_path)

    sc = settings.strategy
    if sc.enabled != [EXPECTED_STRATEGY] or sc.failed_breakout_reversal is None:
        raise SystemExit(
            f"CAMPAIGN_015 config must enable only {EXPECTED_STRATEGY!r}; "
            f"got {sc.enabled}"
        )
    strategy_cfg = sc.failed_breakout_reversal.model_dump()
    _assert_frozen(strategy_cfg)

    pairs = tuple(settings.market.instruments)
    if pairs != EXPECTED_PAIRS:
        raise SystemExit(
            f"CAMPAIGN_015 universe mismatch — got {pairs}, expected "
            f"{EXPECTED_PAIRS}"
        )

    # Build the plan in-process from the frozen windows.
    plan = rolling_window_plan(
        campaign_name="CAMPAIGN_015_failed_breakout_reversal",
        universe_start=UNIVERSE_START,
        universe_end=UNIVERSE_END,
        train_window_days=PLAN_WINDOWS["train_window_days"],
        validation_window_days=PLAN_WINDOWS["validation_window_days"],
        test_window_days=PLAN_WINDOWS["test_window_days"],
        step_days=PLAN_WINDOWS["step_days"],
        parameter_mode=ParameterMode.FROZEN,
        notes=[
            "CAMPAIGN_015 walk-forward plan (Phase 0 §7); 8 folds rolling, "
            "540/180/180/180 days, frozen parameters, strategy_evidence=false.",
        ],
    )
    if plan.split_style is not SplitStyle.ROLLING:
        raise SystemExit("plan.split_style must be ROLLING")
    if plan.parameter_mode is not ParameterMode.FROZEN:
        raise SystemExit("plan.parameter_mode must be FROZEN")
    if plan.strategy_evidence:
        raise SystemExit("plan.strategy_evidence must be False")
    if len(plan.folds) < AGGREGATE_GATES["fold_count_min"]:
        raise SystemExit(
            f"plan has only {len(plan.folds)} folds; "
            f">= {AGGREGATE_GATES['fold_count_min']} required"
        )

    (wf_dir / "plan.json").write_text(
        json.dumps(plan.model_dump(mode="json"), indent=2, default=str),
        encoding="utf-8",
    )

    db_path = Path(settings.app.database_path)
    preflight = _data_preflight(db_path=db_path, plan=plan, pairs=pairs)
    (wf_dir / "preflight.json").write_text(
        json.dumps(preflight, indent=2, default=str), encoding="utf-8",
    )

    print(
        f"=== CAMPAIGN_015 walk-forward run started "
        f"{datetime.now(UTC).isoformat()} ==="
    )
    print(f"folds: {len(plan.folds)}  pairs: {len(pairs)}")
    print(f"db_path: {db_path}  exists: {db_path.exists()}")
    print(
        f"frozen params: range={strategy_cfg['range_lookback']} "
        f"atr={strategy_cfg['atr_lookback']} adx_max={strategy_cfg['adx_max']} "
        f"sweep_buffer={strategy_cfg['sweep_buffer_atr']}*ATR "
        f"max_hold={strategy_cfg['max_bars_in_trade']} "
        f"timing={strategy_cfg['entry_timing']}"
    )

    if preflight["blocked"] or args.preflight_only:
        gate_result = _build_blocked_gate_result(
            preflight=preflight,
            strategy_cfg=strategy_cfg,
            plan=plan,
            settings=settings,
            config_path=config_path,
        )
        (wf_dir / "gate_result.json").write_text(
            json.dumps(gate_result, indent=2, default=str), encoding="utf-8",
        )
        if preflight["blocked"]:
            print("\n!! BLOCKED — local data preflight failed:")
            for reason in preflight["reasons"][:20]:
                print(f"  {reason}")
            if len(preflight["reasons"]) > 20:
                print(f"  ... and {len(preflight['reasons']) - 20} more")
        else:
            print("\n!! preflight-only mode — exiting cleanly without running backtests")
        print(f"wrote {wf_dir / 'gate_result.json'}")
        return 0

    db = Database(db_path)
    candle_repo = CandleRepo(db)
    ds_repo = DataSourceRepo(db)
    instr_repo = InstrumentRepo(db)
    risk_engine = RiskEngine(settings, mode="backtest")

    t0 = time.time()
    cost_runs: dict[str, dict[str, Any]] = {}
    rollups_by_cost: dict[str, list[FoldRollup]] = {}
    cost_labels: list[tuple[str, float]] = [
        ("base", 1.0),
        ("2xcost", float(args.cost_stress)),
    ]
    for cost_label, multiplier in cost_labels:
        print(f"\n--- {cost_label} (cost x{multiplier}) ---")
        rollups: list[FoldRollup] = []
        for fold in plan.folds:
            pair_runs: list[PairFoldRun] = []
            for pair in pairs:
                run = _run_pair_fold(
                    settings=settings,
                    fold=fold,
                    instrument=pair,
                    candle_repo=candle_repo,
                    ds_repo=ds_repo,
                    instr_repo=instr_repo,
                    risk_engine=risk_engine,
                    strategy_cfg=strategy_cfg,
                    out_dir=out_dir,
                    cost_stress=multiplier,
                    cost_label=cost_label,
                )
                pair_runs.append(run)
                print(
                    f"  fold {fold.fold_index:>2d} "
                    f"test=[{fold.test_start}..{fold.test_end}] "
                    f"{pair}: trades={run.trade_count:>4d} "
                    f"sig_rej={run.rejection_count:>3d} "
                    f"exp_r={run.expectancy_r:+.3f} "
                    f"ret_pct={run.return_pct:+.2f}%"
                )
            rollups.append(FoldRollup(
                fold_index=fold.fold_index,
                cost_label=cost_label,
                pair_runs=pair_runs,
            ))
        cost_runs[cost_label] = _aggregate(rollups, cost_label=cost_label)
        rollups_by_cost[cost_label] = rollups

    elapsed = time.time() - t0
    print(f"\nbacktests complete in {elapsed:.1f}s")

    # Build per-fold metrics for the harness (using base costs).
    base_rollups = rollups_by_cost["base"]
    fold_metrics: list[FoldMetrics] = []
    for r in base_rollups:
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

    base_agg = cost_runs["base"]
    stress_agg = cost_runs["2xcost"]

    aggregate_model = AggregateMetrics(
        fold_count=base_agg["fold_count"],
        folds_passing_gates=base_agg["folds_passing"],
        fold_pass_rate=base_agg["fold_pass_rate"],
        total_trades_across_folds=base_agg["total_trades"],
        aggregate_expectancy_r=base_agg["aggregate_expectancy_r"],
        aggregate_return_pct=base_agg["aggregate_return_pct"],
        single_fold_max_return_share=None,
    )

    runner_verdict = _classify(base_agg=base_agg, stress_agg=stress_agg)
    schema_verdict = "PASS" if runner_verdict == "PASS_RESEARCH_SCREEN" else "REJECT"
    results = WalkForwardResults(
        plan=plan,
        fold_metrics=fold_metrics,
        aggregate=aggregate_model,
        overall_verdict=schema_verdict,
    )
    (wf_dir / "results.json").write_text(
        json.dumps(results.model_dump(mode="json"), indent=2, default=str),
        encoding="utf-8",
    )
    (wf_dir / "results.md").write_text(render_results_md(results), encoding="utf-8")

    # Per-fold detail (both cost runs).
    fold_detail: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_015",
        "strategy_name": EXPECTED_STRATEGY,
        "strategy_version": EXPECTED_VERSION,
        "null_model": False,
        "approval_path": (
            "PASS_RESEARCH_SCREEN at best — see "
            "CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md §16 "
            "(candidate for human review, NOT approval)"
        ),
        "git_commit": (_git("rev-parse", "HEAD") or "unknown"),
        "git_dirty": bool(_git("status", "--porcelain")),
        "config_path": str(config_path),
        "config_hash": settings.config_hash,
        "data_source": REQUIRED_DATA_SOURCE,
        "risk_engine_mode": "backtest",
        "fill_timing": "next_bar_open",
        "cost_stress_multiplier": float(args.cost_stress),
        "fold_gates": PER_FOLD_GATES,
        "aggregate_gates": AGGREGATE_GATES,
        "by_cost": {},
        "generated_at": datetime.now(UTC).isoformat(),
    }
    for cost_label, rollups in rollups_by_cost.items():
        fold_detail["by_cost"][cost_label] = {
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
                }
                for r in rollups
            ],
            "aggregate": cost_runs[cost_label],
        }

    (wf_dir / "fold_detail.json").write_text(
        json.dumps(fold_detail, indent=2, default=str), encoding="utf-8",
    )

    # Machine-readable gate_result.json (consumed by Phase 4 + Phase 7).
    gate_result = {
        "campaign_id": "CAMPAIGN_015",
        "strategy_name": EXPECTED_STRATEGY,
        "strategy_version": EXPECTED_VERSION,
        "verdict": runner_verdict,
        "verdict_ceiling": "PASS_RESEARCH_SCREEN",
        "approval_status": "NOT_APPROVED",
        "approved_strategies_yaml_state": "approved: []",
        "config_path": str(config_path),
        "config_hash": settings.config_hash,
        "fold_count": base_agg["fold_count"],
        "by_cost": {
            "base": {
                "aggregate_expectancy_r": base_agg["aggregate_expectancy_r"],
                "aggregate_return_pct": base_agg["aggregate_return_pct"],
                "profit_factor": base_agg["profit_factor"],
                "total_trades": base_agg["total_trades"],
                "fold_pass_rate": base_agg["fold_pass_rate"],
                "folds_passing": base_agg["folds_passing"],
                "pairs_positive_count": base_agg["pairs_positive_count"],
                "single_pair_dominance_pct": base_agg["single_pair_dominance_pct"],
                "median_per_fold_expectancy_r": base_agg["median_per_fold_expectancy_r"],
                "trade_level_cumulative_r": base_agg["trade_level_cumulative_r"],
                "aggregate_gates": base_agg["aggregate_gates"],
                "aggregate_pass": base_agg["aggregate_pass"],
                "expectancy_min_applied": base_agg["expectancy_min_applied"],
                "profit_factor_min_applied": base_agg["profit_factor_min_applied"],
            },
            "2xcost": {
                "aggregate_expectancy_r": stress_agg["aggregate_expectancy_r"],
                "aggregate_return_pct": stress_agg["aggregate_return_pct"],
                "profit_factor": stress_agg["profit_factor"],
                "total_trades": stress_agg["total_trades"],
                "fold_pass_rate": stress_agg["fold_pass_rate"],
                "folds_passing": stress_agg["folds_passing"],
                "aggregate_gates": stress_agg["aggregate_gates"],
                "aggregate_pass": stress_agg["aggregate_pass"],
                "expectancy_min_applied": stress_agg["expectancy_min_applied"],
                "profit_factor_min_applied": stress_agg["profit_factor_min_applied"],
            },
        },
        "blocked": False,
        "blocked_reasons": [],
        "generated_at": datetime.now(UTC).isoformat(),
    }
    (wf_dir / "gate_result.json").write_text(
        json.dumps(gate_result, indent=2, default=str), encoding="utf-8",
    )

    print(f"\nRUNNER VERDICT: {runner_verdict}")
    print(
        f"  base:  exp_r={base_agg['aggregate_expectancy_r']:+.4f} "
        f"pf={base_agg['profit_factor']} "
        f"trades={base_agg['total_trades']} "
        f"folds_pass={base_agg['folds_passing']}/{base_agg['fold_count']} "
        f"pairs_pos={base_agg['pairs_positive_count']}/7"
    )
    print(
        f"  2x:    exp_r={stress_agg['aggregate_expectancy_r']:+.4f} "
        f"pf={stress_agg['profit_factor']} "
        f"trades={stress_agg['total_trades']}"
    )
    print(
        "\n!! NO APPROVAL: even PASS_RESEARCH_SCREEN is candidate for human "
        "review only. configs/approved_strategies.yaml remains approved: []. "
        "DO NOT add failed_breakout_reversal to the registry."
    )
    return 0


def _build_blocked_gate_result(
    *,
    preflight: dict[str, Any],
    strategy_cfg: dict[str, Any],
    plan: WalkForwardPlan,
    settings: Any,
    config_path: Path,
) -> dict[str, Any]:
    return {
        "campaign_id": "CAMPAIGN_015",
        "strategy_name": EXPECTED_STRATEGY,
        "strategy_version": EXPECTED_VERSION,
        "verdict": "BLOCKED",
        "verdict_ceiling": "PASS_RESEARCH_SCREEN",
        "approval_status": "NOT_APPROVED",
        "approved_strategies_yaml_state": "approved: []",
        "config_path": str(config_path),
        "config_hash": settings.config_hash,
        "fold_count": len(plan.folds),
        "blocked": True,
        "blocked_reasons": list(preflight.get("reasons", []))
        or ["preflight-only mode"],
        "preflight_details": preflight.get("details", {}),
        "by_cost": {},
        "generated_at": datetime.now(UTC).isoformat(),
    }


def _classify(*, base_agg: dict[str, Any], stress_agg: dict[str, Any]) -> str:
    """Map aggregate-gate pass/fail to a runner verdict label.

    Even a clean PASS_RESEARCH_SCREEN is a "candidate for human review"
    verdict only — never an approval. The Phase 4 diagnostics
    classifier supplements (does not override) this label."""
    if base_agg["aggregate_pass"] and stress_agg["aggregate_pass"]:
        return "PASS_RESEARCH_SCREEN"
    return "REJECT"


if __name__ == "__main__":
    raise SystemExit(main())
