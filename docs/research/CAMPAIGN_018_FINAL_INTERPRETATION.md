# CAMPAIGN_018 Final Interpretation

**Date:** 2026-05-27  
**Branch:** `research-campaign-018-protective-stop-execution-001`

> **Final campaign interpretation** — `strategy_evidence: true`, `not_approved: true`.

---

## Final verdict

**REJECT** — precommitted screening gates failed. Test lockbox not opened.

---

## Hypothesis: supported or falsified?

**Falsified on primary gate.** The protective-stop-after-+1R exit did **not** achieve train expectancy ≥ 0. Validation improved vs C008 deduped (+0.194 vs +0.161) but train deteriorated (−0.119 vs −0.025).

The hypothesis that break-even protection after +1R would reduce hard-stop churn **without** destroying aggregate edge is **not supported** on the train split under precommitted rules.

---

## Delayed-reversion tail preserved?

**Partially.** Time exits remain (16.4% of all run trades vs C008 ~32% on comparable base-only subset — protective exits absorbed part of the tail). Validation expectancy rose, suggesting some delayed-reversion value retained, but train failure dominates.

---

## Hard-stop churn improved?

**Mixed.** Hard stop share fell vs C008 (~68% → ~47% on combined diagnostics), but **protective_stop exits (37%)** largely replaced them — many ~0R scratches that did not fix train PnL. Net train expectancy **worse**.

---

## C009 target-capping avoided?

**Yes.** Zero target exits. No midline cap. Winner tail not artificially clipped by fixed TP.

---

## Train / validation / stress / null

| check | result |
|---|---|
| train exp ≥ 0 | **FAIL** |
| validation exp gates | **PASS** |
| 2× stress validation | **PASS** (+0.178 R) |
| beat C011 null | **PASS** |
| full 1.5× stress | **FAIL** |

---

## Test lockbox

**Not opened.**

---

## Why no approval

- REJECT verdict on precommitted gates
- Mean-reversion tail risk unchanged
- Train failure worse than C008
- Financing still unmodeled for multi-day holds
- Broad strategy search still paused
- `configs/approved_strategies.yaml` empty

---

## Implications for future research

1. **Protective stop alone** does not rescue range MR train expectancy — hypothesis closed for v0.1.0-c018.
2. Validation uplift is **insufficient** without train gate pass — do not promote on validation alone.
3. Exit research may continue only under **new campaign ID** — no retune of C018 threshold.
4. Consider **financing overlay sprint** before any future multi-day-hold exit variant.
5. Regime / entry-quality separation (bad-entry ~40% bucket) may need **entry-side** research — outside this exit precommit.

---

## Explicit statement

CAMPAIGN_018 does not approve any strategy. C008/C009 remain REJECT. No paper/demo/live enablement.
