# CAMPAIGN_011 — Financing Overlay (ESTIMATED + Conservative Stress)

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

Phase 6 financing overlay for the CAMPAIGN_011 walk-forward
evidence. Applies the existing
[`research/financing/`](../../research/financing) calculator
with the default conservative-stress rate source (debit-only on
both long and short) to every committed CAMPAIGN_011 trade.
**This is an off-engine overlay; engine PnL is unchanged.
MODELED financing remains refused at four layers.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. The
> four-layer `MODELED`-refusal in `src/forex_bot/financing.py`
> plus the research-side calculator stands untouched.
> **CAMPAIGN_011 is a null model — cannot be approved by design.**

## 1. Financing source and treatment ladder

| dimension | value |
|---|---|
| source name | `conservative_stress` (`research.financing.default_stress_rate_source()`) |
| treatment | **`ESTIMATED`** |
| MODELED reachable here? | **no** — `TableRateSource(treatment=MODELED)` raises at construction; `calculate_run(source)` raises if `source.treatment == MODELED`; the campaign runner does not configure or pass any MODELED source. |
| OBSERVED treatment exercised? | **no** — no observed-rate fixture or capture is consumed by this overlay; the calculator falls back to `default_stress_rate_source()` which is debit-only on both sides per pair. |
| `default_stress_rate_source()` rates | per-pair pessimistic annual bp (see [`research/financing/rates.py`](../../research/financing/rates.py) `CONSERVATIVE_BP_PER_DAY`); applied identically to long and short so the net cashflow is debit only. |
| engine-PnL modification? | **no** — `BacktestEngine` is unchanged; financing is added *on top of* the committed engine results. |
| live-promotion blocker status | **`financing_is_live_blocker = true`** — unchanged (structurally moot for the null-model candidate, which cannot be promoted regardless). |

## 2. Commands

```bash
# Phase 6 — financing overlay (no broker call, no credential).
.venv/bin/python scripts/build_campaign_011_financing_overlay.py \
    --campaign-dir backtests/CAMPAIGN_011_random_entry_anchor/
```

The script reads every
`backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_<PAIR>_trades.csv`,
constructs a `PositionInterval` per trade (units, side, entry
price, open / close times — all from the engine's output, all
tz-aware), and calls `research.financing.calculate_run(...,
default_stress_rate_source())`. Outputs:

- [`backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.json)
  — the canonical `FinancingRunReport` JSON (sorted keys,
  ISO-8601 dates).
- [`backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md`](../../backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md)
  — the deterministic markdown rendering.
- [`backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json)
  — extended per-pair / per-side / per-fold breakdown the
  Phase 5 verdict cross-references.

## 3. Headline numbers (verbatim from `FinancingRunReport`)

| field | value |
|---|---|
| `event_count` (per-day rollovers across all trades, weekend skip + Wednesday triple) | **1,080** |
| `cashflow_home_total` (USD, sum across all events) | **−$24.38** |
| `cashflow_home_stress_total` (USD; identical here because the conservative source is debit-only) | **−$24.38** |
| `missing_rate_event_count` | **0** (the conservative stress source is defined for every pair) |
| `financing_treatment` | `ESTIMATED` |
| `financing_in_engine_pnl` | `false` |
| `financing_is_live_blocker` | `true` |

The events:trades ratio = 1,080 / 1,177 ≈ **0.92** — slightly
higher than CAMPAIGN_010's 0.89 because random entry is uniformly
distributed across UTC hours (CAMPAIGN_010 was London-window
concentrated, so some trades closed within the same H4 bar and
never crossed a rollover).

## 4. Impact on the verdict

| metric | pre-financing | financing (ESTIMATED + conservative stress) | post-financing |
|---|---:|---:|---:|
| total trade PnL (USD, sum across 7 pairs × 8 folds) | −$2.67 | **−$24.38** | **−$27.05** |
| aggregate-return-pct on starting equity (per pair $500 × 7 = $3,500) | **−0.076 %** of starting bank | **−0.697 %** | **−0.773 %** of starting bank |
| `aggregate_return_pct` reported by the runner (sum of per-pair %, not normalized) | **−0.53 %** | | **deepens by ≈ −0.70 %** to **≈ −1.23 %** |
| approx aggregate expectancy R (financing applied per-trade) | **−0.0024 R** | financing-per-trade ≈ -$0.021 ≈ -0.016 R/trade equivalent | **≈ −0.018 R** |

Financing strictly **worsens** the verdict. Every PnL-direction
gate that failed in Phase 5 remains failed; **the
`conservative_stress_run_does_not_flip_verdict` gate passes
vacuously** because the pre-financing verdict was already REJECT
(it's a null model — REJECT was always the expected outcome).

| gate | pre-financing | post-financing |
|---|---|---|
| `aggregate.expectancy_R_net_of_stress_financing ≥ 0.05` | **−0.0024 R** (FAIL) | **≈ −0.018 R** (FAIL — wider) |
| `aggregate.profit_factor_net_of_stress_financing ≥ 1.10` | **0.91** (FAIL) | **deeper FAIL** (financing reduces winning sum, increases losing sum) |
| `aggregate.pairs_positive ≥ 4 of 7` | **3 / 7** (GBP_USD, USD_JPY ≈ 0, USD_CHF) (FAIL) | **2 / 7** (USD_JPY flips to net negative under financing; GBP_USD + USD_CHF remain net positive) — FAIL |
| `financing.conservative_stress_run_does_not_flip_verdict` | n/a | **PASS — verdict was already REJECT pre-financing; stress deepens the loss** |
| `financing.modeled_refused` | n/a | **PASS — MODELED never reached, all four refusal layers held** |
| `financing.missing_rate_event_count == 0` | n/a | **PASS — 0 missing** |

## 5. Per-pair financing sensitivity

| pair | trades | rollover events | trade PnL (USD) | financing (USD) | net (USD) | sign change? |
|---|---:|---:|---:|---:|---:|:---:|
| EUR_USD | 119 | 103 | −6.10 | −1.96 | −8.06 | already − |
| GBP_USD | 196 | 186 | **+20.95** | −4.05 | **+16.90** | remains + |
| USD_JPY | 174 | 159 | **+1.76** | −5.46 | **−3.70** | **+→−** (flips under financing) |
| AUD_USD | 190 | 174 | −8.65 | −2.83 | −11.48 | already − |
| USD_CAD | 182 | 170 | −2.18 | −3.42 | −5.61 | already − |
| USD_CHF | 177 | 160 | **+4.62** | −4.48 | **+0.14** | barely + (was clearly +) |
| NZD_USD | 139 | 128 | −13.07 | −2.17 | −15.25 | already − |
| **total** | 1,177 | 1,080 | −2.67 | −24.38 | −27.05 | |

Under conservative stress, USD_JPY flips from net positive
(+$1.76) to net negative (−$3.70). `pairs_positive` falls from
3 / 7 to **2 / 7** (GBP_USD, USD_CHF) — already below the
≥ 4 / 7 gate either way. The aggregate sign sums consistent
with random noise + bounded financing debit.

## 6. Long vs short sensitivity

| side | trades | rollover events | trade PnL (USD) | financing (USD) |
|---|---:|---:|---:|---:|
| long | 610 | 556 | −23.48 | −12.40 |
| short | 567 | 524 | +20.80 | −11.98 |

**Long-short distribution is 610 / 567** — within statistical
bounds of a 50 / 50 random coin flip (binomial 95 % CI for 1,177
trades is ±35; observed difference is 43). Per-bar coin-flip
determinism is statistically holding.

Trade PnL is asymmetric (longs −$23, shorts +$21) — random
sampling means this asymmetry is *not* a directional edge; it's
the noise structure of a 4-year sample. Financing is symmetric
across sides (~−$12 each) — the conservative source debits both
sides equally.

## 7. Per-fold financing sensitivity

| fold | trades | rollover events | trade PnL (USD) | financing (USD) | net (USD) |
|---:|---:|---:|---:|---:|---:|
| 0 | 143 | 123 | −23.97 | −2.83 | −26.80 |
| 1 | 150 | 132 | −2.42 | −2.03 | −4.45 |
| 2 | 153 | 142 | **+21.16** | −2.64 | **+18.52** |
| 3 | 150 | 142 | −4.14 | −3.42 | −7.56 |
| 4 | 162 | 147 | −0.42 | −3.88 | −4.30 |
| 5 | 153 | 145 | **+2.72** | −3.43 | −0.71 |
| 6 | 128 | 124 | **+4.68** | −2.58 | **+2.10** |
| 7 | 138 | 125 | −0.29 | −3.57 | −3.86 |

Fold 2 (+$18.52 net) and Fold 6 (+$2.10 net) remain net
positive under financing; both fail the per-fold expectancy R
gate of ≥ 0.05 (fold 2's expectancy is +0.0387 R, fold 6's is
+0.0541 R but only 3/7 pairs positive). Random outliers like
fold 2 produce momentary positive folds — exactly the noise
structure expected from a null model.

## 8. Missing data + caveats

- **No OBSERVED financing data is available** for the
  2020-2026 universe — OANDA's v20 REST API publishes no
  historical financing-rate series, and no `DAILY_FINANCING`
  transactions were captured under the freeze. The
  `default_stress_rate_source()` is the only authorized
  bp/day reference today, per
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
  §11.
- **No MODELED treatment.** The four-layer refusal stands:
  1. `TableRateSource(treatment=MODELED)` raises.
  2. `calculate_run(rate_source)` raises if
     `source.treatment == MODELED`.
  3. `FinancingRunReport.treatment` is Pydantic-pinned to
     `ESTIMATED` / `OBSERVED` via the calculator output here.
  4. `src/forex_bot/financing.py`
     `financing_treatment_blocks_approval` continues to refuse
     paper / demo / live promotion without MODELED.
- **Cross-pair conversion deferred.** Every pair in this
  universe is XXX_USD or USD_XXX (USD is home for all), so the
  cross-pair fallback note never fires here — `notes` is empty
  for every event.
- **Holiday calendar absent.** Same caveat as CAMPAIGN_010.

## 9. Why this does not approve the strategy

- The overlay is **diagnostic context** added on top of the
  Phase 5 REJECT — it strictly worsens the result; it cannot
  upgrade the verdict.
- **CAMPAIGN_011 cannot be approved by design.** Null model;
  the protocol §4 whitelist places it under "Baseline / null
  model — cannot itself be the 'preferred candidate' for
  paper promotion."
- Even an unexpected PASS in the pre-financing run would
  trigger the investigation playbook per
  [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
  §12, **never** promotion.
- `configs/approved_strategies.yaml` remains `approved: []`.

## 10. Comparison to CAMPAIGN_010's financing overlay

| dimension | CAMPAIGN_010 | **CAMPAIGN_011** |
|---|---:|---:|
| total trades | 2,791 | **1,177** |
| financing events | 2,483 (events:trades 0.89) | **1,080 (events:trades 0.92)** |
| `cashflow_home_stress_total` | −$55.69 | **−$24.38** |
| per-trade financing | −$0.020 | **−$0.021** (nearly identical — consistent cost model) |
| pairs that flip +→− under stress | USD_CHF (CAMPAIGN_010's only +ve pair) | **USD_JPY** (CAMPAIGN_011's marginally +ve pair) |
| trade PnL pre-financing | −$182.78 | **−$2.67** |
| trade PnL + financing | −$238.47 | **−$27.05** |
| 4-year aggregate return % on $3,500 bank | −6.81 % | **−0.77 %** |

The per-trade financing debit (~$0.02) is essentially identical
between the two campaigns — the cost model is consistent. The
*amount* of financing differs (CAMPAIGN_010 had ~2× more trades
→ ~2× more financing events → ~2× more cashflow debit). The
ratios are what matter, and they tell the same story: a
random-entry null model produces near-zero aggregate PnL even
after financing.

## 11. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **CAMPAIGN_011** REJECT (null model anchor; cannot be approved).
- **Paper / demo / live remain blocked.**
- No broker call this sprint.
- No `.env` read; no credential printed; no account / order /
  trade / position / transaction endpoint queried.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.
- `MODELED` financing remains refused at four layers.
- pytest baseline preserved.

## 12. Cross-links

- [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)
  (template + comparison baseline)
- [`backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.json)
- [`backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md`](../../backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md)
- [`backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json)
- [`scripts/build_campaign_011_financing_overlay.py`](../../scripts/build_campaign_011_financing_overlay.py)
