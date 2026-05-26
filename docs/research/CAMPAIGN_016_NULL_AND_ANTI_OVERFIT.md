# CAMPAIGN_016 Null and Anti-Overfit

**Date:** 2026-05-26 · **Label:** `WITHIN_NULL`

Canonical null: deduped CAMPAIGN_011 (`campaign_011_deduped_null_baseline.json`).

| metric | value |
|---|---:|
| null centre exp_r | −0.002915 |
| CAMPAIGN_016 aggregate exp_r | −0.0633 |
| gap vs null | **−0.0604** |
| null per-fold std | 0.0479 |
| LOO min mean gap | −0.156 |
| median fold exp_r | −0.086 |
| trade-level cumulative R | −8.67 |

## Anti-overfit gates

| gate | pass |
|---|---|
| LOO min mean gap ≥ 0.05 R | **no** |
| per-fold t-stat ≥ 2.0 | **no** |
| median per-fold exp_r ≥ 0 | **no** |
| trade-level cumulative R > 0 | **no** |
| pair concentration ≤ 70% | yes |
| fold concentration ≤ 60% | yes |
| cost dominance ≤ 50% | yes |

## Interpretation

Campaign aggregate is **below** the deduped null centre on expectancy R but
did not trip the strict `WORSE_THAN_NULL` multi-axis rule. Classifier
defaults to **`WITHIN_NULL`** because aggregate floor (exp_r ≥ 0.03, PF ≥
1.05) was not met.

Fold-level instability is severe: folds 2–4 positive, folds 5–7 deeply
negative — not robust.

**No approval.**

Diagnostics JSON: `research/campaign_016/diagnostics/null_and_anti_overfit.json`
