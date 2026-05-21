# Lean integration boundary

Per the founders pack
([`01_DECISION_MEMO.md`](../../../forex_bot_founders_pack/01_DECISION_MEMO.md))
the v0 build uses **native Python OANDA as the canonical runtime**.
QuantConnect Lean is intentionally kept out of the live order path.

Allowed uses of Lean:

- **Independent backtest benchmark**: implement `trend_following` in Lean,
  run on the same instrument + timeframe + window, and compare the
  trade list and equity curve against `src/forex_bot/backtesting/`.
- **Research notebooks**: parameter sweeps and regime analysis on
  historical OANDA data.

Forbidden in v0:

- Lean as the live execution engine.
- Strategies that exist only in Lean. Every strategy that can ever go
  live must have a Python implementation tested by
  `tests/unit/test_strategies.py` AND a risk engine that approves its
  orders.

## When you do build the Lean version

Document every divergence in `parity_notes.md`:

- fill model
- quote source (mid vs bid/ask)
- spread model
- rollover / financing treatment
- order timing convention
- warmup period
- fees and commissions

Lean's CLI / OANDA brokerage plugin requires QuantConnect organization
membership at a paid tier as of the writing of the founders pack —
factor that into the decision before depending on Lean for any
operational path.
