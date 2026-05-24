# Edge Discovery — Pre-Campaign Exit-Shape Screen (Exit-Asymmetry Addendum)

**Sprint:** `research-exit-asymmetry-cross-campaign-001` · Phase 5
**Date:** 2026-05-24
**Status:** Addendum to
[`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`](EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md),
the hydrate addendum
[`EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md`](EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md),
and the single-pair-probe addendum
[`EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md`](EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md).

This addendum **only tightens** the lab's standing rules; it does
not relax anything. All prior addenda's requirements remain in
force. The cross-campaign exit-asymmetry finding adds one new
mandatory pre-campaign screen and three reporting requirements.

> No strategy approved. CAMPAIGN_001-014 verdicts unchanged.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked.

---

## A. The structural finding this addendum encodes

Across CAMPAIGN_010 - CAMPAIGN_014 (5 campaigns × 7 pairs × 8 folds
= 280 trade ledgers, 16,354 trades):

- **Every** campaign including the random-entry null CAMPAIGN_011
  has positive `mean_R_given_time` (range +0.07 to +0.21 R).
- **The null has the highest mean_R_given_time of the five
  campaigns** at +0.2093 R. No tested entry signal beats random
  entry on the time-exit subset.
- **Stops contribute 63-69 %** of every campaign's gross losses;
  **time exits contribute 99 %** of every campaign's gross gains.
- The cross-campaign structural-pattern check's Conditions 3
  (null-shares-shape) and 4 (per-fold stop_rate σ ≥ 0.05) pass
  at strict thresholds.
- R-9 fires on exactly 1 / 35 cells (the same one the prior probe
  sprint identified as SELECTED_CELL_ARTIFACT). R-9 is selective.

Full numbers in
[`docs/research/EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_RESULT.md`](EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_RESULT.md).
Binding tests in
[`tests/research/edge_discovery/test_exit_asymmetry.py`](../../tests/research/edge_discovery/test_exit_asymmetry.py).

The implication: any candidate using the lab's stop + fixed-bar
time-exit engine inherits a hard −1 R left tail by construction
and inherits a positive-mean small-time-exit-R right tail from
the H4 drift / mean-reversion structure. The exit engine is doing
its job; an entry signal must demonstrate it adds something to
this shape before the lab spends campaign-scale resources on it.

---

## B. New mandatory pre-campaign screen — exit-shape screen

A candidate proposal cannot be promoted from lab study to campaign
unless it demonstrates, at the lab stage, all of the following
against the CAMPAIGN_011 random-entry null **on the matched fold
plan**:

### B.1 Material time-exit lift over the null

- Candidate `mean_R_given_time` ≥ CAMPAIGN_011 `mean_R_given_time`
  + **0.05 R**, per pair.
- **AND** (carry-over from the probe addendum §A.1) either:
  - the cell is **LOO-stable** across all 8 folds (every leave-
    one-fold-out resample stays above +0.05 R), **OR**
  - there are **≥ 2 above-floor cells** in the per-pair grid (the
    multi-cell coherence test the probe addendum installed).

### B.2 Stops are not worse than the null's

- Candidate `mean_R_given_stop` ≥ CAMPAIGN_011 `mean_R_given_stop`
  − **0.05 R**, per pair.
- Translation: if the candidate's stops are paying more than the
  null's stops, the candidate is wrong-direction-prone relative to
  random entry on the same fold layout. That is not edge.

### B.3 No R-9 (mean-of-means positive while cumulative-R negative)

- Candidate `mean_of_fold_means_overall > 0` **AND**
  `cumulative_r_overall < 0` triggers R-9 (probe addendum §A.5)
  and **stops the proposal at the lab**.
- The lab's standard cell evaluation reports both numbers; the
  proposal must show both are simultaneously positive.

### B.4 Per-fold stop-rate dispersion is bounded

- Per-(candidate, pair) `stop_rate` standard deviation across the
  8 folds must be ≤ **0.06** (the cross-campaign median observed
  in this sprint).
- Translation: a candidate whose stop-rate jumps ±6 percentage
  points between folds is one where a single fold's noise can
  swing the per-fold mean by ±0.06 R or more — large enough to
  manufacture an above-floor cell from nothing. Such candidates
  fail this screen.

A candidate that clears B.1 - B.4 has demonstrated **necessary**
conditions for promotion; B.1 - B.4 are **not sufficient**. The
existing campaign-level gate stack (walk-forward expectancy,
gate counts, financing overlay, independent verifier, etc.) still
applies on top.

A candidate that **fails** any of B.1 - B.4 is **stopped at the
lab** and does not consume campaign resources.

---

## C. New mandatory reporting requirements

In addition to the screen, every cell evaluation the lab produces
must now report (i.e., these fields become part of the standard
output schema, not just the screen's inputs):

### C.1 Mean-vs-cumulative-R pair

Every above-floor cell reports:
- `mean_of_fold_means_overall`
- `cumulative_r_overall`

So R-9 is visible to a human reader before the screen fires.

### C.2 Exit-reason decomposition

Every above-floor cell reports:
- `mean_R_given_stop`
- `mean_R_given_time`
- `mean_R_given_eod` (when applicable)
- `share_gross_loss_from_stops`
- `share_gross_gain_from_time_exits`

So the reader can distinguish "candidate's entry edge is real" from
"candidate's time-exit happened to land in a slightly better part
of the small-positive distribution this run".

### C.3 Per-direction shape

Every above-floor cell reports the same metrics split by
`side ∈ {long, short}`. The cross-campaign sweep showed
meaningful per-side differences (e.g., CAMPAIGN_014's longs have
mean_R_given_time = +0.009 vs shorts at +0.120, with overall mean
−0.213 vs −0.085). The lab can't tell whether a per-side asymmetry
is informative without surfacing it.

### C.4 Per-fold stop-rate trajectory

Every above-floor cell reports the 8 per-fold `stop_rate` values
plus the across-fold standard deviation. So a reader can see at a
glance whether the cell's apparent gap is being driven by a single
fold's stop-rate dropping or by an entry-signal change.

---

## D. What this addendum does NOT change

The following rules remain **exactly** as the prior addenda set
them, with **no relaxation**:

- The +0.05 R per-pair material-gap floor (ranking rules §1.3,
  hydrate addendum §A.2, probe addendum §A.1).
- The CAMPAIGN_011 binding null (hydrate addendum §A.1).
- The observed-vs-published integrity gate (ranking rules §1.2).
- The two-screen null-band + material-gap rule (ranking rules §1.4).
- Red flags R-1 through R-9, including the probe addendum's R-9
  (mean-of-means positive while cumulative-R negative).
- The §1.5 single-pair-declared-candidate path (still requires
  the probe-addendum §A.1 multi-cell coherence test in addition to
  this addendum's exit-shape screen).
- The verdict-word ban: APPROVE / PASS / PROMOTE / SHIP / GO-LIVE /
  GREEN-LIGHT do not appear in any classification field anywhere.

The new pre-campaign screen B.1 - B.4 is **additive**. The new
reporting requirements C.1 - C.4 are **additive**.

---

## E. Does this addendum approve, reverse, or revive any strategy?

**No.**

- CAMPAIGN_010-014 remain REJECT-anchored. The exit-shape diagnosis
  reinforces but does not reverse their REJECT verdicts.
- No candidate strategy currently in the lab's queue is promoted by
  this addendum.
- The addendum is a **filter** on future proposals, not a
  re-evaluation of past ones. Past campaigns went through their
  walk-forward gauntlets under the older rules; their results
  stand.
- `configs/approved_strategies.yaml` remains `approved: []`. No
  change required to that file.

---

## F. Sanity checks for the addendum itself

Before adopting B.1 - B.4 as binding rules, the lab confirmed:

- **The screens are not back-fit to any existing candidate.** B.1
  is the standing +0.05 R per-pair floor specialised to
  `mean_R_given_time`. B.2 uses the same 0.05 R tolerance applied
  to the stop subset. B.3 is the existing R-9 red flag. B.4 is the
  observed cross-campaign median 0.0609, rounded down to 0.06.
- **The screens do not invalidate the existing pre-campaign gate
  stack.** A candidate that fails the existing gate stack will
  also fail B.1 - B.4 in most cases (the existing stack is stricter
  on a different axis: walk-forward expectancy, fold-count, etc.).
  B.1 - B.4 catches the small-n masking pattern the existing stack
  was not designed to catch.
- **The screens do not require new data.** A candidate's lab-stage
  per-fold trade ledger contains every input the four screens need.
  No broker call, no new fetch.
- **The screens scale**: when n_folds_paired < 6 the cell is
  classified `INSUFFICIENT_DATA` rather than promoted (probe-
  addendum carry-over). B.1 - B.4 inherit this rule.

---

## G. Future evolution of this addendum

This addendum may be **tightened further** by:

- Lowering the 0.05 R material-gap floor if a future bias-of-
  fixtures audit shows the null itself is biased toward positive R.
- Adding a per-(candidate, hour-of-day) reporting requirement once
  the recommended next CAMPAIGN_002 H4 per-hour study runs.
- Raising the 0.06 stop_rate dispersion ceiling if a new family
  ends up with reliably-low per-fold stop-rate noise.

It will **not** be relaxed without explicit lab review and a new
sprint write-up justifying the relaxation. The
`tests/research/edge_discovery/test_exit_asymmetry.py` binding
tests pin the headline numbers underneath these rules; any future
loosening must update or invalidate those tests.
