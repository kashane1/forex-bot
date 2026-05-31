# CAMPAIGN_011 Null Baseline — Supersession Record

**Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001  
**Date:** 2026-05-26

## Canonical null baseline (use for new comparisons)

| artifact | path |
|---|---|
| Machine rollup | [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json) |
| Rollup markdown | [`research/null_baselines/campaign_011_deduped_null_baseline.md`](../../research/null_baselines/campaign_011_deduped_null_baseline.md) |
| Human doc | [`CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md) |
| Promotion script | [`scripts/promote_campaign_011_deduped_null_baseline.py`](../../scripts/promote_campaign_011_deduped_null_baseline.py) |

**Data policy:** `CandleRepo.list` dedupe `keep_last` (commit `30b4654`).  
**Verdict:** REJECT (unchanged — null model by design).

## Superseded for numeric null-band use (retain for history)

| source | integrity | do not use for |
|---|---|---|
| `backtests/CAMPAIGN_011_random_entry_anchor/` | LIKELY_CONTAMINATED | null-band centre, trade-count parity |
| [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) | pre-fix SQLite | headline metrics |
| [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §1 table | pre-fix numbers | verbatim floor values |

Binding **comparison protocol** (indistinguishability band ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair, meaningful-improvement margins, anti-overfit rules) in `CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md` **remains in force** — only the **centre metrics** move to the deduped canonical rollup.

## Headline metric migration

| metric | contaminated (superseded) | deduped canonical |
|---|---:|---:|
| total_trades | 1,177 | **1,180** |
| aggregate expectancy R | −0.0024 | **−0.0029** |
| aggregate return % | −0.53 | **−0.68** |
| profit_factor | 0.91 | **0.89** |
| pairs_positive | 3 / 7 | 3 / 7 |
| fold_pass_rate | 0 / 8 | 0 / 8 |

Per-fold expectancy R (deduped): **mean −0.0027**, **std 0.0479**.

## Downstream campaigns

| campaign | null comparison status |
|---|---|
| CAMPAIGN_012 | prior comparison used contaminated null — **re-evaluate** against deduped canonical |
| CAMPAIGN_013 | same |
| CAMPAIGN_014 | same |
| CAMPAIGN_015 deduped | anti-overfit re-checked vs deduped null in sprint Phase 5 |

## Unchanged

- No strategy approved (`approved: []`).
- Paper / demo / live blocked.
- CAMPAIGN_011 REJECT verdict (null diagnostic anchor).
