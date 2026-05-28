# CAMPAIGN_022 — R-Multiple Convention Audit

**Date:** 2026-05-28 · **Sprint:** `infra-lifecycle-feature-capture-and-mfe-mae-execution-001`
**Scope:** read-only audit of committed C022 trade artifacts. **No verdict changed,
no historical metric rewritten, no strategy logic touched.**

## Question

The prior sprint noticed `near_full_loss_share` (share of trades with R ≤ −0.9)
was **0** for USD_JPY and USD_CAD even though hard-stop share was ~60% and the
published per-pair expectancy matched the artifacts. Is this a harmless FX
artifact, a reporting quirk, or an R-normalization bug?

## Method

For every committed `*_train_base_trades.csv`, at hard-stop rows the **price-based
R is exactly −1 by construction** (exit price == stop price). Comparing recorded
`r_multiple` to that price-based R isolates the convention.

## Finding — proven R-normalization inconsistency (USD-base pairs)

At hard stops (exit == stop ⇒ price-based R = −1.000 for all pairs):

| pair | quote role | mean recorded `r_multiple` at stop | recorded_r × rate |
|---|---|---|---|
| AUD_USD | USD-quote | **−1.000** | — |
| EUR_USD | USD-quote | **−1.000** | — |
| GBP_USD | USD-quote | **−1.000** | — |
| NZD_USD | USD-quote | **−1.000** | — |
| USD_CAD | USD-**base** | −0.762 | **−1.0000** |
| USD_CHF | USD-**base** | −1.078 | **−1.0000** |
| USD_JPY | USD-**base** | −0.0082 | **−1.0000** |

The relationship is **exact**: for USD-base pairs (`USD_xxx`), recorded
`r_multiple = price_based_R / rate`, where `rate` is the quote units per 1 USD
(≈110 for JPY, ≈1.31 for CAD, ≈0.93 for CHF). For USD-quote pairs (`xxx_USD`),
recorded R equals the price-based R (correct).

This is **not** stop-only. Checking time-exit rows, the *entire* `r_multiple`
column is scaled the same way — `price_based_R / recorded_r` averages ≈123 for
USD_JPY, ≈1.31 for USD_CAD, ≈0.93 for USD_CHF, and ≈1.000 for EUR_USD.

## Classification

**An R-normalization inconsistency (bug) in the C022 trade exporter**, not a
price/fill error. The entry/exit/stop prices and (separately) the account-currency
`pnl` column are internally consistent; only the `r_multiple` carries a residual
`1/rate` factor for pairs where USD is the **base** currency. Mechanically: R
should be the dimensionless `pnl_account / risk_account`; the quote→USD conversion
that is correctly applied to one of numerator/denominator is **not** applied to the
other for USD-base pairs, leaving R off by the exchange rate.

## Why `near_full_loss_share` was 0 for USD_JPY / USD_CAD

A full-stop loss is price-based −1R. After the `1/rate` scaling the recorded R is
USD_JPY ≈ −0.008 and USD_CAD ≈ −0.76 — both **above** the −0.9 threshold, so they
are never counted as near-full-losses despite being exactly full-stop losses.
USD_CHF (rate ≈0.93) scales to ≈ −1.08, which is below −0.9, so CHF *was* counted —
explaining why only JPY and CAD showed 0.

## Impact on the C022 verdict — none, and the quirk *flatters* C022

Because USD-base R is divided by the rate, the recorded per-pair R **understates**
the true risk-based losses for USD_JPY and USD_CAD (and slightly overstates CHF).
Approximate corrected per-pair train expectancy (recorded × mean rate):

| pair | recorded train exp_R | approx corrected exp_R | direction |
|---|---|---|---|
| USD_JPY | −0.0017 | ≈ **−0.21** | far more negative |
| USD_CAD | −0.0512 | ≈ **−0.067** | more negative |
| USD_CHF | −0.1051 | ≈ −0.098 | ~unchanged (slightly less) |

So a corrected R convention makes C022 **worse**, not better — it would push the
aggregate further below zero. The existing **REJECT is unaffected and, if anything,
reinforced.** There is no scenario where fixing this rescues C022. (Note: USD_JPY's
published near-zero −0.0017R was an artifact of the scaling, not evidence of a
salvageable pair.)

## Actions taken

- **Characterization/regression tests added:** `tests/unit/test_c022_r_convention_audit.py`
  (8 tests) lock the empirical relationship — USD-quote stops record −1R; USD-base
  stops record `r × rate == −1`; JPY/CAD recorded R > −0.9 despite being full
  losses; and a pair-agnostic `price_based_r` helper returns −1 at stop for any
  quote scale. Read-only; artifacts untouched.

## Actions deliberately NOT taken (per sprint rules)

- **No rewrite of historical C022 metrics.** The published numbers stand as the
  record of what the (inconsistent) exporter produced; rewriting them is out of
  scope and unnecessary for the terminal REJECT.
- **No strategy-logic, parameter, or verdict change.**

## Recommendation

1. **Forward fix (this sprint, Phase 3):** the new `lifecycle_features` schema
   must define R as a single, **pair-agnostic, price-based** quantity (R = −1 at
   the stop for every pair) so future campaigns never reproduce this. The
   `price_based_r` helper in the audit test encodes the correct convention.
2. **Optional repair sprint (separate, explicitly scoped):** if the project wants
   *comparable* historical per-pair R across C019–C022, a dedicated repair sprint
   should recompute R from prices/pnl and re-archive — clearly labeled, verdicts
   unchanged. Not required for any current decision.
