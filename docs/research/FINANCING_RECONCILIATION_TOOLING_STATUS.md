# Financing Reconciliation Tooling — Status

**Date:** 2026-05-23 · **Branch:** `research-financing-reconciliation-tooling-001`
`strategy_evidence: false`

Headline status of the local-only financing reconciliation CLI.
**Script shipped, tests pin every rail, synthetic runs
documented.** Nothing in this sprint fetched broker data;
nothing changes a campaign verdict; nothing lifts the
live-promotion blocker.

> No strategy approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. The script writes
> `strategy_evidence: false` and `financing_treatment ∈
> {estimated, unmodeled}` on every output — never `modeled`.

## 1. Script status

[`scripts/reconcile_financing_fixtures.py`](../../scripts/reconcile_financing_fixtures.py)
is implemented and tested. Layout:

| section | role |
|---|---|
| `_parse_args` | argparse CLI (every flag documented in the protocol §2) |
| `_parse_now` | injectable clock parser; rejects naive ISO-8601 strings |
| `_infer_window` | open = earliest event - 13h; close = latest event + 1h (rollover at 21:00 UTC falls strictly inside the window for the committed fixtures) |
| `_instruments` | unique sorted set of observed instruments |
| `_classification_for` | per-row match / mismatch / missing_in_observed / missing_in_calculated under an absolute tolerance |
| `_build_report` | constructs the report dict; rails ban `modeled` treatment and any `True`/`False` drift on the diagnostic flags; sorts rows by `(date_utc, instrument)` |
| `_dump_json` | `sort_keys=True`, 2-space indent, ISO-8601 dates, UTF-8 |
| `_render_md` | deterministic markdown form of the same data |
| `_calc_events_by_key` | aggregates calculator events into a `(date, instrument) -> {cashflow_home, rate_was_missing, notes}` lookup |
| `run(argv)` / `main(argv)` | top-level entrypoints; subprocess + pytest both exercise them |

Strict no-go list (enforced by code + tests):

- no `import forex_bot` / no `oanda` import (grep-rail in
  `test_financing_reconciliation_tooling.test_script_does_not_import_forex_bot`)
- no `os.environ.get('OANDA_*')` /
  `.get('*TOKEN*')` / `.get('*SECRET*')` /
  `.get('*ACCESS_KEY*')` (env-spy rail in
  `test_script_does_not_read_env_vars`)
- no credential value printed (tripwire-env rail in
  `test_script_does_not_print_credentials`)
- no `forex_bot` module pulled in by import (subprocess
  rail in `test_script_module_does_not_pull_in_forex_bot`)
- no `modeled` ever emitted (defense-in-depth: loader
  refuses MODELED, `calculate_run` refuses MODELED,
  `_build_report` raises `RuntimeError` on MODELED before
  writing; tests pin both the happy-path absence and the
  explicit refusal)

## 2. Supported inputs

| flag | required | default | meaning |
|---|:--:|---|---|
| `--observed PATH` | ✓ | — | observed_financing_events fixture (loaded via `load_observed_event_fixture`) |
| `--rates PATH` | ✓ | — | financing_rates fixture (loaded via `load_rate_fixture`) |
| `--output DIR` | | `/tmp/financing_reconcile_default` | output directory; default is `/tmp` so default-arg runs cannot write into the repo |
| `--units` | | `10000` | position size (stringified Decimal) |
| `--entry-price` | | `1.0800` | position entry price (stringified Decimal) |
| `--side` | | `long` | `long` / `short` |
| `--missing-rate-policy` | | `conservative` | `conservative` / `skip` / `error` |
| `--tolerance` | | `1e-9` | absolute per-row tolerance (home-currency units) |
| `--generated-at-utc` | | now(UTC) | injectable ISO-8601 with explicit offset; naive rejected with exit 3 |

## 3. Outputs

Two files per run under `<output>/`:

- `reconciliation.json` — UTF-8, sorted keys, 2-space indent,
  ISO-8601 dates. Carries:
  - `strategy_evidence: false` (literal-pinned)
  - `financing_in_engine_pnl: false` (literal-pinned)
  - `financing_is_live_blocker: true` (literal-pinned)
  - `financing_treatment` — propagated verbatim from the rate
    source; the v1 fixtures all produce `estimated`
  - `tool` / `tool_version`
  - `inputs` block (echoes every CLI arg + the rate source's
    `provenance` + the rate fixture's `rate_missing_dates`)
  - `window` block (open_time, close_time, home_currency)
  - `summary` block (row_count, match, mismatch,
    missing_in_observed, missing_in_calculated,
    rate_was_missing_count)
  - `rows` — per `(date_utc, instrument)`: observed_financing
    (stringified Decimal or null), calculated_cashflow_home
    (float or null), classification, diff, tolerance,
    rate_was_missing, notes
  - `generated_at_utc`

- `reconciliation.md` — deterministic markdown rendering of
  the same data, in the same sort order. Each section
  parallels a JSON block.

Determinism: identical inputs ⇒ bit-identical outputs (modulo
the injectable `--generated-at-utc`; tests pin this).

## 4. Tests

| file | new cases |
|---|---:|
| `tests/research/test_financing_reconciliation_tooling.py` | 22 |

Coverage:

- happy-path exit 0 with `skip` policy; required JSON keys
  and markdown sections present
- determinism of both JSON and markdown across repeat runs
- exit codes: 3 (missing observed file, invalid observed
  schema wrong-kind, missing rate fixture, naive
  `--generated-at-utc`); 2 (default conservative mismatch on
  rate fixture's 5/19); 5 (`--missing-rate-policy error`)
- mismatch classification appears in JSON `rows`
- strategy_evidence rail (false in both outputs)
- modeled rail (never emitted in either output)
- defense-in-depth `_build_report` raises
  `RuntimeError("MODELED")` when called with MODELED
- import isolation: grep + subprocess pin no `forex_bot` /
  `oanda` import
- env-var spy: no `OANDA_*` / `TOKEN` / `SECRET` /
  `ACCESS_KEY` access during run
- credential tripwire: tripwire values absent from stdout +
  stderr
- outputs ≤ 50 KB
- empty observed file ⇒ empty report (exit 0, row_count=0,
  markdown reads `_no rows_`)
- `main(argv)` callable as alternate entrypoint

**22 tests pass.** Full repo suite: **659** passes (637
prior + 22 new). Ruff clean over `src tests scripts
research/parity_verifier research/walk_forward
research/financing`.

## 5. Known limitations

- **One-instrument-per-side per run.** The CLI builds one
  synthetic `PositionInterval` per observed instrument with a
  single `--side` argument applied to all of them. For a
  capture-pilot run with mixed long/short positions across
  the same instrument, the operator would invoke the CLI
  once per side per instrument. A future v2 could accept a
  `--positions positions.json` file with one row per
  position.
- **No file-format autodetection.** The CLI requires
  `--observed` and `--rates` paths explicitly; it does not
  scan a directory for fixtures.
- **No diff against a previous run.** Two reconciliations
  are independently dumped; comparing them is a manual `diff`
  step today.
- **Tolerance is absolute, not relative.** Default `1e-9` is
  synthetic-fixture grade; a future real-data reconciliation
  would relax it (e.g. `--tolerance 0.01`).
- **No machine-readable schema validator separate from the
  loader.** The script delegates schema validation to
  `research.financing.fixtures` (which already raises
  `FixtureValidationError` with strict messages); a future
  refactor could expose a `--validate-only` mode.
- **No `--validate-only` mode.** Every run computes a
  reconciliation; there is no "schema-check the fixtures and
  exit" mode. The loader's standalone validators serve this
  purpose at the API level.
- **`/tmp/` default.** The default `--output` lives under
  `/tmp/`. On systems with restricted `/tmp` (rare locally,
  more common in CI), the operator must pass `--output`
  explicitly. The tests pass `--output tmp_path` to avoid
  the dependency.

## 6. Was any broker / OANDA data fetched?

**No.** This sprint:

- Made zero OANDA calls.
- Issued zero transaction-stream queries.
- Submitted zero orders.
- Read zero credentials from `.env` (and tests pin that the
  script does not call `os.environ.get('OANDA_*')` etc.).
- Did not enable any new endpoint surface.

Every run consumed local JSON fixtures only.

## 7. Is `MODELED` financing now available?

**No.** Neither this sprint nor any rate source under
`research/financing/` produces `MODELED` financing:

- `TableRateSource` refuses MODELED at construction.
- `calculate_run` refuses a MODELED-self-reporting source.
- `_build_report` in the new CLI raises `RuntimeError` if
  asked to emit a MODELED treatment.
- `FutureOandaObservedFinancingModel` in
  `src/forex_bot/financing.py` remains a placeholder whose
  `__init__` raises.

The five-criterion checklist for MODELED in
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 is unchanged by this sprint — none of the criteria are
met yet.

## 8. Is the live blocker lifted?

**No.** `financing_treatment_blocks_approval` in
`src/forex_bot/financing.py` is unchanged. `live`
unconditionally requires `MODELED`; no source produces it;
the live-promotion financing blocker stands. Paper / demo
are also still blocked by the empty approved-strategy
registry.

## 9. Safety state (unchanged by this sprint)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` exists.
- **No bespoke-engine edit.**
- **No `src/forex_bot/financing.py` edit.**
- **No `ObservedFinancingEventRepo` write.**
- **No OANDA call, no `.env` read, no credential printed.**
- **No `*.sqlite3`, candle CSV, or bulky output committed.**
  (Per-run reconciliation outputs live under `/tmp` and are
  not committed.)
- **No new external dependency.**
- **Import isolation grep-enforced + subprocess-pinned.**
- **No MODELED reachable** anywhere in the pipeline.
- **No QuantConnect / LEAN.**

## 10. EVIDENCE_MANIFEST.json

The manifest tracks **campaigns**; this sprint adds no
campaign, so `docs/research/EVIDENCE_MANIFEST.json` requires
no entry — same posture as the two prior financing sprints.
The archive validator continues to PASS.

## 11. Cross-links

- Sprint plan:
  [`FINANCING_RECONCILIATION_TOOLING_001_PLAN.md`](FINANCING_RECONCILIATION_TOOLING_001_PLAN.md)
- CLI protocol:
  [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Synthetic runs:
  [`FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md`](FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md)
- Sister sprint (fixtures + loader):
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md)
- Sister sprint (calculator):
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md)
- Future capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
