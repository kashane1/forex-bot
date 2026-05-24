# CAMPAIGN_014 Financing Overlay (ESTIMATED + conservative stress)

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
`strategy_evidence: false`

Phase 6 financing-overlay record for CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`. **Overlay does NOT
change the REJECT verdict.** Financing impact is small (consistent
with the predicted "$5–15 USD total drag" from the scaffold
sprint's `CAMPAIGN_014_FINANCING_RISK_READINESS.md` §3).

> No strategy approved. CAMPAIGN_014 remains REJECT. MODELED
> financing remains refused at 4 layers. `configs/approved_strategies.yaml`
> remains `approved: []`.

## 1. Command run

```
python scripts/build_campaign_014_financing_overlay.py \
    --campaign-dir backtests/CAMPAIGN_014_calendar_event_window_anomaly
```

| dimension | value |
|---|---|
| input trades | 720 (per-pair-per-fold CSVs from Phase 4) |
| rate source | `conservative_stress` |
| treatment | `ESTIMATED` |
| MODELED status | **REFUSED** (source's `treatment != MODELED` check intact) |
| broker call | **NONE** |
| OANDA transaction-stream query | **NONE** |
| `.env` read | **NONE** |
| credentials printed | **NONE** |

## 2. Financing source

| dimension | value |
|---|---|
| source class | `research.financing.ConservativeStressRateSource` |
| name | `conservative_stress` |
| treatment | `ESTIMATED` (the source's `treatment` attribute is `FinancingTreatment.ESTIMATED`) |
| MODELED reachable? | **NO** — the source refuses MODELED at the constructor; `calculate_run` also refuses MODELED |
| methodology | debit-on-both-sides at a per-pair pessimistic bp/day rate; Wednesday triple-multiplied; weekends skipped |
| home currency | USD |
| missing_rate_policy | `conservative` (debit on both sides at fallback bp/day for unknown pairs — n/a since all 7 USD pairs covered) |

## 3. Report fields (binding from `research.financing`)

| field | value |
|---|---|
| `strategy_evidence` | `false` |
| `financing_in_engine_pnl` | `false` (engine PnL not mutated) |
| `financing_is_live_blocker` | `true` (live promotion still requires MODELED) |
| `treatment` | `ESTIMATED` |
| `event_count` | **697** (= sum of rollovers across 720 trades; some same-day-close trades have 0 rollovers) |
| `cashflow_home_total` | **−$10.64** (estimated; debit-only conservative) |
| `cashflow_home_stress_total` | **−$10.64** (same as `cashflow_home_total` for conservative source — debit-only) |
| `missing_rate_event_count` | **0** (all 7 USD pairs covered) |

## 4. Per-pair financing breakdown

| pair | trades | rollover events | cashflow_home_total (USD) | trade PnL (USD) | financing / |PnL| |
|---|---:|---:|---:|---:|---:|
| EUR_USD | 100 | 95 | −1.34 | −25.49 | 5.3 % |
| GBP_USD | 152 | 151 | −2.13 | −16.06 | 13.3 % |
| USD_JPY | 134 | 121 | −2.72 | −19.00 | 14.3 % |
| AUD_USD |  91 | 90 | −0.98 | −31.91 | 3.1 % |
| USD_CAD |  91 | 90 | −1.19 | −17.99 | 6.6 % |
| USD_CHF |  89 | 88 | −1.59 | −31.34 | 5.1 % |
| NZD_USD |  63 | (in summary file) | (in summary file) | (in summary file) | (computed by overlay) |
| **total** | **720** | **697** | **−$10.64** | **−$154.26** | **~6.9 %** |

Full per-pair / per-side / per-fold breakdown at
`backtests/CAMPAIGN_014_calendar_event_window_anomaly/financing/financing_summary.json`.

## 5. Per-side financing

| side | trades | rollover events | cashflow_home_total (USD) | trade PnL (USD) |
|---|---:|---:|---:|---:|
| long | (~50 % of 720) | (in summary) | (in summary) | (in summary) |
| short | (~50 % of 720) | (in summary) | (in summary) | (in summary) |

Long / short financing is **symmetric** under the conservative
stress source (debit on both sides). No long / short asymmetry
from rate differentials in this view.

## 6. Per-fold financing

| fold | trades | rollover events | cashflow_home_total (USD) | trade PnL (USD) |
|---|---:|---:|---:|---:|
| fold_00 | 93 | (in summary) | (in summary) | (in summary) |
| fold_01 | 84 | (in summary) | (in summary) | (in summary) |
| fold_02 | 82 | (in summary) | (in summary) | (in summary) |
| fold_03 | 90 | (in summary) | (in summary) | (in summary) |
| fold_04 | 100 | (in summary) | (in summary) | (in summary) |
| fold_05 | 92 | (in summary) | (in summary) | (in summary) |
| fold_06 | 89 | (in summary) | (in summary) | (in summary) |
| fold_07 | 90 | (in summary) | (in summary) | (in summary) |
| **total** | **720** | **697** | **−$10.64** | **−$154.26** |

Per-fold detail at the summary JSON.

## 7. Pair-flip table (none)

A "pair flip" would mean a pair that was profitable on raw PnL
becomes unprofitable after financing. **Zero flips for CAMPAIGN_014
since every pair is already unprofitable on raw PnL.** No pair was
positive pre-financing → no pair flips negative under financing.

This is qualitatively different from CAMPAIGN_011 (where USD_JPY
flipped from marginally + to − under financing) and CAMPAIGN_010
(where 1-2 pairs flipped) — CAMPAIGN_014 has no flip candidates
because the directional hypothesis is wrong at gross.

## 8. Impact on verdict

| dimension | pre-financing | post-financing | verdict impact |
|---|---:|---:|---|
| aggregate trade PnL (USD) | −$154.26 | −$164.90 (PnL + financing) | strictly worse |
| aggregate return % (4 y) | −30.85 % | ~−33.0 % (rough estimate) | strictly worse |
| pairs positive | 0 / 7 | 0 / 7 | unchanged |
| inherited gates passing | 2 / 8 | 2 / 8 | unchanged |
| **verdict** | **REJECT** | **REJECT** | **unchanged** |

**Financing makes the REJECT slightly worse, never better.** No
verdict change. No "post-financing positive expectancy"
possibility (CAMPAIGN_014 fails by a wide margin on every direction
gate, and financing only adds debit).

## 9. Comparison to prior campaigns

| dimension | C010 | **C011 null** | C012 | C013 | **C014** |
|---|---:|---:|---:|---:|---:|
| total trades | 1,103 | 1,177 | 3,726 | 7,940 | **720** |
| financing rollover events | (per their docs) | 1,177 events | 3,726 | 7,940 | **697** |
| cashflow_home_stress_total (USD) | (per their docs) | −$24.38 | (per their docs) | −$139.99 | **−$10.64** |
| per-trade financing (bp) | ~0.5 | ~0.5 | ~0.5 | ~0.5 | **~0.3 bp** (lower; shorter avg hold) |
| financing/|PnL| ratio | (per their docs) | (per their docs) | (per their docs) | (per their docs) | **6.9 %** |
| pair flips under financing | 1-2 (per their docs) | 1 (USD_JPY) | 0 | 0 | **0** (already at floor) |

**CAMPAIGN_014's financing cost is the LOWEST in absolute USD of
any real candidate** (−$10.64), consistent with the scaffold
sprint's prediction (≤ 6-bar hold ≈ 1 rollover at most per trade;
many trades close same-day with 0 rollovers). This is the
design's clean payoff — short hold means small financing. The
hypothesis still falsified despite tiny financing cost.

## 10. MODELED refusal verified

| layer | status |
|---|---|
| `ConservativeStressRateSource` constructor | refuses MODELED |
| `TableRateSource` constructor (not used here) | refuses MODELED |
| `calculate_run` (source self-reporting MODELED) | raises |
| `financing_treatment_blocks_approval` in `src/forex_bot/financing.py` | unchanged; live still requires MODELED |

**4 of 4 refusal layers intact.** No code path in this sprint
emits MODELED financing.

## 11. Validation commands run after Phase 6

```
ruff check scripts/build_campaign_014_financing_overlay.py  # All checks passed
python -m pytest -q                                          # 968 / 968 PASS
python scripts/validate_research_archive.py                  # ALL PASS
python scripts/check_research_freeze.py                      # ALL PASS
python scripts/scan_artifacts_for_secrets.py                 # PASSED
git status --short                                            # only Phase 6 artifacts
```

## 12. Safety state (unchanged after Phase 6)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | REJECT (Phase 5 verdict unchanged by financing) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| MODELED financing reachable | no |
| broker call this phase | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| engine PnL mutated | **no** (overlay is additive) |
| financing live-promotion blocker | **stands** (live still requires MODELED) |

## 13. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md) (sprint plan)
- [`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md) (Phase 5 verdict; unchanged by overlay)
- [`CAMPAIGN_014_FINANCING_RISK_READINESS.md`](CAMPAIGN_014_FINANCING_RISK_READINESS.md) (scaffold-sprint readiness)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md) (financing-model status; MODELED still refused)
- [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md), [`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md), [`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md) (sibling overlays)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
