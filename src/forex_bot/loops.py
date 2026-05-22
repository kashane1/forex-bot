"""Paper / practice loop implementations.

Both loops fetch the latest completed candles, run the configured
strategies, hand each signal to the risk engine, and persist everything.
The practice loop additionally submits approved plans to OANDA practice.
The paper loop is *physically incapable* of submitting orders — it does
not even construct an Executor.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal

from forex_bot.approval import assert_loop_strategies_approved
from forex_bot.broker.base import Broker
from forex_bot.broker.mapping import map_spread_snapshot
from forex_bot.clock import utcnow
from forex_bot.config import Settings
from forex_bot.data.repositories import (
    AccountSnapshotRepo,
    BrokerOrderRepo,
    CandleRepo,
    InstrumentRepo,
    OrderPlanRepo,
    RiskDecisionRepo,
    SignalRepo,
    SpreadSnapshotRepo,
    SystemEventRepo,
    TransactionRepo,
)
from forex_bot.domain.candles import CandleFrame, CandleRequest
from forex_bot.domain.market import MarketState
from forex_bot.domain.orders import OrderPlan
from forex_bot.domain.risk import RiskDecision
from forex_bot.domain.signals import Signal
from forex_bot.execution.executor import ExecutionResult, Executor
from forex_bot.execution.planner import Planner
from forex_bot.execution.reconciliation import Reconciler
from forex_bot.logging_config import get_logger
from forex_bot.risk.policy import RiskEngine, RiskInputs
from forex_bot.strategies.base import Strategy, StrategyContext
from forex_bot.strategies.mean_reversion import MeanReversionStrategy
from forex_bot.strategies.trend_following import TrendFollowingStrategy
from forex_bot.strategies.volatility_breakout import VolatilityBreakoutStrategy

logger = get_logger(__name__)


def build_strategies(settings: Settings) -> list[tuple[Strategy, dict]]:
    out: list[tuple[Strategy, dict]] = []
    sc = settings.strategy
    if "trend_following" in sc.enabled and sc.trend_following is not None:
        out.append((TrendFollowingStrategy(version=sc.trend_following.version), sc.trend_following.model_dump()))
    if "volatility_breakout" in sc.enabled and sc.volatility_breakout is not None:
        out.append(
            (
                VolatilityBreakoutStrategy(version=sc.volatility_breakout.version),
                sc.volatility_breakout.model_dump(),
            )
        )
    if "mean_reversion" in sc.enabled:
        if settings.app.mode != "paper":
            logger.warning("mean_reversion is paper-only; ignoring in mode=%s", settings.app.mode)
        else:
            out.append((MeanReversionStrategy(), {}))
    return out


@dataclass
class LoopOutcome:
    signals: list[Signal]
    decisions: list[RiskDecision]
    plans: list[OrderPlan]
    executions: list[ExecutionResult]


def fetch_latest_candles(
    broker: Broker,
    candles: CandleRepo,
    *,
    instruments: Iterable[str],
    granularity: str,
    price_components: str,
    count: int,
    daily_alignment: int,
    alignment_timezone: str,
    weekly_alignment: str,
) -> dict[str, CandleFrame]:
    out: dict[str, CandleFrame] = {}
    for inst in instruments:
        request = CandleRequest(
            instrument=inst,
            granularity=granularity,  # type: ignore[arg-type]
            price=price_components,  # type: ignore[arg-type]
            count=count,
            daily_alignment=daily_alignment,
            alignment_timezone=alignment_timezone,
            weekly_alignment=weekly_alignment,
        )
        fetched = broker.get_candles(request)
        candles.upsert_many(
            fetched,
            source="oanda",
            price_components=price_components,
            request_hash=str(hash((inst, granularity, price_components, count))),
        )
        completed = candles.list(inst, granularity, completed_only=True, limit=400)
        out[inst] = CandleFrame.from_candles(inst, granularity, completed)  # type: ignore[arg-type]
    return out


def run_paper_loop(
    settings: Settings,
    broker: Broker,
    instruments_repo: InstrumentRepo,
    candles: CandleRepo,
    signals: SignalRepo,
    decisions: RiskDecisionRepo,
    plans: OrderPlanRepo,
    snapshots: AccountSnapshotRepo,
    spreads: SpreadSnapshotRepo,
    events: SystemEventRepo,
) -> LoopOutcome:
    # Research-freeze guard: refuse to run any strategy not in the
    # approved-strategy registry. Backtests are unaffected.
    assert_loop_strategies_approved("paper", settings.strategy.enabled)
    risk_engine = RiskEngine(settings)
    planner = Planner(risk=risk_engine, signals=signals, decisions=decisions, plans=plans)
    return _execute_loop(
        settings=settings,
        broker=broker,
        instruments_repo=instruments_repo,
        candles=candles,
        spreads=spreads,
        snapshots=snapshots,
        events=events,
        planner=planner,
        executor=None,
    )


def run_practice_loop(
    settings: Settings,
    broker: Broker,
    instruments_repo: InstrumentRepo,
    candles: CandleRepo,
    signals: SignalRepo,
    decisions: RiskDecisionRepo,
    plans: OrderPlanRepo,
    snapshots: AccountSnapshotRepo,
    spreads: SpreadSnapshotRepo,
    events: SystemEventRepo,
    orders: BrokerOrderRepo,
    transactions: TransactionRepo,
) -> LoopOutcome:
    # Research-freeze guard: refuse to run any strategy not approved for
    # this loop mode. A live-mode Settings has already passed the
    # config-layer live gates (load_settings enforces them).
    _loop_mode = "live" if settings.app.mode == "live" else "demo"
    assert_loop_strategies_approved(
        _loop_mode, settings.strategy.enabled,
        live_gates_ok=(_loop_mode == "live"),
    )
    risk_engine = RiskEngine(settings)
    planner = Planner(risk=risk_engine, signals=signals, decisions=decisions, plans=plans)
    reconciler = Reconciler(
        broker=broker, transactions=transactions, snapshots=snapshots, events=events
    )
    executor = Executor(
        settings=settings,
        broker=broker,
        plans=plans,
        orders=orders,
        transactions=transactions,
        snapshots=snapshots,
        events=events,
        reconciler=reconciler,
    )
    pre_report = reconciler.run()
    if not pre_report.clean:
        events.record(
            "loop_blocked", "warn", "reconciliation failed before loop start",
            {"differences": pre_report.differences},
        )
        return LoopOutcome([], [], [], [])
    return _execute_loop(
        settings=settings,
        broker=broker,
        instruments_repo=instruments_repo,
        candles=candles,
        spreads=spreads,
        snapshots=snapshots,
        events=events,
        planner=planner,
        executor=executor,
    )


def _execute_loop(
    *,
    settings: Settings,
    broker: Broker,
    instruments_repo: InstrumentRepo,
    candles: CandleRepo,
    spreads: SpreadSnapshotRepo,
    snapshots: AccountSnapshotRepo,
    events: SystemEventRepo,
    planner: Planner,
    executor: Executor | None,
) -> LoopOutcome:
    market = settings.market
    strategies = build_strategies(settings)
    if not strategies:
        events.record("loop", "warn", "no strategies enabled", None)
        return LoopOutcome([], [], [], [])

    frames = fetch_latest_candles(
        broker,
        candles,
        instruments=market.instruments,
        granularity=market.granularity,
        price_components=market.candle_price_components,
        count=400,
        daily_alignment=market.daily_alignment,
        alignment_timezone=market.alignment_timezone,
        weekly_alignment=market.weekly_alignment,
    )
    quotes = broker.get_prices(market.instruments)
    quotes_by_instrument = {q.instrument: q for q in quotes}

    snapshot = broker.get_account_summary()
    snapshots.insert(snapshot, raw=snapshot.raw)
    positions = broker.list_positions()

    all_signals: list[Signal] = []
    all_decisions: list[RiskDecision] = []
    all_plans: list[OrderPlan] = []
    all_executions: list[ExecutionResult] = []

    for instrument_name in market.instruments:
        instrument = instruments_repo.get(instrument_name)
        if instrument is None:
            events.record(
                "loop", "warn", f"missing instrument metadata for {instrument_name}", None
            )
            continue
        quote = quotes_by_instrument.get(instrument_name)
        if quote is None:
            events.record("loop", "warn", f"no quote for {instrument_name}", None)
            continue
        spread_snap = map_spread_snapshot(quote, instrument.pip_size)
        spreads.insert_quote(quote, raw=quote.model_dump())
        spreads.insert(spread_snap)

        market_state = MarketState(
            quote=quote,
            spread_snapshot=spread_snap,
        )
        for strategy, cfg in strategies:
            ctx = StrategyContext(
                instrument=instrument,
                candles=frames[instrument_name],
                market_state=market_state,
                open_positions=positions,
                config=cfg,
            )
            signal = strategy.generate_signal(ctx)
            if signal is None:
                continue
            all_signals.append(signal)
            inputs = RiskInputs(
                signal=signal,
                instrument=instrument,
                account=snapshot,
                market_state=market_state,
                positions=positions,
                quotes_by_instrument=quotes_by_instrument,
                atr_pips=Decimal(str(signal.features.get("atr_pips", 0.0))) if signal.features.get("atr_pips") else None,
            )
            decision, plan = planner.plan(inputs)
            all_decisions.append(decision)
            if plan is None:
                continue
            all_plans.append(plan)
            if executor is None:
                events.record(
                    "paper_plan",
                    "info",
                    f"would-have-traded {plan.instrument} {plan.side} units={plan.units}",
                    {"plan_id": plan.plan_id, "signal_id": plan.signal_id},
                )
                continue
            outcome = executor.submit(plan)
            all_executions.append(outcome)

    return LoopOutcome(
        signals=all_signals,
        decisions=all_decisions,
        plans=all_plans,
        executions=all_executions,
    )


def warn_once_if_demo_constrained(settings: Settings, instruments: Sequence[str]) -> None:
    home = settings.market.account_currency.upper()
    for inst in instruments:
        if home not in inst.split("_", 1):
            logger.info(
                "instrument %s has neither base nor quote == account currency %s; "
                "sizing requires a cross quote at runtime.",
                inst,
                home,
            )
            return
    _ = utcnow()  # keep the import live for tests that monkeypatch the clock
