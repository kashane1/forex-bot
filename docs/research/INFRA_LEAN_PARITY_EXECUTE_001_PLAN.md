# Infrastructure Lean-Parity Execute Sprint 001 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-execute-001`
**Base commit:** `f1c9d9f` (HEAD of `infra-lean-parity-run-001`)

## Purpose

The `infra-lean-parity-run-001` sprint authored the faithful Lean
parity algorithm and built the comparison harness, but could not
execute a local Lean backtest — `lean init` required a QuantConnect
account login, which prior sprints' rules forbade.

This sprint **may use local Lean CLI credentials if they are already
present on this machine** (`~/.lean/credentials`). If they are, it
runs the local Lean parity dry run, compares against the bespoke
reference, and documents any divergence. If they are not, it documents
the precise blocker — without faking results, without creating a QC
account itself, without submitting cloud jobs, and without connecting
to any brokerage.

It is **verification only**. CAMPAIGN_002 remains **REJECT** regardless
of any parity outcome; the research freeze is intact.

## Non-goals

This sprint will **not**:

- run a new strategy campaign, hypothesis, or research decision;
- produce a strategy verdict or trading recommendation;
- approve any strategy, or edit `configs/approved_strategies.yaml`
  except to verify it stays empty (`approved: []`);
- tune any strategy parameter or change any CAMPAIGN_002 rule;
- alter the bespoke engine;
- paper / demo / live trade, or make any of those easier to run;
- submit any order or use brokerage / OANDA live credentials;
- submit a **QuantConnect cloud backtest** or use any paid QC tier;
- create a QuantConnect account on the user's behalf;
- print, log, or commit any QuantConnect user id, API token, or any
  other credential.

## Auth-handling rules

- Treat `~/.lean/credentials` as a local secret store: **detect
  presence only**, never read its contents into output, never echo
  values, never commit it.
- If the file is absent → the Lean-execution phases are **blocked**;
  document precisely. Do **not** prompt for credentials, do **not**
  trigger `lean init` interactively (which would request a QC login).
- The local Lean CLI runs in an isolated venv (`/tmp/lean-venv`,
  `lean 1.0.225`) and is invoked only with subcommands that read local
  data and run local Docker backtests — never `lean cloud …`, never
  `lean live …`, never any brokerage operation.

## Local-only execution rules

- All Lean execution happens on the local machine via Lean's local
  Docker backtester. No QuantConnect cloud job is submitted.
- The Lean algorithm consumes the already-exported seven-pair H4 CSVs
  (`research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv`,
  gitignored). It does **not** call OANDA, the QC data API, or any
  brokerage feed.
- Raw Lean output (per-trade CSVs, log files, equity curves) is
  considered bulky and stays under `research/lean_parity/results/`
  (gitignored). Only the compact summary JSON and the comparison
  Markdown are committed.

## Safety invariants (must hold at every commit)

1. `configs/approved_strategies.yaml` stays empty (`approved: []`).
2. `paper-loop`, `demo-loop`, and the live path refuse every strategy.
3. Backtesting / diagnostics stay available; loops stay gated.
4. No credential is printed, logged, or committed: not `.env`, not
   `~/.lean/credentials`, not any QC user id or API token.
5. No `data/*.sqlite3`, no bulky Lean output, and no large candle CSV
   is committed.
6. No synthetic data is presented as real.
7. Prior campaign reports and artifacts (CAMPAIGN_001–009) are
   immutable.
8. `pytest` and `ruff check src tests scripts` stay green.
9. Every new parity artifact is `strategy_evidence: false`.

## Expected phases

| phase | deliverable |
|---|---|
| 0 | Baseline verification & this plan |
| 1 | Lean auth + workspace check (or `LEAN_PARITY_EXECUTE_BLOCKED.md`) |
| 2 | Lean data preflight (only if Phase 1 unblocked) |
| 3 | Local Lean parity run (only if Phases 1–2 pass) |
| 4 | Comparison: Lean vs bespoke reference |
| 5 | Debug Lean parity bugs (only if material divergence) |
| 6 | Final parity status |
| 7 | Safety & final summary |

A blocked phase is documented and the next independent phase proceeds.

## Validation commands

```bash
python3 -m pytest -q
ruff check src tests scripts
python3 scripts/validate_research_archive.py
python3 scripts/check_research_freeze.py
set -a && source .env && set +a && python3 scripts/scan_artifacts_for_secrets.py
bot paper-loop --config configs/paper.yaml --once   # exit 2
bot demo-loop  --config configs/practice.yaml --once # exit 2
grep -nE '^[^#]' configs/approved_strategies.yaml    # => approved: []
git status --short | grep -E '\.sqlite3|\.env|results/' || echo clean
```

## Why this cannot approve a strategy

CAMPAIGN_002 closed **REJECT** in Research Marathon 001. Parity verifies
the *engine* that produced that verdict, not the strategy. A parity
PASS would mean only "two engines agree on the numbers"; the numbers
are a rejected strategy's. A FAIL would mean "the two implementations
disagree" — a software discrepancy to localize. Neither outcome
approves a strategy, lifts the freeze, or enables paper / demo / live.

## Phase 0 verification result

Performed 2026-05-22 on branch `infra-lean-parity-execute-001`:

- Branch base `f1c9d9f`; working tree clean. [verified]
- `configs/approved_strategies.yaml`: `approved: []`. [verified]
- `paper-loop` / `demo-loop` refuse (CLI exit 2). [verified]
- `validate_research_archive.py`, `check_research_freeze.py`,
  `scan_artifacts_for_secrets.py` — all pass. [verified]
- Local artifacts present: H4 store, 7 Lean CSVs, 7 provenance JSONs,
  bespoke reference JSON, Lean algorithm, comparison harness. [verified]
- Lean tooling: `lean 1.0.225` in `/tmp/lean-venv`; Docker 29.1.3
  present. [verified]
- **Lean CLI auth absent** — `~/.lean/credentials` does not exist.
  Phase 1 will hit the blocked path. [verified, no secret printed]
- Targeted approval/guard pytest (36) pass; `ruff check` clean.
  [verified]

Phase 0 safety verification: **all invariants hold.**
