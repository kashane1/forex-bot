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
