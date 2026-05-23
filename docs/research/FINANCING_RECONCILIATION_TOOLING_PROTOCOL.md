# Financing Reconciliation Tooling — Protocol

**Date:** 2026-05-23 · **Branch:** `research-financing-reconciliation-tooling-001`
Phase 1 · `strategy_evidence: false`

The protocol the new `scripts/reconcile_financing_fixtures.py`
CLI follows: what it takes, what it produces, how it
classifies each row, how it handles missing data, how its
exit status is structured, and what its outputs may and may
not claim.

> This protocol does not approve any strategy. CAMPAIGN_002
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.
> `MODELED` financing is **unreachable** through this tool —
> the script propagates the rate source's treatment verbatim
> and refuses to emit `modeled`.

## 1. CLI purpose

Compare a captured- or synthetic-event observation file
(shape: `observed_financing_events` per
[`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md))
against the financing calculator's prediction given a rate
fixture, and produce a deterministic per-row diff report.

The tool is **diagnostic**:

- it does not change any campaign verdict;
- it does not approve a strategy;
- it does not lift the live-promotion blocker;
- it does not produce `MODELED` financing for any source;
- it never reads broker data; never touches the network.

It is the reconciliation step the capture pilot needs in order
to validate captured `DAILY_FINANCING` events against the
calculator's predictions, **before** the calculator can be
claimed to model real broker behaviour.

## 2. Accepted inputs

### 2.1 `--observed PATH` (required)

Path to a fixture file with `kind = "observed_financing_events"`.
Loaded via
[`load_observed_event_fixture`](../../research/financing/fixtures.py).

The events define:

- The instrument set (every event's `instrument` field).
- The observation window: open = earliest event's `time` (with
  any caller-provided `--window-open` override taking
  precedence); close = latest event's `time` + 1 hour
  (caller-provided `--window-close` override takes
  precedence). The default behaviour exists so a fixture-only
  caller does not have to specify a window manually.
- The home currency: copied from the file's
  `account_currency`.
- The account hash: copied from the file's `account_id_hash`
  (already redacted at the loader; never reaches the report's
  output).

### 2.2 `--rates PATH` (required)

Path to a fixture file with `kind = "financing_rates"`. Loaded
via
[`load_rate_fixture(path, treatment=ESTIMATED)`](../../research/financing/fixtures.py).
`MODELED` is refused at the loader; the CLI does not expose a
flag to override that.

The rates feed `TableRateSource`. The file's `missing_dates`
list flows through to the report so a reviewer can see which
dates the rate source intentionally lacks.

### 2.3 `--output DIR` (optional; defaults to a `/tmp` path)

Directory under which the two output files are written. The
directory is created if absent. **The default is a `/tmp`
path** (gitignored by the OS) so a default-arg run cannot
accidentally land bulky files under `docs/`, `backtests/`, or
`research/`. A safer pattern is to always pass `--output`
explicitly.

The script writes exactly two files:

- `reconciliation.json`
- `reconciliation.md`

No other files are written. No temp files. No log dump.

### 2.4 `--units UNITS` (optional; defaults to `10000`)

The position size used for building the synthetic
`PositionInterval` that produces the calculator's per-event
predictions. Default `10000` mirrors every committed fixture.
A future captured-events run with a different position size
would pass `--units` explicitly.

### 2.5 `--entry-price PRICE` (optional; defaults to `1.0800`)

The entry price used in the synthetic `PositionInterval`. For
the committed EUR_USD fixtures the default reconciles
exactly; for other instruments the caller passes a realistic
spot-region value.

### 2.6 `--side {long,short}` (optional; defaults to `long`)

Position side. The CLI deduces nothing from the observed
financing sign; the caller declares the side explicitly. Tests
for both sides exercise this.

### 2.7 `--missing-rate-policy {conservative,skip,error}` (optional; defaults to `conservative`)

Forwarded to `FinancingCalculatorConfig.missing_rate_policy`.
The default matches protocol behaviour.

### 2.8 `--tolerance FLOAT` (optional; defaults to `1e-9`)

Per-row absolute tolerance (in home-currency units) for
considering a calculator vs observed `financing` pair a
`match`. Anything larger than this is classified as
`mismatch`. The default is tight; a future real-data
reconciliation would relax it (e.g. `0.01`).

### 2.9 `--generated-at-utc ISO_DATETIME` (optional; defaults to "now")

Injectable clock for deterministic tests. The CLI writes this
value into the report's `generated_at_utc`. Tests pin
identical inputs ⇒ identical outputs by injecting this.

## 3. Expected JSON output

`reconciliation.json` shape:

```json
{
  "tool": "reconcile_financing_fixtures",
  "tool_version": "1",
  "strategy_evidence": false,
  "financing_in_engine_pnl": false,
  "financing_is_live_blocker": true,
  "financing_treatment": "estimated",

  "inputs": {
    "observed_path": "research/financing/fixtures/observed_multi_day_with_triple.json",
    "rates_path": "research/financing/fixtures/rates_two_week_eur_usd.json",
    "units": "10000",
    "entry_price": "1.0800",
    "side": "long",
    "missing_rate_policy": "conservative",
    "tolerance": 1e-9,
    "rate_source_name": "<provenance from rates file>"
  },

  "window": {
    "open_time": "2026-05-18T08:00:00+00:00",
    "close_time": "2026-05-22T16:00:00+00:00",
    "home_currency": "USD"
  },

  "summary": {
    "row_count": 4,
    "match": 3,
    "mismatch": 0,
    "missing_in_observed": 0,
    "missing_in_calculated": 1,
    "rate_was_missing_count": 1
  },

  "rows": [
    {
      "date_utc": "2026-05-18",
      "instrument": "EUR_USD",
      "weekday": 0,
      "classification": "match",
      "observed_financing": "-0.054",
      "calculated_cashflow_home": -0.054,
      "diff": 0.0,
      "tolerance": 1e-9,
      "rate_was_missing": false,
      "notes": []
    },
    ...
  ],

  "generated_at_utc": "2026-05-23T12:00:00+00:00"
}
```

Sign convention preserved verbatim from each source: observed
`financing` is the broker convention (credit `>0`, debit `<0`);
`calculated_cashflow_home` is the calculator's signed value
(same convention); `diff = observed - calculated`. A `match`
row has `|diff| <= tolerance`.

`strategy_evidence`, `financing_in_engine_pnl`, and
`financing_is_live_blocker` are **literal-pinned** to `false`,
`false`, `true` respectively — the script refuses to emit any
other value (tests pin this).

`financing_treatment` is propagated verbatim from the rate
source. For both v1 sources (`TableRateSource(treatment=...)`
and `ConservativeStressRateSource`), it is `estimated`. The
script refuses to emit `modeled`.

## 4. Expected markdown output

`reconciliation.md` is a deterministic markdown rendering of
the same data:

```
# Financing Reconciliation

`strategy_evidence: false` · `financing_treatment: estimated` ·
`financing_in_engine_pnl: false` · `financing_is_live_blocker: true`

## Inputs

- observed: `research/financing/fixtures/observed_multi_day_with_triple.json`
- rates:    `research/financing/fixtures/rates_two_week_eur_usd.json`
- units:    10000
- ...

## Summary

- row_count: 4
- match: 3
- mismatch: 0
- missing_in_observed: 0
- missing_in_calculated: 1
- rate_was_missing_count: 1

## Rows

| date_utc | instrument | weekday | classification | observed | calculated | diff | tol |
|---|---|---:|---|---:|---:|---:|---:|
| 2026-05-18 | EUR_USD | 0 | match | -0.054000 | -0.054000 | 0.000000 | 1.0e-09 |
| 2026-05-19 | EUR_USD | 1 | missing_in_observed | n/a | -1.296000 | n/a | 1.0e-09 |
| ...        |
```

Determinism: same inputs ⇒ same markdown, byte-for-byte
(modulo `generated_at_utc`, which is injectable). The script
sorts rows by `(date_utc, instrument)` before rendering.

## 5. Deterministic sorting requirements

- Observed events: re-sorted by
  `(time, instrument or "", trade_id or "")` (the loader
  already enforces this).
- Calculator events: emitted in chronological order by
  `calculate_position`.
- Report rows: keyed by `(date_utc, instrument)` and sorted
  lexically by that tuple.
- JSON output: `sort_keys=True`, 2-space indent, ISO-8601
  dates, `ensure_ascii=False`.
- Markdown output: rows in the sort order above; no
  timestamps inside the table.

## 6. Reconciliation tolerance rules

- A row is classified `match` iff both sides have a value
  **and** `|observed - calculated| <= tolerance`.
- Default tolerance is `1e-9` (synthetic-fixture grade). A
  future real-data reconciliation will set this to e.g.
  `0.01` USD per event to allow broker rounding.
- Tolerance is **absolute**, not relative. Per-event
  reconciliation against 10k-unit positions naturally lands
  in cents; relative tolerance would mis-rank tiny vs huge
  positions.
- If a row has only one side, it is `missing_in_observed` or
  `missing_in_calculated` (see §7) regardless of tolerance.
- The exit status is non-zero if any row has
  `classification == "mismatch"`. Rows with
  `missing_in_observed` or `missing_in_calculated` do **not**
  set the exit status non-zero on their own — they are
  expected outcomes for fixtures that intentionally omit a
  date.

## 7. Mismatch classifications

Every report row carries one of:

| classification | meaning | counts toward exit-nonzero? |
|---|---|:--:|
| `match` | both sides exist and `\|diff\| <= tolerance` | no |
| `mismatch` | both sides exist and `\|diff\| > tolerance` | **yes** |
| `missing_in_observed` | calculator produced a row for this `(date, instrument)` but the observed fixture has none | no (informational) |
| `missing_in_calculated` | observed fixture has a row but the calculator skipped that date (e.g. rate missing under `skip` policy) | no (informational) |

The summary section counts each classification. A reviewer
can see at a glance whether a run has zero `mismatch` (the
target state) and how many `missing_in_*` rows are expected.

## 8. Missing-rate behaviour

`--missing-rate-policy` is forwarded to
`FinancingCalculatorConfig.missing_rate_policy`:

- `conservative` (default) — calculator fires the fallback
  (e.g. `-1.2` bp/day debit), emits an event with
  `rate_was_missing=True`, and the row appears in the
  reconciliation. If the observed fixture lacks this date,
  the row is `missing_in_observed`. The `rate_was_missing_count`
  in the summary lets reviewers see how many fallback rows
  participated.
- `skip` — calculator emits no event for a missing-rate
  date. The observed fixture's row for that date (if any)
  becomes `missing_in_calculated`. Useful for tight
  reconciliation against a partial rate set.
- `error` — calculator raises
  `MissingFinancingRateError`; the CLI catches it, writes a
  failure record into the JSON, prints a strict error, and
  exits non-zero.

In every case, `missing_dates` from the rate fixture is
echoed verbatim in `inputs` so the operator can cross-check
with the observed file.

## 9. `strategy_evidence: false` requirement

The CLI's output schema enforces:

- `strategy_evidence` MUST be `false` in JSON and labelled
  `false` in markdown.
- `financing_in_engine_pnl` MUST be `false`.
- `financing_is_live_blocker` MUST be `true`.

Tests assert these by constructing a report and re-loading it
from JSON — any drift produces a test failure. The script
defensively re-asserts these values just before write to
catch any accidental future logic change.

## 10. Why results are diagnostic only

A perfect reconciliation between calculator predictions and
observed events on a **synthetic** fixture demonstrates only
that the calculator's conventions are internally consistent
with the fixtures' construction. It is not evidence that the
calculator reproduces real broker behaviour.

A perfect reconciliation between calculator predictions and
**captured real OANDA** events would, at sufficient volume,
be a necessary precondition for promoting the financing model
to `MODELED`. But the capture has not started; this tool
sits in front of that work.

The summary doc this sprint produces (Phase 4's
`FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md`) explicitly
labels every successful reconciliation as **diagnostic only**.

## 11. Why MODELED remains unavailable

The five criteria for `MODELED` from
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 are unchanged by this sprint:

1. ≥ 60 captured rollovers across the traded universe — not
   started.
2. Per-event reconciliation passes against captured data —
   no captured data exists; this sprint reconciles only
   against synthetic fixtures.
3. `MODELED` `FinancingModel` implementation in
   `src/forex_bot/financing.py` — placeholder still raises.
4. Engine-PnL integration — not done.
5. Documented human approval — not granted.

The CLI **refuses** to emit `financing_treatment: modeled`
even if a rate source maliciously declared itself `MODELED`:

- The fixture loader refuses to construct a
  `TableRateSource(treatment=MODELED)`.
- `calculate_run` refuses a rate source self-reporting
  `MODELED`.
- The CLI also adds a final guard before write: if the
  computed report's `financing_treatment == MODELED`, it
  raises a `RuntimeError` and exits non-zero.

This is defense-in-depth: every layer would have to be
defeated simultaneously for a false `MODELED` to escape.

## 12. Exit status

| condition | exit code |
|---|---:|
| every shared row is `match`; no schema violation | 0 |
| at least one row is `mismatch` | 2 |
| any schema-validation error (`FixtureValidationError`) | 3 |
| any I/O failure on output directory | 4 |
| `--missing-rate-policy error` fired | 5 |
| `RuntimeError` (e.g. defense-in-depth MODELED guard) | 6 |

The script uses `sys.exit(N)` with the codes above. Tests
assert against these.

## 13. Cross-links

- Sprint plan:
  [`FINANCING_RECONCILIATION_TOOLING_001_PLAN.md`](FINANCING_RECONCILIATION_TOOLING_001_PLAN.md)
- Fixture schema:
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Future capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Sister sprint summary (calculator + fixtures):
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md)
- Calculator status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
