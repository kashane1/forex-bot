# Bias-of-Fixtures Audit — Sprint Summary

**Sprint:** `research-bias-of-fixtures-audit-001`
**Date:** 2026-05-24
**Status:** Complete. Audit closed. No strategy approved.
No campaign verdict changed. No parameter tune proposed.

> No strategy approved. CAMPAIGN_001-014 verdicts unchanged.
> `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live loops still refuse every configured strategy.

---

## One-line takeaway

The lab's research substrate — the CAMPAIGN_011 null, the
CAMPAIGN_010-014 trade ledgers, the H4 / event fixtures, the
synthetic test fixtures — passes audit. No fixture bias was found
that invalidates an existing finding or requires a repair sprint.

## Commits by phase

| phase | sha | scope |
|---|---|---|
| 0 | `a76b81f` | audit plan + pre-committed refusals + 3 orientation findings |
| 1 | `2ce0dee` | artifact inventory (285 committed input files, sha256/size/row-count) |
| 2 | `ee159dc` | null-baseline bias study (6 dimensions + cross-campaign comparison) |
| 3 | `bd0ebe0` | cross-campaign comparability (5 invariant axes + headline survival) |
| 4 | `fd994e6` | synthetic-vs-real audit (README + 28 binding tests) |
| 5 | `5b8fb1e` | result doc answering Q1-Q6 + decision on addendum |
| 6 | (this commit) | final validation + summary |

## Files added (10 net-new)

| file | phase | purpose |
|---|---|---|
| `docs/research/BIAS_OF_FIXTURES_AUDIT_001_PLAN.md` | 0 | what fixture bias means here, six audit questions, pre-committed refusals |
| `docs/research/BIAS_OF_FIXTURES_ARTIFACT_INVENTORY.md` | 1 | sha256 / size / row-count for every artifact in scope |
| `research/edge_discovery/studies/bias_null_baseline.py` | 2 | Phase-2 lab study |
| `research/edge_discovery/studies/outputs/real/bias_null_baseline.{json,md}` | 2 | Phase-2 output |
| `research/edge_discovery/studies/bias_cross_campaign_comparability.py` | 3 | Phase-3 lab study |
| `research/edge_discovery/studies/outputs/real/bias_cross_campaign_comparability.{json,md}` | 3 | Phase-3 output |
| `research/edge_discovery/studies/outputs/README.md` | 4 | synthetic-vs-real corpus boundary |
| `tests/research/edge_discovery/test_bias_of_fixtures.py` | 4 | 28 binding tests |
| `docs/research/BIAS_OF_FIXTURES_AUDIT_001_RESULT.md` | 5 | answers Q1-Q6 with decision on addendum |
| `docs/research/BIAS_OF_FIXTURES_AUDIT_001_SUMMARY.md` | 6 | this file |

**Files modified outside the audit's scope: 0.** No
`configs/`, no `src/forex_bot/`, no `backtests/CAMPAIGN_*/`, no
verdict-bearing CAMPAIGN doc, no existing addendum.

## Tests and validation run

| check | result | command |
|---|---|---|
| 28 new bias-of-fixtures tests | **28/28 PASS** | `pytest tests/research/edge_discovery/test_bias_of_fixtures.py` |
| 165 focused edge-discovery tests | **165/165 PASS** | `pytest tests/research/edge_discovery/` |
| 1,223 full pytest | **1,223/1,223 PASS** | `pytest` |
| ruff on Phase 2/3/4 code | **clean** | `ruff check research/edge_discovery/studies/bias_*.py tests/.../test_bias_of_fixtures.py` |
| research freeze gate | **ALL CHECKS PASSED** | `python scripts/check_research_freeze.py` |
| artifact secret scan | **PASSED** | `python scripts/scan_artifacts_for_secrets.py` |
| research archive | **ALL CHECKS PASSED** | `python scripts/validate_research_archive.py` |
| paper-loop refusal | refuses `['trend_following']` | freeze gate |
| demo-loop refusal | refuses `['trend_following']` | freeze gate |
| approval boundary | `approved: []` | `yaml.safe_load(configs/approved_strategies.yaml)` |
| `StrategyNotApprovedError` import | works | `from forex_bot.approval import StrategyNotApprovedError` |

## Artifacts audited

| category | count | notes |
|---|---:|---|
| campaign walk-forward `plan.json` | 5 | CAMPAIGN_010-014 |
| campaign walk-forward `results.json` | 5 | CAMPAIGN_010-014 (5 REJECT × 5) |
| per-fold per-pair `summary.json` | 280 | 5 campaigns × 8 folds × 7 pairs |
| per-fold per-pair `trades.csv` | 280 | total 16,354 trade rows |
| event fixtures | 1 | `research/calendar/fixtures/campaign_014_events.json` (281 events) |
| lean-parity provenance JSONs | 7 | one per major |
| H4 SQLite candle store | 0 (absent, gitignored, not required) | `data/campaign_002.sqlite3` |
| synthetic fixtures | 4 | `sample_fixtures/{*.csv, *.py, README.md}` |
| legacy synthetic outputs | 8 | `outputs/study_*.{json,md}` |
| real-data outputs | 16 | `outputs/real/*.{json,md}` |

**Total: 606 artifacts audited.** Every one accounted for in the
inventory; nothing fabricated; nothing silently missing.

## Null-baseline audit result

CAMPAIGN_011 is **acceptable** as the binding null baseline.

| dimension | result |
|---|---|
| coverage | 56 / 56 (fold, pair) cells with trades |
| direction balance | 51.8 % long (within 5 pp of 50/50) |
| trade-count dispersion | max pair 16.7 %, max fold 13.8 % |
| stop_rate vs others | 0.205 ∈ [0.204, 0.242] (inside) |
| time_rate vs others | 0.789 ∈ [0.746, 0.793] (inside) |
| mean_R given_stop vs others | inside range |
| mean_R given_time vs others | inside range |
| mean_R_overall vs others | outside (less negative) — **structurally desired** |

## Cross-campaign comparability result

CAMPAIGN_010-014 are **comparable enough** for the lab's current
screens.

| invariant axis | status |
|---|---|
| fold layout | identical 8-fold layout (passes) |
| pair universe | identical 7 majors (passes) |
| fill_model + fill_timing + granularity | identical (passes) |
| trade-CSV schema (14 columns) | identical across 280 CSVs (passes) |
| exit-reason vocabulary | identical `['eod', 'stop', 'time']` (passes) |
| trade-window population | C010/011 test-only; C012-014 partial (documentation-grade) |
| coverage anomalies | C013 has 29/56 empty (fold, pair) cells (strategy property, not fixture bug) |

The exit-asymmetry headline **survives** the test-window-only
restriction (max delta on `mean_R_given_time` is 0.0027 R; every
campaign still has positive `mean_R_given_time` and negative
`mean_R_overall` on test-only).

## Synthetic-vs-real fixture result

Confirmed safe. Synthetic fixtures are used by unit tests
(test_loaders, test_costs, test_windows, test_report, test_null);
no real-data study silently consumes them; no ranking-rule
threshold was derived from synthetic-only behaviour. The four
legacy synthetic JSON outputs (`outputs/study_*.json`) lack a
machine-readable `data_kind` field but:

- the matching `.md` files carry the "Exploratory lab output"
  disclaimer header and (where applicable) cite the synthetic
  CSV path in their `inputs` block;
- no active code reads them (`grep -rln` across `research/`,
  `tests/`, `src/` returns 0 hits);
- Phase 4 added `research/edge_discovery/studies/outputs/
  README.md` mapping every file in the directory to its data
  kind, and a binding test that asserts no active code reads
  the legacy filenames.

## Weakened findings

**Zero existing lab findings are invalidated.** Two findings get
explicit documentation:

1. The trade-window-population asymmetry across C010/011 vs
   C012-014. The exit-asymmetry sprint's headline numbers
   survive the test-only restriction (max Δ 0.003 R).
2. The C013 empty-cell pattern (29/56 (fold, pair) cells empty)
   is a property of the currency-strength-rotation strategy
   (only top/bottom-ranked pairs trade), not a fixture defect.

## New lab rules added

**None.** The audit decided **not** to introduce a new ranking
addendum because:

- no existing rule needed to be relaxed (the rules are working);
- no existing rule needed to be tightened to patch a fresh bias
  (the audit did not find one);
- the labeling fix landed as an additive README + binding test,
  not as a new rule.

The four existing addenda
([`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`](EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md),
[`EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md`](EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md),
[`EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md`](EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md),
[`EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md`](EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md))
remain in force.

## Was any strategy approved?

**No.**

## Are paper / demo / live still blocked?

**Yes.** All three loops refuse every configured strategy.
`configs/approved_strategies.yaml` remains `approved: []`.

## Exact files to review first

For a quick read-through of the audit:

1. [`docs/research/BIAS_OF_FIXTURES_AUDIT_001_RESULT.md`](BIAS_OF_FIXTURES_AUDIT_001_RESULT.md)
   — answers Q1-Q6 with citations.
2. [`research/edge_discovery/studies/outputs/real/bias_cross_campaign_comparability.md`](../../research/edge_discovery/studies/outputs/real/bias_cross_campaign_comparability.md)
   — the test-only headline-survival table.
3. [`research/edge_discovery/studies/outputs/real/bias_null_baseline.md`](../../research/edge_discovery/studies/outputs/real/bias_null_baseline.md)
   — the C011 null-vs-others shape comparison.
4. [`tests/research/edge_discovery/test_bias_of_fixtures.py`](../../tests/research/edge_discovery/test_bias_of_fixtures.py)
   — the 28 invariants the audit pinned.

## Recommended next branch

The audit certifies the substrate. The lab is unblocked from running
the next real candidate-discovery sprint *whenever* a fresh
candidate proposal appears, since the existing four-addenda screen
stack is calibrated against fixtures this audit deems adequate.

**Recommended next branches** (priority order, for human
consideration):

1. **A fresh candidate-finding study** that uses the existing
   exit-shape screens (B.1-B.4) at the lab stage — this is the
   path the prior sprint set up; this audit certifies it's ready
   to run.

2. **A documentation-consolidation sprint** that folds the four
   addenda + this audit into a single "lab decision rules" doc.
   Low priority, but improves readability for new readers.

3. **An optional CAMPAIGN_012-014 test-only re-execution** to
   make cross-campaign aggregates literally apples-to-apples.
   The audit shows the qualitative findings would not change
   (deltas < 0.003 R). Lowest priority.

Explicitly **not recommended**: any sprint that revisits
CAMPAIGN_010-014 verdicts. The exit-asymmetry sprint answered that
with a hard no and this audit confirms there's no fixture-bias
loophole.

---

## Appendix — full validation summary at sprint close

```
research freeze gate:       ALL CHECKS PASSED
research archive:           ALL CHECKS PASSED
artifact secret scan:       PASSED
focused edge tests:         165 / 165 PASS
new bias-of-fixtures tests: 28 / 28 PASS
full pytest:                1223 / 1223 PASS
ruff (audit code):          clean
approved_strategies.yaml:   approved: []
paper loop:                 refuses
demo loop:                  refuses
StrategyNotApprovedError:   importable
```
