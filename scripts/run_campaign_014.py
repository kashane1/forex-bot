#!/usr/bin/env python3
"""CAMPAIGN_014 walk-forward evidence runner.

Drives ``calendar_event_window_anomaly 0.1.0-c014`` against each fold's
TEST window from a walk-forward plan, on the 7-pair H4 OANDA practice
universe, and emits per-fold metrics + aggregate + a campaign-level
``WalkForwardResults`` JSON/Markdown via the existing
``research.walk_forward`` harness.

**CAMPAIGN_014 is a research candidate scaffold; this runner produces
research evidence but cannot approve any strategy.** Even a clean PASS
produces ``RESEARCH_PASS_UNAPPROVED`` pending the verifier-extension
sprint + a deliberate human approval action per
``STRATEGY_APPROVAL_PROCESS.md``.

Strict rules — enforced by this script:

  * The strategy must be ``calendar_event_window_anomaly``
    (i.e. ``strategy.enabled == ['calendar_event_window_anomaly']``).
  * The strategy parameters must match the pre-commit verbatim
    (``CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`` §5). Mismatch aborts before
    any backtest fires.
  * The walk-forward plan must be ``parameter_mode == 'frozen'``,
    ``split_style == 'rolling'``, ``strategy_evidence: false``.
  * Every per-pair, per-fold candle source must be ``oanda-practice``
    (no synthetic fallback).
  * The event fixture must validate against
    ``campaign_014.event_fixture.v1`` schema; loader's deny-list must
    not trip; coverage must include every fold's test window.
  * The runner makes no broker call. It reads the local SQLite store
    only. No `.env`, no credentials, no network.
  * No tuning. No parameter sweep. No re-run with altered parameters
    to improve results. No relaxing of ``max_open_positions`` or risk
    settings.

**EVENT-FIXTURE RUNNER CONTRACT (binding):**

  The strategy consumes the event fixture via
  ``ctx.config["event_fixture"]`` (preferred — preloaded
  ``CalendarEventFixture``) or ``ctx.config["event_calendar_path"]``
  (lazy fallback). The runner MUST:

    1. Load the fixture once before any fold runs.
    2. Validate fixture coverage covers every fold's test window;
       classify verdict as ``BLOCKED`` (campaign-level) if not.
    3. Inject the preloaded ``CalendarEventFixture`` into
       ``strategy_config["event_fixture"]`` for each per-pair engine
       invocation (so each invocation reuses the parsed fixture
       without re-reading the JSON file).
    4. Fail closed if the fixture is missing, malformed, or has any
       forbidden field.
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

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.exporters import write_summary_json, write_trades_csv
from forex_bot.backtesting.fills import FillModel
from forex_bot.calendar_events import (
    CalendarEventFixture,
    covers_range,
    load_event_fixture,
)
from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo, InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.calendar_event_window_anomaly import (
    CalendarEventWindowAnomalyStrategy,
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
EXPECTED_VERSION = "0.1.0-c014"
EXPECTED_STRATEGY = "calendar_event_window_anomaly"
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
# CAMPAIGN_014_PRECOMMIT_CHECKLIST.md §5). Any mismatch aborts before
# any backtest fires. (Values must match the YAML at
# configs/campaign_014_calendar_event_window_anomaly.yaml.)
FROZEN_PARAMETERS: dict[str, Any] = {
    "version": EXPECTED_VERSION,
    "timeframe": "H4",
    "event_calendar_path": "research/calendar/fixtures/campaign_014_events.json",
    "event_set": ["NFP", "FOMC", "ECB", "BoJ", "BoE"],
    "impact_ordering": ["FOMC", "NFP", "ECB", "BoJ", "BoE"],
    "post_event_window_bars": 6,
    "atr_lookback": 14,
    "atr_stop_multiple": 2.0,
    "trailing_stop_atr_multiple": None,
    "max_post_event_bars": 6,
    "re_entry_block_bars": 3,
    "event_warmup_bars": 1,
    "min_atr_pips": {},
}

# Inherited gate thresholds (verbatim from CAMPAIGN_010 / 011 / 012 /
# 013). The per-fold gate vector + aggregate gate vector are the
# necessary-but-not-sufficient evidence floor; the Phase 5 verdict
# doc additionally applies the CAMPAIGN_011 null-baseline
# meaningful-improvement comparison (see
# CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md §3) + the C7-specific
# turnover-budget gate (see TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md
# §4 + CAMPAIGN_014_PRECOMMIT_CHECKLIST.md §10).
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
# C7-specific hard REJECT triggers (binding per
# CAMPAIGN_014_PRECOMMIT_CHECKLIST.md §10.1). These supplement the
# inherited gates; the Phase 5 verdict doc evaluates them
# independently.
TURNOVER_GATES = {
    "total_trades_hard_max": 800,
    "total_raw_signals_hard_max": 1500,
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
    inclusive day range — PLUS warm-up margin (180 calendar days) so
    H4 ATR(14) is fully warm at fold start.

    The bespoke engine reads only completed candles; bars outside the
    inclusive test window contribute to ATR warm-up but the strategy's
    event-window logic (R3) only triggers on events whose post-event
    window includes a bar inside the test window.
    """
    warm_up_days_margin = 180
    start = datetime.combine(
        fold.test_start - timedelta(days=warm_up_days_margin),
        datetime.min.time(), tzinfo=UTC,
    )
    end = datetime.combine(
        fold.test_end, datetime.max.time().replace(microsecond=0), tzinfo=UTC,
    )
    return start, end


def _fold_test_window_to_dts(fold: Fold) -> tuple[datetime, datetime]:
    """Fold's test window only (no warm-up margin), used for fixture
    coverage checks."""
    start = datetime.combine(
        fold.test_start, datetime.min.time(), tzinfo=UTC,
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
    fixture: CalendarEventFixture,
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
            f"{REQUIRED_DATA_SOURCE!r}. CAMPAIGN_014 aborts."
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
    # Inject preloaded event fixture into the strategy config dict for
    # this invocation (event-fixture runner contract; binding).
    strategy_cfg_with_fixture = dict(strategy_cfg)
    strategy_cfg_with_fixture["event_fixture"] = fixture
    engine = BacktestEngine(
        instrument=meta,
        strategy=CalendarEventWindowAnomalyStrategy(version=strategy_cfg["version"]),
        strategy_config=strategy_cfg_with_fixture,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(settings.backtest.fixed_slippage_pips)),
            spread_slippage_multiplier=Decimal(
                str(settings.backtest.spread_slippage_multiplier)
            ),
        ),
        starting_equity=Decimal(str(settings.backtest.starting_equity_usd)),
        account_currency=settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(strategy_cfg["max_post_event_bars"]),
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

    @property
    def trade_count(self) -> int:
        return sum(p.trade_count for p in self.pair_runs)

    @property
    def raw_signal_count(self) -> int:
        """Trades + rejected signals = raw signal emission count."""
        return sum(p.trade_count + p.rejection_count for p in self.pair_runs)

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
    total_raw_signals = sum(r.raw_signal_count for r in rollups)
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
    inherited_gate_vector = {
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
    inherited_pass = all(inherited_gate_vector.values())
    turnover_gate_vector = {
        "total_trades_le_800": total_trades <= TURNOVER_GATES["total_trades_hard_max"],
        "total_raw_signals_le_1500": total_raw_signals
        <= TURNOVER_GATES["total_raw_signals_hard_max"],
    }
    turnover_pass = all(turnover_gate_vector.values())
    # Determine pre-null-baseline verdict (null-baseline check is
    # applied in Phase 5 verdict doc, not by this runner).
    if not turnover_pass:
        verdict = "REJECT_TURNOVER_BUDGET"
    elif not inherited_pass:
        verdict = "REJECT"
    else:
        # Inherited gates pass + turnover within budget. The runner
        # cannot grant RESEARCH_PASS_UNAPPROVED — that requires the
        # Phase 5 null-baseline meaningful-improvement check.
        # Print the proto-verdict here; Phase 5 makes the final call.
        verdict = "INHERITED_GATES_PASS_PENDING_NULL_BASELINE_CHECK"
    return {
        "fold_count": fold_count,
        "folds_passing": folds_passing,
        "fold_pass_rate": (folds_passing / fold_count) if fold_count > 0 else 0.0,
        "total_trades": total_trades,
        "total_raw_signals": total_raw_signals,
        "aggregate_return_pct": aggregate_return_pct,
        "aggregate_expectancy_r": aggregate_expectancy_r,
        "profit_factor": agg_pf,
        "pairs_positive_count": pairs_positive_count,
        "pair_returns_pct": pair_totals,
        "pair_trade_counts": pair_trade_counts,
        "pair_expectancy_r": pair_expectancy,
        "single_fold_dominance_pct": single_fold_dom_pct,
        "single_pair_dominance_pct": single_pair_dom_pct,
        "inherited_gates": inherited_gate_vector,
        "turnover_gates": turnover_gate_vector,
        "inherited_pass": inherited_pass,
        "turnover_pass": turnover_pass,
        "runner_verdict": verdict,
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
            "CAMPAIGN_014 frozen-parameter mismatch — see "
            "CAMPAIGN_014_PRECOMMIT_CHECKLIST.md §5:\n"
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
    if sc.enabled != [EXPECTED_STRATEGY] or sc.calendar_event_window_anomaly is None:
        raise SystemExit(
            f"CAMPAIGN_014 config must enable only {EXPECTED_STRATEGY!r}; "
            f"got {sc.enabled}"
        )
    strategy_cfg = sc.calendar_event_window_anomaly.model_dump()
    _assert_frozen(strategy_cfg)

    pairs = tuple(settings.market.instruments)
    if pairs != EXPECTED_PAIRS:
        raise SystemExit(
            f"CAMPAIGN_014 universe mismatch — got {pairs}, expected "
            f"{EXPECTED_PAIRS}"
        )

    plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
    plan = WalkForwardPlan(**plan_payload)
    if plan.parameter_mode is not ParameterMode.FROZEN:
        raise SystemExit(
            f"CAMPAIGN_014 plan must use parameter_mode=frozen; "
            f"got {plan.parameter_mode.value!r}"
        )
    if plan.split_style is not SplitStyle.ROLLING:
        raise SystemExit(
            f"CAMPAIGN_014 plan must use split_style=rolling; "
            f"got {plan.split_style.value!r}"
        )
    if plan.strategy_evidence:
        raise SystemExit("plan.strategy_evidence must be False")
    if len(plan.folds) < AGGREGATE_GATES["fold_count_min"]:
        raise SystemExit(
            f"plan has only {len(plan.folds)} folds; "
            f"≥ {AGGREGATE_GATES['fold_count_min']} required"
        )

    # Load + validate event fixture ONCE before all folds (binding
    # event-fixture runner contract).
    fixture_path = strategy_cfg["event_calendar_path"]
    fixture = load_event_fixture(fixture_path)
    if fixture.schema_version != "campaign_014.event_fixture.v1":
        raise SystemExit(
            f"event fixture schema_version mismatch: {fixture.schema_version!r}"
        )

    # Per-fold fixture-coverage gate (binding; classify campaign as
    # BLOCKED if any fold's test window exceeds fixture coverage).
    blocked_folds: list[tuple[int, str]] = []
    for fold in plan.folds:
        test_start, test_end = _fold_test_window_to_dts(fold)
        if not covers_range(fixture, start=test_start, end=test_end):
            blocked_folds.append((
                fold.fold_index,
                f"test window {test_start.isoformat()}..{test_end.isoformat()} "
                f"exceeds fixture coverage_end_utc {fixture.coverage_end_utc.isoformat()}",
            ))

    db = Database(settings.app.database_path)
    candle_repo = CandleRepo(db)
    ds_repo = DataSourceRepo(db)
    instr_repo = InstrumentRepo(db)
    risk_engine = RiskEngine(settings, mode="backtest")

    print(
        f"=== CAMPAIGN_014 walk-forward run started "
        f"{datetime.now(UTC).isoformat()} ==="
    )
    print(f"folds: {len(plan.folds)}  pairs: {len(pairs)}")
    print(
        f"event fixture: {fixture_path}  "
        f"events: {len(fixture.events)}  "
        f"coverage: {fixture.coverage_start_utc.date()} → "
        f"{fixture.coverage_end_utc.date()}"
    )
    print(
        f"frozen params: post_event_window_bars="
        f"{strategy_cfg['post_event_window_bars']} "
        f"atr={strategy_cfg['atr_stop_multiple']}*ATR{strategy_cfg['atr_lookback']} "
        f"max_hold={strategy_cfg['max_post_event_bars']}"
    )

    if blocked_folds:
        print(
            f"\n!! BLOCKED: {len(blocked_folds)} fold(s) outside fixture coverage:"
        )
        for fi, blk in blocked_folds:
            print(f"  fold {fi}: {blk}")
        print(
            "\nAborting fold execution — per the binding fixture-coverage gate "
            "(CAMPAIGN_014_PRECOMMIT_CHECKLIST.md §10.1), any fold beyond "
            "fixture coverage produces BLOCKED verdict, not silent partial."
        )
        # Still write a minimal results.json so downstream phases have something.
        wf_dir = out_dir / "walk_forward"
        wf_dir.mkdir(parents=True, exist_ok=True)
        detail_path = wf_dir / "fold_detail.json"
        detail_path.write_text(
            json.dumps(
                {
                    "campaign_id": "CAMPAIGN_014",
                    "strategy_name": EXPECTED_STRATEGY,
                    "strategy_version": EXPECTED_VERSION,
                    "fixture_coverage_blocked_folds": blocked_folds,
                    "runner_verdict": "BLOCKED",
                    "generated_at": datetime.now(UTC).isoformat(),
                },
                indent=2, default=str,
            ),
            encoding="utf-8",
        )
        return 0

    t0 = time.time()
    rollups: list[FoldRollup] = []
    for fold in plan.folds:
        pair_runs: list[PairFoldRun] = []
        for pair in pairs:
            run = _run_pair_fold(
                settings=settings,
                fold=fold,
                instrument=pair,
                fixture=fixture,
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
                f"{pair}: trades={run.trade_count:>4d} sig_rej={run.rejection_count:>3d} "
                f"exp_r={run.expectancy_r:+.3f} ret_pct={run.return_pct:+.2f}%"
            )
        rollups.append(FoldRollup(fold_index=fold.fold_index, pair_runs=pair_runs))

    elapsed = time.time() - t0
    print(f"\nbacktests complete in {elapsed:.1f}s")

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
    # Map runner_verdict to WalkForwardResults's PASS/REJECT slot
    # (the harness's overall_verdict schema only accepts PASS/REJECT).
    # The richer verdict (REJECT_TURNOVER_BUDGET / INHERITED_GATES_PASS_PENDING_NULL_BASELINE_CHECK)
    # lives in fold_detail.json.
    schema_verdict = "PASS" if (
        agg["inherited_pass"] and agg["turnover_pass"]
    ) else "REJECT"
    results = WalkForwardResults(
        plan=plan,
        fold_metrics=fold_metrics,
        aggregate=aggregate_model,
        overall_verdict=schema_verdict,
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
                "campaign_id": "CAMPAIGN_014",
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
                "turnover_gate_thresholds": TURNOVER_GATES,
                "event_fixture": {
                    "path": fixture_path,
                    "schema_version": fixture.schema_version,
                    "coverage_start_utc": fixture.coverage_start_utc.isoformat(),
                    "coverage_end_utc": fixture.coverage_end_utc.isoformat(),
                    "event_count": len(fixture.events),
                },
                "fixture_coverage_blocked_folds": blocked_folds,
                "folds": [
                    {
                        "fold_index": r.fold_index,
                        "test_start": str(plan.folds[r.fold_index].test_start),
                        "test_end": str(plan.folds[r.fold_index].test_end),
                        "trade_count": r.trade_count,
                        "raw_signal_count": r.raw_signal_count,
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
    print(f"\nRUNNER VERDICT (pre-null-baseline): {agg['runner_verdict']}")
    print(f"  inherited gates pass: {agg['inherited_pass']}")
    print(f"  turnover gates pass:  {agg['turnover_pass']}  "
          f"(trades={agg['total_trades']}, raw_signals={agg['total_raw_signals']})")
    if agg["runner_verdict"] == "INHERITED_GATES_PASS_PENDING_NULL_BASELINE_CHECK":
        print(
            "\n!! INHERITED GATES PASS — the Phase 5 verdict doc must "
            "additionally apply the CAMPAIGN_011 null-baseline comparison "
            "per CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md §3. Even a "
            "full PASS produces RESEARCH_PASS_UNAPPROVED — verifier "
            "extension + human approval action remain required. "
            "DO NOT add calendar_event_window_anomaly to "
            "configs/approved_strategies.yaml."
        )
    elif agg["runner_verdict"] == "REJECT_TURNOVER_BUDGET":
        print(
            "\n!! REJECT_TURNOVER_BUDGET — turnover budget exceeded. "
            "Per TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md, no rescue "
            "by parameter tuning, max_open_positions relaxation, pair "
            "carve-out, or filter relaxation is permitted. The Phase 5 "
            "verdict doc finalizes REJECT_TURNOVER_BUDGET."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
