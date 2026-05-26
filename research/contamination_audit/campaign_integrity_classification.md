# Campaign Integrity Classification

**Generated:** 2026-05-26T05:22:14Z
**Dedupe fix commit:** `30b4654`

## Summary

| status | campaigns |
|---|---:|
| BLOCKED_NO_RUN | 1 |
| DEDUP_SAFE | 2 |
| LIKELY_CONTAMINATED | 11 |
| NULL_BASELINE_REQUIRES_RERUN | 1 |

## Per-campaign

### CAMPAIGN_001 — DEDUP_SAFE

- **Verdict (unchanged):** SYNTHETIC_NOT_EVIDENCE
- **Valid for decisions:** True
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** Synthetic harness validation on data/campaign.sqlite3; not OANDA H4 duplicate issue.

### CAMPAIGN_002 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** Real OANDA H4 via pre-fix CandleRepo on campaign_002.sqlite3; REJECT verdict likely directionally stable but metrics unverified post-dedupe. Parity CSV lane safe.

### CAMPAIGN_003 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** Same pre-fix SQLite bespoke path as CAMPAIGN_002; REJECT; low rerun priority.

### CAMPAIGN_004 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** Pre-fix SQLite bespoke; strongly negative REJECT; magnitude may shift post-dedupe.

### CAMPAIGN_005 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** DIAGNOSTIC
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** Diagnostic benchmarks on pre-fix SQLite; random-entry baseline may shift.

### CAMPAIGN_006 — BLOCKED_NO_RUN

- **Verdict (unchanged):** REJECT_NO_VALID_RESULT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** D1 infrastructure blocker; no valid bespoke H4 duplicate exposure for verdict.

### CAMPAIGN_007 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** Pre-fix SQLite bespoke H4; REJECT on train/validation.

### CAMPAIGN_008 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** Pre-fix SQLite; validation-positive metrics unverified post-dedupe.

### CAMPAIGN_009 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** Pre-fix SQLite; validation-positive metrics unverified post-dedupe.

### CAMPAIGN_010 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** False
- **Why:** Walk-forward on pre-fix SQLite; REJECT; metrics and gate counts may shift.

### CAMPAIGN_011 — NULL_BASELINE_REQUIRES_RERUN

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** True
- **Rerun required:** True
- **Why:** Null-model anchor on pre-fix SQLite (−0.0024 R, 1177 trades). Deduped rerun artifact exists locally (−0.0029 R, 1180 trades) but must be promoted as canonical before null comparisons for CAMPAIGN_012–015 remain valid.

### CAMPAIGN_012 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** True
- **Why:** Pre-fix SQLite; REJECT vs null baseline uses contaminated CAMPAIGN_011 metrics.

### CAMPAIGN_013 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** True
- **Why:** Pre-fix SQLite; null comparison invalid until CAMPAIGN_011 deduped baseline canonical.

### CAMPAIGN_014 — LIKELY_CONTAMINATED

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** False
- **Mark superseded:** False
- **Rerun required:** True
- **Why:** Pre-fix SQLite; null comparison invalid until CAMPAIGN_011 deduped baseline canonical.

### CAMPAIGN_015 — DEDUP_SAFE

- **Verdict (unchanged):** REJECT
- **Valid for decisions:** True
- **Mark superseded:** True
- **Rerun required:** False
- **Why:** Original bespoke SUPERSEDED BY DEDUP RERUN; canonical evidence is deduped folder (backtests/CAMPAIGN_015_failed_breakout_reversal_deduped). Deduped exp_r −0.0101, WITHIN_NULL, REJECT.

