# Campaign Evidence Integrity After Dedupe Fix

**Sprint:** CAMPAIGN_CONTAMINATION_AUDIT_001
**Date:** 2026-05-26

> No strategy verdicts changed to PASS. No approvals granted.

## Executive summary

Duplicate UTC H4 bars in `data/campaign_002.sqlite3` contaminated pre-fix bespoke loads via `CandleRepo.list`. Canonical dedupe (`keep_last`) landed in commit `30b4654`. CAMPAIGN_015 bespoke evidence is **SUPERSEDED BY DEDUP RERUN**.

CAMPAIGN_011 deduped null baseline is **promoted** (`research/null_baselines/campaign_011_deduped_null_baseline.json`). CAMPAIGN_012–014 null comparisons in prior verdict docs remain **pending re-eval** against the deduped floor.

## Classification table

| campaign | integrity status | verdict | valid | superseded | rerun |
|---|---|---|:--:|:--:|:--:|
| CAMPAIGN_001 | DEDUP_SAFE | SYNTHETIC_NOT_EVIDENCE | yes | no | no |
| CAMPAIGN_002 | LIKELY_CONTAMINATED | REJECT | no | no | no |
| CAMPAIGN_003 | LIKELY_CONTAMINATED | REJECT | no | no | no |
| CAMPAIGN_004 | LIKELY_CONTAMINATED | REJECT | no | no | no |
| CAMPAIGN_005 | LIKELY_CONTAMINATED | DIAGNOSTIC | no | no | no |
| CAMPAIGN_006 | BLOCKED_NO_RUN | REJECT_NO_VALID_RESULT | no | no | no |
| CAMPAIGN_007 | LIKELY_CONTAMINATED | REJECT | no | no | no |
| CAMPAIGN_008 | LIKELY_CONTAMINATED | REJECT | no | no | no |
| CAMPAIGN_009 | LIKELY_CONTAMINATED | REJECT | no | no | no |
| CAMPAIGN_010 | LIKELY_CONTAMINATED | REJECT | no | no | no |
| CAMPAIGN_011 | DEDUP_SAFE | REJECT | no | yes | yes |
| CAMPAIGN_012 | LIKELY_CONTAMINATED | REJECT | no | no | yes |
| CAMPAIGN_013 | LIKELY_CONTAMINATED | REJECT | no | no | yes |
| CAMPAIGN_014 | LIKELY_CONTAMINATED | REJECT | no | no | yes |
| CAMPAIGN_015 | DEDUP_SAFE | REJECT | yes | yes | no |

## CAMPAIGN_015 contaminated vs deduped

| metric | contaminated | deduped |
|---|---:|---:|
| base_exp_r | 0.23 | -0.0101 |
| 2x_exp_r | 0.1909 | -0.0283 |
| total_trades | 164 | 375 |
| anti_overfit | ROBUST_ABOVE_NULL | WITHIN_NULL |

## Per-campaign rationale

### CAMPAIGN_001

Synthetic harness validation on data/campaign.sqlite3; not OANDA H4 duplicate issue.

### CAMPAIGN_002

Real OANDA H4 via pre-fix CandleRepo on campaign_002.sqlite3; REJECT verdict likely directionally stable but metrics unverified post-dedupe. Parity CSV lane safe.

### CAMPAIGN_003

Same pre-fix SQLite bespoke path as CAMPAIGN_002; REJECT; low rerun priority.

### CAMPAIGN_004

Pre-fix SQLite bespoke; strongly negative REJECT; magnitude may shift post-dedupe.

### CAMPAIGN_005

Diagnostic benchmarks on pre-fix SQLite; random-entry baseline may shift.

### CAMPAIGN_006

D1 infrastructure blocker; no valid bespoke H4 duplicate exposure for verdict.

### CAMPAIGN_007

Pre-fix SQLite bespoke H4; REJECT on train/validation.

### CAMPAIGN_008

Pre-fix SQLite; validation-positive metrics unverified post-dedupe.

### CAMPAIGN_009

Pre-fix SQLite; validation-positive metrics unverified post-dedupe.

### CAMPAIGN_010

Walk-forward on pre-fix SQLite; REJECT; metrics and gate counts may shift.

### CAMPAIGN_011

Null-model anchor on pre-fix SQLite (−0.0024 R, 1177 trades). Deduped rerun artifact exists locally (−0.0029 R, 1180 trades) but must be promoted as canonical before null comparisons for CAMPAIGN_012–015 remain valid.

### CAMPAIGN_012

Pre-fix SQLite; REJECT vs null baseline uses contaminated CAMPAIGN_011 metrics.

### CAMPAIGN_013

Pre-fix SQLite; null comparison invalid until CAMPAIGN_011 deduped baseline canonical.

### CAMPAIGN_014

Pre-fix SQLite; null comparison invalid until CAMPAIGN_011 deduped baseline canonical.

### CAMPAIGN_015

Original bespoke SUPERSEDED BY DEDUP RERUN; canonical evidence is deduped folder (backtests/CAMPAIGN_015_failed_breakout_reversal_deduped). Deduped exp_r −0.0101, WITHIN_NULL, REJECT.

