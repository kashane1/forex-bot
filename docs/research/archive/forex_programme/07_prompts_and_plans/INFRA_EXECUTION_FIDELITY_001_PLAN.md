# Infrastructure Execution-Fidelity Sprint 001 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-execution-fidelity-001`
**Base commit:** `107b3d5` (HEAD of `infra-foundation-001`, Phase 6)

## Purpose

The repo is research-only and frozen: Research Marathon 001 closed
**NO-GO**, no strategy is approved, and every order-capable loop refuses
to start. The previous sprint (`infra-foundation-001`) built the
research-safety foundation — the approval registry, H4→D1AGG
aggregation, the financing-model interface, the Lean-parity design, and
the research-archive validator.

This sprint **improves backtest / execution fidelity and independent
validation readiness**. It makes the measurement instrument more
honest and more auditable, and prepares the seams that a *future*,
human-authorized validation effort would need.

It **does not look for a trading edge.** It runs no strategy campaign,
produces no strategy verdict, approves nothing, and does not make
paper / demo / live execution any easier to start. It is pure
fidelity, auditability, and future-validation-readiness work.

## Non-goals

This sprint will **not**:

- run any strategy campaign or produce any new strategy result or
  verdict;
- approve any strategy, or edit `configs/approved_strategies.yaml`
  except to verify it remains empty (`approved: []`);
- paper-trade, enable the demo-loop, submit any order, or make any of
  those easier to run;
- use live credentials or touch any live broker environment;
- connect to OANDA at all (no candle fetch, no account calls);
- tune any strategy parameter;
- claim historical financing is "solved" — it is not, and stays a hard
  live blocker;
- rerun or modify prior campaigns (CAMPAIGN_001–009) or their
  artifacts, except to *link* to them from new documents;
- turn Lean into the main runtime, run a QuantConnect cloud job, or
  require any paid service.

## Phases

| phase | deliverable | independent? |
|---|---|---|
| 0 | Baseline verification & this plan | — |
| 1 | Next-bar-open fill-timing model for the backtester | yes |
| 2 | D1AGG + next-bar-open mechanical smoke validation | depends on Phase 1 |
| 3 | Lean parity executable preparation (local-only) | yes |
| 4 | Observed-financing-event capture design & schema | yes |
| 5 | Research-freeze & approval-guard regression hardening | yes |
| 6 | Final docs, full validation & handoff | depends on 0–5 |

Each phase commits separately when it produces meaningful code or docs.
If a phase is blocked, the blocker is documented and the next
independent phase proceeds. The sprint stops only if proceeding would
risk credentials, order submission, or corruption of prior evidence.

## Safety invariants (must hold at every commit)

1. `configs/approved_strategies.yaml` remains **empty** (`approved: []`).
2. `paper-loop`, `demo-loop`, and the live/practice path **refuse**
   every current strategy via the approved-strategy guard.
3. Backtesting / research commands remain **available** — the guard
   gates loops only, never backtests. The new fill-timing model is a
   backtest-fidelity feature and never relaxes a loop gate.
4. No real credentials are staged, logged, or committed; `.env` and
   `.env.*` stay gitignored. No OANDA connection is made.
5. Prior campaign reports and run artifacts (CAMPAIGN_001–009) are
   **immutable** — referenced, never edited or overwritten.
6. The default backtest fill timing reproduces prior campaign
   behaviour exactly; `next_bar_open` is strictly opt-in.
7. `pytest` and `ruff check` stay green.

## Expected deliverables

- **Phase 0:** `docs/research/INFRA_EXECUTION_FIDELITY_001_PLAN.md`
  (this file).
- **Phase 1:** a configurable fill-timing model
  (`signal_bar_close` | `next_bar_open`) in the backtest engine, a
  `backtest.fill_timing` config field, `--fill-timing` CLI override,
  trade-log / export propagation of the fill timing, tests, and
  `docs/research/FILL_TIMING_MODEL.md`.
- **Phase 2:** `scripts/smoke_d1agg_next_open.py` (diagnostic-only),
  the report `backtests/diagnostics/d1agg_next_open_smoke.md`, and
  smoke tests/assertions.
- **Phase 3:** a local-only Lean parity preparation layer — an updated
  `research/lean_parity/` (README install commands, export format
  spec, CAMPAIGN_002 mapping & tolerance checklists), the scripts
  `scripts/export_lean_parity_data.py` and
  `scripts/build_lean_parity_config.py`, and
  `docs/research/LEAN_PARITY_EXECUTION_GUIDE.md`.
- **Phase 4:** an observed-financing-event schema + repository, an
  OANDA `DAILY_FINANCING` mapper, fixture-only tests, and
  `docs/research/OBSERVED_FINANCING_CAPTURE.md`.
- **Phase 5:** research-freeze regression tests, the CI-style script
  `scripts/check_research_freeze.py`, and a "before merging research
  infra" checklist in `docs/runbooks.md`.
- **Phase 6:** `docs/research/INFRA_EXECUTION_FIDELITY_001_SUMMARY.md`,
  README / runbooks updates if needed, and full validation results.

## Validation commands

Run from the repo root:

```bash
# Full test suite (unit + integration).
.venv/bin/python -m pytest -q

# Targeted approval / guard / fidelity tests.
.venv/bin/python -m pytest tests/unit/test_approved_strategies.py \
    tests/unit/test_approval.py tests/unit/test_fill_timing.py -q

# Lint.
.venv/bin/ruff check src tests scripts

# CLI refusal smoke tests — both must print a refusal and exit 2.
.venv/bin/bot paper-loop --config configs/paper.yaml --once
.venv/bin/bot demo-loop  --config configs/practice.yaml --once

# Research-archive validation.
.venv/bin/python scripts/validate_research_archive.py

# Research-freeze gate (added in Phase 5).
.venv/bin/python scripts/check_research_freeze.py

# Verify the registry is still empty.
grep -nE '^[^#]' configs/approved_strategies.yaml   # => approved: []
```

## Phase 0 verification result

Performed 2026-05-22 on branch `infra-execution-fidelity-001`:

- Branch base: `107b3d5` (`infra-foundation-001` Phase 6 HEAD);
  working tree clean.
- `configs/approved_strategies.yaml`: `approved: []` — empty. [verified]
- Approved-strategy guard wired into `run_paper_loop`,
  `run_practice_loop`, and the `paper-loop` / `demo-loop` CLI commands;
  **not** in the backtest path. [verified]
- `paper-loop` and `demo-loop` refuse all current strategies (CLI smoke
  test exits 2; guard test suite passes). [verified]
- Backtests remain available — the guard gates loops only. [verified]
- Research-archive validator passes all checks. [verified]
- No real credentials in tracked files; `.env` / `.env.*` gitignored;
  no OANDA connection made by this sprint. [verified]

Phase 0 safety verification: **all invariants hold.** Detailed
verification output is recorded in the Phase 6 summary.
