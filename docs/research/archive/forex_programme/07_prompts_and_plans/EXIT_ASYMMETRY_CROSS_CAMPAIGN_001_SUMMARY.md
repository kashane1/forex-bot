# Cross-Campaign Exit-Asymmetry Sprint — Summary

**Sprint:** `research-exit-asymmetry-cross-campaign-001`
**Phase:** 5 (sprint summary + handoff)
**Date:** 2026-05-24
**Status:** Sprint complete. **No strategy approved.** **No campaign
verdict changed.** Paper / demo / live remain blocked.
`configs/approved_strategies.yaml` stays `approved: []`.

---

## 1. What this sprint did

Studied whether the stop / time-exit payoff asymmetry that
surfaced inside the EUR_USD / CAMPAIGN_012 falsification probe is
a recurring **structural** failure mode across CAMPAIGN_010 -
CAMPAIGN_014, or whether it was incidental to one cell.

The answer is unambiguous: **it is structural**. Every campaign,
including the random-entry null CAMPAIGN_011, exhibits the same
shape:

> Hard −1 R stop tail + small-positive time-exit body → ≥ 98 %
> of every campaign's gross gains come from time exits, and the
> null campaign has the **highest** `mean_R_given_time` of all
> five.

The shape is an **exit-engine artifact**, not strategy edge. The
exit engine is doing its job; entry signals tested on top of it
do not add anything materially different from random entry on the
time-exit subset.

This was a **descriptive, diagnostic** sprint. No strategy was
proposed, no campaign was reversed, no parameter was tuned.

---

## 2. Files produced

### 2.1 Plan and result docs (`docs/research/`)

| Phase | File |
|---|---|
| 0 | [`EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_PLAN.md`](EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_PLAN.md) — study plan |
| 4 | [`EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_RESULT.md`](EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_RESULT.md) — interpretation |
| 5 | [`EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md`](EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md) — new pre-campaign screen |
| 5 | this file — sprint summary |

### 2.2 Lab study scripts (`research/edge_discovery/studies/`)

| Phase | File |
|---|---|
| 1 + 2 | `exit_asymmetry_cross_campaign.py` — extraction + descriptive aggregation |
| 3 | `exit_asymmetry_robustness.py` — probe-addendum screens + R-9 sweep |

### 2.3 Lab outputs (`research/edge_discovery/studies/outputs/real/`)

| Phase | File pair |
|---|---|
| 1 + 2 | `exit_asymmetry_cross_campaign.{json, md}` |
| 3 | `exit_asymmetry_robustness.{json, md}` |

### 2.4 Tests (`tests/research/edge_discovery/`)

- `test_exit_asymmetry.py` — 26 binding tests pinning the headline
  observations.

---

## 3. Commits by phase

| Phase | SHA | Title |
|---|---|---|
| 0 | `af40856` | study plan + orientation |
| 1 + 2 | `9b3d415` | cross-campaign exit dataset + descriptive aggregation |
| 3 | `92af040` | robustness screens + binding tests |
| 4 | `1ee9966` | interpretation + RESULT doc |
| 5 | _this commit_ | addendum + sprint summary + final validation |

---

## 4. Campaigns and artifacts included

| Campaign | Trade CSVs loaded | Total trades |
|---|---:|---:|
| CAMPAIGN_010_session_breakout | 56 (7 × 8) | 2,791 |
| CAMPAIGN_011_random_entry_anchor (null) | 56 | 1,177 |
| CAMPAIGN_012_regime_switcher_atr_percentile | 56 | 3,726 |
| CAMPAIGN_013_cross_pair_currency_strength_rotation | 56 | 7,940 |
| CAMPAIGN_014_calendar_event_window_anomaly | 56 | 720 |
| **total** | **280** | **16,354** |

All artifacts already-committed local files; no broker calls; no
new data pulls. Every output JSON carries a `provenance` block
with sha-256 anchors and `data_kind = "real"`,
`exploratory_only = True`.

---

## 5. Key findings

### 5.1 Cross-campaign exit shape (Phase 1 + 2)

| campaign | n | stop_rate | mean_R_given_stop | mean_R_given_time | mean_R_overall | share_loss_from_stops | share_gain_from_times |
|---|---:|---:|---:|---:|---:|---:|---:|
| CAMPAIGN_010 | 2,791 | 0.237 | −0.79 | **+0.193** | −0.041 | 0.69 | 0.99 |
| CAMPAIGN_011 (null) | 1,177 | 0.205 | −0.83 | **+0.209** | −0.002 | 0.67 | 0.99 |
| CAMPAIGN_012 | 3,726 | 0.204 | −0.82 | **+0.145** | −0.052 | 0.63 | 1.00 |
| CAMPAIGN_013 | 7,940 | 0.231 | −0.95 | **+0.211** | −0.056 | 0.68 | 1.00 |
| CAMPAIGN_014 | 720 | 0.242 | −0.81 | **+0.067** | −0.148 | 0.64 | 1.00 |

- **All five campaigns lose overall.**
- **All five have positive `mean_R_given_time`.**
- **CAMPAIGN_011 (random-entry null) has the highest
  `mean_R_given_time`.** No entry signal beats the null on the
  time-exit subset.
- **≥ 98 %** of every campaign's gross gains come from time exits.

### 5.2 Structural-pattern check (Phase 1 + 2)

Classification: **`STRUCTURAL_FAILURE_PATTERN_PARTIAL`**

| Phase 0 condition | observed | PASS? |
|---|---|:---:|
| 1. Universal hard stop (≥ 90 % stops ≤ −0.95 R) | 0.64 - 0.86 | ✗ |
| 2. Universal small-positive time shape (≥ 70 % in band) | 0.63 - 0.74 | ✗ |
| 3. Null shares the shape (|Δ| ≤ 0.05 vs median of others) | Δ ≤ 0.03 | ✓ |
| 4. Fold-noise driver (median per-pair stop_rate σ ≥ 0.05) | 0.061 | ✓ |

Conditions 1 and 2 fail the strict numerical thresholds the plan
set, but the qualitative pattern (stop median R = exactly −1.000
in every campaign, ≥ 98 % of gross gains from time exits, 5 / 5
campaigns with positive `mean_R_given_time`) is intact. Conditions
3 and 4 — the ones that justify the new pre-campaign screen — pass
cleanly.

### 5.3 Robustness sweep (Phase 3)

- 35 (campaign, pair) cells evaluated.
- **R-9 fires on exactly 1 / 35 cells**: EUR_USD / CAMPAIGN_012
  (the cell the prior probe sprint already classified as
  SELECTED_CELL_ARTIFACT). R-9 is selective.
- 29 / 35 cells have negative cumulative R.
- 29 / 35 cells have negative median per-fold mean R.
- The single above-floor cell on `mean_R_given_time` vs C011
  (CAMPAIGN_013 × EUR_USD, gap = +0.0531 R) classifies as
  **`INSUFFICIENT_DATA`** under the lab's paired-fold threshold
  (only 5 of 8 folds had paired time-exit data; the apparent gap
  is stop-rate-driven at correlation = −0.79).
- **No cell classifies as `PROMISING_BUT_INSUFFICIENT_LAB_SIGNAL`
  or stronger.**

---

## 6. New lab rule

Phase 5 installs a new pre-campaign exit-shape screen as a binding
rule in
[`EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md`](EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md).
Briefly:

- **B.1 Material time-exit lift over null:** candidate
  `mean_R_given_time` must beat C011's by ≥ +0.05 R on the matched
  fold plan, with either LOO stability or ≥ 2 above-floor cells
  per the probe addendum §A.1.
- **B.2 Stops not worse than null's:** candidate
  `mean_R_given_stop` ≥ C011's − 0.05 R.
- **B.3 No R-9:** mean-of-means must not be positive while
  cumulative-R is negative.
- **B.4 Per-fold stop-rate dispersion bounded:** per-pair
  stop_rate σ across the 8 folds must be ≤ 0.06.

Plus four new reporting requirements (C.1 - C.4): every above-
floor cell must report mean-vs-cumulative R, per-exit-reason mean R,
per-side metrics, and per-fold stop_rate trajectory.

These are **necessary, not sufficient**, conditions for promotion.
No existing candidate clears them.

---

## 7. Final validation (Phase 5)

| Check | Result |
|---|:---:|
| `pytest tests/research/edge_discovery/ -q` (137 tests, 26 new) | ✓ |
| `pytest -q` (full suite) | ✓ |
| `ruff check research/edge_discovery/studies/ tests/research/edge_discovery/` | ✓ |
| `python scripts/check_research_freeze.py` | ✓ ALL CHECKS PASSED |
| `python scripts/validate_research_archive.py` | ✓ ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | ✓ PASSED |
| `configs/approved_strategies.yaml` | `approved: []` |
| Paper-loop refusal | ✓ blocked |
| Demo-loop refusal | ✓ blocked |
| Live-loop refusal | ✓ blocked |

---

## 8. Was any strategy approved?

**No.** The lab does not propose to approve, paper-trade, demo-
trade, or live-trade any strategy on the basis of this sprint's
findings.

CAMPAIGN_010 - CAMPAIGN_014 remain REJECT-anchored. The exit-
asymmetry diagnosis reinforces but does not reverse their REJECT
verdicts. The new pre-campaign screen is a **filter** on future
proposals, not a re-evaluation of past ones.

`configs/approved_strategies.yaml` is unchanged and remains
`approved: []`.

---

## 9. Files to review first

For a reviewer onboarding to this sprint, the most efficient
reading order is:

1. **[`EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_PLAN.md`](EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_PLAN.md)**
   — the structural question, included artifacts, and pre-committed
   refusals.
2. **[`research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.md`](../../research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.md)**
   — the cross-campaign exit-shape tables and the §6 structural-
   pattern check verdict.
3. **[`research/edge_discovery/studies/outputs/real/exit_asymmetry_robustness.md`](../../research/edge_discovery/studies/outputs/real/exit_asymmetry_robustness.md)**
   — the R-9 sweep, the per-(campaign, pair) fold dispersion, and
   the screened-cell classification.
4. **[`EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_RESULT.md`](EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_RESULT.md)**
   — answers to Q1-Q4, implications for the lab process, and the
   pre-committed list of what this sprint does *not* propose.
5. **[`EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md`](EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md)**
   — the new pre-campaign screen (B.1 - B.4) and the new reporting
   requirements (C.1 - C.4).
6. **[`tests/research/edge_discovery/test_exit_asymmetry.py`](../../tests/research/edge_discovery/test_exit_asymmetry.py)**
   — the binding pins on the headline numbers.

---

## 10. Recommended next branch

In order of cheapness × informativeness:

1. **`research-bias-of-fixtures-audit-001`** — grounds the lab in a
   known no-edge baseline. Required to be confident in the
   CAMPAIGN_011 null underneath the new pre-campaign screen.
   Cheapest of the three.
2. **`research-per-hour-time-exit-001`** — extends the hydrate
   sprint's session study and probes whether the small-positive
   time-exit subset has any hour-of-day exploitable substructure
   that survives the new screen. Moderate cost.
3. **`research-campaign-014-ecb-boe-shorts-only-001`** — carry-over
   from the hydrate sprint's recommended next-3. Untouched by both
   the probe sprint and this sprint. Moderate cost. The new screen
   raises the bar before any such probe could recommend a follow-up.

**Explicitly NOT recommended**: a follow-up probe of the
CAMPAIGN_013 × EUR_USD `mean_R_given_time` cell. It correctly
classifies as `INSUFFICIENT_DATA` and its apparent gap is
stop-rate-driven (corr = −0.79). A future probe would be the
second time the lab spent a sprint falsifying a single-cell
anomaly, and the probe-addendum's §A.1 standing rule says: do not
queue.

---

## 11. One-line takeaway

> Across 16,354 trades in CAMPAIGN_010 - CAMPAIGN_014, the lab's
> exit engine produces a hard −1 R stop tail + small-positive
> time-exit body in every campaign including the random-entry
> null — and the null has the **highest** mean time-exit R. The
> exit shape is an engine artifact; no tested entry signal adds
> measurable lift on top of it. New lab rule: candidates must
> beat the null on the time-exit subset, not have wrong-direction
> stops, not fire R-9, and not have noisy per-fold stop-rate
> dispersion, **before** they get campaign time. No strategy
> approved. CAMPAIGN_010 - CAMPAIGN_014 stay REJECT.
> `configs/approved_strategies.yaml` stays `approved: []`.
