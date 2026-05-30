# Non-USD Cross Cost-Model Design

**Sprint:** `research-nonusd-cross-ingestion-and-cost-models-001` (Phase 4)
**Status:** infrastructure only — diagnostic cost models for a *future*
front gate. No strategy, no campaign, no approval. Cost figures are
ESTIMATES pending real ingested data.

## Why the majors' cost code must not be copied

`forex_bot.financing` (the majors' conservative stress overlay) hides one
assumption: **one leg is USD**. For a cross neither leg is USD, so reusing
it is wrong on three counts:

1. `notional_usd(units, price) = units × price` is in the **quote
   currency** for a cross (e.g. JPY for EUR_JPY), not USD.
2. `risk_usd` similarly assumes the quote currency is USD.
3. A single per-pair bp/day copied from a major ignores that a cross's
   carry is genuinely **two-legged** (base-leg rate − quote-leg rate).

The fallback for unlisted pairs in `financing.py` is the table-max
(1.2 bp/day) — "conservative" but not meaningful for, say, EUR_GBP (two
low-rate legs) vs AUD_JPY (a real carry cross).

## The new package — `forex_bot.research.cost_models`

Three small, tested modules. None imports the majors' assumptions.

### `spread.py` — `CrossSpreadCostModel` + `SpreadStats`

- Spread cost is sourced from the registry's qualitative `est_spread_pips`
  band by default (`source = "registry_estimate"`), or from measured
  `SpreadStats.from_bid_ask(...)` once real bid/ask data exists
  (`source = "measured"`).
- All cost is expressed in **pips using the cross's own pip size**
  (`spread_price` = pips × pip_size), so JPY crosses (0.01) and non-JPY
  crosses (0.0001) are handled correctly with no USD assumption.
- `spread_cost_r(risk_pips, round_trip=True)` returns spread as a fraction
  of risk — round-trip charges both entry and exit. Quote currency
  cancels.

### `carry.py` — `CrossCarryModel`

- Conservative **two-legged** carry stress using the registry's
  **explicit per-cross** `conservative_bp_per_day` (never the majors'
  fallback). `carry_legs` exposes the (long, short) currency pair whose
  differential is the carry.
- `debit_quote(...)` returns the debit in the **quote currency** — honest
  about denomination; converting to USD needs a separate quote/USD rate,
  which the model refuses to fabricate.
- `debit_r(...)` returns the debit as a fraction of risk. Because both the
  debit and the risk are in the quote currency, **the quote currency
  cancels exactly** — so the R figure is correct with **no USD rate**.
  This is the front-gate-ready number.
- Always `>= 0` (a stress cost, never a credit); `treatment = ESTIMATED`;
  `metadata()` declares `financing_in_engine_pnl = False` and
  `financing_is_live_blocker = True`. It can never lift the live blocker —
  OANDA exposes no historical cross financing series.

### `profile.py` — `cross_cost_profile(instrument)`

Bundles spread + carry + structural-break flags into one compact
`diagnostic_only` / `strategy_evidence: False` dict that a future
front-gate cost-realism screen can consume directly.

## Front-gate cost realism (future use, not run here)

A future cross front-gate screen will combine, per candidate:

```
net_edge_R  ≈  gross_edge_R
             − spread.spread_cost_r(risk_pips, round_trip=True)
             − carry.debit_r(units, entry, stop, bars_held)
```

with spread sourced from **measured** `SpreadStats` once cross data is
ingested. The viability review's standing conclusion holds: crosses are
**wider** than the majors, so this cost term is *expected* to be larger,
not smaller — crosses are a breadth/replication expansion, not a cost fix.

## Tests

`tests/unit/test_cross_cost_models.py` (14 tests) covers: registry-band vs
measured spread, pip-size-correct spread price for JPY and non-JPY crosses,
round-trip vs one-way R, measured-overrides-estimate, explicit-bp (not
fallback), debit non-negativity + time-scaling, **quote-currency
independence of `debit_r`**, zero-risk degeneracy, honest metadata, and
non-cross rejection across all three models.
