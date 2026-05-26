# CAMPAIGN_014 — Post-Dedup Null Reference Refresh

**Sprint:** POST_DEDUP_NULL_REFERENCE_REFRESH_001  
**Date:** 2026-05-25  
**Campaign:** CAMPAIGN_014 / `calendar_event_window_anomaly 0.1.0-c014`

## Status

| field | value |
|---|---|
| Prior verdict | **REJECT (direction-of-trade falsification)** |
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

## CAMPAIGN_014 metrics (existing rollup — LIKELY_CONTAMINATED)

Source: [`backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/results.json`](../../backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/results.json) and [`CAMPAIGN_014_EVIDENCE_SUMMARY.md`](CAMPAIGN_014_EVIDENCE_SUMMARY.md).

| metric | CAMPAIGN_014 (pre-fix) |
|---|---:|
| aggregate expectancy R | −0.14774 |
| aggregate return % | −30.85 |
| profit factor | 0.00 |
| pairs positive | 0 / 7 |
| total trades | 720 |
| turnover budget | PASS (720 ≤ 800; 1,240 raw signals ≤ 1,500) |

## Gap vs deduped null (compact rollup recompute)

Deduped null indistinguishability band: ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair.

| axis | deduped null | band | CAMPAIGN_014 | inside band? |
|---|---:|---|---:|:---:|
| aggregate expectancy R | −0.0029 | [−0.0079, +0.0021] | **−0.14774** | NO (~0.145 R below band) |
| profit factor | 0.89 | [0.79, 0.99] | **0.00** | NO (~0.79 below band) |
| aggregate return % | −0.68 | [−2.68, +1.32] | **−30.85** | NO (~28 pp below band) |
| pairs positive | 3 / 7 | [2, 4] | **0 / 7** | NO (2 below band) |

**Classification:** **REJECT (direction-of-trade falsification)** — uniquely among C012/C013/C014, turnover budget was intact; failure is direction-of-trade, not trade-count amplification.

## Did the conclusion change?

**No.** CAMPAIGN_014 was REJECT with expectancy −0.148 R vs contaminated null −0.0024 R. Against deduped null −0.0029 R the gap is −0.1448 R — still ~29× the half-band, worse direction. Turnover and fixture-coverage gates remain PASS in the pre-fix rollup; the REJECT rationale (post-event bar tends to **continue** event direction, not revert) is unchanged.

## Caveats

- CAMPAIGN_014 metrics are **LIKELY_CONTAMINATED**. Event fixture coverage and trade counts may shift on deduped candles; this refresh does not re-run the walk-forward.
- Fixture date-verification audit caveats from the original sprint remain in force.
- A **deduped CAMPAIGN_014 rerun** remains required for validated post-dedup rejection certification.

## Prior docs with superseded null centre

**SUPERSEDED_NULL_REFERENCE** for numeric null-floor values:

- [`CAMPAIGN_014_EVIDENCE_SUMMARY.md`](CAMPAIGN_014_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md) §null baseline table

## References

- [`CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`](CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md)
- [`POST_DEDUP_RERUN_BACKLOG.md`](POST_DEDUP_RERUN_BACKLOG.md)
