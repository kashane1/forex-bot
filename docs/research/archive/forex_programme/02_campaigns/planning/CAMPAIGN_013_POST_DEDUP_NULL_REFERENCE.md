# CAMPAIGN_013 — Post-Dedup Null Reference Refresh

**Sprint:** POST_DEDUP_NULL_REFERENCE_REFRESH_001  
**Date:** 2026-05-25  
**Campaign:** CAMPAIGN_013 / `cross_pair_currency_strength_rotation 0.1.0-c013`

## Status

| field | value |
|---|---|
| Prior verdict | **REJECT** |
| Post-dedup null refresh verdict | **REJECT (unchanged)** |
| Campaign evidence integrity | **LIKELY_CONTAMINATED** (pre-fix SQLite) |
| Old null comparison | **SUPERSEDED_NULL_REFERENCE** |
| Clean post-dedup certification | **Requires deduped campaign rerun** |

## Canonical null baseline (comparison centre)

Source: [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)

| metric | deduped canonical |
|---|---:|
| aggregate expectancy R | −0.0029154071495408797 |
| per-fold expectancy mean / std | −0.0027 / 0.0479 |
| aggregate return % | −0.68 |
| profit factor | 0.89 |
| pairs positive | 3 / 7 |
| total trades | 1,180 |

Supersedes contaminated null centre: −0.0024 R, 1,177 trades, −0.53 % return, PF 0.91.

## CAMPAIGN_013 metrics (existing rollup — LIKELY_CONTAMINATED)

Source: [`backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.json`](../../backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.json) and [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md).

| metric | CAMPAIGN_013 (pre-fix) |
|---|---:|
| aggregate expectancy R | −0.0564 |
| aggregate return % | −113.36 |
| profit factor | 0.000 |
| pairs positive | 1 / 7 |
| total trades | 7,940 |

## Gap vs deduped null (compact rollup recompute)

Indistinguishability band (binding protocol unchanged): ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair around the null centre.

| axis | deduped null | CAMPAIGN_013 | gap (C013 − null) | inside band? |
|---|---:|---:|---:|:---:|
| aggregate expectancy R | −0.0029 | −0.0564 | **−0.0535** | NO (~11× half-band, worse) |
| profit factor | 0.89 | 0.000 | **−0.890** | NO (~9× half-band, worse) |
| aggregate return % | −0.68 | −113.36 | **−112.68 pp** | NO (~56× half-band, worse) |
| pairs positive | 3 / 7 | 1 / 7 | **−2 pairs** | boundary (worse direction) |

**Classification:** **REJECT** — catastrophically worse than null on every binding axis; not `REJECT_INDISTINGUISHABLE_FROM_NULL`.

## Did the conclusion change?

**No.** CAMPAIGN_013 was the worst-performing real candidate by return and trade count. Re-centering the null floor from −0.0024 R to −0.0029 R changes the expectancy gap by only ~0.0005 R — immaterial relative to CAMPAIGN_013's −0.0535 R deficit. Verdict remains **REJECT**.

## Caveats

- CAMPAIGN_013 walk-forward metrics were produced on **pre-fix SQLite**. This refresh updates the **null reference only**; absolute CAMPAIGN_013 metrics are not re-certified on deduped candles.
- Cross-pair runner contract was satisfied on all 8 folds (integration REJECT is on inherited gates, not BLOCKED).
- A **deduped CAMPAIGN_013 rerun** remains required for validated post-dedup rejection certification.

## Prior docs with superseded null centre

**SUPERSEDED_NULL_REFERENCE** for numeric null-floor values:

- [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md) §9

## References

- [`CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`](CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md)
- [`POST_DEDUP_RERUN_BACKLOG.md`](POST_DEDUP_RERUN_BACKLOG.md)
