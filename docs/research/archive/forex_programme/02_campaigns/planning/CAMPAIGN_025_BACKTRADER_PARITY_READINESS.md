# CAMPAIGN_025 — Backtrader parity readiness

**Recommendation: `DEFER_PARITY_REJECTED`.** Do not build Backtrader parity for
C025 in this or a near-term sprint.

---

## Do train/validation results justify parity work?

**No.** Parity is a precommitted gate that matters only *before promoting a
candidate that already passed train + validation*. The C025 train matrix is
`REJECT_MATRIX_NO_TRAIN_CANDIDATE` (0/16 eligible, all net-negative, none beats the
C011 null), and validation was therefore not run. There is **nothing to promote**,
so spending effort proving engine parity would be premature.

## Expected effort (if it were ever justified)

Moderate–high. A faithful Backtrader port would need: M5 data feed per pair,
last-completed H1/H4M1/D1AGG context (precomputed-aligned-columns approach
recommended in `CAMPAIGN_025_BACKTRADER_PARITY_DESIGN.md`), `next_bar_open` via
`cheat_on_open=off`, all five exit models, and the adverse-first same-bar policy.

## Known alignment risks (carried from the parity design)

- **M5 resampling alignment** vs the materialized M1-derived bar edges (esp. the
  17:00 NY boundary).
- **HTF context** must use the last completed bar only (no lookahead) — must match
  this sprint's `merge_asof(direction="backward")` semantics exactly.
- **`next_bar_open` modeling** — orders must fill at the next bar open, not the
  signal bar.
- **Donchian prior-bar behaviour** — channel must exclude the current bar
  (`.shift(1)` / `Highest(...)[-1]`); a one-bar offset silently changes everything.
- **Target/stop same-bar ambiguity** — must reproduce adverse-first.
- **Breakeven / trailing** — intrabar activation thresholds (+1.0R / +1.5R) and
  completed-bar trailing.
- **Channel-exit** — completed-close cross of the prior channel, fill next open.

## This sprint's simulator vs a future parity build

The C025 train-matrix simulator (`src/forex_bot/research/campaign_025_train_matrix.py`)
is an **isolated research engine**, not the shared `forex_bot.backtesting` engine.
If C025 (or any descendant) were ever revived, the parity exercise would be a
three-way check: research simulator ↔ shared engine ↔ Backtrader. None of that is
warranted now.

## Decision

`DEFER_PARITY_REJECTED` — revisit only if a future, materially different idea
clears a train-matrix selection **and** a champion validation. The binding blocker
is not engine fidelity; it is the negative cost-adjusted edge (spread/ATR ≈ 0.5 on
M5).
