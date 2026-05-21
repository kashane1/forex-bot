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
