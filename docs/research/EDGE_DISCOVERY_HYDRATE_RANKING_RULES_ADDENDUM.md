# Edge Discovery — Candidate Ranking Rules (Hydrate Sprint Addendum)

**Sprint:** `research-edge-discovery-lab-hydrate-001` · Phase 4
**Date:** 2026-05-24
**Status:** Addendum to
[`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`](EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md).
What the rules now bind to once real local artifacts are available.
**The original document remains the canonical decision contract.**
This addendum updates the **null baseline citation** and adds two
real-data clarifications that the original could not make until the
artifacts existed.

> No strategy approved. CAMPAIGN_001–014 verdicts unchanged.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked.

---

## A. CAMPAIGN_011 replaces CAMPAIGN_005 as the binding null baseline

The original §3 anchored the null cite to **CAMPAIGN_005, Benchmark
3** (universe mean = `−0.095 R`) because CAMPAIGN_010–014 had not yet
landed as committed artifacts on that sprint's branch.

Effective this sprint, the binding null baseline is **CAMPAIGN_011
random_entry_anchor**, per its
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md). The original §3 table
is **deprecated as the binding floor** and stays as a secondary
cross-reference for the fixed-30-bar shape only.

### A.1 The new binding null table (per-pair, from real artifacts)

Source:
[`research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md`](../../research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md)
§ "Null per pair (CAMPAIGN_011 mean expectancy R across 8 folds)".

| pair | CAMPAIGN_011 mean R (8-fold avg) | n trades | n folds positive | avg spread (pips) |
|---|---:|---:|---:|---:|
| EUR_USD | −0.0650 | 119 | 3 | 1.45 |
| GBP_USD | +0.0756 | 196 | 5 | 1.86 |
| USD_JPY | +0.0000 | 174 | 3 | 1.64 |
| AUD_USD | −0.0415 | 190 | 2 | 1.35 |
| USD_CAD | −0.0069 | 182 | 5 | 1.90 |
| USD_CHF | +0.0269 | 177 | 5 | 1.64 |
| NZD_USD | −0.0986 | 139 | 3 | 2.36 |
| **aggregate** | **−0.0024** | 1,177 | 26 / 56 | 1.73 |

GBP_USD's positive null mean (+0.076 R, 5 / 8 folds positive) is the
clearest demonstration that the per-pair null is not a flat negative
band — random-entry baselines can produce positive per-pair means by
chance, and a candidate that "beats" GBP_USD by less than +0.05 R
has done no work.

### A.2 The new graduation gate (replaces original §1.3 cite)

A lab study comparing a candidate to the null must now report:

1. The candidate's per-pair mean expectancy R on the **same 8-fold
   rolling layout CAMPAIGN_011 used** (matching `plan.json`).
2. The per-pair gap to the table in A.1.
3. A pass requires gap ≥ **+0.05 R** on whichever pair(s) the
   proposal claims to work on (§1.2 still binds: ≥ 30 trades in the
   slice).
4. A pass on the **aggregate** CAMPAIGN_011 null (`−0.0024 R`) is
   **not** sufficient — pair-level pass is required (per Lesson 3).

The lab's `random_null_baseline` for fresh per-study null comparisons
remains useful and still gets run; the binding cite, however, is the
CAMPAIGN_011 per-pair table because that is the same data, same
fold layout, same exit logic as the future candidate.

## B. Real-data clarification 1 — observed-vs-published integrity gate

Every future candidate's evidence packet must include the
observed-vs-published reconciliation that
[`real_study_turnover_cost.md`](../../research/edge_discovery/studies/outputs/real/real_study_turnover_cost.md)
performs on CAMPAIGN_010–014:

- The candidate's observed per-trade mean R (pulled from the
  per-fold per-pair `*_trades.csv` files) must equal the published
  `aggregate_expectancy_r` in `walk_forward/results.json` to within
  **1e-3 R**.
- A drift > 1e-3 R between observed and published is a **freeze
  violation** — it means either the trade ledgers don't match the
  published aggregates, or the published aggregates are computed
  differently than the lab assumed. Either case kills the proposal
  until the discrepancy is resolved.
- This gate is cheap (single script) and protects the lab from
  citing a number it can't reproduce from the source artifacts.

CAMPAIGN_010–014 all pass this gate cleanly (see
[`real_study_turnover_cost.md`](../../research/edge_discovery/studies/outputs/real/real_study_turnover_cost.md)
"Per-campaign observed vs published" table).

## C. Real-data clarification 2 — null-band vs material-gap two-screen rule

The original §1.3 conflated two screens:

1. **Null-band classifier.** The lab's `compare_to_null` function
   labels a study mean as `within_null` / `slightly_above_null` /
   `materially_above_null` based on null stds (descriptive — never a
   significance test).
2. **Material-gap floor.** §1.4 requires the per-trade pre-cost edge
   to clear cost-per-trade with margin; this is an R-unit absolute
   threshold (currently +0.05 R per pair).

The real-data session study (
[`real_study_session_by_hour.md`](../../research/edge_discovery/studies/outputs/real/real_study_session_by_hour.md))
is a worked example of the two screens diverging:

- Three UTC hours (02, 06, 13) are labeled `materially_above_null`
  by the band classifier on a 9,927-bar real H4 frame.
- All three have absolute mean post-cost ≈ `−0.00007` log-units —
  nowhere near the +0.05 R material-gap floor.

The rule **explicitly clarified** by this sprint's addendum: a
proposal must pass **both** screens (null-band ≥ `+1.0` stds AND
per-pair gap ≥ `+0.05 R`). Original §1.3 wording stays in force; this
addendum just makes the implicit conjunction explicit.

## D. Real-data corroboration of existing red flags

The original §2 red flags are corroborated by the real-data studies
(no change to the red-flag list — added column shows the empirical
support):

| red flag | what triggered it on real data |
|---|---|
| **R-1 cost-dominated** | All 5 CAMPAIGN_010-014 ledgers (`real_study_turnover_cost.md`); 0 / 5 had a positive per-trade pre-cost edge. |
| **R-2 within null** | CAMPAIGN_011 by construction; CAMPAIGN_010 aggregate −0.0408 R within band of CAMPAIGN_011's −0.0024 R. |
| **R-3 single-pair effect** | EUR_USD-under-CAMPAIGN_012's +0.0950 R gap; the only above-floor cell in the 7×4 candidate table. |
| **R-5 dominant-event-class with opposite-sign minority** | CAMPAIGN_014: NFP 79.3 % of trades and negative R; ECB / BoE positive on shorts only. |
| **R-6 zero-trade slice on the dominant filter** | CAMPAIGN_014: **FOMC has zero matched trades** within ±24 h of any fixture event in the trades CSV. |

## E. Updated "next 3-5 lab studies" pointer

The original §6 listed the brief's CAMPAIGN_014 narrative as the
top-priority next lab study. **That study has now run** (Phase 3 of
this sprint); its outputs are committed. The updated next-3 priority
list is in
[`EDGE_DISCOVERY_LAB_HYDRATE_001_RESULTS_ADDENDUM.md`](EDGE_DISCOVERY_LAB_HYDRATE_001_RESULTS_ADDENDUM.md) §5:

1. **EUR_USD / CAMPAIGN_012 single-pair declared candidate probe.**
2. **Non-NFP event windows — ECB / BoE shorts-only follow-up.**
3. **Per-fold consistency probe for the EUR_USD / CAMPAIGN_012 cell.**

None of these is authorized to produce a strategy verdict. Each is
a single-script extension of the existing real-data lab.

## F. No new red flags. No relaxed gates.

This addendum **only**:

- swaps the null-cite to CAMPAIGN_011 (§A);
- adds the observed-vs-published integrity gate (§B);
- makes the two-screen rule explicit (§C);
- adds the corroboration column (§D);
- updates the next-studies pointer (§E).

The original ranking rules' §1 (graduation gates), §2 (red flags),
§4 (turnover penalty), and §5 (backlog handling) are **unchanged in
substance**. A proposal that would have failed the original rules
fails the addended rules; a proposal that passes the original rules
also has to pass the new per-pair CAMPAIGN_011-null gate before it
graduates.
