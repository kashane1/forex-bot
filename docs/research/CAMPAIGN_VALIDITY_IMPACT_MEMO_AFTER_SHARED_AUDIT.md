# Campaign Validity Impact Memo — After Shared Infrastructure Audit 001

**Date:** 2026-05-26  
**Branch:** `infra-shared-signal-and-mtf-confluence-audit-001`  
**Does not rewrite any campaign verdict.**

## Shared layers summary

| Layer | Status | Impact on prior campaigns |
|-------|--------|---------------------------|
| Candle / D1AGG | PASS | Low risk for H4 + D1AGG campaigns |
| MTF alignment | WARN | No systemic lookahead found in audited paths; new strategies need shared adapter |
| Indicators | WARN | RSI warmup fillna(50); Donchian/ATR/z-score OK |
| Signal contract | WARN | Metadata gaps only — not evidence of false fills |
| Fill price sides | PASS | Long/short bid/ask rules consistent |
| Fill timing default | WARN | `signal_bar_close` inflates breakout campaigns |
| Exit ordering | PASS | C019 thesis priority matches precommit tests |
| Cost / financing | WARN | Financing often unmodeled — overnight strategies understated cost |
| Risk sizing | PASS | Shared math stable |
| Parity | WARN | Backtrader good; Lean incomplete |

## Could failed strategies still be failed?

**Yes.** No shared-layer bug was found that would plausibly **create** broad false edge across families. Known issues (optimistic fill timing, financing gaps) **hurt** performance vs live — they do not explain rejected campaigns turning into winners.

## Could edge be hidden?

**Possibly mild upward bias** from `signal_bar_close` on fast signal bars — would make weak campaigns look slightly better, not worse. `next_bar_open` reruns are the conservative check.

## CAMPAIGN_019 (mean_reversion_thesis_invalidation)

- C019 artifacts present (committed); **not modified** this sprint.
- Exit priority for thesis_invalidation: **PASS** (existing unit tests).
- **Rerun not required** for infrastructure audit alone unless a future fix changes engine exit ordering or z-score definition.
- C019 verdict interpretation unchanged.

## Campaigns that may need rerun (conservative)

| Trigger | Suggested action |
|---------|------------------|
| Future fix to Donchian/z-score/ATR | Rerun affected families only |
| Switch default to `next_bar_open` repo-wide | Rerun all breakout/trend evidence |
| Add financing overlay to multi-day holds | Rerun hold > 5 day strategies |
| New shared MTF adapter changing D1AGG join | Rerun `regime_switcher` scaffold only |

## Future campaigns

- Block **native OANDA D1** (already invalid).
- Require `fill_timing` declaration in pre-commit.
- Prefer `next_bar_open` for new approval-bound evidence.
- Do not start CAMPAIGN_020 until human authorizes a new strategy sprint.

## Bugs found

**No FAIL-class production bugs** in shared layers this sprint. Findings are **WARN**-level documentation gaps (RSI fill, MTF adapter absence, optimistic timing default, financing).

## No approval statement

This memo and the parent audit **do not** approve any strategy for paper, demo, or live trading.

## Recommended next sprint

1. **Execution-realism sprint:** pin `next_bar_open` for one reference campaign + compare delta  
2. **Shared `htf_align` module** + migrate regime switcher  
3. **Observed financing overlay** for weekly/overnight holds  
4. Optional: additive Signal provenance fields without breaking artifact hashes
