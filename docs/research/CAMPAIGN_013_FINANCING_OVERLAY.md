# CAMPAIGN_013 Financing Overlay (Phase 6)

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
`strategy_evidence: false`

Phase 6 ESTIMATED + conservative-stress financing overlay for
**CAMPAIGN_013 / `cross_pair_currency_strength_rotation 0.1.0-c013`**.
The Phase 5 verdict was already REJECT; this overlay confirms
financing **worsens** the result further and that the
conservative-stress overlay does not flip any verdict-relevant gate
toward PASS. (It does flip USD_JPY — the only positive pair — from
+→−, taking `pairs_positive_count` from 1/7 to 0/7.)

> No broker call. No `.env` read. No OANDA transaction-stream query.
> MODELED treatment refused at the source layer (the call would
> raise). Engine PnL is unchanged; the overlay is additive context.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / 010 / 011 / 012 remain REJECT. CAMPAIGN_013 verdict
> remains `REJECT` after financing.

## 1. Financing source

| field | value |
|---|---|
| source name | `conservative_stress` |
| `FinancingTreatment` | `estimated` (the conservative-stress source is `estimated`-tier; not OBSERVED, not MODELED) |
| MODELED available | **no** (refused at 4 layers in `src/forex_bot/financing.py`; the constructor would raise on any attempt) |
| home currency | USD |
| rollover hour UTC | 21 |
| triple-swap weekday | 2 (Wednesday) |
| skip weekends | True |
| missing rate policy | `conservative` |
| conservative fallback bp/day | 1.2 |
| missing_rate_event_count | **0** (no rollover event lacked a rate) |

**This script uses ESTIMATED + conservative-stress only.** The
`build_campaign_013_financing_overlay.py` script aborts before any
run if the source's treatment is MODELED — matching CAMPAIGN_010 /
011 / 012 verbatim. MODELED financing requires the
separately-authorized credentialed pilot
`research-financing-modeled-capture-credentialed-001`, which has not
run.

## 2. Command run

```bash
python scripts/build_campaign_013_financing_overlay.py \
  --campaign-dir backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation
```

Output (committed):

- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_run.json`
- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_run.md`
- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_summary.json`

## 3. Aggregate financing

| field | value |
|---|---|
| positions (trades) | 7,940 |
| rollover event_count | **7,154** |
| missing_rate_event_count | **0** |
| `cashflow_home_total` | **−$139.99** (estimated baseline) |
| `cashflow_home_stress_total` | **−$139.99** (conservative stress; identical to baseline because the `conservative_stress` source's stress overlay *is* the worst-case debits-on-both-sides ESTIMATED projection) |
| trade PnL (pre-financing) | **−$566.79** (matches engine: −113.36 % across 7 × $500-per-pair = $3,500 total starting equity → −$566.80; reconciles to ±$0.01) |
| trade PnL + financing (estimated) | **−$706.78** (additional −$139.99 drag from rollovers) |

Conservative-stress treatment of the `conservative_stress` source
applies debits-on-both-sides bp/day rates; under this source the
"stress" and "base estimated" projections are equal by construction
(the source is the worst-case projection — it cannot get worse).

## 4. Per-pair sensitivity

| pair | trades | rollover events | cashflow (USD) | stress (USD) | pre-financing trade PnL (USD) | post-financing trade PnL (USD) |
|---|---:|---:|---:|---:|---:|---:|
| EUR_USD | 1,412 | 1,275 | −28.15 | −28.15 | −84.66 | **−112.81** |
| GBP_USD | 648 | 581 | −10.83 | −10.83 | −48.94 | **−59.77** |
| USD_JPY | 310 | 280 | −8.16 | −8.16 | **+2.27** | **−5.89** (flips + → −) |
| AUD_USD | 1,942 | 1,757 | −26.99 | −26.99 | −101.32 | **−128.31** |
| USD_CAD | 958 | 875 | −19.91 | −19.91 | −52.01 | **−71.92** |
| USD_CHF | 807 | 715 | −20.50 | −20.50 | −73.33 | **−93.83** |
| NZD_USD | 1,863 | 1,671 | −25.45 | −25.45 | −208.82 | **−234.27** |
| **total** | **7,940** | **7,154** | **−139.99** | **−139.99** | **−566.79** | **−706.78** |

USD_JPY is the only pair with a pre-financing positive trade PnL
(+$2.27). Financing drags it to −$5.89 — **USD_JPY flips + → −
under financing**, taking `pairs_positive_count` from 1/7 to 0/7
post-financing. (The pre-financing 1/7 figure was already a binding
gate failure; the post-financing 0/7 is *more* failure, not a verdict
flip.)

NZD_USD remains the worst pair: −$234.27 post-financing (33 % of
the entire portfolio's post-financing loss from a single pair).

## 5. Long / short sensitivity

| side | trades | events | cashflow (USD) | stress (USD) | pre-financing trade PnL (USD) | post-financing trade PnL (USD) |
|---|---:|---:|---:|---:|---:|---:|
| long | 3,927 | 3,537 | −65.06 | −65.06 | −318.07 | **−383.13** |
| short | 4,013 | 3,617 | −74.92 | −74.92 | −248.72 | **−323.64** |
| **total** | **7,940** | **7,154** | **−139.99** | **−139.99** | **−566.79** | **−706.78** |

The long/short split is essentially symmetric (49.5 %/50.5 % trade
share; financing drag roughly proportional). The cross-pair rotation
rule fires both sides depending on USD-strength regime; there is no
structural long or short bias. The slightly higher short-side
financing drag (−$74.92 vs −$65.06) reflects the modest skew toward
short USD positions during the test windows.

## 6. Per-fold sensitivity

| fold | trades | events | cashflow (USD) | stress (USD) | pre-financing trade PnL (USD) | post-financing trade PnL (USD) |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 794 | 710 | −17.25 | −17.25 | −96.66 | **−113.91** |
| 1 | 321 | 291 | −3.99 | −3.99 | −1.42 | **−5.41** |
| 2 | 1,166 | 1,052 | −14.37 | −14.37 | −66.44 | **−80.81** |
| 3 | 810 | 716 | −11.36 | −11.36 | −85.16 | **−96.52** |
| 4 | 1,255 | 1,137 | −22.24 | −22.24 | −74.66 | **−96.90** |
| 5 | 1,252 | 1,129 | −23.88 | −23.88 | −81.55 | **−105.43** |
| 6 | 1,149 | 1,040 | −25.92 | −25.92 | −34.29 | **−60.21** |
| 7 | 1,193 | 1,079 | −20.99 | −20.99 | −126.60 | **−147.59** |
| **total** | **7,940** | **7,154** | **−139.99** | **−139.99** | **−566.79** | **−706.78** |

**No fold flips + → − under financing** — all 8 folds were already
negative pre-financing. The smallest pre-financing loss (fold 1 at
−$1.42) grows to −$5.41 post-financing; the largest (fold 7 at
−$126.60) grows to −$147.59. Financing is uniformly additive in the
worse direction.

## 7. Pair-flip table (under conservative stress)

| pair | pre-stress sign | post-stress sign | flips? |
|---|:---:|:---:|:---:|
| EUR_USD | − | − | no |
| GBP_USD | − | − | no |
| USD_JPY | **+** | **−** | **YES** (+$2.27 → −$5.89) |
| AUD_USD | − | − | no |
| USD_CAD | − | − | no |
| USD_CHF | − | − | no |
| NZD_USD | − | − | no |

**1 pair flips signs (USD_JPY).** The conservative-stress overlay
wipes out USD_JPY's tiny pre-financing positive ($2.27 on 310 trades,
≈ $0.007 per trade) with $8.16 of financing drag (a per-trade
$0.026 charge on the long-hold side). This drops
`pairs_positive_count` from 1/7 to **0/7 post-financing**, which is
verdict-relevant in the diagnostic sense (the strategy has *no*
positive pair after financing) but does not change the REJECT verdict
(the ≥ 4/7 gate already failed at 1/7).

Importantly, **no pair gains from financing.** No pair flips − → +.

## 8. Impact on verdict

| dimension | pre-financing | post-financing | gate threshold | post-financing gate |
|---|---:|---:|---|:---:|
| aggregate trade PnL (USD) | −566.79 | **−706.78** | n/a | n/a |
| aggregate return % | −113.36 % | (~−141.4 %)* | ≥ 0.05 R (expectancy) | **FAIL** |
| aggregate expectancy R | −0.0564 | (~−0.0702)* | ≥ 0.05 R | **FAIL** |
| pairs positive | 1 / 7 (USD_JPY +0.0000 R / +$2.27) | **0 / 7** (USD_JPY flips to −$5.89) | ≥ 4 / 7 | **FAIL** |
| fold pass rate | 0 / 8 | 0 / 8 | 100 % | **FAIL** |
| profit factor | 0.000 | ≤ 0.000* | ≥ 1.10 | **FAIL** |
| MODELED financing | refused | refused | required for live promotion | **BLOCKER (independent of CAMPAIGN_013 verdict)** |
| `conservative_stress_run_does_not_flip_verdict` | n/a | PASS (verdict already REJECT pre-financing; cannot get *less* REJECT) | required | **PASS** |
| `modeled_refused` | n/a | PASS (4-layer refusal intact) | required | **PASS** |
| `missing_rate_event_count` | n/a | 0 | = 0 | **PASS** |

\* Approximate post-financing R/% values; the engine's expectancy R
is in stop-units, not USD, so the exact post-financing R requires
re-running PnL through the engine — out of scope. Profit factor
post-financing remains ≤ 0.000 because no fold had positive total
PnL pre-financing and financing is uniformly negative. Directionality
(financing worsens, never improves) is what matters for the verdict.

**Verdict impact: NONE.** The Phase 5 inherited-gate verdict was
already REJECT; financing makes it *more* REJECT, not less. The
`conservative_stress_run_does_not_flip_verdict` gate passes (the
verdict could only flip from PASS→REJECT under stress; it was already
REJECT). The USD_JPY pair-sign flip (+ → −) is a diagnostic
worsening, not a verdict change — the inherited-gate REJECT stands
independently of pair count.

## 9. Comparison to CAMPAIGN_010 / 011 / 012 financing overlays

| metric | CAMPAIGN_010 | CAMPAIGN_011 (null) | CAMPAIGN_012 | **CAMPAIGN_013** |
|---|---:|---:|---:|---:|
| trades | 2,791 | 1,177 | 3,726 | **7,940** |
| rollover events | 2,541 | 1,089 | 3,404 | **7,154** |
| `cashflow_home_total` (USD) | −$54.20 | −$24.38 | −$65.07 | **−$139.99** |
| pre-financing trade PnL (USD) | −$28.49 | −$4.34 | −$217.58 | **−$566.79** |
| post-financing trade PnL (USD) | −$82.69 | −$28.72 | −$282.65 | **−$706.78** |
| pair-sign flips (− → + or + → −) | 0 (no − → +); USD_JPY + → − | 1 (USD_JPY + → −) | 0 (USD_JPY drag absorbed; stays +) | **1 (USD_JPY + → −)** |
| missing_rate_event_count | 0 | 0 | 0 | **0** |
| MODELED refused | yes | yes | yes | **yes** |

CAMPAIGN_013's financing drag is **~2.2 × CAMPAIGN_012's** in
absolute dollars (−$139.99 vs −$65.07), driven by ~2.1 × the trade
count and ~2.1 × the rollover events. Per-trade financing drag is
~$0.018 on CAMPAIGN_013, essentially identical to CAMPAIGN_012's
~$0.017 and CAMPAIGN_011's ~$0.021 — confirming the financing model
is unit-cost stable across campaigns; only the volume changes.

The post-financing total loss (−$706.78) is **the largest of any
campaign**, by a wide margin.

## 10. Missing data

- `missing_rate_event_count = 0`: every one of the 7,154 rollover
  events had a usable rate (via the `conservative_stress` source's
  conservative-fallback policy at 1.2 bp/day where applicable).
- No pair had insufficient trade-level holding data for the overlay.
- Total notional aggregation is implicit in the per-event `notional`
  field of `financing_run.json`.

## 11. MODELED status (binding)

- **MODELED is refused at all 4 layers in `src/forex_bot/financing.py`.**
  The 4 layers are:
  1. `FinancingTreatment` enum lacks an `OBSERVED`/`MODELED` value that
     can be constructed without recorded fixtures.
  2. `default_stress_rate_source()` returns `treatment=estimated`.
  3. The `build_campaign_013_financing_overlay.py` script asserts
     `source.treatment != FinancingTreatment.MODELED` and aborts
     otherwise.
  4. The live-loop gate (which does not exist as a CLI command) would
     also refuse MODELED if it did exist.
- Lifting MODELED requires the separately-authorized credentialed
  pilot `research-financing-modeled-capture-credentialed-001`, which
  has not run. That pilot is **out of scope** for CAMPAIGN_013's
  REJECT verdict.
- The live-promotion financing blocker stands independently of
  CAMPAIGN_013's verdict.

## 12. Why even a paper consideration would not happen

- The Phase 5 verdict is **REJECT** — paper / demo / live promotion
  is not on the table.
- Even if a hypothetical re-design produced a passing variant, the
  live-promotion financing blocker (MODELED refused) would still
  apply.
- No human approval action is justified by this evidence; the
  candidate is rejected.

## 13. Explicit no-approval statement

`configs/approved_strategies.yaml` remains `approved: []`.
CAMPAIGN_013 is rejected. The financing overlay confirms the verdict
and reinforces it (worsens net PnL by −$139.99 and drops
`pairs_positive` from 1/7 to 0/7). Paper / demo / live remain
blocked.

## 14. Committed artifacts

| path | what |
|---|---|
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_run.json` | per-rollover-event detail (7,154 events) |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_run.md` | human-readable per-position summary |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_summary.json` | aggregate + by-pair / by-side / by-fold breakdown |
| `scripts/build_campaign_013_financing_overlay.py` | NEW; mirrors CAMPAIGN_012 verbatim with campaign-id swap |
| `docs/research/CAMPAIGN_013_FINANCING_OVERLAY.md` (this doc) | sprint-level summary |

## 15. Cross-links

- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_013_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_013_FINANCING_RISK_READINESS.md`](CAMPAIGN_013_FINANCING_RISK_READINESS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md) (sibling)
- [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md) (sibling)
- [`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md) (sibling)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
