# Failed Campaign Meta-Analysis — 001

**Sprint:** `research-edge-discovery-lab-001` · Phase 1
**Date:** 2026-05-24
**Status:** Descriptive synthesis of prior rejections — **does not
alter any campaign verdict.**

---

## 0. Reading guide

This file is a **lessons document**, not a verdict document. It looks
across the rejected and diagnostic campaigns the research archive
contains, pulls one row of headline metrics for each, and distills the
reusable patterns. The point is to make the **edge-discovery lab**
filter out the same kinds of failure modes early, before any new
campaign is scaffolded.

Nothing here re-opens, re-tunes, or rescues a rejected strategy. The
campaign verdicts in
`docs/research/EVIDENCE_MANIFEST.json`,
`docs/research/EVIDENCE_INDEX.md`, and
`docs/research/STRATEGY_STATUS.md` are unchanged.

## 1. Honest scope note: which campaigns this covers

The sprint brief lists `CAMPAIGN_002 / 010 / 011 / 012 / 013 / 014` as
the targets. The committed research archive on this branch contains
**only `CAMPAIGN_001`–`CAMPAIGN_009`**. The verdict / artifact files
for `CAMPAIGN_010`–`CAMPAIGN_014` were not located in
`backtests/`, `docs/research/`, `configs/`, or
`docs/research/EVIDENCE_MANIFEST.json`. The relevant archive checks
(`scripts/validate_research_archive.py`) currently expect exactly nine
campaigns; that validation still passes.

Rather than fabricate metric numbers for campaigns whose artifacts
aren't here, this meta-analysis covers them in two clearly separated
sections:

- §3 **Artifact-backed rows.** Pulled directly from the committed
  campaign reports under `backtests/` and `docs/research/`. Verbatim
  metrics, every cell sourceable.
- §4 **Sprint-brief context for CAMPAIGN_010–014.** The qualitative
  claims the brief states (turnover amplification harms a poor edge;
  H4 post-event mean-reversion was rejected; NFP dominated and lost;
  FOMC produced zero trades because the session filter blocked the
  trigger bar; CAMPAIGN_011 = null baseline). These are recorded as
  *brief-supplied context* and treated as lessons input, not as
  re-derived evidence on this branch. If the actual artifacts land
  later, this table extends naturally.

This is the same convention `STRATEGY_STATUS.md` uses for blocked-vs-
rejected distinctions: the file states what it knows and what it
doesn't, and never silently fills the gap.

## 2. Headline summary table

| campaign | family | window-of-judgement | trades | expectancy R | PF | return % | +pairs / total | source |
|---|---|---|---:|---:|---:|---:|---:|---|
| 002 (H4) | trend_following baseline | untouched-test 2025–2026 | 207 | −0.088 | 0.74 | −0.88 % | 1 / 7 (EUR_USD only) | [CAMPAIGN_002 H4 by-pair table](../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md) |
| 002 (H1) | trend_following baseline | untouched-test 2025–2026 | 247 | −0.206 | 0.44 | −1.74 % | n/a (worst across all H1 splits) | [CAMPAIGN_002 H1 untouched-test row](../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md) |
| 003 | trend_following + ADX-14 gate | untouched-test 2025–2026 | 101 | −0.071 | 0.77 | −0.63 % | 1 / 6 (EUR_USD only) | [CAMPAIGN_003 untouched-test row + by-pair table](../../backtests/CAMPAIGN_003_CONTROLLED_ADX_REPORT.md) |
| 004 | volatility_breakout (ATR compression) | untouched-test 2025–2026 | ~233 | −0.163 | 0.63 | per-pair −0.28% … −2.30 % | 0 / 6 | [CAMPAIGN_004 by-pair table](../../backtests/CAMPAIGN_004_VOLATILITY_BREAKOUT_REPORT.md) |
| 005 | benchmarks (random / always-long / always-short) | full window 2020–2026 | random: 85 / pair / seed × 20 seeds × 6 pairs | random mean −0.095 R | n/a | always-long ranges −18.45 % … +46.31 % | n/a (descriptive) | [CAMPAIGN_005 report](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md) |
| 006 | trend_following on D1 | n/a — D1 untestable | 0 valid runs | n/a | n/a | n/a | n/a | [CAMPAIGN_006 report](../../backtests/CAMPAIGN_006_DAILY_TREND_REPORT.md) |
| 007 | pullback_continuation | train + validation (test never opened) | 568 (val) | −0.166 (val), −0.164 (train) | 0.34–1.08 (val) | per-pair −7.62 % … +0.70 % | 1 / 6 (USD_JPY weakly) | [CAMPAIGN_007 validation by-pair table](../../backtests/CAMPAIGN_007_H4_PULLBACK_REPORT.md) |
| 008 | range mean-reversion (regime-filtered) | train + validation (test never opened) | 138 (val) | +0.172 (val), −0.017 (train) | 1.13–1.63 (val) | per-pair +0.56 % … +1.80 % | 6 / 6 (validation) | [CAMPAIGN_008 validation by-pair table](../../backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md) |
| 009 | mean_reversion + midline-target exit | train + validation (test never opened) | 151 (val) | +0.170 (val), −0.062 (train) | 0.96–1.85 (val) | per-pair −0.14 % … +3.10 % | 4 / 6 (validation) | [CAMPAIGN_009 validation by-pair table](../../backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md) |
| 010 (brief) | *not in archive on this branch* | — | — | — | — | — | — | sprint-brief context only |
| 011 (brief) | *random-entry / null baseline* | — | — | — | — | — | — | sprint-brief context only — the **artifact-backed** null baseline on this branch is CAMPAIGN_005 (random-entry mean **−0.095 R**) |
| 012 (brief) | *not in archive on this branch* — turnover amplification narrative | — | — | — | — | — | — | sprint-brief context only |
| 013 (brief) | *not in archive on this branch* — turnover amplification narrative | — | — | — | — | — | — | sprint-brief context only |
| 014 (brief) | *not in archive on this branch* — H4 post-event mean-reversion (rejected); NFP dominated & lost; FOMC produced 0 trades because the session filter blocked the trigger bar | — | — | — | — | — | — | sprint-brief context only |

Every artifact-backed row in §2 is reproducible against the linked
campaign report. Where a sprint pre-commit kept the test lockbox
closed (CAMPAIGN_007 / 008 / 009), the headline metric is the
*validation* (train+val) row, not a never-opened test row — that is
what the pre-commit gates ran on.

## 3. Per-row notes

### 002 (H4 trend baseline)
- Frozen `0.1.0-baseline-frozen`. Real OANDA H4 across 7 majors.
- Untouched-test by-pair: only `EUR_USD` positive (+0.257 R), the
  remaining six were negative — five of six clearly so (`USD_CHF`
  −0.459 R is the worst). Pair positivity 1 / 7.
- Robustness grid: **0 of 81 combinations** produced positive return.
- Costs monotonically worsen the result (base → 1.5× → 2×).
- Lesson row: the entry rule is broadly negative across the universe;
  there is no single hot pair with a defensible edge, and no parameter
  pocket worth chasing.

### 002 (H1)
- Same strategy, H1 timeframe: untouched-test expectancy −0.206 R, PF
  0.44. ~85% of rejections in CAMPAIGN_002 were spread-family on H1.
- Lesson row: **spread / ATR ratio matters.** At H1, ATR is small and
  spread takes a much larger fraction of each candle. The H4 vs H1
  gap is the cost-structure tell, not the strategy tell.

### 003 (ADX trend filter)
- One pre-committed gate added to 002 baseline: ADX-14 > 25.
- Cut trade count roughly in half (101 vs 207), nudged expectancy
  slightly up (−0.071 vs −0.088) but never above break-even. Pair
  positivity again 1 / 6 (EUR_USD only).
- Lesson row: **conditioning *when* a poor edge fires does not turn
  it positive**; it slightly raises per-trade quality but the entry
  rule is still net-negative.

### 004 (volatility breakout)
- ATR-compression breakout. **0 of 6 pairs positive** on untouched
  test, range −0.000 R (USD_JPY) to −0.322 R (EUR_USD).
- Long-trade expectancy −0.173 R, short-trade expectancy −0.214 R
  (long/short asymmetry small).
- Lesson row: a *different* breakout family also fails; not unique to
  the EMA/Donchian baseline. Three rejected entry families in a row
  argues the problem is structural (cost / timeframe / pair character),
  not the specific entry rule.

### 005 (benchmarks)
- **The null baseline this repo has.** Random entry (matched
  frequency, 20 seeds, fixed 30-bar hold) averages **−0.095 R** across
  the six majors after real spreads + slippage.
- Always-long / always-short and no-trade benchmarks also recorded.
- Market character: efficiency-ratio mean 0.24 (choppy), lag-1 return
  autocorrelation ≈ 0 (no persistence to exploit), abs-return AC(1)
  +0.16–0.22 (volatility clustering).
- Lesson row: the bar a candidate has to clear is *not* "positive" —
  it is **"clearly above the −0.095 R random-entry drag"** on a slice
  with non-trivial *n*.

### 006 (D1 trend, infrastructure-blocked)
- Failed to produce a valid result at all: D1 candles close at the
  17:00 NY rollover, so the timestamp lands inside the session filter
  blackout and the close spread is the rollover spread.
- Infrastructure remediation lives in `infra-foundation-001` (D1AGG
  aggregation), not in a strategy verdict.
- Lesson row: **always classify an infrastructure / data blocker
  separately from a strategy blocker**, or the rejection meta-stats
  poison.

### 007 (H4 pullback continuation)
- Validation expectancy −0.166 R, train −0.164 R. Pair positivity
  1 / 6 (USD_JPY weakly).
- USD_JPY's +0.001 R on validation is essentially zero — *not* an
  edge, despite "looking" positive.
- Lesson row: when only one pair is "barely positive" and the rest
  are clearly negative, that's a concentration artifact, not a
  finding.

### 008 (range mean-reversion, regime-filtered)
- **Validation 6 / 6 pairs positive**, +0.172 R, PF 1.29 — the only
  family that ever produced broadly positive validation behavior.
- Train however was −0.017 R (failing the screening gate). Per the
  pre-commit the test lockbox stayed closed.
- Lesson row: **validation-only positivity is not edge confirmation**;
  it is the most overfitting-prone pattern in the archive. CAMPAIGN_009
  was authorized as a focused follow-up specifically because the
  validation signal was strong enough to be worth one (one) controlled
  attempt — which then failed.

### 009 (mean-reversion + midline exit)
- The single-rule follow-up to 008. Added a midline take-profit;
  everything else frozen.
- Train −0.062 R (worse than 008's train −0.017 R), validation +0.170
  R, 4 / 6 pairs positive on validation.
- Train screening gate failed by a *wider* margin than 008, so the
  rescue hypothesis was falsified and the test window stayed closed.
- Lesson row: **a validation-only signal that fails to lift on train
  with a single rule change is highly unlikely to be real**. Don't
  authorize a third follow-up.

### 010 / 011 / 012 / 013 / 014 (sprint-brief context only)
- Brief states: 011 = random-entry / null baseline; 012 & 013 showed
  turnover amplification made bad edge worse; 014 rejected H4
  post-event mean-reversion with NFP dominating-and-losing and FOMC
  producing zero trades because the session filter blocked the
  trigger bar.
- Artifacts for these campaigns were not located in this branch. The
  lessons are recorded in §5 as cross-cutting context; if the
  artifacts land, this section becomes data-backed too.

## 4. Cross-cutting failure attributions

For each artifact-backed campaign, the dominant cause of failure can
be attributed to one or two of the following categories. The
edge-discovery lab's ranking rules (Phase 4) penalize candidates
showing the same pattern early.

| campaign | turnover / cost burden | financing / carry | pair concentration | directionality (long vs short) | data / infra | family-level structural |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| 002 (H4) | **primary** (PF 0.74 on real spreads) | secondary (stress overlay worsens) | **secondary** (only EUR_USD positive) | minor | — | — |
| 002 (H1) | **primary** (spread/ATR catastrophic) | secondary | — | minor | — | secondary (timeframe wrong for this entry) |
| 003 | secondary (still cost-negative even with half the trades) | secondary | **primary** (only EUR_USD positive, same as 002) | — | — | **primary** (entry-conditioning insufficient) |
| 004 | **primary** | secondary | minor | minor | — | **primary** (different breakout family also broadly negative) |
| 005 | n/a — measurement | n/a | descriptive | descriptive | — | n/a |
| 006 | — | — | — | — | **primary** (D1 untestable in current engine) | — |
| 007 | secondary | minor | **primary** (5/6 deeply negative) | minor | — | **primary** (pullback-continuation entry net-negative) |
| 008 | secondary (val PF healthy, train PF poor) | secondary | medium (USD_CAD is the train weak link) | minor | — | **primary** (train/val gap → likely overfit to val window) |
| 009 | secondary | secondary | medium | minor | — | **primary** (single-rule rescue failed; train fell further) |
| 010 (brief) | — | — | — | — | — | sprint-brief context |
| 011 (brief — null) | n/a — measurement | n/a | n/a | n/a | — | n/a |
| 012 (brief) | **primary** (turnover amplification narrative from brief) | — | — | — | — | — |
| 013 (brief) | **primary** (turnover amplification narrative from brief) | — | — | — | — | — |
| 014 (brief) | — | — | **primary** (NFP dominance) | medium | **primary** (session filter blocked FOMC trigger bar) | medium |

Reading the table: **costs / turnover and pair concentration appear
in nearly every row**. Financing is secondary because it is currently
modeled only as a stress overlay; it has never been the *first* cause
of rejection on this branch. Family-level structural failure (the
entry is broadly wrong) shows up whenever a campaign's pair positivity
is 0/N or 1/N.

## 5. Reusable lessons for future candidate selection

These are the lessons the **edge-discovery lab** must encode in its
ranking rules. They are derived from §3 and §4 above plus the
sprint-brief context for 010–014.

1. **The benchmark to beat is random-entry, not zero.**
   CAMPAIGN_005's random-entry mean is **−0.095 R** across the six
   majors after real costs. A new candidate that "barely breaks even"
   is **worse** than the null — the lab should call that explicitly,
   not call it neutral.

2. **Cost / turnover is the single biggest killer.** Three artifact
   campaigns (002 H1, 002 H4, 004) and the brief's 012 / 013 narrative
   all fail primarily on cost burden. The lab must:
     - report *both* pre-cost and post-cost effect size;
     - report the implied trade-count budget (how many trades it takes
       before realized cost = candidate edge);
     - flag candidates whose post-cost effect is < 20% of pre-cost as
       cost-dominated.

3. **Pair concentration must be diagnosed before being celebrated.**
   002 / 003 / 007 all have the "1 of N pairs positive" pattern; that
   is almost always a noise artifact, not an edge. The lab should
   report:
     - pair-positivity ratio (k of n with positive effect of meaningful
       size);
     - the contribution share of the top pair (if it explains > 70% of
       aggregate effect, flag as single-pair concentration);
     - whether the leading pair on the candidate matches a leading pair
       on the random-entry baseline (which would suggest pair drift,
       not strategy edge).

4. **Validation-only positivity is the highest-overfit pattern in the
   archive.** CAMPAIGN_008 (6/6 val positive, train negative) was the
   most exciting signal in the archive — and the follow-up
   CAMPAIGN_009 falsified it. The lab must:
     - never treat a validation-only effect as graduation-ready;
     - require any candidate to show effect on *at least two
       independent windows* before recommending it for a formal
       pre-commit;
     - explicitly state when a candidate looks "validation-only" and
       refuse to rank it above pre-commit candidates that don't.

5. **Always classify infra blockers separately.** CAMPAIGN_006 is not
   a strategy verdict; it is an infrastructure blocker. The lab's
   ranking output must distinguish "no edge found" from "couldn't be
   tested" so the meta-stats stay honest.

6. **Event-window studies must report dominance and zero-trade
   slices.** Brief context for 014: NFP dominated and lost, FOMC
   produced zero trades because the session filter blocked the
   trigger bar. The lab's event-window study (Phase 3) reports:
     - per-event-class trade count *and* a zero-trade flag when the
       session / data filter blocked entries (so a "no signal" finding
       can't be silently confused with "no opportunity tested");
     - per-event-class contribution share — when one class is > 60%
       of all trades, that's "dominance" and a candidate cannot
       graduate on it alone.

7. **Single-rule rescues are unlikely to work.** CAMPAIGN_009 added
   one rule on top of 008, and not only failed but made the train
   side strictly worse. The lab should not recommend a "one-rule
   change" rescue of an artifact-rejected family unless the lab itself
   shows that single rule has independent positive evidence on a
   different study.

8. **Directionality (long vs short) is a small effect on this
   universe.** Across 002 / 004 the long-vs-short expectancy gap is
   in the range of ~0.04 R — much smaller than the random-entry cost
   drag. The lab should report it but not let small directionality
   carry a graduation case alone.

9. **Financing is a documented blocker, not yet a discriminator.**
   Currently modeled only as a conservative stress overlay; it has
   never been the first cause of rejection. Lab studies need to
   report financing-stressed numbers but should not graduate or kill
   a candidate on the stress overlay alone — the live-promotion
   blocker is a separate process per
   `docs/research/FUTURE_RESEARCH_BACKLOG.md` item 1.

10. **No cheap rescue exists for a broadly-negative pair universe.**
    002 H4 + 003 + 004 collectively show three different entries
    failing across 6 majors. The lab should be skeptical of any
    candidate that looks edge-positive only in a regime not yet
    measured by the random-entry baseline (e.g. a narrow event window
    or an exotic-pair subset) — that pattern is the easiest to
    accidentally overfit to.

These ten points become the body of
`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md` in Phase 4. Phase 3's
studies are chosen so each one exercises at least one of them.

---

## Appendix A — sources used

| campaign | file path |
|---|---|
| 002 (H4 & H1 untouched-test rows) | `backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md` |
| 003 (untouched-test row + by-pair) | `backtests/CAMPAIGN_003_CONTROLLED_ADX_REPORT.md` + `docs/research/CAMPAIGN_003_POSTMORTEM.md` |
| 004 (by-pair) | `backtests/CAMPAIGN_004_VOLATILITY_BREAKOUT_REPORT.md` |
| 005 (random + descriptive) | `backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md` |
| 006 (no valid result) | `backtests/CAMPAIGN_006_DAILY_TREND_REPORT.md` |
| 007 (validation by-pair) | `backtests/CAMPAIGN_007_H4_PULLBACK_REPORT.md` |
| 008 (validation by-pair) | `backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md` |
| 009 (validation by-pair + train summary) | `backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md` |
| narrative for 010–014 | sprint brief (this PR's prompt) |
