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
