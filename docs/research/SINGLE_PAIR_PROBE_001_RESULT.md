# Single-Pair Probe Sprint 001 — Result

**Sprint id:** `research-edge-discovery-lab-single-pair-probe-001`
**Phase:** 3
**Date:** 2026-05-24
**Status:** **Falsification result.** The EUR_USD / CAMPAIGN_012
+0.0950 R cell classifies as **SELECTED_CELL_ARTIFACT** under the
lab's Phase 0 anti-overfit rules. **No strategy approved. No
campaign verdict altered.** Paper / demo / live remain blocked.

---

## 1. Headline

The single (pair, candidate) cell that appeared above the lab's
+0.05 R material-gap floor in the hydrate sprint —
**EUR_USD under CAMPAIGN_012 at +0.0950 R vs the CAMPAIGN_011
per-pair null** — does **not** survive the falsification probe.
The cell is classified `SELECTED_CELL_ARTIFACT`. It is most
parsimoniously read as a single chance pick from a 28-cell
(7-pair × 4-candidate) noise grid, not as evidence of a
regime-switcher edge on EUR_USD.

## 2. What appears to drive the cell

From [`probe_single_pair_eur_usd_c012.md`](../../research/edge_discovery/studies/outputs/real/probe_single_pair_eur_usd_c012.md)
and [`probe_robustness_eur_usd_c012.md`](../../research/edge_discovery/studies/outputs/real/probe_robustness_eur_usd_c012.md):

### 2.1 The mean is carried by two outlier folds

CAMPAIGN_012 EUR_USD per-fold expectancy R across the 8 walk-
forward folds:

| fold | C012 expectancy R | C011 null R | gap | trades |
|---:|---:|---:|---:|---:|
| 0 | −0.0474 | −0.1237 | +0.0764 | 88 |
| 1 | −0.1216 | +0.0460 | **−0.1676** | 105 |
| 2 | −0.0300 | +0.0968 | **−0.1268** | 50 |
| 3 | **+0.2506** | +0.2729 | −0.0223 | 37 |
| 4 | +0.0850 | −0.0322 | +0.1171 | 39 |
| 5 | −0.0325 | **−0.3414** | **+0.3090** | 56 |
| 6 | −0.0079 | −0.1597 | +0.1519 | 77 |
| 7 | **+0.1439** | **−0.2785** | **+0.4225** | 27 |

- Only **3 of 8 folds positive** on the candidate (folds 3, 4, 7).
- **Median per-fold candidate expectancy = −0.0189 R** — the
  typical fold loses money.
- Two of the largest positive gaps (folds 5 and 7) are caused
  primarily by CAMPAIGN_011 being unusually bad on those folds
  (−0.34 and −0.28 R), not by CAMPAIGN_012 being good (−0.03 and
  +0.14 R).
- The single most positive candidate fold — fold 3 (+0.25 R) — is
  matched by the null's most positive fold — also fold 3 (+0.27 R).
  The "edge" is essentially zero on the fold the candidate looks
  best on.

### 2.2 Cumulative R across folds is negative

| dimension | value |
|---|---:|
| Total cumulative R (sum across all 479 trades) | **−4.391** |
| Top fold (fold 3) cumulative R | +9.272 |
| Worst fold (fold 1) cumulative R | −12.768 |
| Top fold share of |sum of absolute fold R| | **0.342** (34.2 %) |
| Max chronological drawdown | **−28.4 R** |
| Longest losing streak | 16 trades |

The candidate's mean expectancy R looks positive (+0.0300) only
because the per-fold mean averages over fold magnitudes; the
trade-level cumulative R is **negative** by 4.4 R units. A
strategy whose mean-of-fold-means is positive while its
trade-level cumulative R is negative is exactly the
selected-cell-artifact pattern: small-n folds with high variance
can produce a positive mean of means even when the underlying
process is a net-loser.

### 2.3 LOO sensitivity

Leave-one-fold-out mean gap by dropped fold:

| dropped fold | LOO mean gap R |
|---:|---:|
| 0 | +0.0977 |
| 1 | +0.1325 |
| 2 | +0.1267 |
| 3 | +0.1118 |
| 4 | +0.0919 |
| 5 | +0.0644 |
| 6 | +0.0869 |
| 7 | **+0.0482** |

Dropping fold 7 — the single fold where the null happened to be
worst (−0.28 R) — brings the mean gap to +0.0482 R, **below the
+0.05 floor**. The cell is sensitive to a single fold; per the
plan's §4 ROBUST criteria, this is a failure.

### 2.4 SE-of-the-mean-gap puts the cell within 1.3 SE of zero

| dimension | value |
|---|---:|
| Mean gap R | +0.0950 |
| Per-fold gap std | 0.2032 |
| SE of mean gap (8 folds, paired diff) | 0.0718 |
| t-stat (mean / SE) | **1.323** |

The lab's soft significance threshold is t ≥ 2.0. The cell sits
at 1.3 — within the noise band of the null distribution under
even the lab's coarse descriptive significance check.

### 2.5 Neighboring pairs say "this pair is the lottery winner"

Same CAMPAIGN_012 vs CAMPAIGN_011 gap on the other six majors:

| pair | gap R | above +0.05 floor? |
|---|---:|:---:|
| EUR_USD | **+0.0950** | ✓ |
| GBP_USD | −0.1243 | ✗ |
| USD_JPY | +0.0004 | ✗ |
| AUD_USD | −0.0514 | ✗ |
| USD_CAD | −0.0564 | ✗ |
| USD_CHF | −0.0769 | ✗ |
| NZD_USD | −0.0111 | ✗ |

One pair above floor out of seven. The median non-EUR-USD gap is
**−0.0564 R** — clearly below the floor. The cross-pair signal is
not "C012 works on EUR-style pairs;" it is "C012 lost on six pairs
and happened to land above the floor on one." Classic Lesson 3
pair-concentration without diagnosis.

### 2.6 Neighboring candidates say "this candidate is the lottery winner"

Same EUR_USD gap vs CAMPAIGN_011 EUR_USD null for each candidate:

| candidate | gap R | above +0.05 floor? |
|---|---:|:---:|
| CAMPAIGN_012 regime_switcher_atr_percentile | **+0.0950** | ✓ |
| CAMPAIGN_013 cross_pair_currency_strength_rotation | +0.0360 | ✗ |
| CAMPAIGN_010 session_breakout | −0.0036 | ✗ |
| CAMPAIGN_014 calendar_event_window_anomaly | −0.1498 | ✗ |

One candidate above floor out of four. C013 is close (+0.036) but
below; the rest are spread around zero. There is no
candidate-family coherence; the cell is candidate-specific.

### 2.7 Stop-exit profile is hard-tail

| exit reason | n | mean R |
|---|---:|---:|
| time | 386 | +0.2255 |
| stop | 91 | **−1.0000** |
| eod | 2 | −0.2210 |

91 of 479 trades (19 %) exited via stop at exactly **−1.0 R**.
This is the strategy's hard floor: small mean-reversion-style
wins on time exits + occasional max-R losses on stops. The "edge"
is a fragile asymmetric profile that gets eaten by a 19 % stop-out
rate — if any single fold's stop-out rate jumped to 30 % the
candidate would flip negative immediately.

## 3. Does it survive the anti-overfit checks?

**No.** Three of the §4 failure criteria from the Phase 0 plan
trigger:

1. **LOO_drops_below_floor** (§2.3 above).
2. **at_most_4_of_8_folds_positive** (3 of 8).
3. **median_per_fold_expectancy_negative** (median −0.0189 R).

The classification is therefore `SELECTED_CELL_ARTIFACT` per the
plan's §4.3.

Three "robust" sub-criteria do hold (2× cost-stress survives at
+0.066 R, top-fold share is 0.342 ≤ 0.40, 5 of 8 folds have
positive gap), but the plan's §4.1 requires **all** five robust
criteria, not three of five. The two that fail — LOO above floor
and t-stat ≥ 2 SE — are exactly the screens designed to catch
single-fold lottery effects.

## 4. Does this suggest a real research direction?

**No, on the broad regime-switcher question.** The CAMPAIGN_012
family is REJECT-anchored, has 0 / 8 folds passing gates, and
loses on 6 of 7 pairs. The "EUR_USD outlier" was the lab's only
above-floor cell across CAMPAIGN_010-014 × 7 pairs = 28 candidate
cells; with a +0.05 R noise threshold and per-cell noise σ ≈
0.10-0.20 R, getting one cell above the threshold by chance is
the expected outcome (binomial probability ~0.85 of ≥ 1 cell
above +0.05 R under a no-edge null on this many cells with this
noise scale).

**There is a narrower question worth lab-only follow-up** but it
is not regime_switcher-shaped:

- The candidate's **time-exit trades** have mean R +0.2255 across
  386 of 479 trades. Setting aside the −1.0 R stop-out hard
  floor, the time-exit profile by itself looks meaningfully
  positive on EUR_USD. This is a strategy-of-exit observation,
  not a strategy-of-entry observation, and it is consistent with
  the existing CAMPAIGN_011 null behavior (time-exit returns hug
  random-walk drift). The lab does NOT recommend graduating this
  observation either; it recommends that any future event /
  session / regime study **explicitly report time-exit vs
  stop-exit per-trade R separately** so the asymmetric profile is
  visible upstream.

## 5. Should it be stopped?

**Yes, as a strategy direction.** The EUR_USD / CAMPAIGN_012 cell
is NOT promoted to any further lab study on its own merits.
CAMPAIGN_012's REJECT verdict stands; the single above-floor cell
is documented as a falsification example.

The lab's ranking rules' §1.5 ("single-pair declared candidate")
remains a viable graduation path **for future candidates only** —
just not for this cell, because this cell fails §1.3 (null-band)
and §1.4 (per-trade pre-cost edge with margin) once the LOO and
SE screens are applied.

## 6. Should it become a broader lab study before any campaign?

**No.** The recommended disposition is:

- Document the falsification (this doc).
- Add the LOO + SE-of-mean-gap + neighboring-pair / neighboring-
  candidate checks to the lab's standard candidate evaluation
  flow (Phase 4 addendum).
- Move on. The next lab studies recommended by the hydrate sprint
  (ECB / BoE shorts-only sub-slice; per-fold consistency probe)
  are **smaller in scope** than this single-pair probe was, and
  the answer here ("the cell didn't survive") is the right
  prior to apply to other "lottery winner" observations the lab
  might surface in the future.

## 7. Summary of classification rules vs result

| §4 criterion | required for ROBUST | observed | pass? |
|---|---|---|:---:|
| LOO ≥ floor on every resample | yes | min LOO = +0.0482 (below +0.05) | ✗ |
| ≥ 5 / 8 folds positive (candidate) | yes | 3 / 8 | ✗ |
| Median per-fold expectancy ≥ 0 | yes (implied) | −0.0189 | ✗ |
| 2× cost-stress mean gap ≥ floor | yes | +0.0661 | ✓ |
| Top-fold share ≤ 40 % | yes | 34.2 % | ✓ |
| t-stat ≥ 2 SE | yes | 1.323 | ✗ |
| ≥ 5 / 8 folds positive gap | yes | 5 / 8 | ✓ |

**Conclusion: SELECTED_CELL_ARTIFACT.** No campaign. No further
lab work on this specific cell. The lab's anti-overfit screens
worked exactly as the plan predicted they should.
