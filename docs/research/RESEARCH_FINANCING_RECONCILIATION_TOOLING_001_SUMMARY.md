# Financing Reconciliation Tooling Sprint 001 — Summary & Handoff

**Date:** 2026-05-23 · **Branch:** `research-financing-reconciliation-tooling-001`
`strategy_evidence: false`

Sprint outcome and handoff for the local-only financing
reconciliation CLI. **Script shipped, tests pin every rail,
synthetic runs documented.** Nothing in this sprint fetched
broker data; nothing changes a campaign verdict; nothing lifts
the live-promotion blocker.

> **No strategy is approved. CAMPAIGN_002 remains REJECT.** Paper
> / demo / live remain blocked. No QC / LEAN. No OANDA API
> calls. `configs/approved_strategies.yaml` stays `approved:
> []`. `MODELED` financing remains unreachable through
> `research/financing/`; the script defends in depth and
> refuses to emit `modeled` even if every upstream layer were
> defeated.

## 1. Headline outcome

`scripts/reconcile_financing_fixtures.py` + 5 new docs + 1
new test module are shipped, isolated, and tested:

- 1 new CLI script (`scripts/reconcile_financing_fixtures.py`,
  ~580 lines).
- 22 new tests in
  `tests/research/test_financing_reconciliation_tooling.py`,
  pinning happy path, determinism (JSON + markdown),
  schema/exit-code rails, mismatch classification,
  strategy_evidence + financing_in_engine_pnl +
  financing_is_live_blocker pins, defense-in-depth MODELED
  refusal, import isolation (grep + subprocess), env-var spy,
  credential tripwire, output size cap, empty-events case,
  and the `main(argv)` alternate entrypoint.
- 0 changes to `src/forex_bot/`, `configs/`, `backtests/`, or
  any other production path.
- 0 changes to the existing `research/financing/` package
  (the CLI is a consumer, not an extension).
- Full repo suite: **659 passes** (637 prior + 22 new).
- Ruff: clean over `src tests scripts
  research/parity_verifier research/walk_forward
  research/financing`.
- Archive validator, freeze checker, secret scan all PASS.
- Paper-loop and demo-loop still refuse; no live-loop command
  exists.

## 2. Commit log (this sprint)

| commit | phase | scope |
|---|---|---|
| `f3bb4e4` | 0 | plan doc |
| `e43c466` | 1 | CLI protocol design |
| `bcebff6` | 2 | `scripts/reconcile_financing_fixtures.py` |
| `afd2d08` | 3 | 22 tooling tests |
| `350af17` | 4 | synthetic runs doc + determinism fix |
| `aa85b9c` | 5 | status doc + EVIDENCE_INDEX update |
| _this_ | 6 | this summary + EVIDENCE_INDEX summary-link + final validation |

## 3. Files changed

- **Docs (new):**
  - `docs/research/FINANCING_RECONCILIATION_TOOLING_001_PLAN.md`
  - `docs/research/FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`
  - `docs/research/FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md`
  - `docs/research/FINANCING_RECONCILIATION_TOOLING_STATUS.md`
  - `docs/research/RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`
- **Docs (edited):**
  - `docs/research/EVIDENCE_INDEX.md` — adds a financing
    reconciliation tooling subsection.
- **Code (new):**
  - `scripts/reconcile_financing_fixtures.py` — the CLI.
- **Tests (new):**
  - `tests/research/test_financing_reconciliation_tooling.py`

No file in `src/forex_bot/`, `configs/`, `backtests/`, or
`research/financing/` was modified. No `*.sqlite3` was created
or committed. No `.env` was read. No OANDA call.

## 4. Validation commands run

Final pass (Phase 6), all green:

- `python -m pytest -q` — **659 passed in 2.30 s** (637
  prior + 22 new)
- `ruff check src tests scripts research/parity_verifier
  research/walk_forward research/financing` — **All checks
  passed!**
- `python scripts/validate_research_archive.py` — **ALL
  CHECKS PASSED**
- `python scripts/check_research_freeze.py` — **ALL CHECKS
  PASSED**
- `python scripts/scan_artifacts_for_secrets.py` — **PASSED**
  (1,969 committed artifact files; no credentials)
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml`
  — refuses
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml`
  — refuses
- `python -m forex_bot.cli --help` — no `live-loop` command
  listed

## 5. Confirmation no strategy is approved
`configs/approved_strategies.yaml` verified `approved: []`.
Freeze checker passes.

## 6. Confirmation CAMPAIGN_002 remains REJECT
No CAMPAIGN_002 artifact, config, or report was touched.
Archive validator's `verdicts_non_approval` and
`report_verdict_tokens` checks pass.

## 7. Confirmation paper/demo/live remain blocked
- `paper-loop` refuses (`['trend_following']` not approved).
- `demo-loop` refuses (same).
- `python -m forex_bot.cli --help` does not list `live-loop`.

## 8. Reconciliation CLI summary

`scripts/reconcile_financing_fixtures.py` is a local-only
diagnostic CLI:

- **Inputs** — `--observed PATH` (observed_financing_events
  fixture), `--rates PATH` (financing_rates fixture);
  optional `--output DIR` (default `/tmp/...`), `--units`,
  `--entry-price`, `--side`, `--missing-rate-policy`,
  `--tolerance`, `--generated-at-utc` (injectable clock).
- **Pipeline** — load fixtures via `research.financing.fixtures`;
  infer window from observed events; build one synthetic
  `PositionInterval` per observed instrument; run
  `calculate_run`; per `(date_utc, instrument)`, classify
  `match` / `mismatch` / `missing_in_observed` /
  `missing_in_calculated` under an absolute tolerance.
- **Outputs** — exactly two files per run:
  `reconciliation.json` (sort_keys=True, 2-space indent,
  ISO-8601 dates) + `reconciliation.md` (deterministic markdown
  table). Carries `strategy_evidence: false`,
  `financing_in_engine_pnl: false`,
  `financing_is_live_blocker: true`, and
  `financing_treatment` propagated verbatim from the rate
  source (`estimated` for v1 sources).
- **Exit codes** — `0` success / `2` mismatch / `3` schema /
  `4` I/O / `5` missing-rate `error` policy fired / `6`
  RuntimeError (incl. defense-in-depth MODELED guard).
- **Defense-in-depth** — three layers refuse `MODELED`:
  loader, `calculate_run`, and `_build_report`.

The script does **not** import `forex_bot`, does **not**
import any OANDA client, does **not** read environment
variables, does **not** open a network connection, and
does **not** read `.env`. Four separate tests pin these
properties.

## 9. Synthetic runs summary

Five runs against the committed synthetic fixtures
(documented in
[`FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md`](FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md)):

| run | inputs | policy | exit | rows | match | mismatch | other |
|---|---|---|---:|---:|---:|---:|---|
| 1 | multi_day_with_triple + rates_two_week | `skip` | 0 | 4 | 3 | 0 | 1 missing_in_calculated (matches rate fixture's `missing_dates`) |
| 2 | multi_day_with_triple + rates_two_week | `conservative` (default) | **2** | 4 | 3 | **1** | calculator fired `-1.296` fallback vs observed `-0.054` on 5/19 |
| 3 | missing_rate_fallback + rates_two_week | `skip` | 0 | 2 | 2 | 0 | both fixtures agree to skip 5/19 |
| 4 | same_day_no_rollover + rates_two_week | `conservative` | 0 | 0 | 0 | 0 | empty observed file ⇒ empty report |
| 5 | multi_day_with_triple + rates_two_week | `error` | **5** | n/a | n/a | n/a | calculator raised; script aborted before any file written |

Outputs live under `/tmp/financing_reconcile_runs/`; not
committed.

## 10. Test status

**22 new tests pass** in
`tests/research/test_financing_reconciliation_tooling.py`. Full
repo suite: **659 passes** (637 prior + 22 new). Ruff clean.

Coverage: happy path (exit 0, required JSON keys, markdown
sections); JSON + markdown determinism; exit codes 2 / 3 / 5;
mismatch classification appears in output; strategy_evidence
+ MODELED rails; defense-in-depth `_build_report` MODELED
refusal; import isolation (grep + subprocess); env-var spy;
credential tripwire; outputs ≤ 50 KB; empty observed file;
`main()` callable.

## 11. Whether any broker/OANDA data was fetched

**No.** Zero OANDA calls, zero transaction-stream queries,
zero orders, zero `.env` reads. The script doesn't even
import an HTTP client; subprocess + grep tests pin that no
`forex_bot` or `oanda` import is present.

## 12. Whether MODELED financing is now available

**No.** Three layers refuse `MODELED`:

- `TableRateSource(treatment=MODELED)` raises at
  construction.
- `calculate_run` raises if the rate source self-reports
  `MODELED`.
- `_build_report` in the new CLI raises `RuntimeError` if
  asked to emit a MODELED treatment, before any file is
  written.

The five-criterion checklist for MODELED in
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 is unchanged by this sprint. None of those criteria are
met yet.

## 13. Remaining limitations

- **One-instrument-per-side per run.** Mixed long/short
  positions across the same instrument require multiple
  invocations. A v2 `--positions positions.json` flag could
  consume a richer position spec.
- **No `--validate-only` mode.** Every run computes a
  reconciliation; the loader's stand-alone schema validators
  are the API-level equivalent.
- **No machine-readable diff between two runs.** Two
  reconciliations dump independently; comparing them is a
  manual `diff` step.
- **Absolute tolerance only.** Default `1e-9` is synthetic
  grade; a future real-data reconciliation would set
  `--tolerance 0.01` or similar.
- **`/tmp` default for `--output`.** Operators on systems
  with restricted `/tmp` (rare locally, possible in CI) must
  pass `--output` explicitly. Tests use `pytest`'s `tmp_path`
  to avoid the dependency.
- **No fixture autodetection.** `--observed` and `--rates`
  must be explicit; the CLI does not scan a directory.
- **No real captured data.** Capture pilot has not started;
  the script has nothing real to reconcile against yet.
  Every reconciliation today shows only that the calculator
  is internally consistent with the fixtures' construction.

## 14. Recommended next branch

**`research-financing-observed-capture-pilot-001`** — the
read-only `DAILY_FINANCING` capture pipeline scoped by
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md).
With this sprint's reconciliation CLI in place, the capture
sprint's first run can pipe captured events into a
fixture-shape JSON dump and immediately reconcile against
synthetic rate fixtures using
`scripts/reconcile_financing_fixtures.py`. The capture
sprint's review can focus purely on the read-only OANDA
fetch path; reconciliation is already designed and tested.

If broker authorizations are not forthcoming, two
freeze-compatible alternatives:

1. **`research-financing-bp-day-fixture-expansion-001`** —
   rate-fixture variants for the remaining 6 H4 universe
   pairs (GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF,
   NZD_USD). Still synthetic, still ESTIMATED, but
   broadens the reconciliation surface so the capture
   sprint can reconcile every pair from day one.
2. **`research-financing-reconciliation-batch-001`** — a
   small driver that runs the reconciliation CLI over a
   directory of fixture pairs and aggregates per-pair
   summaries into one diagnostic doc. Useful for sanity-
   checking many synthetic scenarios in one pass before the
   capture pilot.

A third option — implementing a market-interest-rate-
differential MODELED model — remains **not recommended**
until the capture pipeline provides ground-truth data to
reconcile against.

## 15. Files to review first (priority order)

1. **[`docs/research/FINANCING_RECONCILIATION_TOOLING_001_PLAN.md`](FINANCING_RECONCILIATION_TOOLING_001_PLAN.md)**
   — sprint scope, safety invariants, non-goals.
2. **[`docs/research/FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)**
   — CLI inputs, JSON + markdown output shapes,
   classification rules, exit codes, defense-in-depth
   MODELED guard.
3. **[`docs/research/FINANCING_RECONCILIATION_TOOLING_STATUS.md`](FINANCING_RECONCILIATION_TOOLING_STATUS.md)**
   — headline status (script, supported inputs, outputs,
   tests, known limitations, safety state).
4. **[`docs/research/FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md`](FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md)**
   — five-run table with commands, exit codes, and
   summaries; confirmation no broker data fetched.
5. **[`scripts/reconcile_financing_fixtures.py`](../../scripts/reconcile_financing_fixtures.py)**
   — the CLI. `run(argv)` is the top-level entrypoint;
   `_build_report` is where the report dict is constructed;
   the defense-in-depth MODELED guard lives at the end of
   that helper.
6. **[`tests/research/test_financing_reconciliation_tooling.py`](../../tests/research/test_financing_reconciliation_tooling.py)**
   — 22 tests covering every rail.
7. The CLI's reconciliation anchor — same as the previous
   sprint:
   [`research/financing/fixtures/observed_multi_day_with_triple.json`](../../research/financing/fixtures/observed_multi_day_with_triple.json)
   + [`research/financing/fixtures/rates_two_week_eur_usd.json`](../../research/financing/fixtures/rates_two_week_eur_usd.json).

## 16. Cross-links

- Plan: [`FINANCING_RECONCILIATION_TOOLING_001_PLAN.md`](FINANCING_RECONCILIATION_TOOLING_001_PLAN.md)
- Protocol: [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Synthetic runs: [`FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md`](FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md)
- Status: [`FINANCING_RECONCILIATION_TOOLING_STATUS.md`](FINANCING_RECONCILIATION_TOOLING_STATUS.md)
- Sister sprint (fixtures + loader):
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md)
- Sister sprint (calculator):
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md)
- Future capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Evidence index: [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
