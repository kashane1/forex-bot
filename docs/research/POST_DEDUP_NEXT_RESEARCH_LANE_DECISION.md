# Post-Dedup Next Research Lane Decision

**Date:** 2026-05-26  
**Sprint:** `research-post-dedup-failure-meta-analysis-001`  
**Inputs:** Phase 1 metric matrix · Phase 2 archetype analysis

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`.

---

## Selected lane

### **`pause broad strategy search`** (option 6)

No new broad CAMPAIGN_018, no pair-specific lab, no regime lab, no financing sprint, and no data-expansion sprint in the immediate next step. The next sprint should **document the pause**, consolidate dedup-safe learnings, and define re-entry criteria before any new pattern-family campaign is scaffolded.

---

## Decision summary

| option | verdict | rationale |
|---|---|---|
| 1. pair-specific lab | **reject** | USD_JPY is the only pair positive across all three campaigns, but exp_r ≈ 0.001–0.004 — economically indistinguishable from null. NZD_USD / EUR_USD “leaders” are C016 sparse-trade concentration artifacts (exp_r 1.2–2.2R on tiny *n*). |
| 2. regime-specific lab | **reject** | Six folds show isolated beat-null cells, but no fold/regime where a *family* consistently wins across C015–C017. Fold winners rotate by campaign (C015 fold 5, C016 folds 2–4, C017 folds 0/5/6). |
| 3. broad CAMPAIGN_018 discovery | **reject** | Three consecutive deduped broad families (reversal, weekly momentum, weekly vol breakout) are all REJECT + WITHIN_NULL. Another broad search without a new falsifiable hypothesis repeats known failure mode. |
| 4. financing / cost modeling | **defer** | 2× cost worsens all candidates, but aggregate base exp_r is already negative while null centre is −0.0029R. Cost drag is real (stops 50%, time 48%) yet not the primary blocker — directional edge is absent at aggregate level. MODELED financing remains refused. |
| 5. data expansion first | **defer** | C016 is sparse (137 trades) and weekly boundary parity is untested end-to-end in Backtrader, but C015 (375 trades) and C017 (230 trades) still fail WITHIN_NULL with adequate *n*. Data volume alone does not explain the rejection cluster. |
| 6. **pause broad strategy search** | **select** | Safest falsifiable next step: stop broad pattern churn until a pre-declared re-entry gate is met. |

---

## Evidence from Phase 1 (metric matrix)

| campaign | base exp_r | gap vs null | trades | fold pass | anti-overfit | Backtrader |
|---|---:|---:|---:|---:|---|---|
| CAMPAIGN_011 (null) | −0.0029 | 0 | 1,180 | 0/8 | n/a | n/a |
| CAMPAIGN_015 | −0.0101 | −0.0072 | 375 | 2/8 | WITHIN_NULL | TOLERABLE_DRIFT |
| CAMPAIGN_016 | −0.0633 | −0.0604 | 137 | 3/8 | WITHIN_NULL | BLOCKED (non-decision-blocking) |
| CAMPAIGN_017 | −0.0227 | −0.0198 | 230 | 3/8 | WITHIN_NULL | BLOCKED (non-decision-blocking) |

All three candidates sit **below** the deduped null centre on aggregate exp_r. Anti-overfit labels are uniformly WITHIN_NULL — none cleared ROBUST_ABOVE_NULL.

---

## Evidence from Phase 2 (archetypes)

### Pairs

| pair | mean exp_r (C015–C017) | pattern | lab-worthy? |
|---|---:|---|:---:|
| USD_JPY | +0.0025 | positive in 3/3 campaigns | **no** — magnitude ≈ null noise |
| USD_CAD | −0.197 | negative in 3/3 campaigns | exclusion note only |
| NZD_USD / EUR_USD | inflated mean | C016 outlier-driven | **no** — concentration artifact |
| GBP_USD | mixed | C016 −1.0R clip on sparse cells | **no** |

Automated classifier emitted `PAIR_SPECIFIC_SIGNAL_WORTH_LAB` because USD_JPY is consistently positive. **Human override:** magnitude is ~0.003R, far below the 0.03R aggregate floor and null std band (0.048R). This is not a tradable archetype.

### Side / exit

- Aggregate long exp_r: **−0.063** · short: **+0.020** — short less bad but still within null at portfolio level.
- Exit mix: **50% stops**, 48% time — losses driven by stop-outs and low hit rate, not primarily cost-stress alone.
- Weekly strategies (C016, C017) do **not** show reduced cost sensitivity; 2× cost delta is −0.008 to −0.009R.

### Fold / regime

- Fold 7: universal fail (all three campaigns negative, below null).
- Beat-null folds exist per campaign but **do not align** across families → regime lab not justified.

### Concentration

- C016 best pair NZD_USD exp_r = **2.24R** on ~3.6% of trades — classic sparse-cell artifact.
- Single-pair dominance 37–39% across campaigns — below gates but pair-level “winners” are not stable across families.

---

## Re-entry criteria (before any new broad campaign)

A future sprint may resume broad pattern research only if **all** of the following are true:

1. A **new falsifiable hypothesis** is written in a pre-commit doc — not a retune of C015/C016/C017.
2. The hypothesis specifies expected beat-null magnitude **≥ 0.05R** above deduped null centre on aggregate, with pre-declared minimum trade count.
3. Backtrader verification path is defined (not BLOCKED/DEFERRED) **or** explicitly scoped as diagnostic-only with decision-blocking flag documented.
4. Human review approves resumption in a research decision memo — still **no** `approved_strategies.yaml` edit.
5. Evidence uses **DEDUPED_INPUT** paths only; contaminated pre-fix metrics excluded.

---

## What this decision does NOT do

- Does not approve any strategy.
- Does not edit `configs/approved_strategies.yaml`.
- Does not enable paper / demo / live.
- Does not create CAMPAIGN_018.
- Does not retune C015, C016, or C017.

---

## Alternative considered seriously: data expansion

Deferred, not selected. Weekly cross-sectional momentum’s 137-trade sample is thin, but the H4 reversal campaign (375 trades) also failed WITHIN_NULL. Expanding data before pausing would likely produce another under-powered broad search unless paired with a genuinely new hypothesis class — which this sprint explicitly withholds.
