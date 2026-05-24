# Edge Discovery — Candidate Ranking Rules (Single-Pair Probe Addendum)

**Sprint:** `research-edge-discovery-lab-single-pair-probe-001` · Phase 4
**Date:** 2026-05-24
**Status:** Addendum to
[`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`](EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md)
and the prior hydrate addendum
[`EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md`](EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md).
What this probe changes about how the lab ranks candidates. The
original ranking rules + the hydrate addendum remain in force; this
addendum **tightens** rather than relaxes.

> No strategy approved. CAMPAIGN_001–014 verdicts unchanged.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked.

---

## A. What this probe changes

The hydrate sprint's pair-baseline study identified exactly one
above-floor cell (EUR_USD / CAMPAIGN_012, +0.0950 R) across a 7-pair
× 4-candidate grid. The probe falsified that cell. The lab's
ranking rules therefore gain three concrete **anti-multiple-
comparisons** clarifications:

### A.1 The +0.05 R material-gap floor is a per-cell threshold, not a
per-grid threshold

The original ranking rules §1.3 and the hydrate addendum §A.2
established the +0.05 R floor as a per-pair gate. The probe makes
explicit that **passing the +0.05 R floor in a single cell on a
multi-cell grid is not, by itself, evidence**.

The lab evaluates a 7-pair × 4-candidate grid of 28 cells in its
pair-baseline study. Even under a no-edge null with per-cell noise
σ ≈ 0.15 R (centered between the 0.12 R candidate σ and 0.20 R
null σ observed), the expected number of cells above +0.05 R is
~10 / 28 by raw count, but **only ~1 / 28** if the per-cell mean
is paired-difference vs the same null across 8 folds with SE ≈
0.07 R (close to what was observed for the EUR_USD / C012 cell).

A future lab proposal citing "≥ 1 above-floor cell in the pair-
baseline grid" must therefore **either**:

1. Show that ≥ 1 LOO resample of that cell stays above floor
   (probe Phase 2 §2.3 — this cell failed at fold-7 LOO), **or**
2. Show that ≥ 2 cells in the grid clear the floor with positive
   gaps (multi-cell coherence — the broad-pattern test that
   neighbor-pair / neighbor-candidate checks operationalize).

### A.2 New mandatory check — leave-one-fold-out (LOO) stability

Every above-floor cell the lab surfaces must report the LOO range
of the mean gap. The probe's lab script for this is reusable:

- [`research/edge_discovery/studies/probe_robustness_eur_usd_c012.py::_check_loo`](../../research/edge_discovery/studies/probe_robustness_eur_usd_c012.py)
  generalizes to any (pair, candidate, null_campaign) triple.
- The binding criterion: **`min_loo_mean_gap ≥ +0.05 R`**. If any
  single fold's removal drops the mean gap below the floor, the
  cell is fold-concentrated and is **stopped at the lab**.

### A.3 New mandatory check — standard-error-of-mean-gap on the 8 folds

Treat the per-fold gap values as 8 paired observations; compute
the standard error of the mean gap. A cell is above the lab's
soft significance band only if:

- **mean_gap_r ≥ 2 × se_mean_gap** (i.e. t-stat ≥ 2.0)

The probe cell at t ≈ 1.3 is below this floor; the same screen
applied generically would catch any future single-fold-driven
"edge" before it gets a follow-up.

### A.4 New mandatory check — median ≥ 0 on per-fold expectancy

If the **median** per-fold candidate expectancy R is negative,
the candidate is signaling that the typical fold loses money. A
positive mean of means in that situation is, by definition,
carried by outlier folds. The lab will report the median
alongside the mean for every cell and treat **median < 0 as a
red flag R-9 (new)** alongside the existing R-1 through R-8.

### A.5 New red flag — R-9: mean-of-means positive while
cumulative-R negative

The probe surfaced a striking pattern: the EUR_USD / CAMPAIGN_012
cell has a mean-of-means expectancy of +0.0300 R while the **sum
of trade-level r_multiple across all 479 trades is −4.391 R**.
A strategy whose mean-of-fold-means is positive while its
trade-level cumulative R is negative is a small-n averaging
artifact and is **stopped at the lab**.

The lab's standard cell evaluation now reports both:

- `mean_expectancy_r` (mean of per-fold means; what the existing
  pair-baseline study reports)
- `total_cumulative_r` (sum of per-trade r_multiple; what the
  trade ledger produces)

If `mean_expectancy_r > 0` and `total_cumulative_r < 0`, R-9 fires.

## B. Does EUR_USD-only research deserve more lab work?

**Not on this candidate, not on this signal.** The probe's result
classifies the cell as SELECTED_CELL_ARTIFACT; the lab will not
queue a follow-up specifically for EUR_USD / regime_switcher_atr_
percentile.

The lab **may** still queue a follow-up on **time-exit vs
stop-exit asymmetry across all candidates × all pairs**, because
the probe's §2.7 observation (91 stop trades at exactly −1.0 R;
386 time trades at +0.226 R) generalizes beyond this one cell.
That follow-up is a structural lab study, not a single-pair
single-candidate probe; it does not promote any strategy and it
is explicitly distinct from this sprint's anomaly.

## C. Does CAMPAIGN_012 remain rejected?

**Yes.** Per
[`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md) and the probe's
findings:

- 5 of 8 inherited aggregate gates fail.
- Aggregate expectancy R is −0.0521 (vs +0.05 gate, vs CAMPAIGN_011
  null −0.0024 — ~21 × the indistinguishability half-band worse).
- 0 / 8 folds pass.
- Only 1 / 7 pairs has positive aggregate expectancy R (USD_JPY
  at +0.0004 R — essentially random walk).
- The EUR_USD per-pair cell that looked above-floor turns out to
  be a single-fold-driven artifact under the probe's screens.

`configs/approved_strategies.yaml` remains `approved: []`.
CAMPAIGN_012's REJECT verdict stands. The probe does not propose
a campaign reversal or a campaign extension.

## D. What should be studied next if this fails?

**This branch's recommendation when the probe fails** (which it
did):

1. **Time-exit / stop-exit asymmetry study, cross-candidate /
   cross-pair.** Pull every trade in every fold of every
   CAMPAIGN_010-014 campaign; group by `exit_reason`; compute
   per-(reason, candidate, pair) mean R and per-reason n. Question:
   does the −1.0 R stop floor pattern observed here generalize?
   If yes, that's a **lab-side observation about the strategy
   family** (small-wins / occasional-max-loss), not a candidate
   promotion path.

2. **CAMPAIGN_014 ECB / BoE shorts-only follow-up.** Carry-over
   from the hydrate sprint's recommended next-3. The probe didn't
   touch this; it is still the next viable narrow lab study.

3. **Bias-of-fixtures audit.** Recommended in the prior lab
   sprint's ranking rules §6.5 but never run. Cheaper than a new
   real-data sweep and grounds the lab in a known no-edge baseline.

## E. What should be studied next if this had looked promising?

For completeness, since the plan's §4 specified both branches:

If the cell had survived (it did not — see §A.5 et al.), the next
lab study would have been:

1. **Per-fold consistency probe at a finer resolution.** Pull each
   fold's per-week test-window slice and compute weekly mean R for
   EUR_USD under CAMPAIGN_012, side-by-side with CAMPAIGN_011.
   Question: is the +0.0950 R gap held across the test window
   uniformly, or does it cluster in a few specific weeks /
   regimes?

2. **CAMPAIGN_002-derived H4 OHLC time-of-day study restricted to
   EUR_USD.** Pull the real H4 store, compute per-hour LONG and
   SHORT forward-return means, and check whether any hour's
   distribution coincides with the CAMPAIGN_012 entry-time
   distribution from §2.7 of the probe result. The hydrate sprint's
   session study already laid the groundwork; this would extend
   it to a tighter pair × hour × side breakdown.

3. **Single-pair declared candidate proposal draft** per the
   original ranking rules §1.5 — explicitly EUR_USD-only,
   risk-budget-capped, with a pre-committed walk-forward plan
   referencing CAMPAIGN_011's per-fold layout.

None of those is in scope for this sprint. The cell failed; the
"next if fail" branch (§D) applies.

## F. No relaxation of the existing rules

This addendum **only** tightens. Specifically:

- The +0.05 R per-pair floor is unchanged.
- The CAMPAIGN_011 binding null is unchanged.
- The observed-vs-published integrity gate is unchanged.
- The two-screen null-band + material-gap rule is unchanged.
- The §2 red flags R-1 through R-8 are unchanged.

New, additive content:

- §A.2: LOO stability check is now mandatory for any above-floor
  cell.
- §A.3: t-stat ≥ 2 SE check on the per-fold gap distribution.
- §A.4: per-fold median ≥ 0 reporting requirement.
- §A.5: new red flag **R-9 (mean-of-means positive while
  cumulative-R negative)**.

These reflect lessons learned from the falsification work; they
make the next single-pair-cell evaluation cheaper and safer than
this one was.
