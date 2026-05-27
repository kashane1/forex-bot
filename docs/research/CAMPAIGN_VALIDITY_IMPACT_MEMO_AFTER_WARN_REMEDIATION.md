# Campaign Validity Impact — After WARN Remediation

**Date:** 2026-05-27  
**Sprint:** `infra-shared-audit-warn-remediation-and-next-bar-open-001`

## Fill timing (CAMPAIGN_019 reference)

| Finding | Impact |
|---------|--------|
| `signal_bar_close` reproduces C019 committed metrics | Historical C019 artifacts remain valid **as recorded** |
| `next_bar_open` validation expectancy **0.0175** vs **0.0962** | Validation uplift was **optimistic**; upper-bound evidence |
| Train mixed (+0.034 R for open) | Do not assume uniform optimism; validation is binding |

**Prior `signal_bar_close` campaigns:** Treat as **upper-bound**, especially validation splits.  
**Future approval-bound:** Require `next_bar_open` in precommit.  
**C019 verdict:** **REJECT unchanged.** Rerun optional for narrative only.

## HTF adapter

Shared `htf_align` added; strategies not migrated. No rerun until a strategy refactor adopts it.

## RSI policy

Default legacy preserved. No rerun for C008/C009/C019.

## Signal provenance

Metadata-only; no rerun.

## Financing

Still **WARN** / blocker for multi-day holds. See `OBSERVED_COST_FINANCING_OVERLAY_NEXT_SCOPE.md`.

## No approval

No strategy approved. CAMPAIGN_020 not created.
