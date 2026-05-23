# Free / Local Parity Verifier — Sprint-004 Rounding Fixes

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-004-rounding-closure`
**Phase:** 3 · `strategy_evidence: false`

Verifier-side rounding/precision fixes applied per the
[`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md)
M1/M2 plan. Before/after numbers + interpretation.

> No bespoke-engine edits. No CAMPAIGN_002 rule changes. No
> parameter tuning. No strategy approval. CAMPAIGN_002 remains
> REJECT.

## Changes applied

| change | file | rationale |
|---|---|---|
| Add `display_precision: int` to `InstrumentSpec` | `research/parity_verifier/models.py` | Audit M2 prerequisite |
| Populate `display_precision = 5` (USD-quote majors) / `3` (USD_JPY) | `research/parity_verifier/instruments.py` | Match bespoke per-pair values from `data/campaign_002.sqlite3` |
| New `round_price(price, display_precision)` helper | `research/parity_verifier/rules.py` | Decimal-based, ROUND_HALF_UP, identical formula to `forex_bot.domain.instruments.Instrument.round_price` |
| Round the initial stop via `round_price(...)` after `initial_stop_price(...)` | `research/parity_verifier/event_loop.py` | Audit M1 — close the precision gap on the initial stop only |
| 6 new fixture tests for `round_price` | `tests/research/test_parity_verifier_rules.py` | Pin the rounding behavior and assert equality with the bespoke formula re-implemented inline (without importing forex_bot) |
| Updated `InstrumentSpec` metadata test to assert `display_precision` | `tests/research/test_parity_verifier_models.py` | Pin per-pair display precision (5 USD-quote, 3 USD_JPY) |

What was deliberately **not** changed:
- Trailing-stop rounding — bespoke also doesn't round trailing
  (`backtesting/engine.py:244, 250`), so no fix is needed.
- Entry / exit / time fill rounding — bespoke doesn't round these
  either; matches.
- Sized units — verifier's `int(raw)` already equals bespoke's
  `ROUND_DOWN` for positive `raw`.
- Float-vs-Decimal throughout — explicit audit M3 deferral; would
  re-implement the bespoke engine inside the verifier and
  sacrifice independence.

## Before / after — full-data comparison

Bespoke reference (no-RiskEngine): **1,647 trades** across 7 pairs,
no change.

### Totals

| metric | Sprint-003 post-debug | Sprint-004 post-round_price | Δ |
|---|---|---|---|
| Verifier total trades | 1,655 | **1,655** | 0 |
| Total Δ % vs bespoke | +0.49 % (OK) | **+0.49 % (OK)** | 0 |
| Overall comparison status | WARN | **WARN** | unchanged |
| Pairs OK / WARN / FAIL | 3 / 4 / 0 | **3 / 4 / 0** | unchanged |

### Per-pair (post fix)

| pair | bespoke trades | verifier trades | Δ % | Δ R | Δ pp | status |
|---|---|---|---|---|---|---|
| EUR_USD | 233 | 235 | +0.86 | +0.0160 | +0.7604 | WARN |
| GBP_USD | 215 | 215 | +0.00 | +0.0005 | +0.0141 | **OK** |
| USD_JPY | 247 | 251 | +1.62 | −0.0125 | +0.3069 | **OK** |
| AUD_USD | 237 | 238 | +0.42 | −0.0033 | −0.2232 | **OK** |
| USD_CAD | 251 | 251 | +0.00 | −0.0605 | +0.0000 | WARN |
| USD_CHF | 224 | 223 | −0.45 | +0.0428 | +1.6332 | WARN |
| NZD_USD | 240 | 242 | +0.83 | −0.0078 | −0.5096 | WARN |
| **total** | **1647** | **1655** | **+0.49** | | | **WARN** |

### Per-pair delta (Sprint-004 vs Sprint-003 numbers)

| pair | trades Δ | exp R Δ | return % Δ |
|---|---|---|---|
| EUR_USD | 235 → 235 (0) | −0.1801 → −0.1801 (0) | −10.0701 → −10.0741 (−0.0040) |
| GBP_USD | 215 → 215 (0) | −0.0966 → −0.0966 (0) | −5.1107 → −5.1041 (+0.0066) |
| USD_JPY | 251 → 251 (0) | −0.0126 → −0.0126 (0) | −1.0642 → −1.0666 (−0.0024) |
| AUD_USD | 238 → 238 (0) | −0.2167 → −0.2167 (0) | −12.1254 → −12.1245 (+0.0009) |
| USD_CAD | 251 → 251 (0) | −0.2409 → −0.2409 (0) | −14.1071 → −14.1096 (−0.0025) |
| USD_CHF | 223 → 223 (0) | −0.1002 → −0.1002 (0) | −5.4018 → −5.3990 (+0.0028) |
| NZD_USD | 242 → 242 (0) | −0.2722 → −0.2723 (−0.0001) | −15.2142 → −15.2128 (+0.0014) |

(Sprint-003 post-debug column is the run captured in
`FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md`. The minor expectancy
delta on NZD_USD is sub-rounding-unit and reflects the float→Decimal
conversion's residual.)

## Interpretation

The rounding fix is **correct** (verifier now matches bespoke's
documented `round_price` convention exactly, as proven by
`test_round_price_matches_bespoke_formula`) but its impact on the
comparison is **negligible**:

- Zero pair-level trade-count changes.
- Zero expectancy-R changes on 6 / 7 pairs (NZD_USD shifts by
  −0.0001 R — within rounding noise).
- Sub-0.01 pp return-% shifts on every pair.
- All pair statuses unchanged.

Why so small? ATR-based stops are many pips wide (typically 20–80
pips for these pairs). A fractional-pip rounding of the stop level
almost never flips a borderline `bid_low <= stop` or `ask_high >= stop`
comparison — H4 bars usually move by many pips between candles, so
the rounding is well inside the bar's intrabar range. The fix
matters for definitional correctness, not for outcome arithmetic.

## What remains (out of scope, per audit M3)

The persistent WARN-band drift on 4 / 7 pairs (largest: USD_CHF
return +1.63 pp) is most plausibly **float-vs-Decimal arithmetic
accumulating across thousands of indicator-evaluation and
trade-by-trade compounding steps**, not initial-stop rounding.
Converting the verifier to Decimal end-to-end would re-implement the
bespoke engine inside the verifier and sacrifice the independence
that gives the comparison its value. **Phase 4 will classify the
remaining drift precisely and either accept it as inherent float
precision noise or punt to a future, opt-in, Decimal-precision
sprint.**

## What this proves

- The verifier and the bespoke engine now share an identical
  `round_price` convention for initial stops.
- The remaining WARN drift is **not** caused by stop-price rounding
  — that variable has been controlled.
- The directional verdict still holds: every CAMPAIGN_002 H4 pair
  is loss-making on the no-RiskEngine path under both engines.
- CAMPAIGN_002 remains REJECT under either measurement.

## What this does NOT prove

- It does not prove the bespoke engine is exactly correct — the
  remaining sub-WARN drift on 4 / 7 pairs is unresolved.
- It does not approve any strategy.
- It does not enable any paper / demo / live loop.

## Files changed

- `research/parity_verifier/models.py` (+`display_precision` field)
- `research/parity_verifier/instruments.py` (per-pair
  display_precision values)
- `research/parity_verifier/rules.py` (+`round_price` helper)
- `research/parity_verifier/event_loop.py` (wire `round_price` into
  initial-stop computation)
- `tests/research/test_parity_verifier_rules.py` (+6 round_price
  tests)
- `tests/research/test_parity_verifier_models.py` (+ assert
  display_precision per pair)

Bespoke engine, CAMPAIGN_002 rules, strategy modules, campaign
configs, campaign reports, approved_strategies.yaml: **all
unchanged**.
