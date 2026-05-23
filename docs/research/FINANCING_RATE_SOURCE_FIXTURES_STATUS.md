# Financing Rate-Source Fixtures — Status

**Date:** 2026-05-23 · **Branch:** `research-financing-rate-source-fixtures-001`
`strategy_evidence: false`

Headline status of the fixture-format / loader-adapter /
pilot-spec sprint. **The fixture format is defined, fixtures
are committed, the loader is implemented, the pilot spec is
drafted, and tests pin every rail.** Nothing in this sprint
fetches broker data; nothing changes a campaign verdict;
nothing lifts the live-promotion blocker.

> No strategy approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. The calculator's
> `financing_treatment` over committed fixtures remains
> `estimated`; `MODELED` is refused everywhere in
> `research/financing/`.

## 1. Fixture schema status

[`docs/research/FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
defines two top-level shapes (picked by `"kind"`):

- **`observed_financing_events`** — rows mirror
  [`ObservedFinancingEvent`](../../src/forex_bot/domain/transactions.py)
  field-for-field. Account-level fields (`account_currency`,
  `account_id_hash`) live on the file. Sign convention is the
  canonical OANDA `DAILY_FINANCING` convention: credit `>0`,
  debit `<0`. `units` and `financing` are stringified
  `Decimal`s; numeric literals are rejected.
- **`financing_rates`** — rows are
  `(date_utc, instrument, long_annual_bp, short_annual_bp)`.
  Annual basis points; signs follow the calculator protocol
  §4 (positive = position receives, negative = position pays).
  An optional file-level `missing_dates` list flags
  intentionally absent dates.

Every fixture file declares `synthetic` (boolean), a
`provenance` string, `schema_version: 1`, and rejects unknown
top-level or row-level keys. Datetimes are ISO-8601 with
explicit offset; naive timestamps are rejected.

The format is intentionally identical to what a future
observed-capture pilot would dump: only the `synthetic` flag
differs between this sprint's hand-built files (`true`) and
a future dump of real captured events (`false`). The loader
does not care which side wrote the file.

## 2. Fixture files added

All under `research/financing/fixtures/`, total ~9 KB:

| file | bytes | kind | demonstrates |
|---|---:|---|---|
| `observed_eur_usd_long_debit.json` | 1098 | events | 3 rollovers across Tue/Wed/Thu; Wed row 3x the rest |
| `observed_eur_usd_short_credit.json` | 624 | events | one rollover that arrives as a credit (sign-convention test) |
| `observed_usd_jpy_precision.json` | 647 | events | USD-base pair preserving JPY-precision-region values |
| `observed_usd_cad_short_debit.json` | 1076 | events | short USD_CAD across Mon/Tue/Wed with the Wednesday triple |
| `observed_same_day_no_rollover.json` | 451 | events | empty events array (zero-event case) |
| `observed_multi_day_with_triple.json` | 1384 | events | long EUR_USD Mon-Fri with the four rollovers |
| `observed_missing_rate_fallback.json` | 1006 | events | omits the Tuesday rollover to pair with a `missing_dates` rate fixture |
| `observed_weekend_skip.json` | 889 | events | held across the weekend; only Fri+Mon rows present |
| `rates_two_week_eur_usd.json` | 1804 | rates | two business weeks of EUR_USD long/short rates with one explicit `missing_dates` entry |
| `README.md` | 3870 | docs | scope + contributor checklist + synthetic-hash preimage |

Every event fixture uses the documented synthetic
`account_id_hash`
(`c4e91d9f7c03827938cbb2c82608bba023e98f23d52b2f84784cbcf9652df69f`
= SHA-256 of `"fixture-account-001"`); every committed file
carries `synthetic: true`; every file is < 10 KB. Three
tests pin these invariants
(`test_every_committed_fixture_carries_synthetic_true`,
`test_every_committed_fixture_is_under_10kb`,
`test_every_committed_event_fixture_uses_documented_hash`).

## 3. Loader / adapter status

[`research/financing/fixtures.py`](../../research/financing/fixtures.py)
adds:

| symbol | role |
|---|---|
| `FixtureValidationError` | exception raised on any schema violation; carries file path, row index, and offending field |
| `ObservedEventDict` | `TypedDict` mirroring `ObservedFinancingEvent` field-for-field, plus the canonical `event_key` |
| `canonical_event_key(...)` | sha1 derivation matching `ObservedFinancingEvent.event_key`, redefined locally so the loader stays import-isolated |
| `load_observed_event_fixture(path) -> list[ObservedEventDict]` | reads + validates + returns deterministically sorted events |
| `load_rate_fixture(path, *, treatment=ESTIMATED) -> (TableRateSource, list[date])` | reads + validates + returns a populated rate source and the file's `missing_dates`; refuses `MODELED` treatment |
| `utc_date_of(event)` | convenience helper for reconciliation tests |
| `SCHEMA_VERSION = 1` | version constant; the loader refuses anything else |

Strict validation surface (each rejection produces a strict
human-readable message):

- unknown / missing top-level keys
- wrong `kind`
- wrong `schema_version`
- non-boolean `synthetic`
- non-string / empty `provenance`
- (event files) `account_currency` not `^[A-Z]{3}$`
- (event files) `account_id_hash` not 64-char lowercase hex
- (event rows) missing required / unknown keys
- (event rows) numeric literal for `units` / `financing`
- (event rows) unparseable Decimal
- (event rows) naive `time`
- (event rows) bad `instrument` shape
- (rate files) `rate_unit` not `"annual_bp"` (v1)
- (rate rows) bad date / instrument / non-numeric rate
- (rate rows) `bool` masquerading as numeric (rejected
  explicitly since Python's `bool` is an `int` subclass)
- (rate files) `missing_dates` ⋂ `rates` non-empty
- (rate files) duplicate `(date_utc, instrument)` row
- invalid JSON, top-level array, missing file

Import isolation: `research/financing/fixtures.py` does not
import from `forex_bot`. Both the package-wide grep rail
(`test_financing_package_does_not_import_forex_bot` in
`test_financing_models.py`) and an explicit per-file pin
(`test_fixtures_module_does_not_import_forex_bot` in
`test_financing_fixtures.py`) cover it.

The loader emits **diagnostic-only** data: a `calculate_run`
report driven from a fixture-loaded `TableRateSource` still
carries `strategy_evidence: false`, `financing_in_engine_pnl:
false`, `financing_is_live_blocker: true`, and at most
`financing_treatment: estimated`.

## 4. Tests

| file | new cases |
|---|---:|
| `tests/research/test_financing_fixtures.py` | 43 |

Coverage:

- determinism (every committed event fixture, the rate
  fixture, repeat-load equality)
- top-level schema rails (unknown / missing keys, wrong kind /
  version, non-boolean synthetic, bad account_id_hash, bad
  account_currency)
- event-row rails (unknown / missing keys, naive time,
  numeric financing literal, unparseable Decimal, bad
  instrument)
- file rails (invalid JSON, top-level array, missing file)
- rate-fixture rails (bad rate_unit, duplicate
  (date_utc, instrument), missing_dates overlap, MODELED
  refusal, bad date, non-numeric rate, bool-as-numeric)
- sign-convention preservation (long debit, short credit,
  Wednesday triple = 3x neighbours)
- canonical `event_key` helper matches loaded event_key;
  loaded `ObservedEventDict` field set matches canonical
  `ObservedFinancingEvent.model_fields` exactly; event_key
  property reconciles
- reconciliation against the calculator: with
  `missing_rate_policy=SKIP`, calculator per-event
  `cashflow_home` matches observed `financing` at rel=1e-9
  for the dates where the rate fixture has rows; the one
  skipped date is exactly the fixture's `missing_dates`
  entry; with `CONSERVATIVE`, fallback fires on the missing
  row
- weekend-skip fixture's dates are Friday and Monday
- `utc_date_of` helper
- diagnostic rails through `calculate_run`
- import isolation (explicit per-file pin)
- fixture-file safety (synthetic=true, <10 KB, documented hash)

**43 new tests pass.** Full repo suite: **637 passes**
(594 prior + 43 new). Ruff clean over `src tests scripts
research/parity_verifier research/walk_forward research/financing`.

## 5. Was any broker / OANDA data fetched?

**No.** This sprint:

- Made zero OANDA calls.
- Issued zero transaction-stream queries.
- Submitted zero orders.
- Read zero credentials from `.env`.
- Did not enable any new endpoint surface.

The committed fixtures are entirely synthetic; the loader runs
against local files only.

## 6. Is `MODELED` financing now available?

**No.** Neither this sprint nor the loader produces `MODELED`
financing:

- `TableRateSource` (the loader's output) refuses
  `treatment=MODELED` at construction.
- `calculate_run` refuses a rate source self-reporting
  `MODELED`.
- `FinancingRunReport` refuses
  `financing_treatment=MODELED`.
- `FutureOandaObservedFinancingModel` in
  `src/forex_bot/financing.py` is still a placeholder whose
  `__init__` raises.

For `MODELED` to become available, the full criteria in
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 must be satisfied — none of those criteria are met in this
sprint.

## 7. Is the live blocker lifted?

**No.** `financing_treatment_blocks_approval` in
`src/forex_bot/financing.py` is unchanged. `live`
unconditionally requires `MODELED`; no source in
`research/financing/` produces `MODELED`; the live-promotion
financing blocker stands. Paper / demo are also still blocked
by the underlying approved-strategy registry (which remains
`approved: []`).

## 8. Safety state (unchanged by this sprint)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` command exists.
- **No bespoke-engine edit.**
- **No `src/forex_bot/financing.py` edit.**
- **No `ObservedFinancingEventRepo` write.** The table
  remains empty.
- **No OANDA call, no `.env` read, no credential printed.**
- **No `*.sqlite3`, candle CSV, or bulky output committed.**
- **No new external dependency.**
- **Import isolation grep-enforced** + per-file pin in tests.
- **No `MODELED` financing reachable** through any rate
  source.
- **No QuantConnect / LEAN.**

## 9. EVIDENCE_MANIFEST.json

The manifest tracks **campaigns**; this sprint adds no
campaign, so `docs/research/EVIDENCE_MANIFEST.json` requires
no entry. Same posture as the sister sprint
[`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md)
§9. The archive validator continues to PASS.

## 10. Cross-links

- Sprint plan:
  [`FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md`](FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md)
- Fixture schema:
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Future-capture pilot spec (future-facing only; not
  implemented in this sprint):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Sister sprint (calculator):
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Calculator status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Existing capture design (dormant):
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Existing per-trade overlay:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
