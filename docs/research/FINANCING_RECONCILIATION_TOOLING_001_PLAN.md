# Financing Reconciliation Tooling Sprint 001 — Plan

**Date:** 2026-05-23 · **Branch:** `research-financing-reconciliation-tooling-001`
**Base commit:** `d987e77` (HEAD of `research-financing-rate-source-fixtures-001`)
`strategy_evidence: false`

Infrastructure sprint. Builds **local-only reconciliation
tooling** around the synthetic financing fixtures so the future
observed-capture pilot has a ready, tested, deterministic
pipeline to validate captured `DAILY_FINANCING` events against
the calculator. No broker call, no credential read, no network.

> **No strategy is approved. CAMPAIGN_002 remains REJECT.** Paper
> / demo / live remain blocked. No QuantConnect / LEAN. **No
> OANDA API calls.** No new strategy campaign. **This sprint
> cannot, and will not, approve a strategy or make financing
> `MODELED`.** The calculator's `financing_treatment` over any
> reconciliation run remains `estimated`; the live-promotion
> blocker remains.

## 1. Purpose

The previous sprint built:

- a fixture schema
  ([`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)),
- a loader
  ([`research/financing/fixtures.py`](../../research/financing/fixtures.py)),
- 8 committed synthetic event fixtures + 1 rate fixture,
- and a reconciliation pattern proved inside the pytest suite
  (`test_reconciliation_skips_missing_date_matches_observed_per_row`).

This sprint promotes that pattern from a test helper to a
**stand-alone, deterministic CLI** that:

1. Takes one observed-events fixture and one rates fixture as
   inputs.
2. Builds a `PositionInterval` set covering the observation
   window from the events themselves (caller-provided
   metadata).
3. Runs `calculate_run` with the loaded rate source and
   protocol-default config.
4. Compares the calculator's per-event `cashflow_home` to the
   observed `financing` for every shared rollover date.
5. Classifies each row as `match` / `mismatch` / `missing_in_observed`
   / `missing_in_calculated`.
6. Writes a deterministic JSON report and a deterministic
   markdown summary under an explicit output directory.
7. Exits with a non-zero status if any row is `mismatch` or if
   the inputs fail schema validation.

The tool runs **only** against local files. It does not import
`forex_bot`, does not import any broker client, does not read
`.env`, and does not touch the network.

## 2. Non-goals

- **Not a broker call.** Zero OANDA, zero capture, zero
  transaction-stream queries.
- **Not a campaign runner.** No backtest, no signal logic, no
  campaign verdict edit.
- **Not a strategy.** The script writes
  `strategy_evidence: false` on every output and never reaches
  `MODELED` financing.
- **Not a fixture generator.** The script does not invent new
  fixtures; it consumes already-committed ones (or any
  schema-conforming file the caller provides).
- **Not a calculator change.** `research/financing/` semantics
  are frozen by the previous sprint.
- **Not a treatment-gate change.** `financing_treatment_blocks_approval`
  in [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py)
  remains authoritative.
- **Not a CAMPAIGN_002 revival.** No CAMPAIGN_002 artifact is
  loaded.
- **Not a paper / demo / live enabler.** Refusals stand.
- **Not bulky-output writer.** The script writes one small
  JSON + one small markdown file per run; no candle CSV, no
  SQLite, no large dump.

## 3. Safety invariants

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT. No verdict edit, no re-run.
3. Paper / demo loops keep refusing; no `live-loop` exists.
4. No QC / LEAN command.
5. **No OANDA API call.** No transaction-stream query, no
   pricing read, no candle fetch.
6. **No `.env` read. No credential value printed.** The script
   refuses to read environment variables that look like
   credentials and does not propagate any environment-derived
   secret into its output.
7. **No `*.sqlite3`, candle CSV, or bulky output gets
   staged.** Run outputs live under an explicit `--output`
   directory; the default value points to `/tmp` (gitignored
   by the system).
8. The bespoke engine under `src/forex_bot/` is **not
   modified**.
9. `src/forex_bot/financing.py`, `domain/transactions.py`,
   `broker/mapping.py`, and the observed-event repo /
   migration are **not modified**.
10. The walk-forward harness, free / local verifier, and
    fixture loader are **not modified**.
11. No new external dependency is added (the script uses
    `argparse` + `json` + the existing `research/financing/`
    package).
12. The script may not import from `forex_bot`. A
    grep-enforced rail in
    `tests/research/test_financing_reconciliation_tooling.py`
    pins this.
13. Every artifact written by the script carries
    `strategy_evidence: false` and `financing_treatment` ∈
    `{estimated, unmodeled}` — never `modeled`.
14. The script exits non-zero on:
    - any fixture-schema violation (propagating
      `FixtureValidationError`),
    - any per-row mismatch beyond the configured tolerance,
    - any I/O failure on the output directory.
15. The script exits zero **only** if every shared rollover
    date produces a `match` row within tolerance and no
    schema violation occurred.

## 4. Current fixture / loader status (from sister sprint)

From the previous sprint summary:

- Schema:
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
  defines `observed_financing_events` and `financing_rates`
  shapes; mirrors `ObservedFinancingEvent` field-for-field.
- Loader:
  [`research/financing/fixtures.py`](../../research/financing/fixtures.py)
  exposes `load_observed_event_fixture(path)` and
  `load_rate_fixture(path, *, treatment=ESTIMATED) -> (source, missing_dates)`.
- Fixtures: 9 committed files under
  [`research/financing/fixtures/`](../../research/financing/fixtures/),
  total ~9 KB.
- Tests: 43 fixture-loader + reconciliation tests pass; full
  repo suite **637** passes.
- `MODELED` is refused at every layer (rate source
  construction, `calculate_run`, `FinancingRunReport`).
- The previous sprint's
  `test_reconciliation_skips_missing_date_matches_observed_per_row`
  established the pattern this sprint promotes to a CLI.

This sprint adds **tooling only**. Schema, loader, calculator,
and fixtures are not touched.

## 5. Why this sprint precedes observed capture

A capture pilot reads broker data and writes events to a
table. The work splits into two safety surfaces:

- **Broker surface** — touches credentials, the OANDA HTTP
  client, transaction-stream parsing.
- **Reconciliation surface** — takes captured events and the
  calculator's predictions and computes per-row diffs.

The first surface is unavoidable. The second is a pure-Python
local operation that should already exist *before* the broker
surface lands, so the capture sprint's review can focus on the
read-only fetch path without simultaneously inventing how
reconciliation works.

Concretely: when the capture pilot dumps a captured-events
JSON file (per
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§9), the next step is `reconcile_financing_fixtures.py` against
the existing rate fixtures. If the tool already passes on
synthetic fixtures, the only thing left to verify is that
captured events match the expected shape — which the loader
already enforces.

## 6. Expected CLI / tooling outputs

A run produces exactly two files inside the chosen output
directory:

- `reconciliation.json` — UTF-8, sorted keys, 2-space indent,
  ISO-8601 dates. Carries:
  - `strategy_evidence: false` (literal-pinned)
  - `financing_treatment: estimated` (or `unmodeled` if the
    rate source declares `unmodeled`)
  - `financing_in_engine_pnl: false`
  - `financing_is_live_blocker: true`
  - `tool_version: "1"`
  - per-row results: `(date_utc, instrument, applied_side,
    classification, observed_financing, calculated_cashflow_home,
    diff, tolerance)` for every shared and unshared rollover
    date in the window
  - summary counts by classification
  - input file paths (the on-disk paths the caller passed)
- `reconciliation.md` — deterministic markdown table form of
  the same data, suitable for review-time eyeballing.

Determinism: identical inputs ⇒ bit-identical outputs (the
only clock-read is `generated_at_utc`, which is injectable for
tests).

## 7. Planned phases

| phase | output | commit |
|---|---|---|
| 0 | this plan doc + baseline validators | docs-only |
| 1 | `docs/research/FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md` | docs-only |
| 2 | `scripts/reconcile_financing_fixtures.py` + small helpers if needed | code |
| 3 | `tests/research/test_financing_reconciliation_tooling.py` | tests |
| 4 | `docs/research/FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md` (small safe summaries only; no bulky dumps committed) | docs |
| 5 | `docs/research/FINANCING_RECONCILIATION_TOOLING_STATUS.md` + `EVIDENCE_INDEX.md` update | docs |
| 6 | `docs/research/RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md` + final validation | docs |

Each phase ends with a commit and the standard validators:
`pytest -q`, `ruff check ...`, archive validator, freeze
checker, secret scanner.

## 8. Validation surface

Per-phase: `python -m pytest -q`, archive validator, freeze
checker, secret scanner.

Final phase (Phase 6) adds:

- `ruff check src tests scripts research/parity_verifier research/walk_forward research/financing`
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml`
  (must refuse)
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml`
  (must refuse)
- `python -m forex_bot.cli --help` (must not list `live-loop`)

## 9. Explicit statement on approval, MODELED, and verdicts

**This sprint cannot approve a strategy.** Building a
reconciliation CLI — even one that produces a perfect per-row
match against synthetic fixtures — does not satisfy any
approval criterion. Specifically:

- **MODELED financing remains unavailable.** Neither the
  loader nor the calculator nor the new CLI produces
  `MODELED` financing. The CLI propagates the rate source's
  treatment verbatim into its report; for both v1 sources
  that means `ESTIMATED`.
- **The live blocker remains.**
  `financing_treatment_blocks_approval` is unchanged. `live`
  unconditionally requires `MODELED`.
- **CAMPAIGN_002 verdict is not modified.** No CAMPAIGN_002
  artifact is loaded.
- **`configs/approved_strategies.yaml` is not modified.**

A perfect reconciliation on synthetic fixtures shows that the
calculator's conventions are internally consistent — nothing
more. It is **not** evidence that the calculator's predictions
match real OANDA financing. That evidence requires real
captured events; capture has not started.

## 10. Cross-links

- Sister sprint summary (calculator + fixtures):
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md)
- Fixture schema:
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Future capture pilot spec (this tool is its
  reconciliation step):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Calculator status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Existing observed-event capture design (dormant):
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Existing per-trade overlay and `FinancingTreatment` gate:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
