# C1 High-Volatility Front-Gate — Decision (Phase 6)

**Status:** DECISION (front-gate screen verdict)
**Date:** 2026-05-29
**Branch:** `research-c1-high-volatility-frontgate-001`
**Freeze state:** intact — this decision creates **no** campaign, **no** strategy,
**no** approval, and enables **no** paper/demo/live.

---

## Verdict

# `FAIL_FRONT_GATE`

The volatility-conditioned `C1_trend_cont_long` fade is **statistically real and
C1-specific** but **does not survive realistic execution cost**, and its economic
weight is **concentrated** rather than broadly persistent. Applying the
**pre-committed** Phase-1 rule, it fails the front gate on the cost criterion.

## Gate-by-gate (against the frozen Phase-1 rule)

| Gate (frozen threshold) | Result | Pass? |
|---|---|---|
| **Cost:** `net = |mean_ret60| − (spread_hivol + 0.5) ≥ +0.20` on both primaries | EUR_USD −0.36, USD_JPY −0.23 (GBP_USD −1.36); worse at 1.0 stress | **FAIL** |
| **Null:** matched-Z ≤ −2 **and** vol-matched-Z ≤ −2 at 60 min, both primaries | EUR −3.71/−2.76; JPY −3.48/−2.58 | PASS |
| **Adds value:** \|hi-vol mean\| > \|unconditional mean\|, both primaries | yes on all pairs/horizons | PASS |
| **Stability:** ≥4/6 years neg **and** ≥3/4 sessions neg, no year >60%, both primaries | sessions all-neg (pass); years not clean; magnitude concentrated | **BORDERLINE/FAIL** |
| **Generalisation:** GBP_USD same sign **and** net ≥ 0 | sign negative ✓ but net −1.36 and 60-min null fails | **FAIL** |

The frozen rule: *"FAIL_FRONT_GATE if `net < 0` after cost on either primary."*
Both primaries are net-negative → **FAIL**, independently reinforced by the
borderline stability and the cost-defeated, null-failing generalisation pair.

## What actually happened (the honest story)

This screen produced its **strongest-ever evidence that C1 is a genuine factor**:
in the high-volatility regime, the EUR_USD and USD_JPY fades beat not just a
session-matched null but a **volatility-matched** null (−2.76 / −2.58 at 60 min),
proving the reversion is **C1-specific**, not a restatement of "volatile bars
mean-revert." Conditioning on volatility also measurably amplified the reversion
(EUR_USD −1.17 → −1.78; USD_JPY −1.14 → −2.09).

**And it still fails — on cost.** The amplified reversion only just exceeds the
(wider) high-volatility spread (1.09×/1.15× on the primaries; 0.60× on GBP) and
goes **net-negative** once a modest 0.5-pip slippage is charged. The favourable
pockets that made the candidate look promising in validation were
**session-specific** (EUR_USD·London, USD_JPY·Tokyo); the honestly pre-registered
**all-session** high-vol hypothesis blends those with the flat sessions and lands
below the cost wall. Re-adding a session filter now would be the precise post-hoc
optimisation the front gate exists to forbid.

This is the same wall that defeated C026, C029, C031, H16, and H03: a real,
measurable, even null-surviving structural effect whose magnitude is simply
smaller than the cost of trading it on this corpus.

## Consequence — pre-committed lane closure

Per the stop criterion frozen in `C1_HIGH_VOL_HYPOTHESIS.md` §8 and in the C1
factor verdict: a `FAIL` **closes the M1/HTF time-bar confluence directional lane
on this corpus**, joining the retired non-time-bar directional lane. C1 is
catalogued as a **real-but-not-tradable factor** — validated, understood, and
shelved.

**Reopen only** with genuinely new inputs — longer history (10–15y), genuine
**non-USD crosses** (to settle the last residual USD share and supply independent
replications), tighter real execution data, or a **new external thesis** — and
then only via a **fresh pre-registered screen**, never a re-tune of C1.

## No Phase 7

The next-step prompt (Phase 7) is produced **only on `PASS`**. This is a `FAIL`,
so no `NEXT_PROMPT_AFTER_C1_HIGH_VOL_FRONTGATE.md` is created and **no campaign
scaffold is recommended.**

## Hard-rule confirmation

No campaign (no CAMPAIGN_032 or any campaign). No strategy. No entry/exit rules.
No train/validation/test. No parameters optimised (thresholds frozen in Phase 1
before any conditioned number; the result was read against them, not tuned to
them). No strategy approved. Paper/demo/live remain blocked. No OANDA APIs, no
credentials.
