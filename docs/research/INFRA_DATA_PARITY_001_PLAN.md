# Infrastructure Data/Parity Sprint 001 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-data-parity-001`
**Base commit:** `340ae64` (HEAD of `infra-execution-fidelity-001`)

## Purpose

The previous sprint (`infra-execution-fidelity-001`) built the
execution-fidelity infrastructure — the next-bar-open fill model, the
D1AGG smoke harness, the Lean-parity export scripts, observed-financing
capture, and the research-freeze gate. Several of those tools could not
be *exercised* because no real OANDA H4 candle store was present locally.

This sprint makes the repo **more reproducible and independently
verifiable** by putting real data through that infrastructure:

- rebuild / verify a local real OANDA practice H4 data store;
- run the full six-pair D1AGG + next-bar-open diagnostic smoke;
- produce Lean-parity export artifacts for the CAMPAIGN_002 H4 baseline;
- optionally run a local Lean parity dry run, if Lean is installed;
- write a data-rehydration runbook so any of this is reproducible.

It is **not a strategy campaign.** Any backtest executed here is
parity / diagnostic only and **cannot** produce a trading
recommendation, a verdict, or an approval.

## Non-goals

This sprint will **not**:

- run any strategy campaign, or produce any strategy verdict or
  recommendation;
- approve any strategy, or edit `configs/approved_strategies.yaml`
  except to verify it stays empty (`approved: []`);
- paper-trade, enable the demo-loop, submit any order, or make any of
  those easier to run;
- use live credentials or touch any live broker environment;
- fall back to synthetic data for anything described as "real";
- tune any strategy parameter;
- claim a parity result as a strategy result — CAMPAIGN_002 stays
  REJECT regardless of any parity outcome;
- rerun or modify prior campaigns (CAMPAIGN_001–009) or their
  artifacts, except to *link* to them from new documents;
- require any QuantConnect cloud job or paid service.

## Phases

| phase | deliverable | needs credentials / data? |
|---|---|---|
| 0 | Baseline verification & this plan | no |
| 1 | Local real OANDA H4 store rehydration / verification | **yes — OANDA practice credentials** |
| 2 | Full six-pair D1AGG + next-bar-open diagnostic smoke | needs the Phase 1 store |
| 3 | Lean-parity data export for CAMPAIGN_002 H4 | needs the Phase 1 store |
| 4 | Optional local Lean parity dry run | needs Phase 3 + a local Lean install |
| 5 | Data-reproducibility & rehydration runbook | no |
| 6 | Research-freeze & archive hardening | no |
| 7 | Final docs, validation & handoff | no |

Each phase commits separately when it produces meaningful code or docs.
A blocked phase is documented and the next independent phase proceeds.
Phases 1–4 are data-dependent; phases 0 and 5–7 are not — if data is
unavailable, the data-independent phases still ship in full, and the
data-dependent scripts ship **ready to run** the moment data exists.

### Credential-availability status (checked 2026-05-22)

`.env` is absent and `OANDA_ACCOUNT_ID_PRACTICE` /
`OANDA_ACCESS_TOKEN_PRACTICE` are unset. **OANDA practice credentials
are not available in this environment.** Per the Phase 1 rules, the
H4-fetch is therefore **blocked**: Phase 1 ships the rehydration script,
manifest, and tests (ready to run), and Phases 2–4 ship their tooling
and documented blockers. A human can lift the blocker by providing
practice credentials and re-running the documented commands.

## Safety invariants (must hold at every commit)

1. `configs/approved_strategies.yaml` stays empty (`approved: []`).
2. paper-loop, demo-loop, and the live path refuse every strategy.
3. Backtesting / diagnostics stay available; loops stay gated.
4. **Never** live credentials. Practice credentials only, and only for
   read-only candle fetches.
5. No credential value — account id or token — is printed, logged, or
   committed. `.env` / `.env.*` stay gitignored.
6. No `data/*.sqlite3` store is committed. Market-data stores are local
   and gitignored.
7. No synthetic data is presented as real. A "real OANDA" path either
   uses real OANDA data or reports a blocker.
8. Prior campaign reports and artifacts (CAMPAIGN_001–009) are immutable.
9. `pytest` and `ruff check` stay green.

## Exact data-handling rules

- **Source:** OANDA **practice** environment only
  (`broker.environment: practice`, `*_PRACTICE` env vars). The
  practice-data environment guard (`forex_bot.guards`) must pass.
- **Universe:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF.
- **Granularity / window:** H4, 2020-01-01 through 2026-05-20.
- **Completeness:** completed candles only; incomplete candles dropped.
- **Store:** a gitignored local SQLite file, default
  `data/oanda_h4_research.sqlite3`. `data/` is already gitignored.
- **Provenance:** every fetch records source label, host, window,
  candle counts, and raw + normalized SHA-256 hashes in `data_sources`.
- **No synthetic fallback:** if a fetch fails or credentials are
  missing, the script stops and reports — it never synthesizes.
- **Redaction:** account ids are redacted in all output; tokens never
  appear. Committed artifacts carry hashes and counts, never raw data
  or credentials.
- **Committed vs not:** scripts, manifests, hashes, small diagnostic
  reports, and small parity configs/samples are committed. The SQLite
  store and any large market-data export are **not**.

## Expected artifacts

- **Phase 0:** `docs/research/INFRA_DATA_PARITY_001_PLAN.md` (this file).
- **Phase 1:** `scripts/rehydrate_oanda_h4_store.py`,
  `docs/research/OANDA_H4_DATA_REHYDRATION.md`, tests. The SQLite store
  is produced locally and **not** committed.
- **Phase 2:** `backtests/diagnostics/d1agg_next_open_six_pair_smoke.md`,
  smoke tooling/tests.
- **Phase 3:** `research/lean_parity/exports/campaign_002_h4/` (manifest,
  config, parameter mapping, tolerance notes; data export only if
  small), an updated `LEAN_PARITY_EXECUTION_GUIDE.md`, tests.
- **Phase 4:** `docs/research/LEAN_PARITY_LOCAL_STATUS.md` and, if Lean
  is installed, `docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md` plus
  small results under `research/lean_parity/results/campaign_002_h4/`.
- **Phase 5:** `docs/research/DATA_REHYDRATION_RUNBOOK.md`,
  `scripts/prepare_local_research_data.py`, tests.
- **Phase 6:** archive / freeze re-validation; `EVIDENCE_INDEX.md`
  updated with diagnostic/parity references if useful.
- **Phase 7:** `docs/research/INFRA_DATA_PARITY_001_SUMMARY.md`.

## Validation commands

```bash
# Full test suite.
.venv/bin/python -m pytest -q

# Lint.
.venv/bin/ruff check src tests scripts

# Research-archive integrity and the research-freeze gate.
.venv/bin/python scripts/validate_research_archive.py
.venv/bin/python scripts/check_research_freeze.py

# CLI refusal smoke tests — both must exit 2.
.venv/bin/bot paper-loop --config configs/paper.yaml --once
.venv/bin/bot demo-loop  --config configs/practice.yaml --once

# Registry still empty.
grep -nE '^[^#]' configs/approved_strategies.yaml   # => approved: []

# Confirm no data store / credentials are staged.
git status --short | grep -E '\.sqlite3|\.env' || echo "clean"
```

## Phase 0 verification result

Performed 2026-05-22 on branch `infra-data-parity-001`:

- Branch base `340ae64`; working tree clean.
- `configs/approved_strategies.yaml`: `approved: []` — empty. [verified]
- paper-loop and demo-loop refuse (CLI exit 2). [verified]
- `validate_research_archive.py` — all checks pass. [verified]
- `check_research_freeze.py` — all checks pass. [verified]
- No `.env` or `*.sqlite3` tracked; no credentials staged. [verified]
- OANDA practice credentials **not available** — Phase 1 fetch blocked
  (documented above). [verified]

Phase 0 safety verification: **all invariants hold.**
