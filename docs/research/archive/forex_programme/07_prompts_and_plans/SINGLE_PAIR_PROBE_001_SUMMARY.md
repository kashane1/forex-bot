# Single-Pair Probe Sprint 001 — Summary

**Sprint id:** `research-edge-discovery-lab-single-pair-probe-001`
**Branch:** `research-edge-discovery-lab-single-pair-probe-001`
**Date opened / closed:** 2026-05-24 (single-day sprint)
**Disposition:** **Falsification delivered.** The hydrate sprint's
single above-floor cell (EUR_USD / CAMPAIGN_012, +0.0950 R)
classifies as **SELECTED_CELL_ARTIFACT**. No strategy approved.
No campaign verdict altered. Paper / demo / live remain blocked.

---

## 1. Did the anomaly survive?

**No.** The EUR_USD / CAMPAIGN_012 cell fails three of the Phase 0
plan's anti-overfit criteria:

1. **LOO_drops_below_floor** — dropping fold 7 brings the mean gap
   to +0.0482 R, below the +0.05 R floor.
2. **at_most_4_of_8_folds_positive** — only 3 of 8 folds positive.
3. **median_per_fold_expectancy_negative** — median per-fold
   expectancy R is −0.0189 (typical fold loses money).

The mean-of-fold-means is positive (+0.0300) but the **sum of
trade-level R across all 479 trades is NEGATIVE (−4.391 R)** — a
small-n averaging artifact. The cell is most parsimoniously read
as the expected one-in-twenty-eight chance pick from the
hydrate sprint's 7-pair × 4-candidate noise grid.

## 2. Robustness classification

**`SELECTED_CELL_ARTIFACT`** per
[`SINGLE_PAIR_PROBE_001_PLAN.md`](SINGLE_PAIR_PROBE_001_PLAN.md) §4.3.

## 3. Branch / commits by phase

| phase | commit | what |
|---|---|---|
| 0 | `f2933c6` | plan + anomaly definition + classification rules |
| 1 | `214b445` | extract EUR_USD / C012 evidence slice |
| 2 | `601a836` | robustness + classification + 17 binding tests |
| 3 | `2ff53ad` | interpretation + result doc |
| 4 | `4f5a5fe` | ranking rules addendum (tightens, never relaxes) |
| 5 | *(this commit)* | final validation + summary |

5 commits, branched from the hydrate sprint tip
(`7381bf2` Phase 5 of `research-edge-discovery-lab-hydrate-001`).

## 4. Files changed

10 files, +3,016 insertions, 0 deletions (plus one minor edit to
`probe_single_pair_eur_usd_c012.py` for ruff cleanliness).

### Plan / result / addendum / summary docs (4 + this file)

- [`SINGLE_PAIR_PROBE_001_PLAN.md`](SINGLE_PAIR_PROBE_001_PLAN.md)
  — Phase 0 contract (236 lines).
- [`SINGLE_PAIR_PROBE_001_RESULT.md`](SINGLE_PAIR_PROBE_001_RESULT.md)
  — Phase 3 interpretation (248 lines).
- [`EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md`](EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md)
  — Phase 4 ranking-rules tightening (210 lines).
- `SINGLE_PAIR_PROBE_001_SUMMARY.md` — this file.

### Probe scripts (2)

- [`research/edge_discovery/studies/probe_single_pair_eur_usd_c012.py`](../../research/edge_discovery/studies/probe_single_pair_eur_usd_c012.py)
  — Phase 1 extractor.
- [`research/edge_discovery/studies/probe_robustness_eur_usd_c012.py`](../../research/edge_discovery/studies/probe_robustness_eur_usd_c012.py)
  — Phase 2 robustness checks + classifier.

### Probe outputs (4 — 2 × JSON + MD)

- [`research/edge_discovery/studies/outputs/real/probe_single_pair_eur_usd_c012.{json,md}`](../../research/edge_discovery/studies/outputs/real/probe_single_pair_eur_usd_c012.md)
- [`research/edge_discovery/studies/outputs/real/probe_robustness_eur_usd_c012.{json,md}`](../../research/edge_discovery/studies/outputs/real/probe_robustness_eur_usd_c012.md)

### Tests (1)

- [`tests/research/edge_discovery/test_single_pair_probe.py`](../../tests/research/edge_discovery/test_single_pair_probe.py)
  — 17 tests that pin the SELECTED_CELL_ARTIFACT classification,
  the per-fold breakdown numbers, the LOO sensitivity, the
  neighbor-pair / neighbor-candidate isolation, and the t-stat
  result. If a future change silently flips the classification, a
  test fails.

## 5. Tests / validation run

| check | command | result |
|---|---|---|
| focused edge-discovery suite | `pytest tests/research/edge_discovery -q` | **111 passed** (was 94 at the hydrate-sprint tip; +17 from `test_single_pair_probe.py`) |
| full pytest | `pytest tests/ -q` | **1,169 passed** (was 1,152 at hydrate-sprint tip; +17 net) |
| ruff (touched areas) | `ruff check research/edge_discovery tests/research/edge_discovery` | **All checks passed!** |
| research-freeze gate | `python scripts/check_research_freeze.py` | **ALL PASSED** (loops refuse `trend_following`; 14 campaigns; 14 diagnostic artifacts; no creds) |
| research-archive validator | `python scripts/validate_research_archive.py` | **ALL PASSED** (282 evidence-index links resolve; no credential strings in 2,795 artifact files) |
| secret scan | `python scripts/scan_artifacts_for_secrets.py` | **PASSED** (pattern scan over 2,889 files; value scan skipped — no creds in env) |
| paper/demo/live refusal | direct `assert_loop_strategies_approved` | **all 3 refuse** (`StrategyNotApprovedError`) |
| import-isolation guard | `test_isolation.py` | **PASSED** — probe code adds no `forex_bot.broker` / `loops` / `approval` / `execution` imports |

## 6. Key tables / metrics

### 6.1 Per-fold candidate vs null (the source data)

| fold | C012 R | C011 null R | gap R |
|---:|---:|---:|---:|
| 0 | −0.0474 | −0.1237 | +0.0764 |
| 1 | −0.1216 | +0.0460 | −0.1676 |
| 2 | −0.0300 | +0.0968 | −0.1268 |
| 3 | **+0.2506** | +0.2729 | −0.0223 |
| 4 | +0.0850 | −0.0322 | +0.1171 |
| 5 | −0.0325 | **−0.3414** | +0.3090 |
| 6 | −0.0079 | −0.1597 | +0.1519 |
| 7 | **+0.1439** | **−0.2785** | +0.4225 |
| **mean** | **+0.0300** | **−0.0650** | **+0.0950** |
| median | **−0.0189** | −0.0780 | +0.0967 |

### 6.2 Robustness screens

| screen | value | floor | pass? |
|---|---|---|:---:|
| n folds positive (candidate expectancy R > 0) | 3 / 8 | ≥ 5 | ✗ |
| median per-fold expectancy R | −0.0189 | ≥ 0 | ✗ |
| LOO min mean gap R | +0.0482 | ≥ +0.05 | ✗ |
| 2× cost-stress mean gap R | +0.0661 | ≥ +0.05 | ✓ |
| top-fold share of |abs sum| | 0.342 | ≤ 0.40 | ✓ |
| t-stat (mean / SE) | 1.323 | ≥ 2.0 | ✗ |
| n folds positive gap | 5 / 8 | ≥ 5 | ✓ |

3 / 7 pass — well short of the 5 / 5 needed for ROBUST classification.

### 6.3 Neighbor checks

| screen | observed | what it says |
|---|---|---|
| pairs above floor (C012 vs C011, all 7 majors) | 1 / 7 (EUR_USD only); median non-EUR-USD gap = −0.0564 R | the rest of the universe is clearly below floor — EUR_USD is the outlier, not the leader of a pattern |
| candidates above floor on EUR_USD (C010/12/13/14 vs C011) | 1 / 4 (C012 only); median = ≈ 0 | no candidate-family coherence — the cell is candidate-specific |

### 6.4 Stop-exit hard tail

| exit reason | n | mean R |
|---|---:|---:|
| time | 386 | +0.2255 |
| stop | 91 | −1.0000 (exactly) |
| eod | 2 | −0.2210 |

19% of trades exit at exactly −1.0 R; the strategy's profile is
small mean-reversion-style wins / occasional max-loss losses. A
profile that gets eaten by even a small uptick in the stop-out
rate.

## 7. Approval / safety status (unchanged)

- **Was any strategy approved by this sprint?** No. The approved-
  strategy registry remains `approved: []`.
- **Was any campaign verdict altered?** No. CAMPAIGN_012 remains
  REJECT. All other CAMPAIGN_001-014 verdicts unchanged.
- **Is paper / demo / live trading enabled?** No. All three loops
  refuse `trend_following` and any other test strategy
  (`StrategyNotApprovedError`).
- **Was the OANDA broker contacted?** No. The probe code is
  import-isolated — `tests/research/edge_discovery/test_isolation.py`
  still passes.
- **Was any campaign trade ledger modified?** No. Every per-fold
  `*_summary.json` and `*_trades.csv` is read-only input.

## 8. Exact files to review first

For a ~8-minute review pass, in this order:

1. [`docs/research/SINGLE_PAIR_PROBE_001_PLAN.md`](SINGLE_PAIR_PROBE_001_PLAN.md) §4 — the
   four classification buckets and their rules.
2. [`research/edge_discovery/studies/outputs/real/probe_robustness_eur_usd_c012.md`](../../research/edge_discovery/studies/outputs/real/probe_robustness_eur_usd_c012.md) —
   the headline classification + the LOO / cost-stress / neighbor
   tables.
3. [`docs/research/SINGLE_PAIR_PROBE_001_RESULT.md`](SINGLE_PAIR_PROBE_001_RESULT.md) §2 — why
   the mean is misleading (fold 3 + fold 7 carry it; cumulative R
   is negative).
4. [`docs/research/EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md`](EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md) §A —
   the new mandatory LOO / SE / median / R-9 checks the lab will
   apply to any future above-floor cell.
5. [`tests/research/edge_discovery/test_single_pair_probe.py`](../../tests/research/edge_discovery/test_single_pair_probe.py) —
   the binding tests that prevent silent classification flips.

## 9. Recommended next branch

The probe's §D ("what next if this fails") and §E ("what next if
this had looked promising") gave the answer. Since the cell failed:

1. **`research-exit-asymmetry-cross-campaign-001`** (new, lab-only) —
   pull every trade in every fold of every CAMPAIGN_010-014; group
   by `exit_reason`; report per-(reason, campaign, pair) mean R and
   n. The probe surfaced a striking pattern (91 stops at exactly
   −1.0 R; 386 time exits at +0.226 R on EUR_USD / C012); the
   question is whether it generalizes across the family. Pure
   structural observation, not a strategy promotion.

2. **`research-edge-discovery-lab-event-shorts-001`** (carried
   over from the hydrate sprint) — focused study of the CAMPAIGN_014
   ECB / BoE small-n positive shorts sub-slice from the real
   event-window study. Single-script extension; lab-only.

3. **`research-edge-discovery-lab-bias-of-fixtures-001`** —
   sanity rerun of the lab's four studies on the committed
   synthetic fixtures only, to keep the lab honest about not
   drifting onto its own fixture characteristics. Recommended in
   the original `EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md` §6.5
   but never run.

This sprint takes no position on which comes first; it just makes
sure none of them is a probe of this specific cell.

## 10. Anti-overfit gates landed (carried forward)

The probe's enduring contribution to the lab is in the
[`EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md`](EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md) §A
section. From now on, any above-floor cell the lab surfaces must
report:

- LOO mean gap across 8 resamples (§A.2)
- t-stat ≥ 2 SE on the per-fold gap distribution (§A.3)
- Per-fold median expectancy R alongside mean (§A.4)
- Trade-level cumulative R alongside mean-of-fold-means; R-9 fires
  if mean > 0 while cumulative < 0 (§A.5)

These are deterministic, cheap, and tested. The next time a
similar single-pair cell shows up, the lab can falsify it in one
script.
