# CAMPAIGN_012 — Post-Dedup Null Reference Refresh

**Sprint:** POST_DEDUP_NULL_REFERENCE_REFRESH_001  
**Date:** 2026-05-25  
**Campaign:** CAMPAIGN_012 / `regime_switcher_atr_percentile 0.1.0-c012`

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

## CAMPAIGN_012 metrics (existing rollup — LIKELY_CONTAMINATED)

Source: [`backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json`](../../backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json) and [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md).

| metric | CAMPAIGN_012 (pre-fix) |
|---|---:|
| aggregate expectancy R | −0.0521 |
| aggregate return % | −43.52 |
| profit factor | 0.034 |
| pairs positive | 1 / 7 |
| total trades | 3,726 |

## Gap vs deduped null (compact rollup recompute)

Indistinguishability band (binding protocol unchanged): ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair around the null centre.

| axis | deduped null | CAMPAIGN_012 | gap (C012 − null) | inside band? |
|---|---:|---:|---:|:---:|
| aggregate expectancy R | −0.0029 | −0.0521 | **−0.0492** | NO (~10× half-band, worse) |
| profit factor | 0.89 | 0.034 | **−0.856** | NO (~9× half-band, worse) |
| aggregate return % | −0.68 | −43.52 | **−42.84 pp** | NO (~21× half-band, worse) |
| pairs positive | 3 / 7 | 1 / 7 | **−2 pairs** | boundary (worse direction) |

**Classification:** **REJECT** — not `REJECT_INDISTINGUISHABLE_FROM_NULL` (divergence is far outside the symmetric band in the worse direction).

## Did the conclusion change?

**No.** CAMPAIGN_012 was REJECT against the contaminated null (−0.0024 R) and remains REJECT against the deduped canonical null (−0.0029 R). Shifting the null centre by ~0.0005 R does not move CAMPAIGN_012 anywhere near the indistinguishability band or the meaningful-improvement margin (+0.0524 R → ≥ 0.05 R).

## Caveats

- CAMPAIGN_012 walk-forward metrics were produced on **pre-fix SQLite** (duplicate-candle contamination). This refresh recomputes the **null-reference gap only**; it does **not** certify CAMPAIGN_012's absolute metrics on deduped candles.
- A **deduped CAMPAIGN_012 rerun** remains required for validated post-dedup rejection certification (see [`POST_DEDUP_RERUN_BACKLOG.md`](POST_DEDUP_RERUN_BACKLOG.md)).

## Prior docs with superseded null centre

The following retain historical value but their numeric null-floor references (−0.0024 R, 1,177 trades, −0.53 %, PF 0.91) are **SUPERSEDED_NULL_REFERENCE**:

- [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md) §8

## References

- [`CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`](CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md)
- [`CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md) (this doc)
