# OANDA Practice Read-Only Integration Sprint 001 — Summary & Handoff

**Date:** 2026-05-22 · **Branch:** `oanda-practice-readonly-001`
**Base commit:** `359b3e4` (HEAD of `infra-data-parity-001`)

This sprint performed a complete **read-only** OANDA practice
integration and data-foundation pass, now that practice credentials are
available locally. It is **not** a strategy campaign: no order was
submitted, no strategy was approved, no trading verdict was produced,
and the research freeze is intact.

## What changed

**New scripts**
- `scripts/oanda_readonly_healthcheck.py` — read-only OANDA practice API
  healthcheck (safety-gated, structurally incapable of order calls).
- `scripts/audit_oanda_instruments.py` — instrument-metadata audit.
- `scripts/audit_h4_data_quality.py` — H4 data-quality audit.
- `scripts/scan_artifacts_for_secrets.py` — credential leak scanner.

**Improved scripts / code**
- `scripts/rehydrate_oanda_h4_store.py` — added a read-only `--report`
  mode that renders the rehydration result doc.
- `scripts/smoke_d1agg_next_open.py` — the report now states
  `strategy_evidence: false` explicitly.
- `src/forex_bot/backtesting/audit.py` — added `classify_gaps` (weekend
  / year-end-holiday / outage-like / suspicious-short).
- `src/forex_bot/broker/oanda.py` — **two real bugs fixed**, surfaced by
  the healthcheck against the live practice API:
  - `_candle_params` no longer sends `includeFirst` on count-only
    requests (OANDA 400-rejects that);
  - `list_open_orders` now calls `/pendingOrders` — the repo previously
    called the non-existent `/openOrders` route (OANDA 404).

**New docs** — the sprint plan, credential check, read-only healthcheck
result, instrument metadata audit, H4 rehydration result, H4 data
quality audit, and this summary (all under `docs/research/`).

**Updated docs** — `LEAN_PARITY_EXECUTION_GUIDE.md`,
`LEAN_PARITY_LOCAL_STATUS.md`, `EVIDENCE_INDEX.md`,
`EVIDENCE_MANIFEST.json` (one diagnostic-artifact description), the
six-pair D1AGG smoke report, and the Lean `EXPORT_MANIFEST.md`.

**Tests** — 53 new tests added; the full suite is **370 passed**.

## What did NOT change

- `configs/approved_strategies.yaml` remains empty (`approved: []`).
- No strategy is approved; no campaign was run; no trading verdict or
  recommendation was produced.
- `paper-loop`, `demo-loop`, and the live path still refuse every
  strategy.
- Prior campaign artifacts (CAMPAIGN_001–009) are untouched.
- No order was submitted, created, modified, or closed.
- No live credentials were used; the live host was never contacted.
- Financing remains **estimated / stress-only** — a standing hard live
  blocker, unchanged by this sprint.

## Credential status

Practice credentials are present and valid. `OANDA_ENVIRONMENT=practice`;
the practice account id and token are set (non-placeholder); the `*_LIVE`
env vars are placeholders and were never selected. The practice-data
environment guard passes. **No credential value — account id or token —
was printed, logged, or committed.** `.env` is gitignored and untracked.
See `OANDA_PRACTICE_CREDENTIAL_CHECK.md`.

## Read-only endpoint health

**9 / 9 read-only endpoints OK** against OANDA practice — account
summary, account details, instruments, pricing, candles, transactions
(`sinceid`), open trades, open positions, pending orders. No order
endpoint was called. The healthcheck surfaced the two broker bugs noted
above, both fixed with regression tests. See
`OANDA_READONLY_HEALTHCHECK_RESULT.md`.

## Instrument metadata status

**7 / 7 instruments verified** — the six-pair research universe plus the
historical NZD_USD (CAMPAIGN_001/002/003), kept separate. Every stable
field (type, pip location, display precision, trade-units precision,
minimum trade size) matches the repo's JPY-aware expectation. Margin
rate is recorded as informational (broker/account-specific). No
blockers. See `OANDA_INSTRUMENT_METADATA_AUDIT.md`.

## H4 rehydration status

**59,587 completed H4 candles** rehydrated from OANDA practice — six
majors (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF),
2020-01-01 → 2026-05-19, ~9,931 candles/pair, bid/ask, completed
candles only, no synthetic fallback. Raw + normalized provenance hashes
recorded. The store `data/oanda_h4_research.sqlite3` is gitignored and
**not committed**. See `OANDA_H4_REHYDRATION_RESULT.md`.

## H4 data audit status

**All 6 pairs acceptable for diagnostics / parity** — 0 incomplete
candles, 0 duplicate timestamps, full bid/ask coverage, full ~6-year
history. Gaps classified: 333 expected weekend gaps + 4 expected
year-end holiday closures per pair; **0 outage-like and 0 suspicious
gaps**. Abnormal spreads (~99% on the rollover-close H4 bar) are
expected microstructure. See `OANDA_H4_DATA_QUALITY_AUDIT.md`.

## Six-pair D1AGG smoke status

**PASS.** All six majors aggregate H4 → D1AGG (1,655 trading-day D1AGG
bars each) and pass every mechanical check: real-OANDA provenance,
rollover-blackout clearance, next-bar-open availability, engine fills at
bar N+1 open, and explicit final-bar missing-next-bar detection.
Diagnostic only — `strategy_evidence: false`. See
`backtests/diagnostics/d1agg_next_open_six_pair_smoke.md`.

## Lean export status

**Produced.** A full Lean-parity export of all six pairs in the H4 store
(full window, ~9,931 candles each). The bulky candle CSVs are gitignored
and **not committed**; the six provenance JSONs and the export manifest
are committed. NZD_USD (the 7th CAMPAIGN_002 instrument) is not in the
six-pair store and was not exported. Parity only — CAMPAIGN_002 stays
REJECT. See `research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md`.

## Lean local parity status

**Not executed — Lean is not installed.** The `lean` CLI and Python
package are absent (Docker is present; host `dotnet` is not required).
Per Phase 8's rule the local parity dry run is documented-but-skipped;
no Lean run was executed and no result fabricated. The prior
data-availability blocker is cleared — the H4 store and export bundle
now exist. The only remaining blocker is installing the Lean toolchain,
a deliberate human step. See `LEAN_PARITY_LOCAL_STATUS.md`.

## Local files created but NOT committed

- `data/oanda_h4_research.sqlite3` — the rehydrated H4 store
  (~59,587 candles). Gitignored (`/data/`, `*.sqlite3`).
- `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` —
  6 Lean custom-data CSVs (~0.95 MB each). Gitignored
  (`research/lean_parity/exports/**/*.csv`). Regenerable via the
  commands in the export manifest.

Both are reproducible from the committed scripts; neither is required in
git.

## Validation results

- `pytest` — **370 passed**.
- `ruff check src tests scripts` — clean.
- `scripts/validate_research_archive.py` — all checks pass.
- `scripts/check_research_freeze.py` — all checks pass.
- `scripts/scan_artifacts_for_secrets.py` — PASSED (no credential value
  or credential-shaped string in any committed/staged artifact).
- `bot paper-loop` / `bot demo-loop` — both refuse (exit 2).
- `configs/approved_strategies.yaml` — `approved: []`.
- No `*.sqlite3` store and no `.env` tracked or staged.

## Safety state

The research freeze is **intact**. The approved-strategy registry is
empty; every order-capable loop refuses; backtests/diagnostics remain
available; no credential leaked; prior evidence is untouched; every new
diagnostic / parity artifact is `strategy_evidence: false`.

## Remaining blockers

1. **Lean toolchain not installed** — blocks the optional local Lean
   parity dry run. Deliberate human step (`pip install lean` + workspace
   + algorithm).
2. **NZD_USD not in the H4 store** — the 7th CAMPAIGN_002 instrument is
   outside the six-pair rehydration universe; a complete CAMPAIGN_002
   parity would need a separate NZD_USD fetch.
3. **Financing is estimated / stress-only** — a standing hard live
   blocker, unchanged. Not in scope for a read-only sprint.

## Recommended next human decision points

1. Decide whether to install the Lean toolchain and run the local
   CAMPAIGN_002 H4 parity dry run (verification only — it cannot approve
   a strategy).
2. Decide whether to rehydrate NZD_USD for a complete seven-instrument
   CAMPAIGN_002 parity, or to accept the six-pair scope.
3. The research freeze stands. Nothing in this sprint implies or
   warrants a strategy approval; lifting the freeze remains a separate,
   deliberate, evidence-backed human decision per
   `docs/research/STRATEGY_APPROVAL_PROCESS.md`.

## Files to review first

1. `docs/research/OANDA_PRACTICE_READONLY_001_PLAN.md` — the sprint plan.
2. This summary.
3. `src/forex_bot/broker/oanda.py` — the two broker bug fixes.
4. `docs/research/OANDA_READONLY_HEALTHCHECK_RESULT.md` — endpoint health.
5. `docs/research/OANDA_H4_DATA_QUALITY_AUDIT.md` — the data verdict.
