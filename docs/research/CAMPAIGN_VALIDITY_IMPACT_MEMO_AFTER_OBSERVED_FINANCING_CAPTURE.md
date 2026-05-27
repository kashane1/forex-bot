# Campaign Validity Impact — After Observed Financing Capture

**Date:** 2026-05-27  
**Sprint:** `infra-observed-financing-capture-readonly-002`

## Capture succeeded?

**Partial** — infrastructure and safety path complete; **no new observed financing rows** committed (credentials absent in runner; prior practice history empty).

## Observed data sufficient?

**No** — insufficient for rate inference or observed overlay on reference ledgers.

## Synthetic overlay vs observed

Synthetic stress (~0.04–0.08R drag) remains **inconclusive vs practice** until `DAILY_FINANCING` transactions are captured. Treat synthetic as conservative stress, not calibrated truth.

## C019 impact

**No verdict change** (REJECT). Interpretation unchanged: gross metrics understate carry; `next_bar_open` fill timing dominates validity vs financing for C019.

## Weekly / multi-day families

Continue to treat gross R as **optimistic** without observed financing. Promotion review should require:

1. Declared `financing_mode` in precommit
2. Observed practice capture OR documented empty-account rationale
3. Financing overlay on trade ledger

## Historical verdict changes?

**None justified.**

## No-approval statement

No strategy approved. CAMPAIGN_020 not created.
