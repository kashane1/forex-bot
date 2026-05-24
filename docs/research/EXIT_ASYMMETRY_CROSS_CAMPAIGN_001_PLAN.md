# Cross-Campaign Exit-Asymmetry Lab Study — Phase 0 Plan

**Sprint id:** `research-exit-asymmetry-cross-campaign-001`
**Phase:** 0 — orientation + study plan
**Date:** 2026-05-24
**Status:** Plan only. **No strategy approved.** **No campaign
verdict changed.** Paper / demo / live remain blocked.

> Constraints (verbatim from the brief, re-stated here so they bind
> every later phase of this branch):
>
> - This is not a strategy campaign and not an optimization sprint.
> - Do not approve any strategy.
> - Do not change campaign verdicts.
> - Do not tune parameters.
> - Do not use broker endpoints.
> - Do not fetch new broker data.
> - Use existing local research artifacts only.
> - Keep the research freeze, approval gates, credential rules, and
>   paper/demo/live refusal behaviour intact.

This is a **diagnostic, descriptive** lab sprint. It studies whether
the **exit / payoff shape** that surfaced in the EUR_USD / CAMPAIGN_012
falsification probe is a recurring structural failure mode across
CAMPAIGN_010 - CAMPAIGN_014, or whether it was incidental to one
cell. The output of this sprint is a diagnosis and, possibly, a new
pre-campaign screen. It is **not** a tuning proposal and it does
**not** propose new candidates.

---

## 1. Carry-over from the single-pair probe

The probe sprint
[`research-edge-discovery-lab-single-pair-probe-001`](SINGLE_PAIR_PROBE_001_RESULT.md)
classified the EUR_USD / CAMPAIGN_012 +0.0950 R cell as
`SELECTED_CELL_ARTIFACT`. While doing so it surfaced a striking
shape inside the trade ledger of that one cell:

- 91 of 479 trades (19%) exited via `stop` at exactly **−1.000 R**.
- 386 of 479 trades (81%) exited via `time` at mean **+0.226 R**.
- 2 of 479 exited via `eod` at mean −0.221 R.
- The mean-of-fold-means was **+0.0300 R** (positive) while the
  trade-level cumulative R was **−4.391 R** (negative). This is
  exactly the small-n averaging artifact the probe addendum's new
  red flag **R-9** is designed to catch.

The probe addendum
([EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md §A.5](EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md))
explicitly flagged this asymmetry as a candidate **structural** lab
question:

> The lab **may** still queue a follow-up on **time-exit vs
> stop-exit asymmetry across all candidates × all pairs**, because
> the probe's §2.7 observation generalises beyond this one cell.

This sprint is the follow-up. It does not promote any strategy and
it is explicitly distinct from the probe sprint's anomaly.

---

## 2. The exact structural question

> **Q1.** Across CAMPAIGN_010 - CAMPAIGN_014, do `stop` exits
> systematically crystallise the strategy's losses near −1 R while
> `time` exits crystallise systematically smaller, mostly
> positive R values?
>
> **Q2.** Is the resulting payoff shape — a hard −1 R left tail plus
> a thin small-positive right tail — present in the **random-entry
> null** CAMPAIGN_011 as well? In other words, is the asymmetry a
> property of the **strategy family** or the **exit engine**?
>
> **Q3.** Are positive cells in the existing pair-baseline grid (the
> hydrate sprint's table) **dominated** by their time-exit subset
> rather than by genuine edge across both exit modes? Equivalently:
> when a campaign × pair × fold cell looks positive, is it because
> the time exits did better than usual, the stop rate was lower than
> usual, or both?
>
> **Q4.** Does the per-fold variance of the stop-rate (or
> stop-cumulative-R contribution) explain a large share of the
> per-fold variance of expectancy R? If yes, a single fold's
> stop-rate noise can manufacture or destroy an apparent edge — which
> ties directly back to R-9 and the LOO stability screen in the
> probe addendum.

The sprint does **not** ask: "could we make CAMPAIGN_012 work by
loosening the stop?" That would be parameter tuning; out of scope.

---

## 3. Included campaigns and artifacts

All inputs are **already-committed local artifacts**. No broker
calls. No new data pulls. The five campaigns and their trade
artifacts are:

| Campaign | Family | Current verdict | Per-fold per-pair trade CSVs |
|---|---|---|:---:|
| CAMPAIGN_010_session_breakout | session_breakout | REJECT | 56 (7 pairs × 8 folds) |
| CAMPAIGN_011_random_entry_anchor | random_entry (null baseline) | REJECT | 56 |
| CAMPAIGN_012_regime_switcher_atr_percentile | regime_switcher | REJECT | 56 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | currency_strength | REJECT | 56 |
| CAMPAIGN_014_calendar_event_window_anomaly | event_window | REJECT | 56 |

Per-campaign supporting artifacts already loaded by the lab's
`research.edge_discovery.real_data` module:

- `walk_forward/results.json` — fold layout, aggregate verdict.
- `folds/fold_NN/fold_NN_<PAIR>_summary.json` — per-fold per-pair
  metrics dictionary (8 folds × 7 pairs = 56 files per campaign).
- `folds/fold_NN/fold_NN_<PAIR>_trades.csv` — per-trade ledger
  with `entry_time`, `exit_time`, `side`, `r_multiple`, `pnl`,
  `bars_held`, `exit_reason`, `fill_timing`, `spread_paid_pips`,
  `stop_price`, etc. **56 files per campaign × 5 campaigns = 280
  trade files in total.**

`CAMPAIGN_011_random_entry_anchor` is the **binding null**, exactly
as in the prior hydrate and probe sprints. Every per-cell screen this
sprint runs is **paired** with the same cell under CAMPAIGN_011.

CAMPAIGN_010 - CAMPAIGN_014 share the same fold plan (8 folds,
rolling, 7-major universe, identical date span) so per-(campaign,
pair, fold) cells line up across campaigns. The lab's existing
hydrate sprint already verified this; this sprint trusts that
verification and does not re-derive it.

---

## 4. Exit categories

From the trade ledger schema (see
`research/edge_discovery/real_data.py::CAMPAIGN_TRADES_COLUMNS`):

| `exit_reason` | meaning | expected count |
|---|---|---|
| `stop` | hard stop hit; r_multiple is the realised loss including spread/slippage; in the EUR_USD / C012 ledger this was exactly −1.000 R every time | majority of negative R trades |
| `time` | held to time-stop / bars-held budget; exit at the bar that elapsed the strategy's hold horizon | majority of small positive R and small negative R trades |
| `eod` | end-of-day or end-of-window flatten; small subset | rare |

The Phase 1 dataset must report the **full set** of observed
`exit_reason` values across all 5 campaigns and not assume the
three above are exhaustive. Any new value goes into the JSON
output verbatim.

---

## 5. Metrics to compute

### 5.1 Per (campaign, pair, fold, side, exit_reason)

The base cell of the cross-campaign dataset is the 5-tuple

```
(campaign_name, instrument, fold_index, side, exit_reason)
```

For each base cell, Phase 2 reports:

- `n_trades`
- `mean_r`
- `median_r`
- `min_r`, `max_r`, `std_r`
- `sum_r` (cumulative R contributed by this cell)
- `share_of_trades_in_cell_subset_of_(campaign, pair, fold)` —
  what fraction of that pair × fold's trades came from this
  side × exit_reason combination
- `share_of_signed_R_in_cell_subset_of_(campaign, pair, fold)` —
  what fraction of |sum of trade-level R| in the (campaign, pair,
  fold) cell came from this side × exit_reason

### 5.2 Per (campaign, pair, fold) — exit-shape summary

- `stop_rate` = n_stop / n_total
- `time_rate` = n_time / n_total
- `eod_rate` = n_eod / n_total
- `mean_R_given_stop`
- `mean_R_given_time`
- `mean_R_given_eod`
- `share_of_gross_losses_explained_by_stops` =
  Σ |r_multiple|·1{r<0, reason=stop} / Σ |r_multiple|·1{r<0}
- `share_of_gross_gains_explained_by_time_exits` =
  Σ r_multiple·1{r>0, reason=time} / Σ r_multiple·1{r>0}
- `pct_stops_at_or_below_minus_0_95_R`
- `pct_time_exits_in_band_[-0_5,_+0_5]_R`

### 5.3 Per campaign — across folds × pairs

- mean and median of every Section 5.2 metric across the 56 cells.
- per-side breakdown: do longs and shorts share the same stop /
  time pattern, or is one direction asymmetrically punished?
- standard deviation of `stop_rate` across folds (within pair) and
  across pairs (within fold) — this quantifies whether stop-rate is
  a noisy meta-variable that drives per-fold R.

### 5.4 Cross-campaign — comparison vs CAMPAIGN_011 null

For each (pair, fold) — and aggregated per pair, per fold, per
campaign — Phase 3 computes the **gap vs C011** of:

- mean_R_given_stop
- mean_R_given_time
- stop_rate
- share_of_gross_losses_explained_by_stops

A campaign whose stop-given-R and stop-rate **match** C011 is one
where the exit engine is doing the same thing as a random-entry
strategy; any "edge" must therefore be sitting in the time-exit
subset only, which is the small-n masking pattern §1 surfaced.

---

## 6. What counts as a structural failure pattern

A finding is classified **STRUCTURAL_FAILURE_PATTERN** if **all**
of the following hold across the 5-campaign × 7-pair × 8-fold grid:

1. **Universal hard stop**: ≥ 90% of `stop` trades, across all 5
   campaigns, have `r_multiple ≤ −0.95`.
2. **Universal time-exit small-positive shape**: ≥ 70% of `time`
   trades, across all 5 campaigns, fall in the band
   `r_multiple ∈ [−0.5, +0.5]`, and the campaign-level
   `mean_R_given_time` is positive for ≥ 4 / 5 campaigns
   *including* the null CAMPAIGN_011.
3. **Null shares the shape**: CAMPAIGN_011's `mean_R_given_stop`
   and `stop_rate` are within ±0.05 of the median of CAMPAIGN_010,
   012, 013, 014. Equivalently: the random-entry null produces
   the same exit shape as the real strategies, so the shape is an
   **exit-engine** property, not a strategy property.
4. **Fold-noise driver**: the per-fold standard deviation of
   `stop_rate` (within a campaign × pair) is ≥ 0.05 — i.e., a
   single fold can have a stop rate 5+ percentage points off the
   pair-average, large enough to flip a small mean-of-means
   positive cell into negative once you condition on the stop-heavy
   fold.

If all four conditions hold, the structural failure pattern is
**confirmed cross-campaign**. The implication is that any candidate
strategy using this exit engine inherits the same fragile shape, and
the lab cannot tell signal from stop-rate noise on a single grid
cell.

## 7. What counts as an interesting but non-actionable finding

Several adjacent observations are plausible and would be valuable to
record but **must not** become approval / promotion paths:

- **Per-direction asymmetry**: longs and shorts may have meaningfully
  different stop / time patterns inside a single campaign × pair.
  This is interesting and goes into the result doc, but it is **not**
  a "this strategy works for shorts only" finding because the per-
  direction cells are still subject to the same LOO / t-stat / median
  / R-9 screens the probe addendum installed, and on small per-
  direction cells the screens will more often than not refuse.
- **One campaign appears materially better on time-exit R**:
  documented, but does not change the campaign's REJECT verdict and
  does not propose an exit-only "strategy".
- **A specific pair behaves differently from the other six**:
  recorded as a pair-shape note. **Not** a promotion path. The
  probe sprint's §A.1 makes explicit that ≥ 1 above-floor cell in
  a 28-cell grid is the chance expectation under a no-edge null.
- **A specific time-of-day / session / event-window window has a
  noticeably better mean R given time-exit**: recorded as a future
  lab idea (the existing
  [EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md](EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md)
  already lists session / event sub-slice probes as the natural
  next narrow studies). This sprint does not run those sub-slice
  studies itself.

---

## 8. Classification buckets for any candidate cell

Carrying the probe-addendum vocabulary forward, any (campaign, pair,
fold, side, exit_reason) cell that shows a positive gap vs C011's
matched cell is classified into one of:

| bucket | required conditions |
|---|---|
| `STRUCTURAL_FAILURE_PATTERN` | the cross-grid §6 conditions all hold |
| `NULL_LIKE_BEHAVIOR` | the cell's mean R and stop rate are within ±0.05 / ±0.05 of the same cell under C011 |
| `ISOLATED_SELECTED_CELL_ARTIFACT` | the cell looks above-floor on the headline gap but fails ≥ 1 of: LOO stability, t-stat ≥ 2, median per-fold R ≥ 0, R-9 (mean-of-means positive while sum-of-trades-R negative) |
| `PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL` | passes ≥ 4 of the 5 robust probe-addendum sub-criteria, but does not pass all 5 — i.e., interesting enough to record but **not** sufficient to recommend a campaign or a new candidate |
| `INSUFFICIENT_DATA` | the cell has < 20 trades or < 4 folds with non-zero trade count, so the screens cannot fire reliably |

`PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL` is **not** a green light. It
is a recorded observation for the lab's standing rules; the next
sprint that wants to investigate it must propose a separate
narrow-scope probe (per the probe addendum §A.1, the lab now requires
**two** above-floor cells or **one** LOO-stable cell in a multi-cell
grid before further work is queued — and `PROMISING_BUT_INSUFFICIENT`
is by definition neither).

---

## 9. Why this sprint cannot approve or revive any strategy

1. **The 5 campaigns under study are all REJECT.** Their REJECT
   status is anchored in their walk-forward `results.json`, their
   per-fold gate-fail counts, and their committed evidence summaries.
   This sprint reads those artifacts; it does not regenerate the
   underlying backtests.
2. **The lab's verdict-word ban remains in force.** Outputs of
   this sprint do not use APPROVE / PASS / PROMOTE / SHIP / GO-LIVE
   in any classification field.
3. **Even a confirmed structural failure pattern would not approve
   anything.** The implication of confirmation is that future
   candidates need a **pre-campaign exit-shape screen**, not that
   any existing candidate can be salvaged by tuning its stop.
4. **CAMPAIGN_011 is the random-entry null.** Any "edge" the sprint
   finds inside C011's ledger by definition is not an edge — it
   describes the exit engine. Any pattern shared with C011 cannot
   be elevated into a candidate.
5. **The single-pair probe sprint already documented the standing
   rule.** Per
   [EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md §A.1](EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md),
   future proposals must show **≥ 2 above-floor cells in the
   per-pair-baseline grid** or **a single LOO-stable cell**. The
   diagnostic question here is structural, not single-cell;
   anything cell-shaped that surfaces inherits the §A.1 standing
   rule and is **stopped at the lab**.
6. **`configs/approved_strategies.yaml` will remain `approved: []`.**
   No yaml change is in scope.

The deliverables at the end of this branch are: a diagnosis
document, a cross-campaign exit dataset under
`research/edge_discovery/studies/outputs/real/`, a possible new
pre-campaign screen captured as an addendum, and binding tests that
pin the headline observations. **No campaign change, no candidate
proposal, no approval.**

---

## 10. Outputs the sprint will produce

| Phase | Path | Type |
|---|---|---|
| 0 | `docs/research/EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_PLAN.md` | plan (this doc) |
| 1 | `research/edge_discovery/studies/exit_asymmetry_cross_campaign.py` | extraction + base aggregation script |
| 1 | `research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.{json,md}` | extraction outputs |
| 2 | analysis tables embedded in the Phase 1 outputs (extraction and analysis run together; see Phase 2 §11.2 below) | — |
| 3 | `research/edge_discovery/studies/exit_asymmetry_robustness.py` | null-comparison + LOO / R-9 / t-stat screens for any above-floor cells |
| 3 | `research/edge_discovery/studies/outputs/real/exit_asymmetry_robustness.{json,md}` | robustness outputs |
| 3 | `tests/research/edge_discovery/test_exit_asymmetry.py` | binding pins for headline observations |
| 4 | `docs/research/EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_RESULT.md` | interpretation doc |
| 5 | `docs/research/EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md` | new lab-rule addendum (if justified by §6 / §7 outcomes) |
| 5 | `docs/research/EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_SUMMARY.md` | sprint summary |

Per the probe sprint convention, every JSON output carries a
`provenance` block (kind `real`, exploratory_only `True`, list of
sha-256-anchored inputs) and acknowledges the lab's verdict-word ban
via `verdict_word_ban_acknowledged: True`.

---

## 11. Phasing

### 11.1 Phase 0 (this doc) — committed at end of phase

- Plan written and committed.
- Baseline freeze / archive / secret-scan / lab-test gates run and
  green.
- `configs/approved_strategies.yaml` re-verified as `approved: []`.

### 11.2 Phase 1 + Phase 2 — extraction + analysis (run together)

The user brief separates these into two phases, but extraction and
descriptive aggregation share data; the script computes them in one
pass and writes one `.json` / `.md` pair. The Phase 1 commit message
will explicitly name both phases.

The script:

1. Loads all 280 trade CSVs (5 campaigns × 7 pairs × 8 folds) via
   `research.edge_discovery.real_data.load_campaign_trades`.
2. Joins per-fold per-pair metadata from
   `load_campaign_fold_pair_summaries`.
3. Computes the §5.1 base-cell metrics and the §5.2 / §5.3 / §5.4
   aggregates.
4. Writes JSON + MD outputs. **Does not commit raw concatenated
   trades CSV** (would be a large derived file); the JSON output
   carries the aggregates only.

### 11.3 Phase 3 — robustness + null comparison

- For every campaign × pair cell whose mean R gap vs C011 exceeds
  +0.05 R, run: LOO, t-stat ≥ 2 SE, median ≥ 0, R-9
  (mean-of-means vs sum-of-trades), top-fold dominance, neighbouring
  pair / candidate isolation.
- Classify each into one of the §8 buckets.
- Write `exit_asymmetry_robustness.{json,md}` and the binding pin
  tests in `tests/research/edge_discovery/test_exit_asymmetry.py`.

### 11.4 Phase 4 — interpretation

- `EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_RESULT.md` answers Q1 - Q4
  with the numbers from Phases 1 - 3.
- Includes a "what this does NOT propose" section enumerating the
  pre-committed refusals.

### 11.5 Phase 5 — addendum + summary + final validation

- If §6 confirmed STRUCTURAL_FAILURE_PATTERN, write
  `EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md` adding mandatory
  pre-campaign exit-shape screens to the candidate-ranking rules.
- If §6 did not confirm — i.e., the shape was specific to a subset —
  the addendum still goes in but only as a softer "report this when
  surfacing above-floor cells" reporting requirement.
- Write `EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_SUMMARY.md`.
- Run focused lab tests, full pytest, ruff on touched files,
  freeze / archive / secret-scan, and paper / demo refusal probes.

---

## 12. Pre-committed refusals

Even before any data is loaded, this branch refuses, by construction,
to:

- Approve any strategy or family.
- Reverse, soften, or extend any CAMPAIGN_010 - 014 verdict.
- Propose a parameter change to any existing campaign's stop / time
  exit.
- Propose a new candidate strategy.
- Emit a markdown file containing APPROVE / PASS / PROMOTE / SHIP /
  GO-LIVE / GREEN-LIGHT in any classification field.
- Touch `configs/approved_strategies.yaml`, `forex_bot.broker`,
  `forex_bot.loops`, `forex_bot.approval`, or `forex_bot.execution`.

These refusals are pinned in
`tests/research/edge_discovery/test_exit_asymmetry.py` via tests
that re-verify:

- `verdict_word_ban_acknowledged` is True in every JSON output.
- The result markdown files do not contain banned verdict words in
  any classification context.
- `provenance.exploratory_only` is True.
- The configs yaml remains `approved: []` (already pinned by the
  existing test suite; reasserted here for clarity).

---

## 13. Baseline check log (Phase 0)

Before this plan was committed, on this branch:

- `python -m pytest tests/research/edge_discovery/` — **111 / 111 passed**.
- `python scripts/check_research_freeze.py` — `ALL CHECKS PASSED`.
- `python scripts/validate_research_archive.py` — `ALL CHECKS PASSED`.
- `python scripts/scan_artifacts_for_secrets.py` — `PASSED` (no
  credential value or credential-shaped strings).
- `configs/approved_strategies.yaml` — `approved: []`.

The lab is in its expected resting state on entry to this sprint.

---

## 14. Expected outcomes

Most likely (probability rank, lab's prior given the probe finding):

1. **The structural pattern holds**, including in CAMPAIGN_011's
   null ledger. The lab's existing exit engine produces a hard −1 R
   stop tail by construction, and the small positive time-exit
   shape is a drift / mean-reversion artifact of fixed-bar holds.
   The pre-campaign screen this sprint proposes will require
   future candidates to demonstrate **edge in their stop-exit
   subset** (or in their distribution shape, not just mean-of-means)
   before lab time is allocated to a follow-up.
2. **The pattern holds but is one campaign or pair-specific.**
   The addendum still goes in but with narrower wording.
3. **The pattern does not hold cross-campaign.** Unlikely given the
   probe finding but plausible. The Phase 4 result doc still
   recommends per-(exit_reason, side) reporting in standard cell
   evaluation, and the addendum becomes a reporting requirement
   rather than a screen.

In all three outcomes, no campaign is reversed, no candidate is
proposed, and `configs/approved_strategies.yaml` stays
`approved: []`.
