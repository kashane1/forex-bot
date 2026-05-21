--- FILE: 00_README.md ---
# Forex Bot Founders Pack

Date: 2026-05-21
Status: Engineering specification, not financial advice
Primary broker choice: OANDA
Preferred tooling: Native Python bot first, with QuantConnect Lean used deliberately as a research/backtest/live-engine option rather than casually mixed in.

## Executive verdict

The notes are directionally strong on engineering: OANDA-first is a reasonable path for a Mac-native autonomous bot because OANDA has a documented v20 REST API, practice/live account flow, pricing, candles, order endpoints, account state, and transaction streams. QuantConnect Lean is also a serious tool for research, backtesting, optimization, and live trading.

The main correction is this: do not use Lean "whenever possible" unless you define exactly what Lean owns. A common failure mode is to backtest in Lean, execute in a separate custom Python engine, and accidentally implement different candle handling, fill logic, spread logic, sizing, rounding, and order semantics. That creates false confidence. The repo should choose one of these patterns:

1. Native Python OANDA bot as canonical runtime, with a small internal backtester and optional Lean parity tests.
2. Lean-first strategy engine, with OANDA live trading through Lean.
3. Hybrid, but only if the strategy, risk model, and execution model are shared or mechanically generated from one canonical specification.

Recommended for this project: start with option 1 for the MVP because the bankroll is small, the strategy is simple, and direct OANDA integration gives you maximal control and minimal platform overhead. Use Lean as an independent benchmark/research harness after the OANDA adapter, ledger, risk engine, and backtest assumptions are stable. Re-evaluate Lean-first after the first validated demo/paper period.

## What this pack contains

- `01_DECISION_MEMO.md` - final architecture recommendation and alternative analysis.
- `02_PRD.md` - product requirements for the first repo build.
- `03_ARCHITECTURE.md` - component boundaries, runtime flow, and repo layout.
- `04_OANDA_ADAPTER_SPEC.md` - broker adapter contract and OANDA endpoint plan.
- `05_RISK_POLICY.md` - mandatory risk limits, kill switches, and position sizing.
- `06_STRATEGY_SPEC.md` - v1 strategy definitions and what is excluded.
- `07_DATA_BACKTEST_VALIDATION.md` - data, backtesting, and model validation rules.
- `08_REPO_SCAFFOLD_AND_TASKS.md` - implementation roadmap and file tree.
- `09_AI_BUILD_PROMPT.md` - prompt to give Codex or Claude.
- `10_RUNBOOKS.md` - local ops, incident response, and deployment notes.
- `11_CONFIG_EXAMPLES.md` - YAML examples and environment variables.
- `12_ACCEPTANCE_CRITERIA.md` - tests and go-live gates.
- `13_SOURCES.md` - source list used to ground the spec.

## Non-negotiable principles

1. No LLM in the live order path.
2. No live trading until the safety gates pass.
3. Risk engine must approve every order plan.
4. Every live order must have a server-side protective stop or equivalent risk-limiting order attached at submission time when supported.
5. No grid, no martingale, no averaging down.
6. Demo/paper first; live mode must require an explicit configuration flag and separate credentials.
7. Backtests are evidence, not proof. Strategy promotion requires out-of-sample tests, walk-forward tests, paper trading, and manual approval.

## First build target

Build a demo-only OANDA practice bot that can:

- Load config safely.
- Fetch account summary and tradeable instrument metadata.
- Fetch H1/H4 candles using bid/ask/mid data as required.
- Persist candles, prices, signals, order plans, orders, fills, transactions, and account snapshots.
- Produce signals from a trend-following strategy.
- Convert signals into risk-approved order plans.
- Submit practice orders only after all guards pass.
- Reconcile broker state against local ledger on every loop and after every order.
- Generate weekly reports.

The first version does not need ML, GA, news trading, scalping, triangular arbitrage, portfolio optimization, or fully automated live deployment.


--- FILE: 01_DECISION_MEMO.md ---
# Decision Memo

## Context

The intended project is a forex trading bot for OANDA, built by a software engineer, with interest in QuantConnect Lean tooling. The initial bankroll discussed in the notes is USD 500. The engineering goal is not to build an income machine; it is to build a controlled research and execution system that can survive, log reality, and support disciplined iteration.

## Decision

Build OANDA-first with a native Python runtime for the MVP. Keep the code broker-neutral at the domain layer, but implement only the OANDA adapter initially. Use QuantConnect Lean as a deliberate secondary path for research and parity testing, not as an undefined side tool.

Recommended MVP stack:

- Python 3.12+
- OANDA v20 REST API
- OANDA practice account first
- SQLite for operational ledger; optional DuckDB/Parquet for research data
- Pydantic for config/domain validation
- httpx or requests for HTTP
- pandas/numpy for indicator calculations
- pytest/respx or equivalent for tests
- Typer CLI for operational commands
- launchd on macOS only after demo stability

## Why OANDA-first is reasonable

OANDA documents the v20 REST API for practice/live account access, token-based authentication, accounts, pricing, candles, orders, trades, positions, and transaction streams. This makes it a straightforward engineering target for a local bot.

OANDA also exposes account-specific instrument metadata such as instrument name, pip location, display precision, margin rate, minimum trade size, and trailing-stop limits. The bot should fetch and cache this metadata instead of hardcoding pip sizes, margin assumptions, or trade-size constraints.

## Lean decision

Lean is valuable, but the pack recommends not making it the main runtime in v0 unless you intentionally choose Lean-first. Lean brings a professional event-driven engine, backtesting, optimization, research notebooks, reports, and live trading pathways, including OANDA integration. However, using Lean's CLI/live deployment has platform requirements, and the QuantConnect docs currently state that using the CLI requires membership in an organization on a paid tier.

Lean should enter the project in one of these ways:

### Option A: Native Python canonical runtime, Lean as independent benchmark

Use the Python bot to define strategy, risk, broker adapter, and ledger. Separately implement a Lean version of the same strategy to detect whether results are broadly consistent. This is best for fast MVP iteration.

### Option B: Lean-first

Use Lean for research, backtests, and live deployment from the beginning. This reduces custom infrastructure but increases framework coupling and may require paid QuantConnect organization access. This is best if you want formal reports, optimization, and event-driven live trading as the core product from day one.

### Option C: Hybrid shared core

Create pure Python strategy/risk functions that can run inside both the native bot and Lean. This is possible but needs discipline, wrappers, and parity tests. Avoid this in v0 unless you are prepared to write the adapter layer carefully.

## Recommended final stance

Use native Python OANDA for v0. Add Lean after the first stable data and risk pipeline exists. The main reason is not that Lean is bad; it is that two runtimes before you have validated the domain model will create unnecessary surface area.

## Alternatives considered

### FOREX.com first

The original notes understate FOREX.com a little. FOREX.com advertises REST API trading with streaming prices and account/order functionality, though access may require contacting support after opening a standard account. Since the user has already chosen OANDA, this does not change the recommendation. It only means the original claim that FOREX.com lacks a usable API path should be softened.

### MT5/MQL5 first

MT5 is a viable trading ecosystem, but it is not the cleanest Mac-native Python path. The official MetaTrader5 Python package on PyPI currently distributes Windows x86-64 wheels, and MT5-on-mac setups tend to introduce terminal/Wine/bridge complexity. If an MT5 route is ever required, prefer an MQL5 Expert Advisor or a Windows/VPS setup instead of a fragile Python-to-MT5 bridge on macOS.

### Backtrader first

Backtrader remains useful for local strategy experimentation, but it should not be the live OANDA layer for this project. If used, treat it as exploratory research only.

## Evidence-backed assumptions

- OANDA v20 API exists and supports account access, REST calls, token authentication, prices, candles, orders, and transaction streams.
- OANDA instrument metadata should be queried from the account, not hardcoded.
- Lean supports OANDA live brokerage workflows through its CLI/cloud documentation and OANDA brokerage plugin.
- Lean has useful research/backtesting/optimization/live-trading tooling.
- FOREX.com does have an advertised REST API route, so it should not be dismissed as impossible.
- MT5 Python package distribution is Windows-oriented on PyPI at the time of this pack.
- Trend-following/time-series momentum has academic evidence across asset classes including currencies, but that evidence does not prove a small retail OANDA implementation will be profitable.
- Retail forex and CFD trading carry high risk, and simulated performance has known limitations.

## Risky or overconfident assumptions in the original notes

1. "Trend following is strongest first strategy" is directionally defensible, but it is not proof that a Donchian/EMA/ATR strategy on a few OANDA pairs will survive spread, financing, slippage, and regime changes.
2. "H1/H4 avoids scalping problems" is sensible but not sufficient. You still need spread filters, rollover avoidance, execution realism, weekend controls, and liquidity checks.
3. "OANDA samples are a good starting point" is true only as examples. They are not production scaffolds.
4. "$500 can run a real bot" is mechanically possible, but economically constrained. It is mainly enough for learning and data collection, not reliable income.
5. "Use Lean whenever possible" is dangerous unless you define ownership boundaries and parity tests.
6. "Weekly AI-assisted improvement" can help with review, but it can also encourage parameter chasing. Require validation gates before any change goes live.
7. "Carry filter later" is fine, but carry/swap data availability and financing treatment must be solved before using carry as a signal.

## Decision checkpoints

Revisit this decision after:

- 30 demo trading days with no reconciliation mismatches.
- At least 100 closed paper/demo trades, or 3 months of low-frequency live-equivalent demo operation, whichever comes first.
- A complete execution-quality report covering spread, slippage, skipped trades, order rejects, latency, financing, and gaps.
- A Lean parity backtest that either agrees with the native engine within tolerance or documents why it differs.


--- FILE: 02_PRD.md ---
# Product Requirements Document

## Product name

Working name: `oanda-forex-research-bot`

## Product summary

A local Python application for researching, paper/demo trading, risk-controlling, executing, reconciling, and reporting low-frequency OANDA forex strategies. It is designed to start in OANDA practice mode and make live trading deliberately hard to enable.

## Primary user

A software engineer who wants to build and operate a personal forex automation system with strong engineering controls, broker-state reconciliation, local logs, and AI-assisted review outside the live decision path.

## Goals

1. Provide a clean OANDA practice-trading bot that is reliable enough to run unattended but conservative enough to fail safe.
2. Separate strategy signal generation from risk approval and broker execution.
3. Make every decision auditable through durable logs and a local ledger.
4. Support deterministic backtests and paper/demo comparisons.
5. Allow weekly/monthly review by humans and coding assistants without exposing live broker credentials.

## Non-goals for v0

- No promise of profit.
- No live trading by default.
- No LLM-based live trade decisions.
- No tick scalping or high-frequency trading.
- No triangular arbitrage.
- No grid, martingale, averaging down, or recovery schemes.
- No ML/GA live strategy in v0.
- No multi-broker support beyond interfaces and stubs.
- No cloud deployment until local demo stability exists.

## MVP scope

### Must have

- CLI commands:
  - `bot doctor`
  - `bot sync-instruments`
  - `bot fetch-candles`
  - `bot backtest`
  - `bot paper-loop`
  - `bot demo-loop`
  - `bot reconcile`
  - `bot report weekly`
- OANDA practice account integration.
- Read-only mode by default.
- Explicit `allow_order_submission: true` required for any broker order.
- Separate `allow_live_trading: true` required for live environment.
- Strategy plugins that return signals, not orders.
- Risk engine that converts approved signals into order plans.
- Broker adapter that submits, modifies, closes, and reconciles only approved order plans.
- Server-side stop loss required for every new position where supported.
- Local persistence for candles, spreads, signals, orders, fills, transactions, account snapshots, and risk events.
- Structured logs in JSONL.
- Unit tests for sizing, pip value, risk approvals, order planning, OANDA response parsing, and config safety.

### Should have

- Lean parity harness for at least one strategy.
- Weekly report generation in Markdown and HTML.
- Export of trades/signals to CSV/Parquet.
- Launchd plist template for macOS.
- Notification hook abstraction for future email/Slack/Telegram/webhook support.

### Could have later

- DuckDB/Parquet research store.
- Economic calendar/news blackout module.
- Carry/swap-aware filters.
- Multi-account support.
- VPS deployment.
- Cloud dashboards.

## User stories

1. As the operator, I can verify my OANDA practice credentials and account metadata without submitting orders.
2. As the operator, I can backfill candles for allowed instruments and inspect missing data.
3. As the operator, I can run a backtest and see metrics, trades, and configuration hash.
4. As the operator, I can run a paper loop that generates would-have-traded signals without broker orders.
5. As the operator, I can run a practice demo loop that submits tiny OANDA practice orders only when all guards pass.
6. As the operator, I can stop the bot by setting a kill-switch file or config flag.
7. As the operator, I can reconcile local state with OANDA account state after restart, network loss, or order submission.
8. As the operator, I can produce a weekly report and ask an AI assistant to review it without exposing secrets.

## Safety requirements

- Secrets must come only from environment variables or a local ignored secrets file.
- Live account IDs and tokens must never be committed.
- The app must refuse to start in live mode unless all live gates are explicitly enabled.
- The app must refuse to submit orders when local ledger and broker state disagree.
- The app must stop opening new positions after daily/weekly loss limits or drawdown thresholds are hit.
- The app must block orders when spread, price status, market status, or instrument metadata is invalid.
- The app must round order units and prices using OANDA instrument metadata.

## Success metrics

Engineering success is measured before trading performance:

- 0 unauthorized order submissions.
- 0 live orders unless live gates are explicitly enabled.
- 0 unreconciled positions after restart.
- 100% of order attempts linked to signal, order plan, risk decision, broker response, and transaction IDs.
- Backtest and demo execution assumptions documented for every strategy version.
- Weekly report generated without manual database edits.

Trading research success requires:

- Positive out-of-sample expectancy after realistic costs.
- Acceptable max drawdown under stress tests.
- Stable performance across reasonable parameter ranges.
- Demo results not materially worse than backtest beyond predefined tolerance.


--- FILE: 03_ARCHITECTURE.md ---
# Architecture

## System principle

Strategies are allowed to have opinions. The risk engine is allowed to approve or reject. Only the execution layer can talk to the broker. The broker is treated as source of truth for positions, open trades, open orders, margin, and transactions.

## Runtime flow

```text
market data
  -> candle builder / data store
  -> strategy signal
  -> risk engine
  -> order plan
  -> broker adapter
  -> broker response
  -> transaction stream / account snapshot
  -> ledger reconciliation
  -> reports and alerts
```

## Major components

### Config layer

Loads YAML plus environment variables. Validates with Pydantic. Refuses unsafe combinations such as live environment without `allow_live_trading: true`.

### Domain model

Pure Python dataclasses or Pydantic models for:

- Instrument
- Candle
- Quote
- SpreadSnapshot
- Signal
- RiskDecision
- OrderPlan
- BrokerOrder
- Fill
- Trade
- Position
- AccountSnapshot
- Transaction
- StrategyRun
- BacktestRun
- Report

### Broker interface

Defines a strict adapter contract. OANDA implements it first. The domain layer must not know OANDA endpoint details.

### Data layer

SQLite is the operational ledger. Optional DuckDB/Parquet can be added for research. SQLite is enough for v0 and easier to audit.

### Strategy layer

Strategies consume candles, market state, and config. They emit `Signal` objects. They must not place orders, read credentials, or perform broker calls.

### Risk layer

Consumes account state, instrument metadata, current spread, open exposure, recent P/L, and a strategy signal. Emits approved or rejected `RiskDecision` plus an `OrderPlan` if approved.

### Execution layer

Consumes approved order plans only. Performs idempotency checks, submits orders to OANDA practice/live depending on config, and records broker responses.

### Reconciliation layer

On startup and after every order event, compare local ledger against OANDA account details, open orders, trades, positions, and transactions. If mismatch is unresolved, block new orders.

### Reporting layer

Produces daily/weekly/monthly reports from the ledger. Reports should include execution metrics, risk events, blocked trades, strategy performance, and rule violations.

## Suggested repo tree

```text
forex-bot/
  pyproject.toml
  README.md
  .env.example
  .gitignore
  configs/
    paper.yaml
    practice.yaml
    live.example.yaml
  src/
    forex_bot/
      __init__.py
      cli.py
      config.py
      clock.py
      logging_config.py
      domain/
        account.py
        candles.py
        instruments.py
        orders.py
        positions.py
        risk.py
        signals.py
        transactions.py
      broker/
        base.py
        oanda.py
        errors.py
        mapping.py
      data/
        db.py
        migrations.py
        repositories.py
        candle_store.py
      strategies/
        base.py
        trend_following.py
        volatility_breakout.py
        mean_reversion.py
        indicators.py
      risk/
        sizing.py
        exposure.py
        policy.py
        kill_switch.py
      execution/
        planner.py
        executor.py
        reconciliation.py
        retry_policy.py
      backtesting/
        engine.py
        fills.py
        metrics.py
        walk_forward.py
      reporting/
        weekly.py
        render.py
      lean/
        README.md
        parity_notes.md
  tests/
    unit/
    integration/
    fixtures/
  scripts/
    install_launchd.sh
    uninstall_launchd.sh
  docs/
    architecture.md
    risk_policy.md
    strategy_research.md
    runbooks.md
```

## Loop types

### Paper loop

Generates signals and order plans but does not submit broker orders. Saves would-have-traded events.

### Practice loop

Submits to OANDA practice only after explicit config approval. Used for execution testing.

### Live loop

Disabled until all acceptance gates pass. Requires separate config, separate environment variables, and manual approval.

## Failure behavior

The default failure mode is `block_new_orders`. Examples:

- Cannot load config: exit.
- Cannot fetch account: exit or block.
- Cannot fetch current prices: block.
- Current spread too wide: block.
- Missing instrument metadata: block.
- Reconciliation mismatch: block.
- Kill switch active: block and optionally flatten if configured.
- Order submit returns unknown status: block and reconcile.
- Transaction stream disconnects: reconnect, poll `transactions/sinceid`, reconcile, then resume if clean.

## Lean interoperability plan

The repo should include a `src/forex_bot/lean/README.md` explaining the chosen Lean boundary. For v0, Lean should not be required to run the bot. Later, either:

1. Implement the same strategy in Lean for parity backtests, or
2. Move the strategy into Lean as canonical runtime if Lean-first becomes the decision.

Any Lean implementation must document differences in fill model, quote source, spread model, rollover treatment, and order semantics.


--- FILE: 04_OANDA_ADAPTER_SPEC.md ---
# OANDA Adapter Specification

## Purpose

Implement a broker adapter that maps the internal domain model to OANDA v20 REST API calls. The adapter must support read-only operations first, then practice order submission after risk approval.

## Credentials and environments

Use environment variables only:

- `OANDA_ENVIRONMENT`: `practice` or `live`
- `OANDA_ACCOUNT_ID_PRACTICE`
- `OANDA_ACCESS_TOKEN_PRACTICE`
- `OANDA_ACCOUNT_ID_LIVE`
- `OANDA_ACCESS_TOKEN_LIVE`

The app must refuse live mode unless:

- `environment: live`
- `allow_live_trading: true`
- `allow_order_submission: true`
- `live_acknowledgement` matches an exact configured phrase
- the account ID comes from the live env var, not practice

## Adapter interface

`Broker` should expose:

```python
class Broker(Protocol):
    def get_account_summary(self) -> AccountSnapshot: ...
    def get_account_details(self) -> AccountDetails: ...
    def list_instruments(self) -> list[Instrument]: ...
    def get_candles(self, request: CandleRequest) -> list[Candle]: ...
    def get_prices(self, instruments: list[str]) -> list[Quote]: ...
    def stream_prices(self, instruments: list[str]) -> Iterator[Quote | Heartbeat]: ...
    def list_open_orders(self) -> list[BrokerOrder]: ...
    def list_open_trades(self) -> list[Trade]: ...
    def list_positions(self) -> list[Position]: ...
    def submit_order(self, plan: OrderPlan) -> BrokerOrderResult: ...
    def close_trade(self, trade_id: str, units: Decimal | None = None) -> BrokerOrderResult: ...
    def get_transactions_since(self, last_transaction_id: str) -> list[Transaction]: ...
    def stream_transactions(self) -> Iterator[Transaction | Heartbeat]: ...
```

## Endpoint plan

Use the OANDA docs as source of truth. v0 needs:

- `GET /v3/accounts` - verify token and accounts.
- `GET /v3/accounts/{accountID}` - full account details for reconciliation.
- `GET /v3/accounts/{accountID}/summary` - NAV, balance, margin, P/L snapshot.
- `GET /v3/accounts/{accountID}/instruments` - instrument metadata.
- `GET /v3/accounts/{accountID}/instruments/{instrument}/candles` - historical candles.
- `GET /v3/accounts/{accountID}/pricing` - current bid/ask prices and tradeable status.
- `GET /v3/accounts/{accountID}/pricing/stream` - streaming prices when needed.
- `POST /v3/accounts/{accountID}/orders` - order submission.
- `GET /v3/accounts/{accountID}/orders` - open/pending orders.
- `GET /v3/accounts/{accountID}/trades` - open trades.
- `GET /v3/accounts/{accountID}/positions` - positions.
- `GET /v3/accounts/{accountID}/transactions/sinceid` - catch-up after disconnect.
- `GET /v3/accounts/{accountID}/transactions/stream` - broker events.

## Important OANDA-specific details

### Candle data

- Store candle `complete` flag and refuse to trade on incomplete candles unless a strategy explicitly supports it.
- Store bid, ask, and midpoint components when requested.
- Do not silently use midpoint prices for fills.
- Respect OANDA daily alignment and timezone settings.
- Store the exact request parameters used for any backtest dataset.

### Price stream

OANDA's pricing stream is not a full tick feed. It can provide at most 4 prices per second for each requested instrument and may not send every price during rapid movement. The strategy should therefore remain low-frequency. Do not design a scalper around this stream.

### Instrument metadata

Instrument metadata includes fields such as:

- name
- type
- display precision
- pip location
- trade units precision
- minimum trade size
- margin rate
- trailing stop distance constraints

Use these fields for rounding, sizing, pip calculations, margin checks, and validation.

### Order metadata and idempotency

Use OANDA `clientExtensions` where appropriate:

- deterministic client order ID derived from strategy run ID + signal ID + timestamp bucket
- tag with strategy name and version
- comment with config hash

Before submitting an order, check local ledger and broker open orders/trades for the same client ID to avoid duplicate orders after retries.

### Order types for v0

Implement only:

- Market order with stop-loss-on-fill.
- Optional take-profit-on-fill.
- Optional trailing stop only after basic stop-loss flow is reliable.

Do not implement complex order types until the reconciliation layer is proven.

### Protective stops

Every new position must include a stop loss on fill when supported. If OANDA rejects the stop loss or creates an order without protection, the execution layer must immediately block further trading and reconcile. Depending on configuration, it may close the unprotected trade.

## Error handling

Classify errors:

- Auth errors: exit and block.
- Invalid account/instrument: exit and block.
- 4xx order validation error: record rejection, block signal, do not retry blindly.
- 429/rate limit or transient 5xx: retry with bounded exponential backoff and jitter.
- Network timeout before knowing order status: do not retry the same order until idempotency check and reconciliation complete.
- Stream disconnect: reconnect and backfill transactions using last transaction ID.

## Reconciliation requirement

After startup and after every order submission:

1. Fetch account details.
2. Fetch open orders/trades/positions.
3. Fetch transactions since the last stored transaction ID.
4. Compare against local ledger.
5. If mismatch cannot be explained, set `trading_blocked = true`.

## Testing requirements

- Unit tests for mapping OANDA instrument metadata to domain model.
- Unit tests for candle parsing and complete/incomplete handling.
- Unit tests for order request construction.
- Unit tests for idempotency key generation.
- Integration tests using mocked OANDA responses.
- Optional practice-account smoke tests gated behind explicit environment variables.

## Security requirements

- Never log tokens.
- Redact account IDs in logs unless `debug_sensitive: true`, which must never be enabled in committed configs.
- Do not write secrets to the SQLite ledger.
- Provide `.env.example` only, not `.env`.


--- FILE: 05_RISK_POLICY.md ---
# Risk Policy

## Mission

The first mission is survival and clean data, not income. A USD 500 bankroll is too small to justify aggressive leverage. The bot should behave like an instrumented research system with strict capital preservation.

## Hard prohibitions

The bot must never implement these in live or demo order submission:

- Martingale.
- Grid averaging.
- Averaging down after loss.
- Doubling after loss.
- Removing or widening stop loss because a trade is losing.
- Opening multiple correlated positions during v0.
- Trading without a protective stop.
- Trading during an unreconciled broker/local state mismatch.
- Trading while kill switch is active.
- Trading during configured market blackout windows.
- LLM-generated live trade decisions.

## Default risk limits

```yaml
risk:
  starting_equity_usd: 500
  risk_per_trade_pct: 0.25
  max_risk_per_trade_pct: 0.50
  max_daily_loss_pct: 1.00
  max_weekly_loss_pct: 2.00
  max_total_drawdown_pct: 8.00
  max_open_positions: 1
  max_pending_orders: 1
  max_correlated_positions: 1
  max_positions_per_instrument: 1
  require_stop_loss: true
  require_server_side_protection: true
  allow_martingale: false
  allow_grid: false
  allow_averaging_down: false
```

## Position sizing

The core sizing formula:

```text
risk_amount_home = account_nav_home * risk_per_trade_pct / 100
stop_distance_price = abs(entry_price - stop_price)
pip_size = 10 ** instrument.pip_location
stop_distance_pips = stop_distance_price / pip_size
pip_value_per_unit_home = broker_or_conversion_model(instrument, account_currency, current_prices)
raw_units = risk_amount_home / (stop_distance_pips * pip_value_per_unit_home)
units = round_down_to_trade_units_precision(raw_units)
```

Then apply constraints:

- `units >= minimumTradeSize`
- `units <= maximumOrderUnits`
- estimated margin required fits configured margin buffer
- position value does not exceed max notional exposure
- currency exposure is within caps
- spread and slippage assumptions do not invalidate the stop/risk

If any input is missing, reject the trade.

## Spread filter

Reject new trades when:

- price status is not tradeable
- bid or ask is missing
- spread pips exceeds instrument-specific max
- spread / ATR exceeds configured threshold
- current spread is above recent percentile threshold

Example:

```yaml
spread_filter:
  enabled: true
  max_spread_pips:
    EUR_USD: 1.5
    USD_JPY: 2.0
    GBP_USD: 2.5
    AUD_USD: 2.0
    USD_CAD: 2.5
  max_spread_to_atr_pct: 8.0
```

## Time and event filters

In v0, avoid known problematic windows rather than trying to model them:

- no new trades around daily rollover
- no new trades near Friday close
- no new trades immediately after Sunday open
- no weekend holds unless explicitly enabled
- no trading around high-impact news until a calendar module exists

Example:

```yaml
session_filter:
  timezone: America/New_York
  block_new_trades:
    - name: rollover
      start: "16:45"
      end: "17:15"
    - name: friday_close
      day: Friday
      start: "15:00"
      end: "23:59"
    - name: sunday_open
      day: Sunday
      start: "00:00"
      end: "19:00"
```

## Daily and weekly loss controls

Track realized and unrealized P/L. If either daily or weekly loss threshold is breached:

- block new trades
- continue monitoring open trades
- do not widen stops
- optionally flatten positions only if `auto_flatten_on_loss_limit: true`

Flattening can reduce tail risk but can also crystallize temporary drawdowns. Default in v0: block new trades and preserve existing protective exits unless a critical risk condition exists.

## Margin buffer

The bot must treat broker leverage as a ceiling, not a target. Add a margin buffer rule:

```yaml
margin:
  min_margin_available_pct_of_nav: 80
  max_margin_used_pct_of_nav: 10
  reject_if_margin_closeout_percent_above: 20
```

## Exposure rules

Because forex pairs share currencies, a long EUR/USD and long GBP/USD are both short USD exposure. v0 should have only one open position. Later versions should track currency-level exposure.

## Kill switch

Implement both:

- config kill switch: `trading_enabled: false`
- file kill switch: if `./KILL_SWITCH` exists, block all new orders immediately

Optional emergency mode:

```yaml
kill_switch:
  block_new_orders: true
  cancel_pending_orders: true
  flatten_positions: false
```

## Risk decision audit

Every signal must receive a stored risk decision:

- approved/rejected
- rejection reason codes
- account NAV used
- instrument metadata version
- spread snapshot
- stop distance
- units before and after rounding
- estimated risk
- estimated margin
- config hash

## Manual approval gates

No strategy can move to live unless:

1. Unit tests pass.
2. Backtest passes minimum criteria.
3. Out-of-sample passes.
4. Walk-forward passes.
5. Practice demo period passes.
6. Reconciliation is clean.
7. Manual review approves exact config hash.


--- FILE: 06_STRATEGY_SPEC.md ---
# Strategy Specification

## Strategy interface

Strategies emit signals. They do not size positions, submit orders, read credentials, or mutate broker state.

```python
class Strategy(Protocol):
    name: str
    version: str

    def warmup_bars_required(self) -> int: ...

    def generate_signal(
        self,
        instrument: Instrument,
        candles: CandleFrame,
        market_state: MarketState,
        open_positions: list[Position],
        config: StrategyConfig,
    ) -> Signal | None: ...
```

Signal fields:

```text
signal_id
strategy_name
strategy_version
instrument
timeframe
timestamp
side: long | short | flat
entry_intent: market | stop | limit
confidence: optional numeric, not used for leverage in v0
stop_model
stop_price
exit_model
features: dict
reason: text
```

## V1 strategy: trend following

### Hypothesis

Major FX pairs sometimes trend across H1/H4 horizons. A simple trend-following breakout system with ATR-based risk, strict spread filters, and low leverage may produce a realistic research baseline.

### Timeframes

- Primary: H4
- Optional: H1 for entries with H4 direction filter

### Instruments

Start with a small whitelist:

- EUR_USD
- USD_JPY
- GBP_USD
- AUD_USD
- USD_CAD

Add pairs only after spread/financing/liquidity checks.

### Indicators

- EMA fast: 50
- EMA slow: 200
- Donchian lookback: 20 or 55 bars
- ATR lookback: 14

### Long setup

- EMA fast > EMA slow
- close breaks above Donchian high from prior completed bars
- ATR is above minimum threshold
- spread filter passes
- no open position
- session filter passes

### Short setup

- EMA fast < EMA slow
- close breaks below Donchian low from prior completed bars
- ATR is above minimum threshold
- spread filter passes
- no open position
- session filter passes

### Stops and exits

- Initial stop: `entry - atr_multiple * ATR` for long, `entry + atr_multiple * ATR` for short
- Default ATR multiple: 2.0 to 3.0; optimize only inside predefined ranges
- Exit on trailing ATR stop, opposite breakout, or max bars in trade
- Never widen stop after entry

### Validation notes

The evidence for broad time-series momentum supports this as a research candidate, not as proof of profitability. The exact implementation must survive costs, spread, financing, slippage, candle alignment, and parameter robustness tests.

## V1 strategy: volatility breakout

### Hypothesis

Breakouts following range compression can capture trend expansions, but false breakouts are common. This strategy is closely related to trend following and should share most infrastructure.

### Setup

- H1/H4 timeframe
- Compression defined by lower-than-recent ATR or Donchian width percentile
- Entry on break of compression range
- Direction filter optional: higher timeframe EMA regime
- Spread/ATR ratio must pass
- No trade near rollover or thin sessions

### Stops and exits

- Initial stop on opposite side of compression range or ATR stop
- Optional take-profit at fixed R only during testing
- Prefer trailing stop or time-based exit

## Paper-only strategy: mean reversion

### Hypothesis

Range-bound FX markets may revert after overextension, but trend regimes can cause severe losses. Therefore mean reversion must remain paper-only until validated.

### Setup

- Active only when trend-strength filter says range
- Example filters: ADX below threshold, EMA distance low, Donchian width stable
- Entry: z-score, Bollinger, or RSI-style overbought/oversold
- Exit: midline, fixed R, or time stop

### Mandatory guards

- Disabled during strong trend
- Disabled during high volatility expansion
- Disabled when spread/ATR is high
- Hard stop required

## Strategy families excluded from v0

### Triangular arbitrage

Rejected for this project. A MacBook, retail broker API, and small account are not suitable for competing on short-lived FX arbitrage opportunities.

### Grid / martingale

Rejected. These approaches often hide risk until a trend or gap creates catastrophic drawdown.

### ML/GA optimized indicator systems

Research-only. Overfitting risk is high. ML/GA can later assist with parameter search, regime classification, or feature analysis, but not live decision-making until validation standards are much stronger.

### News prediction

Rejected for v0. News-driven trading requires latency, event data, and execution controls that are outside the first build.

## Parameter governance

Every strategy config must have:

- explicit parameter values
- allowed parameter ranges
- strategy version
- config hash
- training window
- test window
- out-of-sample window
- validation report link

No parameter change can go live without generating a new strategy version and validation report.

## Strategy promotion gates

A strategy can move from research to paper/demo only if:

- no lookahead bias detected
- no use of incomplete candles unless designed for it
- realistic bid/ask spread and slippage modeled
- transaction costs and financing considered
- out-of-sample performance not materially worse than in-sample
- parameter sensitivity is reasonable
- drawdown is within policy

A strategy can move from demo to live only if:

- demo execution matches expected behavior
- no reconciliation failures
- no unprotected trades
- no risk policy violations
- manual approval of exact config hash


--- FILE: 07_DATA_BACKTEST_VALIDATION.md ---
# Data, Backtesting, and Validation

## Data principles

1. Store raw broker data before transforming it.
2. Preserve request parameters for every historical data pull.
3. Never trade on a candle that is not marked complete unless the strategy explicitly supports intrabar logic.
4. Backtests must use the same instrument metadata, rounding, sizing, and risk checks as practice/live execution.
5. Fill assumptions must be conservative.

## Operational data store

Use SQLite in v0.

Minimum tables:

- `instruments`
- `candles`
- `price_snapshots`
- `spread_snapshots`
- `signals`
- `risk_decisions`
- `order_plans`
- `broker_orders`
- `fills`
- `transactions`
- `account_snapshots`
- `positions`
- `strategy_runs`
- `backtest_runs`
- `system_events`

## Candle schema

Store:

- instrument
- granularity
- time
- complete
- bid open/high/low/close nullable
- ask open/high/low/close nullable
- mid open/high/low/close nullable
- volume
- source
- request hash
- inserted_at

Use a unique key on `(instrument, granularity, time, price_component_set)` or a normalized equivalent.

## Backtest fill model

Do not fill at midpoint by default. Use:

- long entry at ask
- long exit at bid
- short entry at bid
- short exit at ask

Add slippage assumptions. For H1/H4 strategies, a simple conservative model is acceptable in v0:

```text
entry_slippage_pips = max(config.fixed_slippage_pips, spread_pips * config.spread_slippage_multiplier)
exit_slippage_pips = same or higher
```

The backtester should support later replacement with empirical slippage from practice data.

## Costs

Include:

- spread
- commission if applicable for account pricing model
- financing/rollover estimates where available
- price rounding
- unit rounding
- minimum trade size
- margin requirements

If exact financing is not available, flag the backtest as incomplete for any strategy that holds overnight.

## Bias checks

Required checks:

- No lookahead through current candle high/low/close before the candle is complete.
- No survivorship bias in instrument list changes.
- No using future spread averages to accept current trades.
- No parameter selection on test set.
- No deleting bad periods because they hurt results.
- No cherry-picking only successful pairs.

## Validation workflow

1. Research backtest on training period.
2. Freeze parameters.
3. Run out-of-sample test.
4. Run walk-forward or rolling-window test.
5. Run stress tests.
6. Run paper loop.
7. Run OANDA practice demo loop.
8. Compare backtest, paper, and practice execution.
9. Approve or reject live promotion.

## Suggested split

For each instrument/timeframe, use rolling splits instead of one static split. Example:

- Train: 24 months
- Validate: 6 months
- Test: 6 months
- Roll forward by 3 or 6 months

The exact windows can vary, but they must be defined before results are reviewed.

## Metrics

Report at minimum:

- total return
- CAGR if period length supports it
- max drawdown
- drawdown duration
- Sharpe and Sortino, with caveats
- profit factor
- expectancy per trade
- average R
- median R
- win rate
- average win/loss
- trade count
- exposure time
- turnover
- average spread paid
- estimated slippage
- largest single loss
- daily and weekly loss limit hits
- risk rejections
- correlation by currency exposure

## Minimum evidence gates

Do not promote a strategy only because it has high in-sample return. Require:

- enough trades to be meaningful for the timeframe
- out-of-sample expectancy not materially degraded
- max drawdown within policy
- no single pair dominates all results unless explicitly accepted
- parameter robustness around chosen values
- performance survives doubled transaction cost stress
- performance survives adverse slippage stress
- no hidden dependency on one market crisis period

## Backtest overfitting controls

Use these controls before trusting any result:

- fixed hypothesis before testing
- limited parameter grid
- train/validation/test separation
- walk-forward validation
- record every run, not only winners
- use deflated Sharpe or probability-of-backtest-overfitting concepts for heavily searched parameter spaces
- prefer simple strategies with fewer degrees of freedom

## Lean parity testing

If Lean is used, define parity tolerances:

- same instrument list
- same granularity
- same candle alignment
- same warmup period
- same fees/spread/slippage assumptions where possible
- same risk model or documented approximation
- same order timing convention

Differences must be documented in `src/forex_bot/lean/parity_notes.md`.

## Practice vs backtest reconciliation

Weekly report should compare:

- signals generated in backtest-like mode
- paper signals
- actual practice orders
- skipped signals and rejection reasons
- expected entry vs actual fill
- expected stop vs broker stop
- expected units vs actual units
- spread at signal time vs assumed spread
- transaction stream events vs local ledger


--- FILE: 08_REPO_SCAFFOLD_AND_TASKS.md ---
# Repo Scaffold and Implementation Tasks

## Recommended tooling

- Python 3.12+
- uv or pip-tools for dependency management
- pydantic for config/domain validation
- httpx for HTTP client
- pandas/numpy for indicators and research data frames
- sqlalchemy or sqlite-utils for persistence; raw sqlite is acceptable in v0
- duckdb and pyarrow optional for research exports
- typer for CLI
- rich for console output
- structlog or Python logging JSON formatter
- pytest for tests
- respx or responses for mocked HTTP tests
- ruff for linting
- mypy or pyright for type checking

## Initial commands

```bash
mkdir forex-bot
cd forex-bot
git init
uv init --package
uv add pydantic pydantic-settings httpx pandas numpy typer rich python-dotenv tenacity
uv add --dev pytest pytest-cov respx ruff mypy freezegun
mkdir -p configs src/forex_bot tests/unit tests/integration tests/fixtures docs scripts
```

Use equivalent pip/poetry commands if not using uv.

## Milestone 0: Safety skeleton

Tasks:

- Create project layout.
- Add `.gitignore` and `.env.example`.
- Add `Config` model with safety gates.
- Add CLI with `doctor` command.
- Add redacted logging.
- Add tests proving live mode refuses unsafe config.

Definition of done:

- `pytest` passes.
- `bot doctor --config configs/practice.yaml` works without credentials and reports missing env vars safely.
- No order-related code exists yet.

## Milestone 1: Domain models and storage

Tasks:

- Implement domain models.
- Implement SQLite connection and migrations.
- Implement repositories for instruments, candles, signals, risk decisions, order plans, transactions, account snapshots.
- Add config hash utility.

Definition of done:

- Domain model validation tests pass.
- Migrations are idempotent.
- Test fixtures can insert/read candles and decisions.

## Milestone 2: OANDA read-only adapter

Tasks:

- Implement authenticated HTTP client.
- Implement `get_account_summary`.
- Implement `list_instruments`.
- Implement `get_candles`.
- Implement `get_prices`.
- Implement retry/backoff for safe GET requests.
- Add mocked endpoint tests.

Definition of done:

- No order submission methods implemented or they raise `NotImplementedError`.
- Read-only smoke test can be run manually against practice when env vars exist.
- Instrument metadata is stored locally.

## Milestone 3: Indicators and first backtest

Tasks:

- Implement EMA, ATR, Donchian helpers.
- Implement trend-following strategy signal generation.
- Implement simple backtest engine using bid/ask aware fills.
- Add metrics.
- Add `bot backtest`.

Definition of done:

- Backtest uses only completed candles.
- Backtest saves run config hash and trade list.
- Unit tests catch lookahead mistakes in Donchian breakout.

## Milestone 4: Risk engine

Tasks:

- Implement position sizing.
- Implement spread filters.
- Implement daily/weekly loss checks.
- Implement exposure checks.
- Implement kill switch.
- Implement risk decision persistence.

Definition of done:

- Given a signal, risk engine returns approved/rejected with reason codes.
- Position sizing tests include EUR_USD, JPY pair, and non-USD quote conversion cases.
- All rejected trades are stored.

## Milestone 5: Paper loop

Tasks:

- Implement loop that fetches latest complete candles.
- Generate signals.
- Run risk checks.
- Save paper order plans.
- No broker order submission.

Definition of done:

- Running paper loop cannot submit orders even if credentials exist.
- Weekly report includes would-have-traded events.

## Milestone 6: Practice execution

Tasks:

- Implement OANDA order submission for practice only.
- Use idempotent client IDs.
- Attach stop-loss-on-fill.
- Save broker response.
- Implement transaction catch-up.
- Implement reconciliation after order submit.

Definition of done:

- Practice execution requires `allow_order_submission: true` and `environment: practice`.
- Live environment still blocked.
- Unknown order status blocks further orders until reconciliation.

## Milestone 7: Reporting

Tasks:

- Implement `bot report weekly`.
- Include P/L, risk decisions, execution quality, slippage, spread, strategy attribution, reconciliation issues.
- Export Markdown and HTML.

Definition of done:

- Report can be generated from SQLite only.
- No secrets appear in report.

## Milestone 8: Lean parity harness

Tasks:

- Add Lean project directory or instructions.
- Implement trend-following strategy in Lean or document why deferred.
- Compare selected backtest window with native engine.

Definition of done:

- Differences are documented.
- No Lean requirement to run core OANDA bot.

## Milestone 9: Live readiness but not live by default

Tasks:

- Add live config template only.
- Add live safety prompts/acknowledgement.
- Add launchd templates.
- Add incident runbooks.

Definition of done:

- Tests prove live mode is impossible without all gates.
- Manual checklist exists.
- No real live secrets in repo.

## Issue backlog labels

- `safety`
- `broker-oanda`
- `risk`
- `strategy`
- `backtest`
- `data`
- `reconciliation`
- `reporting`
- `lean`
- `ops`
- `docs`

## First 10 tickets

1. Scaffold project with config, CLI, logging, and test setup.
2. Implement safe config gates and live-mode refusal tests.
3. Implement SQLite migrations and repositories.
4. Implement OANDA read-only account summary and instrument sync.
5. Implement candle fetch and storage with complete flag.
6. Implement indicators and trend-following signal generation.
7. Implement backtest engine with bid/ask fill model.
8. Implement risk sizing and spread filters.
9. Implement paper loop and report of would-have-traded signals.
10. Implement practice order submission with stop-loss-on-fill and reconciliation.


--- FILE: 09_AI_BUILD_PROMPT.md ---
# AI Build Prompt for Codex or Claude

Copy this prompt into Codex or Claude when starting the repo.

```text
You are building a production-minded but demo-first forex research and execution bot. This is engineering research, not financial advice. The repo must default to safety and must not place live trades unless all explicit live gates are enabled.

Use the docs in this founders pack as binding requirements:

- 01_DECISION_MEMO.md
- 02_PRD.md
- 03_ARCHITECTURE.md
- 04_OANDA_ADAPTER_SPEC.md
- 05_RISK_POLICY.md
- 06_STRATEGY_SPEC.md
- 07_DATA_BACKTEST_VALIDATION.md
- 08_REPO_SCAFFOLD_AND_TASKS.md
- 10_RUNBOOKS.md
- 11_CONFIG_EXAMPLES.md
- 12_ACCEPTANCE_CRITERIA.md

Build the repository from scratch in Python 3.12+.

Core rules:

1. No LLM or AI component in the live trading decision path.
2. Strategies emit Signal objects only.
3. The risk engine is the only component allowed to approve an order plan.
4. The broker adapter may submit only approved order plans.
5. OANDA practice mode comes before live mode.
6. Live mode must be impossible unless environment is live, allow_order_submission is true, allow_live_trading is true, and the live acknowledgement phrase exactly matches config.
7. No secrets in code, logs, tests, docs, or fixtures.
8. Every order attempt must be auditable from signal to risk decision to order plan to broker response to transaction reconciliation.
9. Implement tests before or alongside code. Safety tests are mandatory.
10. Prefer simple, readable code with explicit types over clever abstractions.

Initial implementation target:

- Project scaffold with pyproject.toml.
- Typer CLI.
- Pydantic config.
- JSON logging with secret redaction.
- SQLite ledger with idempotent migrations.
- Domain models.
- OANDA read-only adapter: account summary, instruments, candles, prices.
- Trend-following strategy signal generator.
- Risk engine: sizing, spread filter, daily/weekly loss checks, max position checks, kill switch.
- Backtest engine with bid/ask-aware fill model.
- Paper loop that cannot submit broker orders.
- Practice execution only after explicit flag, with stop-loss-on-fill and reconciliation.
- Weekly report.

Do not implement live trading until all acceptance criteria pass. You may include a live config template, but it must be inert and safe.

Use official OANDA docs as source of truth for endpoint details. Do not trust sample repos as production code. Use mocked HTTP tests for OANDA responses. Add practice-account smoke tests behind explicit environment variables but skip them by default in CI.

After each milestone:

- Run tests.
- Update README.
- Update docs if behavior differs.
- Summarize safety implications.

Start with Milestone 0 from 08_REPO_SCAFFOLD_AND_TASKS.md. Show the file tree and then implement the minimal safe skeleton.
```

## Review prompt for changes

```text
Review this change as if it could cause real broker orders. Focus on:

- Can this bypass risk checks?
- Can this submit live orders accidentally?
- Can this duplicate orders on retry?
- Can this trade on stale, incomplete, or misaligned data?
- Can this hide reconciliation mismatches?
- Can secrets leak through logs, reports, errors, or tests?
- Are backtest assumptions different from practice/live assumptions?
- Are there new parameters that encourage overfitting?

Return blockers, non-blocking concerns, and required tests.
```

## Weekly strategy review prompt

```text
Analyze the attached weekly bot report. Do not propose live changes first. Identify:

- rule violations
- risk rejections
- reconciliation issues
- spread/slippage anomalies
- strategy performance by instrument and session
- difference between backtest assumptions and practice execution
- signs of overfitting or parameter chasing
- one conservative experiment for paper/demo only

Any proposed change must include a hypothesis, expected effect, affected config hash, validation plan, rollback plan, and promotion gate.
```


--- FILE: 10_RUNBOOKS.md ---
# Runbooks

## Local setup

1. Install Python 3.12+.
2. Install uv or chosen package manager.
3. Clone repo.
4. Copy `.env.example` to `.env` locally; never commit `.env`.
5. Create OANDA practice account and token.
6. Set practice env vars.
7. Run `bot doctor`.
8. Run `bot sync-instruments`.
9. Run `bot fetch-candles`.
10. Run `bot backtest`.
11. Run `bot paper-loop`.
12. Only then consider `bot demo-loop` with OANDA practice order submission.

## Daily operator checklist

- Confirm bot process is running only in intended mode.
- Check latest account snapshot.
- Check reconciliation status.
- Check open positions and protective stops.
- Check daily loss usage.
- Check spread/rejection anomalies.
- Check logs for auth, HTTP, or broker errors.

## Weekly operator checklist

- Generate weekly report.
- Review all closed trades.
- Review rejected trades.
- Compare paper signals vs practice orders.
- Review spread/slippage by pair and session.
- Review any reconciliation mismatches.
- Review all config changes.
- Archive report with config hash.

## Incident: kill switch

Trigger if:

- unexpected order appears
- unprotected position exists
- broker/local reconciliation mismatch persists
- token leak suspected
- repeated order rejects
- runaway loop or duplicate order attempt
- daily/weekly loss breached unexpectedly

Steps:

1. Create `KILL_SWITCH` file in repo root or set config `trading_enabled: false`.
2. Confirm bot logs show `trading_blocked`.
3. Manually inspect OANDA account in broker UI.
4. Cancel unexpected pending orders manually if needed.
5. Close positions manually if risk requires it.
6. Rotate token if a leak is possible.
7. Do not restart order submission until root cause is documented.

## Incident: unknown order status

Cause examples:

- timeout after submit
- broker returns partial response
- network disconnect
- process crash after submit before local write

Steps:

1. Block new orders.
2. Fetch account details.
3. Fetch open orders, trades, positions.
4. Fetch transactions since last known transaction ID.
5. Search by client order ID.
6. Update local ledger.
7. If still unknown, leave trading blocked and inspect broker UI.

## Incident: transaction stream disconnect

Steps:

1. Reconnect with backoff.
2. Poll `transactions/sinceid` using last stored transaction ID.
3. Store missing transactions.
4. Reconcile account, open orders, trades, positions.
5. Resume only if clean.

## Incident: data gap

Steps:

1. Stop trading on affected instruments.
2. Backfill missing candles.
3. Verify no incomplete candle was treated as complete.
4. Recompute indicators for affected windows.
5. Document affected signals.

## Incident: spread spike

Steps:

1. Confirm spread filter rejected new trades.
2. Check if any open trades were stopped during spike.
3. Record spread distribution in report.
4. Consider widening blackout windows only after validation, not reactively.

## Token rotation

1. Stop bot.
2. Activate kill switch.
3. Revoke old OANDA token in account portal.
4. Generate new token.
5. Update local environment variable.
6. Run `bot doctor`.
7. Run read-only account summary.
8. Remove kill switch only after confirming no secrets were committed.

## macOS launchd deployment

Do not set up launchd until demo mode is stable.

Required before launchd:

- absolute path to venv/uv command
- absolute path to config
- working directory set
- log directory exists
- env vars loaded securely
- kill switch path known
- restart policy conservative

The launchd job should start in paper or practice mode, never live by default.

## Rollback plan

Every deploy should have:

- git commit hash
- config hash
- migration version
- rollback command
- previous known-good config
- manual broker inspection checklist

Rollback steps:

1. Activate kill switch.
2. Stop process.
3. Inspect broker state.
4. Checkout previous git commit.
5. Restore previous config.
6. Run migrations only if reversible or compatible.
7. Start in read-only doctor/reconcile mode.
8. Resume paper/practice only after clean reconciliation.


--- FILE: 11_CONFIG_EXAMPLES.md ---
# Configuration Examples

## `.env.example`

```bash
OANDA_ENVIRONMENT=practice
OANDA_ACCOUNT_ID_PRACTICE=replace_me
OANDA_ACCESS_TOKEN_PRACTICE=replace_me
OANDA_ACCOUNT_ID_LIVE=replace_me_only_when_ready
OANDA_ACCESS_TOKEN_LIVE=replace_me_only_when_ready
```

## `configs/paper.yaml`

```yaml
app:
  name: oanda-forex-research-bot
  mode: paper
  trading_enabled: false
  allow_order_submission: false
  allow_live_trading: false
  database_path: ./data/bot.sqlite3
  log_path: ./logs/bot.jsonl
  kill_switch_path: ./KILL_SWITCH

broker:
  name: oanda
  environment: practice
  account_id_env: OANDA_ACCOUNT_ID_PRACTICE
  token_env: OANDA_ACCESS_TOKEN_PRACTICE
  request_timeout_seconds: 10
  max_retries: 3

market:
  account_currency: USD
  instruments:
    - EUR_USD
    - USD_JPY
    - GBP_USD
    - AUD_USD
    - USD_CAD
  granularity: H4
  candle_price_components: BA
  daily_alignment: 17
  alignment_timezone: America/New_York
  weekly_alignment: Friday

strategy:
  enabled:
    - trend_following
  trend_following:
    version: 0.1.0
    timeframe: H4
    ema_fast: 50
    ema_slow: 200
    donchian_lookback: 20
    atr_lookback: 14
    atr_stop_multiple: 2.5
    max_bars_in_trade: 80

risk:
  starting_equity_usd: 500
  risk_per_trade_pct: 0.25
  max_risk_per_trade_pct: 0.50
  max_daily_loss_pct: 1.00
  max_weekly_loss_pct: 2.00
  max_total_drawdown_pct: 8.00
  max_open_positions: 1
  max_pending_orders: 1
  max_correlated_positions: 1
  require_stop_loss: true
  require_server_side_protection: true
  allow_martingale: false
  allow_grid: false
  allow_averaging_down: false

spread_filter:
  enabled: true
  max_spread_to_atr_pct: 8.0
  max_spread_pips:
    EUR_USD: 1.5
    USD_JPY: 2.0
    GBP_USD: 2.5
    AUD_USD: 2.0
    USD_CAD: 2.5

session_filter:
  enabled: true
  timezone: America/New_York
  block_new_trades:
    - name: rollover
      start: "16:45"
      end: "17:15"
    - name: friday_close
      day: Friday
      start: "15:00"
      end: "23:59"
    - name: sunday_open
      day: Sunday
      start: "00:00"
      end: "19:00"
```

## `configs/practice.yaml`

```yaml
app:
  name: oanda-forex-research-bot
  mode: practice
  trading_enabled: true
  allow_order_submission: true
  allow_live_trading: false
  database_path: ./data/bot.sqlite3
  log_path: ./logs/bot.jsonl
  kill_switch_path: ./KILL_SWITCH

broker:
  name: oanda
  environment: practice
  account_id_env: OANDA_ACCOUNT_ID_PRACTICE
  token_env: OANDA_ACCESS_TOKEN_PRACTICE
  request_timeout_seconds: 10
  max_retries: 3

# Inherit or duplicate market, strategy, risk, spread_filter, session_filter from paper config.
```

## `configs/live.example.yaml`

This is intentionally inert. Do not rename to `live.yaml` until all acceptance criteria pass.

```yaml
app:
  name: oanda-forex-research-bot
  mode: live
  trading_enabled: false
  allow_order_submission: false
  allow_live_trading: false
  live_acknowledgement: "NOT_APPROVED"
  required_live_acknowledgement: "I_ACCEPT_THE_RISK_AND_APPROVE_THIS_EXACT_CONFIG_HASH"
  approved_config_hash: "replace_with_manual_approval_hash"
  database_path: ./data/live-bot.sqlite3
  log_path: ./logs/live-bot.jsonl
  kill_switch_path: ./KILL_SWITCH

broker:
  name: oanda
  environment: live
  account_id_env: OANDA_ACCOUNT_ID_LIVE
  token_env: OANDA_ACCESS_TOKEN_LIVE
  request_timeout_seconds: 10
  max_retries: 3

risk:
  risk_per_trade_pct: 0.25
  max_risk_per_trade_pct: 0.50
  max_daily_loss_pct: 1.00
  max_weekly_loss_pct: 2.00
  max_open_positions: 1
  require_stop_loss: true
  require_server_side_protection: true
  allow_martingale: false
  allow_grid: false
  allow_averaging_down: false
```

## Config validation rules

The app must reject:

- `environment: live` with practice account env vars
- `mode: live` without `allow_live_trading: true`
- `allow_live_trading: true` without exact acknowledgement phrase
- `allow_order_submission: true` with `trading_enabled: false`
- `risk_per_trade_pct > max_risk_per_trade_pct`
- `require_stop_loss: false`
- `allow_martingale: true`
- `allow_grid: true`
- `allow_averaging_down: true`
- empty instrument whitelist
- missing spread filter for enabled instrument
- missing or invalid kill switch path


--- FILE: 12_ACCEPTANCE_CRITERIA.md ---
# Acceptance Criteria

## Safety acceptance criteria

- Tests prove live mode cannot start with default config.
- Tests prove order submission cannot occur in paper mode.
- Tests prove order submission cannot occur when kill switch file exists.
- Tests prove no strategy can call broker adapter directly.
- Tests prove risk rejection prevents order plan creation or execution.
- Tests prove duplicate client order ID cannot submit twice without reconciliation.
- Tests prove missing stop loss rejects a new position order.
- Tests prove stale price or missing spread rejects a trade.
- Tests prove incomplete candles are not used by default.

## OANDA adapter acceptance criteria

- Can fetch account summary in practice mode.
- Can fetch and store instrument metadata.
- Can fetch candles with complete flags.
- Can fetch current prices and compute spread.
- Can parse transaction stream events or mocked stream events.
- Can backfill transactions since last transaction ID.
- Can submit a practice market order with stop-loss-on-fill only when all gates pass.
- Can reconcile local ledger with OANDA open orders/trades/positions after order submission.

## Risk acceptance criteria

- Correct sizing for EUR_USD with USD account.
- Correct sizing for JPY pairs using pip location.
- Correct handling of non-USD quote conversion or rejection if conversion unavailable.
- Unit rounding uses trade units precision.
- Minimum trade size enforced.
- Margin buffer enforced.
- Max open position enforced.
- Daily and weekly loss limits enforced.
- Spread/ATR filter enforced.

## Backtest acceptance criteria

- Uses completed candles only.
- Uses bid/ask-aware fill model.
- Includes spread and slippage assumptions.
- Stores config hash and data request hash.
- Produces trade list and metrics.
- Prevents lookahead in Donchian breakout by using prior bars.
- Records all tested parameter sets, not only winners.

## Reporting acceptance criteria

Weekly report includes:

- account NAV and P/L
- realized and unrealized drawdown
- closed trades
- open trades
- win rate
- expectancy
- average R
- profit factor
- strategy contribution
- pair/session contribution
- average spread paid
- estimated slippage
- risk rejections
- reconciliation mismatches
- rule violations
- config hash
- code commit hash

## Demo-to-live promotion gates

Live mode is not allowed until all are true:

1. All unit and integration tests pass.
2. At least 30 calendar days of practice operation with no unresolved reconciliation mismatch.
3. At least one full weekly report reviewed manually.
4. No unprotected practice trades.
5. No duplicate practice orders.
6. No risk policy violations.
7. Backtest and practice differences explained.
8. Live config hash approved manually.
9. Separate live OANDA token configured outside repo.
10. Rollback and kill-switch runbook tested.

## Definition of done for v0

The repo is v0-complete when it can run from fresh clone through:

```bash
bot doctor --config configs/paper.yaml
bot sync-instruments --config configs/paper.yaml
bot fetch-candles --config configs/paper.yaml --instrument EUR_USD --granularity H4
bot backtest --config configs/paper.yaml
bot paper-loop --config configs/paper.yaml --once
bot report weekly --config configs/paper.yaml
```

And, with explicit practice credentials and order flag:

```bash
bot demo-loop --config configs/practice.yaml --once
bot reconcile --config configs/practice.yaml
```

No live command should work from default files.


--- FILE: 13_SOURCES.md ---
# Sources and Evidence Notes

Date checked: 2026-05-21

## Official broker/platform docs

- OANDA v20 REST API introduction: https://developer.oanda.com/rest-live-v20/introduction/
- OANDA pricing and candles endpoints: https://developer.oanda.com/rest-live-v20/pricing-ep/
- OANDA order endpoints: https://developer.oanda.com/rest-live-v20/order-ep/
- OANDA transaction endpoints: https://developer.oanda.com/rest-live-v20/transaction-ep/
- OANDA account and instrument endpoints: https://developer.oanda.com/rest-live-v20/account-ep/
- OANDA instrument definitions: https://developer.oanda.com/rest-live-v20/instrument-df/
- OANDA Python samples: https://github.com/oanda/v20-python-samples
- QuantConnect Lean CLI docs: https://www.quantconnect.com/docs/v2/lean-cli
- QuantConnect Lean OANDA brokerage docs: https://www.quantconnect.com/docs/v2/lean-cli/live-trading/brokerages/cfd-and-forex-brokerages
- QuantConnect Lean OANDA brokerage plugin: https://github.com/QuantConnect/Lean.Brokerages.OANDA
- FOREX.com API trading page: https://www.forex.com/en/trading-tools/api-trading/
- MetaTrader5 Python package on PyPI: https://pypi.org/project/MetaTrader5/

## Risk and regulation

- CFTC forex fraud advisory: https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/fraudadv_forex.html
- CFTC forex customer advisory: https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_MustKnowForex.html
- eCFR 17 CFR 4.41, simulated or hypothetical performance limitations: https://www.ecfr.gov/current/title-17/chapter-I/part-4/subpart-D/section-4.41
- OANDA US margin rates and leverage ratios: https://www.oanda.com/us-en/legal/margin-rates/

## Strategy/research background

- Moskowitz, Ooi, Pedersen, Time Series Momentum: https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum
- Hurst, Ooi, Pedersen, A Century of Evidence on Trend-Following Investing: https://research.cbs.dk/en/publications/a-century-of-evidence-on-trend-following-investing/
- Brunnermeier, Nagel, Pedersen, Carry Trades and Currency Crashes: https://www.nber.org/papers/w14473
- Bailey, Borwein, Lopez de Prado, Zhu, The Probability of Backtest Overfitting: https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- Bailey and Lopez de Prado, The Deflated Sharpe Ratio: https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf

## How to interpret this evidence

The sources justify engineering feasibility and broad strategy-family research, not an expected profit. OANDA/Lean docs show that the platform path is plausible. Trend-following research supports a candidate hypothesis. CFTC/eCFR materials warn that forex and hypothetical backtests have substantial limitations. The repo must treat backtests as fragile evidence and practice trading as an execution-quality test, not as proof of future profitability.
