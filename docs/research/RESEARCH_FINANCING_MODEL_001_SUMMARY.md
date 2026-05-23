# Research Financing Model Sprint 001 — Summary & Handoff

**Date:** 2026-05-23 · **Branch:** `research-financing-model-001`
`strategy_evidence: false`

Sprint outcome and handoff for the research-grade financing /
carry / rollover calculator under `research/financing/`. The
calculator is implemented, tested, and ready for use by future
strategy campaigns as a richer per-event diagnostic on top of
the existing per-trade overlay.

> **No strategy is approved. CAMPAIGN_002 remains REJECT.** Paper
> / demo / live remain blocked. No QC / LEAN. No OANDA API
> calls. No new strategy campaign. `configs/approved_strategies.yaml`
> stays `approved: []`. The existing
> [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py)
> approval gate remains authoritative for the live-promotion
> financing blocker.

## 1. Headline outcome

The `research/financing/` package is **shipped, tested, and
isolated**:

- 4 module files (`models.py`, `rates.py`, `calculator.py`,
  `reporting.py`) + `__init__.py` + `README.md`.
- 4 test files (`tests/research/test_financing_*.py`) with 71
  cases covering long/short carry, missing-rate policies,
  weekend skip, Wednesday triple swap, JPY precision, currency
  conversion, calculator aggregation, JSON / markdown
  determinism, and a grep-enforced import-isolation rail.
- Full repo suite: **594 passes** (523 prior + 71 new).
- Ruff: clean over `src tests scripts research/parity_verifier
  research/walk_forward research/financing`.
- Archive validator, freeze checker, and secret scan all PASS.
- Paper-loop and demo-loop still refuse; no live-loop command
  exists.

## 2. Commit log (this sprint)

| commit | phase | scope |
|---|---|---|
| `f82ad29` | 0 | plan doc (`FINANCING_MODEL_001_PLAN.md`) |
| `367b770` | 1 | current-assumptions audit (`FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`) |
| `c6b3c92` | 2 | protocol design (`FINANCING_MODEL_PROTOCOL.md`) |
| `5cb1864` | 3 | `research/financing/` module skeleton |
| `f0190d3` | 4 | fixture tests (71 cases) + tz-aware validator order fix |
| `45a714e` | 5 | `CAMPAIGN_002_FINANCING_RETROSPECTIVE.md` (diagnostic only) |
| `6c35ca5` | 6 | `FINANCING_MODEL_STATUS.md` + `EVIDENCE_INDEX.md` update |
| _this_ | 7 | this summary + final validation + `EVIDENCE_INDEX.md` link to this doc |

## 3. Files changed

- **Docs (new):**
  - `docs/research/FINANCING_MODEL_001_PLAN.md`
  - `docs/research/FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`
  - `docs/research/FINANCING_MODEL_PROTOCOL.md`
  - `docs/research/CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`
  - `docs/research/FINANCING_MODEL_STATUS.md`
  - `docs/research/RESEARCH_FINANCING_MODEL_001_SUMMARY.md`
- **Docs (edited):**
  - `docs/research/EVIDENCE_INDEX.md` — adds the
    `research-grade financing calculator` subsection.
- **Code (new):**
  - `research/financing/__init__.py`
  - `research/financing/models.py`
  - `research/financing/rates.py`
  - `research/financing/calculator.py`
  - `research/financing/reporting.py`
  - `research/financing/README.md`
- **Tests (new):**
  - `tests/research/test_financing_models.py`
  - `tests/research/test_financing_rates.py`
  - `tests/research/test_financing_calculator.py`
  - `tests/research/test_financing_reporting.py`

No file in `src/forex_bot/`, `configs/`, `backtests/`, or any
other production path was modified. No `*.sqlite3` was created
or committed. No `.env` was read.

## 4. What the module does

- **Per-day rollover events** keyed on (date, position
  interval). Each event records the date, weekday, rollover
  multiplier (1 normally, 3 on the configured triple-swap
  weekday), the long and short rates used, the applied side
  and bp/day, notional in home currency, signed `cashflow_home`
  (debit `<0`, credit `>0`), `cashflow_home_stress` (clamped
  `<=0`), provenance, and a per-event note list.
- **Pluggable rate source.** `TableRateSource` for explicit
  per-(date, instrument) tables; `ConservativeStressRateSource`
  for debit-only pessimistic bp/day (default; mirrors the
  per-pair table from `src/forex_bot/financing.py`).
- **Conservative missing-rate fallback.** Default policy: when
  a rate is missing, apply `conservative_fallback_bp_per_day`
  (default `1.2`) as a debit and flag the event. `skip` and
  `error` policies are available for callers who explicitly
  accept different behaviour.
- **Calendar conventions.** Weekend skip by default; Wednesday
  triple-rollover by default. Both individually toggleable.
- **Deterministic, reproducible outputs.** JSON and markdown
  reports are bit-identical for identical inputs. Only `now=`
  is read from the clock, and it is injectable.
- **Import isolation.** No file under `research/financing/`
  imports from `forex_bot`. A grep-enforced test rail in
  `tests/research/test_financing_models.py` guards
  independence (mirroring the walk-forward harness pattern).
- **Approval-gate honesty.** Every `FinancingRunReport` carries
  `strategy_evidence: false`, `financing_in_engine_pnl: false`,
  `financing_is_live_blocker: true`, and a `financing_treatment`
  that matches the rate source (`ESTIMATED` for both v1
  sources). `MODELED` is **refused** both at the rate-source
  constructor and inside `calculate_run`.

## 5. What the module deliberately does NOT do

- **Does not fetch broker data.** Zero network calls.
- **Does not touch `src/forex_bot/`.** The bespoke engine, the
  per-trade overlay, the `FinancingTreatment` enum, the
  approval gate, and the observed-event schema are unchanged.
- **Does not write to `observed_financing_events`.** The table
  remains empty under the freeze.
- **Does not produce `MODELED` financing.** That slot remains
  reserved for `FutureOandaObservedFinancingModel` in
  `src/forex_bot/financing.py`.
- **Does not lift the live-promotion blocker.** Live
  unconditionally requires `MODELED`, and nothing here is
  `MODELED`.
- **Does not approve any strategy.**
- **Does not change CAMPAIGN_002's verdict.** CAMPAIGN_002
  remains REJECT (independent of any financing model — every
  pair was already loss-making on directional expectancy).
- **Does not modify `configs/approved_strategies.yaml`.** The
  list stays `[]`.
- **Does not fix historical financing.** OANDA exposes no
  historical financing-rate series; the bot has captured no
  `DAILY_FINANCING` transactions. Stress mode is the only
  research path today.

## 6. Validation results

All commands run on this branch's HEAD.

| command | result |
|---|---|
| `python -m pytest -q` | **594 passed in ~2.1 s** |
| `ruff check src tests scripts research/parity_verifier research/walk_forward research/financing` | **All checks passed!** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** (9 campaigns intact, 0 strategy_approved, 100 evidence-index links resolve, 0 credential strings in 1949 files) |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** (paper-loop refuses, demo-loop refuses) |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** (value scan SKIPPED — no real OANDA credentials sourced; pattern scan clean) |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refuses (`['trend_following']` not in approved registry) |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refuses (`['trend_following']` not in approved registry) |
| `python -m forex_bot.cli --help` | no `live-loop` command listed |

## 7. Safety state (final)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.** No verdict change.
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` exists.
- **No bespoke-engine edit.**
- **No `src/forex_bot/financing.py` edit.**
- **No `ObservedFinancingEventRepo` write.**
- **No OANDA call, no `.env` read, no credential printed.**
- **No new external dependency.**
- **No `*.sqlite3` or candle CSV committed.**
- **Import isolation:** no file under `research/financing/`
  imports from `forex_bot` (grep-enforced).
- **No `MODELED` financing reachable** through any rate source
  in this module.

## 8. Recommended next branch

Two complementary options, both compatible with the freeze:

1. **`research-financing-observed-capture-pilot-001`** — a
   **forward-looking** infrastructure sprint that enables the
   `ObservedFinancingEventRepo` capture path against a
   long-lived practice account, *without* submitting any
   orders. The repo already exists; the missing piece is a
   loop that pulls the transaction stream and persists events.
   This is the slowest path to `MODELED` financing
   (forward-capture takes months) but it is the only path that
   does not depend on a 3rd-party data fetch. Important: the
   sprint must enable read-only transaction stream access; it
   must not enable order submission. (Authorization for read-
   only practice fetches needs explicit human approval per the
   freeze.)

2. **`research-financing-rate-source-fixtures-001`** — a
   docs-and-fixtures sprint that codifies what a "real
   historical rate set" would look like and ships a small,
   committed fixture covering a few illustrative weeks. The
   calculator can already consume any
   `TableRateSource`; this sprint would build the per-date
   adapter, document the shape, and provide a tiny worked
   example. Useful primarily as preparation for option 1's
   reconciliation work.

A **third** option — promoting the calculator's `ESTIMATED`
output to `MODELED` by fitting market-interest-rate
differentials — is **not recommended** until at least one of
the above provides ground-truth data to reconcile against. The
existing financing-design doc (§3) flags that path as a
research project in its own right and warns against introducing
untested model assumptions.

In the meantime, the calculator's `ESTIMATED` stress mode is
ready to be attached to any future campaign's pre-commit.

## 9. Files to review first

In priority order:

1. **[`docs/research/FINANCING_MODEL_001_PLAN.md`](FINANCING_MODEL_001_PLAN.md)** —
   the sprint's scope, safety invariants, and non-goals.
2. **[`docs/research/FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)** —
   the protocol the calculator implements (inputs, outputs,
   rollover convention, triple swap, weekend skip, missing-rate
   fallback, currency conversion, stress mode, deterministic
   reproducibility, approval-gate non-interaction, feature
   classification).
3. **[`docs/research/FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`](FINANCING_MODEL_CURRENT_ASSUMPTIONS.md)** —
   the audit that motivates the new module: what is and is not
   financing-modeled today in the engine, overlay, observed-
   event capture, instrument metadata, and risk engine.
4. **[`docs/research/FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)** —
   headline status: implemented pieces, tests, limitations,
   how future campaigns should use the calculator, and the
   relationship to the existing per-trade overlay.
5. **[`research/financing/README.md`](../../research/financing/README.md)** —
   module overview, layout, and quick-start examples.
6. **[`research/financing/models.py`](../../research/financing/models.py)** —
   shapes and Pydantic rails. The
   `FinancingRunReport.financing_treatment` enforcement and
   the `strategy_evidence: false` pin live here.
7. **[`research/financing/calculator.py`](../../research/financing/calculator.py)** —
   the per-day rollover-event generator. The
   `_rollover_dates` and `_build_event` helpers are where the
   weekend / triple-swap / missing-rate logic lives.
8. **[`research/financing/rates.py`](../../research/financing/rates.py)** —
   the two v1 rate sources. The bp/day table is mirrored from
   `src/forex_bot/financing.CONSERVATIVE_BP_PER_DAY` locally
   to preserve import isolation; a test confirms parity.
9. **[`tests/research/test_financing_calculator.py`](../../tests/research/test_financing_calculator.py)** —
   the heart of the test surface. Long/short × positive/
   negative carry, triple swap, weekend skip, missing-rate
   policies, JPY precision, cross-pair fallback, and
   aggregation.
10. **[`docs/research/CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`](CAMPAIGN_002_FINANCING_RETROSPECTIVE.md)** —
    diagnostic-only retrospective. Demonstrates calculator
    attachment without loading CAMPAIGN_002 trade data; verdict
    explicitly unchanged.

## 10. Cross-links

- Plan: [`FINANCING_MODEL_001_PLAN.md`](FINANCING_MODEL_001_PLAN.md)
- Audit: [`FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`](FINANCING_MODEL_CURRENT_ASSUMPTIONS.md)
- Protocol: [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Retrospective: [`CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`](CAMPAIGN_002_FINANCING_RETROSPECTIVE.md)
- Status: [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Existing overlay design:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Observed-event capture (dormant):
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Walk-forward harness (sister sprint):
  [`RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md`](RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md)
- Recommended-next-branch source:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §5.4
- Evidence index: [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
