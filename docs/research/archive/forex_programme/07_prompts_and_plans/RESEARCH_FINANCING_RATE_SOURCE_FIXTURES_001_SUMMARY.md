# Financing Rate-Source Fixtures Sprint 001 — Summary & Handoff

**Date:** 2026-05-23 · **Branch:** `research-financing-rate-source-fixtures-001`
`strategy_evidence: false`

Sprint outcome and handoff for the fixture format,
loader/adapter, and observed-capture pilot specification.
**Schema defined, fixtures committed, loader implemented and
tested, pilot spec drafted.** Nothing in this sprint fetched
broker data; nothing changes a campaign verdict; nothing lifts
the live-promotion blocker.

> **No strategy is approved. CAMPAIGN_002 remains REJECT.** Paper
> / demo / live remain blocked. No QC / LEAN. No OANDA API
> calls. `configs/approved_strategies.yaml` stays `approved:
> []`. `MODELED` financing remains unreachable through
> `research/financing/` — the existing
> [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py)
> approval gate remains authoritative for the live-promotion
> financing blocker.

## 1. Headline outcome

`research/financing/fixtures.py` + `research/financing/fixtures/`
+ 4 new docs are shipped, tested, and isolated:

- 1 new loader module (`fixtures.py`), 0 changes to the
  existing module, schema, or gate code.
- 9 fixture files (8 events + 1 rates) + a `fixtures/README.md`,
  total ~13 KB on disk.
- 43 new tests in `tests/research/test_financing_fixtures.py`,
  pinning every validation rail, sign convention, Wednesday
  triple-swap shape, reconciliation against the calculator,
  loader determinism, fixture-file safety (synthetic=true,
  <10 KB, documented hash), and import isolation.
- Full repo suite: **637 passes** (594 prior + 43 new).
- Ruff: clean over `src tests scripts research/parity_verifier
  research/walk_forward research/financing`.
- Archive validator, freeze checker, secret scan all PASS.
- Paper-loop and demo-loop still refuse; no live-loop command
  exists.

## 2. Commit log (this sprint)

| commit | phase | scope |
|---|---|---|
| `fa5f2e9` | 0 | plan doc |
| `372b9a7` | 1 | fixture schema design (`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`) |
| `aa53878` | 2 | 9 committed fixture files + `fixtures/README.md` |
| `593880b` | 3 | loader/adapter (`research/financing/fixtures.py`) |
| `e3141ca` | 4 | 43 fixture loader + reconciliation tests |
| `dfee39f` | 5 | `FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md` (future-facing only) |
| `b1fb281` | 6 | `FINANCING_RATE_SOURCE_FIXTURES_STATUS.md` + `EVIDENCE_INDEX.md` update |
| _this_ | 7 | this summary + EVIDENCE_INDEX summary link + final validation |

## 3. Files changed

- **Docs (new):**
  - `docs/research/FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md`
  - `docs/research/FINANCING_OBSERVED_FIXTURE_SCHEMA.md`
  - `docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`
  - `docs/research/FINANCING_RATE_SOURCE_FIXTURES_STATUS.md`
  - `docs/research/RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`
- **Docs (edited):**
  - `docs/research/EVIDENCE_INDEX.md` — adds a financing
    rate-source fixtures & pilot spec subsection.
- **Code (new):**
  - `research/financing/fixtures.py` — loader/adapter.
- **Code (edited):**
  - `research/financing/__init__.py` — public re-exports for
    the loader API.
- **Fixture data (new):**
  - `research/financing/fixtures/README.md`
  - `research/financing/fixtures/observed_eur_usd_long_debit.json`
  - `research/financing/fixtures/observed_eur_usd_short_credit.json`
  - `research/financing/fixtures/observed_usd_jpy_precision.json`
  - `research/financing/fixtures/observed_usd_cad_short_debit.json`
  - `research/financing/fixtures/observed_same_day_no_rollover.json`
  - `research/financing/fixtures/observed_multi_day_with_triple.json`
  - `research/financing/fixtures/observed_missing_rate_fallback.json`
  - `research/financing/fixtures/observed_weekend_skip.json`
  - `research/financing/fixtures/rates_two_week_eur_usd.json`
- **Tests (new):**
  - `tests/research/test_financing_fixtures.py`

No file in `src/forex_bot/`, `configs/`, `backtests/`, or any
other production path was modified. No `*.sqlite3` was created
or committed. No `.env` was read. No OANDA call.

## 4. Fixture schema summary

Two top-level shapes (picked by `kind`):

- **`observed_financing_events`** — rows mirror the canonical
  [`ObservedFinancingEvent`](../../src/forex_bot/domain/transactions.py)
  field-for-field
  (`transaction_id`, `account_id_hash`, `instrument`,
  `trade_id`, `units`, `financing`, `currency`, `time`,
  `source`). Account-level fields live on the file
  (`account_currency`, `account_id_hash`); the loader copies
  them into each loaded event. Sign convention: credit `>0`,
  debit `<0` (OANDA `DAILY_FINANCING` convention).
- **`financing_rates`** — rows are
  `(date_utc, instrument, long_annual_bp, short_annual_bp)`.
  Annual basis points; signs follow the calculator protocol's
  §4 (positive ⇒ receives, negative ⇒ pays). An optional
  `missing_dates` list flags intentionally absent dates.

Every fixture file declares `synthetic` (boolean),
`provenance` (non-empty string), `schema_version: 1`. Unknown
top-level or row-level keys are rejected. `units` and
`financing` are **stringified Decimals**; numeric literals are
rejected. Datetimes are ISO-8601 with explicit offset; naive
timestamps are rejected.

The format is intentionally identical to what a future
observed-capture pilot would dump: only the `synthetic` flag
differs between committed synthetic fixtures (`true`) and a
future dump of real captured events (`false`). The loader does
not care which side wrote the file.

## 5. Fixture files added

9 files under `research/financing/fixtures/`, ~13 KB total
(including README); each `*.json` < 10 KB:

| file | bytes | demonstrates |
|---|---:|---|
| `observed_eur_usd_long_debit.json` | 1098 | long EUR_USD, 3 rollovers (Tue/Wed/Thu) with the Wed row 3x the rest |
| `observed_eur_usd_short_credit.json` | 624 | short EUR_USD, one rollover that arrives as a credit |
| `observed_usd_jpy_precision.json` | 647 | USD-base pair preserving JPY-precision-region values |
| `observed_usd_cad_short_debit.json` | 1076 | short USD_CAD across Mon/Tue/Wed with the Wednesday triple |
| `observed_same_day_no_rollover.json` | 451 | empty events array (zero-event case) |
| `observed_multi_day_with_triple.json` | 1384 | long EUR_USD Mon-Fri with the four rollovers; the reconciliation anchor |
| `observed_missing_rate_fallback.json` | 1006 | omits Tuesday rollover; paired with the rate fixture's `missing_dates` entry |
| `observed_weekend_skip.json` | 889 | held across the weekend; only Fri+Mon rows present |
| `rates_two_week_eur_usd.json` | 1804 | two business weeks of EUR_USD long/short rates with one explicit `missing_dates` entry |
| `README.md` | 3870 | scope, contributor checklist, documented synthetic-hash preimage |

Every event fixture uses the documented synthetic
`account_id_hash`
(`c4e91d9f7c03827938cbb2c82608bba023e98f23d52b2f84784cbcf9652df69f`
= SHA-256 of `"fixture-account-001"`). Every fixture carries
`synthetic: true`. Tests pin all three properties (synthetic
flag, size cap, documented hash).

## 6. Loader / adapter implementation status

`research/financing/fixtures.py` is shipped:

| symbol | role |
|---|---|
| `FixtureValidationError` | raised on any schema violation; carries file path, row index, and offending field |
| `ObservedEventDict` | `TypedDict` mirroring the canonical `ObservedFinancingEvent` field set + `event_key` |
| `canonical_event_key(...)` | sha1 derivation matching `ObservedFinancingEvent.event_key`, redefined locally so the loader stays import-isolated |
| `load_observed_event_fixture(path) -> list[ObservedEventDict]` | reads + validates + returns deterministically sorted events |
| `load_rate_fixture(path, *, treatment=ESTIMATED) -> (TableRateSource, list[date])` | reads + validates + returns a populated rate source and the file's `missing_dates`; refuses `MODELED` treatment |
| `utc_date_of(event)` | convenience helper for reconciliation tests |
| `SCHEMA_VERSION = 1` | version constant |

Strict validation (each rejection produces a strict
human-readable message naming file, row, and field):

- unknown / missing top-level keys
- wrong `kind` / `schema_version`
- non-boolean `synthetic`, non-string / empty `provenance`
- (event files) `account_currency` not `^[A-Z]{3}$`,
  `account_id_hash` not 64-char lowercase hex
- (event rows) unknown / missing required keys, naive `time`,
  numeric `financing` literal, unparseable Decimal, bad
  `instrument` shape
- (rate files) `rate_unit != "annual_bp"`, duplicate `(date,
  instrument)`, `missing_dates` ⋂ `rates` non-empty, MODELED
  refusal, bad date format, non-numeric rate, bool-as-numeric
  rejected explicitly
- file rails (invalid JSON, top-level array, missing file)

Import isolation: the file does **not** import from
`forex_bot`. Both the package-wide grep rail (in
`test_financing_models.py`) and an explicit per-file pin (in
`test_financing_fixtures.py`) cover the new loader.

The loader emits **diagnostic-only** data: a `calculate_run`
report driven from a fixture-loaded `TableRateSource` still
carries `strategy_evidence: false`,
`financing_in_engine_pnl: false`,
`financing_is_live_blocker: true`, and at most
`financing_treatment: estimated`.

## 7. Test status

**43 new tests pass** in `tests/research/test_financing_fixtures.py`:

- Determinism (every committed fixture loads sorted; rate
  fixture round-trips; same-day-no-rollover fixture loads to
  empty list)
- Top-level schema rails (unknown / missing keys, wrong kind /
  version, non-boolean synthetic, bad account_id_hash, bad
  account_currency)
- Event-row rails (unknown / missing keys, naive time,
  numeric financing literal, unparseable Decimal, bad
  instrument)
- File rails (invalid JSON, top-level array, missing file)
- Rate-fixture rails (bad rate_unit, duplicate (date_utc,
  instrument), missing_dates overlap, MODELED refusal, bad
  date, non-numeric rate, bool-as-numeric)
- Sign-convention preservation (long debit, short credit,
  Wednesday-row 3x neighbours, weekday=2)
- `canonical_event_key` helper matches loaded event_key;
  loaded `ObservedEventDict` field set equals canonical
  `ObservedFinancingEvent.model_fields` exactly; event_key
  property reconciles
- Reconciliation: with `missing_rate_policy=SKIP`, the
  calculator's per-event `cashflow_home` matches observed
  `financing` at rel=1e-9 for the 3 dates where rates exist;
  the one skipped date is exactly the fixture's
  `missing_dates` entry; with `CONSERVATIVE`, fallback fires
  on the missing 5/19 row (`-1.296` USD)
- Weekend-skip fixture's dates are Friday and Monday
- `utc_date_of` helper
- Diagnostic rails through `calculate_run`
- Import isolation (explicit per-file pin)
- Fixture-file safety (synthetic=true, <10 KB, documented
  hash)

Full repo suite: **637 passes** (594 prior + 43 new). Ruff
clean.

## 8. Observed-capture pilot spec summary

[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
is a future-facing spec only; this sprint does not implement
it. It narrows the scope of the follow-on capture sprint by
fixing:

- **Required authorizations** (live-vs-practice decision,
  read-only credential, documented window, absence of order
  activity, freeze remains in effect)
- **Endpoint allowlist** — only transactions stream + sinceid
  + by-id; explicit denylist on `/orders`, `/trades`,
  `/positions`, `/pricing`, `/accounts/.../configuration`
- **Expected transaction types** — `DAILY_FINANCING` primary;
  any `ORDER_FILL` with non-zero `financing` secondary;
  `RESETTABLE_PL` context only
- **Credential handling** — existing read-only token; no new
  scopes; no logging / printing; `.env` stays uncommitted
- **Redaction** — `hash_account_id` at parser boundary; raw
  id never persisted; `ObservedFinancingEvent.account_id_hash`
  validator refuses non-digests
- **Local storage** — existing `observed_financing_events`
  table; no schema change; SQLite uncommitted; optional
  fixture-shape JSON dumps satisfy the same <10 KB rules
- **Fixture-normalization path** — captured dumps use the same
  shape as this sprint's synthetic fixtures, only
  `synthetic: false` differs; the existing loader accepts both
- **Reconciliation steps** — per-pair empirical bp/day vs the
  conservative table; Wednesday-multiplier verification;
  weekend-skip verification; per-event reconciliation at a
  tight tolerance
- **`MODELED` acceptance criteria** — five items: ≥60
  captured rollovers, reconciliation passes, MODELED
  `FinancingModel` implementation, engine-PnL opt-in
  integration, human approval. None happen in the capture
  sprint alone (the pilot delivers items 1 and 2 only)
- **Why `MODELED` remains blocked** even after this sprint:
  no captured events, no MODELED model, no engine
  integration, no human approval

## 9. Was any broker / OANDA data fetched?

**No.** This sprint made zero OANDA calls, issued zero
transaction-stream queries, submitted zero orders, read zero
credentials from `.env`, and did not enable any new endpoint
surface. The committed fixtures are entirely synthetic; the
loader runs against local files only.

## 10. Is `MODELED` financing now available?

**No.** Neither the loader nor any fixture produces `MODELED`
financing:

- `TableRateSource` refuses `treatment=MODELED` at
  construction (loader path tested).
- `calculate_run` refuses a rate source self-reporting
  `MODELED`.
- `FinancingRunReport` refuses
  `financing_treatment=MODELED`.
- `FutureOandaObservedFinancingModel` in
  `src/forex_bot/financing.py` remains a placeholder whose
  `__init__` raises.

For `MODELED` to become available, the full criteria in
`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md` §11 must be
satisfied — none of those criteria are met in this sprint.

## 11. Remaining limitations

- **No real captured events.** The
  `observed_financing_events` table remains empty. Capture
  has not started.
- **`MODELED` unreachable.** Loader / calculator / report
  models all refuse `MODELED`.
- **Live blocker remains.**
  `financing_treatment_blocks_approval` in
  `src/forex_bot/financing.py` continues to require `MODELED`
  for `live`; no source in `research/financing/` produces it.
- **No capture pipeline implementation.** The pilot spec is
  drafted; the capture loop, the dump CLI, and any
  per-event reconciliation against real OANDA charges are
  future-sprint work.
- **Cross-pair conversion still deferred.** The sister
  sprint's deferred-features list (cross-pair conversion,
  holiday calendar) is unchanged.
- **`rate_unit` is fixed at `annual_bp`.** A future version
  could add `bp_per_day`; the loader would translate. v1 only
  accepts the one unit.
- **No CLI dry-run.** Like the sister sprint, the loader is
  imported and driven from notebook / campaign / test code.
  A `scripts/dump_observed_financing_fixture.py` script could
  land as part of the capture sprint.

## 12. Recommended next branch

**`research-financing-observed-capture-pilot-001`** — the
read-only `DAILY_FINANCING` capture pipeline scoped by
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md).
Prerequisites are the human authorizations in §2 of that
spec. Until those exist, the spec is a reference, not a
license.

If those authorizations are not forthcoming yet, two
freeze-compatible alternatives:

1. **`research-financing-reconciliation-tooling-001`** — a
   docs-and-tooling sprint that adds a small CLI under
   `scripts/` for running the reconciliation pattern in
   `test_reconciliation_skips_missing_date_matches_observed_per_row`
   over arbitrary fixture pairs. Useful preparation for the
   capture sprint's per-event reconciliation step.
2. **`research-financing-bp-day-fixture-expansion-001`** — a
   docs-and-fixtures sprint adding rate-fixture variants for
   the remaining 6 H4 universe pairs (GBP_USD, USD_JPY,
   AUD_USD, USD_CAD, USD_CHF, NZD_USD), still synthetic but
   covering the full universe so the capture sprint can
   reconcile per-pair from day one.

A **third** option — implementing a market-interest-rate-
differential `MODELED` model — remains **not recommended**
until the capture pipeline provides ground-truth data to
reconcile against (per
[`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md) §3).

## 13. Files to review first (priority order)

1. **[`docs/research/FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md`](FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md)** —
   sprint scope, safety invariants, non-goals.
2. **[`docs/research/FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)** —
   the on-disk schema (event + rate shapes, sign convention,
   required vs optional fields, rejection rules,
   determinism).
3. **[`docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)** —
   future-facing capture pilot spec; endpoint allowlist;
   redaction; MODELED acceptance criteria; why MODELED stays
   blocked.
4. **[`docs/research/FINANCING_RATE_SOURCE_FIXTURES_STATUS.md`](FINANCING_RATE_SOURCE_FIXTURES_STATUS.md)** —
   headline status (schema, fixtures, loader, tests, safety
   state).
5. **[`research/financing/fixtures/README.md`](../../research/financing/fixtures/README.md)** —
   per-file scope, synthetic-hash preimage, contributor
   checklist.
6. **[`research/financing/fixtures.py`](../../research/financing/fixtures.py)** —
   the loader. Strict validation surface in `_check_*`
   helpers; `load_observed_event_fixture` and
   `load_rate_fixture` are the two entry points.
7. **[`tests/research/test_financing_fixtures.py`](../../tests/research/test_financing_fixtures.py)** —
   the bulk of the test surface; the reconciliation tests
   (`test_reconciliation_skips_missing_date_matches_observed_per_row`,
   `test_reconciliation_conservative_policy_fires_fallback_on_missing`)
   are the pattern the capture sprint will reuse against
   real data.
8. **[`research/financing/fixtures/observed_multi_day_with_triple.json`](../../research/financing/fixtures/observed_multi_day_with_triple.json)**
   + **[`research/financing/fixtures/rates_two_week_eur_usd.json`](../../research/financing/fixtures/rates_two_week_eur_usd.json)** —
   the reconciliation anchor pair.

## 14. Cross-links

- Plan: [`FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md`](FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md)
- Schema: [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Pilot spec (future-facing only):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Status: [`FINANCING_RATE_SOURCE_FIXTURES_STATUS.md`](FINANCING_RATE_SOURCE_FIXTURES_STATUS.md)
- Sister sprint (calculator):
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Calculator status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Existing per-trade overlay:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Existing observed-event capture design (dormant):
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Evidence index: [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
