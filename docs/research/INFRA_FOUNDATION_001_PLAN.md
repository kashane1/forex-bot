# Infrastructure Foundation Sprint 001 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-research-foundation-001`
**Base commit:** `8c76dec` (the research-freeze HEAD)

## Purpose

Research Marathon 001 closed **NO-GO** and the repo is frozen with no
approved trading strategy. This sprint **strengthens the repo as a safe
research / backtesting platform** so that *future* research — if a human
ever authorizes it — is more trustworthy.

This sprint **does not look for a trading edge.** It runs no strategy
campaign, approves no strategy, and submits no orders. It is pure
infrastructure, documentation, and safety hardening.

## Phases

| phase | deliverable | independent? |
|---|---|---|
| 0 | Baseline audit & safety verification; this plan | — |
| 1 | Valid D1 research support via H4→D1 aggregation | yes |
| 2 | Financing / swap modeling foundation | yes |
| 3 | Lean parity design & minimal skeleton | yes |
| 4 | Research artifact integrity & evidence-index hardening | yes |
| 5 | Approval workflow hardening | depends on Phase 2 enum |
| 6 | Final docs, validation & handoff | depends on 0–5 |

Each phase commits separately when it produces meaningful code or docs.
If a phase is blocked, the blocker is documented and the next
independent phase proceeds. The sprint stops only if proceeding would
risk credentials, order submission, or corruption of prior evidence.

## Explicit non-goals

This sprint will **not**:

- run any strategy campaign or produce any new strategy result;
- approve any strategy, or edit `configs/approved_strategies.yaml`
  except to verify it remains empty;
- paper-trade, enable the demo-loop, or submit any order;
- use live credentials or touch a live broker environment;
- tune any strategy parameter;
- claim financing is "solved" — it is not, and stays a live blocker;
- modify or overwrite prior campaign reports/artifacts (CAMPAIGN_001–009)
  except to *link* to them from new documents;
- turn Lean into the main runtime, or require any paid service.

## Safety invariants (must hold at every commit)

1. `configs/approved_strategies.yaml` remains **empty** (`approved: []`).
2. `paper-loop`, `demo-loop`, and the live/practice path **refuse**
   every current strategy (the approved-strategy guard).
3. Backtesting / research commands remain **available** — the guard
   gates loops only, never backtests.
4. No real credentials are staged, logged, or committed; `.env` and
   `.env.*` stay gitignored.
5. Prior campaign reports and run artifacts are **immutable**.
6. `pytest` and `ruff check` stay green.

## Expected deliverables

- **Phase 0:** `docs/research/INFRA_FOUNDATION_001_PLAN.md` (this file).
- **Phase 1:** an H4→D1 aggregation module, a CLI/script entry point,
  tests, and `docs/research/D1_AGGREGATION_DESIGN.md`.
- **Phase 2:** a `FinancingModel` interface with `NoFinancingModel`,
  `ConservativeStressFinancingModel`, and a future-observed placeholder;
  a financing-treatment enum surfaced in report metadata; tests; and
  `docs/research/FINANCING_MODEL_DESIGN.md`.
- **Phase 3:** `docs/research/LEAN_PARITY_DESIGN.md` and a
  `research/lean_parity/` skeleton targeting the CAMPAIGN_002 H4
  baseline.
- **Phase 4:** `docs/research/EVIDENCE_MANIFEST.json`,
  `scripts/validate_research_archive.py` with tests, and an updated
  `docs/research/EVIDENCE_INDEX.md`.
- **Phase 5:** `docs/research/STRATEGY_APPROVAL_PROCESS.md`, a validated
  schema for `approved_strategies.yaml` entries, and tests. The file
  stays empty.
- **Phase 6:** updated `README.md` / `docs/runbooks.md`, and
  `docs/research/INFRA_FOUNDATION_001_SUMMARY.md`.

## Validation commands

Run from the repo root:

```bash
# Full test suite (unit + integration).
.venv/bin/python -m pytest -q

# Targeted guard / safety tests.
.venv/bin/python -m pytest tests/unit/test_approved_strategies.py -q

# Lint.
ruff check src tests scripts

# CLI refusal smoke tests — both must print a refusal and exit 2.
.venv/bin/bot paper-loop --config configs/paper.yaml --once
.venv/bin/bot demo-loop  --config configs/practice.yaml --once

# Research-archive validation (added in Phase 4).
.venv/bin/python scripts/validate_research_archive.py

# Verify the registry is still empty.
grep -nE '^[^#]' configs/approved_strategies.yaml   # => approved: []
```

## Phase 0 audit result

Performed 2026-05-22 on branch `infra-research-foundation-001`:

- Branch base: `8c76dec` (research-freeze HEAD); working tree clean.
- `configs/approved_strategies.yaml`: `approved: []` — empty. ✔
- Approved-strategy guard wired into `run_paper_loop`,
  `run_practice_loop`, and the `paper-loop` / `demo-loop` CLI commands;
  **not** in the backtest path. ✔
- `paper-loop` and `demo-loop` refuse all current strategies (verified
  by CLI smoke test, exit 2, and 19 guard tests). ✔
- Backtests remain available (guard is loop-only; full suite passes). ✔
- No real credentials in tracked files — the only token/account-shaped
  strings are obvious fakes inside `tests/unit/test_logging_redaction.py`
  that exist to test redaction. `.env` and `.env.local` are gitignored. ✔

Phase 0 safety verification: **all invariants hold.**
