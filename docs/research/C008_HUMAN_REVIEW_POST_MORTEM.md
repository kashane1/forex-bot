# C008 Human Review Post-Mortem

**Diagnostic only** — `strategy_evidence: false`

## Why C008 remains rejected / research-only

1. **Pre-committed gate failure:** train expectancy **−0.017 R** vs required **≥ 0**. Bright-line rule committed before the run; not relaxed post-hoc.
2. **Test lockbox never opened:** 2025–2026 window not run because screening failed.
3. **Research-only cap:** mean-reversion tail risk; marathon verdict capped at REVISE even if numeric gates passed.
4. **Evidence integrity flag:** dedup contamination audit classifies C008 as LIKELY_CONTAMINATED — any future use requires rerun, not promotion from this sprint.
5. **No approval path:** `configs/approved_strategies.yaml` remains `approved: []`.

## Why validation strength is still interesting

- Validation (2023–2024, never used for design): **+0.172 R**, PF **1.29**, **6/6 pairs positive**.
- Survived **2× cost stress** on full window (+0.027 R).
- Beat random-entry benchmark on every split — unlike trend/breakout campaigns (C002–C004, C007).
- Only campaign in the archive with broad validation-era positivity in the mean-reversion family.

This makes C008 the **strongest clue**, not an approval.

## Why train gate failure matters

- Train was **flat-negative** (−0.017 R), not deeply negative like trend campaigns.
- But the gate is **train ≥ 0** — a deliberate anti-overfit screen. Validation-only positivity without train support is exactly the failure mode the marathon guards against.
- Trade anatomy shows train damage concentrated in **USD_CAD** (−0.382 R) and **stop exits** (153/156 losers stopped out).
- **Monday/Tuesday** and **london_ny_overlap** sessions weak on train.

## Why C009 did not rescue it

- Single change: **midline-target exit** (hypothesis: time-stop caps winners; mean exit fixes train).
- Result: train **worsened** (−0.062 R vs −0.017 R); validation similar (+0.170 vs +0.172 R).
- Midline exit increased win rate but **did not** fix train expectancy — hypothesis **falsified** for this parameterization.
- C009 still **REJECT**; no test window opened.

## What cannot be concluded

- Cannot conclude C008 is profitable or approved.
- Cannot conclude validation results will replicate in 2025–2026 test window (never run).
- Cannot conclude cross-asset or confluence overlays provide tradable filters without new pre-registered campaign.
- Cannot retune ADX, z-score, stops, or sessions based on validation winners.

## What would be required before any future mean-reversion campaign

See `FUTURE_MEAN_REVERSION_RESEARCH_GATE.md`. Minimum:

- **New campaign ID** (not C008/C009 retune).
- Fresh pre-commit with explicit market-structure thesis.
- Train ≥ 0 and validation gates re-declared **before** run.
- Cost atlas + FRED features + confluence role pre-declared.
- Beat-null requirement, 2× stress, financing treatment if holds cross rollover.
- Evidence integrity rerun if promotion ever considered.
- Separate human promotion sprint — not this diagnostic.

## No approval / paper / live

- No strategy approved.
- CAMPAIGN_018 not created.
- Paper/demo/live remain blocked.
- Executor/broker unchanged.

## Disclaimer

Diagnostic post-mortem only. Not strategy evidence.
