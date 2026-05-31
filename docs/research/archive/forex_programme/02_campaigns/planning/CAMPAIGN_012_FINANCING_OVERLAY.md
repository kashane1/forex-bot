# CAMPAIGN_012 Financing Overlay (Phase 6)

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
`strategy_evidence: false`

Phase 6 ESTIMATED + conservative-stress financing overlay for
**CAMPAIGN_012 / `regime_switcher_atr_percentile 0.1.0-c012`**. The
Phase 5 verdict was already REJECT; this overlay confirms financing
**worsens** the result further and that the conservative-stress
overlay does not flip any verdict-relevant gate.

> No broker call. No `.env` read. No OANDA transaction-stream query.
> MODELED treatment refused at the source layer (the call would
> raise). Engine PnL is unchanged; the overlay is additive context.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / 010 / 011 remain REJECT. CAMPAIGN_012 verdict
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
`build_campaign_012_financing_overlay.py` script aborts before any
run if the source's treatment is MODELED — matching CAMPAIGN_010 /
011 verbatim. MODELED financing requires the separately-authorized
credentialed pilot
`research-financing-modeled-capture-credentialed-001`, which has not
run.

## 2. Command run

```bash
python scripts/build_campaign_012_financing_overlay.py \
  --campaign-dir backtests/CAMPAIGN_012_regime_switcher_atr_percentile
```

Output (committed):

- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_run.json`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_run.md`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_summary.json`

## 3. Aggregate financing

| field | value |
|---|---|
| positions (trades) | 3,726 |
| rollover event_count | 3,404 |
| missing_rate_event_count | **0** |
| `cashflow_home_total` | **−$65.07** (estimated baseline) |
| `cashflow_home_stress_total` | **−$65.07** (conservative stress; identical to baseline here because the `conservative_stress` source's stress overlay is the worst-case debits-on-both-sides ESTIMATED projection) |
| trade PnL (pre-financing) | −$217.58 (matches engine: −43.52 % of $500 starting equity) |
| trade PnL + financing (estimated) | **−$282.65** (additional −$65.07 drag from rollovers) |

Conservative-stress treatment of the `conservative_stress` source
applies debits-on-both-sides bp/day rates; under this source the
"stress" and "base estimated" projections are equal by construction
(the source is the worst-case projection — it cannot get worse).

## 4. Per-pair sensitivity

| pair | trades | rollover events | cashflow (USD) | stress (USD) | pre-financing trade PnL (USD) | post-financing trade PnL (USD) |
|---|---:|---:|---:|---:|---:|---:|
| EUR_USD | 479 | 432 | −7.47 | −7.47 | −5.36 | **−12.83** |
| GBP_USD | 555 | 508 | −9.58 | −9.58 | −40.61 | **−50.19** |
| USD_JPY | 624 | 578 | −16.01 | −16.01 | +41.71 | **+25.70** |
| AUD_USD | 551 | 503 | −7.01 | −7.01 | −67.39 | **−74.40** |
| USD_CAD | 584 | 530 | −8.96 | −8.96 | −63.55 | **−72.51** |
| USD_CHF | 542 | 493 | −11.25 | −11.25 | −28.69 | **−39.94** |
| NZD_USD | 391 | 360 | −4.79 | −4.79 | −53.68 | **−58.47** |
| **total** | **3,726** | **3,404** | **−65.07** | **−65.07** | **−217.58** | **−282.65** |

USD_JPY is the only pair with a pre-financing positive trade PnL
(+$41.71); financing drags it down to +$25.70 — still positive but
materially smaller. No pair flips +→− under stress (USD_JPY's
financing drag is large but its pre-financing PnL is large enough to
absorb it; all other pairs were already negative pre-financing).

## 5. Long / short sensitivity

| side | trades | events | cashflow (USD) | stress (USD) | pre-financing trade PnL (USD) | post-financing trade PnL (USD) |
|---|---:|---:|---:|---:|---:|---:|
| long | 1,918 | 1,768 | −34.37 | −34.37 | −112.21 | **−146.58** |
| short | 1,808 | 1,636 | −30.70 | −30.70 | −105.37 | **−136.07** |
| **total** | **3,726** | **3,404** | **−65.07** | **−65.07** | **−217.58** | **−282.65** |

The long/short split is essentially symmetric (51.5 %/48.5 % trade
share; similar financing impact). The regime gate does not
preferentially fire long or short; the trend-filter sub-signal
distributes evenly given the regime + close-vs-close definition.

## 6. Per-fold sensitivity

| fold | trades | events | cashflow (USD) | stress (USD) | pre-financing trade PnL (USD) | post-financing trade PnL (USD) |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 678 | 596 | −13.19 | −13.19 | −66.45 | **−79.64** |
| 1 | 811 | 732 | −12.45 | −12.45 | −64.70 | **−77.15** |
| 2 | 320 | 291 | −4.11 | −4.11 | −38.39 | **−42.50** |
| 3 | 254 | 237 | −4.65 | −4.65 | −14.13 | **−18.78** |
| 4 | 358 | 347 | −7.44 | −7.44 | −10.23 | **−17.67** |
| 5 | 407 | 383 | −8.40 | −8.40 | +7.61 | **−0.79** |
| 6 | 638 | 584 | −11.03 | −11.03 | −23.78 | **−34.81** |
| 7 | 260 | 234 | −3.81 | −3.81 | −7.51 | **−11.32** |
| **total** | **3,726** | **3,404** | **−65.07** | **−65.07** | **−217.58** | **−282.65** |

**Fold 5 flips +→− under financing** (+$7.61 pre-financing → −$0.79
post-financing). This was already a REJECT fold pre-financing
(expectancy −0.0077 R; pairs-positive 3/7 below the ≥ 4/7 gate), so
the flip is informational, not verdict-changing.

## 7. Pair-flip table (under conservative stress)

| pair | pre-stress sign | post-stress sign | flips? |
|---|:---:|:---:|:---:|
| EUR_USD | − | − | no |
| GBP_USD | − | − | no |
| USD_JPY | **+** | **+** | no (drag from +$41.71 to +$25.70; still positive) |
| AUD_USD | − | − | no |
| USD_CAD | − | − | no |
| USD_CHF | − | − | no |
| NZD_USD | − | − | no |

**No pair flips signs.** The conservative-stress overlay simply
deepens existing losses; the only positive pair (USD_JPY) absorbs the
financing drag without flipping. Importantly, no pair gains from
financing.

## 8. Impact on verdict

| dimension | pre-financing | post-financing | gate threshold | post-financing gate |
|---|---:|---:|---|:---:|
| aggregate trade PnL (USD) | −217.58 | **−282.65** | n/a | n/a |
| aggregate return % | −43.52 % | (~−56.5 %)* | ≥ 0.05 R (expectancy) | **FAIL** |
| aggregate expectancy R | −0.0521 | (~−0.0660)* | ≥ 0.05 R | **FAIL** |
| pairs positive | 1 / 7 (USD_JPY +0.0004 R) | 1 / 7 (USD_JPY drops but stays positive) | ≥ 4 / 7 | **FAIL** |
| fold pass rate | 0 / 8 | 0 / 8 | 100 % | **FAIL** |
| MODELED financing | refused | refused | required for live promotion | **BLOCKER (independent of CAMPAIGN_012 verdict)** |
| `conservative_stress_run_does_not_flip_verdict` | n/a | PASS (verdict already REJECT pre-financing; cannot get *less* REJECT) | required | **PASS** |
| `modeled_refused` | n/a | PASS (4-layer refusal intact) | required | **PASS** |
| `missing_rate_event_count` | n/a | 0 | = 0 | **PASS** |

\* Approximate post-financing R/% values; the engine's expectancy R
is in stop-units, not USD, so the exact post-financing R requires
re-running PnL through the engine — out of scope. The directionality
(financing worsens, never improves) is what matters for the verdict.

**Verdict impact: NONE.** The Phase 5 inherited-gate verdict was
already REJECT; financing makes it more REJECT, not less. The
`conservative_stress_run_does_not_flip_verdict` gate passes (the
verdict could only flip from PASS→REJECT under stress; it was already
REJECT).

## 9. Missing data

- `missing_rate_event_count = 0`: every one of the 3,404 rollover
  events had a usable rate (via the `conservative_stress` source's
  conservative-fallback policy at 1.2 bp/day where applicable).
- No pair had insufficient trade-level holding data for the overlay.
- Total notional aggregation is implicit in the per-event `notional`
  field of `financing_run.json` (sample row: `notional=267.66` for a
  267-unit EUR_USD short at entry price 1.16654).

## 10. MODELED status (binding)

- **MODELED is refused at all 4 layers in `src/forex_bot/financing.py`.**
  The 4 layers are:
  1. `FinancingTreatment` enum lacks an `OBSERVED`/`MODELED` value that
     can be constructed without recorded fixtures.
  2. `default_stress_rate_source()` returns `treatment=estimated`.
  3. The `build_campaign_012_financing_overlay.py` script asserts
     `source.treatment != FinancingTreatment.MODELED` and aborts
     otherwise.
  4. The live-loop gate (which does not exist as a CLI command) would
     also refuse MODELED if it did exist.
- Lifting MODELED requires the separately-authorized credentialed
  pilot `research-financing-modeled-capture-credentialed-001`, which
  has not run. That pilot is **out of scope** for CAMPAIGN_012's
  REJECT verdict.
- The live-promotion financing blocker stands independently of
  CAMPAIGN_012's verdict.

## 11. Why even a paper consideration would not happen

- The Phase 5 verdict is **REJECT** — paper / demo / live promotion
  is not on the table.
- Even if a hypothetical re-design produced a passing variant, the
  live-promotion financing blocker (MODELED refused) would still
  apply.
- No human approval action is justified by this evidence; the
  candidate is rejected.

## 12. Explicit no-approval statement

`configs/approved_strategies.yaml` remains `approved: []`.
CAMPAIGN_012 is rejected. The financing overlay confirms the verdict
and reinforces it (worsens net PnL by −$65.07). Paper / demo / live
remain blocked.

## 13. Committed artifacts

| path | what |
|---|---|
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_run.json` | per-rollover-event detail (3,404 events) |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_run.md` | human-readable per-position summary |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_summary.json` | aggregate + by-pair / by-side / by-fold breakdown |
| `scripts/build_campaign_012_financing_overlay.py` | NEW; mirrors CAMPAIGN_011 verbatim with campaign-id swap |
| `docs/research/CAMPAIGN_012_FINANCING_OVERLAY.md` (this doc) | sprint-level summary |

## 14. Cross-links

- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_012_FINANCING_RISK_READINESS.md`](CAMPAIGN_012_FINANCING_RISK_READINESS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md) (sibling)
- [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md) (sibling)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
