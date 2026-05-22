# Infrastructure Data/Parity Sprint 001 — Summary

**Date:** 2026-05-22 · **Branch:** `infra-data-parity-001`
**Base commit:** `340ae64` (HEAD of `infra-execution-fidelity-001`)

Companion to [`INFRA_DATA_PARITY_001_PLAN.md`](INFRA_DATA_PARITY_001_PLAN.md).
This sprint aimed to put **real OANDA H4 data** through the
execution-fidelity infrastructure to make the repo reproducible and
independently verifiable. It ran no strategy campaign, produced no
verdict, and approved nothing.

## Headline: the data fetch was blocked

**No OANDA practice credentials were available** in this environment
(`.env` absent, env vars unset). Per the Phase 1 contingency rule, the
real-data fetch was **not run**. The sprint therefore:

- shipped every data-dependent tool **ready to run** (rehydration,
  six-pair smoke, Lean export) and **tested**;
- shipped every data-independent deliverable **in full** (the runbook,
  the orchestrator, the archive hardening);
- documented each blocker precisely so a human can lift it by providing
  practice credentials and re-running the documented commands.

Nothing was faked: no synthetic data stands in for real OANDA data
anywhere.

## What changed

| phase | commit | change |
|---|---|---|
| 0 | `3431449` | Baseline verification; this sprint's plan. |
| 1 | `86a55ea` | `scripts/rehydrate_oanda_h4_store.py` — builds a local real-OANDA practice H4 store (six majors, 2020–2026) with raw+normalized hashes; practice-only, no synthetic fallback, store gitignored. `OANDA_H4_DATA_REHYDRATION.md`; 10 tests. |
| 2 | `01a0b0a` | Six-pair D1AGG + next-bar-open smoke — `smoke_d1agg_next_open.py` extended with `smoke_from_store()`, a six-major coverage table, and per-pair data hashes. Report `backtests/diagnostics/d1agg_next_open_six_pair_smoke.md`; 2 tests. |
| 3 | `2766b3b` | Lean-parity export bundle `research/lean_parity/exports/campaign_002_h4/` (`EXPORT_MANIFEST.md`); exporter retargeted to the rehydrated store; export CSVs gitignored; guide updated; 4 tests. |
| 4 | `890c31d` | Lean local-parity detection — Lean not installed; `LEAN_PARITY_LOCAL_STATUS.md` records it and the setup steps; run skipped, no faked result. |
| 5 | `3eec7e8` | `scripts/prepare_local_research_data.py` — a safe ordered orchestrator with `--dry-run`; `DATA_REHYDRATION_RUNBOOK.md`; 9 tests. |
| 6 | `5732edf` | Archive hardening — `EVIDENCE_MANIFEST.json` v2 gains a `diagnostic_artifacts` array; new validator check `check_diagnostic_artifacts`; `EVIDENCE_INDEX.md` gains a diagnostic/parity section; 4 tests. |
| 7 | _(this commit)_ | Final docs, full validation, handoff. |

## What did NOT change

- **No strategy campaign was run; no verdict produced.** CAMPAIGN_001–009
  remain REJECT; Research Marathon 001 remains NO-GO.
- **No strategy approved.** `configs/approved_strategies.yaml` is still
  `approved: []`.
- **No order path changed.** paper-loop, demo-loop and the live path
  still refuse every strategy. Nothing was made easier to run.
- **No OANDA connection was made** — no credentials were available, and
  none were used, printed, logged, or committed.
- **No prior campaign artifact** was modified or overwritten.
- **Financing is still unsolved** — `UNMODELED` / `ESTIMATED`, a hard
  live-promotion blocker.

## Per-deliverable status

| deliverable | status |
|---|---|
| H4 data rehydration | tool shipped + tested; **fetch blocked** (no OANDA practice credentials) |
| Six-pair D1AGG smoke | tooling shipped; ran in fallback on the committed EUR_USD D1AGG sample (all mechanical checks PASS); **six-pair real-data run blocked** (no H4 store) |
| Lean parity export | exporter + bundle manifest shipped + tested; **export blocked** (no H4 store) |
| Lean local parity run | **blocked** — Lean CLI not installed (Docker is present); documented, not faked |
| Data rehydration runbook | shipped in full — runbook + `--dry-run` orchestrator |
| Freeze / archive hardening | shipped in full — `diagnostic_artifacts` manifest + validator check |

## Validation results

All run from the repo root on the final commit:

| check | result |
|---|---|
| `pytest -q` | **315 passed** (286 baseline + 29 new) |
| `ruff check src tests scripts` | **All checks passed** |
| `scripts/validate_research_archive.py` | **ALL CHECKS PASSED** |
| `scripts/check_research_freeze.py` | **ALL CHECKS PASSED** |
| `bot paper-loop … --once` | refused, **exit 2** |
| `bot demo-loop … --once` | refused, **exit 2** |
| `configs/approved_strategies.yaml` | `approved: []` — empty |
| `data/*.sqlite3` staged | none — no data store committed |
| credentials staged | none; `.env` / `.env.*` gitignored |

## Safety state

All sprint safety invariants hold:

1. The approved-strategy registry is empty.
2. paper-loop, demo-loop and the live path refuse every strategy.
3. Backtesting / diagnostics stay available; loops stay gated.
4. No live credentials were used; no OANDA connection was made.
5. No credential value was printed, logged, or committed.
6. No `data/*.sqlite3` store and no candle-export CSV is committed.
7. No synthetic data is presented as real.
8. Prior campaign reports and artifacts are immutable.
9. `pytest` and `ruff check` are green.

## Remaining blockers

1. **No OANDA practice credentials** in this environment. This blocks
   the H4 fetch (Phase 1), and therefore the six-pair real-data smoke
   (Phase 2) and the Lean-parity data export (Phase 3). The tooling is
   wired, tested, and runs the moment credentials are provided.
2. **QuantConnect Lean is not installed** (the `lean` CLI / package).
   Docker is present. This blocks the local parity dry run (Phase 4).
3. **Historical financing remains unsolved** — a standing hard
   live-promotion blocker, unchanged by this sprint.
4. **No strategy has earned PAPER-TRADE-ONLY.** The research freeze
   holds; this sprint did not change that and was not meant to.

## Recommended next human decision points

1. **Provide OANDA practice credentials and rehydrate.** Put
   `OANDA_ACCOUNT_ID_PRACTICE` / `OANDA_ACCESS_TOKEN_PRACTICE` in a local
   `.env`, then run `python scripts/prepare_local_research_data.py`
   (or the step-by-step `DATA_REHYDRATION_RUNBOOK.md`). That single
   action lifts blockers 1 and produces the six-pair smoke and the Lean
   export on real data.
2. **Install Lean** (`pip install lean`; Docker is already present) to
   enable the CAMPAIGN_002 H4 parity dry run — see
   `LEAN_PARITY_LOCAL_STATUS.md`. A parity run verifies the bespoke
   engine and approves nothing.
3. **Financing remains the gating problem** for any live consideration;
   no infrastructure sprint changes that.
4. Re-running any campaign — under `next_bar_open` or otherwise — would
   be **new research**, needing a fresh pre-committed campaign per
   `STRATEGY_APPROVAL_PROCESS.md`. It is out of scope for an
   infrastructure sprint.

## Files to review first

1. [`INFRA_DATA_PARITY_001_PLAN.md`](INFRA_DATA_PARITY_001_PLAN.md) —
   scope, non-goals, data-handling rules.
2. [`scripts/rehydrate_oanda_h4_store.py`](../../scripts/rehydrate_oanda_h4_store.py)
   — the data-fetch entry point and its guards.
3. [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md) — how to
   reproduce every local data store.
4. [`backtests/diagnostics/d1agg_next_open_six_pair_smoke.md`](../../backtests/diagnostics/d1agg_next_open_six_pair_smoke.md)
   — the six-pair smoke report.
5. This summary.
