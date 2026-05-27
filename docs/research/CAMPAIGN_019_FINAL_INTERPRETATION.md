# CAMPAIGN_019 — Final Interpretation

**Date:** 2026-05-27  
**Branch:** `research-campaign-019-thesis-invalidation-execution-001`  
**Verdict:** **REJECT**

---

## Final verdict

The precommitted hypothesis `thesis_invalidation_zscore_continuation_exit` is **falsified on
train**. Validation showed positive expectancy (+0.0962 R) and beat the C011 null, but the
repo's binding gate requires train pass before lockbox — same structural failure mode as C018.

---

## Hypothesis support

| Question | Answer |
|---|---|
| Thesis invalidation fired? | Yes — 12.3–13.0% of train/val trades (within 5–45% band) |
| Hypothesis supported? | **No** — train expectancy remained negative |
| Mechanism operative? | Yes — z-score exits at ±3.0 observed; zero target/protective |

---

## Train vs gates

| Check | Result |
|---|---|
| Train expectancy ≥ 0 | **FAIL** (−0.072 R) |
| Train improved vs C008 deduped | **FAIL** (C008 −0.025 R; C019 worse by −0.047 R) |
| vs C018 train | C019 **better** (−0.072 vs −0.119 R) but still negative |

---

## Validation vs gates

| Check | Result |
|---|---|
| Validation exp > 0 | **PASS** (+0.0962 R) |
| Validation PF ≥ 1.05 | **PASS** (1.1423) |
| Beat C011 null + 0.010 R | **PASS** |
| 2× cost stress | **PASS** (+0.0499 R) |

Validation uplift alone is **insufficient** per precommit (C018 precedent).

---

## Mechanism quality

| Diagnostic | C019 | Notes |
|---|---|---|
| Thesis invalidation rate | 12.6% | Active, not inert |
| Time-exit share (train) | 26.5% | Preserved (≥15% diagnostic) |
| Time-exit median R | 1.36 R | Below C008 ~3.29 R — tail weakened |
| Hard-stop share (train) | 60.7% | Still dominant; invalidation did not fix train |
| Target / protective exits | 0 | Scope respected |

---

## Stress and null

| Check | Result |
|---|---|
| stress_15x full window | **FAIL** (−0.0139 R) |
| vs C011 null | **PASS** (meaningful beat, not WITHIN_NULL) |

---

## Backtrader parity

**PASS** — train 219/219 exact; validation 138/137 (±1); exit shares CLOSE_MATCH.

---

## Test lockbox

**Not opened** — screening failed.

---

## Why no approval

Train failure is a binding falsifier. Precommit maximum outcome even on full pass would be
RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED — not approval. Campaign did not reach that stage.

---

## Future research implications

1. **Z-score continuation invalidation** at ±3.0 does not rescue C008 train expectancy; validation-only uplift pattern persists (C018/C019).
2. **USD_CAD train drag** (−0.39 R) remains a major train-loss contributor — structural pair issue, not exit-only.
3. Next work should **not** retune C019 parameters. Options: exit-hypothesis precommit 003 with a different falsifiable mechanism, or infrastructure (financing overlay, stop/exit diagnostics) before another MR exit campaign.
4. Backtrader lane is **viable** for C019 — independent corroboration available for future exit tests.
