# OANDA Practice Read-Only Integration Sprint 001 — Plan

**Date:** 2026-05-22 · **Branch:** `oanda-practice-readonly-001`
**Base commit:** `359b3e4` (HEAD of `infra-data-parity-001`)

## Purpose

The previous sprint (`infra-data-parity-001`) built the data-rehydration
and Lean-parity tooling but could not *exercise* it: no OANDA practice
credentials were present, so every real-data phase shipped ready-to-run
and documented its blocker.

OANDA **practice** credentials are now loaded locally. This sprint
performs a complete **read-only** integration and data-foundation pass:

- safely verify the practice credentials without exposing them;
- verify every read-only broker endpoint the repo relies on;
- validate instrument metadata used for sizing / pip / margin;
- validate candle fetching and provenance;
- rehydrate the real OANDA H4 research store the prior sprint needed;
- run data-quality audits over that store;
- run the full six-pair D1AGG + next-bar-open diagnostic smoke;
- generate Lean-parity export artifacts from the real H4 store;
- optionally run a local Lean parity dry run if Lean is installed;
- harden credential redaction and read-only safety;
- preserve the research freeze.

It is **not** a strategy campaign, **not** paper/demo/live trading, and
**not** a data-synthesis exercise. Every backtest-shaped run here is
**diagnostic / parity only** and cannot produce a verdict, a
recommendation, or an approval.

## Non-goals

This sprint will **not**:

- submit, create, modify, or close any order or trade;
- run any strategy campaign, or produce any strategy verdict /
  recommendation;
- approve any strategy, or edit `configs/approved_strategies.yaml`
  except to verify it stays empty (`approved: []`);
- run `paper-loop` or `demo-loop`, or make either easier to run;
- use live credentials or touch any live broker environment;
- call any OANDA **order / trade / position-modifying** endpoint;
- fall back to synthetic data for anything described as "real";
- tune any strategy parameter;
- claim a parity result as a strategy result — CAMPAIGN_002 stays
  REJECT regardless of any parity outcome;
- rerun or modify prior campaigns (CAMPAIGN_001–009) or their
  artifacts, except to *link* to them from new documents;
- require any QuantConnect cloud job or paid service;
- print, log, or commit any credential value.

## Safety invariants (must hold at every commit)

1. `configs/approved_strategies.yaml` stays empty (`approved: []`).
2. `paper-loop`, `demo-loop`, and the live path refuse every strategy.
3. Backtesting / diagnostics stay available; loops stay gated.
4. **Never** live credentials. Practice credentials only, and only for
   **read-only** endpoints.
5. No credential value — account id or token — is printed, logged, or
   committed. `.env` / `.env.*` stay gitignored.
6. No `data/*.sqlite3` store is committed. Market-data stores are local
   and gitignored.
7. No synthetic data is presented as real. A "real OANDA" path either
   uses real OANDA data or reports a blocker.
8. Prior campaign reports and artifacts (CAMPAIGN_001–009) are immutable.
9. `pytest` and `ruff check src tests scripts` stay green.
10. Every new diagnostic / parity artifact is marked
    `strategy_evidence: false` (or equivalent prose) and claims no
    approval.

## Read-only rules

- **Practice only.** `broker.environment: practice`, `*_PRACTICE` env
  vars. The practice-data environment guard (`forex_bot.guards`) must
  pass before any network call.
- **Read-only OANDA endpoints only**, namely:
  - `GET /v3/accounts/{id}/summary` — account summary
  - `GET /v3/accounts/{id}` — account details
  - `GET /v3/accounts/{id}/instruments` — instrument list / metadata
  - `GET /v3/accounts/{id}/pricing` — pricing snapshot
  - `GET /v3/accounts/{id}/instruments/{ins}/candles` — candles
  - `GET /v3/accounts/{id}/transactions*` — transaction history (read)
  - `GET /v3/accounts/{id}/openTrades`, `/openPositions` — read, if
    implemented in the repo
- A script that needs network access **refuses** when the environment
  is `live`, when order-submission config is enabled, or when
  credentials are missing — and exits non-zero.
- Account ids are redacted in every output (first/last 3 chars).
  Tokens never appear in any output, log, or committed file.

## Order-submission prohibitions

The following OANDA endpoints are **forbidden** in this sprint and must
never be called by any code added or run here:

- `POST /v3/accounts/{id}/orders` — create order
- `PUT  /v3/accounts/{id}/orders/{id}` — replace order
- `PUT  /v3/accounts/{id}/orders/{id}/cancel` — cancel order
- `PUT  /v3/accounts/{id}/trades/{id}/close` — close trade
- `PUT  /v3/accounts/{id}/trades/{id}/orders` — modify trade SL/TP
- `PUT  /v3/accounts/{id}/positions/{ins}/close` — close position
- any `POST`/`PUT`/`PATCH`/`DELETE` against the practice account.

New scripts call only `GET`. The existing `OandaBroker.submit_order`
already refuses a live environment; this sprint never invokes it.

## Expected phases

| phase | deliverable | needs credentials / data? |
|---|---|---|
| 0 | Baseline verification & this plan | no |
| 1 | Credential & environment gate | **yes — practice credentials** |
| 2 | Read-only OANDA API health check | needs Phase 1 |
| 3 | Instrument metadata verification | needs Phase 1 |
| 4 | Real OANDA H4 data rehydration | needs Phase 1 |
| 5 | H4 data audit & quality report | needs the Phase 4 store |
| 6 | Six-pair D1AGG + next-bar-open diagnostic smoke | needs the Phase 4 store |
| 7 | Lean-parity export from real H4 data | needs the Phase 4 store |
| 8 | Optional local Lean parity dry run | needs Phase 7 + a local Lean install |
| 9 | Safety & secret regression scan | no |
| 10 | Final summary & handoff | no |

Each phase commits separately when it produces meaningful code or docs.
A blocked phase is documented and the next independent phase proceeds.
If credentials are missing or ambiguous, all OANDA network work stops,
a `OANDA_PRACTICE_READONLY_001_BLOCKED.md` is written, and only the
data-independent phases (0, 9, 10) ship.

## Expected artifacts

- **Phase 0:** `docs/research/OANDA_PRACTICE_READONLY_001_PLAN.md` (this).
- **Phase 1:** `docs/research/OANDA_PRACTICE_CREDENTIAL_CHECK.md` (or
  `OANDA_PRACTICE_READONLY_001_BLOCKED.md` on failure).
- **Phase 2:** `scripts/oanda_readonly_healthcheck.py`,
  `docs/research/OANDA_READONLY_HEALTHCHECK_RESULT.md`, tests.
- **Phase 3:** `docs/research/OANDA_INSTRUMENT_METADATA_AUDIT.md`,
  tests if mismatches surface code assumptions.
- **Phase 4:** the local `data/oanda_h4_research.sqlite3` store
  (**not committed**), `docs/research/OANDA_H4_REHYDRATION_RESULT.md`.
- **Phase 5:** `docs/research/OANDA_H4_DATA_QUALITY_AUDIT.md`.
- **Phase 6:** `backtests/diagnostics/d1agg_next_open_six_pair_smoke.md`.
- **Phase 7:** `research/lean_parity/exports/campaign_002_h4/` (manifest,
  config, provenance, parameter mapping, tolerance notes), an updated
  `docs/research/LEAN_PARITY_EXECUTION_GUIDE.md`, tests.
- **Phase 8:** `docs/research/LEAN_PARITY_LOCAL_STATUS.md` and, if Lean
  is installed, `docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md` plus
  small results under `research/lean_parity/results/campaign_002_h4/`.
- **Phase 9:** archive / freeze re-validation; secret-scan output.
- **Phase 10:** `docs/research/OANDA_PRACTICE_READONLY_001_SUMMARY.md`.

The SQLite store and any large market-data export are **not** committed.

## How credentials must be handled

- Credentials live only in a local, gitignored `.env`
  (`OANDA_ENVIRONMENT`, `OANDA_ACCOUNT_ID_PRACTICE`,
  `OANDA_ACCESS_TOKEN_PRACTICE`). `.env` and `.env.*` are gitignored;
  only `.env.example` (placeholders) is tracked.
- A script may report **whether** a credential env var is set, never
  its value. Account ids are redacted to first/last 3 chars
  (`abc…001`). Tokens are never echoed, logged, or written.
- Every generated document is secret-scanned before commit. The
  research-freeze gate's `no_credentials` check scans all committed
  artifacts.
- `.env` is never staged or committed. The live `*_LIVE` env vars are
  never read by any code run in this sprint.

## Validation commands

```bash
# Full test suite.
python3 -m pytest -q

# Lint.
ruff check src tests scripts

# Research-archive integrity and the research-freeze gate.
python3 scripts/validate_research_archive.py
python3 scripts/check_research_freeze.py

# CLI refusal smoke tests — both must exit 2.
bot paper-loop --config configs/paper.yaml --once
bot demo-loop  --config configs/practice.yaml --once

# Registry still empty.
grep -nE '^[^#]' configs/approved_strategies.yaml   # => approved: []

# Confirm no data store / credentials are staged.
git status --short | grep -E '\.sqlite3|\.env' || echo "clean"
```

## Phase 0 verification result

Performed 2026-05-22 on branch `oanda-practice-readonly-001`:

- Branch base `359b3e4` (HEAD of `infra-data-parity-001`); working tree
  clean. [verified]
- `configs/approved_strategies.yaml`: `approved: []` — empty. [verified]
- `paper-loop` and `demo-loop` refuse (CLI exit 2). The approval guard
  (`assert_loop_strategies_approved`) runs **before** `_build_broker`
  in both `cli.py` commands — the loop refuses before any broker is
  constructed or any network call is made. [verified]
- `validate_research_archive.py` — all checks pass. [verified]
- `check_research_freeze.py` — all checks pass. [verified]
- No `.env` or `*.sqlite3` tracked; nothing credential-shaped staged.
  [verified]
- Targeted approval/guard pytest (93 tests) and the full suite
  (315 tests) pass; `ruff check src tests scripts` clean. [verified]

Phase 0 safety verification: **all invariants hold.**
