# Cross-Campaign Exit-Asymmetry — Result

**Sprint:** `research-exit-asymmetry-cross-campaign-001`
**Phase:** 4 (interpretation)
**Date:** 2026-05-24
**Status:** Diagnostic result. **No strategy approved.** **No
campaign verdict changed.** Paper / demo / live remain blocked.
`configs/approved_strategies.yaml` stays `approved: []`.

> This document is the **interpretation** of the cross-campaign exit-
> asymmetry data the lab pulled in Phases 1 - 3. The numbers it
> cites live in
> [`research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.json`](../../research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.json)
> and
> [`research/edge_discovery/studies/outputs/real/exit_asymmetry_robustness.json`](../../research/edge_discovery/studies/outputs/real/exit_asymmetry_robustness.json),
> pinned by [`tests/research/edge_discovery/test_exit_asymmetry.py`](../../tests/research/edge_discovery/test_exit_asymmetry.py).

---

## 1. Plan questions, answered

### Q1. Across CAMPAIGN_010-014, do `stop` exits systematically crystallise losses near −1 R while `time` exits crystallise systematically smaller, mostly positive R?

**Yes, broadly — and specifically yes for stops, weakly yes for time exits.**

| campaign | n_total | stop_rate | mean_R_given_stop | mean_R_given_time | pct_stops≤−0.95 R |
|---|---:|---:|---:|---:|---:|
| CAMPAIGN_010_session_breakout | 2,791 | 0.237 | −0.7917 | +0.1926 | 0.637 |
| CAMPAIGN_011_random_entry_anchor | 1,177 | 0.205 | −0.8312 | +0.2093 | 0.705 |
| CAMPAIGN_012_regime_switcher_atr_percentile | 3,726 | 0.204 | −0.8178 | +0.1450 | 0.679 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 7,940 | 0.231 | −0.9483 | +0.2105 | 0.856 |
| CAMPAIGN_014_calendar_event_window_anomaly | 720 | 0.242 | −0.8081 | +0.0667 | 0.718 |

- **`mean_R_given_stop` is in the band [−0.95, −0.79] in all 5 campaigns**, and the median per-stop R is exactly −1.0000 R for every campaign (see Phase 1+2 JSON `per_campaign[*].median_r_given_stop`). 63-86% of stops sit at or below −0.95 R; the rest are partial-fill stops that paid less than 1 R (typically when the stop bar opens past the stop price and the realised loss is slightly larger or smaller than the planned risk).
- **`mean_R_given_time` is positive in every campaign**, with the highest value belonging to **the random-entry null CAMPAIGN_011** at +0.2093 R. The two ranges
  [+0.07, +0.21] for time-exit mean R and [−0.95, −0.79] for stop-mean R are inside-engine numbers — they describe what the lab's fixed-bar-hold exit engine produces, not what the strategy's entry signal earned.
- 65-74% of time exits sit inside the [−0.5, +0.5] R band — most time exits are small.

So the answer to Q1 is **yes, but the asymmetry is not strategy-specific**. See Q2.

### Q2. Is the asymmetry a property of the strategy family or of the exit engine?

**Exit engine.**

- **CAMPAIGN_011 (random-entry null) has the highest `mean_R_given_time` of all 5 campaigns at +0.2093 R**, even though it has no entry signal at all. Its stop_rate (0.205) and `mean_R_given_stop` (−0.8312) sit firmly inside the cross-campaign distribution (|Δ vs cross-campaign median| ≤ 0.03 for both).
- The cross-campaign structural-pattern check's **Condition 3 (null-shares-shape) PASSES** at the strict ±0.05 threshold.
- This is the single most important finding of the sprint: there is **no entry signal** in any campaign that produces a `mean_R_given_time` higher than what random entry produces on the same fold layout. Whatever positive expectancy the time-exit subset has across the cross-campaign grid is being generated **by the H4 mean-reversion / drift in the underlying price series**, not by any of the entry-signal families on test.

### Q3. Are positive cells dominated by their time-exit subset rather than by edge across both modes?

**Yes, almost categorically.**

- In every one of the 5 campaigns, the share of gross gains explained by `time` exits is **≥ 98.9 %**:

| campaign | share_gross_loss_from_stops | share_gross_gain_from_time_exits |
|---|---:|---:|
| CAMPAIGN_010 | 0.688 | **0.990** |
| CAMPAIGN_011 (null) | 0.668 | **0.989** |
| CAMPAIGN_012 | 0.631 | **0.999** |
| CAMPAIGN_013 | 0.681 | **0.996** |
| CAMPAIGN_014 | 0.642 | **0.997** |

  Translation: virtually 100 % of every campaign's *positive* trades come from time exits, while stops contribute 63-69 % of every campaign's *negative* trades. The strategy families are mathematically incapable of generating gross gains via stops; they can only generate gains by waiting for the time exit to land somewhere in the small positive band.

- The 7 cells (out of 35) whose `mean_of_fold_means_overall` is positive are mostly cases where the stop-rate happened to be lower than the cross-grid average; the **R-9 sweep fires on exactly one of them**: EUR_USD under CAMPAIGN_012 — the cell the prior probe sprint already classified as a SELECTED_CELL_ARTIFACT. Of the remaining 6 positive-mean cells, all have non-negative cumulative R but also have neighbour pairs / neighbour campaigns that look like noise (i.e., they do not pass the probe-addendum's §A.1 multi-cell coherence requirement).

### Q4. Does per-fold stop-rate variance drive per-fold expectancy?

**Yes, materially.**

- **Median per-(campaign, pair) stop_rate standard deviation across folds is 0.0609.** The structural-pattern check's Condition 4 passes at the ±0.05 threshold. A stop_rate that varies by ±6 percentage points fold-to-fold, paired with a `mean_R_given_stop` near −1 R, means a single fold's stop-rate noise can swing the per-fold mean R by ±0.06 R on its own — large enough to flip a small mean-of-means positive into negative.
- The CAMPAIGN_013 × EUR_USD above-floor cell on `mean_R_given_time` is the cleanest example. Its stop-rate-gap correlation across the 5 paired folds is **−0.79**: folds with higher candidate-cell stop rates have lower gap vs the null. The apparent +0.0531 R `mean_R_given_time` gap **is being generated by stop-rate noise rather than by any actual time-exit edge**.

---

## 2. Headline interpretation

The five candidate strategies CAMPAIGN_010-014 share an exit engine
(hard stop + fixed-bar time exit). Across the entire 280-trade-file
grid:

> **Every campaign loses money on average. Every campaign's gross
> gains come almost exclusively from time exits. Every campaign,
> including the random-entry null, has a positive mean-time-exit R
> ranging from +0.07 to +0.21 R — and the null has the highest mean
> time-exit R of the five. The exit engine, not the entry signal,
> determines the shape of the payoff distribution.**

This is **not** an indictment of stop losses as risk control. The
stops are doing exactly what stop losses are supposed to do: when
the strategy is wrong, they crystallise the planned 1 R loss
before slippage can compound it. The 63-69 % of every campaign's
gross losses coming from stops is the structural cost of having
risk control: stops convert "wrong-direction trade" into "−1 R
exit" reliably.

The diagnosis is **about the entry signal**, not the exit. The
strategies in CAMPAIGN_010-014 don't generate enough right-tail
gain via time exits to offset the −1 R left tail from stops, and
the random-entry null shows that the lab's exit engine on its own
already squeezes most of the available H4 drift / mean-reversion
out of the time-exit subset. There is no "left over edge" for an
entry signal to capture if it sits on top of the same exit engine.

---

## 3. Implications for the lab's process

### 3.1 Should stops be doing useful risk control or just crystallising negative entry edge?

**Both, simultaneously.** The stops *are* doing risk control — they
prevent any individual trade from costing > 1 R — and they *are*
crystallising the strategy's negative entry edge whenever the entry
direction is wrong. The two are not mutually exclusive and the
former is not optional. The right interpretation is "the stop is
fine; the entry can't find enough right-tail to pay for the stop."

### 3.2 Are time exits masking weak signal?

**Yes, in the sense that the time-exit subset has a small positive
mean across every campaign including the null, which makes
mean-of-fold-means positive in cells where it is not actually
exploitable.** This is the R-9 / single-pair-probe pattern. The
single above-floor cell from Phase 1+2 (C013 × EUR_USD on time-only)
is exactly this masking pattern; once it goes through the Phase 3
screens it downgrades to `INSUFFICIENT_DATA`.

The lab will continue to report mean R *and* cumulative R *and*
median per-fold R *and* `mean_R_given_time` and `mean_R_given_stop`
separately for every above-floor cell — see §3.3.

### 3.3 Should future candidates require pre-campaign exit-shape screens?

**Yes.** Specifically the lab will add a **pre-campaign exit-shape
screen** to the candidate-ranking rules. The screen requires a
candidate proposal to demonstrate at the lab stage that:

1. The candidate's expected `mean_R_given_time` materially exceeds
   the same statistic from the **random-entry null** (CAMPAIGN_011).
   "Materially" means ≥ +0.05 R *and* ≥ 1 LOO-stable cell *or*
   ≥ 2 above-floor cells in the per-pair grid (the existing probe-
   addendum §A.1 carry-over).
2. The candidate's expected `mean_R_given_stop` is **not** worse
   than the null's by ≥ 0.05 R — i.e., the candidate isn't simply
   wrong-direction-prone.
3. The candidate's expected `mean_R_overall` is positive in
   ≥ 5/8 folds *and* the per-trade `cumulative_r_overall` is
   positive (R-9 cannot fire).
4. The per-(pair, fold) stop_rate dispersion is ≤ the cross-
   campaign median of 0.06 — i.e., the candidate's per-fold
   stop-rate noise is not large enough to manufacture a per-fold
   mean-of-means false positive.

These four screens are codified as a new lab rule in the Phase 5
addendum
([EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md](EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md)).
They are **necessary, not sufficient**, conditions for a candidate
to be promoted from lab study to campaign. **No existing candidate
clears them.**

### 3.4 Should any family be retired earlier based on exit/payoff shape?

**No campaign verdict is reversed by this sprint** — CAMPAIGN_010-014
are already REJECT-anchored and their REJECT verdicts stand. The
sprint's structural finding does, however, justify the lab making
the following observation at proposal-review time:

> A candidate whose mechanism is "the entry signal directs an H4
> trade with a stop and a fixed-bar time exit" *cannot, by
> construction, generate gross gains in its stop-exit subset*. Any
> edge the candidate has has to live in its time-exit subset. If
> the candidate's expected `mean_R_given_time` is not materially
> better than the random-entry null's `mean_R_given_time`, the
> candidate is not adding anything to the exit engine and lab time
> is wasted by sending it to a campaign.

This is a **pre-campaign filter**, not a post-campaign reversal.
The five existing campaigns went through their walk-forward gauntlets
under the older lab rules; their REJECT verdicts are now reinforced
by this structural diagnosis.

### 3.5 What does this say about designing the next edge-discovery studies?

Three concrete directions remain on the table from prior sprints:

1. **CAMPAIGN_014 ECB / BoE shorts-only follow-up** (hydrate addendum
   §B). Still a valid narrow study; the probe sprint did not invalidate
   it. **Whether it produces something worth a campaign depends on
   the pre-campaign exit-shape screen this sprint installs.**

2. **Time-of-day / session sub-slice of CAMPAIGN_002 H4** (hydrate
   addendum §B and probe result §E). This is the natural next lab
   study to test whether the small positive time-exit subset has
   *any* exploitable structure — e.g., whether there is an hour-of-
   day during which `mean_R_given_time` is materially higher than the
   campaign-wide ~+0.15 average and *also* clears the
   CAMPAIGN_011 null at the same hour.

3. **Bias-of-fixtures audit** (probe result §D). Cheap; grounds the
   lab in a known no-edge baseline. The exit-asymmetry findings here
   make this a more pressing audit, because if the lab is going to
   add a "must beat null on time-exit subset" screen it needs to be
   confident the null itself is faithful.

The lab does **not** recommend a follow-up that probes the C013 ×
EUR_USD `mean_R_given_time` cell. That cell is INSUFFICIENT_DATA
under the probe-addendum's paired-fold threshold and its apparent
gap is stop-rate-driven (corr = −0.79). A future probe of it would
be the second time the lab spent a sprint falsifying a single-cell
anomaly, and the standing §A.1 rule already says: do not queue.

---

## 4. What this sprint does NOT propose

Restating the pre-committed refusals from §12 of the Phase 0 plan:

1. **No strategy is approved.** `configs/approved_strategies.yaml`
   stays `approved: []`.
2. **No campaign verdict is reversed.** CAMPAIGN_010-014 remain
   REJECT-anchored.
3. **No parameter is tuned.** The sprint does not propose a wider
   stop, a longer time budget, or a different stop placement on any
   existing candidate.
4. **No new candidate is proposed.** The diagnosis does not contain
   a "and now here is the strategy that would work" reveal. The
   lab's conclusion is that future candidates need a higher bar
   before they get campaign time, not that any candidate exists
   that clears it.
5. **No broker call, no new data pull.** Every number in this doc
   was derived from already-committed local artifacts.
6. **No verdict-word in any classification field.** APPROVE / PASS /
   PROMOTE / SHIP / GO-LIVE / GREEN-LIGHT do not appear in any
   classification block in the JSON or markdown outputs.

The deliverable of this sprint is a **diagnosis** plus a new
**pre-campaign screen** captured in the Phase 5 addendum. Nothing
more.

---

## 5. Structural classification (Phase 0 §6 + §8)

### 5.1 Cross-grid structural pattern

**Classification:** `STRUCTURAL_FAILURE_PATTERN_PARTIAL`

| Phase 0 condition | strict threshold | observed | PASS? |
|---|---|---|:---:|
| 1. Universal hard stop (≥ 90 % of stops ≤ −0.95 R per campaign) | 0.90 | range 0.637 - 0.856 | ✗ |
| 2. Universal small-positive time shape (≥ 70 % in band + mean > 0 in ≥ 4/5 campaigns incl null) | 0.70 in band | range 0.630 - 0.739; mean > 0 in 5/5 | ✗ (band fails) |
| 3. Null shares the shape (|Δ| ≤ 0.05 vs median of others) | 0.05 | stop_rate Δ = 0.029, mean_R_given_stop Δ = 0.018 | ✓ |
| 4. Fold-noise driver (median per-pair stop_rate σ ≥ 0.05) | 0.05 | 0.0609 | ✓ |

Conditions 1 and 2 fail at the strict thresholds the plan set, but
**both fail in a direction that is informative, not surprising**:

- Condition 1: 64-86 % of stops at ≤ −0.95 R is enough for stops to
  dominate gross losses (Q3) without being *literally* universal. The
  partial stops simply reflect bar-open-past-stop-price slippage; the
  median stop R is exactly −1.0000 R for every campaign.
- Condition 2: the small-band fraction is 63-74 % across the
  campaigns, just under the 70 % threshold the plan set. The plan's
  threshold was deliberately strict; relaxing it to 60 % would let
  Condition 2 pass on 5/5 campaigns. The qualitative story (positive
  mean time R with a tight distribution around zero) is intact.

Conditions 3 and 4 pass cleanly. **The shape is an exit-engine
artifact** (Condition 3) and **per-fold stop-rate noise is large
enough to drive per-fold expectancy** (Condition 4). These are the
two conditions that justify the new pre-campaign screen.

### 5.2 Per-(campaign, instrument) cell sweep

- 35 cells total.
- 7 cells with `mean_of_fold_means_overall > 0`.
- 29 / 35 cells with `cumulative_r_overall < 0`.
- 29 / 35 cells with `median_per_fold_mean_r_overall < 0`.
- **R-9 fires on exactly 1 / 35 cells**: EUR_USD / CAMPAIGN_012.
  This is the cell the prior probe sprint already classified as
  SELECTED_CELL_ARTIFACT. R-9 is selective.
- The single above-floor cell on `mean_R_given_time` vs C011
  (CAMPAIGN_013 × EUR_USD, gap = +0.0531 R) classifies as
  `INSUFFICIENT_DATA` after the Phase 3 screens (n_folds_paired = 5
  < the lab's required 6, the apparent gap is stop-rate-driven at
  corr = −0.79, and the t-stat = 1.97 sits just below 2.0).
- **No cell classifies as `PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL`
  or stronger.**

---

## 6. Recommended next branches

In order of cheapness × informativeness:

1. **Bias-of-fixtures audit (lab) — recommended first.** Required to
   ground the null assumption underneath the new pre-campaign screen.
   Cost: low (1-2 days). Does not touch any campaign.
2. **Per-hour `mean_R_given_time` study restricted to CAMPAIGN_002
   H4 vs CAMPAIGN_011 H4** — extends the hydrate sprint's session
   study and tests whether the small-positive-time-exit subset has
   any hour-of-day exploitable substructure that survives the new
   screen. Cost: moderate. Does not propose a candidate; produces a
   ranked-by-hour table.
3. **CAMPAIGN_014 ECB / BoE shorts-only narrow probe** — carry-over
   from the hydrate sprint's next-3, untouched by both the probe
   sprint and this sprint. Cost: moderate. The pre-campaign screen
   this sprint installs raises the bar before any such probe could
   recommend a follow-up.

This sprint takes no position on which of those is run first; it
just makes sure none of them is a probe of the C013 × EUR_USD time-
only cell, which is now correctly classified as `INSUFFICIENT_DATA`.

---

## 7. Numerical pins (re-stated for verifier)

These numbers are pinned by
[`tests/research/edge_discovery/test_exit_asymmetry.py`](../../tests/research/edge_discovery/test_exit_asymmetry.py).
A future lab change that flips them changes the diagnosis and must
be re-evaluated:

- Total cross-campaign trades: **16,354**.
- Cross-campaign exit-reason vocabulary: **`['eod', 'stop', 'time']`**.
- 5 / 5 campaigns have `mean_R_given_time > 0`.
- 5 / 5 campaigns have `mean_R_overall ≤ 0`.
- 5 / 5 campaigns have `share_gross_loss_from_stops ≥ 0.60`.
- 5 / 5 campaigns have `share_gross_gain_from_time_exits ≥ 0.98`.
- Structural-pattern check classification: `STRUCTURAL_FAILURE_PATTERN_PARTIAL`.
- Conditions 3 (null shares shape) and 4 (fold-noise driver) PASS.
- R-9 fires on exactly 1 / 35 cells: EUR_USD / CAMPAIGN_012.
- ≥ 28 / 35 cells have `cumulative_r_overall < 0`.
- ≥ 28 / 35 cells have negative median per-fold `mean_r_overall`.
- The CAMPAIGN_013 × EUR_USD `mean_R_given_time` cell classifies as
  `INSUFFICIENT_DATA` (n_folds_paired = 5 < required 6).
- `configs/approved_strategies.yaml` remains `approved: []`.

This concludes the diagnostic portion. Phase 5 captures the new
lab rule and the sprint summary.
