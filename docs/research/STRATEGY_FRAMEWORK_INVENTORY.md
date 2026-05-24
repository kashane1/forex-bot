# Strategy Framework Inventory

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-001`
`strategy_evidence: false`

A read-only inventory of the existing strategy / backtest / risk /
data / reporting / research surfaces that any new candidate would
have to plug into. This document is the input to Phase B3
(shortlist) and Phase B4 (preferred candidate evaluation design).
**It writes no code, runs no campaign, and approves nothing.**

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. Every line below is grep-verified
> against the current commit; nothing here implies a new family
> is *authorized* — only that the surface to plug into exists.

## 1. Strategy interface

[`src/forex_bot/strategies/base.py`](../../src/forex_bot/strategies/base.py)
defines the **only** API a strategy must satisfy:

```python
class Strategy(Protocol):
    name: str
    version: str
    def warmup_bars_required(self) -> int: ...
    def generate_signal(self, ctx: StrategyContext) -> Signal | None: ...
```

`StrategyContext` (frozen dataclass) is the **only** data a strategy
is allowed to read at each call:

- `instrument: Instrument` — symbol + pip size + price rounding;
- `candles: CandleFrame` — bar history; the strategy is expected
  to call `.completed_only().df` to avoid mid-bar lookahead;
- `market_state: MarketState` — last quote, last spread snapshot;
- `open_positions: list[Position]` — current open positions; a
  strategy must skip emitting when it already holds the
  instrument (the four existing strategies all do this);
- `config: dict[str, Any]` — per-strategy parameters (typed by
  the corresponding `StrategyConfig` sub-model — see §6).

A strategy returns `Signal | None`. **It never returns an order,
never sizes a position, never bypasses the RiskEngine.** Sizing,
spread gating, session blackout, exposure cap, margin check,
correlation cap, and kill-switch enforcement all sit in the
risk layer (§5).

## 2. Existing strategy modules

[`src/forex_bot/strategies/`](../../src/forex_bot/strategies/):

| module | family | verdict source | key params |
|---|---|---|---|
| [`trend_following.py`](../../src/forex_bot/strategies/trend_following.py) | EMA-trend + Donchian breakout (+ optional ADX gate) | CAMPAIGN_002 REJECT; CAMPAIGN_003 REJECT | ema_fast/slow 50/200, donchian 20, ATR 14, ATR stop 2.5, optional `adx_min` |
| [`volatility_breakout.py`](../../src/forex_bot/strategies/volatility_breakout.py) | Donchian breakout out of an ATR-compressed regime; **no** EMA trend filter | CAMPAIGN_004 REJECT | compression_lookback 60, compression_percentile 40, breakout_lookback 20, ATR stop 2.0 |
| [`pullback_continuation.py`](../../src/forex_bot/strategies/pullback_continuation.py) | EMA-trend regime + pullback-to-EMA + continuation close | CAMPAIGN_007 REJECT (screening fail) | ema 50/200, pullback_lookback 6, pullback_band 0.5, ATR stop 2.0 |
| [`mean_reversion.py`](../../src/forex_bot/strategies/mean_reversion.py) | ADX<20 range regime + z-score extreme + RSI confirmation; optional midline-target exit | CAMPAIGN_008 REJECT (research-only); CAMPAIGN_009 REJECT (research-only) | zscore_lookback 20, z-thresh ±2.0, rsi 14, adx_max 20, ATR stop 1.5, `midline_exit` flag |

[`indicators.py`](../../src/forex_bot/strategies/indicators.py)
exports: `ema`, `atr`, `donchian_high`, `donchian_low`, `adx`,
`rsi`, `zscore`. These are the existing primitives a new family
can compose without adding code under
`src/forex_bot/strategies/`.

## 3. Backtest engine

[`src/forex_bot/backtesting/engine.py`](../../src/forex_bot/backtesting/engine.py)
(676 lines) — the bespoke `BacktestEngine`. Relevant properties
for a new candidate's eval design:

- **Single-instrument, single-position-at-a-time** per backtest
  run; multi-instrument campaigns drive the engine once per pair.
- Replays the strategy **bar-by-bar over completed candles**.
- Calls **`RiskEngine.evaluate(mode='backtest')`** for every
  emitted signal so the same gates that govern paper / demo apply
  to the backtest — except for the operational-only gates
  (`trading_enabled`, `kill_switch`, `reconciled`,
  `pending_order_count`).
- Supports a `--no-risk-engine` mode (legacy direct sizing) for
  the no-RiskEngine comparison evidence path (used by
  CAMPAIGN_002's 1,647-trade isolation report).
- Fill model: bid/ask-aware; never fills on incomplete candles.
  See [`fills.py`](../../src/forex_bot/backtesting/fills.py) for
  `FillModel`, `FillTiming`, and the `NEXT_BAR_OPEN_UNAVAILABLE`
  sentinel.
- Metrics: [`metrics.py`](../../src/forex_bot/backtesting/metrics.py)
  emits `BacktestMetrics`, `TradeRecord`, and an equity bar
  series via `compute_metrics(...)`.
- Outputs: [`exporters.py`](../../src/forex_bot/backtesting/exporters.py)
  writes trades / equity / rejections / report bundles via
  `write_all(...)` and `write_risk_rejections_csv(...)`.
- Audit: [`audit.py`](../../src/forex_bot/backtesting/audit.py)
  reports candle completeness, gaps, duplicates, abnormal
  spreads — the candidate must pass an audit on its data before
  any backtest is trusted.
- D1 aggregation: [`d1_aggregation.py`](../../src/forex_bot/backtesting/d1_aggregation.py)
  aggregates H4 → D1 with next-bar-open fills and a
  non-rollover spread reference. Used by the smoke diagnostics;
  not yet a closed CAMPAIGN_006 path
  ([`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §2).

There is also an **engine-side** walk-forward split helper at
[`backtesting/walk_forward.py`](../../src/forex_bot/backtesting/walk_forward.py)
(`WalkForwardSplit`, `walk_forward_splits`). It is **separate
from** the research harness in
[`research/walk_forward/`](../../research/walk_forward/) — the
research harness is the authorized walk-forward evidence path for
future candidates (see §8 below).

## 4. Engine PnL — what it does and does not include

What the engine accounts for in PnL:

- realized PnL on closed positions from bid/ask fills;
- equity time-series at bar boundaries;
- spread costs implied by bid/ask divergence.

What the engine **does not** include:

- **Financing / swap / rollover.** No financing accrual lives in
  `BacktestEngine`. The existing per-trade
  [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py)
  overlay sits *outside* the engine and is applied at report
  time; the new research calculator under
  [`research/financing/`](../../research/financing/) also sits
  outside the engine and is purely diagnostic. **No candidate's
  reported PnL is net of *historical* financing** today.
- **Commissions** beyond what the spread already accounts for.
- **Slippage** beyond the configured fill model.

This means every new candidate's report **must** carry a
financing overlay (per the protocol §8) — the headline PnL is
otherwise misleading.

## 5. Risk engine

[`src/forex_bot/risk/policy.py`](../../src/forex_bot/risk/policy.py)
(329 lines) — `RiskEngine.evaluate(...)` is the **only** thing
allowed to turn a `Signal` into an `OrderPlan`. Stateless; the
caller persists every `RiskDecision`.

`RiskInputs`:

- `signal: Signal`
- `instrument: Instrument`
- `account: AccountSnapshot`
- `market_state: MarketState`
- `positions: list[Position]`
- `quotes_by_instrument: dict[str, Quote]`
- `realized_pl_today`, `realized_pl_week`, `drawdown_pct`
- `atr_pips: Decimal | None`
- `reconciled: bool` (live-only)

Risk-engine gates (every gate, including the operational-only
ones, listed for the candidate's risk diagnostic checklist):

| gate | source | live-only? |
|---|---|---|
| stop-loss required | `RiskConfig.require_stop_loss` | no |
| spread cap | `SpreadFilterConfig` | no |
| session blackout | `SessionFilterConfig` | no |
| sizing (risk per trade %) | `RiskConfig.risk_per_trade_pct` / `max_risk_per_trade_pct` | no |
| daily loss limit | `RiskConfig.max_daily_loss_pct` | no |
| weekly loss limit | `RiskConfig.max_weekly_loss_pct` | no |
| total drawdown limit | `RiskConfig.max_total_drawdown_pct` | no |
| max open positions | `RiskConfig.max_open_positions` | no |
| max correlated positions | `RiskConfig.max_correlated_positions` | no |
| max positions per instrument | `RiskConfig.max_positions_per_instrument` (default 1) | no |
| margin guards | `MarginConfig` | no |
| no martingale / grid / averaging-down | `RiskConfig` (hard prohibitions) | no |
| pending-order count | `RiskConfig.max_pending_orders` | yes |
| trading_enabled flag | `AppConfig.trading_enabled` | yes |
| kill switch | [`kill_switch.py`](../../src/forex_bot/risk/kill_switch.py) | yes |
| reconciled flag | broker reconciliation state | yes |

[`exposure.py`](../../src/forex_bot/risk/exposure.py) and
[`sizing.py`](../../src/forex_bot/risk/sizing.py) supply the
helpers (`currency_exposure`, `has_open_position`,
`compute_pip_value_home`, `size_position`).

Adding a **new** risk rule for a new strategy family would
require a CODE change. The discovery sprint does not allow that;
the preferred candidate's eval design (Phase B4) must therefore
work **within** the existing gate set, and any necessary new
gate becomes a documented future-sprint dependency.

## 6. Strategy config schema (binding constraint)

[`src/forex_bot/config.py`](../../src/forex_bot/config.py) is
where strategies plug in. The class `StrategyConfig` (extra
`"forbid"`) **explicitly enumerates** the four existing
families:

```python
class StrategyConfig(BaseModel):
    enabled: list[str]
    trend_following: TrendFollowingStrategyConfig | None = None
    volatility_breakout: VolatilityBreakoutStrategyConfig | None = None
    pullback_continuation: PullbackContinuationStrategyConfig | None = None
    mean_reversion: MeanReversionStrategyConfig | None = None
```

`@model_validator` enforces that any name in `enabled` has a
matching sub-config and vice versa. **Adding a fifth strategy
family requires editing `config.py`** — i.e. a future,
human-authorized scaffold sprint. The discovery sprint does
not edit `config.py`; the eval design (Phase B4) must list
"add `StrategyConfig.<new_name>` and `<new_name>StrategyConfig`"
as the first task of that future sprint.

This is also where the `RiskConfig`'s hard prohibitions live
(`require_stop_loss`, no martingale, no grid, no averaging
down). Any future candidate inherits all of them; the
shortlist cannot propose a family that needs to violate any
of them.

## 7. Domain models a new candidate uses (no edit expected)

[`src/forex_bot/domain/`](../../src/forex_bot/domain/) (read-only
for this sprint):

- `candles.CandleFrame` — bar-history container with
  `completed_only()` projection.
- `instruments.Instrument` — symbol, pip size, price rounding,
  display name, currency pair.
- `market.MarketState` — last `Quote` (bid/ask), `SpreadSnapshot`.
- `positions.Position` — open position state.
- `signals.Signal` — the only thing a strategy emits.
- `orders.OrderPlan` — the only thing a risk engine emits.
- `risk.RiskDecision`, `RiskRejectionCode` — gate outcomes.
- `account.AccountSnapshot` — equity / margin state.
- `transactions.ObservedFinancingEvent` (and
  `ObservedFinancingEventRepo` in `data/repositories.py`) — the
  capture / observed-financing path; the table remains empty
  ([`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
  §10).

The candle store and instrument metadata both live in
[`src/forex_bot/data/`](../../src/forex_bot/data/) (SQLite via
[`db.py`](../../src/forex_bot/data/db.py),
[`migrations.py`](../../src/forex_bot/data/migrations.py),
[`repositories.py`](../../src/forex_bot/data/repositories.py)).
The repo's H4 OANDA data covers the seven CAMPAIGN_002 pairs
(EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF,
NZD_USD); rehydration is documented in
[`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md).
No new fetch is allowed for this sprint.

## 8. Walk-forward research harness (authoritative future-evidence path)

[`research/walk_forward/`](../../research/walk_forward/) — the
package a future candidate must use to generate, validate, and
report its walk-forward evaluation. Public API:

```python
from research.walk_forward import (
    Fold, WalkForwardPlan, FoldMetrics, AggregateMetrics,
    WalkForwardResults, ParameterMode, SplitStyle,
    PlanValidationError, validate_plan,
    rolling_window_plan, expanding_window_plan,
    render_plan_md, render_results_md,
)
```

Constraints (mirrored from
[`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)):

- `parameter_mode = "frozen"` is the only authorized mode today.
- Minimum 3 folds; forward-only ordering; no consecutive
  test-window overlap; all boundaries inside the universe
  (`validate_plan` enforces).
- The harness ships no runner — the campaign reads the plan,
  runs the bespoke `BacktestEngine` per fold's test window, and
  builds `FoldMetrics`/`AggregateMetrics`/`WalkForwardResults`.
- Every output carries `strategy_evidence: false` until a
  human-approved promotion flips it (out of scope for this
  protocol).

A new candidate's eval design (Phase B4) therefore must
declare:

- `SplitStyle` (rolling vs expanding);
- `train_days`, `validation_days`, `test_days`, `step_days`;
- minimum fold count and the universe window;
- the per-fold pass/fail metric definitions and their
  thresholds.

## 9. Financing research calculator (authoritative overlay path)

[`research/financing/`](../../research/financing/) — the
package a future candidate must use to compute the financing
overlay. Public API:

```python
from research.financing import (
    PositionInterval, FinancingCalculatorConfig,
    FinancingTreatment, MissingRatePolicy,
    DailyFinancingEvent, PositionFinancingSummary,
    FinancingRunReport, RatePair,
    FinancingRateSource, TableRateSource,
    ConservativeStressRateSource, CONSERVATIVE_BP_PER_DAY,
    default_stress_rate_source,
    calculate_position, calculate_run,
    MissingFinancingRateError,
    load_observed_event_fixture, load_rate_fixture,
    canonical_event_key, utc_date_of,
    FixtureValidationError, ObservedEventDict,
    render_summary_md, dump_events_json,
)
```

Properties relevant to a candidate (mirrored from
[`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)):

- **ESTIMATED only.** Both shipped sources
  (`TableRateSource`, `ConservativeStressRateSource`) emit
  `ESTIMATED`. **MODELED is refused** at every layer.
- **Weekend skip + Wednesday triple swap** are config defaults;
  conservative stress is debit-only on both sides; missing-rate
  policy is `conservative` by default.
- Synthetic rate fixtures exist for **all seven CAMPAIGN_002
  H4 pairs** under
  [`research/financing/fixtures/`](../../research/financing/fixtures/)
  — the candidate can drive a `TableRateSource` from any of
  them as a sanity-check pair-specific overlay.
- A candidate's report **must** embed
  `financing_treatment`, `financing_in_engine_pnl: false`,
  `financing_is_live_blocker: true`,
  `cashflow_home_total`, `cashflow_home_stress_total`,
  `missing_rate_event_count` verbatim.

The reconciliation CLI
[`scripts/reconcile_financing_fixtures.py`](../../scripts/reconcile_financing_fixtures.py)
exists for future MODELED capture work; the discovery sprint
does not use it (no observed data to reconcile against).

## 10. Reporting

[`src/forex_bot/reporting/`](../../src/forex_bot/reporting/):

- [`render.py`](../../src/forex_bot/reporting/render.py) — the
  campaign-report renderer used by
  `scripts/build_campaign_*_report.py`.
- [`weekly.py`](../../src/forex_bot/reporting/weekly.py) —
  weekly summary helpers.

The campaign-report shape is the existing
[`backtests/CAMPAIGN_*_REPORT.md`](../../backtests/) template:
pair table → headline metrics → per-pair detail → cost-stress
regimes → financing overlay → walk-forward (when present) →
verdict. The new candidate's report must follow this shape
plus the additions mandated by the protocol (financing overlay
fields per §9 above; walk-forward results per §8).

## 11. Data sources currently usable

| source | location | use |
|---|---|---|
| OANDA practice H4 (7 pairs) | local SQLite store (e.g. `data/campaign_002.sqlite3`; provenance hashes recorded) | the only authorized historical bar data for backtests |
| Instrument metadata | OANDA metadata audit + repo-side rounding tables | sizing, rounding |
| Synthetic financing rate fixtures (7 pairs, 2-week each) | `research/financing/fixtures/rates_two_week_*.json` | overlay diagnostic |
| Synthetic observed-financing fixtures | `research/financing/fixtures/observed_*.json` | reconciliation diagnostic (no real broker data) |
| Free / local parity verifier inputs | `research/parity_verifier/` | independent corroboration |

**No new fetch is authorized for this sprint.** Any data
requirement beyond this list is a future-sprint dependency.

## 12. Campaign / pre-commit / report doc templates

The existing campaign documents follow a consistent shape that
the new candidate's eval design (Phase B4) and future
pre-commit doc must mirror:

- `docs/research/<CAMPAIGN_NAME>_PRECOMMIT.md` — hypothesis,
  strategy, frozen parameters, data, splits, costs, financing,
  test-window discipline, pass/fail gates. Reference:
  [`CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md`](CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md).
- `backtests/<CAMPAIGN_NAME>_REPORT.md` — headline metrics, per
  pair, gate verdict, walk-forward, financing overlay,
  independent corroboration, verdict.
- `docs/research/<CAMPAIGN_NAME>_POSTMORTEM.md` (optional but
  recommended for REJECT campaigns).
- `docs/research/<CAMPAIGN_NAME>_WALK_FORWARD.md` — new doc
  template implied by
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8 row 3.
- `docs/research/<CAMPAIGN_NAME>_FINANCING_RECONCILIATION.md` —
  new doc template implied by §8 row 4.
- Manifest update in
  [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json) with
  `strategy_approved: false` (until a deliberate human flip).

## 13. What the discovery sprint *cannot* answer from this surface

These open questions are out-of-scope for the discovery sprint
and are recorded so Phase B4 can encode them as future-sprint
dependencies:

- **MODELED financing for the candidate's pairs/window.**
  Requires a credentialed practice / live capture sprint
  ([`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
  §10) — separately authorized.
- **`StrategyConfig.<new_name>` slot.** Requires editing
  [`config.py`](../../src/forex_bot/config.py).
- **New risk-engine gate** (e.g. a carry-aware exposure cap).
  Requires editing [`policy.py`](../../src/forex_bot/risk/policy.py).
- **New domain primitive** (e.g. a session-of-day tag on
  candles). Requires editing
  [`domain/`](../../src/forex_bot/domain/) and possibly the
  data store.
- **New indicator** not already in
  [`indicators.py`](../../src/forex_bot/strategies/indicators.py).
- **Engine-PnL financing accrual.** Requires editing
  [`backtesting/engine.py`](../../src/forex_bot/backtesting/engine.py).
- **A new asset universe** (non-FX). Requires a data-foundation
  sprint per
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §5.
- **A valid D1 backtest path.** Requires closing the CAMPAIGN_006
  blocker per
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §2.

Each of these is a separate, future, human-authorized branch.
None is undertaken in this sprint.

## 14. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.**
- No `live-loop` command exists; CLI commands inspected:
  `doctor`, `sync-instruments`, `fetch-candles`, `backtest`,
  `audit-data`, `paper-loop`, `demo-loop`, `reconcile`, `report`.
- No code edited in this phase.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 15. Cross-links

- Sprint plan:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md)
- Protocol:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- Next-direction memo:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- Walk-forward protocol:
  [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- Walk-forward status:
  [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- Financing protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Financing status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Strategy status registry:
  [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- Future research backlog:
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
