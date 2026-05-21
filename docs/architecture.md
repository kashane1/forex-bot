# Architecture

This document is the operational summary. The binding spec is
[`forex_bot_founders_pack/03_ARCHITECTURE.md`](../forex_bot_founders_pack/03_ARCHITECTURE.md).

## Layers

| Layer | Module | Responsibilities | NOT allowed |
|-------|--------|------------------|-------------|
| Config | `config.py` | Pydantic validation, live-mode gates, env credential lookup | Read broker, write ledger |
| Domain | `domain/` | Frozen Pydantic models, no I/O | Network or DB calls |
| Broker | `broker/` | OANDA v20 REST, error taxonomy, JSON↔domain mapping | Sizing, strategy logic |
| Data | `data/` | SQLite ledger, repositories, migrations | Broker calls, sizing |
| Strategies | `strategies/` | Pure indicators + signal generation | Credentials, broker calls, sizing |
| Risk | `risk/` | Sizing, policy, kill switch, exposure, session blackout | Broker calls |
| Execution | `execution/` | Plan → submit → reconcile, the ONLY broker.submit_order() caller | Strategy decisions |
| Backtest | `backtesting/` | Bar replay, bid/ask fills, metrics | Live calls, real money |
| Reporting | `reporting/` | Weekly report from SQLite only | Broker calls |
| CLI | `cli.py`, `loops.py` | Glue, ops commands | Strategy logic |

## Flow per iteration of the paper / practice loop

1. `fetch_latest_candles` — pull and persist candles per instrument.
2. `broker.get_prices` — current bid/ask, persist as spread snapshots.
3. `broker.get_account_summary` — record an account snapshot.
4. `broker.list_positions` — current state used by the risk engine.
5. For each instrument × enabled strategy:
   1. `strategy.generate_signal(ctx)` — pure function, returns `Signal | None`.
   2. `planner.plan(inputs)` — persists signal, evaluates risk, persists decision and (if approved) order plan.
   3. Practice loop only: `executor.submit(plan)` — submits to OANDA practice, persists broker order + reconciles.

## Failure behavior — default is block

- Cannot load config → exit with non-zero code.
- Cannot fetch prices → block new orders for that loop.
- Spread too wide → reject signal, store the rejection.
- Missing instrument metadata → reject signal.
- Reconciliation mismatch → set `trading_blocked=True` on the Executor for the rest of the process.
- Unknown order status after submit → block + reconcile.
- Kill switch file present → reject every signal.

## Loop types

- **paper-loop**: `mode=paper`. Constructs a Planner without an
  Executor. It is *physically* impossible to submit orders.
- **demo-loop / practice loop**: `mode=practice`,
  `allow_order_submission=true`. Submits to OANDA practice only.
- **live loop**: not implemented in v0 by intent. The `live.example.yaml`
  template cannot start the bot.
