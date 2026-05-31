# Post-Dedup Failure Meta-Analysis — Sprint 001 Summary

**Date:** 2026-05-26  
**Branch:** `research-post-dedup-failure-meta-analysis-001`  
**Base:** `research-weekly-volatility-contraction-breakout-001`

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_018 was **not** created.

---

## 1. Sprint outcome

Analyzed dedup-safe evidence from CAMPAIGN_011 (null), CAMPAIGN_015, CAMPAIGN_016, and CAMPAIGN_017. Built comparable metric matrix and archetype analysis. Selected next lane: **pause broad strategy search**.

---

## 2. Commits by phase

| phase | description | key files |
|---|---|---|
| 0 | Truth audit + plan | `docs/research/POST_DEDUP_FAILURE_META_ANALYSIS_001_PLAN.md` |
| 1 | Metric collector + matrix | `scripts/collect_post_dedup_campaign_metrics.py`, `research/post_dedup_meta/campaign_metric_matrix.*`, `docs/research/POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md`, `tests/unit/test_post_dedup_meta_analysis.py`, fixtures |
| 2 | Archetype analysis | `scripts/analyze_post_dedup_archetypes.py`, `research/post_dedup_meta/archetype_analysis.*`, `docs/research/POST_DEDUP_ARCHETYPE_ANALYSIS.md` |
| 3 | Lane decision | `docs/research/POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md` |
| 4 | Next sprint prompt | `docs/research/NEXT_SPRINT_PROMPT_AFTER_POST_DEDUP_META.md` |
| 5 | Summary + validation | this file |

---

## 3. Campaigns included

| campaign | role | dedup-safe path |
|---|---|---|
| CAMPAIGN_011 | deduped null baseline | `research/null_baselines/campaign_011_deduped_null_baseline.json` |
| CAMPAIGN_015 | candidate (REJECT) | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/` |
| CAMPAIGN_016 | candidate (REJECT) | `backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/` |
| CAMPAIGN_017 | candidate (REJECT) | `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/` |

---

## 4. Metric matrix summary

| campaign | base exp_r | gap vs null | trades | fold pass | PF | anti-overfit |
|---|---:|---:|---:|---:|---:|---|
| CAMPAIGN_011 | −0.0029 | 0 | 1,180 | 0/8 | 0.894 | n/a |
| CAMPAIGN_015 | −0.0101 | −0.0072 | 375 | 2/8 | 2.848 | WITHIN_NULL |
| CAMPAIGN_016 | −0.0633 | −0.0604 | 137 | 3/8 | 0.982 | WITHIN_NULL |
| CAMPAIGN_017 | −0.0227 | −0.0198 | 230 | 3/8 | 0.770 | WITHIN_NULL |

All candidates worsen under 2× cost stress. C016 is the weakest aggregate performer despite 3/8 fold pass.

---

## 5. Archetype findings

| dimension | finding |
|---|---|
| Least bad pair | USD_JPY — positive in 3/3 campaigns but exp_r ≈ 0.001–0.004 (null noise) |
| Worst pair | USD_CAD — negative in 3/3 campaigns (mean −0.197R) |
| Side | Short less bad (−0.063 long vs +0.020 short aggregate) but portfolio still WITHIN_NULL |
| Exit driver | Stops 50%, time 48% — low hit rate / stop-outs dominate |
| Weekly cost | C016/C017 2× cost deltas ≈ −0.008 to −0.009R; weekly turnover does not rescue edge |
| Fold regime | Fold 7 universal fail; beat-null folds do not replicate across strategy families |
| Concentration | C016 NZD_USD 2.24R on sparse trades — artifact, not signal |

---

## 6. Reliable archetype?

**No.** Automated classifier flagged `PAIR_SPECIFIC_SIGNAL_WORTH_LAB` on USD_JPY consistency, but human review overrides: magnitude is economically null. No pair, side, fold, or exit archetype survives aggregate WITHIN_NULL scrutiny at tradable magnitude.

Labels applied: `NO_RELIABLE_ARCHETYPE`, `COST_MODEL_DOMINATES` (secondary), `DATA_TOO_SPARSE` (C016 weekly).

---

## 7. Selected next research lane

**`pause broad strategy search`**

See [`POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md`](POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md).

---

## 8. Why selected

Three consecutive deduped broad pattern families failed WITHIN_NULL. Exploratory pair/fold cells are either noise (USD_JPY), concentration artifacts (C016 NZD_USD), or non-replicating across families (fold winners rotate by campaign). Retuning rejected campaigns is forbidden. CAMPAIGN_018 broad discovery is not falsifiably justified. Pausing contains overfitting risk and forces explicit re-entry criteria before the next pattern-family spend.

---

## 9. Safety checks

| check | result |
|---|---|
| CAMPAIGN_018 created | **no** |
| Strategy approved | **no** — `approved: []` |
| Paper / demo / live | **blocked** — freeze gate PASS |
| pytest | 1565 passed (including 5 new collector/archetype tests) |
| ruff | All checks passed |
| research freeze | ALL CHECKS PASSED |
| archive validation | ALL CHECKS PASSED |
| secret scan | PASSED |
| .env / credentials / SQLite / bulky dumps staged | **none** |

---

## 10. Files to review first

1. [`docs/research/POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md`](POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md) — lane choice + re-entry gates
2. [`docs/research/POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md`](POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md) — headline comparison table
3. [`docs/research/POST_DEDUP_ARCHETYPE_ANALYSIS.md`](POST_DEDUP_ARCHETYPE_ANALYSIS.md) — pair/fold/side/exit synthesis
4. [`docs/research/NEXT_SPRINT_PROMPT_AFTER_POST_DEDUP_META.md`](NEXT_SPRINT_PROMPT_AFTER_POST_DEDUP_META.md) — copy-paste prompt for pause sprint
5. [`research/post_dedup_meta/campaign_metric_matrix.json`](../../research/post_dedup_meta/campaign_metric_matrix.json) — machine-readable matrix
6. [`research/post_dedup_meta/archetype_analysis.json`](../../research/post_dedup_meta/archetype_analysis.json) — machine-readable archetypes
