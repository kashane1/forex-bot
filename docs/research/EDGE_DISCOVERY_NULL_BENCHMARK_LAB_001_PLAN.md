# EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001 — PLAN

**Branch:** `research-edge-discovery-null-benchmark-lab-001`
**Date:** 2026-05-28
**Kind:** research infrastructure / diagnostics only — **NOT** a strategy campaign, **NOT** CAMPAIGN_027.
**Status entering sprint:** existing edge-discovery lab present (`research/edge_discovery/`); this sprint **extends and hardens** it.

> This sprint builds **no tradable strategy**, approves **nothing**, opens **no test
> lockbox**, and changes **no executor/broker/OANDA** behavior. It is a
> diagnostics layer that lets a *future* strategy idea be cheaply screened
> *before* it earns a full campaign. The maximum attainable status of any
> output here is "exploratory diagnostic / candidate hypothesis" — never
> APPROVE / GO / PROMOTE (those words are structurally reserved for the formal
> campaign + human-approval machinery).

---

## Purpose

We have run ~26 strategy campaigns; most failed at or below the C011 null. The
C025 → C026 sequence is the clearest lesson: a full M5 Donchian+HTF campaign
(C025) was built and rejected because **M5 spread/ATR ≈ 0.45** defeated every
candidate; C026 then re-ran the same family across M3/M15/M30 and confirmed a
monotone cost ladder (M3 ≈ 0.59 → M30 ≈ 0.15 spread/ATR) but **no candidate
crossed into positive edge** on any timeframe. Both were expensive ways to
re-learn that the idea had no edge beyond a matched null.

The fix is a reusable **edge-discovery + matched-null benchmark lab**: a cheap
diagnostics layer a proposed signal/filter/exit/timeframe/pair/session must
pass *before* we spend a campaign on it.

## Relationship to C011 / C025 / C026

- **C011** is the canonical **null baseline** (deduped: aggregate expectancy
  −0.0029 R, PF 0.89, 0/8 fold pass, 1,180 trades;
  `research/null_baselines/campaign_011_deduped_null_baseline.json`). It is a
  *diagnostic anchor*, never an improvable strategy. This sprint **preserves**
  that status and uses C011 as the generic-null reference the matched-null
  module compares against.
- **C025 / C026** remain **REJECT** (`REJECT_MATRIX_NO_TRAIN_CANDIDATE` /
  `REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE`, both `TEST_LOCKBOX_CLOSED /
  NOT_APPROVED`). This sprint does **not** change their verdicts; it runs the
  new diagnostics *retrospectively* on their committed compact artifacts to
  prove the lab would have flagged them earlier.

## Motivation from repeated campaign failures

Direct "strategy idea → full campaign" search is too slow and too noisy:
- a full campaign costs days of scaffolding, materialization, gates, parity;
- large parameter matrices invite selection noise ("best of 16" looks good by
  chance);
- cost feasibility (spread/ATR) is frequently the *binding* constraint and is
  cheap to check *first*;
- entry edge and exit edge get conflated;
- single-pair artifacts masquerade as portfolio edges.

A diagnostics layer turns these into cheap pre-checks.

## Pivot: integrate with the existing lab (do NOT rebuild)

A mature edge-discovery lab **already exists** and is **import-isolated**
(`research/edge_discovery/`, ~6,900 LOC, built by `research-edge-discovery-lab-001`,
`-hydrate-001`, `-single-pair-probe-001`). It already provides forward returns
(`windows.py`), cost overlays (`costs.py`), a generic random null (`null.py`),
report writing with a verdict-word ban (`report.py`), real-data loaders
(`real_data.py`), and a `studies/` suite (session/pair opportunity maps,
exit-asymmetry, turnover-cost, single-pair robustness).

**This sprint extends that lab in place.** It does **not** create a parallel
`src/forex_bot/research/edge_discovery/` package, and it preserves the
import-isolation rule (lab code may import only `forex_bot.financing`; never
broker/loops/approval/execution). See
`docs/research/EDGE_DISCOVERY_EXISTING_LAB_AUDIT_001.md` (Phase 1) for the full
capability-to-gap map.

## Non-goals

- No strategy approval; `configs/approved_strategies.yaml` stays `approved: []`.
- No paper/demo/live enablement; no executor/broker/OANDA mutation.
- No new broker data fetches; local committed artifacts + local data only.
- No test-lockbox opening; no CAMPAIGN_027; no revival/tuning of rejected work.
- No verdict changes to C011/C025/C026.
- No second `edge_discovery` package; no duplication of existing utilities.

## Safety invariants

- Lab stays import-isolated (`tests/research/edge_discovery/test_isolation.py`
  must keep passing — only `forex_bot.financing` allowed).
- All study reports go through `write_study_report`, which refuses banned
  verdict words.
- Diagnostics are deterministic given a `--seed`; randomness is seeded
  explicitly and recorded in provenance.
- Retrospective never fabricates missing data: if a per-trade/signal ledger or
  raw OHLC is unavailable in this worktree it is marked
  `SKIPPED_*_UNAVAILABLE` and recorded as a compatibility gap.
- No `.env`, credentials, DB dumps, raw candles, or bulky artifacts committed.

## Planned modules (extensions inside `research/edge_discovery/`)

Only genuine gaps — reuse `windows`/`costs`/`null`/`report`/`real_data` as-is:

1. `matched_nulls.py` — **NEW.** Matched-null benchmarks from a trade/signal
   ledger: `timestamp_random_same_pair`, `side_shuffled`, `pair_matched_random`,
   `session_matched_random`, `holding_period_matched_random`, `full_matched_null`.
   Preserves pair/side/session/weekday/hold-bucket structure; deterministic
   seeds; sparse-bucket handling; compact summary (mean/median/p05/p95
   expectancy, P(null ≥ strategy), strategy percentile, effect size). Generic
   `null.py` random baseline is reused for the single-frame case; this adds the
   *ledger-matched* case.
2. `filter_ablation.py` — **NEW.** Trigger-only / +one-filter / cumulative /
   leave-one-out / all-filters diagnostics from staged pass columns; flags
   filters that only shrink the sample vs. genuinely add edge.
3. `multiple_comparison.py` — **NEW.** Matrix-level selection-noise checks:
   variant count, best-vs-median, best-vs-null percentile, label-permutation
   test, pair-holdout and time-block stability, fragility flags.

Existing concerns (reused, not rebuilt): forward returns → `windows.py`;
cost feasibility / opportunity map → `costs.py` + `research/cost_atlas/` +
existing `study_session`/`study_pair_baseline`; entry/exit decomposition →
existing `studies/exit_asymmetry_*`.

## Planned scripts (local-only CLI diagnostics, under `scripts/`)

- `run_edge_discovery_matched_null.py`
- `run_edge_discovery_filter_ablation.py`
- `run_edge_discovery_matrix_sanity.py`
- `run_edge_discovery_cost_feasibility.py` (thin wrapper around existing cost
  utilities + retrospective on committed spread/ATR diagnostics)

Each: local-only, no broker calls, no approval, no test-lockbox, `--seed`
deterministic where random, `--dry-run`/preflight where practical, compact
artifacts under `research/edge_discovery/`, fail-safe on missing inputs.

## Artifacts

- New modules + tests under `research/edge_discovery/` and
  `tests/research/edge_discovery/`.
- Retrospective artifacts under `research/edge_discovery/retrospectives/`
  (`c025_*`, `c026_*`, `retrospective_compatibility_gaps.json`).
- Docs under `docs/research/`: this plan, the existing-lab audit, the
  edge-discovery protocol, re-entry gates, future-search workflow,
  pre-campaign checklist, future-campaign artifact requirements, the C025/C026
  retrospective, and the sprint summary.
- Index/status updates: `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`,
  `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md`.

## Validation commands

```
PYTHONPATH=$PWD/src python -m pytest tests/ -q
PYTHONPATH=$PWD/src ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```
(Worktree note: `PYTHONPATH=$PWD/src` is required — the editable install points
at the primary checkout.)

## Blocked conditions

- Real-data retrospective diagnostics requiring raw OHLC / per-trade / signal
  ledgers that C025/C026 never persisted → marked `SKIPPED_*_UNAVAILABLE`, not
  forced. Recorded in `retrospective_compatibility_gaps.json`.
- Postgres research DB / primary-checkout sqlite candle stores are **not**
  required and **not** copied into this worktree.

## Phase plan (revised after Phase-1 pivot)

- **Phase 0** — truth audit + this plan. *(commit)*
- **Phase 1** — existing-lab audit + capability→gap map. *(commit)*
- **Phase 2** — `matched_nulls.py` + tests. *(commit)*
- **Phase 3** — `filter_ablation.py` + tests. *(commit)*
- **Phase 4** — `multiple_comparison.py` + tests. *(commit)*
- **Phase 5** — CLI diagnostic scripts + guardrail tests. *(commit)*
- **Phase 6** — protocol / re-entry gates / future-workflow / checklist /
  artifact-requirements docs. *(commit)*
- **Phase 7** — C025/C026 retrospective (artifact-first; skip-and-document). *(commit)*
- **Phase 8** — index/status/manifest/backlog updates. *(commit)*
- **Phase 9** — full validation + sprint summary. *(commit)*
