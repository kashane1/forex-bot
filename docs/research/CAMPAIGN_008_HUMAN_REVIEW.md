# CAMPAIGN_008 Range Mean-Reversion — Human Review

**Date of review:** 2026-05-22
**Decision:** authorize a single focused follow-up — **CAMPAIGN_009** —
under a fresh, independent pre-commit. This is option (1) of the two
choices recorded in `docs/research/RESEARCH_MARATHON_001_NO_GO.md`.
**Status of CAMPAIGN_008 itself:** **unchanged — REJECT.** This document
does not reopen, re-grade, or overwrite CAMPAIGN_008. Its report,
pre-commit spec, config, and run artifacts are immutable.

---

## 1. Why this document exists

Research Marathon 001 closed **NO-GO** — a valid negative-evidence
result. Its single near-miss, CAMPAIGN_008 (regime-filtered H4 mean
reversion), was explicitly *handed to human review* rather than
auto-advanced, because the marathon's rules cap it at REVISE and forbid
the marathon supervisor from acting further.

The NO-GO note named exactly two acceptable next steps:

1. Authorize a focused CAMPAIGN_009 that adds a proper midline-target
   exit to `mean_reversion` and re-screens under a fresh pre-commit.
2. Decline further research.

This review records the decision to take **option 1**, and the
reasoning behind it, so that CAMPAIGN_009 can never be mistaken for
post-hoc tampering with CAMPAIGN_008's verdict.

## 2. Why CAMPAIGN_008 did not pass

CAMPAIGN_008 is REJECT for one specific, pre-committed reason and no
other:

- The CAMPAIGN_008 pre-commit set a **screening gate** requiring, among
  other things, **train expectancy ≥ 0**.
- The train split (2020–2022) came in at **−0.017 R** (profit factor
  1.02) — flat within noise, but on the wrong side of a bright line.
- Per test-window discipline, a failed screening gate means the
  2025–2026 reported test window is **not opened**. It was not.
- The gate was **not relaxed** after the result was seen. Relaxing
  "train ≥ 0" to "train ≥ −0.02" to let CAMPAIGN_008 through would have
  been precisely the post-hoc rationalization the pre-commit discipline
  exists to prevent. It was not done, and it is not being done now.

CAMPAIGN_008 therefore stands as REJECT. Nothing below changes that.

## 3. Why regime-filtered mean reversion still merits one campaign

CAMPAIGN_008 is REJECT, but it is **categorically different** from the
marathon's other rejections, and from CAMPAIGN_002/003/004:

- **Validation (2023–2024, never used to design the strategy):**
  **+0.172 R, profit factor 1.29, +1.04 %, 6 of 6 pairs positive.** A
  broad, clean positive on an out-of-design split.
- **Cost-stress survival:** expectancy stays positive at base
  (+0.069 R), 1.5× (+0.040 R) and 2.0× (+0.027 R) cost regimes.
- **Train was flat, not a loss:** −0.017 R / PF 1.02 — unlike the
  −0.07 to −0.16 R trend/breakout/pullback campaigns.
- It is the **only** strategy in the project (CAMPAIGN_002–008) that
  beats the CAMPAIGN_005 random-entry benchmark (−0.095 R) on *every*
  split.
- It is consistent with the CAMPAIGN_005 diagnostic: H4 majors were
  choppy / range-bound across 2020–2026 (efficiency ratio 0.24) — the
  natural habitat of a regime-filtered reversion strategy and the exact
  conditions that broke the trend campaigns.

This is the single direction in the tested universe that has shown a
real, cost-survivable signal. One more disciplined campaign is a
proportionate response — and the marathon's NO-GO note explicitly
invited it.

## 4. The weakness CAMPAIGN_009 targets — and the honest caveat

CAMPAIGN_008's known structural weakness: **the backtest engine had no
midline-target exit.** A reversion trade could only leave via the hard
ATR stop or the 40-bar time stop. The 40-bar timer is a coarse proxy
for "the reversion completed" — a real mean-reversion system exits
*at the mean*.

**Honest caveat, stated up front:** the CAMPAIGN_008 full-window
trade-diagnostics showed time-stop exits averaging **+1.89 R**
(92.7 % win rate). A midline-target exit cuts those trades shorter, so
it is **not self-evident that it improves results** — it may bank
smaller, more frequent wins, or it may cap winners and hurt. That
uncertainty is exactly why CAMPAIGN_009 must *test* the change against
fresh pre-committed gates rather than assume it.

## 5. What CAMPAIGN_009 changes — exactly one predeclared rule

CAMPAIGN_009 makes **one** predeclared change and freezes everything
else:

| dimension | CAMPAIGN_008 | CAMPAIGN_009 | changed? |
|---|---|---|---|
| Strategy version | `mean_reversion 0.1.0-c008` | `mean_reversion 0.2.0-c009` | yes (new version) |
| Exit model | hard stop **or** 40-bar time stop | hard stop **or midline target or** 40-bar time stop | **yes — the one rule change** |
| Entry: ADX regime gate | ADX-14 < 20 | ADX-14 < 20 | no |
| Entry: z-score thresholds | ±2.0 | ±2.0 | no |
| Entry: RSI confirmation | <35 / >65 | <35 / >65 | no |
| Hard stop | 1.5 × ATR-14 | 1.5 × ATR-14 | no |
| Time stop | 40 bars | 40 bars | no |
| risk_per_trade | 0.25 % | 0.25 % | no |
| Universe / timeframe | 6 majors / H4 | 6 majors / H4 | no |

The midline target is the **rolling mean of close over `zscore_lookback`
bars** — the exact level the z-score is measured against, i.e. the
target is "z-score reverts to zero." It is opt-in behind a `midline_exit`
config flag: with the flag off, the emitted signal is byte-identical to
CAMPAIGN_008, so CAMPAIGN_008 remains exactly reproducible. No
entry/regime parameter is tuned.

## 6. Why this is a new pre-committed hypothesis, not gate relaxation

This is the governance crux. CAMPAIGN_009 is a legitimate new
hypothesis, **not** a post-hoc loosening of CAMPAIGN_008:

1. **CAMPAIGN_008's gate is untouched.** "train ≥ 0" still stands.
   CAMPAIGN_008 is still REJECT. No prior artifact is edited.
2. **CAMPAIGN_009 tests a different strategy.** `0.2.0-c009` has
   materially different exit behavior. It is not "CAMPAIGN_008 with a
   softer gate" — it is a different system that must prove itself.
3. **A fresh, independent pre-commit** (`CAMPAIGN_009_PRECOMMIT.md`) is
   written and committed *before* the campaign runs. The gates are
   fixed in advance, in git history, ahead of any result.
4. **The new gates are stricter, not looser.** CAMPAIGN_009 requires
   validation expectancy **strictly > 0** (CAMPAIGN_008 allowed ≥ 0),
   and *adds* a stress_2× validation gate and a financing-stressed
   validation gate that CAMPAIGN_008 did not have. The 2025–2026 test
   window stays a sealed lockbox; even the full-window descriptive run
   is deferred behind the screening gate.
5. **Train must independently clear ≥ 0 again.** CAMPAIGN_009 re-screens
   from scratch. The CAMPAIGN_008 validation result is *not* assumed or
   carried over — if c009's train is negative, c009 is REJECT, full
   stop, exactly as c008 was.
6. **The post-hoc move is the one explicitly NOT taken.** Re-running
   CAMPAIGN_008 unchanged with a relaxed train gate would be
   rationalization. CAMPAIGN_009 instead changes the *strategy*, writes
   *new* gates, and earns or fails its verdict on *new* evidence.

## 7. Scope and ceiling

- CAMPAIGN_009's **best attainable verdict is PAPER-TRADE-ONLY.** It can
  never recommend live trading.
- The strategy remains `paper_only = True`.
- Financing remains **unmodeled in-engine** — a conservative stress
  overlay only, and an unconditional hard blocker for any live
  consideration, independent of any backtest result.
- A NO-GO (REJECT) outcome for CAMPAIGN_009 is an equally acceptable,
  valid result. The campaign is designed to produce honest evidence,
  not a desired verdict.

## 8. References

- Pre-commit: `docs/research/CAMPAIGN_009_PRECOMMIT.md`
- Marathon close-out: `docs/research/RESEARCH_MARATHON_001_NO_GO.md`
- CAMPAIGN_008 report: `backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md`
- CAMPAIGN_008 pre-commit: `docs/research/CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md`
- CAMPAIGN_009 report (produced by the campaign): `backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md`
