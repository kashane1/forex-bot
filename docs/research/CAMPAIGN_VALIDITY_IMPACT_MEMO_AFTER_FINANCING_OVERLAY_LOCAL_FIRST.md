# Campaign Validity Impact — After Financing Overlay (Local-First)

**Date:** 2026-05-27  
**Sprint:** `infra-observed-cost-financing-overlay-local-first-001`

## Overlaid ledgers

C019 (train+validation base), C016 weekly folds base, C017 weekly folds base, C008 deduped forensic train — **synthetic_fixture** stress rates.

## Financing data type

**Synthetic conservative stress** — not broker-observed. Manual fixture mode uses committed JSON schedules also labeled synthetic.

## Campaign families most affected

1. **H4 mean-reversion multi-day** (C008, C019) — ~0.08R average drag under stress
2. **Weekly rebalance** (C016, C017) — ~0.04–0.05R drag; gross already weak
3. **Short-hold / failed breakout** (C015) — lower sensitivity; not overlaid in reference run

## Multi-day / weekly evidence downgrade?

**Trustworthiness of gross R for holds > 3 days should be downgraded** for research interpretation until observed financing is captured. This is an **overlay-required** caveat, not a formal verdict token change.

## Observed financing before further consideration?

**Yes** for any future promotion review of weekly/overnight/multi-day strategies. Infrastructure overlay proves material drag; observed capture sprint is the next data step.

## C019 materially affected?

**Interpretation:** Gross train/validation expectancy was already near zero/negative; synthetic financing drag (~0.08R) reinforces that carry was understated. **Verdict unchanged: REJECT.** Fill-timing (`next_bar_open`) remains the larger validity WARN than financing for C019.

## Short-hold / no-campaign campaigns

Largely **unaffected** by financing overlay magnitude; spread/slippage and fill timing dominate.

## Verdict changes justified?

**None.** Do not rewrite REJECT → PASS or alter manifest verdicts from synthetic financing.

## No-approval statement

No strategy approved. CAMPAIGN_020 not created.
