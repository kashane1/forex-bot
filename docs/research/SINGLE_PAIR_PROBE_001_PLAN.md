# Single-Pair Probe Sprint 001 — Plan

**Sprint id:** `research-edge-discovery-lab-single-pair-probe-001`
**Branch:** `research-edge-discovery-lab-single-pair-probe-001`
**Opened:** 2026-05-24
**Disposition:** **Narrow falsification probe.** Goal is to confirm
the EUR_USD / CAMPAIGN_012 +0.0950 R material-gap cell is either a
robust exploratory signal worth further lab work or a selected-cell
artifact / data-snoop. **No strategy approval. No campaign verdict
changes.** Paper / demo / live remain blocked.

---

## 1. The exact anomaly being tested

From the hydrate sprint's
[`real_study_pair_baseline.md`](../../research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md)
gap-from-null table:

| pair | CAMPAIGN_011 null R (8-fold mean) | CAMPAIGN_012 R (8-fold mean) | gap | floor |
|---|---:|---:|---:|---:|
| **EUR_USD** | **−0.0650** | **+0.0300** | **+0.0950** | +0.05 |

Exactly **one** (pair, candidate) cell across the entire
CAMPAIGN_010-014 vs CAMPAIGN_011-null comparison table cleared the
+0.05 R material-gap floor. Every other cell stayed within or below
the null. The probe's question:

> Is this +0.0950 R gap a robust property of the
> regime_switcher_atr_percentile signal on EUR_USD, or is it a
> selected-cell artifact — a single fold (or two folds) carrying
> the mean while the typical fold is at or below null?

## 2. Why this is lab-only and NOT a campaign

- The walk-forward result for CAMPAIGN_012 is **REJECT** and stays
  REJECT. Per
  [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md) and
  [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md):
  5 of 8 aggregate gates fail; the **single-pair-dominance pattern
  was already noted** in CAMPAIGN_012's own evidence summary
  (USD_JPY at +0.0004 R as the only "positive" pair).
- The hydrate sprint's discovery is that on EUR_USD specifically,
  CAMPAIGN_012 happens to clear the lab's material-gap floor vs the
  CAMPAIGN_011 per-pair null — but this is a single cell pulled from
  a 7-pair × 4-candidate grid. **The lab's own ranking rules** (R-3,
  "single-pair effect dressed up as a universe effect") **and**
  Lesson 3 from the meta-analysis already warn against treating a
  single-pair cell as evidence.
- The probe runs in the lab, against committed artifacts only, with
  no new backtest executions. There is no path from this probe to a
  campaign in this sprint; even a "promising" classification only
  recommends a future broader lab study.

## 3. Required anti-overfit checks

The probe must include every one of these. If any one fails to land
a "robust" classification, the cell is downgraded.

1. **Fold consistency.** Per-fold per-EUR_USD expectancy R for
   CAMPAIGN_012 — how many of the 8 folds are positive, what is the
   median (not mean) per-fold R, what is the single-fold dominance
   share, what is the leave-one-fold-out (LOO) mean?
2. **Standard-error band.** Treat the 8 per-fold expectancy R values
   as 8 independent observations; compute the standard error of the
   mean gap to null. If the +0.0950 R gap is within 1 standard
   error of zero on the gap distribution, it cannot be distinguished
   from noise.
3. **2× cost stress (qualitative).** The committed trade ledgers
   carry observed `spread_paid_pips` per trade. Recompute per-trade
   R under a 2× spread assumption (scaling the per-trade cost
   contribution) and check whether the +0.0950 R gap survives.
4. **Leave-one-fold-out (LOO).** For each fold k, drop fold k from
   the 8-fold mean and recompute the gap. If removing any single
   fold flips the sign of the gap or drops it below the +0.05 floor,
   the cell is fold-concentrated and **disqualified** as evidence.
5. **Neighboring-pair comparison.** Look at the same CAMPAIGN_012 vs
   CAMPAIGN_011 gap on every other pair (GBP_USD, USD_JPY, AUD_USD,
   USD_CAD, USD_CHF, NZD_USD). If EUR_USD is the only "above-floor"
   cell but the other six pairs are all clustered around zero, the
   EUR_USD cell is consistent with a chance pick from 7 independent
   noisy estimates.
6. **Neighboring-candidate comparison.** Look at the same EUR_USD
   gap vs CAMPAIGN_011 for CAMPAIGN_010, CAMPAIGN_013, CAMPAIGN_014
   (and CAMPAIGN_012). If multiple candidates all produce ≥+0.05 R
   gap on EUR_USD, the cell is candidate-robust on this pair; if
   only CAMPAIGN_012 does, the cell is candidate-specific.
7. **Direction / session / exit-type / regime clustering.** Pull
   the EUR_USD trade ledger across all 8 CAMPAIGN_012 folds and
   look at:
   - long vs short share + per-side mean R
   - per-UTC-hour entry distribution + per-hour mean R
   - per-exit-reason distribution (time / stop / tp) + per-reason
     mean R
   - per-fold-window time-period concentration
8. **Dominance checks.** Compute, for the EUR_USD trade ledger:
   - top-fold share of total R: what fraction of the cumulative R
     comes from the single best fold?
   - top-N% trades share of total R: what fraction comes from the
     top 5% / 10% of trades by R?
   - top-month share of total R: what fraction comes from the
     single best calendar month?

## 4. Pass / fail / uncertain classification rules

The probe must classify the cell into exactly one of four buckets.
The lab's `random_null_baseline` is NOT regenerated here; the
binding null is the committed CAMPAIGN_011 per-pair per-fold table.

### 4.1 ROBUST_EXPLORATORY_SIGNAL — all of the following true

- LOO mean gap ≥ +0.05 R on every leave-one-fold-out resample (no
  single fold carries the mean).
- ≥ 5 of 8 per-fold gaps to the per-fold null are positive (binomial
  ≥ 0.625, well above the 0.5 chance baseline).
- 2× cost-stress mean gap is still ≥ +0.05 R.
- Top-fold cumulative-R share is ≤ 40 %.
- Standard error of the mean gap < 0.5 × the mean gap (i.e. the gap
  is ≥ 2 standard errors away from zero in the noise-sense).

### 4.2 WEAK_UNSTABLE_SIGNAL

- LOO mean gap drops below +0.05 R for ≥ 1 of the 8 leave-one-fold-
  out resamples.
- 4 or 5 of 8 folds positive (between chance and structurally
  positive).
- 2× cost-stress mean gap drops to between 0 and +0.05 R.
- Top-fold cumulative-R share is 40-60 %.

### 4.3 SELECTED_CELL_ARTIFACT — any one of the following true

- LOO removes one fold and the mean gap flips sign or drops below
  the floor.
- ≤ 4 of 8 folds positive.
- Median (not mean) per-fold expectancy R is negative (i.e. the
  typical fold loses money; the positive average is carried by
  outliers).
- Top-fold cumulative-R share exceeds 60 %.
- Standard error of the mean gap is ≥ the mean gap itself (gap is
  within 1 SE of zero on the gap distribution).

### 4.4 INSUFFICIENT_DATA

- EUR_USD trade ledger across all 8 folds has < 200 trades total
  (CAMPAIGN_012 EUR_USD has 479 trades, so this branch should not
  trigger).
- Any of the committed per-fold per-pair JSONs / CSVs is missing.

A "robust" classification authorizes a single follow-up **lab study**
(not a campaign). A "weak" classification parks the cell in
[`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) (if that file
exists in the repo — see Phase 5). An "artifact" classification
documents the falsification and recommends no follow-up.

## 5. Expected artifacts

| artifact | path |
|---|---|
| this plan | `docs/research/SINGLE_PAIR_PROBE_001_PLAN.md` |
| extraction study script | `research/edge_discovery/studies/probe_single_pair_eur_usd_c012.py` |
| extraction output JSON / MD | `research/edge_discovery/studies/outputs/real/probe_single_pair_eur_usd_c012.{json,md}` |
| robustness study script | `research/edge_discovery/studies/probe_robustness_eur_usd_c012.py` |
| robustness output JSON / MD | `research/edge_discovery/studies/outputs/real/probe_robustness_eur_usd_c012.{json,md}` |
| result interpretation | `docs/research/SINGLE_PAIR_PROBE_001_RESULT.md` |
| ranking notes addendum | `docs/research/EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md` |
| sprint summary | `docs/research/SINGLE_PAIR_PROBE_001_SUMMARY.md` |
| smoke tests | `tests/research/edge_discovery/test_single_pair_probe.py` |

## 6. Validation commands (run in Phase 5)

```
# Focused lab tests
pytest tests/research/edge_discovery -q

# Full repo regression
pytest tests/ -q

# Lint touched areas
ruff check research/edge_discovery tests/research/edge_discovery

# Freeze, archive, secret scans
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py

# Paper/demo/live refusal — direct
python -c "from forex_bot.loops import assert_loop_strategies_approved; \
  assert_loop_strategies_approved('paper', ['trend_following'])"
# (expected: StrategyNotApprovedError)
```

## 7. What this sprint will NOT do

- Will not modify `configs/approved_strategies.yaml`,
  `configs/paper.yaml`, `configs/practice.yaml`,
  `configs/live.example.yaml`, the loops module, the broker module,
  the evidence manifest, the evidence index,
  `STRATEGY_STATUS.md`, any `CAMPAIGN_*_STATUS.md`, any
  `CAMPAIGN_*_WALK_FORWARD_RESULT.md`, any
  `walk_forward/results.json`, any per-fold per-pair summary or
  trades CSV.
- Will not re-execute any backtest.
- Will not call the OANDA broker. Will not read `.env`. Will not
  hash credentials.
- Will not write `APPROVE` / `PASS` / `GO` / `PROMOTE` in any output.
  The lab's verdict-word ban applies; the existing
  [`test_report.py`](../../tests/research/edge_discovery/test_report.py) regression-guards it.
- Will not import from `forex_bot.broker` / `loops` / `approval` /
  `execution`. The existing
  [`test_isolation.py`](../../tests/research/edge_discovery/test_isolation.py) regression-guards
  it.

## 8. First-glance numbers (to be replaced in Phase 1)

From a 30-second peek at the committed per-fold per-pair summary
JSONs to validate the plan's premise:

**CAMPAIGN_012 EUR_USD per-fold expectancy R:**
−0.0474, −0.1216, −0.0300, **+0.2506**, +0.0850, −0.0325, −0.0079, **+0.1439**
(mean +0.0300, median **−0.0189**, std 0.121, total trades 479)

**CAMPAIGN_011 EUR_USD per-fold expectancy R (null):**
−0.1237, +0.0460, +0.0968, **+0.2729**, −0.0322, **−0.3414**, −0.1597, **−0.2785**
(mean −0.0650, median −0.0780, std 0.203, total trades 119)

Per-fold gap (CAMPAIGN_012 − CAMPAIGN_011) by fold index:
+0.0763, **−0.1676**, **−0.1268**, −0.0223, +0.1172, **+0.3089**, +0.1518, **+0.4224**

Median per-fold gap: **+0.0968**; 6 of 8 folds positive — but the
median per-fold C012 expectancy is **negative**, and two of the
positive gaps are driven by CAMPAIGN_011's exceptionally bad folds
5 and 7 (−0.34 and −0.28). These observations are precisely what
Phase 1 will measure carefully, and Phase 2 will pressure-test.

The plan does not pre-commit the classification; Phase 3 reads the
Phase 2 outputs and applies §4's rules.
