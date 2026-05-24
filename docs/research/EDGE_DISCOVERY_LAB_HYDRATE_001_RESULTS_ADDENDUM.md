# Edge Discovery Lab — Hydrate Sprint 001 Results Addendum

**Sprint:** `research-edge-discovery-lab-hydrate-001` · Phase 4
**Date:** 2026-05-24
**Status:** Addendum to
[`EDGE_DISCOVERY_LAB_001_RESULTS.md`](EDGE_DISCOVERY_LAB_001_RESULTS.md).
What changed after pointing the lab at real local artifacts.
**No strategy approved. No campaign verdict altered.** Paper /
demo / live loops still refuse every configured strategy.

---

## 1. What this addendum covers

The prior `EDGE_DISCOVERY_LAB_001_RESULTS.md` documents the
**synthetic-fixture** baseline run. This addendum is the **real-data**
counterpart: same four studies, same lab module, same null-band
analysis, but every input is now a real local artifact (the
committed CAMPAIGN_010-014 walk-forward results / per-fold summaries
/ per-fold trade CSVs, the committed CAMPAIGN_014 event fixture, and
— for the session study — the operator-local H4 OHLC SQLite store).

The prior sprint's synthetic outputs are committed and **unchanged**.
The new real-data outputs land under
`research/edge_discovery/studies/outputs/real/` so the audit trail
keeps both runs side-by-side.

## 2. Headline real-data findings (descriptive only)

### 2.1 Event-window study — real CAMPAIGN_014 trades + real fixture

Output: [`research/edge_discovery/studies/outputs/real/real_study_event_window.md`](../../research/edge_discovery/studies/outputs/real/real_study_event_window.md)

| dimension | real value | what it says |
|---|---:|---|
| n trades | 720 | every trade from the committed CAMPAIGN_014 per-fold per-pair CSVs |
| overall mean R | **−0.1477** | identical to the published CAMPAIGN_014 aggregate (cross-check passes) |
| CAMPAIGN_011 null mean R | −0.0024 | binding null floor per [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) |
| gap vs null | **−0.1453 R** → `materially_below_null` | the strategy lost to a random-entry null on the same universe by 0.145 R per trade |
| NFP dominance share | **79.3 %** (571 / 720) | far above the §2 R-3 cap; pair-concentration's event-class analogue |
| FOMC matched trades | **0** (within ±24 h of any fixture event) | exactly the zero-trade-class failure mode the meta-analysis warned about; R-6 red flag triggers |
| BoE shorts mean R | +0.380 (n = 22) | tiny n; positive only on shorts, negative on longs (asymmetry) |
| ECB shorts mean R | +0.318 (n = 27) | same asymmetric pattern; small n |

The synthetic event-window study's headline was `within_null` —
which was the correct answer for a 6-event GBM fixture. The
real-data answer is **materially below the null**, plus the exact
dominance / zero-trade-class signature the brief warned about. **The
synthetic-study conclusion ("the test rig is wired right") still
stands; the real-data rerun adds a substantive falsification of the
CAMPAIGN_014 design** without changing CAMPAIGN_014's already-
recorded REJECT verdict.

### 2.2 Turnover-cost study — five rejected campaigns, real ledgers

Output: [`research/edge_discovery/studies/outputs/real/real_study_turnover_cost.md`](../../research/edge_discovery/studies/outputs/real/real_study_turnover_cost.md)

| campaign | trades | mean R obs | mean R pub | obs vs pub | observed avg spread (pips) | verdict |
|---|---:|---:|---:|---:|---:|---|
| CAMPAIGN_010 session_breakout | 2,791 | −0.0408 | −0.0408 | ✓ identical | 1.63 | REJECT |
| CAMPAIGN_011 random_entry_anchor | 1,177 | **−0.0024** | −0.0024 | ✓ identical | 1.73 | REJECT (null model) |
| CAMPAIGN_012 regime_switcher | 3,726 | −0.0521 | −0.0521 | ✓ identical | 1.75 | REJECT |
| CAMPAIGN_013 cross_pair_strength | 7,940 | −0.0564 | −0.0564 | ✓ identical | 1.73 | REJECT |
| CAMPAIGN_014 calendar_event_window | 720 | −0.1477 | −0.1477 | ✓ identical | 1.69 | REJECT |
| **cross-campaign totals** | **16,354** | — | — | | 1.71 | 5/5 REJECT |

Cross-checks:

- **Observed = published** for every campaign to 1e-3 R precision.
  The committed per-fold per-pair trade CSVs faithfully reconstruct
  the published aggregate expectancy R. This is a clean integrity
  result for the campaign artifacts themselves.
- **Zero campaigns have a positive pre-cost edge per trade** on the
  real data. Lesson 2 (cost / turnover is the most common cause of
  failure) is corroborated: every rejected campaign lands either at
  or below the random-entry null per trade.
- **CAMPAIGN_011 hugs zero (−0.0024 R)** — the random-entry null
  model behaves as designed, validating its use as the binding floor
  for future candidates.

The synthetic turnover-cost matrix (cost-per-trade `+0.000173`
log-units on EUR_USD) remains correct in shape. The real-data
addition: the matrix's "any candidate below cost-per-trade is
turnover-negative" diagonal has now been **populated with five real
rejected campaigns**, every one of which sits on or below that
diagonal — empirical corroboration of the gate at §4 of the ranking
rules.

### 2.3 Pair-baseline study — per-pair fold expectancy vs CAMPAIGN_011

Output: [`research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md`](../../research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md)

CAMPAIGN_011 provides the **per-pair** random-entry null (one mean
expectancy R per pair, averaged across 8 walk-forward folds). Best
gap to that null in any of CAMPAIGN_010 / 012 / 013 / 014:

| pair | CAMPAIGN_011 null R | best candidate | best gap R | clears +0.05 floor? |
|---|---:|---|---:|:---:|
| EUR_USD | −0.0650 | CAMPAIGN_012 (regime_switcher) | **+0.0950** | ✓ |
| GBP_USD | +0.0756 | CAMPAIGN_013 (cross_pair) | −0.0907 | ✗ |
| USD_JPY | +0.0000 | CAMPAIGN_012 | +0.0004 | ✗ |
| AUD_USD | −0.0415 | CAMPAIGN_013 | +0.0105 | ✗ |
| USD_CAD | −0.0069 | CAMPAIGN_013 | −0.0048 | ✗ |
| USD_CHF | +0.0269 | CAMPAIGN_010 | −0.0070 | ✗ |
| NZD_USD | −0.0986 | CAMPAIGN_013 | +0.0183 | ✗ |
| **above-null pairs** | — | — | — | **1 / 7** |

**Only one (pair, campaign) cell** cleared the +0.05 R material
gap: EUR_USD under CAMPAIGN_012 (regime_switcher_atr_percentile).
CAMPAIGN_012's overall verdict was REJECT and remains REJECT — the
positive-on-one-pair pattern is exactly Lesson 3 (pair concentration
without diagnosis); a single pair cleared the floor while the rest
of the universe stayed below it. This single-pair survivor is the
strongest reason **not** to retire the EUR_USD-on-regime-switcher
hypothesis silently; but it is also not, by itself, evidence for an
edge. It is a candidate the next sprint may probe further (as a
single-pair declared candidate per §1.5 of the ranking rules).

The prior synthetic-fixture pair-baseline study's headline (best gap
≈ `+0.05` R on EUR_USD via CAMPAIGN_008 validation-only) **still
holds in spirit**, but the real-data version replaces the
synthetic-citation table with per-fold-summary aggregates and
re-anchors the null floor from CAMPAIGN_005 universe-mean to
CAMPAIGN_011 per-pair — a more apples-to-apples comparison.

### 2.4 Session study — real EUR_USD H4, 2020–2026

Output: [`research/edge_discovery/studies/outputs/real/real_study_session_by_hour.md`](../../research/edge_discovery/studies/outputs/real/real_study_session_by_hour.md)

| dimension | value |
|---|---:|
| signals (H4 closes used) | **9,927** (real EUR_USD bars 2020-01-01 → 2026-05-19) |
| overall mean post-cost (LONG forward 4 bars) | −0.000197 |
| CAMPAIGN_011-style null mean | −0.000191 |
| null std (across 20 seeds) | 0.000041 |
| overall band | `within_null` |

Hours flagged `materially_above_null` by the lab's per-hour band
(UTC_02, UTC_06, UTC_13) all sit at absolute means of ≈ `−0.00007`
— statistically distinguishable from the null distribution in the
descriptive sense, but **the absolute level is essentially zero and
nowhere near the lab's R-unit material-gap floor**. This is exactly
the kind of "the lab's band-classifier sees structure that an R-unit
ranking rule should not promote" pattern the ranking rules' §1.4
("per-trade pre-cost edge clears cost-per-trade with margin") were
designed to catch.

**Takeaway:** the lab's null-band classifier and the lab's R-unit
material-gap floor are two **different** screens. A study can pass
the null-band classifier on absolute terms (signal distinguishable
from random noise) without passing the material-gap floor (gap
large enough to matter after costs). The ranking rules require both;
this run is a worked example of the distinction.

## 3. Do the prior synthetic-study conclusions still hold?

| conclusion (synthetic baseline) | status after real data |
|---|---|
| The lab's null-band machinery is wired right; `within_null` on a 6-event GBM fixture is the right answer | ✓ holds |
| Cost-per-trade ≈ `+0.000173` log-units on EUR_USD; the turnover-amplification diagonal is correct | ✓ holds; now empirically populated by 5 rejected campaigns |
| Lesson 3 pair-concentration shows up in the artifact-backed table for CAMPAIGN_002 / 003 / 007 | ✓ holds; now extended into CAMPAIGN_010 / 012 / 013 / 014 too |
| The synthetic session study is a capability check, not a finding | ✓ holds; the real-data session study confirms the lab can handle a 9,927-row real H4 frame |
| Brief's CAMPAIGN_014 NFP-dominance / FOMC-zero-trades narrative would surface if the real fixture lands | ✓ **confirmed empirically** (79.3 % / 0 trades) |
| CAMPAIGN_005 is the lab's binding null baseline | ✗ **replaced by CAMPAIGN_011 per its NULL_BASELINE_INTERPRETATION** — see §4 below |
| The candidate-ranking material-gap floor is +0.05 R | ✓ holds; 1/7 pairs (EUR_USD / CAMPAIGN_012) clears it on real data |

## 4. CAMPAIGN_011 replaces CAMPAIGN_005 as the binding null baseline

This is the single most important reclassification this sprint
produces. From [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md):

> CAMPAIGN_011 is the null model — it is NOT a trading candidate. It
> is a measurement instrument.

Both CAMPAIGN_005 and CAMPAIGN_011 are random-entry baselines. The
difference:

| dimension | CAMPAIGN_005 (Benchmark 3) | CAMPAIGN_011 (random_entry_anchor) |
|---|---|---|
| sprint phase | broad benchmark over universe | walk-forward, same fold layout as CAMPAIGN_010+ |
| folds | none — universe mean | **8** rolling-window folds |
| hold | fixed 30 H4 bars | random-anchor + same exit logic as CAMPAIGN_010 family |
| seed control | 20 seeds, matched frequency | `master_seed = 20260523`, frozen |
| pair-level resolution | per-pair mean | per-pair per-fold mean (56 cells) |
| committed artifacts | report Markdown only | full walk_forward/{results, plan, fold_detail}.json + 56 per-fold per-pair summaries + 1,177 trade rows |
| financing overlay | n/a | ESTIMATED + conservative stress |
| use case | universe-level "is this candidate beating chance overall?" | per-pair per-fold "is this candidate beating chance on the same fold layout it has to clear?" |

Going forward:

- The §3 cite ("universe mean = −0.095 R from CAMPAIGN_005") is
  **deprecated** as the binding floor; it stays as a secondary
  cross-reference for the fixed-30-bar shape only.
- The new binding null is the per-pair mean expectancy R from
  CAMPAIGN_011 (the column in §2.3 above). A future real candidate
  must clear this per-pair table by the material gap (+0.05 R) on
  whichever pairs it claims to work on — same fold layout, same
  data, same exit logic.
- The lab's existing CAMPAIGN_005-anchored `study_pair_baseline.py`
  is not deleted; it stays as a historical synthetic-citation study.
  The new `study_real_pair_baseline.py` is the binding artifact.

## 5. Hypotheses worth studying next, ranked

These are **lab-study** hypotheses, not campaign candidates. None of
them is authorized to produce a verdict. Ranking is rough priority.

1. **EUR_USD under CAMPAIGN_012 regime-switcher — single-pair
   declared candidate?** The only (pair, candidate) cell that
   cleared the +0.05 R material gap vs CAMPAIGN_011 in real data.
   Question: is the +0.0950 R gap robust to (a) a 2× cost-stress
   rerun, (b) an out-of-sample split using CAMPAIGN_002's H4 store
   2020-2021 as a hold-out, (c) per-fold consistency (does it appear
   in ≥ 4 of 8 folds, or is one fold carrying it)? Park as
   "validation-only — second-window check required" if (b) or (c)
   fail. Lab can run this with the existing loaders; no new module.
2. **Non-NFP event windows — ECB / BoE shorts only.** The real
   event-window study shows ECB shorts at +0.318 R (n = 27) and BoE
   shorts at +0.380 R (n = 22), with longs negative. **n is too
   small to graduate** but a follow-up study extending the
   tolerance window (the lab's current ±24 h is conservative; the
   campaign's IMPLEMENTATION_SPEC entry window is tighter) and
   restricting to SHORT side may surface enough sample to test
   honestly. Lab study; no campaign.
3. **Per-fold consistency probe for the EUR_USD / CAMPAIGN_012
   cell.** Pull all 8 folds' per-pair EUR_USD expectancy R; if one
   fold's +0.40 R is dragging the average and the other 7 are flat,
   the cell is fold-concentrated (analogue of pair-concentration).
   Single-script extension of the existing
   `study_real_pair_baseline.py`.

## 6. Ideas to stop early

- **Aggregate "calendar event window anomaly" as a strategy
  template.** The real data shows the gap to null is −0.145 R per
  trade with NFP dominance ~80 %. No follow-up campaign on the
  aggregate template — only the narrowly-declared sub-questions in
  §5 are worth lab time.
- **Pair-broad turnover-amplification candidates.** Cross-campaign
  rollup shows ZERO pre-cost positive per-trade edges in the real
  data across 16,354 trades. Any candidate whose pitch is "trade
  more often to amplify a weak edge" is stopped at the lab by R-1.
- **Universe-wide "session of day" edge claims on EUR_USD only.**
  The real-data session study's absolute means are uniformly ≈
  −0.0002 across hours; "trade only this hour" is not a defensible
  thesis on this data.

## 7. Should CAMPAIGN_014 be retired, kept for continuation research,
or filtered?

The real event-window study materially supports **retirement of the
aggregate template** and **selective continuation only on declared
sub-slices**. Specifically:

- Aggregate calendar-event-window-anomaly: REJECT verdict stands,
  no follow-up campaign warranted. Documented limitation: ECB / BoE
  short-side sub-slices have small-n positive R but n < 30 in the
  current fixture, below the §1.2 threshold for graduation.
- Event filtering (NFP-only or NFP-excluded variants): not enough
  evidence to invest in a follow-up campaign. The dominance result
  says NFP is the entire campaign's behavior; the per-class win-rate
  result says NFP loses on both sides; together that's a
  diagnostic, not a stepping stone.
- Continuation research: only the ECB / BoE shorts sub-slice in §5.2
  has any positive signal, and it is small-n. Lab follow-up only.

## 8. Exact files to review first

1. [`docs/research/EDGE_DISCOVERY_LAB_HYDRATE_001_PLAN.md`](EDGE_DISCOVERY_LAB_HYDRATE_001_PLAN.md) — what this sprint's
   contract is.
2. [`docs/research/EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md`](EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md) — what real
   artifacts were available and what is local-only.
3. [`research/edge_discovery/studies/outputs/real/real_study_event_window.md`](../../research/edge_discovery/studies/outputs/real/real_study_event_window.md) —
   the real-data NFP dominance + FOMC zero-trade pattern.
4. [`research/edge_discovery/studies/outputs/real/real_study_turnover_cost.md`](../../research/edge_discovery/studies/outputs/real/real_study_turnover_cost.md) —
   cross-campaign observed-vs-published integrity check.
5. [`research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md`](../../research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md) —
   the one EUR_USD / CAMPAIGN_012 +0.0950 R cell.
6. `EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md` (this sprint
   Phase 4) — what the ranking rules now bind to.
