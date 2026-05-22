# Infrastructure Lean-Parity Sprint 001 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-001`
**Base commit:** `bf4ec44` (HEAD of `oanda-practice-readonly-001`)

## Purpose

The `oanda-practice-readonly-001` sprint built the real OANDA practice
H4 store (six pairs), produced a six-pair Lean-parity export, and
confirmed Lean was not installed. CAMPAIGN_002 — the parity target —
originally used **seven** instruments: the six majors **plus NZD_USD**.

This sprint completes **independent-engine parity readiness** for the
CAMPAIGN_002 H4 baseline:

- add NZD_USD to the local real OANDA H4 store (practice credentials);
- export a complete **seven-pair** CAMPAIGN_002 H4 Lean-parity bundle;
- install or detect local Lean;
- run a local Lean parity dry run if Lean is available, else document
  the exact remaining blocker;
- build a reproducible **custom-engine** CAMPAIGN_002 H4 parity
  reproduction so both engines can be compared side-by-side;
- write a human-readable parity status report.

It is **not** a strategy campaign. CAMPAIGN_002 stays **REJECT**
regardless of any parity output. Parity verifies the *measurement
instrument* (the bespoke backtest engine); it cannot approve a strategy.

## Non-goals

This sprint will **not**:

- run a new strategy campaign, hypothesis, or research decision;
- produce a strategy verdict or trading recommendation;
- approve any strategy, or edit `configs/approved_strategies.yaml`
  except to verify it stays empty (`approved: []`);
- tune any strategy parameter;
- paper / demo / live trade, or make any of those easier to run;
- submit, create, close, or modify any order;
- use live credentials or touch any live broker environment;
- run any QuantConnect **cloud** job or require a paid service;
- fall back to synthetic data for anything described as "real";
- treat a parity result as a strategy result — CAMPAIGN_002 stays
  REJECT;
- rerun or modify prior campaign artifacts (CAMPAIGN_001–009).

## Phases

| phase | deliverable | needs credentials / Lean? |
|---|---|---|
| 0 | Baseline verification & this plan | no |
| 1 | NZD_USD H4 rehydration; seven-pair data audit | **practice credentials** |
| 2 | Seven-pair CAMPAIGN_002 H4 Lean-parity export | needs the Phase 1 store |
| 3 | Lean local installation / detection | no — local only |
| 4 | Local Lean parity dry run (if Lean available) | needs local Lean |
| 5 | Custom-engine parity reproduction package | needs the Phase 1 store |
| 6 | Parity comparison / status report | no |
| 7 | Safety & archive finalization | no |
| 8 | Final summary & handoff | no |

Each phase commits separately. A blocked phase is documented and the
next independent phase proceeds. Phase 4 is gated on Lean being locally
runnable; if it is not, the blocker is documented and the phase skipped.

## Safety invariants (must hold at every commit)

1. `configs/approved_strategies.yaml` stays empty (`approved: []`).
2. `paper-loop`, `demo-loop`, and the live path refuse every strategy.
3. Backtesting / diagnostics stay available; loops stay gated.
4. **Never** live credentials. Practice credentials only, read-only.
5. No credential value — account id or token — is printed, logged, or
   committed. `.env` / `.env.*` stay gitignored.
6. No `data/*.sqlite3` store is committed. Market-data stores are local
   and gitignored.
7. No synthetic data is presented as real.
8. Prior campaign reports and artifacts (CAMPAIGN_001–009) are immutable.
9. `pytest` and `ruff check src tests scripts` stay green.
10. Every new diagnostic / parity artifact is marked
    `strategy_evidence: false` and claims no approval.
11. No large candle CSV is committed — Lean-parity CSV exports stay
    gitignored.

## Data-handling rules

- **Source:** OANDA **practice** only (`broker.environment: practice`,
  `*_PRACTICE` env vars). The practice-data environment guard must pass.
- **Universe (this sprint):** the seven CAMPAIGN_002 instruments —
  EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, **NZD_USD**.
- **Granularity / window:** H4, 2020-01-01 through 2026-05-20.
- **Completeness:** completed candles only; incomplete candles dropped.
- **Store:** the gitignored local SQLite file
  `data/oanda_h4_research.sqlite3`. The six-pair store from the prior
  sprint persists; NZD_USD is upserted into it (idempotent).
- **Provenance:** every fetch records source label, host, window,
  candle counts, and raw + normalized SHA-256 hashes.
- **No synthetic fallback:** a failed fetch stops and reports.
- **Committed vs not:** scripts, manifests, provenance JSONs, small
  diagnostic reports, and small parity configs are committed. The
  SQLite store and the bulky Lean candle CSVs are **not**.

## Lean-parity goals

- **Verification, not research.** A Lean re-implementation of the
  CAMPAIGN_002 H4 `trend_following` baseline checks the bespoke engine.
  A parity PASS corroborates the engine; a FAIL localizes an engine bug.
  Neither outcome approves a strategy.
- **Seven-pair completeness:** the export bundle must cover all seven
  CAMPAIGN_002 instruments so the parity comparison is not partial.
- **Both engines reproducible:** the custom engine's CAMPAIGN_002 H4
  baseline must be re-runnable side-by-side (Phase 5), so a future Lean
  run has a committed, hash-pinned reference to compare against.
- **Local only:** Lean's local Docker backtester — no QuantConnect
  cloud, no paid tier, no brokerage connection.
- **Fill timing:** CAMPAIGN_002 predates the fill-timing model, so
  parity uses `signal_bar_close` (see `FILL_TIMING_MODEL.md`).
- **Excluded from parity:** financing (unmodeled in both engines); the
  bespoke RiskEngine's spread / session / correlation / margin filters
  (bespoke — compare only the bespoke engine's accepted trades).

## Expected artifacts

- **Phase 0:** `docs/research/INFRA_LEAN_PARITY_001_PLAN.md` (this).
- **Phase 1:** `docs/research/OANDA_H4_NZDUSD_REHYDRATION_RESULT.md`,
  `docs/research/OANDA_H4_DATA_QUALITY_AUDIT_7PAIR.md`.
- **Phase 2:** updated `research/lean_parity/exports/campaign_002_h4/`
  bundle (seven-pair manifest + provenance JSONs), updated
  `LEAN_PARITY_EXECUTION_GUIDE.md`.
- **Phase 3:** updated `docs/research/LEAN_PARITY_LOCAL_STATUS.md`.
- **Phase 4:** `docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md` (if
  Lean runs) or `docs/research/LEAN_PARITY_CAMPAIGN_002_BLOCKED.md`.
- **Phase 5:** `scripts/run_custom_campaign_002_h4_parity.py`,
  `backtests/diagnostics/custom_campaign_002_h4_parity.md`.
- **Phase 6:** `docs/research/CAMPAIGN_002_H4_PARITY_STATUS.md`.
- **Phase 7:** archive / freeze re-validation; manifest/index updates.
- **Phase 8:** `docs/research/INFRA_LEAN_PARITY_001_SUMMARY.md`.

## Validation commands

```bash
# Full test suite.
python3 -m pytest -q

# Lint.
ruff check src tests scripts

# Research-archive integrity, the research-freeze gate, secret scan.
python3 scripts/validate_research_archive.py
python3 scripts/check_research_freeze.py
set -a && source .env && set +a && python3 scripts/scan_artifacts_for_secrets.py

# CLI refusal smoke tests — both must exit 2.
bot paper-loop --config configs/paper.yaml --once
bot demo-loop  --config configs/practice.yaml --once

# Registry still empty.
grep -nE '^[^#]' configs/approved_strategies.yaml   # => approved: []

# Confirm no data store / credentials / bulky CSV are staged.
git status --short | grep -E '\.sqlite3|\.env|exports/.*\.csv' || echo "clean"
```

## Phase 0 verification result

Performed 2026-05-22 on branch `infra-lean-parity-001`:

- Branch base `bf4ec44` (HEAD of `oanda-practice-readonly-001`); working
  tree clean. [verified]
- `configs/approved_strategies.yaml`: `approved: []` — empty. [verified]
- `paper-loop` and `demo-loop` refuse (CLI exit 2). [verified]
- `validate_research_archive.py`, `check_research_freeze.py`,
  `scan_artifacts_for_secrets.py` — all pass. [verified]
- Local H4 store present: `data/oanda_h4_research.sqlite3`, 59,587 real
  OANDA practice candles across six pairs; NZD_USD not yet present.
  [verified]
- Practice credentials present and safe — `OANDA_ENVIRONMENT=practice`,
  practice account id + token set, live vars are placeholders. No
  secret value printed. [verified]
- Targeted approval/guard pytest (93) pass; `ruff check` clean.
  [verified]

Phase 0 safety verification: **all invariants hold.**
