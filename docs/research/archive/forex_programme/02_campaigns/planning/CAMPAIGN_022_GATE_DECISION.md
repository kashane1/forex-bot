# CAMPAIGN_022 — Gate Decision

**Date:** 2026-05-28 · **Strategy:** `h4_h1_pullback_resolution_entry 0.1.0-c022`
**Decision:** **REJECT** · **Test lockbox:** NOT opened · **Approval:** none

## Discipline applied (frozen, no exceptions)

- No validation rescue if train fails.
- No gate softening after seeing results.
- No retuning before or after any split.
- No merging of the C023 ADX-22 sibling threshold into C022.

## Binding decision path

1. **Train gate (binding first):** train expectancy = **−0.1042R** < 0 → **FAIL**.
2. Train fail is **terminal** → classify **REJECT** immediately.
3. Do **not** run the test window. Test lockbox **remains closed**.
4. Validation metrics are reported for completeness only — they do **not** rescue a failed train
   gate, and in any case also fail (val exp −0.1663R, PF 0.690, 1/7 pairs positive, 2× stress −0.2468R,
   does not beat the C011 null).

## Gate checks (all recorded; none softened)

| gate | result |
|---|---|
| train expectancy ≥ 0 | ❌ (−0.1042) |
| validation expectancy > 0 | ❌ (−0.1663) |
| validation PF ≥ 1.05 | ❌ (0.690) |
| validation trades ≥ 150 | ✅ (1027) |
| validation pairs positive ≥ 4/7 | ❌ (1) |
| 2× cost-stress validation exp ≥ 0 | ❌ (−0.2468) |
| beat C011 null by +0.010R | ❌ |
| Backtrader parity PASS | n/a — not run (lockbox already closed by train fail) |

## Outcome

- **Verdict: REJECT.** Maximum attainable status would have been RESEARCH_PASS — never approval —
  and even that is unreachable here.
- `configs/approved_strategies.yaml` remains `approved: []`. Paper/demo/live blocked.
- No parameter was changed at any point; the frozen `0.1.0-c022` set produced this result as-is.
