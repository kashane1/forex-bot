# EDGE_DISCOVERY_EXISTING_LAB_AUDIT_001

**Branch:** `research-edge-discovery-null-benchmark-lab-001`
**Date:** 2026-05-28
**Purpose:** Before writing any new code, map the capabilities the
`null-benchmark-lab-001` prompt requested onto what the repo **already**
provides, so we extend the existing import-isolated lab instead of rebuilding
it. This is the binding reconciliation document for the sprint.

> Diagnostic/infrastructure inventory only. Approves nothing, changes no
> verdict, opens no test lockbox.

---

## 1. Existing lab — what is already here

A full edge-discovery lab exists at top-level **`research/edge_discovery/`**
(~6,900 LOC), built by three prior sprints:

- `research-edge-discovery-lab-001` (core modules + 4 synthetic studies)
- `research-edge-discovery-lab-hydrate-001` (real-data loaders + real studies)
- `research-edge-discovery-lab-single-pair-probe-001` (EUR_USD / C012 probe + robustness)

### 1.1 Existing modules (`research/edge_discovery/`)

| module | role | reuse for this sprint |
|---|---|---|
| `windows.py` | `compute_forward_returns(frame, signal_times, *, window_bars, side)`, `Side` enum, `ForwardReturns` | **forward-return diagnostics** — reuse as-is |
| `costs.py` | `apply_cost_overlay`, `cost_fraction`, `financing_stress_fraction`, `turnover_cost_burden`, `pip_value_for` | **cost feasibility** — reuse as-is |
| `null.py` | `random_null_baseline` (single-frame random entry), `compare_to_null` (descriptive bands) | **generic** null — reuse; matched-null is the gap |
| `report.py` | `summarize_study`, `write_study_report` (verdict-word ban), `StudySummary` | report emission — reuse as-is |
| `loaders.py` | `load_candles_csv`, `load_event_fixture`, `CandleSample`, `EventFixture` | synthetic fixtures — reuse |
| `real_data.py` | H4-from-sqlite loader, `load_campaign_trades` (canonical trade ledger), `load_campaign_fold_pair_summaries`, `load_canonical_null_baseline_rollup` (C011), `StudyProvenance`/`StudyInput`, `assert_real_data_kind` | real-data + provenance — reuse |

### 1.2 Existing studies (`research/edge_discovery/studies/`)

Synthetic: `study_session`, `study_pair_baseline`, `study_event_window`,
`study_turnover_cost`. Real-data: `study_real_session_by_hour`,
`study_real_pair_baseline`, `study_real_event_window`,
`study_real_turnover_cost`. Bias/robustness: `bias_null_baseline`,
`bias_cross_campaign_comparability`, `exit_asymmetry_robustness`,
`exit_asymmetry_cross_campaign`, `probe_single_pair_eur_usd_c012`,
`probe_robustness_eur_usd_c012`.

### 1.3 Existing docs (`docs/research/EDGE_DISCOVERY_*`)

`EDGE_DISCOVERY_LAB_001_PLAN/RESULTS/SUMMARY.md`,
`EDGE_DISCOVERY_LAB_HYDRATE_001_PLAN/RESULTS_ADDENDUM/SUMMARY.md`,
`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`,
`EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md`,
`EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md`,
`EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md`,
`EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md`,
`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`.

### 1.4 Existing tests (`tests/research/edge_discovery/`)

`test_windows`, `test_costs`, `test_null`, `test_report`, `test_loaders`,
`test_real_data`, `test_real_studies_smoke`, `test_bias_of_fixtures`,
`test_exit_asymmetry`, `test_single_pair_probe`, **`test_isolation`** (import
rail). All passing at baseline.

---

## 2. Requested capability → existing capability → gap

The original prompt asked for 7 diagnostics. Mapping:

| # | requested diagnostic | already exists? | this sprint |
|---|---|---|---|
| 1 | cost feasibility / opportunity map | **Yes** — `costs.py`, `turnover_cost_burden`, `study_session`/`study_pair_baseline`, `research/cost_atlas/` | **Reuse**; add a thin retrospective wrapper over committed C025/C026 spread/ATR diagnostics |
| 2 | forward-return signal information | **Yes** — `windows.py` `compute_forward_returns` | **Reuse** |
| 3 | matched-null comparison | **Partial** — `null.py` is single-frame *random* entry only; no pair/side/session/weekday/hold-matched modes from a ledger | **GAP → `matched_nulls.py`** |
| 4 | entry/exit decomposition | **Partial** — `studies/exit_asymmetry_*` covers exit-vs-entry asymmetry | **Reuse**; documented as the decomposition home (no duplicate module) |
| 5 | filter contribution / ablation | **No** dedicated module | **GAP → `filter_ablation.py`** |
| 6 | pair/timeframe/session opportunity map | **Yes** — session/pair studies + cost atlas | **Reuse** |
| 7 | multiple-comparison sanity | **Partial** — `probe_robustness_*` has fragility ideas but no general matrix-level module | **GAP → `multiple_comparison.py`** |

**Net new code:** `matched_nulls.py`, `filter_ablation.py`,
`multiple_comparison.py` (+ tests). Everything else is reuse + documentation +
retrospective + CLI wrappers.

---

## 3. Import-isolation constraints (binding)

`tests/research/edge_discovery/test_isolation.py` enforces:

- **Banned:** any import of `forex_bot.broker`, `forex_bot.loops`,
  `forex_bot.approval`, `forex_bot.execution`.
- **Allowed forex_bot import:** **only** `forex_bot.financing` (pure data table
  used by the cost-stress overlay). *Any other* `from forex_bot.*` import fails
  `test_lab_only_imports_financing_from_forex_bot`.

**Consequences for the new modules:**
- No importing the Postgres candle store, `forex_bot.strategies.indicators`,
  or the campaign loaders. Session bucketing, weekday mapping, and any small
  helpers must be **self-contained pure functions** inside the lab.
- The C011 null rollup loader lives at top-level `research.null_baselines`
  (not under `forex_bot`), so it remains importable from the lab.
- New study reports must pass through `report.write_study_report` (verdict-word
  ban: `APPROVE`/`APPROVED`/`GO`/`PROMOTE`/`PROMOTED`).

---

## 4. Artifact compatibility constraints

Canonical real-data trade-ledger schema (from `real_data.load_campaign_trades`)
is `fold_NN_<PAIR>_trades.csv` under `<campaign_dir>/folds/` with columns:
`instrument, side, units, entry_time, exit_time, entry_price, exit_price,
stop_price, pnl, r_multiple, bars_held, spread_paid_pips, exit_reason,
fill_timing`. The matched-null and decomposition diagnostics consume a ledger
of this shape.

**C025/C026 did NOT persist per-trade ledgers.** They committed only rolled-up
artifacts:
- `research/campaign_025/train_matrix/train_matrix_metrics.csv`
  (`candidate_id, archetype, trade_count, expectancy_r, profit_factor,
  pairs_nonneg, top_pair_concentration, stress_2x_expectancy_r,
  beat_c011_null_by, avg_hold_bars, avg_spread_atr_ratio`)
- `train_matrix_pair_metrics.csv`, `train_matrix_side_metrics.csv`,
  `train_matrix_spread_atr_diagnostics.json`,
  `train_matrix_comparison_to_c011_null.csv`,
  `train_matrix_signal_funnel_diagnostics.json`, `candidate_registry.json`, …
- C026 mirror under `research/campaign_026/timeframe_ladder/` (+
  `execution_timeframe` column).

**Therefore in the retrospective (Phase 7):**
- **Runnable from committed artifacts:** matrix-sanity (variant count,
  best-vs-median, best-vs-null percentile, pair-holdout from pair metrics) and
  cost-feasibility (spread/ATR diagnostics + `avg_spread_atr_ratio`).
- **Not runnable (no ledger):** matched-null, forward-return, entry/exit
  decomposition on C025/C026 → `SKIPPED_TRADE_LEDGER_UNAVAILABLE` /
  `SKIPPED_SIGNAL_LEDGER_UNAVAILABLE`, recorded in
  `research/edge_discovery/retrospectives/retrospective_compatibility_gaps.json`.

This gap motivates the **future-campaign artifact-emission requirements** doc.

---

## 5. Data-availability constraints

- Real OHLC bars live in a Postgres research DB (`market_data.candles`) and
  gitignored sqlite candle stores in the **primary** checkout. This worktree's
  `data/` is empty; the sqlite stores hold **H1/H4/D only** (M1-derived TFs are
  materialized on demand).
- Policy: default to committed compact artifacts + local data only. Do **not**
  copy DB files into the worktree, fetch broker data, or require the research
  DB. Real-data diagnostics that need unavailable stores are skipped and
  documented, never forced.

---

## 6. Decision

Extend `research/edge_discovery/` in place. Add exactly three modules
(`matched_nulls`, `filter_ablation`, `multiple_comparison`) plus tests, CLI
wrappers, gate/checklist/workflow docs, and an artifact-first C025/C026
retrospective. Reuse all existing utilities. Do not create a second
`edge_discovery` package. Preserve import-isolation, the verdict-word ban, and
all freeze invariants.
